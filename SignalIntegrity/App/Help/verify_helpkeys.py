#!/usr/bin/env python
"""Compare a freshly generated ``helpkeys`` file against the legacy key list.

After migrating the help system from LyX/eLyXer to MkDocs, run this to confirm
that every context-help label the application relies on still resolves to a
page/anchor in the new site.

Usage::

    python verify_helpkeys.py [new_helpkeys] [legacy_helpkeys]

Defaults:
    new_helpkeys    = ./site/helpkeys              (output of gen_helpkeys.py)
    legacy_helpkeys = ./Help.html.LyXconv/helpkeys (frozen legacy list)

Exit code is non-zero if any legacy label is missing from the new file, so this
can be wired into CI.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_NEW = os.path.join(HERE, 'site', 'helpkeys')
DEFAULT_LEGACY = os.path.join(HERE, 'Help.html.LyXconv', 'helpkeys')


def load_keys(path):
    """Return the set of labels (left-hand side of ' >>> ') in a helpkeys file."""
    keys = set()
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tokens = line.split(' >>> ')
            if len(tokens) == 2:
                keys.add(tokens[0])
    return keys


def main(argv):
    new_path = argv[1] if len(argv) > 1 else DEFAULT_NEW
    legacy_path = argv[2] if len(argv) > 2 else DEFAULT_LEGACY

    for path, what in ((new_path, 'new'), (legacy_path, 'legacy')):
        if not os.path.isfile(path):
            sys.stderr.write('%s helpkeys not found: %s\n' % (what, path))
            return 2

    new_keys = load_keys(new_path)
    legacy_keys = load_keys(legacy_path)

    missing = sorted(legacy_keys - new_keys)
    added = sorted(new_keys - legacy_keys)

    print('legacy labels : %d' % len(legacy_keys))
    print('new labels    : %d' % len(new_keys))
    print('missing (in legacy, not in new) : %d' % len(missing))
    print('added   (in new, not in legacy) : %d' % len(added))

    if missing:
        print('\n--- MISSING labels (context help will break for these) ---')
        for k in missing:
            print('  ' + k)
    if added:
        print('\n--- ADDED labels (new anchors not previously present) ---')
        for k in added:
            print('  ' + k)

    return 1 if missing else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
