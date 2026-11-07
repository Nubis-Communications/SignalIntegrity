@echo off
REM Usage: RunFast.bat [SECONDS]   (default threshold: 1.0 seconds)
set THRESHOLD=%1
if "%THRESHOLD%"=="" set THRESHOLD=1.0
set PYTHONPATH=%PYTHONPATH%;.
python .\TestSignalIntegrity\RunTimedTests.py --faster-than %THRESHOLD%
pause
