"""
find_missing_help.py

Scan the SignalIntegrity App source for help keys referenced by devices
(PartPropertyHelp('device:...')) and control elements
(AddHelpElement('Control-Help:...') and similar), then report which of those
keys do NOT exist in the built help system (helpkeys file).
"""

# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# Copyright (c) 2021-2025 Nubis Communications, Inc.
# Copyright (c) 2026 Ciena, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

import os
import re

# This utility lives in <repo>/Test/Utilities, so the repository root is two
# directories up.  SignalIntegrityPages is a sibling of the repository root.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
APP_DIR = os.path.join(REPO_ROOT, 'SignalIntegrity', 'App')
HELPKEYS = os.path.join(
    REPO_ROOT, '..', 'SignalIntegrityPages',
    'SignalIntegrity', 'App', 'Help', 'site', 'helpkeys')

# Patterns that register a help key in the source.
REF_RE = re.compile(
    r"(?:AddHelpElement|PartPropertyHelp)\(\s*['\"]([^'\"]*)['\"]")

def existing_keys():
    keys = set()
    with open(HELPKEYS, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(' >>> ')
            keys.add(parts[0])
    return keys

def referenced_keys():
    refs = {}  # key -> list of (file, line)
    for root, _dirs, files in os.walk(APP_DIR):
        for name in files:
            if not name.endswith('.py'):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    for i, line in enumerate(f, 1):
                        for m in REF_RE.finditer(line):
                            key = m.group(1)
                            refs.setdefault(key, []).append(
                                (os.path.relpath(path, APP_DIR), i))
            except OSError:
                continue
    return refs

def main():
    existing = existing_keys()
    refs = referenced_keys()

    missing_devices = []
    missing_controls = []
    missing_other = []
    for key, locs in sorted(refs.items()):
        if key == '' or key.endswith(':'):
            # empty / placeholder help keys
            bucket = missing_other
        elif key in existing:
            continue
        elif key.startswith('device:'):
            bucket = missing_devices
        elif key.startswith('Control-Help:'):
            bucket = missing_controls
        else:
            bucket = missing_other
        bucket.append((key, locs))

    def dump(title, items):
        print('=' * 70)
        print(title, '(%d)' % len(items))
        print('=' * 70)
        for key, locs in items:
            loc = ', '.join('%s:%d' % l for l in locs)
            print('  %-45s %s' % (repr(key), loc))
        print()

    dump('DEVICES with no help entry', missing_devices)
    dump('CONTROL ELEMENTS with no help entry', missing_controls)
    dump('OTHER / placeholder help keys', missing_other)

    print('Total referenced keys: %d' % len(refs))
    print('Total existing help keys: %d' % len(existing))

if __name__ == '__main__':
    main()
