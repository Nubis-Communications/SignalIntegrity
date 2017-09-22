#!/bin/bash
export PYTHONPATH=$PYTHONPATH:~/Work/PySI
export PYTHONPATH=$PYTHONPATH:~/Work/PySI/TestSignalIntegrity
export PYTHONPATH=$PYTHONPATH:/usr/lib/python2.7
export PYTHONPATH=$PYTHONPATH:/usr/lib/python2.7/dist-packages
cd ~/Work/PySI
python-coverage -o '/usr/*' -x ~/Work/PySI/TestPySIApp/TestPySIApp.py > /dev/null
python-coverage html -d CoverageReport
python-coverage erase
#read -p "Press [Enter] key to continue..."
firefox file:///home/peterp/Work/PySI/CoverageReport/index.html > /dev/null
read -p "Press [Enter] key to continue..."
rm -rf CoverageReport
