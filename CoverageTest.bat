@echo off
set PYTHONPATH=%PYTHONPATH%;C:\Users\peter.pupalaikis\Work\Books\LyxBook\PythonSource
coverage erase
coverage -x .\TestSignalIntegrity\TestAll.py >NUL
coverage html -d CoverageReport
coverage erase
pause
START /WAIT explorer .\CoverageReport\Index.html
pause
rmdir /S /Q CoverageReport