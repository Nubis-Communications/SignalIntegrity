#!/bin/bash
# Build the SignalIntegrity MkDocs help site and (re)generate the helpkeys index.
#
# This replaces the old LyX + eLyXer 'Convert.sh' workflow.
#
# Prerequisites:
#   pip install mkdocs pillow pymdown-extensions
#   (content is produced separately by convert_help.py, which needs lyx + pandoc)
set -e
cd "$(dirname "$0")"

# Build the static site into ./site
mkdocs build --clean

# Generate ./site/helpkeys from the anchor ids in the built HTML.
python gen_helpkeys.py site

echo "help site built in ./site (open ./site/index.html)"
