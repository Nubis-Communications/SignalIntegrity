@echo off
REM Deploy the SignalIntegrity MkDocs help site to GitHub Pages (Option B).
REM
REM The gh-pages branch is checked out in place in this repository and keeps the
REM nested directory layout that INSTALLED apps expect:
REM   SignalIntegrity/App/Help/site/   (help pages + helpkeys)
REM   SignalIntegrity/App/Doc/xhtml/   (Doxygen API docs, mirrored from repo root)
REM
REM Installed apps resolve online help at
REM   .../SignalIntegrity/SignalIntegrity/App/Help/site/...
REM and the SoftwareDocumentation link at
REM   .../SignalIntegrity/SignalIntegrity/App/Doc/xhtml/index.xhtml
REM so this script builds the site IN PLACE and commits the gh-pages working tree
REM directly.  It does NOT use 'mkdocs gh-deploy' (which force-flattens .\site to
REM the branch root and would destroy the nested layout and sibling folders).
REM
REM Prerequisites:
REM   pip install mkdocs pillow pymdown-extensions
REM   (the Markdown content lives in .\docs and is edited directly)
setlocal enabledelayedexpansion
cd /d "%~dp0"

REM Resolve the gh-pages repo root (this script lives in SignalIntegrity\App\Help).
for %%I in ("%~dp0..\..\..") do set "REPO=%%~fI"

REM Paths committed by this script (relative to REPO).
set "SITE_REL=SignalIntegrity/App/Help/site"
set "DOCS_REL=SignalIntegrity/App/Doc/xhtml"

REM Build the static site into .\site and regenerate the helpkeys index.
mkdocs build --clean || goto :error
python gen_helpkeys.py site || goto :error

REM Guard: make sure the gh-pages branch is checked out before committing.
for /f "delims=" %%B in ('git -C "%REPO%" rev-parse --abbrev-ref HEAD') do set "BRANCH=%%B"
if /i not "!BRANCH!"=="gh-pages" (
    echo error: expected the gh-pages branch checked out in "%REPO%" but found "!BRANCH!".
    goto :error
)

REM Mirror the Doxygen API docs from the repo root into the App path so the
REM online SoftwareDocumentation link resolves.  robocopy /MIR returns exit
REM codes 0-7 on success (>=8 is a real failure).
robocopy "%REPO%\Doc\xhtml" "%REPO%\SignalIntegrity\App\Doc\xhtml" /MIR /NFL /NDL /NJH /NJS /NP
if %ERRORLEVEL% GEQ 8 goto :error

REM Ensure .nojekyll at the repo root so _-prefixed asset dirs are served.
if not exist "%REPO%\.nojekyll" type nul > "%REPO%\.nojekyll"

REM Stage only the help site, the mirrored docs, and .nojekyll (captures deletes
REM of stale files without touching Doc\, Images\, Videos\).
git -C "%REPO%" add -A -- "%SITE_REL%" "%DOCS_REL%" ".nojekyll" || goto :error

REM Empty-commit guard: exit cleanly when nothing changed.
git -C "%REPO%" diff --cached --quiet
if %ERRORLEVEL%==0 (
    echo nothing to deploy - help site and docs are already up to date.
    goto :eof
)

git -C "%REPO%" commit -m "Deploy help site and API docs" || goto :error
git -C "%REPO%" push || goto :error

echo help site and API docs deployed to the gh-pages branch (GitHub Pages will publish shortly).
goto :eof

:error
echo deploy failed.
exit /b 1
