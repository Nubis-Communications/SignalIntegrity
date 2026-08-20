@echo off
set PYTHONPATH=%PYTHONPATH%;.
python .\TestSignalIntegrity\RunTimedTests.py --record
pause
