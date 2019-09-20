"""
TestBook.py
"""
from __future__ import print_function

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
import unittest
import os
import sys
from __builtin__ import set

class TestBookFormattingTest(unittest.TestCase):
    bookpath='../../../SignalIntegrityBook/'
    pythonpath='../../SignalIntegrity/'
    testpath='./'

    def LyxFileList(self):
        lyxFileList=[]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        for root, dirs, files in os.walk(self.bookpath):
            for file in files:
                if file.endswith(".lyx"):
                    lyxFileList.append(os.path.join(root, file))
        return lyxFileList
    
    def _PythonFileList(self):
        pythonFileList=[]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        for root, dirs, files in os.walk(self.pythonpath):
            for file in files:
                if file.endswith(".py"):
                    pythonFileList.append(os.path.join(root, file))
        return pythonFileList
    
    def _TestFileList(self):
        pythonFileList=[]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        for root, dirs, files in os.walk(self.testpath):
            for file in files:
                if file.endswith(".py"):
                    pythonFileList.append(os.path.join(root, file))
        return pythonFileList

    def AllFileList(self):
        return self._PythonFileList()+self._TestFileList()

    def PythonClassList(self,filename):
        classList=[]
        with open(filename,'r') as f:
            lines=f.readlines()

        for line in lines:
            tokens=line.split(' ')
            while '' in tokens:
                tokens.remove('')
            if len(tokens)>=2:
                if tokens[0]=='class':
                    partialClassName=tokens[1]
                    classNameTokens=partialClassName.split('(')
                    if len(classNameTokens)>=2:
                        classList.append(classNameTokens[0])
        return classList

    def TotalClassList(self):
        PythonClassList=set()
        pythonFiles=self.AllFileList()
        for filename in pythonFiles:
            classList=self.PythonClassList(filename)
            PythonClassList.update(classList)
        return PythonClassList

    def PythonFuncList(self,filename):
        funcList=[]
        with open(filename,'r') as f:
            lines=f.readlines()

        for line in lines:
            tokens=line.split(' ')
            while '' in tokens:
                tokens.remove('')
            if len(tokens)>=2:
                if tokens[0]=='def':
                    partialFuncName=tokens[1]
                    classNameTokens=partialFuncName.split('(')
                    if len(classNameTokens)>=2:
                        funcList.append(classNameTokens[0])
        return funcList
    
    def TotalFuncList(self):
        PythonFuncList=set()
        pythonFiles=self.AllFileList()
        for filename in pythonFiles:
            funcList=self.PythonFuncList(filename)
            PythonFuncList.update(funcList)
        return PythonFuncList

    def testLyxFileList(self):
        return
        for filename in self.LyxFileList():
            print(filename)
    
    def testListPythonFiles(self):
        return
        for filename in self._PythonFileList():
            print(filename)
    
    def testListTestFiles(self):
        return
        for filename in self._TestFileList():
            print(filename)
    
    def testListClasses(self):
        return
        PythonClassList=self.TotalClassList()
        
        for classname in PythonClassList:
            print(classname)

    def testListFuncs(self):
        return
        PythonFuncList=self.TotalFuncList()
        
        for funcname in PythonFuncList:
            print(funcname)

    def testPrintLyxClassCandidates(self):
        return
        PythonClassList=self.TotalClassList()
        for filename in self.LyxFileList():
            print(filename)
            with open(filename,'r') as f:
                lines=f.readlines()
            for lineindex in range(len(lines)):
                if lines[lineindex] == '\\series bold\n':
                    try:
                        if lines[lineindex+2] == '\\series default\n':
                            if lines[lineindex+1].strip() in PythonClassList:
                                print('FOUND ONE: '+lines[lineindex+1])
                            else:
                                print('*'+lines[lineindex+1])
                    except:
                        pass

    def testConvertClassesToFormat(self):
        return
        PythonClassList=self.TotalClassList()
        for filename in self.LyxFileList():
            print(filename)
            with open(filename,'r') as f:
                lines=f.readlines()
            newLines=[]
            lineindex=0
            while lineindex < len(lines):
                if lines[lineindex] == '\\series bold\n':
                    try:
                        if lines[lineindex+2] == '\\series default\n':
                            if lines[lineindex+1].strip() in PythonClassList:
                                print('FOUND ONE: '+lines[lineindex+1])
                                newLines.append('\\begin_inset Flex PythonClass\n')
                                newLines.append('status collapsed\n')
                                newLines.append('\n')
                                newLines.append('\\begin_layout Plain Layout\n')
                                newLines.append('\n')
                                newLines.append(lines[lineindex+1])
                                newLines.append('\\end_layout\n')
                                newLines.append('\n')
                                newLines.append('\\end_inset\n')
                                newLines.append('\n')
                                lineindex=lineindex+3
                            else:
                                newLines.append(lines[lineindex])
                                lineindex=lineindex+1
                        else:
                            newLines.append(lines[lineindex])
                            lineindex=lineindex+1
                    except:
                        newLines.append(lines[lineindex])
                        lineindex=lineindex+1
                else:
                    newLines.append(lines[lineindex])
                    lineindex=lineindex+1
            with open(filename,'w') as f:
                f.writelines(newLines)
            
    def testConvertFuncsToFormat(self):
        return
        PythonFuncList=self.TotalFuncList()
        for filename in self.LyxFileList():
            print(filename)
            with open(filename,'r') as f:
                lines=f.readlines()
            newLines=[]
            lineindex=0
            while lineindex < len(lines):
                if lines[lineindex] == '\\family typewriter\n':
                    try:
                        if lines[lineindex+2] == '\\family default\n':
                            lineToCompare=lines[lineindex+1].strip()
                            if lineToCompare in PythonFuncList:
                                if lineToCompare[0]=='p':
                                    print('FOUND ONE (PROPERTY): '+lineToCompare)
                                    newLines.append('\\begin_inset Flex PythonVariable\n')
                                    newLines.append('status collapsed\n')
                                    newLines.append('\n')
                                    newLines.append('\\begin_layout Plain Layout\n')
                                    newLines.append('\n')
                                    newLines.append(lines[lineindex+1])
                                    newLines.append('\\end_layout\n')
                                    newLines.append('\n')
                                    newLines.append('\\end_inset\n')
                                    newLines.append('\n')
                                    lineindex=lineindex+3
                                else:
                                    newLines.append(lines[lineindex])
                                    lineindex=lineindex+1
                            elif lineToCompare.replace('()','') in PythonFuncList:
                                print('FOUND ONE:'+lineToCompare)
                                newLines.append('\\begin_inset Flex PythonFunc\n')
                                newLines.append('status collapsed\n')
                                newLines.append('\n')
                                newLines.append('\\begin_layout Plain Layout\n')
                                newLines.append('\n')
                                newLines.append(lines[lineindex+1].replace('()',''))
                                newLines.append('\\end_layout\n')
                                newLines.append('\n')
                                newLines.append('\\end_inset\n')
                                newLines.append('\n')
                                lineindex=lineindex+3
                            else:
                                newLines.append(lines[lineindex])
                                lineindex=lineindex+1
                        else:
                            newLines.append(lines[lineindex])
                            lineindex=lineindex+1
                    except:
                        newLines.append(lines[lineindex])
                        lineindex=lineindex+1
                else:
                    newLines.append(lines[lineindex])
                    lineindex=lineindex+1
            with open(filename,'w') as f:
                f.writelines(newLines)

    def testPrintLyxFuncCandidates(self):
        return
        PythonFuncList=self.TotalFuncList()
        for filename in self.LyxFileList():
            print(filename)
            with open(filename,'r') as f:
                lines=f.readlines()
            for lineindex in range(len(lines)):
                if lines[lineindex] == '\\family typewriter\n':
                    try:
                        if lines[lineindex+2] == '\\family default\n':
                            lineToCompare=lines[lineindex+1].strip()
                            if lineToCompare in PythonFuncList:
                                if lineToCompare[0]=='p':
                                    print('FOUND ONE (PROPERTY): '+lineToCompare)
                                else:
                                    print('missing (): '+lineToCompare)
                            elif lineToCompare.replace('()','') in PythonFuncList:
                                print('FOUND ONE:'+lineToCompare)
                            else:
                                print('*'+lines[lineindex+1])
                    except:
                        pass

    def FormattedClassList(self,silent=True):
        PythonClassList=self.TotalClassList()
        formattedClassList=set()
        for filename in self.LyxFileList():
            if not silent:
                print(filename)
            with open(filename,'r') as f:
                lines=f.readlines()
            for lineindex in range(len(lines)):
                if lines[lineindex] == '\\begin_inset Flex PythonClass\n':
                    try:
                        classname=lines[lineindex+5].strip()
                        if classname in PythonClassList:
                            if not silent:
                                print('FOUND ONE: '+classname)
                            formattedClassList.add(classname)
                        else:
                            if not silent:
                                print('class not in list: '+classname)
                    except:
                        pass
        return formattedClassList


    def testListFormattedClasses(self):
        return
        formattedClassList=self.FormattedClassList()
        for classname in formattedClassList:
            print(classname)

