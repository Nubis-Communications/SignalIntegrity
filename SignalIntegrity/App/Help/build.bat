@echo off
REM Build the SignalIntegrity MkDocs help site and (re)generate the helpkeys index.
REM
REM This replaces the old LyX + eLyXer 'converthelp.bat' workflow.
REM
REM Prerequisites:
REM   pip install mkdocs pillow pymdown-extensions
REM   (content is produced separately by convert_help.py, which needs lyx + pandoc)
setlocal
cd /d "%~dp0"

REM Build the static site into .\site
mkdocs build --clean || goto :error

REM Generate .\site\helpkeys from the anchor ids in the built HTML.
python gen_helpkeys.py site || goto :error

echo help site built in .\site (open .\site\index.html)
goto :eof

:error
echo build failed.
exit /b 1
