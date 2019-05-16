"""
TestHelpers.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

import os
import sys

if sys.version_info.major < 3:
    from cStringIO import StringIO
else:
    from io import StringIO

from SignalIntegrity.Lib.FrequencyDomain.FrequencyResponse import FrequencyResponse
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.Lib.SParameters.SParameterFile import SParameterFile

def PlotTikZ(filename,plot2save,scale=None):
    try:
        from matplotlib2tikz import save as tikz_save
        import matplotlib
    except:
        return

    if not isinstance(plot2save,matplotlib.figure.Figure):
        plot2save=plot2save.gcf()
    try:
        tikz_save(filename,figure=plot2save,show_info=False,float_format='%.6g')
    except:
        tikz_save(filename,figure=plot2save,show_info=False)
    texfile=open(filename,'rU' if sys.version_info.major < 3 else 'r')
    lines=[]
    for line in texfile:
        line=line.replace('\xe2\x88\x92','-')
        if not scale is None:
            line=line.replace('begin{tikzpicture}','begin{tikzpicture}[scale='+str(scale)+']')
        lines.append(str(line))
    texfile.close()
    texfile=open(filename,'w')
    for line in lines:
        texfile.write(line)
    texfile.close()

class SParameterCompareHelper(object):
    def SParametersAreEqual(self,lhs,rhs,epsilon=0.00001):
        if lhs.m_P != rhs.m_P: return False
        if lhs.m_Z0 != rhs.m_Z0: return False
        if len(lhs) != len(rhs): return False
        for n in range(len(lhs)):
            if abs(lhs.m_f[n] - rhs.m_f[n]) > .1:
                return False
            lhsn=lhs[n]
            rhsn=rhs[n]
            for r in range(lhs.m_P):
                for c in range(lhs.m_P):
                    if abs(lhsn[r][c] - rhsn[r][c]) > epsilon:
                        return False
        return True

class ResponseTesterHelper(SParameterCompareHelper):
    plotErrors=True
    def CheckFrequencyResponseResult(self,fr,fileName,text):
        #path=os.getcwd()
        #os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if not os.path.exists(fileName):
            fr.WriteToFile(fileName)
            self.assertTrue(False, fileName + ' not found')
        regression=FrequencyResponse().ReadFromFile(fileName)
        #os.chdir(path)
        self.assertTrue(regression == fr,text + ' incorrect')
    def GetFrequencyResponseResult(self,fileName):
        #path=os.getcwd()
        #os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if not os.path.exists(fileName):
            return None
        regression=FrequencyResponse().ReadFromFile(fileName)
        #os.chdir(path)
        return regression
    def CheckWaveformResult(self,wf,fileName,text):
        #path=os.getcwd()
        #os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if not os.path.exists(fileName):
            wf.WriteToFile(fileName)
            self.assertTrue(False, fileName + ' not found')
        regression=Waveform().ReadFromFile(fileName)
        wfsAreEqual=(regression==wf)
        if not wfsAreEqual:
            if ResponseTesterHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title(fileName)
                plt.xlabel('time (s)')
                plt.ylabel('amplitude')
                plt.semilogy(regression.Times(),[abs(wf[k]-regression[k]) for k in range(len(regression))])
                plt.grid(True)
                plt.show()

                plt.clf()
                plt.title(fileName)
                plt.xlabel('time (s)')
                plt.ylabel('amplitude')
                plt.plot(wf.Times(),wf.Values(),label='calculated')
                plt.plot(regression.Times(),regression.Values(),label='regression')
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()
        #os.chdir(path)
        self.assertTrue(wfsAreEqual,text + ' incorrect')
    def GetWaveformResult(self,fileName):
        #path=os.getcwd()
        #os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if not os.path.exists(fileName):
            return None
        regression=Waveform().ReadFromFile(fileName)
        #os.chdir(path)
        return regression
    def CheckSParametersResult(self,sp,fileName,text):
        #path=os.getcwd()
        #os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if not os.path.exists(fileName):
            sp.WriteToFile(fileName)
            self.assertTrue(False, fileName + ' not found')
        regression=SParameterFile(fileName,50.)
        #os.chdir(path)
        self.assertTrue(self.SParametersAreEqual(sp,regression,0.00001),text + ' incorrect')

class SourcesTesterHelper(object):
    def CheckSymbolicResult(self,selfid,symbolic,Text):
        #os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileName = ('_'.join(selfid.split('.')[-1:])).replace('test','') + '.tex'
        if not os.path.exists(fileName):
            symbolic.WriteToFile(fileName)
            self.assertTrue(False, fileName + ' not found')
        regression=''
        with open(fileName, 'rU' if sys.version_info.major < 3 else 'r') as regressionFile:
            for line in regressionFile:
                regression = regression + line
        comparison = symbolic.Get()
        self.assertTrue(regression == comparison,Text + ' incorrect with ' + fileName)

class RoutineWriterTesterHelper(object):
    maxNumLines=65
    maxLineLength=88
    def __init__(self, methodName='runTest'):
        self.standardHeader = ['import SignalIntegrity.Lib as si\n']
    def execfile(self,filepath, globals=None, locals=None):
        if globals is None:
            globals = {}
        globals.update({
            "__file__": filepath,
            "__name__": "__main__",
        })
        with open(filepath, 'rb') as file:
            exec(compile(file.read(), filepath, 'exec'), globals, locals)

    def CheckRoutineWriterResult(self,fileName,sourceCode,Text):
        #os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if not os.path.exists(fileName):
            sourceCodeFile=open(fileName,'w')
            for line in sourceCode:
                sourceCodeFile.write(line)
            sourceCodeFile.close()
            self.assertTrue(False, fileName + ' not found')
        regression=[]
        with open(fileName, 'rU' if sys.version_info.major < 3 else 'r') as regressionFile:
            regression = regressionFile.readlines()
#             for line in regressionFile:
#                 regression.append(line)
        self.assertTrue(regression == sourceCode,Text + ' incorrect')
    def WriteCode(self,fileName,Routine,headerLines,printFuncName=False):
        #os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sourceCode = []
        sourceCode.extend(headerLines)
        addingLines = False
        indent=4
        with open(fileName, 'rU' if sys.version_info.major < 3 else 'r') as inputFile:
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
                            line = line.replace('test','').replace('self,','').replace('self','')
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
                            lineToAppend=line[indent+4:]
                            if len(lineToAppend)==0:
                                lineToAppend='\n'
                            if lineToAppend[-1]!='\n':
                                lineToAppend=lineToAppend+'\n'
                            sourceCode.append(lineToAppend)
        scriptName = Routine.replace('test','')
        scriptName = Routine.replace('test','').replace('(self)','').replace('(self,)','')
        splitscriptName=scriptName.split('(')
        if len(splitscriptName)==2:
            scriptName=splitscriptName[0]
        scriptFileName=scriptName + 'Code.py'
        self.CheckRoutineWriterResult(scriptFileName,sourceCode,Routine + ' source code')
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        self.execfile(scriptFileName)
        sys.stdout = old_stdout
        outputFileName = scriptName + '.po'
        if not os.path.exists(outputFileName):
            resultFile = open(outputFileName, 'w')
            resultFile.write(mystdout.getvalue())
            resultFile.close()
            self.assertTrue(False, outputFileName + ' not found')
        regressionFile = open(outputFileName, 'rU' if sys.version_info.major < 3 else 'r')
        regression = regressionFile.read()
        regressionFile.close()
        self.assertTrue(regression == mystdout.getvalue(), outputFileName + ' incorrect')
    def EntireListOfClassFunctions(self,fileName,className):
        #os.chdir(os.path.dirname(os.path.realpath(__file__)))
        defName=[]
        inClass= className is ''
        with open(fileName, 'rU' if sys.version_info.major < 3 else 'r') as inputFile:
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
        #os.chdir(os.path.dirname(os.path.realpath(__file__)))
        outputFileName=fileName.split('/')[-1].split('.')[0]+'_'+className+'_'+defName[0]
        outputFileName=outputFileName.replace('Test','')
        lineDefFileName=outputFileName+'_LineNums.tex'
        outputFileName=outputFileName+'.py'
        if checkNames:
            allDefNames = self.EntireListOfClassFunctions(fileName,className)
            self.assertTrue(all([name in allDefNames for name in defName]), 'def names wrong for '+outputFileName)
        inClass= className is ''
        inDef=False
        addingLines=False
        strippingDoc=False
        sourceCode=[]
        indent=0
        lineDef=[]
        inputFile = DocStripped(fileName)
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
                    strippingDoc=False
                    lineNumber=1
                else:
                    inClass = False
                    inDef = False
                    addingLines = False
                    strippingDoc=False
            elif "def" == line.lstrip(' ').split(' ')[0]:
                if inClass:
                    thisDefName=line.lstrip(' ').split(' ')[1].split('(')[0]
                    if any(d == thisDefName for d in defName):
                        inDef=True
                        defMacro=className+'_'+thisDefName+'_Num'
                        defMacro=''.join(ch for ch in defMacro if ch.isalpha())
                        defLine='\\def\\'+defMacro+'{'+str(lineNumber)+'}\n'
                        lineDef=lineDef+[defLine]
                        addingLines=True
                        strippingDoc=False
                    else:
                        if addingLines:
                            sourceCode.append("...\n")
                            lineNumber=lineNumber+1
                        inDef=False
                        addingLines=False
                        strippingDoc=False
                else:
                    inDef=False
                    addingLines=False
                    strippingDoc=False
            elif pragmaLine:
                strippingDoc=False
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
                    if '##' == line.lstrip(' ').split(' ')[0]:
                        strippingDoc=True
                    if not inDef and not strippingDoc:
                        addingLines=False
                        strippingDoc=False
            if addingLines and not strippingDoc:
                sourceCode.append(line[indent:])
                lineNumber=lineNumber+1
        if not os.path.exists(outputFileName):
            with open(outputFileName, 'w') as outputFile:
                for line in sourceCode:
                    outputFile.write(line)
        regression=DocStripped(outputFileName,False).doc
        self.assertTrue(regression == sourceCode, outputFileName + ' incorrect')
#         for line in regression:
#             if len(line)>self.maxLineLength:
#                 print line
        self.assertTrue(max([len(line) for line in regression])<=self.maxLineLength,outputFileName + ' has line that is too long: ')

        self.assertTrue(len(regression)<=self.maxNumLines,outputFileName + ' has too many lines: '+str(len(regression)))
        if lineDefs:
            if not os.path.exists(lineDefFileName):
                with open(lineDefFileName, 'w') as outputFile:
                    for line in lineDef:
                        outputFile.write(line)
            with open(lineDefFileName, 'rU' if sys.version_info.major < 3 else 'r') as regressionFile:
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

class DocStripped(object):
    def __init__(self,filename,strip=True):
        self.doc=[]
        inDocString=False
        with open(filename, 'rU' if sys.version_info.major < 3 else 'r') as inputFile:
            for line in inputFile:
                if not strip:
                    self.doc.append(line)
                    continue
                if line.count('"""')==1:
                    inDocString=not inDocString
                    continue
                elif line.count('"""')==2:
                    continue
                if not inDocString:
                    self.doc.append(line)
    def __len__(self):
        return len(self.doc)
    def __getitem__(self,item):
        return self.doc[item]



