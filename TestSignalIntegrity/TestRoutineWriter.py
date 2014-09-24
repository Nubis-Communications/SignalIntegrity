import unittest

import os
from cStringIO import StringIO
import sys
import SignalIntegrity as si

class TestRoutineWriter(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        self.standardHeader = ['from SignalIntegrity import si\n','\n']
        unittest.TestCase.__init__(self,methodName)
    def CheckResult(self,selfid,sourceCode,Text):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileName = ('_'.join(selfid.split('.')[2:])).replace('test','') + '.py'
        if not os.path.exists(fileName):
            sourceCodeFile=open(fileName,'w')
            for line in sourceCode:
                sourceCodeFile.write(line)
            sourceCodeFile.close()
            self.assertTrue(False, fileName + ' not found')
        regression=[]
        with open(fileName, 'r') as regressionFile:
            for line in regressionFile:
                regression.append(line)
        self.assertTrue(regression == sourceCode,Text + ' incorrect')
    def WriteCode(self,fileName,Routine,headerLines,printFuncName=False):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sourceCode = []
        sourceCode.extend(headerLines)
        addingLines = False
        with open(fileName, 'r') as inputFile:
            for line in inputFile:
                if 'def' in line:
                    addingLines = False
                    if Routine in line:
                        addingLines = True
                        includingLines = True
                        if printFuncName:
                            line = line.replace('test','').replace('self','')
                            sourceCode.append(line[4:])
                        continue
                if addingLines:
                    if '# exclude' in line:
                        includingLines = False
                        continue
                    if '# include' in line:
                        includingLines = True
                        continue
                    if includingLines:
                        if printFuncName:
                            sourceCode.append(line[4:])
                        else:
                            sourceCode.append(line[8:])
        self.CheckResult(self.id(),sourceCode,Routine + ' source code')
    def testVoltageAmplifier2Code(self):
        self.WriteCode('TestSources.py','testVoltageAmplifier2Full(self)',self.standardHeader)
    def testVoltageAmplifier4Code(self):
        self.WriteCode('TestSources.py','testVoltageAmplifier4(self)',self.standardHeader)

if __name__ == '__main__':
    unittest.main()