#     def testGenerateHyphenate(self):
#         formattedClassList=self.FormattedClassList()
#         lines=[]
#         for classname in formattedClassList:
#             hyphenatedClassName=classname[0]
#             for ci in range(1,len(classname)):
#                 c=classname[ci]
#                 if c.isupper():
#                     try:
#                         n=classname[ci+1]
#                         if not n.isupper():
#                             hyphenatedClassName=hyphenatedClassName+'-'
#                     except:
#                         pass
#                 hyphenatedClassName=hyphenatedClassName+c
#             lines.append('\\hyphenation{'+hyphenatedClassName+'}\n')
#         os.chdir(os.path.dirname(os.path.realpath(__file__)))
#         with open(self.bookpath+'classhyphenation.tex','w') as f:
#             f.writelines(lines)

    def testGenerateHyphenate(self):
        return
        formattedClassList=self.FormattedClassList()
        lines=[]
        for classname in formattedClassList:
            hyphenatedClassName=''
            classname=classname.replace('RLGC','RLGc')
            classname=classname.replace('SinX','Sinx')
            classname=classname.replace('TDR','TDr')
            for ci in range(0,len(classname)):
                c=classname[ci]
                if c.isupper():
                    if ci>0:
                        n=classname[ci-1]
                        if n.islower():
                            hyphenatedClassName=hyphenatedClassName+'-'
                hyphenatedClassName=hyphenatedClassName+c
            hyphenatedClassName=hyphenatedClassName.replace('RLGc','RLGC')
            hyphenatedClassName=hyphenatedClassName.replace('Sinx','SinX')
            hyphenatedClassName=hyphenatedClassName.replace('TDr','TDR')
            lines.append('\\hyphenation{'+hyphenatedClassName+'}\n')
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        with open(self.bookpath+'classhyphenation.tex','w') as f:
            f.writelines(lines)

    def ConvertLine(self,line):
        assembledLine=''
        if '\\frac' in line:
            #print(line)
            for i in range(len(line)):
                try:
                    if line[i:i+5] == '\\frac':
                        fracStart=i-1
                        i=i+5
                        keepGoing=True
                        while keepGoing:
                            if line[i]=='{':
                                i=i+1
                                numerStart=i
                                i=i+1
                                while keepGoing:
                                    if line[i]=='}':
                                        numerEnd=i-1
                                        i=i+1
                                        while keepGoing:
                                            if line[i]=='{':
                                                i=i+1
                                                denomStart=i
                                                i=i+1
                                                while keepGoing:
                                                    if line[i]=='}':
                                                        denomEnd=i-1
                                                        keepGoing=False
                                                    else:
                                                        i=i+1
                                            else:
                                                i=i+1
                                    else:
                                        i=i+1
                            else:
                                i=i+1
                        print('ended')
                        seg0=line[:fracStart]
                        seg1="'+lfrac('"
                        seg2=line[numerStart:numerEnd+1]+"','"
                        seg3=line[denomStart:denomEnd+1]+"')+'"
                        seg4=line[denomEnd+2:]
                        print(line)
                        newline=seg0+seg1+seg2+seg3+seg4
                        newline=newline.replace("''+","").replace("+''","")
                        print(newline)
                        return self.ConvertLine(newline)
                except:
                    return assembledLine
        else:
            return line

    def testFindFrac(self):
        pythonFileList=self._PythonFileList()
        fracFileList=[]
        for file in pythonFileList:
            with open(file,'r') as f:
                lines=f.readlines()
            for line in lines:
                if '\\frac' in line:
                    fracFileList.append(file)
                    break
        for file in fracFileList:
            #print(file)
            with open(file,'r') as f:
                lines=f.readlines()
            lines=[self.ConvertLine(line) for line in lines]
            with open(file,'w') as f:
                f.writelines(lines)
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()