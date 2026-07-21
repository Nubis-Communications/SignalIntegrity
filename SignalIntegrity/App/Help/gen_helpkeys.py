#!/usr/bin/env python
"""Generate the ``helpkeys`` index for the SignalIntegrity MkDocs help site.

This scans a *built* MkDocs site directory for HTML element ids that correspond
to context-help labels (ids beginning with one of the known prefixes) and writes
a ``helpkeys`` file mapping::

    <label> >>> <relative-page>.html#<label>

The SignalIntegrity application reads this file at runtime to resolve
context-sensitive help requests (see
``SignalIntegrity.App.BuildHelpSystem.HelpSystemKeys``).

Usage::

    python gen_helpkeys.py [site_dir]

If ``site_dir`` is omitted, ``./site`` next to this script is used.
"""
import os
import re
import sys

# Keep this list in sync with HelpSystemKeys.labelPrefixes in
# SignalIntegrity/App/BuildHelpSystem.py.
LABEL_PREFIXES = ('sec:', 'sub:', 'Control-Help:', 'device:', 'par:', 'pc:')


def scan_site_for_keys(site_dir):
    """Return a dict of label -> 'relative/page.html#label' for every context
    help anchor found under *site_dir*."""
    keydict = {}
    idre = re.compile(r'id="([^"]+)"')
    for root, _dirs, files in os.walk(site_dir):
        for name in files:
            if not name.endswith('.html'):
                continue
            filepath = os.path.join(root, name)
            rel = os.path.relpath(filepath, site_dir).replace('\\', '/')
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except OSError:
                continue
            for anchor in idre.findall(content):
                if anchor.startswith(LABEL_PREFIXES) and anchor not in keydict:
                    keydict[anchor] = rel + '#' + anchor
    return keydict


def main(argv):
    if len(argv) > 1:
        site_dir = argv[1]
    else:
        site_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site')
    if not os.path.isdir(site_dir):
        sys.stderr.write('site directory not found: %s\n' % site_dir)
        return 1
    keydict = scan_site_for_keys(site_dir)
    out = os.path.join(site_dir, 'helpkeys')
    with open(out, 'w', encoding='ascii', errors='replace') as f:
        for key in sorted(keydict):
            f.write('%s >>> %s\n' % (key, keydict[key]))
    sys.stdout.write('wrote %d help keys to %s\n' % (len(keydict), out))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
