
#!/bin/bash
export PYTHONPATH=${PYTHONPATH}:~/Work/Books/LyxBook/PythonSource
cd ~/Work/Books/LyxBook/PythonSource
python-coverage -x ./TestSignalIntegrity/TestAll.py > /dev/null
python-coverage html -d CoverageReport
python-coverage erase
#read -p "Press [Enter] key to continue..."
firefox file:///home/peterp/Work/Books/LyxBook/PythonSource/CoverageReport/index.html > /dev/null
read -p "Press [Enter] key to continue..."
rm -rf CoverageReport
