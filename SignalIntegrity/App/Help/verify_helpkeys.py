#!/usr/bin/env python
"""Verify the ``helpkeys`` index of the SignalIntegrity MkDocs help site.

Every context-help request the application makes is resolved by looking a label
up in ``helpkeys`` and opening the ``page.html#anchor`` it maps to (see
``SignalIntegrity.App.BuildHelpSystem.HelpSystemKeys``).  This checks that the
index and the built site agree with each other:

* every label maps to a page that exists in the site,
* that page really carries an element with the id the label resolves to, and
* every context-help anchor in the site is present in the index, so that
  ``helpkeys`` is not stale with respect to a newer build.

Usage::

    python verify_helpkeys.py [site_dir]

If ``site_dir`` is omitted, ``./site`` next to this script is used.  The exit
code is non-zero if anything is wrong, so this can be wired into CI.

To check the opposite direction - labels referenced by the application source
that do not exist in the site at all - use ``Test/Utilities/find_missing_help.py``
in the SignalIntegrity repository.
"""
import os
import sys

from gen_helpkeys import scan_site_for_keys


def load_keys(path):
    """Return a dict of label -> target, and the list of labels appearing twice."""
    keys = {}
    duplicates = []
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tokens = line.split(' >>> ')
            if len(tokens) != 2:
                continue
            label, target = tokens
            if label in keys:
                duplicates.append(label)
            else:
                keys[label] = target
    return keys, duplicates


def main(argv):
    site_dir = argv[1] if len(argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'site')

    if not os.path.isdir(site_dir):
        sys.stderr.write('site directory not found: %s\n'
                         '(build the site first: mkdocs build)\n' % site_dir)
        return 2
    helpkeys_path = os.path.join(site_dir, 'helpkeys')
    if not os.path.isfile(helpkeys_path):
        sys.stderr.write('helpkeys not found: %s\n'
                         '(generate it first: python gen_helpkeys.py)\n' % helpkeys_path)
        return 2

    keys, duplicates = load_keys(helpkeys_path)
    anchors = scan_site_for_keys(site_dir)

    unresolved = []
    for label in sorted(keys):
        page, _, anchor = keys[label].partition('#')
        if not os.path.isfile(os.path.join(site_dir, page)):
            unresolved.append((label, 'page does not exist: ' + page))
        elif anchor == '':
            unresolved.append((label, 'no anchor in target: ' + keys[label]))
        elif label not in anchors:
            unresolved.append((label, 'no element with id "' + anchor + '" in ' + page))

    unindexed = sorted(set(anchors) - set(keys))

    print('labels in helpkeys      : %d' % len(keys))
    print('anchors in the site     : %d' % len(anchors))
    print('unresolved labels       : %d' % len(unresolved))
    print('anchors not in helpkeys : %d' % len(unindexed))
    print('duplicated labels       : %d' % len(duplicates))

    if unresolved:
        print('\n--- UNRESOLVED labels (context help will break for these) ---')
        for label, why in unresolved:
            print('  %-50s %s' % (label, why))
    if unindexed:
        print('\n--- ANCHORS missing from helpkeys (regenerate it) ---')
        for label in unindexed:
            print('  ' + label)
    if duplicates:
        print('\n--- DUPLICATED labels (the first one wins) ---')
        for label in sorted(set(duplicates)):
            print('  ' + label)

    return 1 if (unresolved or unindexed or duplicates) else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
