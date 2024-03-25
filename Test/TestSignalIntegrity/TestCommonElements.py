"""
TestCommonElements.py
"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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

import SignalIntegrity.Lib as si

from numpy import linalg,array,identity
from numpy.linalg import inv
import os

class TestCommonElements(unittest.TestCase,si.test.SourcesTesterHelper,si.test.RoutineWriterTesterHelper,si.test.ResponseTesterHelper):
    def __init__(self, methodName='runTest'):
        si.test.RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def id(self):
        return '.'.join(unittest.TestCase.id(self).split('.')[-3:])
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        si.td.wf.Waveform.adaptionStrategy='SinX'
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        self.TrySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        SignalIntegrity.App.Preferences['Calculation.TrySVD']=True
        self.CheckConditionNumber=SignalIntegrity.App.Preferences['Calculation.CheckConditionNumber']
        SignalIntegrity.App.Preferences['Calculation.CheckConditionNumber']=True
        self.MultiPortTee=SignalIntegrity.App.Preferences['Calculation.MultiPortTee']
        self.MultiPortTee=False
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        os.chdir(self.cwd)
        si.td.wf.Waveform.adaptionStrategy='SinX'
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation.TrySVD']=self.TrySVD
        SignalIntegrity.App.Preferences['Calculation.CheckConditionNumber']=self.CheckConditionNumber
        SignalIntegrity.App.Preferences['Calculation.MultiPortTee']=self.MultiPortTee
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def testDeviceShuntFourPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2','port 1 D 1 2 D 2 3 D 1 4 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Shunt Device Four Port Symbolic')
    def testDeviceShuntFourPortNumericDeriv(self):
        Z=45.
        D=si.dev.SeriesZ(Z)
        resdef=si.dev.ShuntDeviceFourPort(D)
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2',
            'port 1 D 1 2 D 2 3 D 1 4 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',D)
        resderiv=sspn.SParameters()
        difference = linalg.norm(array(resdef)-array(resderiv))
        self.assertTrue(difference<1e-10,'Z Shunt Four Port derivation different than device')
    def testDeviceShuntFourPortNumericSimplifiedSymbolic(self):
        Z=45.
        D=si.dev.SeriesZ(Z)
        resdef=si.dev.ShuntDeviceFourPort(D)
        Wba=array([[-1./3,0,2./3,0],
        [0,-1./3,0,2./3],
        [2./3,0,-1./3,0],
        [0,2./3,0,-1./3]])
        Wbx=array([[0,0,2./3,0],
        [2./3,0,0,0],
        [0,0,2./3,0],
        [2./3,0,0,0]])
        Wxa=array([[0,0,0,0],
            [0,2./3,0,2./3],
            [0,0,0,0],
            [2./3,0,2./3,0]])
        Wxx=array([[0,D[1][1],0,D[1][0]],
            [-1./3,0,0,0],
            [0,D[0][1],0,D[0][0]],
            [0,0,-1./3,0]])
        I=array(identity(4))
        resderiv=array(Wba)+array(Wbx).dot(inv(I-array(Wxx))).dot(array(Wxa))
        difference = linalg.norm(array(resdef)-array(resderiv))
        self.assertTrue(difference<1e-10,'Z Shunt Four Port derivation different than device')
    def testZShuntFourPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2 ','port 1 D 1 2 D 2 3 D 1 4 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.SeriesZ('Z'))
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Shunt Z Four Port')
    def testZShuntFourPortSafeTee(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2 ',
            'port 1 D 1 2 D 2 3 D 1 4 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.SeriesZ('Z'))
        ssps.InstallSafeTees()
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Shunt Z Four Port')
    def testZShuntFourPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','port 1 D 1 2 D 2 3 D 3 4 D 4'])
        ssps=si.sd.SystemSParametersSymbolic(
            sdp.SystemDescription(),eqprefix='\\begin{equation} ',
            eqsuffix=' \\end{equation}')
        ssps.AssignSParameters('D',si.sy.ShuntZ(4,'Z'))
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Z Shunt Four Port Symbolic')
    def testZShuntFourPortNumeric(self):
        Z=-34.45+1j*24.98
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2',
            'port 1 D 1 2 D 2 3 D 1 4 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.SeriesZ(Z))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.ShuntZFourPort(Z)
        difference = linalg.norm(array(rescalc)-array(rescorrect))
        self.assertTrue(difference<1e-10,'Z Shunt Four Port Numeric incorrect')
    def testZShuntThreePortPossibility1(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2','port 1 D 1 2 D 1 3 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.SeriesZ('Z'))
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Shunt Z Three Port')
    def testZShuntThreePortPossibility2(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device O 1 open','port 1 D 1 2 D 3 3 D 2',
            'connect D 4 O 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('D',si.sy.ShuntZ(4,'Z'))
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Shunt Z Three Port')
    def testZShuntThreePortPossibility3(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device Z 2','port 1 D 1 2 D 3 3 D 2',
            'connect D 2 Z 2','connect Z 1 D 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.ShuntZ(4,'Z'))
        ssps.AssignSParameters('Z',si.sy.SeriesZ('\\varepsilon'))
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Shunt Z Three Port')
    def testZShuntThreePortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','port 1 D 1 2 D 2 3 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
        ssps.AssignSParameters('D',si.sy.ShuntZ(3,'Z'))
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Z Shunt Three Port Symbolic')
    def testZShuntThreePortPossibility1Numeric(self):
        Z=-34.45+1j*24.98
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2','port 1 D 1 2 D 1 3 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.SeriesZ(Z))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.ShuntZThreePort(Z)
        difference = linalg.norm(array(rescalc)-array(rescorrect))
        self.assertTrue(difference<1e-10,'Z Shunt Three Port Possibility 1 Numeric incorrect')
    def testZShuntThreePortPossibility2Numeric(self):
        Z=-34.45+1j*24.98
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device O 1 open',
            'port 1 D 1 2 D 3 3 D 2',
            'connect D 4 O 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.ShuntZFourPort(Z))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.ShuntZThreePort(Z)
        difference = linalg.norm(array(rescalc)-array(rescorrect))
        self.assertTrue(difference<1e-10,'Z Shunt Three Port Possibility 2 Numeric incorrect')
    def testZShuntThreePortPossibility3NumericDirectSaveComplex(self):
        Z=-34.45+1j*24.98
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device T 2 thru','connect T 1 D 2','connect T 1 D 4',
            'port 1 D 1 2 D 3 3 T 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.ShuntZFourPort(Z))
        sspn.InstallSafeTees()
        rescalc=sspn.SParameters(solvetype='direct')
        rescorrect=si.dev.ShuntZThreePort(Z)
        difference = linalg.norm(array(rescalc)-array(rescorrect))
        self.assertTrue(difference<1e-10,'Z Shunt Three Port Possibility 3 Numeric incorrect')
    def testZShuntThreePortPossibility3NumericDirectSave50(self):
        Z=50.
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device T 2 thru','connect T 1 D 2','connect T 1 D 4',
            'port 1 D 1 2 D 3 3 T 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.ShuntZFourPort(Z))
        sspn.InstallSafeTees()
        rescalc=sspn.SParameters(solvetype='direct')
        rescorrect=si.dev.ShuntZThreePort(Z)
        difference = linalg.norm(array(rescalc)-array(rescorrect))
        self.assertTrue(difference<1e-10,'Z Shunt Three Port Possibility 3 Numeric incorrect')
    def testZShuntThreePortPossibility3NumericBlock50(self):
        Z=50.
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','connect D 2 D 4',
            'port 1 D 1 2 D 3 3 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.ShuntZFourPort(Z))
        sspn.InstallSafeTees()
        rescalc=sspn.SParameters()
        rescorrect=si.dev.ShuntZThreePort(Z)
        difference = linalg.norm(array(rescalc)-array(rescorrect))
        self.assertTrue(difference<1e-6,'Z Shunt Three Port Possibility 3 Numeric incorrect')
    def testZShuntThreePortPossibility3NumericBlock50Unsafe(self):
        Z=50.
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','connect D 2 D 4',
            'port 1 D 1 2 D 3 3 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.ShuntZFourPort(Z))
        #sspn.InstallSafeTees()
        si.sd.Numeric.trySVD=False
        with self.assertRaises(si.SignalIntegrityException) as cm:
            rescalc=sspn.SParameters()
        si.sd.Numeric.trySVD=True
        self.assertEqual(cm.exception.parameter,'Numeric')
        #rescorrect=si.dev.ShuntZThreePort(Z)
        #difference = linalg.norm(array(rescalc)-array(rescorrect))
        #self.assertTrue(difference<1e-6,'Z Shunt Three Port Possibility 3 Numeric incorrect')
    def testZShuntThreePortPossibility3NumericBlock50UnsafeFixed(self):
        Z=50.
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','connect D 2 D 4',
            'port 1 D 1 2 D 3 3 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.ShuntZFourPort(Z))
        #sspn.InstallSafeTees()
        #with self.assertRaises(si.PySIException) as cm:
        rescalc=sspn.SParameters()
        #self.assertEqual(cm.exception.parameter,'Numeric')
        rescorrect=si.dev.ShuntZThreePort(Z)
        difference = linalg.norm(array(rescalc)-array(rescorrect))
        self.assertTrue(difference<1e-6,'Z Shunt Three Port Possibility 3 Numeric incorrect')
    def testZShuntThreePortPossibility3NumericBlockComplex(self):
        Z=-34.45+1j*24.98
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','connect D 2 D 4',
            'port 1 D 1 2 D 3 3 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.ShuntZFourPort(Z))
        sspn.InstallSafeTees()
        rescalc=sspn.SParameters()
        rescorrect=si.dev.ShuntZThreePort(Z)
        difference = linalg.norm(array(rescalc)-array(rescorrect))
        self.assertTrue(difference<1e-5,'Z Shunt Three Port Possibility 3 Numeric incorrect')
    def testZShuntThreePortPossibility3NumericDirect50(self):
        Z=50.
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','connect D 2 D 4',
            'port 1 D 1 2 D 3 3 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.ShuntZFourPort(Z))
        sspn.InstallSafeTees()
        rescalc=sspn.SParameters(solvetype='direct')
        rescorrect=si.dev.ShuntZThreePort(Z)
        difference = linalg.norm(array(rescalc)-array(rescorrect))
        self.assertTrue(difference<1e-10,'Z Shunt Three Port Possibility 3 Numeric incorrect')
    def testZShuntThreePortPossibility3NumericDirectComplex(self):
        Z=-34.45+1j*24.98
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','connect D 2 D 4',
            'port 1 D 1 2 D 3 3 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.ShuntZFourPort(Z))
        sspn.InstallSafeTees()
        rescalc=sspn.SParameters(solvetype='direct')
        rescorrect=si.dev.ShuntZThreePort(Z)
        difference = linalg.norm(array(rescalc)-array(rescorrect))
        self.assertTrue(difference<1e-10,'Z Shunt Three Port Possibility 3 Numeric incorrect')
    def testTeeNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2 thru','port 1 D 1 2 D 1 3 D 2','connect D 2 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.InstallSafeTees()
        rescalc1=sspn.SParameters(solvetype='block')
        rescorrect=si.dev.Tee()
        difference = linalg.norm(array(rescalc1)-array(rescorrect))
        self.assertTrue(difference<1e-6,'Tee Numeric incorrect')
    def testTeeNumericDirect(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2 thru','port 1 D 1 2 D 1 3 D 2','connect D 2 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.InstallSafeTees()
        rescalc2=sspn.SParameters(solvetype='direct')
        rescorrect=si.dev.Tee()
        difference = linalg.norm(array(rescalc2)-array(rescorrect))
        self.assertTrue(difference<1e-6,'Tee Numeric incorrect')
    def testZShuntTwoPortPossibility1(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2','device G 1 ground',
            'port 1 D 1 2 D 1','connect D 2 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.SeriesZ('Z'))
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Shunt Z Two Port')
    def testZShuntTwoPortPossibility2(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','device G 1 ground',
            'port 1 D 1 2 D 2','connect D 3 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.ShuntZ(3,'Z'))
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Shunt Z Three Port')
    def WrongShuntZTwoPort(self,Z):
        D='2\\cdot \\left('+Z+'+Z0\\right)'
        return [['\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}'],
                ['\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}'],
                ['\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}'],
                ['\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}']]

    def testZShuntTwoPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2','port 1 D 1 2 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
        ssps.AssignSParameters('D',si.sy.ShuntZ(2,'Z'))
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Z Shunt Three Port Symbolic')
    def testZShuntTwoPortSymbolicWrong(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2','port 1 D 1 2 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
        with self.assertRaises(si.SignalIntegrityException) as cm:
            ssps.AssignSParameters('D',self.WrongShuntZTwoPort('Z'))
        self.assertEqual(cm.exception.parameter,'SystemDescription')
        #ssps.LaTeXSolution().Emit()
        #self.CheckSymbolicResult(self.id(),ssps,'Z Shunt Two Port Symbolic')
    def testFrequencyDependentSeriesCResampling(self):
        sp=si.sp.dev.SeriesC(si.fd.EvenlySpacedFrequencyList(1e9,100),1e-9)
        sp2=sp.Resample(si.fd.EvenlySpacedFrequencyList(2e9,200))
        regression=si.sp.dev.SeriesC(si.fd.EvenlySpacedFrequencyList(2e9,200),1e-9)
        self.assertTrue(self.SParametersAreEqual(sp2,regression,0.00001),'incorrect')
    def testFrequencyDependentSeriesLResampling(self):
        sp=si.sp.dev.SeriesL(si.fd.EvenlySpacedFrequencyList(1e9,100),1e-9)
        sp2=sp.Resample(si.fd.EvenlySpacedFrequencyList(2e9,200))
        regression=si.sp.dev.SeriesL(si.fd.EvenlySpacedFrequencyList(2e9,200),1e-9)
        self.assertTrue(self.SParametersAreEqual(sp2,regression,0.00001),'incorrect')
    def testFrequencyDependentMutualResampling(self):
        sp=si.sp.dev.Mutual(si.fd.EvenlySpacedFrequencyList(1e9,100),1e-9)
        sp2=sp.Resample(si.fd.EvenlySpacedFrequencyList(2e9,200))
        regression=si.sp.dev.Mutual(si.fd.EvenlySpacedFrequencyList(2e9,200),1e-9)
        self.assertTrue(self.SParametersAreEqual(sp2,regression,0.00001),'incorrect')
    def testFrequencyDependentTLineFourPortResampling(self):
        sp=si.sp.dev.TLineLossless(si.fd.EvenlySpacedFrequencyList(1e9,100),4,25,1e-9)
        sp2=sp.Resample(si.fd.EvenlySpacedFrequencyList(2e9,200))
        regression=si.sp.dev.TLineLossless(si.fd.EvenlySpacedFrequencyList(2e9,200),4,25,1e-9)
        self.assertTrue(self.SParametersAreEqual(sp2,regression,0.00001),'incorrect')
    def testFrequencyDependentTLineTwoPortResampling(self):
        sp=si.sp.dev.TLineLossless(si.fd.EvenlySpacedFrequencyList(1e9,100),2,75,1e-9)
        sp2=sp.Resample(si.fd.EvenlySpacedFrequencyList(2e9,200))
        regression=si.sp.dev.TLineLossless(si.fd.EvenlySpacedFrequencyList(2e9,200),2,75,1e-9)
        self.assertTrue(self.SParametersAreEqual(sp2,regression,0.00001),'incorrect')
    def testDeviceFourPortShuntCode(self):
        self.WriteCode('TestCommonElements.py','testDeviceShuntFourPort(self)',self.standardHeader)
    def testZShuntFourPortCode(self):
        self.WriteCode('TestCommonElements.py','testZShuntFourPort(self)',self.standardHeader)
    def testZShuntFourPortSafeTeeCode(self):
        self.WriteCode('TestCommonElements.py','testZShuntFourPortSafeTee(self)',self.standardHeader)
    def testZShuntThreePortPossibility1Code(self):
        self.WriteCode('TestCommonElements.py','testZShuntThreePortPossibility1(self)',self.standardHeader)
    def testZShuntThreePortPossibility2Code(self):
        self.WriteCode('TestCommonElements.py','testZShuntThreePortPossibility2(self)',self.standardHeader)
    def testZShuntThreePortPossibility3Code(self):
        self.WriteCode('TestCommonElements.py','testZShuntThreePortPossibility3(self)',self.standardHeader)
    def testZShuntTwoPortCode(self):
        self.WriteCode('TestCommonElements.py','testZShuntTwoPortPossibility2(self)',self.standardHeader)
    def testTeeNetworkSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device Sl 2','device Sr 2','device Sm 2',
                      'connect Sl 2 Sr 2 Sm 2','port 1 Sl 1 2 Sr 1 3 Sm 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}',
            size='small')
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee Network Three Port Symbolic')
    def testTeeNetworkSymbolicImpedances(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device Sl 2','device Sr 2','device Sm 2',
                      'connect Sl 2 Sr 2 Sm 2','port 1 Sl 1 2 Sr 1 3 Sm 1'])
        sd=sdp.SystemDescription()
        sd.AssignSParameters('Sl',si.sy.SeriesZ('Zl'))
        sd.AssignSParameters('Sr',si.sy.SeriesZ('Zr'))
        sd.AssignSParameters('Sm',si.sy.SeriesZ('Zm'))
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}',
            size='small')
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee Network with Impedances Three Port Symbolic')
    def testTeeNetworkGroundedCenterSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device Sl 2','device Sr 2','device Sm 2','device g 1 ground',
                      'connect Sl 2 Sr 2 Sm 2','connect Sm 1 g 1','port 1 Sl 1 2 Sr 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}',
            size='small')
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee Network Center Grounded Two Port Symbolic')
    def testTeeNetworkGroundedCenterSymbolicImpedances(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device Sl 2','device Sr 2','device Sm 1',
                      'connect Sl 2 Sr 2 Sm 1','port 1 Sl 1 2 Sr 1'])
        sd=sdp.SystemDescription()
        sd.AssignSParameters('Sl',si.sy.SeriesZ('Zl'))
        sd.AssignSParameters('Sr',si.sy.SeriesZ('Zr'))
        sd.AssignSParameters('Sm',si.sy.ShuntZ(1,'Zm'))
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}',
            size='small')
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee Network Center Grounded with Impedances Three Port Symbolic')
    def testTeeNetworkSymbolicCode(self):
        self.WriteCode('TestCommonElements.py','testTeeNetworkSymbolic(self)',self.standardHeader)
    def testTeeNetworkSymbolicImpedancesCode(self):
        self.WriteCode('TestCommonElements.py','testTeeNetworkSymbolicImpedances(self)',self.standardHeader)
    def testTeeNetworkGroundedCenterSymbolicCode(self):
        self.WriteCode('TestCommonElements.py','testTeeNetworkGroundedCenterSymbolic(self)',self.standardHeader)
    def testTeeNetworkGroundedCenterSymbolicImpedancesCode(self):
        self.WriteCode('TestCommonElements.py','testTeeNetworkGroundedCenterSymbolicImpedances(self)',self.standardHeader)

if __name__ == '__main__':
    unittest.main()

