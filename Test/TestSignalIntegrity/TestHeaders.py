"""
TestHeaders.py
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

exclusionList=[
    'doxypy.py']

license=[
    '# Copyright (c) 2018 Teledyne LeCroy, Inc.\n',
    '# All rights reserved worldwide.\n',
    '#\n',
    '# This file is part of SignalIntegrity.\n',
    '#\n',
    '# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms\n',
    '# of the GNU General Public License as published by the Free Software Foundation, either\n',
    '# version 3 of the License, or any later version.\n',
    '#\n',
    '# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;\n',
    '# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n',
    '# See the GNU General Public License for more details.\n',
    '#\n',
    '# You should have received a copy of the GNU General Public License along with this program.\n',
    '# If not, see <https://www.gnu.org/licenses/>\n']

class TestHeadersTest(unittest.TestCase):
    write=False
    test=True
    debugFile=None
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    def tearDown(self):
        pass
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
    def testFiles(self):
        errors=False
        thisDir=os.getcwd()
        rootDir=thisDir+'/../..'
        for r, d, f in os.walk(rootDir):
            for file in f:
                if file in exclusionList:
                    continue
                if not self.debugFile is None:
                    if file != self.debugFile:
                        continue
                pythonFileName=os.path.abspath(os.path.join(r,file))
                if pythonFileName[-3:] != '.py':
                    continue
                if 'Code' in pythonFileName[-8:]:
                    continue
                if 'TestSignalIntegrity' in pythonFileName:
                    if file[:4]!='Test':
                        if len(file.split('_'))>1:
                            continue
                if True:
                    with open(pythonFileName) as f:
                        lines=f.readlines()
                    inquotes=False
                    donequotes=False
                    quotesLineStart=0
                    quotesLineEnd=0
                    lineNum=0
                    for lineNum in range(min(50,len(lines))):
                        if donequotes:
                            break
                        line=lines[lineNum]
                        numQuotes=line.count('"""')
                        if not donequotes:
                            if not inquotes:
                                if numQuotes==2:
                                    donequotes=True
                                    quotesLineStart=lineNum
                                    quotesLineEnd=lineNum
                                elif numQuotes==1:
                                    inquotes=True
                                    quotesLineStart=lineNum
                            else:
                                if numQuotes==1:
                                    donequotes=True
                                    inquotes=False
                                    quotesLineEnd=lineNum
                    if donequotes:
                        quotedLineThreshold=0
                        if quotesLineStart > quotedLineThreshold:
                            quotesLineStart=0
                            quotesLineEnd=0
                            donequotes=False

                    if not donequotes:
                        if inquotes:
                            #error - could not find end of first quoted string
                            print(pythonFileName+' Error: unresolved quoted string')
                            errors=True
                        else:
                            #error? no quoted string at beginning
                            print(pythonFileName+' Error: no quoted string')
                            # for now, just print the annoying messages, but don't fail the test
                            #errors=True
                            pass
                    else:
                        # quoted sring at beginning
                        pass
                    #
                    # if a quoted string was found, it is between quotesLineStart and quotesLineEnd
                    # inclusive.  We start looking for the license comments beginnging at quotesLineEnd+1
                    # either way.
                    inLicense=False
                    doneLicense=False
                    licenseLineStart=0
                    licenseLineEnd=0
                    for lineNum in range((quotesLineEnd),len(lines)):
                        if doneLicense:
                            break
                        line=lines[lineNum]
                        if not inLicense:
                            if line[:1] == '#':
                                licenseLineStart=lineNum
                                inLicense=True
                        else:
                            if line[:1] != '#':
                                licenseLineEnd=lineNum-1
                                inLicense=False
                                doneLicense=True
                    if doneLicense:
                        licenseLineThreshold=10
                        licenseLineMinCount=5
                        if licenseLineEnd-licenseLineStart<licenseLineMinCount:
                            doneLicense=False
                        elif licenseLineStart>licenseLineThreshold:
                            doneLicense=False
                    if not doneLicense:
                        # error - no license string
                        print(pythonFileName+' Error: no license')
                        errors=True
                    else:
                        if licenseLineEnd-licenseLineStart+1 != len(license):
                            print(pythonFileName+' Error: license length incorrect')
                            print(str(licenseLineEnd-licenseLineStart+1)+' vs. correct length of '+str(len(license)))
                            errors=True
                        else:
                            for licenseLineNum in range(len(license)):
                                actualLine=lines[licenseLineStart+licenseLineNum]
                                licenseLine=license[licenseLineNum]
                                if len(actualLine)==len(licenseLine)+1:
                                    # thinking maybe it ends in \r\n instead of \n
                                    if actualLine[-2:]=='\r\n':
                                        actualLine=actualLine[:-2]+'\n'
                                if actualLine!=licenseLine:
                                    print(pythonFileName+' Error: license incorrect')
                                    errors=True
                                    break
                        pass
                    realLines=[]
                    if donequotes:
                        realLines=realLines+lines[quotesLineStart:quotesLineEnd+1]
                    else:
                        realLines=realLines+['"""\n',str(file)+'\n','"""\n']
                    realLines=realLines+['\n']
                    realLines=realLines+license
                    if doneLicense:
                        realLines=realLines+lines[licenseLineEnd+1:]
                    elif donequotes:
                        realLines=realLines+lines[quotesLineEnd+1:]
                    else:
                        realLines=realLines+lines
                    # remove old headers
                    inquotes=False
                    donequotes=False
                    quotesLineStart=0
                    quotesLineEnd=0
                    lineNum=0
                    for lineNum in range(len(realLines)):
                        if donequotes:
                            break
                        line=realLines[lineNum]
                        if line[:3]=="'''":
                            if not donequotes:
                                if not inquotes:
                                    quotesLineStart=lineNum
                                    inquotes=True
                                else:
                                    quotesLineEnd=lineNum
                                    inquotes=False
                                    donequotes=True
                    if donequotes:
                        realLines=realLines[:quotesLineStart]+realLines[quotesLineEnd+1:]

                    if self.write:
                        with open(pythonFileName,'w') as f:
                            f.writelines(realLines)

        if self.test:
            self.assertFalse(errors,'there were license errors')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testFiles']
    unittest.main()