import SignalIntegrity as si
import os
from cStringIO import StringIO
import sys

SD=si.sd.SystemDescription()
SD.AddDevice('F',4)
SD.AddDevice('?1',1)
SD.AddDevice('?2',1)
SD.AddPort('F',1,1)
SD.AddPort('F',2,2)
SD.ConnectDevicePort('F',3,'?1',1)
SD.ConnectDevicePort('F',4,'?2',1)
#old_stdout = sys.stdout
#sys.stdout = mystdout = StringIO()
#sd.Print()  # print the system description
spc = si.sd.Deembedder(SD)
symbolic=si.sd.SymbolicDeembedder(spc,True,True)
symbolic.SymbolicSolution()
#sys.stdout = old_stdout
os.chdir(os.path.dirname(os.path.realpath(__file__)))
fileName = 'output.tex'
if not os.path.exists(fileName):
    symbolic.WriteToFile(fileName)
regression=''
with open(fileName, 'r') as regressionFile:
    for line in regressionFile:
        regression = regression + line
comparison = symbolic.Get()
print regression == comparison