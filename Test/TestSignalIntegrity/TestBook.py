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
if sys.version_info.major < 3:
    from cStringIO import StringIO
else:
    from io import StringIO

import SignalIntegrity.Lib as si

class Test(unittest.TestCase,si.test.RoutineWriterTesterHelper,si.test.ResponseTesterHelper):
    def __init__(self, methodName='runTest'):
        si.test.RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def id(self):
        return '.'.join(unittest.TestCase.id(self).split('.')[-3:])
    def CheckSymbolicResult(self,selfid,symbolic,Text):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileName = '_'.join(selfid.split('.')) + '.tex'
        if not os.path.exists(fileName):
            symbolic.WriteToFile(fileName)
            self.assertTrue(False, fileName + ' not found')
        regression=''
        with open(fileName, 'rU' if sys.version_info.major < 3 else 'r') as regressionFile:
            for line in regressionFile:
                regression = regression + line
        comparison = symbolic.Get()
        self.assertTrue(regression == comparison,Text + ' incorrect')
    def testBook(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        parser = si.p.SystemDescriptionParser()
        parser.m_addThru = False
        parser.AddLine('device L 2')
        parser.AddLine('device R 2')
        parser.AddLine('port 1 L 1')
        parser.AddLine('port 2 R 2')
        parser.AddLine('connect L 2 R 1')
        # parser.WriteToFile('book.txt')
        sd = si.sd.SystemSParameters(parser.SystemDescription())
        n = sd.NodeVector()
        W = sd.WeightsMatrix()
        m = sd.StimulusVector()
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        print(('{0:' + str(5 * len(n)) + '}').format('Weights Matrix'), end=' ')
        print('| {0:4}'.format('n'), end=' ')
        print('| {0:4} |'.format('m'))
        print('----------------------------------------------')
        for r in range(len(n)):
            for c in range(len(sd.NodeVector())):
                print('{0:4}'.format(str(W[r][c])), end=' ')
            print(' | {0:4}'.format(n[r]), end=' ')
            print('| {0:4} |'.format(m[r]))
        print('----------------------------------------------')
        print('\\left[ \\identity - ' + si.helper.Matrix2LaTeX(W) +\
        '\\right] \\cdot '+ si.helper.Matrix2LaTeX([[i] for i in n]) +\
        ' = '+ si.helper.Matrix2LaTeX([[i] for i in m]))
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sys.stdout = old_stdout
        fileName = '_'.join(self.id().split('.')) + '.txt'
        if not os.path.exists(fileName):
            resultFile = open(fileName, 'w')
            resultFile.write(mystdout.getvalue())
            resultFile.close()
            self.assertTrue(False, fileName + ' not found')
        regressionFile = open(fileName, 'rU' if sys.version_info.major < 3 else 'r')
        regression = regressionFile.read()
        regressionFile.close()
        self.assertTrue(regression == mystdout.getvalue(), 'Book Example 1 incorrect')
    def testSystemDescriptionExample(self):
        sd = si.sd.SystemDescription()
        sd.AddDevice('L', 2)  # add two-port left device
        sd.AddDevice('R', 2)  # add two-port right device
        sd.AddPort('L', 1, 1)  # add a port at port 1 of left device
        sd.AddPort('R', 2, 2)  # add a port at port 2 of right device
        sd.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
        # pragma: exclude
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        # pragma: include
        sd.Print()  # print the system description
        spc = si.sd.SystemSParameters(sd)
        n = spc.NodeVector()  # get the node vector
        m = spc.StimulusVector()  # get the stimulus vector
        W = spc.WeightsMatrix()  # get the weights matrix
        # print out the vectors and matrices
        print(('{0:' + str(5 * len(n)) + '}').format('Weights Matrix'), end=' ')
        print('| {0:4}'.format('n'), end=' ')
        print('| {0:4} |'.format('m'))
        print('----------------------------------------------')
        for r in range(len(W)):
            for c in range(len(W[r])):
                print('{0:4}'.format(str(W[r][c])), end=' ')
            print(' | {0:4}'.format(n[r]), end=' ')
            print('| {0:4} |'.format(m[r]))
        print('----------------------------------------------')
        # pragma: exclude
        sys.stdout = old_stdout
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileName = '_'.join(self.id().split('.')) + '.txt'
        if not os.path.exists(fileName):
            resultFile = open(fileName, 'w')
            resultFile.write(mystdout.getvalue())
            resultFile.close()
            self.assertTrue(False, fileName + ' not found')
        regressionFile = open(fileName, 'rU' if sys.version_info.major < 3 else 'r')
        regression = regressionFile.read()
        regressionFile.close()
        self.assertTrue(regression == mystdout.getvalue(), 'Book Example System Description incorrect')
    def testSymbolicExample(self):
        symbolic = si.sd.Symbolic()
        symbolic.DocStart()
        symbolic._AddEq('\\mathbf{S}='+symbolic._LaTeXMatrix(si.sy.SeriesZ('Z')))
        symbolic.DocEnd()
        symbolic.WriteToFile('Symbolic.tex')
        # pragma: exclude
        symbolic.Clear()
        symbolic._AddEq('\\mathbf{S}='+symbolic._LaTeXMatrix(si.sy.SeriesZ('Z')))
        symbolic.Emit()
        self.CheckSymbolicResult(self.id(),symbolic,'Symbolic Example')
    def testSystemDescriptionSymbolicExampleOld(self):
        sd = si.sd.SystemDescription()
        sd.AddDevice('L', 2)  # add two-port left device
        sd.AddDevice('R', 2)  # add two-port right device
        sd.AddPort('L', 1, 1)  # add a port at port 1 of left device
        sd.AddPort('R', 2, 2)  # add a port at port 2 of right device
        sd.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
        ssps = si.sd.SystemSParametersSymbolic(sd)
        ssps.LaTeXSystemEquation().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Book Example System Description Symbolic')
    def testSystemDescriptionSymbolicExample(self):
        ssps = si.sd.SystemDescriptionSymbolic()
        ssps.AddDevice('L', 2)  # add two-port left device
        ssps.AddDevice('R', 2)  # add two-port right device
        ssps.AddPort('L', 1, 1)  # add a port at port 1 of left device
        ssps.AddPort('R', 2, 2)  # add a port at port 2 of right device
        ssps.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
        ssps.LaTeXSystemEquation().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Book Example System Description Symbolic')
    def testSymbolicMethods(self):
        sdp = si.p.SystemDescriptionParser()
        #sdp.AddLines(['device L 2','device R 2','device M 2','device G 1 ground','port 1 L 1 2 R 2',
        #   'connect L 2 R 1 M 1','connect G 1 M 2'])
        sdp.AddLines(['device L 2','device R 2','port 1 L 1 2 R 2','connect L 2 R 1'])
        spc = si.sd.SystemSParameters(sdp.SystemDescription())
        symbolic=si.sd.SystemSParametersSymbolic(spc)
        symbolic.Clear().LaTeXSystemEquation()
        self.CheckSymbolicResult('LaTeXSystemEquation',symbolic,'LaTeXSystemEquation')
        symbolic.Clear().LaTeXSolution(solvetype='direct')
        self.CheckSymbolicResult('LaTeXDirectSolution',symbolic,'LaTeXDirectSolution')
        symbolic.Clear().LaTeXSolution(size='big')
        self.CheckSymbolicResult('LaTeXBlockSolutionBig',symbolic,'LaTeXBlockSolutionBig')
        symbolic.Clear().LaTeXSolution(size='biggest')
        self.CheckSymbolicResult('LaTeXBlockSolutionBiggest',symbolic,'LaTeXBlockSolutionBiggest')
        symbolic.Clear().LaTeXSolution()
        self.CheckSymbolicResult('LaTeXBlockSolution',symbolic,'LaTeXBlockSolution')
    def testSymbolicSolutionExample1Old(self):
        sd = si.sd.SystemDescription()
        sd.AddDevice('S', 2)  # add two-port left device
        sd.AddDevice('\\Gamma t', 1)  # add a termination
        sd.AddPort('S', 1, 1)  # add a port at port 1 of left device
        sd.ConnectDevicePort('S', 2, '\\Gamma t', 1)  # connect the other ports
        spc = si.sd.SystemSParameters(sd)
        symbolic=si.sd.SystemSParametersSymbolic(spc)
        symbolic.LaTeXSystemEquation()
        symbolic.LaTeXSolution(solvetype='direct')
        symbolic.LaTeXSolution(solvetype='block').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 1')
    def testSymbolicSolutionExample1(self):
        ssps = si.sd.SystemSParametersSymbolic()
        ssps.AddDevice('S', 2)  # add two-port left device
        ssps.AddDevice('\\Gamma t', 1)  # add a termination
        ssps.AddPort('S', 1, 1)  # add a port at port 1 of left device
        ssps.ConnectDevicePort('S', 2, '\\Gamma t', 1)  # connect the other ports
        ssps.LaTeXSystemEquation()
        ssps.LaTeXSolution(solvetype='direct')
        ssps.LaTeXSolution(solvetype='block').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Book Example Symbolic Solution 1')
    def testSymbolicSolutionParserExample1Old(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['device S 2','device \\{\\Gamma\\}t 1','port 1 S 1','connect S 2 \\{\\Gamma\\}t 1'])
        sdp.WriteToFile('SymbolicSolution1.txt',False)
        spc = si.sd.SystemSParameters(sdp.SystemDescription())
        symbolic=si.sd.SystemSParametersSymbolic(spc)
        symbolic.LaTeXSystemEquation()
        symbolic.LaTeXSolution(solvetype='direct')
        symbolic.LaTeXSolution(solvetype='block').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 1 Parser')
    def testSymbolicSolutionParserExample1(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['device S 2','device \\{\\Gamma\\}t 1','port 1 S 1',
            'connect S 2 \\{\\Gamma\\}t 1'])
        sdp.WriteToFile('SymbolicSolution1.txt',False)
        ssps = si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.LaTeXSystemEquation()
        ssps.LaTeXSolution(solvetype='direct')
        ssps.LaTeXSolution(solvetype='block').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Book Example Symbolic Solution 1 Parser')
    def testSymbolicSolutionParserFileExample1Old(self):
        sdp = si.p.SystemDescriptionParser().File('SymbolicSolution1.txt')
        spc = si.sd.SystemSParameters(sdp.SystemDescription())
        symbolic=si.sd.SystemSParametersSymbolic(spc)
        symbolic.LaTeXSystemEquation()
        symbolic.LaTeXSolution(solvetype='direct')
        symbolic.LaTeXSolution(solvetype='block').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 1 Parser File')
    def testSymbolicSolutionParserFileExample1(self):
        sdp = si.p.SystemDescriptionParser().File('SymbolicSolution1.txt')
        ssps = si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.LaTeXSystemEquation()
        ssps.LaTeXSolution(solvetype='direct')
        ssps.LaTeXSolution(solvetype='block').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Book Example Symbolic Solution 1 Parser File')
    def testSymbolicSolutionExample2Old(self):
        sd = si.sd.SystemDescription()
        sd.AddDevice('L', 2)  # add two-port left device
        sd.AddDevice('R', 2)  # add two-port right device
        sd.AddPort('L', 1, 1)  # add a port at port 1 of left device
        sd.AddPort('R', 2, 2)  # add a port at port 2 of right device
        sd.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
        spc = si.sd.SystemSParameters(sd)
        symbolic=si.sd.SystemSParametersSymbolic(spc)
        symbolic.LaTeXSystemEquation()
        symbolic.LaTeXSolution(solvetype='direct')
        symbolic.LaTeXSolution(solvetype='block').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 2')
    def testSymbolicSolutionExample2(self):
        ssps = si.sd.SystemSParametersSymbolic()
        ssps.AddDevice('L', 2)  # add two-port left device
        ssps.AddDevice('R', 2)  # add two-port right device
        ssps.AddPort('L', 1, 1)  # add a port at port 1 of left device
        ssps.AddPort('R', 2, 2)  # add a port at port 2 of right device
        ssps.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
        ssps.LaTeXSystemEquation()
        ssps.LaTeXSolution(solvetype='direct')
        ssps.LaTeXSolution(solvetype='block').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Book Example Symbolic Solution 2')
    def testNumericSolutionExample2(self):
        sspn = si.sd.SystemSParametersNumeric()
        sspn.AddDevice('L', 2)  # add two-port left device
        sspn.AddDevice('R', 2)  # add two-port right device
        sspn.AddPort('L', 1, 1)  # add a port at port 1 of left device
        sspn.AddPort('R', 2, 2)  # add a port at port 2 of right device
        sspn.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
        fl=[i*100.*1e6 for i in range(100+1)]; sp=[]
        spl=si.sp.SParameterFile('cable.s2p',50.).Resample(fl)
        spr=si.sp.SParameterFile('filter.s2p',50.).Resample(fl)
        for n in range(len(fl)):
            sspn.AssignSParameters('L',spl[n])
            sspn.AssignSParameters('R',spr[n])
            sp.append(sspn.SParameters())
        spres=si.sp.SParameters(fl,sp).WriteToFile('result.s2p')
        # pragma: exclude
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(spres.m_P)+'p'
        self.CheckSParametersResult(spres,spFileName,spFileName)
    def testNumericSolutionExample2a(self):
        sspn = si.sd.SystemSParametersNumeric()
        sspn.AddDevice('L', 2)  # add two-port left device
        sspn.AddDevice('R', 2)  # add two-port right device
        sspn.AddPort('L', 1, 1)  # add a port at port 1 of left device
        sspn.AddPort('R', 2, 2)  # add a port at port 2 of right device
        sspn.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
        fl=[i*100.*1e6 for i in range(100+1)]; spdl=[]; sp=[]
        spdl.append(('L',si.sp.SParameterFile('cable.s2p',50.).Resample(fl)))
        spdl.append(('R',si.sp.SParameterFile('filter.s2p',50.).Resample(fl)))
        for n in range(len(fl)):
            for ds in spdl: sspn.AssignSParameters(ds[0],ds[1][n])
            sp.append(sspn.SParameters())
        spres=si.sp.SParameters(fl,sp).WriteToFile('result.s2p')
        # pragma: exclude
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(spres.m_P)+'p'
        self.CheckSParametersResult(spres,spFileName,spFileName)
    def testSymbolicSolutionParserExample2Old(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['device L 2','device R 2','port 1 L 1 2 R 2','connect L 2 R 1'])
        sdp.WriteToFile('SymbolicSolution2.txt',False)
        spc = si.sd.SystemSParameters(sdp.SystemDescription())
        symbolic=si.sd.SystemSParametersSymbolic(spc)
        symbolic.LaTeXSystemEquation()
        symbolic.LaTeXSolution(solvetype='direct')
        symbolic.LaTeXSolution(solvetype='block').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 2 Parser')
    def testNumericSolutionParserExample2(self):
        sspnp = si.p.SystemSParametersNumericParser([i*100.*1e6 for i in range(100+1)])
        sspnp.AddLines(['device L 2 file cable.s2p','device R 2 file filter.s2p',
            'port 1 L 1 2 R 2','connect L 2 R 1']).WriteToFile('example2.txt')
        spres=sspnp.SParameters().WriteToFile('result.s2p')
        # pragma: exclude
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(spres.m_P)+'p'
        self.CheckSParametersResult(spres,spFileName,spFileName)
    def testSymbolicSolutionParserExample2(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['device L 2','device R 2','port 1 L 1 2 R 2','connect L 2 R 1'])
        sdp.WriteToFile('SymbolicSolution2.txt',False)
        ssps = si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.LaTeXSystemEquation()
        ssps.LaTeXSolution(solvetype='direct')
        ssps.LaTeXSolution(solvetype='block').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Book Example Symbolic Solution 2 Parser')
    def testSymbolicSolutionParserFileExample2Old(self):
        sdp = si.p.SystemDescriptionParser().File('SymbolicSolution2.txt')
        spc = si.sd.SystemSParameters(sdp.SystemDescription())
        symbolic=si.sd.SystemSParametersSymbolic(spc)
        symbolic.LaTeXSystemEquation()
        symbolic.LaTeXSolution(solvetype='direct')
        symbolic.LaTeXSolution(solvetype='block').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 2 Parser File')
    def testNumericSolutionParserFileExample2(self):
        fl=[i*100.*1e6 for i in range(100+1)]
        sspnp = si.p.SystemSParametersNumericParser(fl).File('example2.txt')
        spres=sspnp.SParameters().WriteToFile('result.s2p')
        # pragma: exclude
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(spres.m_P)+'p'
        self.CheckSParametersResult(spres,spFileName,spFileName)
    def testSymbolicSolutionParserFileExample2(self):
        sdp = si.p.SystemDescriptionParser().File('SymbolicSolution2.txt')
        ssps = si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.LaTeXSystemEquation()
        ssps.LaTeXSolution(solvetype='direct')
        ssps.LaTeXSolution(solvetype='block').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Book Example Symbolic Solution 2 Parser File')
    def testSymbolicSolutionExample3Old(self):
        sd = si.sd.SystemDescription()
        sd.AddDevice('L', 2)  # add two-port left device
        sd.AddDevice('R', 2)  # add two-port right device
        sd.AddDevice('M', 2)  # add two-port middle device
        sd.AddDevice('G', 1, [[-1]]) # add a ground
        sd.AddPort('L', 1, 1)  # add a port at port 1 of left device
        sd.AddPort('R', 2, 2)  # add a port at port 2 of right device
        sd.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
        sd.ConnectDevicePort('L', 2, 'M', 1)
        sd.ConnectDevicePort('G', 1, 'M', 2)
        spc = si.sd.SystemSParameters(sd)
        symbolic=si.sd.SystemSParametersSymbolic(spc,size='small')
        symbolic.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 3')
    def testSymbolicSolutionExample3(self):
        ssps = si.sd.SystemSParametersSymbolic(size='small')
        ssps.AddDevice('L', 2)  # add two-port left device
        ssps.AddDevice('R', 2)  # add two-port right device
        ssps.AddDevice('M', 2)  # add two-port middle device
        ssps.AddDevice('G', 1, [[-1]]) # add a ground
        ssps.AddPort('L', 1, 1)  # add a port at port 1 of left device
        ssps.AddPort('R', 2, 2)  # add a port at port 2 of right device
        ssps.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
        ssps.ConnectDevicePort('L', 2, 'M', 1)
        ssps.ConnectDevicePort('G', 1, 'M', 2)
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Book Example Symbolic Solution 3')
    def testSymbolicSolutionParserExample3Old(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['device L 2','device R 2','device M 2','device G 1 ground','port 1 L 1 2 R 2',
            'connect L 2 R 1 M 1','connect G 1 M 2'])
        # pragma: exclude
        sdp.WriteToFile('SymbolicSolution3.txt',False)
        # pragma: include
        spc = si.sd.SystemSParameters(sdp.SystemDescription())
        symbolic=si.sd.SystemSParametersSymbolic(spc,size='small')
        symbolic.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 3 Parser')
    def testSymbolicSolutionParserExample3(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['device L 2','device R 2','device M 2','device G 1 ground',
            'port 1 L 1 2 R 2','connect L 2 R 1 M 1','connect G 1 M 2'])
        # pragma: exclude
        sdp.WriteToFile('SymbolicSolution3.txt',False)
        # pragma: include
        ssps = si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Book Example Symbolic Solution 3 Parser')
    def testSymbolicSolutionParserFileExample3Old(self):
        sdp = si.p.SystemDescriptionParser().File('SymbolicSolution3.txt')
        spc = si.sd.SystemSParameters(sdp.SystemDescription())
        symbolic=si.sd.SystemSParametersSymbolic(spc,size='small')
        symbolic.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 3 Parser File')
    def testSymbolicSolutionParserFileExample3(self):
        sdp = si.p.SystemDescriptionParser().File('SymbolicSolution3.txt')
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Book Example Symbolic Solution 3 Parser File')
    def testSymbolicDeembeddingExample1Old(self):
        d=si.sd.Deembedder()
        d.AddDevice('S',2)
        d.AddUnknown('Su',1)
        d.ConnectDevicePort('S',2,'Su',1)
        d.AddPort('S',1,1)
        symbolic=si.sd.DeembedderSymbolic(d,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 1')
    def testSymbolicDeembeddingExample1(self):
        ds=si.sd.DeembedderSymbolic(size='small',known='\\Gamma_{msd}')
        ds.AddDevice('S',2)
        ds.AddUnknown('\\Gamma_{dut}',1)
        ds.ConnectDevicePort('S',2,'\\Gamma_{dut}',1)
        ds.AddPort('S',1,1)
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 1')
    def testSymbolicDeembeddingThruExample1Old(self):
        d=si.sd.Deembedder()
        d.AddDevice('D',2)
        d.AddUnknown('Su',1)
        d.ConnectDevicePort('D',2,'Su',1)
        d.AddPort('D',1,1,True)
        symbolic=si.sd.DeembedderSymbolic(d,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 1 Thru')
    def testSymbolicDeembeddingThruExample1(self):
        ds=si.sd.DeembedderSymbolic(size='small',known='\\Gamma_{msd}')
        ds.AddDevice('D',2)
        ds.AddUnknown('\\Gamma_{dut}',1)
        ds.ConnectDevicePort('D',2,'\\Gamma_{dut}',1)
        ds.AddPort('D',1,1,True)
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 1 Thru')
    def testSymbolicDeembeddingParserExample1Old(self):
        dp=si.p.DeembedderParser()
        dp.AddLines(['device D 2','unknown Su 1','port 1 D 1','connect D 2 Su 1'])
        dp.WriteToFile('SymbolicDeembedding1Old.txt',False)
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 1 Parser')
    def testSymbolicDeembeddingParserExample1(self):
        dp=si.p.DeembedderParser()
        dp.AddLines(['device D 2','unknown \\Gamma_{dut} 1','port 1 D 1','connect D 2 \\Gamma_{dut} 1'])
        # pragma: exclude
        dp.WriteToFile('SymbolicDeembedding1.txt',False)
        # pragma: include
        ds = si.sd.DeembedderSymbolic(dp.SystemDescription(),size='small',known='\\Gamma_{msd}')
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 1 Parser')
    def testSymbolicDeembeddingParserFileExample1Old(self):
        dp=si.p.DeembedderParser().File('SymbolicDeembedding1Old.txt')
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 1 Parser File')
    def testSymbolicDeembeddingParserFileExample1(self):
        dp=si.p.DeembedderParser().File('SymbolicDeembedding1.txt')
        ds = si.sd.DeembedderSymbolic(dp.SystemDescription(),size='small')
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 1 Parser File')
    def testSymbolicDeembeddingExample2Old(self):
        d=si.sd.Deembedder()
        d.AddDevice('L',2)
        d.AddUnknown('Su',2)
        d.AddDevice('R',2)
        d.AddPort('L',1,1)
        d.AddPort('R',1,2)
        d.ConnectDevicePort('L',2,'Su',1)
        d.ConnectDevicePort('R',2,'Su',2)
        symbolic=si.sd.DeembedderSymbolic(d,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 2')
    def testSymbolicDeembeddingExample2(self):
        ds=si.sd.DeembedderSymbolic(size='small')
        ds.AddDevice('L',2)
        ds.AddUnknown('U',2)
        ds.AddDevice('R',2)
        ds.AddPort('L',1,1)
        ds.AddPort('R',1,2)
        ds.ConnectDevicePort('L',2,'U',1)
        ds.ConnectDevicePort('R',2,'U',2)
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 2')
    def testSymbolicDeembeddingParserExample2Old(self):
        dp=si.p.DeembedderParser()
        dp.AddLines(['device L 2','unknown Su 2','device R 2',
            'port 1 L 1 2 R 1','connect L 2 Su 1','connect R 2 Su 2'])
        # pragma: exclude
        dp.WriteToFile('SymbolicDeembedding2Old.txt',False)
        # pragma: include
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 2 Parser')
    def testSymbolicDeembeddingParserExample2(self):
        dp=si.p.DeembedderParser()
        dp.AddLines(['device L 2','unknown U 2','device R 2',
            'port 1 L 1 2 R 1','connect L 2 U 1','connect R 2 U 2'])
        # pragma: exclude
        dp.WriteToFile('SymbolicDeembedding2.txt',False)
        # pragma: include
        ds = si.sd.DeembedderSymbolic(dp.SystemDescription(),size='small')
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 2 Parser')
    def testSymbolicDeembeddingParserFileExample2Old(self):
        dp=si.p.DeembedderParser().File('SymbolicDeembedding2Old.txt')
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 2 Parser File')
    def testSymbolicDeembeddingParserFileExample2(self):
        dp=si.p.DeembedderParser().File('SymbolicDeembedding2.txt')
        ds = si.sd.DeembedderSymbolic(dp.SystemDescription(),size='small')
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 2 Parser File')
    def testSymbolicDeembeddingExample3Old(self):
        d=si.sd.Deembedder()
        d.AddDevice('L',2)
        d.AddUnknown('Su',2)
        d.AddPort('L',1,1)
        d.AddPort('Su',2,2,True)
        d.ConnectDevicePort('L',2,'Su',1)
        symbolic=si.sd.DeembedderSymbolic(d,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 3')
    def testSymbolicDeembeddingExample3(self):
        ds=si.sd.DeembedderSymbolic(size='small')
        ds.AddDevice('L',2)
        ds.AddUnknown('Su',2)
        ds.AddPort('L',1,1)
        ds.AddPort('Su',2,2,True)
        ds.ConnectDevicePort('L',2,'Su',1)
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 3')
    def testSymbolicDeembeddingThruExample3Old(self):
        d=si.sd.Deembedder()
        d.AddDevice('L',2)
        d.AddUnknown('Su',2)
        d.AddPort('L',1,1,True)
        d.AddPort('Su',2,2,True)
        d.ConnectDevicePort('L',2,'Su',1)
        symbolic=si.sd.DeembedderSymbolic(d,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding 3 Thru incorrect')
    def testSymbolicDeembeddingThruExample3(self):
        ds=si.sd.DeembedderSymbolic(size='small')
        ds.AddDevice('L',2)
        ds.AddUnknown('Su',2)
        ds.AddPort('L',1,1,True)
        ds.AddPort('Su',2,2,True)
        ds.ConnectDevicePort('L',2,'Su',1)
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding 3 Thru incorrect')
    def testSymbolicDeembeddingParserExample3Old(self):
        dp=si.p.DeembedderParser()
        dp.AddLines(['device L 2','unknown Su 2','port 1 L 1 2 Su 2','connect L 2 Su 1'])
        dp.WriteToFile('SymbolicDeembedding3Old.txt',False)
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 3 Parser')
    def testSymbolicDeembeddingParserExample3(self):
        dp=si.p.DeembedderParser()
        dp.AddLines(['device L 2','unknown Su 2','port 1 L 1 2 Su 2','connect L 2 Su 1'])
        # pragma: exclude
        dp.WriteToFile('SymbolicDeembedding3.txt',False)
        # pragma: include
        ds = si.sd.DeembedderSymbolic(dp.SystemDescription(),size='small')
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 3 Parser')
    def testSymbolicDeembeddingParserFileExample3Old(self):
        dp=si.p.DeembedderParser().File('SymbolicDeembedding3Old.txt')
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 3 Parser File')
    def testSymbolicDeembeddingParserFileExample3(self):
        dp=si.p.DeembedderParser().File('SymbolicDeembedding3.txt')
        ds = si.sd.DeembedderSymbolic(dp.SystemDescription(),size='small')
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 3 Parser File')
    def testSymbolicDeembeddingExample4Old(self):
        d=si.sd.Deembedder()
        d.AddDevice('F',4)
        d.AddUnknown('?1',1)
        d.AddUnknown('?2',1)
        d.AddPort('F',1,1)
        d.AddPort('F',2,2)
        d.ConnectDevicePort('F',3,'?1',1)
        d.ConnectDevicePort('F',4,'?2',1)
        symbolic=si.sd.DeembedderSymbolic(d,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 4')
    def testSymbolicDeembeddingExample4(self):
        ds=si.sd.DeembedderSymbolic(size='small')
        ds.AddDevice('F',4)
        ds.AddUnknown('U_1',1)
        ds.AddUnknown('U_2',1)
        ds.AddPort('F',1,1)
        ds.AddPort('F',2,2)
        ds.ConnectDevicePort('F',3,'U_1',1)
        ds.ConnectDevicePort('F',4,'U_2',1)
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 4')
    def testSymbolicDeembeddingParserExample4Old(self):
        dp=si.p.DeembedderParser()
        dp.AddLines(['device F 4','unknown ?1 1','unknown ?2 1','port 1 F 1 2 F 2',
            'connect F 3 ?1 1','connect F 4 ?2 1'])
        # pragma: exclude
        dp.WriteToFile('SymbolicDeembedding4Old.txt',False)
        # pragma: include
        ds = si.sd.DeembedderSymbolic(dp.SystemDescription(),size='small')
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 4 Parser')
    def testSymbolicDeembeddingParserExample4(self):
        dp=si.p.DeembedderParser()
        dp.AddLines(['device F 4','unknown ?1 1','unknown ?2 1','port 1 F 1 2 F 2',
            'connect F 3 ?1 1','connect F 4 ?2 1'])
        dp.WriteToFile('SymbolicDeembedding4.txt',False)
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 4 Parser')
    def testSymbolicDeembeddingParserFileExample4Old(self):
        dp=si.p.DeembedderParser().File('SymbolicDeembedding4Old.txt')
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 4 Parser File')
    def testSymbolicDeembeddingParserFileExample4(self):
        dp=si.p.DeembedderParser().File('SymbolicDeembedding4.txt')
        ds = si.sd.DeembedderSymbolic(dp.SystemDescription(),size='small')
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 4 Parser File')
    def testSymbolicDeembeddingExample5Old(self):
        d=si.sd.Deembedder()
        d.AddDevice('D1',2)
        d.AddDevice('D2',2)
        d.AddDevice('D3',2)
        d.AddUnknown('Su',2)
        d.AddPort('D1',1,1)
        d.AddPort('D2',1,2)
        d.ConnectDevicePort('D1',2,'Su',1)
        d.ConnectDevicePort('D2',2,'D3',1)
        d.ConnectDevicePort('D3',2,'Su',2)
        symbolic=si.sd.DeembedderSymbolic(d,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 5')
    def testSymbolicDeembeddingExample5(self):
        ds=si.sd.DeembedderSymbolic(size='small')
        ds.AddDevice('D1',2)
        ds.AddDevice('D2',2)
        ds.AddDevice('D3',2)
        ds.AddUnknown('Su',2)
        ds.AddPort('D1',1,1)
        ds.AddPort('D2',1,2)
        ds.ConnectDevicePort('D1',2,'Su',1)
        ds.ConnectDevicePort('D2',2,'D3',1)
        ds.ConnectDevicePort('D3',2,'Su',2)
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 5')
    def testSymbolicDeembeddingParserExample5Old(self):
        dp=si.p.DeembedderParser()
        dp.AddLines(['device D1 2','device D2 2','device D3 2',
            'unknown Su 2','port 1 D1 1 2 D2 1',
            'connect D1 2 Su 1','connect D2 2 D3 1',
            'connect D3 2 Su 2'])
        dp.WriteToFile('SymbolicDeembedding5Old.txt',False)
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 5 Parser')
    def testSymbolicDeembeddingParserExample5(self):
        dp=si.p.DeembedderParser()
        dp.AddLines(['device D1 2','device D2 2','device D3 2',
            'unknown Su 2','port 1 D1 1 2 D2 1',
            'connect D1 2 Su 1','connect D2 2 D3 1',
            'connect D3 2 Su 2'])
        # pragma: exclude
        dp.WriteToFile('SymbolicDeembedding5.txt',False)
        # pragma: include
        ds = si.sd.DeembedderSymbolic(dp.SystemDescription(),size='small')
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 5 Parser')
    def testSymbolicDeembeddingParserFileExample5Old(self):
        dp=si.p.DeembedderParser().File('SymbolicDeembedding5Old.txt')
        ds = si.sd.DeembedderSymbolic(dp.SystemDescription(),size='small')
        ds.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Book Example Symbolic Deembedding Solution 5 Parser File')
    def testSymbolicDeembeddingParserFileExample5(self):
        dp=si.p.DeembedderParser().File('SymbolicDeembedding5.txt')
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,size='small')
        symbolic.SymbolicSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 5 Parser File')
    def testSymbolicVirtualProbeExample1(self):
        vps=si.sd.VirtualProbeSymbolic(size='small')
        vps.AddDevice('\\Gamma_T',1)
        vps.AddDevice('C',2)
        vps.AddDevice('\\Gamma_R',1)
        vps.ConnectDevicePort('\\Gamma_T',1,'C',1)
        vps.ConnectDevicePort('C',2,'\\Gamma_R',1)
        vps.AssignM('\\Gamma_T',1,'m1')
        vps.pMeasurementList = [('\\Gamma_T',1)]
        vps.pOutputList = [('\\Gamma_R',1)]
        vps.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),vps,'Book Example Symbolic Virtual Probe 1')
    def testSymbolicVirtualProbeExample1Old(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('T',1)
        sd.AddDevice('C',2)
        sd.AddDevice('R',1)
        sd.ConnectDevicePort('T',1,'C',1)
        sd.ConnectDevicePort('C',2,'R',1)
        sd.AssignM('T',1,'m1')
        vp=si.sd.VirtualProbe(sd)
        vp.pMeasurementList = [('T',1)]
        vp.pOutputList = [('R',1)]
        svp=si.sd.VirtualProbeSymbolic(vp,size='small')
        svp.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 1')
    def testSymbolicVirtualProbeParserExample1Old(self):
        vpp=si.p.VirtualProbeParser()
        vpp.AddLines(['device T 1','device C 2','device R 1','connect T 1 C 1','connect C 2 R 1',
            'stim m1 T 1','meas T 1','output R 1'])
        vpp.WriteToFile('VirtualProbe1.txt',False)
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,size='small')
        svp.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 1 Parser')
    def testSymbolicVirtualProbeParserExample1(self):
        vpp=si.p.VirtualProbeParser()
        vpp.AddLines(['device T 1','device C 2','device R 1','connect T 1 C 1',
            'connect C 2 R 1','stim m1 T 1','meas T 1','output R 1'])
        # pragma: exclude
        vpp.WriteToFile('VirtualProbe1.txt',False)
        # pragma: include
        vps=si.sd.VirtualProbeSymbolic(vpp.SystemDescription(),size='small')
        vps.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),vps,'Book Example Symbolic Virtual Probe 1 Parser')
    def testSymbolicVirtualProbeParserFileExample1Old(self):
        vpp=si.p.VirtualProbeParser().File('VirtualProbe1.txt')
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,size='small')
        svp.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 1 Parser File')
    def testSymbolicVirtualProbeParserFileExample1(self):
        vpp=si.p.VirtualProbeParser().File('VirtualProbe1.txt')
        vps=si.sd.VirtualProbeSymbolic(vpp.SystemDescription(),size='small')
        vps.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),vps,'Book Example Symbolic Virtual Probe 1 Parser File')
    def testSymbolicVirtualProbeExample2Old(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('T',2)
        sd.AddDevice('C',4)
        sd.AddDevice('R',2)
        sd.ConnectDevicePort('T',1,'C',1)
        sd.ConnectDevicePort('T',2,'C',2)
        sd.ConnectDevicePort('C',3,'R',1)
        sd.ConnectDevicePort('C',4,'R',2)
        sd.AssignM('T',1,'m1')
        sd.AssignM('T',2,'m2')
        vp=si.sd.VirtualProbe(sd)
        vp.pMeasurementList = [('T',1),('T',2)]
        vp.pOutputList = [('R',1),('R',2)]
        svp=si.sd.VirtualProbeSymbolic(vp,size='small')
        svp.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 2')
    def testSymbolicVirtualProbeExample2(self):
        vps=si.sd.VirtualProbeSymbolic(size='small')
        vps.AddDevice('T',2)
        vps.AddDevice('C',4)
        vps.AddDevice('R',2)
        vps.ConnectDevicePort('T',1,'C',1)
        vps.ConnectDevicePort('T',2,'C',2)
        vps.ConnectDevicePort('C',3,'R',1)
        vps.ConnectDevicePort('C',4,'R',2)
        vps.AssignM('T',1,'m1')
        vps.AssignM('T',2,'m2')
        vps.pMeasurementList = [('T',1),('T',2)]
        vps.pOutputList = [('R',1),('R',2)]
        vps.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),vps,'Book Example Symbolic Virtual Probe 2')
    def testSymbolicVirtualProbeParserExample2Old(self):
        vpp=si.p.VirtualProbeParser()
        vpp.AddLines(['device T 2','device C 4','device R 2','connect T 1 C 1','connect T 2 C 2',
            'connect C 3 R 1','connect C 4 R 2','stim m1 T 1','stim m2 T 2','meas T 1 T 2','output R 1 R 2'])
        vpp.WriteToFile('VirtualProbe2.txt',False)
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,size='small')
        svp.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 2 Parser')
    def testSymbolicVirtualProbeParserExample2(self):
        vpp=si.p.VirtualProbeParser()
        vpp.AddLines(['device T 2','device C 4','device R 2','connect T 1 C 1','connect T 2 C 2',
            'connect C 3 R 1','connect C 4 R 2','stim m1 T 1','stim m2 T 2','meas T 1 T 2',
            'output R 1 R 2'])
        # pragma: exclude
        vpp.WriteToFile('VirtualProbe2.txt',False)
        # pragma: include
        vps=si.sd.VirtualProbeSymbolic(vpp.SystemDescription(),size='small')
        vps.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),vps,'Book Example Symbolic Virtual Probe 2 Parser')
    def testSymbolicVirtualProbeParserFileExample2Old(self):
        vpp=si.p.VirtualProbeParser().File('VirtualProbe2.txt')
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,size='small')
        svp.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 2 Parser File')
    def testSymbolicVirtualProbeParserFileExample2(self):
        vpp=si.p.VirtualProbeParser().File('VirtualProbe2.txt')
        vps=si.sd.VirtualProbeSymbolic(vpp.SystemDescription(),size='small')
        vps.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),vps,'Book Example Symbolic Virtual Probe 2 Parser File')
    def testSymbolicVirtualProbeExample3Old(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('T',2)
        sd.AddDevice('C',4)
        sd.AddDevice('R',2)
        sd.ConnectDevicePort('T',1,'C',1)
        sd.ConnectDevicePort('T',2,'C',2)
        sd.ConnectDevicePort('C',3,'R',1)
        sd.ConnectDevicePort('C',4,'R',2)
        sd.AssignM('T',1,'m1')
        sd.AssignM('T',2,'m2')
        vp=si.sd.VirtualProbe(sd)
        vp.pMeasurementList = [('T',1),('T',2)]
        vp.pOutputList = [('R',1),('R',2)]
        vp.pStimDef = [[1],[-1]]
        svp=si.sd.VirtualProbeSymbolic(vp,size='small')
        svp.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 3')
    def testSymbolicVirtualProbeExample3(self):
        vps=si.sd.VirtualProbeSymbolic(size='small')
        vps.AddDevice('T',2)
        vps.AddDevice('C',4)
        vps.AddDevice('R',2)
        vps.ConnectDevicePort('T',1,'C',1)
        vps.ConnectDevicePort('T',2,'C',2)
        vps.ConnectDevicePort('C',3,'R',1)
        vps.ConnectDevicePort('C',4,'R',2)
        vps.AssignM('T',1,'m1')
        vps.AssignM('T',2,'m2')
        vps.pMeasurementList = [('T',1),('T',2)]
        vps.pOutputList = [('R',1),('R',2)]
        vps.pStimDef = [[1],[-1]]
        vps.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),vps,'Book Example Symbolic Virtual Probe 3')
    def testSymbolicVirtualProbeParserExample3Old(self):
        vpp=si.p.VirtualProbeParser()
        vpp.AddLines(['device T 2','device C 4','device R 2','connect T 1 C 1',
            'connect T 2 C 2','connect C 3 R 1','connect C 4 R 2','stim m1 T 1',
            'stim m2 T 2','meas T 1 T 2','output R 1 R 2','stimdef [[1],[-1]]'])
        vpp.WriteToFile('VirtualProbe3.txt',False)
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,size='small')
        svp.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 3 Parser')
    def testSymbolicVirtualProbeParserExample3(self):
        vpp=si.p.VirtualProbeParser()
        vpp.AddLines(['device T 2','device C 4','device R 2','connect T 1 C 1',
            'connect T 2 C 2','connect C 3 R 1','connect C 4 R 2','stim m1 T 1',
            'stim m2 T 2','meas T 1 T 2','output R 1 R 2','stimdef [[1],[-1]]'])
        # pragma: exclude
        vpp.WriteToFile('VirtualProbe3.txt',False)
        # pragma: include
        vps=si.sd.VirtualProbeSymbolic(vpp.SystemDescription(),size='small')
        vps.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),vps,'Book Example Symbolic Virtual Probe 3 Parser')
    def testSymbolicVirtualProbeParserFileExample3Old(self):
        vpp=si.p.VirtualProbeParser().File('VirtualProbe3.txt')
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,size='small')
        svp.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 3 Parser File')
    def testSymbolicVirtualProbeParserFileExample3(self):
        vpp=si.p.VirtualProbeParser().File('VirtualProbe3.txt')
        vps=si.sd.VirtualProbeSymbolic(vpp.SystemDescription(),size='small')
        vps.LaTeXEquations().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),vps,'Book Example Symbolic Virtual Probe 3 Parser File')
    def testSymbolicVirtualProbeExample4Old(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('T',2)
        sd.AddDevice('MM1',4,si.dev.MixedModeConverter())
        sd.AddDevice('MM2',4,si.dev.MixedModeConverter())
        sd.AddDevice('C',4)
        sd.AddDevice('R',2)
        sd.ConnectDevicePort('T',1,'MM1',1)
        sd.ConnectDevicePort('T',2,'MM1',2)
        sd.ConnectDevicePort('MM1',3,'MM2',3)
        sd.ConnectDevicePort('MM1',4,'MM2',4)
        sd.ConnectDevicePort('MM2',1,'C',1)
        sd.ConnectDevicePort('MM2',2,'C',2)
        sd.ConnectDevicePort('C',3,'R',1)
        sd.ConnectDevicePort('C',4,'R',2)
        sd.AssignM('T',1,'m1')
        sd.AssignM('T',2,'m2')
        vp=si.sd.VirtualProbe(sd)
        vp.pMeasurementList = [('MM1',3)]
        vp.pOutputList = [('R',1),('R',2)]
        vp.pStimDef = [[1],[-1]]
        svp=si.sd.VirtualProbeSymbolic(vp,size='small')
        svp.LaTeXTransferMatrix().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 4')
    def testSymbolicVirtualProbeExample4(self):
        vps=si.sd.VirtualProbeSymbolic(size='small')
        vps.AddDevice('T',2)
        vps.AddDevice('MM1',4,si.dev.MixedModeConverter())
        vps.AddDevice('MM2',4,si.dev.MixedModeConverter())
        vps.AddDevice('C',4)
        vps.AddDevice('R',2)
        vps.ConnectDevicePort('T',1,'MM1',1)
        vps.ConnectDevicePort('T',2,'MM1',2)
        vps.ConnectDevicePort('MM1',3,'MM2',3)
        vps.ConnectDevicePort('MM1',4,'MM2',4)
        vps.ConnectDevicePort('MM2',1,'C',1)
        vps.ConnectDevicePort('MM2',2,'C',2)
        vps.ConnectDevicePort('C',3,'R',1)
        vps.ConnectDevicePort('C',4,'R',2)
        vps.AssignM('T',1,'m1')
        vps.AssignM('T',2,'m2')
        vps.pMeasurementList = [('MM1',3)]
        vps.pOutputList = [('R',1),('R',2)]
        vps.pStimDef = [[1],[-1]]
        vps.LaTeXTransferMatrix().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),vps,'Book Example Symbolic Virtual Probe 4')
    def testSymbolicVirtualProbeParserExample4Old(self):
        vpp=si.p.VirtualProbeParser()
        vpp.AddLines(['device T 2','device MM1 4 mixedmode voltage','device MM2 4 mixedmode voltage','device C 4',
            'device R 2','connect T 1 MM1 1','connect T 2 MM1 2','connect MM1 3 MM2 3','connect MM1 4 MM2 4',
            'connect MM2 1 C 1','connect MM2 2 C 2',
            'connect C 3 R 1','connect C 4 R 2','stim m1 T 1 m2 T 2','meas MM1 3','output R 1 R 2',
            'stimdef [[1],[-1]]'])
        vpp.WriteToFile('VirtualProbe4.txt',False)
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,size='small')
        svp.LaTeXTransferMatrix().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 4 Parser')
    def testSymbolicVirtualProbeParserExample4(self):
        vpp=si.p.VirtualProbeParser()
        vpp.AddLines(['device T 2','device MM1 4 mixedmode voltage','device MM2 4 mixedmode voltage',
            'device C 4','device R 2','connect T 1 MM1 1','connect T 2 MM1 2',
            'connect MM1 3 MM2 3','connect MM1 4 MM2 4','connect MM2 1 C 1','connect MM2 2 C 2',
            'connect C 3 R 1','connect C 4 R 2','stim m1 T 1 m2 T 2','meas MM1 3',
            'output R 1 R 2','stimdef [[1],[-1]]'])
        # pragma: exclude
        vpp.WriteToFile('VirtualProbe4.txt',False)
        # pragma: include
        vps=si.sd.VirtualProbeSymbolic(vpp.SystemDescription(),size='small')
        vps.LaTeXTransferMatrix().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),vps,'Book Example Symbolic Virtual Probe 4 Parser')
    def testSymbolicVirtualProbeParserFileExample4Old(self):
        vpp=si.p.VirtualProbeParser().File('VirtualProbe4.txt')
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,size='small')
        svp.LaTeXTransferMatrix().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 4 Parser File')
    def testSymbolicVirtualProbeParserFileExample4(self):
        vpp=si.p.VirtualProbeParser().File('VirtualProbe4.txt')
        vps=si.sd.VirtualProbeSymbolic(vpp.SystemDescription(),size='small')
        vps.LaTeXTransferMatrix().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),vps,'Book Example Symbolic Virtual Probe 4 Parser File')
    def testParserBreaker(self):
        ssps=si.p.SystemSParametersNumericParser(si.fd.EvenlySpacedFrequencyList(1,10))
        ssps.AddLines(['device R1 2 R 50.','device R2 1 R 50.','port 1 R1 1','connect R1 2 R2 1'])
        ssps.SParameters()
    def testSymbolicDeembeddingParserFileTwoTwoTwo(self):
        dp=si.p.DeembedderParser().AddLines(['unknown U1 2','unknown U2 2','device D 2','port 1 U1 1','port 2 U2 2','connect U1 2 D 1','connect D 2 U2 1'])
        ds = si.sd.DeembedderSymbolic(dp.SystemDescription(),size='small')
        ds.DocStart().SymbolicSolution().DocEnd().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ds,'Symbolic Deembedding TwoTwoTwo File')
    def testSymbolicSolutionExample1Code(self):
        self.WriteCode('TestBook.py','testSymbolicSolutionExample1(self)',self.standardHeader)
    def testSymbolicSolutionParserExample2Code(self):
        self.WriteCode('TestBook.py','testSymbolicSolutionParserExample2(self)',self.standardHeader)
    def testNumericSolutionExample2Code(self):
        self.WriteCode('TestBook.py','testNumericSolutionExample2(self)',[self.standardHeader[0]])
    def testNumericSolutionExample2aCode(self):
        self.WriteCode('TestBook.py','testNumericSolutionExample2a(self)',[self.standardHeader[0]])
    def testNumericSolutionParserExample2Code(self):
        self.WriteCode('TestBook.py','testNumericSolutionParserExample2(self)',[self.standardHeader[0]])
    def testNumericSolutionParserFileExample2Code(self):
        self.WriteCode('TestBook.py','testNumericSolutionParserFileExample2(self)',[self.standardHeader[0]])
    def testSymbolicSolutionParserFileExample3Code(self):
        self.WriteCode('TestBook.py','testSymbolicSolutionParserFileExample3(self)',self.standardHeader)
    def testSystemDescriptionExampleCode(self):
        headerLines=['from __future__ import print_function\n']+self.standardHeader
        self.WriteCode('TestBook.py','testSystemDescriptionExample(self)',headerLines)
    def testSymbolicExampleCode(self):
        self.WriteCode('TestBook.py','testSymbolicExample(self)',self.standardHeader)
    def testSystemDescriptionExampleSymbolicCode(self):
        self.WriteCode('TestBook.py','testSystemDescriptionSymbolicExample(self)',self.standardHeader)
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
    def testSymbolicVirtualProbeParserFileExample3Code(self):
        self.WriteCode('TestBook.py','testSymbolicVirtualProbeParserExample3(self)',self.standardHeader)
    def testSymbolicVirtualProbeParserFileExample4Code(self):
        self.WriteCode('TestBook.py','testSymbolicVirtualProbeParserFileExample4(self)',self.standardHeader)

if __name__ == "__main__":
    unittest.main()
