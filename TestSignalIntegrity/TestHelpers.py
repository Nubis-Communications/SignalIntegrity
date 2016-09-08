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
        if lhs.m_P != rhs.m_P: return False
        if lhs.m_Z0 != rhs.m_Z0: return False
        if len(lhs) != len(rhs): return False
        for n in range(len(lhs)):
            if abs(lhs.m_f[n] - rhs.m_f[n]) > epsilon: return False
            lhsn=lhs[n]
            rhsn=rhs[n]
            for r in range(lhs.m_P):
                for c in range(lhs.m_P):
                    if abs(lhsn[r][c] - rhsn[r][c]) > epsilon:
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
        regression=si.sp.SParameterFile(fileName,50.)
        os.chdir(path)
        self.assertTrue(self.SParametersAreEqual(sp,regression,0.00001),text + ' incorrect')

class SourcesTesterHelper(object):
    def CheckSymbolicResult(self,selfid,symbolic,Text):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
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
        indent=4
        with open(fileName, 'rU') as inputFile:
            for line in inputFile:
                if len(line.split())>=2:
                    pragmaLine = ('pragma:' == line.split()[1])
                else:
                    pragmaLine = False
                if "def" == line.lstrip(' ').split(' ')[0]:
                    addingLines = False
                    if Routine in line:
                        addingLines = True
                        includingLines = True
                        if printFuncName:
                            line = line.replace('test','').replace('self','')
                            sourceCode.append(line[indent:])
                        continue
                if addingLines:
                    if pragmaLine:
                        tokens=line.split()
                        pindex=tokens.index('pragma:')
                        tokens=[tokens[i] for i in range(pindex,len(tokens))]
                        for token in tokens:
                            if token == 'exclude':
                                includingLines = False
                            elif token == 'include':
                                includingLines = True
                            elif token == 'outdent':
                                indent = indent+4
                            elif token == 'indent':
                                indent = indent-4
                        continue
                    if includingLines:
                        if printFuncName:
                            sourceCode.append(line[indent:])
                        else:
                            sourceCode.append(line[indent+4:])
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
    def EntireListOfClassFunctions(self,fileName,className):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        defName=[]
        inClass= className is ''
        with open(fileName, 'rU') as inputFile:
            for line in inputFile:
                if "class" == line.lstrip(' ').split(' ')[0]:
                    if className == line.lstrip(' ').split(' ')[1].split('(')[0]:
                        inClass = True
                    else:
                        inClass = False
                elif "def" == line.lstrip(' ').split(' ')[0]:
                    if inClass:
                        defName.append(line.lstrip(' ').split(' ')[1].split('(')[0])
        return defName
    def WriteClassCode(self,fileName,className,defName,checkNames=True,lineDefs=False):
        if isinstance(defName,str):
            defName=[defName]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        outputFileName=fileName.split('/')[-1].split('.')[0]+'_'+className+'_'+defName[0]
        lineDefFileName=outputFileName+'_LineNums.tex'
        outputFileName=outputFileName+'.py'
        if checkNames:
            allDefNames = self.EntireListOfClassFunctions(fileName,className)
            self.assertTrue(all([name in allDefNames for name in defName]), 'def names wrong for '+outputFileName)
        inClass= className is ''
        inDef=False
        addingLines=False
        sourceCode=[]
        indent=0
        lineDef=[]
        with open(fileName, 'rU') as inputFile:
            lineNumber=1
            for line in inputFile:
                if len(line.split())>=2:
                    pragmaLine = ('pragma:' == line.split()[1])
                else:
                    pragmaLine = False
                if "class" == line.lstrip(' ').split(' ')[0]:
                    if className == line.lstrip(' ').split(' ')[1].split('(')[0]:
                        inClass = True
                        inDef = False
                        addingLines = True
                        lineNumber=1
                    else:
                        inClass = False
                        inDef = False
                        addingLines = False
                elif "def" == line.lstrip(' ').split(' ')[0]:
                    if inClass:
                        thisDefName=line.lstrip(' ').split(' ')[1].split('(')[0]
                        if any(d == thisDefName for d in defName):
                            inDef=True
                            defMacro=className+'_'+thisDefName+'_Num'
                            defMacro=''.join(ch for ch in defMacro if ch.isalpha())
                            defLine='\\def\\'+defMacro+'{'+str(lineNumber)+'}\n'
                            lineDef=lineDef+[defLine]
                            """
                            if not addingLines:
                                sourceCode.append("...")
                            """
                            addingLines=True
                        else:
                            if addingLines:
                                sourceCode.append("...\n")
                                lineNumber=lineNumber+1
                            inDef=False
                            addingLines=False
                    else:
                        inDef=False
                        addingLines=False
                elif pragmaLine:
                        tokens=line.split()
                        pindex=tokens.index('pragma:')
                        tokens=[tokens[i] for i in range(pindex,len(tokens))]
                        silent=False
                        for token in tokens:
                            if token == 'silent':
                                silent=True
                            if token == 'exclude':
                                if inDef:
                                    if addingLines:
                                        if not silent:
                                            sourceCode.append("...\n")
                                            lineNumber=lineNumber+1
                                    addingLines = False
                            elif token == 'include':
                                if inDef:
                                    addingLines = True
                            elif token == 'outdent':
                                indent = indent+4
                            elif token == 'indent':
                                indent = indent-4
                        continue
                else:
                    if addingLines:
                        if not inDef:
                            addingLines=False
                if addingLines is True:
                    sourceCode.append(line[indent:])
                    lineNumber=lineNumber+1
        if not os.path.exists(outputFileName):
            with open(outputFileName, 'w') as outputFile:
                for line in sourceCode:
                    outputFile.write(line)
        with open(outputFileName, 'rU') as regressionFile:
            regression = regressionFile.readlines()
        self.assertTrue(regression == sourceCode, outputFileName + ' incorrect')
        if lineDefs:
            if not os.path.exists(lineDefFileName):
                with open(lineDefFileName, 'w') as outputFile:
                    for line in lineDef:
                        outputFile.write(line)
            with open(lineDefFileName, 'rU') as regressionFile:
                regression = regressionFile.readlines()
            self.assertTrue(regression == lineDef, lineDefFileName + ' incorrect')

class CallbackTesterHelper(object):
    def __init__(self):
        self.InitCallbackTester()
    def InitCallbackTester(self,abortOn=-1):
        self.abortOn=abortOn
        self.numProgress=0
        self.firstProgress=None
        self.lastProgress=None
    def CallbackTester(self,progress):
        if self.numProgress == 0:
            self.firstProgress=progress
        self.lastProgress=progress
        self.numProgress=self.numProgress+1
        if self.numProgress == self.abortOn:
            return False
        else:
            return True  
    def CallBackTesterResults(self):
        return [self.numProgress,self.firstProgress,self.lastProgress]
    def CheckCallbackTesterResults(self,correct):
        return correct == self.CallBackTesterResults()


