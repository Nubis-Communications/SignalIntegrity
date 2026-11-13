"""
Prepare and optionally publish a SignalIntegrity release.
"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

import argparse
import getpass
import os
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REMOTE = 'origin'
SOURCE_BRANCH = 'InNextRelease'
TARGET_BRANCH = 'master'
INSTALLATION_NOTE = (
    'See [Installation](https://github.com/Nubis-Communications/'
    'SignalIntegrity/wiki/Installation) for installation instructions.'
)
EXCLUDED_SCRIPTS = {
    'LinkDoc.sh',
    'LinkHelp.sh',
    'UnlinkDoc.sh',
    'UnlinkHelp.sh',
}


def _make_ca_bundle():
    """Include the Windows OS trust store for TLS-intercepted upload networks."""
    if not hasattr(ssl, 'enum_certificates'):
        return None
    try:
        import certifi
        bundle = Path(certifi.where()).read_bytes()
    except (ImportError, OSError):
        bundle = b''

    extra_certificates = []
    for store in ('ROOT', 'CA'):
        try:
            certificates = ssl.enum_certificates(store)
        except OSError:
            continue
        for certificate, encoding, _trust in certificates:
            if encoding == 'x509_asn':
                extra_certificates.append(
                    ssl.DER_cert_to_PEM_cert(certificate).encode()
                )
    if not extra_certificates:
        return None

    bundle_path = Path(tempfile.gettempdir()) / 'signalintegrity_ca_bundle.pem'
    bundle_path.write_bytes(bundle + b'\n' + b''.join(extra_certificates))
    return str(bundle_path)


class ReleaseError(Exception):
    """An expected release prerequisite or operation failed."""


class ReleaseCancelled(Exception):
    """The user declined a release operation."""


def _run(command, cwd=ROOT, capture_output=False, check=True, env=None):
    """Run a command without a shell and report failures explicitly."""
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            check=False,
            text=True,
            capture_output=capture_output,
            env=env,
        )
    except OSError as error:
        raise ReleaseError(
            'Could not run {}: {}'.format(command[0], error)
        ) from error
    if check and result.returncode:
        raise ReleaseError(
            'Command failed with exit code {}: {}'.format(
                result.returncode, ' '.join(command)
            )
        )
    return result


def _git_output(arguments):
    return _run(
        ['git'] + arguments, capture_output=True
    ).stdout.strip()


def _confirm(prompt):
    answer = input('{} [y/N]: '.format(prompt)).strip().lower()
    return answer in ('y', 'yes')


def _require_clean_worktree(
    prompt_for_cleanup=False, allowed_untracked_file=None
):
    allowed_change = None
    if allowed_untracked_file is not None:
        allowed_change = '?? {}'.format(
            allowed_untracked_file.relative_to(ROOT).as_posix()
        )
    while True:
        changes = _git_output(
            ['status', '--porcelain', '--untracked-files=all']
        )
        relevant_changes = [
            line for line in changes.splitlines()
            if line != allowed_change
        ]
        if not relevant_changes:
            return
        message = (
            'The worktree is not clean. Commit, stash, or otherwise clean up '
            'these changes before releasing:\n{}'.format(
                '\n'.join(relevant_changes)
            )
        )
        if not prompt_for_cleanup:
            raise ReleaseError(message)
        print(message)
        try:
            answer = input(
                'Clean up the worktree, then press Enter to check again '
                '(or type q to quit): '
            ).strip().lower()
        except EOFError as error:
            raise ReleaseCancelled(
                'Release cancelled while waiting for a clean worktree.'
            ) from error
        if answer in ('q', 'quit', 'cancel'):
            raise ReleaseCancelled(
                'Release cancelled because the worktree is not clean.'
            )


def _require_branch(branch):
    result = _run(
        ['git', 'show-ref', '--verify', '--quiet', 'refs/heads/' + branch],
        check=False,
    )
    if result.returncode:
        raise ReleaseError('Required local branch does not exist: {}'.format(branch))


def _release_version(source_ref):
    about = _git_output([
        'show', '{}:SignalIntegrity/__about__.py'.format(source_ref)
    ])
    match = re.search(
        r'(?m)^__version__\s*=\s*[\'"]([^\'"]+)[\'"]\s*$',
        about,
    )
    if not match:
        raise ReleaseError(
            'Could not read __version__ from {}:SignalIntegrity/__about__.py'.format(
                source_ref
            )
        )
    version = match.group(1)
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ReleaseError(
            'Release version {!r} is not in the expected X.Y.Z format'.format(
                version
            )
        )
    return version


def _notes_for_version(markdown, version):
    heading = '## Version {}'.format(version)
    lines = markdown.splitlines()
    try:
        start = lines.index(heading)
    except ValueError:
        raise ReleaseError(
            'Temporary release notes have no {!r} section'.format(heading)
        )
    end = next(
        (i for i in range(start + 1, len(lines))
         if lines[i].startswith('## Version ')),
        len(lines),
    )
    notes = '\n'.join(lines[start + 1:end]).strip()
    if not notes:
        raise ReleaseError(
            'The {!r} release-notes section is empty'.format(heading)
        )
    return notes


def _release_notes_file(path, version):
    expected_name = '.release-notes-v{}.md'.format(version)
    if path.name != expected_name or path.parent != ROOT:
        raise ReleaseError(
            'The temporary release notes file must be {} in the repository '
            'root.'.format(expected_name)
        )
    if not path.is_file():
        raise ReleaseError(
            'Temporary release notes file not found: {}'.format(path)
        )
    change = _git_output([
        'status', '--porcelain', '--untracked-files=all', '--',
        path.relative_to(ROOT).as_posix(),
    ])
    expected_change = '?? ' + path.relative_to(ROOT).as_posix()
    if change != expected_change:
        raise ReleaseError(
            'The temporary release notes file must be newly created and '
            'untracked; status was {!r}.'.format(change)
        )
    try:
        markdown = path.read_text(encoding='utf-8')
    except OSError as error:
        raise ReleaseError(
            'Could not read temporary release notes file: {}'.format(error)
        ) from error
    return _notes_for_version(markdown, version)


def _check_tag_is_available(tag):
    local_tag = _run(
        ['git', 'show-ref', '--verify', '--quiet', 'refs/tags/' + tag],
        check=False,
    )
    if local_tag.returncode == 0:
        raise ReleaseError('Git tag already exists locally: {}'.format(tag))
    remote_tag = _run(
        ['git', 'ls-remote', '--exit-code', '--tags', REMOTE,
         'refs/tags/' + tag],
        capture_output=True,
        check=False,
    )
    if remote_tag.returncode == 0 and remote_tag.stdout.strip():
        raise ReleaseError('Git tag already exists on {}: {}'.format(REMOTE, tag))
    if remote_tag.returncode not in (0, 2):
        raise ReleaseError(
            'Could not check whether tag {} exists on {}'.format(tag, REMOTE)
        )


def _ahead_behind(left, right):
    counts = _git_output([
        'rev-list', '--left-right', '--count', '{}...{}'.format(left, right)
    ]).split()
    if len(counts) != 2:
        raise ReleaseError(
            'Could not compare {} with {}'.format(left, right)
        )
    return int(counts[0]), int(counts[1])


def _merge_release_branch(source_version, source_notes, notes_path):
    _require_clean_worktree(allowed_untracked_file=notes_path)
    _require_branch(TARGET_BRANCH)
    _require_branch(SOURCE_BRANCH)

    _run(['git', 'fetch', '--prune', REMOTE])
    for branch in (TARGET_BRANCH, SOURCE_BRANCH):
        _run(
            ['git', 'rev-parse', '--verify',
             'refs/remotes/{}/{}'.format(REMOTE, branch)]
        )

    source_ahead, source_behind = _ahead_behind(
        SOURCE_BRANCH, '{}/{}'.format(REMOTE, SOURCE_BRANCH)
    )
    if source_ahead or source_behind:
        raise ReleaseError(
            'Local {} and {}/{} differ (local-only commits: {}, '
            'remote-only commits: {}). Push or update the release branch first.'
            .format(
                SOURCE_BRANCH, REMOTE, SOURCE_BRANCH,
                source_ahead, source_behind,
            )
        )

    target_ahead, _ = _ahead_behind(
        TARGET_BRANCH, '{}/{}'.format(REMOTE, TARGET_BRANCH)
    )
    if target_ahead:
        raise ReleaseError(
            'Local {} contains {} commit(s) not present on {}/{}. '
            'Push or reconcile the target branch first.'.format(
                TARGET_BRANCH, target_ahead, REMOTE, TARGET_BRANCH
            )
        )

    fetched_version = _release_version(
        '{}/{}'.format(REMOTE, SOURCE_BRANCH)
    )
    if fetched_version != source_version:
        raise ReleaseError(
            'The release branch version changed during preflight '
            '({} to {}). Retry the release.'.format(
                source_version, fetched_version
            )
        )
    tag = 'v' + source_version
    _check_tag_is_available(tag)
    print(
        '\nRelease {} will merge {}/{} into {}/{}.'.format(
            source_version, REMOTE, SOURCE_BRANCH, REMOTE, TARGET_BRANCH
        )
    )
    if not _confirm('Continue with a fast-forward-only master update?'):
        raise ReleaseCancelled('Release cancelled before changing branches.')

    _run(['git', 'checkout', TARGET_BRANCH])
    _run(['git', 'pull', '--ff-only', REMOTE, TARGET_BRANCH])
    _run([
        'git', 'merge', '--ff-only',
        '{}/{}'.format(REMOTE, SOURCE_BRANCH),
    ])
    merged_version = _release_version(TARGET_BRANCH)
    if merged_version != source_version:
        raise ReleaseError(
            'Merged {} has version {}, expected {}'.format(
                TARGET_BRANCH, merged_version, source_version
            )
        )
    _require_clean_worktree(allowed_untracked_file=notes_path)

    return merged_version, tag, source_notes


def _push_release_branch():
    if not _confirm('Push {} to {}?'.format(TARGET_BRANCH, REMOTE)):
        raise ReleaseCancelled(
            'Artifacts are prepared locally, but push and publishing were cancelled.'
        )
    _run(['git', 'push', REMOTE, TARGET_BRANCH])


def _excluded_directory(relative_path):
    parts = relative_path.parts
    if any(part.startswith('.') for part in parts):
        return True
    if any(part in ('__pycache__', 'SignalIntegrity.egg-info', 'build', 'dist')
           for part in parts):
        return True
    if parts and parts[0] == 'Test':
        return True
    if parts[:3] == ('SignalIntegrity', 'App', 'Help'):
        return True
    if parts[:4] == (
        'SignalIntegrity', 'App', 'Examples', 'PowerIntegrity'
    ):
        return True
    return False


def _include_file(relative_path):
    parts = relative_path.parts
    name = relative_path.name
    suffix = relative_path.suffix.lower()

    if any(part.startswith('.') for part in parts):
        return False
    if '__pycache__' in parts or 'SignalIntegrity.egg-info' in parts:
        return False
    if any(part in ('build', 'dist') for part in parts):
        return False
    if parts and parts[0] == 'Test':
        return False
    if parts[:3] == ('SignalIntegrity', 'App', 'Help'):
        return False
    if parts[:4] == (
        'SignalIntegrity', 'App', 'Examples', 'PowerIntegrity'
    ):
        return False
    if name in EXCLUDED_SCRIPTS:
        return False
    if suffix in ('.pyc', '.p') or (
        'cached' in name.lower() and suffix == '.p'
    ):
        return False
    if parts[0] == 'Doc':
        return relative_path.as_posix() == 'Doc/README.md'
    if len(parts) == 1:
        return suffix == '.py' or name in ('LICENSE.txt', 'README.md')
    return True


def _release_files(root):
    files = []
    for directory, subdirectories, filenames in os.walk(
        str(root), topdown=True, followlinks=False
    ):
        current = Path(directory)
        kept_directories = []
        for name in subdirectories:
            path = current / name
            relative = path.relative_to(root)
            if not path.is_symlink() and not _excluded_directory(relative):
                kept_directories.append(name)
        subdirectories[:] = kept_directories

        for name in filenames:
            path = current / name
            relative = path.relative_to(root)
            if path.is_symlink():
                continue
            if _include_file(relative):
                files.append(relative)
    return sorted(files, key=lambda path: path.as_posix().lower())


def _prepare_artifacts(root, version, output_directory):
    if root == output_directory or root in output_directory.parents:
        raise ReleaseError(
            'Output directory must be outside the repository worktree.'
        )
    output_directory.mkdir(parents=True, exist_ok=True)

    name = 'SignalIntegrity-' + version
    staging_directory = output_directory / name
    zip_path = output_directory / (name + '.zip')
    if staging_directory.exists() or staging_directory.is_symlink() or zip_path.exists():
        print('Existing release artifacts were found:')
        if staging_directory.exists() or staging_directory.is_symlink():
            print('  {}'.format(staging_directory))
        if zip_path.exists():
            print('  {}'.format(zip_path))
        if not _confirm('Replace these exact versioned artifacts?'):
            raise ReleaseCancelled('Artifact generation cancelled.')
        if staging_directory.is_symlink() or staging_directory.is_file():
            staging_directory.unlink()
        elif staging_directory.exists():
            shutil.rmtree(str(staging_directory))
        if zip_path.exists():
            zip_path.unlink()

    files = _release_files(root)
    if not files:
        raise ReleaseError('No source files were selected for the release archive.')

    for relative in files:
        source = root / relative
        destination = staging_directory / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source), str(destination))

    with zipfile.ZipFile(
        str(zip_path), 'w', compression=zipfile.ZIP_DEFLATED
    ) as archive:
        for relative in files:
            archive.write(
                str(staging_directory / relative),
                (Path(name) / relative).as_posix(),
            )

    print('Created source archive: {}'.format(zip_path))
    _run(
        [
            sys.executable, 'setup.py', 'bdist_wheel', '--universal'
        ],
        cwd=staging_directory,
    )
    wheel_files = sorted((staging_directory / 'dist').glob('*.whl'))
    if not wheel_files:
        raise ReleaseError(
            'Wheel build completed without producing a wheel in dist/.'
        )
    print('Created wheel(s):')
    for wheel in wheel_files:
        print('  {}'.format(wheel))
    return zip_path, wheel_files


def _publish_github(tag, version, notes, zip_path):
    if not _confirm('Create the GitHub release and upload the source ZIP?'):
        return False
    if not shutil.which('gh'):
        raise ReleaseError(
            'GitHub CLI (gh) is required for GitHub release publishing.'
        )
    _run(['gh', 'auth', 'status'])

    release_notes = notes + '\n\n' + INSTALLATION_NOTE + '\n'
    notes_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            suffix='.md',
            delete=False,
        ) as notes_file:
            notes_file.write(release_notes)
            notes_path = notes_file.name
        _run([
            'gh', 'release', 'create', tag, str(zip_path),
            '--title', 'SignalIntegrity ' + version,
            '--notes-file', notes_path,
            '--target', TARGET_BRANCH,
        ])
        return True
    finally:
        if notes_path and os.path.exists(notes_path):
            os.remove(notes_path)


def _publish_pypi(version, wheel_files):
    if not _confirm('Publish the wheel to a Python package index?'):
        return None
    print('Choose the upload target:')
    print('  1. TestPyPI')
    print('  2. PyPI (production)')
    target = input('Target [1/2, default 1]: ').strip() or '1'
    if target not in ('1', '2'):
        raise ReleaseError('Invalid package-index selection: {}'.format(target))

    if target == '1':
        command = [
            sys.executable, '-m', 'twine', 'upload',
            '--repository-url', 'https://test.pypi.org/legacy/',
        ]
        target_name = 'TestPyPI'
    else:
        if not _confirm(
            'Publish version {} to production PyPI?'.format(version)
        ):
            return None
        command = [sys.executable, '-m', 'twine', 'upload']
        target_name = 'PyPI'

    upload_env = os.environ.copy()
    upload_env['TWINE_USERNAME'] = '__token__'
    if not upload_env.get('TWINE_PASSWORD'):
        upload_env['TWINE_PASSWORD'] = getpass.getpass(
            'Enter the {} API token (input hidden): '.format(target_name)
        )
    if not upload_env['TWINE_PASSWORD']:
        raise ReleaseError('No PyPI API token was provided.')
    upload_env['TWINE_NON_INTERACTIVE'] = '1'

    print('Uploading {} wheel(s) to {}.'.format(len(wheel_files), target_name))
    _run(command + [str(wheel) for wheel in wheel_files], env=upload_env)
    return 'testpypi' if target == '1' else 'pypi'


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            'Merge InNextRelease into master, build release artifacts, and '
            'optionally publish them.'
        )
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=ROOT.parent,
        help=(
            'directory for the versioned source folder and ZIP '
            '(default: repository parent directory)'
        ),
    )
    parser.add_argument(
        '--release-notes-file',
        type=Path,
        required=True,
        help=(
            'temporary, untracked Markdown file named '
            '.release-notes-vX.Y.Z.md in the repository root'
        ),
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)
    try:
        ca_bundle = _make_ca_bundle()
        if ca_bundle:
            os.environ['REQUESTS_CA_BUNDLE'] = ca_bundle
            os.environ['SSL_CERT_FILE'] = ca_bundle

        repository_root = Path(
            _git_output(['rev-parse', '--show-toplevel'])
        ).resolve()
        if repository_root != ROOT:
            raise ReleaseError(
                'Run MakeRelease.py from the SignalIntegrity repository root.'
            )
        version = _release_version(SOURCE_BRANCH)
        notes_path = args.release_notes_file.expanduser().resolve()
        notes = _release_notes_file(notes_path, version)
        _require_clean_worktree(
            prompt_for_cleanup=True,
            allowed_untracked_file=notes_path,
        )

        version, tag, notes = _merge_release_branch(
            version, notes, notes_path
        )
        zip_path, wheel_files = _prepare_artifacts(
            ROOT,
            version,
            args.output_dir.expanduser().resolve(),
        )
        _push_release_branch()
        github_published = _publish_github(tag, version, notes, zip_path)
        pypi_target = _publish_pypi(version, wheel_files)
        if github_published or pypi_target == 'pypi':
            try:
                notes_path.unlink()
            except OSError as error:
                raise ReleaseError(
                    'Release completed, but temporary release notes could not '
                    'be deleted: {}'.format(error)
                ) from error
            print('Removed temporary release notes: {}'.format(notes_path))
        else:
            print(
                'No public release was published; temporary release notes '
                'were retained at {}.'.format(notes_path)
            )
        print('\nRelease {} preparation is complete.'.format(version))
        print('Source ZIP: {}'.format(zip_path))
        print('Wheel(s): {}'.format(', '.join(str(path) for path in wheel_files)))
        return 0
    except ReleaseCancelled as error:
        print(str(error))
        return 0
    except (ReleaseError, subprocess.SubprocessError) as error:
        print('Release failed: {}'.format(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
