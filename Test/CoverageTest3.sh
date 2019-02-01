#!/bin/bash
python3-coverage run --source='../SignalIntegrity/' ./TestSignalIntegrity/TestAll.py > /dev/null
python3-coverage html -d CoverageReport
python3-coverage erase
#read -p "Press [Enter] key to continue..."
firefox "file:"$PWD"/CoverageReport/index.html" > /dev/null
read -p "Press [Enter] key to continue..."
rm -rf CoverageReport
