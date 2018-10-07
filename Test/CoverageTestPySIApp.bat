@echo off
set PYTHONPATH=%PYTHONPATH%;.
coverage erase
coverage run .\TestPySIApp\TestPySIApp.py >NUL
coverage html -d CoverageReport
coverage erase
pause
START /WAIT explorer .\CoverageReport\Index.html
pause
rmdir /S /Q CoverageReport
