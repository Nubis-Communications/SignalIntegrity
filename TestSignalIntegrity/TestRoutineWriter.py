import unittest

import os
from cStringIO import StringIO
import sys
import SignalIntegrity as si

class TestRoutineWriter(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        self.standardHeader = ['import SignalIntegrity as si\n','\n']
        unittest.TestCase.__init__(self,methodName)
    def CheckResult(self,fileName,sourceCode,Text):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if not os.path.exists(fileName):
            sourceCodeFile=open(fileName,'w')
            for line in sourceCode:
                sourceCodeFile.write(line)
            sourceCodeFile.close()
            self.assertTrue(False, fileName + ' not found')
        regression=[]
        with open(fileName, 'rU') as regressionFile:
            for line in regressionFile:
                regression.append(line)
        self.assertTrue(regression == sourceCode,Text + ' incorrect')
    def WriteCode(self,fileName,Routine,headerLines,printFuncName=False):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sourceCode = []
        sourceCode.extend(headerLines)
        addingLines = False
        with open(fileName, 'rU') as inputFile:
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
        scriptName = Routine.replace('test','').replace('(self)','')
        scriptFileName=scriptName + 'Code.py'
        self.CheckResult(scriptFileName,sourceCode,Routine + ' source code')
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        execfile(scriptFileName)
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sys.stdout = old_stdout
        outputFileName = scriptName + '.po'
        if not os.path.exists(outputFileName):
            resultFile = open(outputFileName, 'w')
            resultFile.write(mystdout.getvalue())
            resultFile.close()
            self.assertTrue(False, outputFileName + ' not found')
        regressionFile = open(outputFileName, 'rU')
        regression = regressionFile.read()
        regressionFile.close()
        self.assertTrue(regression == mystdout.getvalue(), outputFileName + ' incorrect')
    def testVoltageAmplifierFourPortCode(self):
        self.WriteCode('TestSources.py','testVoltageAmplifierFourPort(self)',self.standardHeader)
    def testVoltageAmplifierTwoPortCode(self):
        self.WriteCode('TestSources.py','testVoltageAmplifierTwoPort(self)',self.standardHeader)
    def testVoltageAmplifierTwoPortAlternateCode(self):
        self.WriteCode('TestSources.py','testVoltageAmplifierTwoPortAlternate(self)',self.standardHeader)
    def testVoltageAmplifierThreePortCode(self):
        self.WriteCode('TestSources.py','testVoltageAmplifierThreePort(self)',self.standardHeader)
    def testVoltageAmplifierThreePortAlternateCode(self):
        self.WriteCode('TestSources.py','testVoltageAmplifierThreePortAlternate(self)',self.standardHeader)
    def testExampleCode(self):
        self.WriteCode('TestSystemDescription.py','testSystemDescriptionExampleBlock(self)',self.standardHeader)
    def testSymbolicSolutionExample1Code(self):
        self.WriteCode('TestBook.py','testSymbolicSolutionExample1(self)',self.standardHeader)
    def testSymbolicSolutionParserExample2Code(self):
        self.WriteCode('TestBook.py','testSymbolicSolutionParserExample2(self)',self.standardHeader)
    def testSymbolicSolutionParserFileExample3Code(self):
        self.WriteCode('TestBook.py','testSymbolicSolutionParserFileExample3(self)',self.standardHeader)
    def testSystemDescriptionExampleCode(self):
        self.WriteCode('TestBook.py','testSystemDescriptionExample(self)',self.standardHeader)
    def testSymbolicDeembeddingExample1Code(self):
        self.WriteCode('TestBook.py','testSymbolicDeembeddingExample1(self)',self.standardHeader)
    def testSymbolicDeembeddingParserExample2Code(self):
        self.WriteCode('TestBook.py','testSymbolicDeembeddingParserExample2(self)',self.standardHeader)
    def testSymbolicDeembeddingParserFileExample3Code(self):
        self.WriteCode('TestBook.py','testSymbolicDeembeddingParserFileExample3(self)',self.standardHeader)
    def testSymbolicDeembeddingExample4Code(self):
        self.WriteCode('TestBook.py','testSymbolicDeembeddingExample4(self)',self.standardHeader)
    def testSymbolicDeembeddingExample5Code(self):
        self.WriteCode('TestBook.py','testSymbolicDeembeddingExample5(self)',self.standardHeader)
    def testSymbolicVirtualProbeExample1Code(self):
        self.WriteCode('TestBook.py','testSymbolicVirtualProbeExample1(self)',self.standardHeader)
    def testSymbolicVirtualProbeExample2Code(self):
        self.WriteCode('TestBook.py','testSymbolicVirtualProbeExample2(self)',self.standardHeader)
    def testSymbolicVirtualProbeExample3Code(self):
        self.WriteCode('TestBook.py','testSymbolicVirtualProbeExample3(self)',self.standardHeader)
    def testSymbolicVirtualProbeParserFileExample4Code(self):
        self.WriteCode('TestBook.py','testSymbolicVirtualProbeParserFileExample4(self)',self.standardHeader)
    def testSymbolicTransistorSimpleCode(self):
        self.WriteCode('TestSources.py','testSymbolicTransistorSimple(self)',self.standardHeader)
    def testSymbolicTransistorZoCode(self):
        self.WriteCode('TestSources.py','testSymbolicTransistorZO(self)',self.standardHeader)
    def testOpAmpNoZD(self):
        self.WriteCode('TestSources.py','testOperationalAmplifierNoZD(self)',self.standardHeader)
    def testOpAmpAgain(self):
        self.WriteCode('TestSources.py','testOperationalAmplifierAgain(self)',self.standardHeader)
    def testIdealTransformerSymbolic(self):
        self.WriteCode('TestSources.py','testIdealTransformerSymbolic(self)',self.standardHeader)
    def testVoltageAmplifierTwoPortVoltageSeriesFeedbackCode(self):
        self.WriteCode('TestSources.py','testVoltageAmplifierTwoPortVoltageSeriesFeedback(self)',self.standardHeader)
    def testVoltageAmplifierFourPortVoltageSeriesFeedbackCode(self):
        self.WriteCode('TestSources.py','testVoltageAmplifierFourPortVoltageSeriesFeedback(self)',self.standardHeader)
    def testVoltageAmplifierFourPortVoltageSeriesFeedbackAlternateCode(self):
        self.WriteCode('TestSources.py','testVoltageAmplifierFourPortVoltageSeriesFeedbackAlternate(self)',self.standardHeader)
    def testCurrentAmplifierFourPortCode(self):
        self.WriteCode('TestSources.py','testCurrentAmplifierFourPort(self)',self.standardHeader)
    def testTransconductanceAmplifierFourPortCode(self):
        self.WriteCode('TestSources.py','testTransconductanceAmplifierFourPort(self)',self.standardHeader)
    def testTransresistanceAmplifierFourPortCode(self):
        self.WriteCode('TestSources.py','testTransresistanceAmplifierFourPort(self)',self.standardHeader)

if __name__ == '__main__':
    unittest.main()