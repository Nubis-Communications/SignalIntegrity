#!/bin/bash
export PYTHONPATH=$PYTHONPATH:~/Work/Books/LyxBook/PythonSource
export PYTHONPATH=$PYTHONPATH:~/Work/Books/LyxBook/PythonSource/TestSignalIntegrity
export PYTHONPATH=$PYTHONPATH:/usr/lib/python2.7
export PYTHONPATH=$PYTHONPATH:/usr/lib/python2.7/dist-packages
cd ~/Work/Books/LyxBook/PythonSource
python-coverage -o '/usr/*' -x ~/Work/Books/LyxBook/PythonSource/TestSignalIntegrity/TestAll.py > /dev/null
python-coverage html -d CoverageReport
python-coverage erase
#read -p "Press [Enter] key to continue..."
firefox file:///home/peterp/Work/Books/LyxBook/PythonSource/CoverageReport/index.html > /dev/null
read -p "Press [Enter] key to continue..."
rm -rf CoverageReport
