#!/bin/bash
# Deploy the SignalIntegrity MkDocs help site to GitHub Pages (Option B).
#
# The gh-pages branch is checked out in place in this repository and keeps the
# nested directory layout that INSTALLED apps expect:
#   SignalIntegrity/App/Help/site/   (help pages + helpkeys)
#   SignalIntegrity/App/Doc/xhtml/   (Doxygen API docs, mirrored from repo root)
#
# Installed apps resolve online help at
#   .../SignalIntegrity/SignalIntegrity/App/Help/site/...
# and the SoftwareDocumentation link at
#   .../SignalIntegrity/SignalIntegrity/App/Doc/xhtml/index.xhtml
# so this script builds the site IN PLACE and commits the gh-pages working tree
# directly.  It does NOT use 'mkdocs gh-deploy' (which force-flattens ./site to
# the branch root and would destroy the nested layout and sibling folders).
#
# Prerequisites:
#   pip install mkdocs pillow pymdown-extensions
#   (the Markdown content lives in ./docs and is edited directly)
set -e
cd "$(dirname "$0")"

# Resolve the gh-pages repo root (this script lives in SignalIntegrity/App/Help).
REPO="$(cd ../../.. && pwd)"

# Paths committed by this script (relative to REPO).
SITE_REL="SignalIntegrity/App/Help/site"
DOCS_REL="SignalIntegrity/App/Doc/xhtml"

# Build the static site into ./site and regenerate the helpkeys index.
mkdocs build --clean
python gen_helpkeys.py site

# Guard: make sure the gh-pages branch is checked out before committing.
BRANCH="$(git -C "$REPO" rev-parse --abbrev-ref HEAD)"
if [ "$BRANCH" != "gh-pages" ]; then
    echo "error: expected the gh-pages branch checked out in $REPO but found $BRANCH." >&2
    exit 1
fi

# Mirror the Doxygen API docs from the repo root into the App path so the
# online SoftwareDocumentation link resolves.  Prefer rsync; fall back to cp.
mkdir -p "$REPO/$DOCS_REL"
if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "$REPO/Doc/xhtml/" "$REPO/$DOCS_REL/"
else
    rm -rf "$REPO/$DOCS_REL"
    mkdir -p "$REPO/$DOCS_REL"
    cp -r "$REPO/Doc/xhtml/." "$REPO/$DOCS_REL/"
fi

# Ensure .nojekyll at the repo root so _-prefixed asset dirs are served.
[ -f "$REPO/.nojekyll" ] || : > "$REPO/.nojekyll"

# Stage only the help site, the mirrored docs, and .nojekyll (captures deletes
# of stale files without touching Doc/, Images/, Videos/).
git -C "$REPO" add -A -- "$SITE_REL" "$DOCS_REL" ".nojekyll"

# Empty-commit guard: exit cleanly when nothing changed.
if git -C "$REPO" diff --cached --quiet; then
    echo "nothing to deploy - help site and docs are already up to date."
    exit 0
fi

git -C "$REPO" commit -m "Deploy help site and API docs"
git -C "$REPO" push

echo "help site and API docs deployed to the gh-pages branch (GitHub Pages will publish shortly)."
