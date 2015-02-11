set PYTHONPATH=%PYTHONPATH%;C:\Users\peter.pupalaikis\Work\Books\LyxBook\PythonSource
coverage erase
coverage -x .\TestSignalIntegrity\TestAll.py
coverage html -d CoverageReport
coverage erase
explorer .\CoverageReport\Index.html