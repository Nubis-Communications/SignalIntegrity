#!/bin/bash
# if coverage doesn't work, try python-coverage
coverage run --source='../SignalIntegrity/' ./TestSignalIntegrity/TestAll.py > /dev/null
coverage html -d CoverageReport
coverage erase
#read -p "Press [Enter] key to continue..."
firefox "file:"$PWD"/CoverageReport/index.html" > /dev/null
read -p "Press [Enter] key to continue..."
rm -rf CoverageReport
