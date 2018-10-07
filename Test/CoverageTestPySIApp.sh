#!/bin/bash
python-coverage run --source='../SignalIntegrity/,../PySIApp/' ./TestPySIApp/TestPySIApp.py > /dev/null
python-coverage html -d CoverageReport
python-coverage erase
#read -p "Press [Enter] key to continue..."
firefox "file:"$PWD"/CoverageReport/index.html" > /dev/null
read -p "Press [Enter] key to continue..."
rm -rf CoverageReport
