#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      peter.pupalaikis
#
# Created:     11/03/2015
# Copyright:   (c) peter.pupalaikis 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os
import sys
from cStringIO import StringIO
import SignalIntegrity as si

class SParameterCompareHelper(object):
    def SParametersAreEqual(self,lhs,rhs,epsilon):
        if len(lhs) != len(rhs): return False
        if len(lhs.m_d) != len(rhs.m_d): return False
        for n in range(len(lhs.Data())):
            if abs(lhs.m_f[n] - rhs.m_f[n]) > epsilon: return False
            for r in range(lhs.m_P):
                for c in range(lhs.m_P):
                    if abs(lhs.m_d[n][r][c] - rhs.m_d[n][r][c]) > epsilon:
                        return False
        return True


class ResponseTesterHelper(SParameterCompareHelper):
    def CheckFrequencyResponseResult(self,fr,fileName,text):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if not os.path.exists(fileName):
            fr.WriteToFile(fileName)
            self.assertTrue(False, fileName + ' not found')
        regression=si.sp.FrequencyResponse().ReadFromFile(fileName)
        os.chdir(path)
        self.assertTrue(regression == fr,text + ' incorrect')
    def GetFrequencyResponseResult(self,fileName):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if not os.path.exists(fileName):
            return None
        regression=si.sp.FrequencyResponse().ReadFromFile(fileName)
        os.chdir(path)
        return regression
    def CheckWaveformResult(self,wf,fileName,text):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if not os.path.exists(fileName):
            wf.WriteToFile(fileName)
            self.assertTrue(False, fileName + ' not found')
        regression=si.td.wf.Waveform().ReadFromFile(fileName)
        os.chdir(path)
        self.assertTrue(regression == wf,text + ' incorrect')
    def GetWaveformResult(self,fileName):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if not os.path.exists(fileName):
            return None
        regression=si.td.wf.Waveform().ReadFromFile(fileName)
        os.chdir(path)
        return regression
    def CheckSParametersResult(self,sp,fileName,text):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if not os.path.exists(fileName):
            sp.WriteToFile(fileName)
            self.assertTrue(False, fileName + ' not found')
        regression=si.sp.File(fileName)
        os.chdir(path)
        self.assertTrue(self.SParametersAreEqual(sp,regression,0.00001),text + ' incorrect')

class SourcesTesterHelper(object):
    def CheckSymbolicResult(self,selfid,symbolic,Text):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileName = '_'.join(selfid.split('.')) + '.tex'
        fileName = ('_'.join(selfid.split('.')[2:])).replace('test','') + '.tex'
        if not os.path.exists(fileName):
            symbolic.WriteToFile(fileName)
            self.assertTrue(False, fileName + ' not found')
        regression=''
        with open(fileName, 'rU') as regressionFile:
            for line in regressionFile:
                regression = regression + line
        comparison = symbolic.Get()
        self.assertTrue(regression == comparison,Text + ' incorrect with ' + fileName)

class RoutineWriterTesterHelper(object):
    def __init__(self, methodName='runTest'):
        self.standardHeader = ['import SignalIntegrity as si\n','\n']
    def CheckRoutineWriterResult(self,fileName,sourceCode,Text):
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
        self.CheckRoutineWriterResult(scriptFileName,sourceCode,Routine + ' source code')
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
