"""
TestBalun.py
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
from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
from SignalIntegrity.App import TpX
from SignalIntegrity.App import TikZ
import SignalIntegrity.Lib as si
import os

class TestBalunTest(unittest.TestCase,si.test.SourcesTesterHelper,
                                si.test.SParameterCompareHelper,
                                si.test.SignalIntegrityAppTestHelper):
    relearn=True
    debug=False
    checkPictures=True
    keepNewFormats=False
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd=os.getcwd()
        os.chdir(self.path)
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        self.Caching=SignalIntegrity.App.Preferences['Cache.CacheResults']
        SignalIntegrity.App.Preferences['Cache.CacheResults']=False
        self.UseSinX=SignalIntegrity.App.Preferences['Calculation.UseSinX']
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=True
        self.TextLimit=SignalIntegrity.App.Preferences['Appearance.LimitText']
        SignalIntegrity.App.Preferences['Appearance.LimitText']=60
        self.RoundDisplayedValues=SignalIntegrity.App.Preferences['Appearance.RoundDisplayedValues']
        SignalIntegrity.App.Preferences['Appearance.RoundDisplayedValues']=4
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        os.chdir(self.cwd)
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Cache.CacheResults']=self.Caching
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=self.UseSinX
        SignalIntegrity.App.Preferences['Appearance.LimitText']=self.TextLimit
        SignalIntegrity.App.Preferences['Appearance.RoundDisplayedValues']=self.RoundDisplayedValues
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def testBalunSymbolic(self):
        import SignalIntegrity.Lib as si
        symbolic=si.sd.Symbolic(size='small')
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines([
            'device D1 4',
            'device D2 4',
            'device G1 1 ground',
            'device G2 1 ground',
            'port 1 td 0 D1 1',
            'connect D1 2 D2 1',
            'port 2 td 0 D1 3',
            'connect D1 4 D2 3 G2 1',
            'connect D2 2 G1 1',
            'port 3 td 0 D2 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        D=si.sy.IdealTransformer('a')
        ssps.AssignSParameters('D1',D)
        ssps.AssignSParameters('D2',D)
        ssps.DocStart()
        ssps._AddEq('a=\\sqrt{2}')
        ssps.LaTeXSolution(size='biggest')
        ssps.DocEnd()
        #ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,'Ideal Balun')
    def testIdealBalunMM(self):
        self.SParameterResultsChecker('IdealBalunMM.si')
    def testIdealBalunSimulation(self):
        self.SimulationResultsChecker('IdealBalunSimulation.si')
    def testFourPortHFSSSymbolic(self):
        import SignalIntegrity.Lib as si
        symbolic=si.sd.Symbolic(size='small')
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines([
            'device D1 4 idealtransformer 1.0',
            'device S 4',
            'device D3 4 idealtransformer 1.0',
            'device G1 1 ground',
            'device G2 1 ground',
            'port 1 td 0 D1 1',
            'port 2 td 0 D3 1',
            'connect G1 1 D1 2',
            'connect D1 3 S 1',
            'connect D1 4 S 2',
            'connect S 3 D3 3',
            'connect S 4 D3 4',
            'connect D3 2 G2 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.DocStart()
        ssps.LaTeXSolution(size='biggest')
        ssps.DocEnd()
        #ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,'HFSS Four Port Measurement')
    def testBalunBackBack(self):
        import SignalIntegrity.Lib as si
        symbolic=si.sd.Symbolic(size='small')
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines([
            'device B1 3 balun',
            'device B2 3 balun',
            'port 1 td 0 B1 1',
            'port 2 td 0 B2 1',
            'connect B2 2 B1 2',
            'connect B2 3 B1 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.DocStart()
        ssps.LaTeXSolution(size='biggest')
        ssps.DocEnd()
        #ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,'Balun back-to-back')
    def testReferenceSymbolic(self):
        import SignalIntegrity.Lib as si
        symbolic=si.sd.Symbolic(size='small')
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines([
            'device D1 4 idealtransformer 1.0',
            'device G1 1 ground',
            'port 1 td 0 D1 1',
            'connect D1 2 G1 1',
            'port 2 td 0 D1 3',
            'port 3 td 0 D1 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.DocStart()
        ssps.LaTeXSolution(size='biggest')
        ssps.DocEnd()
        #ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,'Reference')
    def testSimulationUnjustifiedNodes(self):
        import SignalIntegrity.Lib as si
        symbolic=si.sd.Symbolic(size='small')
        sdp=si.p.SimulatorParser()
        sdp.AddLines([
            'voltagesource VG1 1',
            'device R1 2 R 50.0',
            'device D1 4 idealtransformer 1.0',
            'device G1 1 ground',
            'device R2 2 R 50.0',
            'device VO2 3 voltagetovoltageconverter',
            'connect R1 1 VG1 1',
            'connect R1 2 D1 1',
            'connect D1 2 G1 1',
            'voltageoutput VO1 VO2 2',
            'connect VO2 2 R2 1 D1 3',
            'voltageoutput VO3 D1 4',
            'connect D1 4 R2 2 VO2 1',
            'device VO2_3 1 open',
            'connect VO2 3 VO2_3 1',
            'voltageoutput VO2 VO2 3'])
        ssps=si.sd.SimulatorSymbolic(sdp.SystemDescription(),size='small')
        ssps.DocStart()
        ssps.LaTeXEquations()
        ssps.DocEnd()
        #ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,'Reference')
    def testSimulationUnjustifiedNodes2(self):
        import SignalIntegrity.Lib as si
        symbolic=si.sd.Symbolic(size='small')
        sdp=si.p.SimulatorParser()
        sdp.AddLines([
            'voltagesource VG1 1',
            'device R1 2 R 50.0',
            'device R2 2 R 50.0',
            'device VO2 3 voltagetovoltageconverter',
            'device Ref1 3 reference',
            'connect R1 1 VG1 1',
            'connect R1 2 Ref1 1',
            'voltageoutput VO1 Ref1 2',
            'connect Ref1 2 R2 1 VO2 2',
            'voltageoutput VO3 Ref1 3',
            'connect Ref1 3 VO2 1 R2 2',
            'device VO2_3 1 open',
            'connect VO2 3 VO2_3 1',
            'voltageoutput VO2 VO2 3'])
        ssps=si.sd.SimulatorSymbolic(sdp.SystemDescription(),size='small')
        ssps.DocStart()
        ssps.LaTeXEquations()
        ssps.DocEnd()
        #ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,'Reference')
    def testSimulationJustifiedNodes2(self):
        import SignalIntegrity.Lib as si
        symbolic=si.sd.Symbolic(size='small')
        sdp=si.p.SimulatorParser()
        sdp.AddLines([
            'voltagesource VG1 1',
            'device R1 2 R 50.0',
            'device R2 2 R 50.0',
            'device VO2 3 voltagetovoltageconverter',
            'device Ref1 3 reference',
            'connect R1 1 VG1 1',
            'connect R1 2 Ref1 1',
            'connect VO2 2 R2 1 Ref1 2',
            'connect R2 2 Ref1 3 VO2 1',
            'device VO2_3 1 open',
            'connect VO2 3 VO2_3 1',
            'voltageoutput VO2 VO2 3'])
        ssps=si.sd.SimulatorSymbolic(sdp.SystemDescription(),size='small')
        ssps.DocStart()
        ssps.LaTeXEquations()
        ssps.DocEnd()
        #ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,'Reference')
    def testSimulationVoltageJustifiedNoSVD(self):
        try:
            file_name=self.SetupCalculation('SimulationUnjustifiedNodesVoltage.si',
                                        self.id(),
                                        whether_svd=False,
                                        allow_nonunique=False,
                                        probe_list=[('VO1','on'),('VO2','off'),('VO3','off')])
            with self.assertRaises(AssertionError):
                self.SimulationResultsChecker(file_name, checkProject=False, checkPicture=False, checkNetlist=False)
        finally:
            self.RestoreCalculation(self.id())
    def testSimulationVoltageJustifiedSVD(self):
        try:
            file_name=self.SetupCalculation('SimulationUnjustifiedNodesVoltage.si',
                                        self.id(),
                                        whether_svd=True,
                                        allow_nonunique=False,
                                        probe_list=[('VO1','on'),('VO2','off'),('VO3','off')])
            self.SimulationResultsChecker(file_name, checkProject=False, checkPicture=False, checkNetlist=False)
        finally:
            self.RestoreCalculation(self.id())
    def testSimulationVoltageUnustifiedNoSVD(self):
        try:
            file_name=self.SetupCalculation('SimulationUnjustifiedNodesVoltage.si',
                                        self.id(),
                                        whether_svd=False,
                                        allow_nonunique=False,
                                        probe_list=[('VO1','on'),('VO2','on'),('VO3','on')])
            with self.assertRaises(AssertionError):
                self.SimulationResultsChecker(file_name, checkProject=False, checkPicture=False, checkNetlist=False)
        finally:
            self.RestoreCalculation(self.id())
    def testSimulationVoltageUnjustifiedSVDAllowNonUnique(self):
        try:
            file_name='SimulationUnjustifiedNodesVoltage.si'
            file_name=self.SetupCalculation(file_name,
                                        self.id(),
                                        whether_svd=True,
                                        allow_nonunique=True,
                                        probe_list=[('VO1','on'),('VO2','on'),('VO3','on')])
            os.chdir(self.path)
            pysi=SignalIntegrityAppHeadless()
            self.assertTrue(pysi.OpenProjectFile(os.path.realpath(file_name)),file_name + ' couldnt be opened')
            result=pysi.Simulate()
            self.assertNotEqual(result,{},file_name+' produced none')
            self.assertEqual(result.OutputWaveform('VO2')-result.OutputWaveform('VO3'),
                             result.OutputWaveform('VO1'),
                             'unjustified waveforms produced but dont add up')
        finally:
            self.RestoreCalculation(self.id())
    def testSimulationVoltageUnustifiedSVDNoNonUnique(self):
        try:
            file_name=self.SetupCalculation('SimulationUnjustifiedNodesVoltage.si',
                                        self.id(),
                                        whether_svd=True,
                                        allow_nonunique=False,
                                        probe_list=[('VO1','on'),('VO2','on'),('VO3','on')])
            with self.assertRaises(AssertionError):
                self.SimulationResultsChecker(file_name, checkProject=False, checkPicture=False, checkNetlist=False)
        finally:
            self.RestoreCalculation(self.id())
    def testSimulationCurrentJustifiedNoSVD(self):
        try:
            file_name=self.SetupCalculation('SimulationUnjustifiedNodesCurrent.si',
                                        self.id(),
                                        whether_svd=False,
                                        allow_nonunique=False,
                                        probe_list=[('IO1','on'),('IO2','off'),('IO3','off')])
            with self.assertRaises(AssertionError):
                self.SimulationResultsChecker(file_name, checkProject=False, checkPicture=False, checkNetlist=False)
        finally:
            self.RestoreCalculation(self.id())
    def testSimulationCurrentJustifiedSVD(self):
        try:
            file_name=self.SetupCalculation('SimulationUnjustifiedNodesCurrent.si',
                                        self.id(),
                                        whether_svd=True,
                                        allow_nonunique=False,
                                        probe_list=[('IO1','on'),('IO2','off'),('IO3','off')])
            self.SimulationResultsChecker(file_name, checkProject=False, checkPicture=False, checkNetlist=False)
        finally:
            self.RestoreCalculation(self.id())
    def testSimulationCurrentUnustifiedNoSVD(self):
        try:
            file_name=self.SetupCalculation('SimulationUnjustifiedNodesCurrent.si',
                                        self.id(),
                                        whether_svd=False,
                                        allow_nonunique=False,
                                        probe_list=[('IO1','on'),('IO2','on'),('IO3','on')])
            with self.assertRaises(AssertionError):
                self.SimulationResultsChecker(file_name, checkProject=False, checkPicture=False, checkNetlist=False)
        finally:
            self.RestoreCalculation(self.id())
    def testSimulationCurrentUnjustifiedSVDAllowNonUnique(self):
        try:
            file_name='SimulationUnjustifiedNodesCurrent.si'
            self.SetupCalculation(file_name,
                                        self.id(),
                                        whether_svd=True,
                                        allow_nonunique=True,
                                        probe_list=[('IO1','on'),('IO2','on'),('IO3','on')])
            os.chdir(self.path)
            pysi=SignalIntegrityAppHeadless()
            self.assertTrue(pysi.OpenProjectFile(os.path.realpath(file_name)),file_name + ' couldnt be opened')
            result=pysi.Simulate()
            self.assertNotEqual(result,{},file_name+' produced none')
            self.assertEqual(result.OutputWaveform('IO3')+result.OutputWaveform('IO2'),
                             result.OutputWaveform('IO1'),
                             'unjustified waveforms produced but dont add up')
        finally:
            self.RestoreCalculation(self.id())
    def testSimulationCurrentUnustifiedSVDNoNonUnique(self):
        try:
            file_name=self.SetupCalculation('SimulationUnjustifiedNodesCurrent.si',
                                        self.id(),
                                        whether_svd=True,
                                        allow_nonunique=False,
                                        probe_list=[('IO1','on'),('IO2','on'),('IO3','on')])
            with self.assertRaises(AssertionError):
                self.SimulationResultsChecker(file_name, checkProject=False, checkPicture=False, checkNetlist=False)
        finally:
            self.RestoreCalculation(self.id())
    def testFourToTwo(self):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        siapp=SignalIntegrityAppHeadless()
        self.assertTrue(siapp.OpenProjectFile('FourToTwoSimulation.si'))
        netlist=siapp.Drawing.schematic.NetList().textToShow
        sp=si.p.SimulatorParser()
        sp.AddLines([line.replace(' file None','') for line in netlist])
        sn=si.sd.SimulatorNumeric(sp.SystemDescription())
        import random
        sp_device=[[random.random() for _ in range(4)] for _ in range(4)]
        sn.AssignSParameters('S',sp_device)
        tm=sn.TransferMatrix()
        voltages=sn.SourceVector()
        currents=[name[0] for name in sn.pOutputList]
        # assert order of voltages and currents
        self.assertTrue(voltages==['V1','V2'])
        self.assertTrue(currents==['I1','I2'])
        import numpy as np
        V=np.identity(2)
        I=np.array(V).dot(tm)
        # I is actually tm, and is Y, the Y parameters
        Y=I
        sp_correct_twoport = si.sp.SParameters([0],[si.cvt.Y2S(Y)])
        # we now have the correct s-parameters - verify that they are computed properly
        # with references
        siapp=SignalIntegrityAppHeadless()
        self.assertTrue(siapp.OpenProjectFile('FourToTwoSp.si'))
        netlist=siapp.Drawing.schematic.NetList().textToShow
        sspnp=si.p.SystemSParametersNumericParser()
        sspnp.AddLines([line.replace(' file None','') for line in netlist])
        sspn=si.sd.SystemSParametersNumeric(sspnp.SystemDescription())
        sspn.AssignSParameters('S',sp_device)
        sp_calculated = si.sp.SParameters([0],[sspn.SParameters()])
        self.assertTrue(self.SParametersAreEqual(sp_correct_twoport, sp_calculated), 'calculated s-parameters incorrect')
        Wba=np.array([[1./3.,0],[0,1./3.]])
        Wbx=np.array([[2./3.,-2./3.,0,0,0,0,0,0],
                      [0,0,2./3.,-2./3.,0,0,0,0]])
        I=np.identity(8)
        S=sp_device
        Wxx=np.array([[0,0,0,0,S[0][0],S[0][1],S[0][2],S[0][3]],
                     [0,0,0,0,S[1][0],S[1][1],S[1][2],S[1][3]],
                     [0,0,0,0,S[2][0],S[2][1],S[2][2],S[2][3]],
                     [0,0,0,0,S[3][0],S[3][1],S[3][2],S[3][3]],
                     [1./3.,2./3.,0,0,0,0,0,0],
                     [2./3.,1./3.,0,0,0,0,0,0],
                     [0,0,1./3.,2./3.,0,0,0,0],
                     [0,0,2./3.,1./3.,0,0,0,0]])
        Wxa=np.array([[0,0],
                      [0,0],
                      [0,0],
                      [0,0],
                      [2./3.,0],
                      [-2./3.,0],
                      [0,2./3.],
                      [0,-2./3.]])
        sp_calculated_formula=si.sp.SParameters([0],[(Wba+Wbx.dot(np.linalg.inv(I-Wxx)).dot(Wxa)).tolist()])
        self.assertTrue(self.SParametersAreEqual(sp_correct_twoport, sp_calculated_formula), 'calculated s-parameters by formula incorrect')
        A=np.array([[2./3.,-2./3.,0,0],
                    [0,0,2./3.,-2./3.]])
        B=np.array([[1./3.,2./3.,0,0],
                   [2./3.,1./3.,0,0],
                   [0,0,1./3.,2./3.],
                   [0,0,2./3.,1./3.]])
        C=np.array([[2./3.,0],
                   [-2./3.,0],
                   [0,2./3.],
                   [0,-2./3.]])
        I4=np.identity(4)
        sp.calculated_formula_alternate=si.sp.SParameters([0],[(Wba+A.dot(S).dot(np.linalg.inv(I4-B.dot(S))).dot(C)).tolist()])
        self.assertTrue(self.SParametersAreEqual(sp_correct_twoport, sp_calculated_formula), 'calculated s-parameters by alternate formula incorrect')
    def testFourToTwoSymbolic(self):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        siapp=SignalIntegrityAppHeadless()
        self.assertTrue(siapp.OpenProjectFile('FourToTwoSp.si'))
        netlist=siapp.Drawing.schematic.NetList().textToShow
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines([line.replace(' file None','') for line in netlist])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.DocStart()
        ssps.LaTeXSolution()
        ssps.DocEnd()
        #ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,'Four to Two Port Symbolic Incorrect')
    def testFourToTwoSimulationSymbolic(self):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        siapp=SignalIntegrityAppHeadless()
        self.assertTrue(siapp.OpenProjectFile('FourToTwoSimulation.si'))
        netlist=siapp.Drawing.schematic.NetList().textToShow
        sp=si.p.SimulatorParser()
        sp.AddLines([line.replace(' file None','') for line in netlist])
        ss=si.sd.SimulatorSymbolic(sp.SystemDescription(),size='small')
        ss.DocStart()
        ss.LaTeXTransferMatrix()
        ss.DocEnd()
        #ss.Emit()
        self.CheckSymbolicResult(self.id(),ss,'Four to Two Port Symbolic Simulation Incorrect')
    def SetupCalculation(self,file_name,test_id,whether_svd,allow_nonunique,probe_list):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        siapp=SignalIntegrityAppHeadless()
        self.TrySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        SignalIntegrity.App.Preferences['Calculation.TrySVD']=whether_svd
        self.AllowNonUnique=SignalIntegrity.App.Preferences['Calculation.AllowNonUniqueSolutions']
        SignalIntegrity.App.Preferences['Calculation.AllowNonUniqueSolutions']=allow_nonunique
        SignalIntegrity.App.Preferences.SaveToFile()
        siapp=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
        opened=siapp.OpenProjectFile(file_name)
        for name,state in probe_list:
            siapp.Device(name)['state']['Value']=state
        siapp.SaveProjectToFile(test_id.split('.')[-1].replace('test',''))
        return siapp.fileparts.filename
    def RestoreCalculation(self,test_id):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        siapp=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation.TrySVD']=self.TrySVD
        SignalIntegrity.App.Preferences['Calculation.AllowNonUniqueSolutions']=self.AllowNonUnique
        SignalIntegrity.App.Preferences.SaveToFile()
        siapp=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
        os.remove(test_id.split('.')[-1].replace('test','')+'.si')
