#!/bin/bash
python-coverage run --source='../SignalIntegrity/,../PySIApp/' ./TestSignalIntegrity/TestAll.py > /dev/null
python-coverage html -d CoverageReport
python-coverage erase
#read -p "Press [Enter] key to continue..."
firefox "file:"$PWD"/CoverageReport/index.html" > /dev/null
read -p "Press [Enter] key to continue..."
rm -rf CoverageReport
