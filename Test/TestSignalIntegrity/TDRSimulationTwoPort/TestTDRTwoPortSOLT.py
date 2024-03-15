"""
TestTDRTwoPortSOLT.py
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
import os

import matplotlib.pyplot as plt

from numpy import array
from numpy.linalg import inv

class TestTDRTwoPortTest(unittest.TestCase,si.test.SParameterCompareHelper,
                    si.test.SignalIntegrityAppTestHelper,
                    si.test.RoutineWriterTesterHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        si.test.RoutineWriterTesterHelper.__init__(self)
    def setUp(self):
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        #self.forceWritePictures=True
    def tearDown(self):
        os.chdir(self.cwd)
        unittest.TestCase.tearDown(self)
    def GetSimulationResultsCheck(self,filename):
        if not hasattr(TestTDRTwoPortTest, 'simdict'):
            TestTDRTwoPortTest.simdict=dict()
        if filename in TestTDRTwoPortTest.simdict:
            return TestTDRTwoPortTest.simdict[filename]
        TestTDRTwoPortTest.simdict[filename] = self.SimulationResultsChecker(filename)
        return TestTDRTwoPortTest.simdict[filename]

    def testTDRSOLPerfectButWithLength(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        f=si.fd.EvenlySpacedFrequencyList(500.e6,50)
        sp = si.p.SimulatorNumericParser(f)
        netListLines=['device R1 2 R 50.0',
                     'device T1 2 tline zc 50.0 td 500e-12',
                     'device I 4 currentcontrolledvoltagesource 1.0',
                     'device R3 1 R 50.0',
                     'device R4 1 R 50.0',
                     'device D3 4 directionalcoupler',
                     'voltagesource VG2 1',
                     'connect VG2 1 R1 1',
                     'output R1 2',
                     'connect R1 2 I 1',
                     'connect T1 1 D3 2',
                     'connect T1 2 R2 1',
                     'connect D3 1 I 2',
                     'output D3 3',
                     'connect D3 3 R3 1',
                     'output D3 4',
                     'connect D3 4 R4 1',
                     'device I_2 1 ground',
                     'device I_3 1 open',
                     'connect I 3 I_2 1',
                     'connect I 4 I_3 1',
                     'output I 4']
        sp.AddLines(netListLines+['device R2 1 ground'])
        tm=sp.TransferMatrices()
        td=si.td.wf.TimeDescriptor(-51e-9,112,1e9)
        iwf=si.td.wf.PulseWaveform(td,Amplitude=1.,StartTime=0.,PulseWidth=500e-12)
        tmp=si.td.f.TransferMatricesProcessor(tm)
        # The output waveforms are in order V, A, B, I
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawShort=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 open']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawOpen=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 50.0']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawLoad=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 20.0']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawDUT=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        f=spRawDUT.f()
        calStandards=[si.m.calkit.std.ShortStandard(f),si.m.calkit.OpenStandard(f),si.m.calkit.LoadStandard(f)]
        et=[si.m.cal.ErrorTerms().Initialize(1) for _ in range(len(f))]
        Gamma=[[[0.]] for _ in range(len(f))]
        for n in range(len(et)):
            et[n].ReflectCalibration([spRawShort[n][0][0],
                                   spRawOpen[n][0][0],
                                   spRawLoad[n][0][0]],
                                  [calStandards[0][n][0][0],
                                   calStandards[1][n][0][0],
                                   calStandards[2][n][0][0]],
                                  0)
            Gamma[n]=et[n].DutCalculation(spRawDUT[n])
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 1e-6),'s-parameters not equal')

    def testTDRSOLImPerfectButWithLength(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        f=si.fd.EvenlySpacedFrequencyList(500.e6,50)
        sp = si.p.SimulatorNumericParser(f)
        netListLines=['device R1 2 R 40.0',
                     'device T1 2 tline zc 60.0 td 5e-10',
                     'device I 4 currentcontrolledvoltagesource 1.0',
                     'device R3 1 R 50.0',
                     'device R4 1 R 50.0',
                     'device D3 4 directionalcoupler',
                     'voltagesource VG2 1',
                     'connect VG2 1 R1 1',
                     'output R1 2',
                     'connect R1 2 I 1',
                     'connect T1 1 D3 2',
                     'connect T1 2 R2 1',
                     'connect D3 1 I 2',
                     'output D3 3',
                     'connect D3 3 R3 1',
                     'output D3 4',
                     'connect D3 4 R4 1',
                     'device I_2 1 ground',
                     'device I_3 1 open',
                     'connect I 3 I_2 1',
                     'connect I 4 I_3 1',
                     'output I 4']
        sp.AddLines(netListLines+['device R2 1 ground'])
        tm=sp.TransferMatrices()
        td=si.td.wf.TimeDescriptor(-51e-9,112,1e9)
        iwf=si.td.wf.PulseWaveform(td,Amplitude=1.,StartTime=0.,PulseWidth=500e-12)
        tmp=si.td.f.TransferMatricesProcessor(tm)
        # The output waveforms are in order V, A, B, I
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawShort=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 open']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawOpen=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 50.0']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawLoad=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 20.0']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawDUT=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        f=spRawDUT.f()
        calStandards=[si.m.calkit.std.ShortStandard(f),si.m.calkit.OpenStandard(f),si.m.calkit.LoadStandard(f)]
        et=[si.m.cal.ErrorTerms().Initialize(1) for _ in range(len(f))]
        Gamma=[[[0.]] for _ in range(len(f))]
        for n in range(len(et)):
            et[n].ReflectCalibration([spRawShort[n][0][0],
                                   spRawOpen[n][0][0],
                                   spRawLoad[n][0][0]],
                                  [calStandards[0][n][0][0],
                                   calStandards[1][n][0][0],
                                   calStandards[2][n][0][0]],
                                  0)
            Gamma[n]=et[n].DutCalculation(spRawDUT[n])
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 1e-6),'s-parameters not equal')

    def testVNASOLPerfect(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        f=si.fd.EvenlySpacedFrequencyList(500.e6,50)
        sp = si.p.SimulatorNumericParser(f)
        netListLines=['device R1 2 R 50.0',
                     'device T1 2 tline zc 50.0 td 0.0',
                     'device I 4 currentcontrolledvoltagesource 1.0',
                     'device R3 1 R 50.0',
                     'device R4 1 R 50.0',
                     'device D3 4 directionalcoupler',
                     'voltagesource VG2 1',
                     'connect VG2 1 R1 1',
                     'output R1 2',
                     'connect R1 2 I 1',
                     'connect T1 1 D3 2',
                     'connect T1 2 R2 1',
                     'connect D3 1 I 2',
                     'output D3 3',
                     'connect D3 3 R3 1',
                     'output D3 4',
                     'connect D3 4 R4 1',
                     'device I_2 1 ground',
                     'device I_3 1 open',
                     'connect I 3 I_2 1',
                     'connect I 4 I_3 1',
                     'output I 4']

        sp.AddLines(netListLines+['device R2 1 ground'])
        tm=sp.TransferMatrices()
        td=si.td.wf.TimeDescriptor(-51e-9,112,1e9)
        iwf=si.td.wf.PulseWaveform(td,Amplitude=1.,StartTime=0.,PulseWidth=500e-12)
        tmp=si.td.f.TransferMatricesProcessor(tm)
        # The output waveforms are in order V, A, B, I
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawShort=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 open']).TransferMatrices())
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawOpen=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 50.0']).TransferMatrices())
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawLoad=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 20.0']).TransferMatrices())
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawDUT=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        f=spRawDUT.f()
        calStandards=[si.m.calkit.std.ShortStandard(f),si.m.calkit.OpenStandard(f),si.m.calkit.LoadStandard(f)]
        et=[si.m.cal.ErrorTerms().Initialize(1) for _ in range(len(f))]
        Gamma=[[[0.]] for _ in range(len(f))]
        for n in range(len(et)):
            et[n].ReflectCalibration([spRawShort[n][0][0],
                                   spRawOpen[n][0][0],
                                   spRawLoad[n][0][0]],
                                  [calStandards[0][n][0][0],
                                   calStandards[1][n][0][0],
                                   calStandards[2][n][0][0]],
                                  0)
            Gamma[n]=et[n].DutCalculation(spRawDUT[n])
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 1e-6),'s-parameters not equal')
        return

        cl=[si.m.cal.ReflectCalibrationMeasurement(spRawShort,si.m.calkit.std.ShortStandard(f),1,'s'),
            si.m.cal.ReflectCalibrationMeasurement(spRawOpen,si.m.calkit.std.OpenStandard(f),1,'o'),
            si.m.cal.ReflectCalibrationMeasurement(spRawLoad,si.m.calkit.std.LoadStandard(f),1,'l')]
        cm=si.m.cal.Calibration(1,cl)

        et=cm.ErrorTerms()
        pass

    def testVNASOLImperfect(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        f=si.fd.EvenlySpacedFrequencyList(500.e6,50)
        sp = si.p.SimulatorNumericParser(f)
        netListLines=['device R1 2 R 40.0',
                     'device T1 2 tline zc 60.0 td 5e-10',
                     'device I 4 currentcontrolledvoltagesource 1.0',
                     'device R3 1 R 50.0',
                     'device R4 1 R 50.0',
                     'device D3 4 directionalcoupler',
                     'voltagesource VG2 1',
                     'connect VG2 1 R1 1',
                     'output R1 2',
                     'connect R1 2 I 1',
                     'connect T1 1 D3 2',
                     'connect T1 2 R2 1',
                     'connect D3 1 I 2',
                     'output D3 3',
                     'connect D3 3 R3 1',
                     'output D3 4',
                     'connect D3 4 R4 1',
                     'device I_2 1 ground',
                     'device I_3 1 open',
                     'connect I 3 I_2 1',
                     'connect I 4 I_3 1',
                     'output I 4']
        sp.AddLines(netListLines+['device R2 1 ground'])
        tm=sp.TransferMatrices()
        td=si.td.wf.TimeDescriptor(-51e-9,112,1e9)
        iwf=si.td.wf.PulseWaveform(td,Amplitude=1.,StartTime=0.,PulseWidth=500e-12)
        tmp=si.td.f.TransferMatricesProcessor(tm)
        # The output waveforms are in order V, A, B, I
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawShort=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 open']).TransferMatrices())
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawOpen=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 50.0']).TransferMatrices())
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawLoad=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 20.0']).TransferMatrices())
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawDUT=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        f=spRawDUT.f()
        calStandards=[si.m.calkit.std.ShortStandard(f),si.m.calkit.OpenStandard(f),si.m.calkit.LoadStandard(f)]
        et=[si.m.cal.ErrorTerms().Initialize(1) for _ in range(len(f))]
        Gamma=[[[0.]] for _ in range(len(f))]
        for n in range(len(et)):
            et[n].ReflectCalibration([spRawShort[n][0][0],
                                   spRawOpen[n][0][0],
                                   spRawLoad[n][0][0]],
                                  [calStandards[0][n][0][0],
                                   calStandards[1][n][0][0],
                                   calStandards[2][n][0][0]],
                                  0)
            Gamma[n]=et[n].DutCalculation(spRawDUT[n])
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 1e-6),'s-parameters not equal')
        return

        cl=[si.m.cal.ReflectCalibrationMeasurement(spRawShort,si.m.calkit.std.ShortStandard(f),1,'s'),
            si.m.cal.ReflectCalibrationMeasurement(spRawOpen,si.m.calkit.std.OpenStandard(f),1,'o'),
            si.m.cal.ReflectCalibrationMeasurement(spRawLoad,si.m.calkit.std.LoadStandard(f),1,'l')]
        cm=si.m.cal.Calibration(1,cl)

        et=cm.ErrorTerms()

    def testTDRSOLClosedForm(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        f=si.fd.EvenlySpacedFrequencyList(500.e6,50)
        sp = si.p.SimulatorNumericParser(f)
        netListLines=['device R1 2 R 40.0',
                     'device T1 2 tline zc 60.0 td 5e-10',
                     'device I 4 currentcontrolledvoltagesource 1.0',
                     'device R3 1 R 50.0',
                     'device R4 1 R 50.0',
                     'device D3 4 directionalcoupler',
                     'voltagesource VG2 1',
                     'connect VG2 1 R1 1',
                     'output R1 2',
                     'connect R1 2 I 1',
                     'connect T1 1 D3 2',
                     'connect T1 2 R2 1',
                     'connect D3 1 I 2',
                     'output D3 3',
                     'connect D3 3 R3 1',
                     'output D3 4',
                     'connect D3 4 R4 1',
                     'device I_2 1 ground',
                     'device I_3 1 open',
                     'connect I 3 I_2 1',
                     'connect I 4 I_3 1',
                     'output I 4']
        sp.AddLines(netListLines+['device R2 1 R 20.0'])
        tm=sp.TransferMatrices()
        td=si.td.wf.TimeDescriptor(-51e-9,112,1e9)
        iwf=si.td.wf.PulseWaveform(td,Amplitude=1.,StartTime=0.,PulseWidth=500e-12)
        tmp=si.td.f.TransferMatricesProcessor(tm)
        # The output waveforms are in order V, A, B, I
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawDUT=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])
        pass

    def SParameterRegressionChecker(self,sp,spfilename):
        currentDirectory=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))        
        if not os.path.exists(spfilename):
            sp.WriteToFile(spfilename)
            if not self.relearn:
                self.assertTrue(False, spfilename + ' not found')
        regression=si.sp.SParameterFile(spfilename)
        SpAreEqual=self.SParametersAreEqual(sp, regression,1e-3)

        if not SpAreEqual:
            if si.test.SignalIntegrityAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(regression.m_P):
                    for c in range(regression.m_P):
                        plt.semilogy(regression.f(),[abs(sp[n][r][c]-regression[n][r][c]) for n in range(len(regression))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(regression.m_P):
                    for c in range(regression.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(sp.FrequencyResponse(r+1,c+1).Frequencies(),sp.FrequencyResponse(r+1,c+1).Values('dB'),label='S'+str(r+1)+str(c+1)+' calculated')
                        plt.plot(regression.FrequencyResponse(r+1,c+1).Frequencies(),regression.FrequencyResponse(r+1,c+1).Values('dB'),label='S'+str(r+1)+str(c+1)+' regression')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

                for r in range(regression.m_P):
                    for c in range(regression.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(sp.FrequencyResponse(r+1,c+1).Frequencies(),sp.FrequencyResponse(r+1,c+1).Values('deg'),label='S'+str(r+1)+str(c+1)+' calculated')
                        plt.plot(regression.FrequencyResponse(r+1,c+1).Frequencies(),regression.FrequencyResponse(r+1,c+1).Values('deg'),label='S'+str(r+1)+str(c+1)+' regression')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(self.SParametersAreEqual(sp, regression,1e-3),spfilename + ' incorrect')
        os.chdir(currentDirectory)
    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])

    def testTDRSOLPerfectButWithLengthDelay(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        f=si.fd.EvenlySpacedFrequencyList(500.e6,50)
        sp = si.p.SimulatorNumericParser(f)
        netListLines=['device R1 2 R 50.0',
                      'device T1 2 tline zc 50.0 td 1e-9',
                      'device I 4 currentcontrolledvoltagesource 1.0',
                      'device R3 1 R 50.0',
                      'device R4 1 R 50.0',
                      'device D3 4 directionalcoupler',
                      'voltagesource VG2 1',
                      'device T2 2 tline zc 50.0 td 1e-9',
                      'connect VG2 1 R1 1',
                      'connect R1 2 T2 1',
                      'connect T1 1 D3 2',
                      'connect T1 2 R2 1',
                      'output I 1',
                      'connect I 1 T2 2',
                      'connect D3 1 I 2',
                      'output D3 3',
                      'connect D3 3 R3 1',
                      'output D3 4',
                      'connect D3 4 R4 1',
                      'device I_2 1 ground',
                      'device I_3 1 open',
                      'connect I 3 I_2 1',
                      'connect I 4 I_3 1',
                      'output I 4']
        sp.AddLines(netListLines+['device R2 1 ground'])
        tm=sp.TransferMatrices()
        td=si.td.wf.TimeDescriptor(-52e-9,129,1e9)
        iwf=si.td.wf.PulseWaveform(td,Amplitude=1.,StartTime=-2e-9,PulseWidth=1e-9)
        tmp=si.td.f.TransferMatricesProcessor(tm)
        # The output waveforms are in order V, A, B, I
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawShort=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 open']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawOpen=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 50.0']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawLoad=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 20.0']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawDUT=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        f=spRawDUT.f()
        calStandards=[si.m.calkit.std.ShortStandard(f),si.m.calkit.OpenStandard(f),si.m.calkit.LoadStandard(f)]
        et=[si.m.cal.ErrorTerms().Initialize(1) for _ in range(len(f))]
        Gamma=[[[0.]] for _ in range(len(f))]
        GammaAlt=[[[0.]] for _ in range(len(f))]
        for n in range(len(et)):
            et[n].ReflectCalibration([spRawShort[n][0][0],
                                   spRawOpen[n][0][0],
                                   spRawLoad[n][0][0]],
                                  [calStandards[0][n][0][0],
                                   calStandards[1][n][0][0],
                                   calStandards[2][n][0][0]],
                                  0)
            Gamma[n]=et[n].DutCalculation(spRawDUT[n])
            GammaAlt[n]=et[n].DutCalculationAlternate(spRawDUT[n])
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTCalcAltSp=si.sp.SParameters(f,GammaAlt)
        self.SParameterRegressionChecker(DUTCalcAltSp, self.NameForTest()+'Alternate_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 1e-6),'s-parameters not equal')

    def testTDRSOLImPerfectButWithLengthDelay(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        f=si.fd.EvenlySpacedFrequencyList(500.e6,50)
        sp = si.p.SimulatorNumericParser(f)
        netListLines=['device R1 2 R 40.0',
                      'device T1 2 tline zc 60.0 td 1e-9',
                      'device I 4 currentcontrolledvoltagesource 1.0',
                      'device R3 1 R 50.0',
                      'device R4 1 R 50.0',
                      'device D3 4 directionalcoupler',
                      'voltagesource VG2 1',
                      'device T2 2 tline zc 55.0 td 1e-9',
                      'connect VG2 1 R1 1',
                      'connect R1 2 T2 1',
                      'connect T1 1 D3 2',
                      'connect T1 2 R2 1',
                      'output I 1',
                      'connect I 1 T2 2',
                      'connect D3 1 I 2',
                      'output D3 3',
                      'connect D3 3 R3 1',
                      'output D3 4',
                      'connect D3 4 R4 1',
                      'device I_2 1 ground',
                      'device I_3 1 open',
                      'connect I 3 I_2 1',
                      'connect I 4 I_3 1',
                      'output I 4']
        sp.AddLines(netListLines+['device R2 1 ground'])
        tm=sp.TransferMatrices()
        td=si.td.wf.TimeDescriptor(-52e-9,129,1e9)
        iwf=si.td.wf.PulseWaveform(td,Amplitude=1.,StartTime=-2e-9,PulseWidth=1e-9)
        tmp=si.td.f.TransferMatricesProcessor(tm)
        # The output waveforms are in order V, A, B, I
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawShort=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        if self.plot:
            plt.clf()
            plt.title('short measure waveforms')
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(owf.Times('ns'),owf.Values(),label='voltage')
            plt.plot(refwf.DelayBy(0).Times('ns'),refwf.DelayBy(0).Values(),label='reflect')
            plt.plot(incwf.Times('ns'),incwf.Values(),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('short measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('amplitude (dB)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('dB'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('dB'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('short measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('phase (deg)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('deg'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('deg'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 open']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawOpen=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        if self.plot:
            plt.clf()
            plt.title('open measure waveforms')
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(owf.Times('ns'),owf.Values(),label='voltage')
            plt.plot(refwf.DelayBy(0).Times('ns'),refwf.DelayBy(0).Values(),label='reflect')
            plt.plot(incwf.Times('ns'),incwf.Values(),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('open measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('amplitude (dB)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('dB'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('dB'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('open measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('phase (deg)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('deg'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('deg'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 50.0']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawLoad=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        if self.plot:
            plt.clf()
            plt.title('load measure waveforms')
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(owf.Times('ns'),owf.Values(),label='voltage')
            plt.plot(refwf.DelayBy(0).Times('ns'),refwf.DelayBy(0).Values(),label='reflect')
            plt.plot(incwf.Times('ns'),incwf.Values(),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('load measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('amplitude (dB)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('dB'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('dB'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('load measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('phase (deg)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('deg'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('deg'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 20.0']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawDUT=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        if self.plot:
            plt.clf()
            plt.title('DUT measure waveforms')
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(owf.Times('ns'),owf.Values(),label='voltage')
            plt.plot(refwf.DelayBy(0).Times('ns'),refwf.DelayBy(0).Values(),label='reflect')
            plt.plot(incwf.Times('ns'),incwf.Values(),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('DUT measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('amplitude (dB)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('dB'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('dB'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('DUT measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('phase (deg)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('deg'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('deg'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

        f=spRawDUT.f()
        calStandards=[si.m.calkit.std.ShortStandard(f),si.m.calkit.OpenStandard(f),si.m.calkit.LoadStandard(f)]
        et=[si.m.cal.ErrorTerms().Initialize(1) for _ in range(len(f))]
        Gamma=[[[0.]] for _ in range(len(f))]
        for n in range(len(et)):
            et[n].ReflectCalibration([spRawShort[n][0][0],
                                   spRawOpen[n][0][0],
                                   spRawLoad[n][0][0]],
                                  [calStandards[0][n][0][0],
                                   calStandards[1][n][0][0],
                                   calStandards[2][n][0][0]],
                                  0)
            Gamma[n]=et[n].DutCalculation(spRawDUT[n])
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 1e-4),'s-parameters not equal')

    def testVNASOLPerfectDelay(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        f=si.fd.EvenlySpacedFrequencyList(500.e6,50)
        sp = si.p.SimulatorNumericParser(f)
        netListLines=['device R1 2 R 50.0',
                      'device T1 2 tline zc 50.0 td 0.',
                      'device I 4 currentcontrolledvoltagesource 1.0',
                      'device R3 1 R 50.0',
                      'device R4 1 R 50.0',
                      'device D3 4 directionalcoupler',
                      'voltagesource VG2 1',
                      'device T2 2 tline zc 50.0 td 5e-10',
                      'connect VG2 1 R1 1',
                      'connect R1 2 T2 1',
                      'connect T1 1 D3 2',
                      'connect T1 2 R2 1',
                      'output I 1',
                      'connect I 1 T2 2',
                      'connect D3 1 I 2',
                      'output D3 3',
                      'connect D3 3 R3 1',
                      'output D3 4',
                      'connect D3 4 R4 1',
                      'device I_2 1 ground',
                      'device I_3 1 open',
                      'connect I 3 I_2 1',
                      'connect I 4 I_3 1',
                      'output I 4']
        sp.AddLines(netListLines+['device R2 1 ground'])
        tm=sp.TransferMatrices()
        td=si.td.wf.TimeDescriptor(-50.5e-9,112,1e9)
        iwf=si.td.wf.PulseWaveform(td,Amplitude=1.,StartTime=-1e-9,PulseWidth=1e-9)
        tmp=si.td.f.TransferMatricesProcessor(tm)
        # The output waveforms are in order V, A, B, I
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawShort=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 open']).TransferMatrices())
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawOpen=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 50.0']).TransferMatrices())
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawLoad=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 20.0']).TransferMatrices())
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawDUT=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        f=spRawDUT.f()
        calStandards=[si.m.calkit.std.ShortStandard(f),si.m.calkit.OpenStandard(f),si.m.calkit.LoadStandard(f)]
        et=[si.m.cal.ErrorTerms().Initialize(1) for _ in range(len(f))]
        Gamma=[[[0.]] for _ in range(len(f))]
        for n in range(len(et)):
            et[n].ReflectCalibration([spRawShort[n][0][0],
                                   spRawOpen[n][0][0],
                                   spRawLoad[n][0][0]],
                                  [calStandards[0][n][0][0],
                                   calStandards[1][n][0][0],
                                   calStandards[2][n][0][0]],
                                  0)
            Gamma[n]=et[n].DutCalculation(spRawDUT[n])
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 1e-6),'s-parameters not equal')
        return

        cl=[si.m.cal.ReflectCalibrationMeasurement(spRawShort,si.m.calkit.std.ShortStandard(f),1,'s'),
            si.m.cal.ReflectCalibrationMeasurement(spRawOpen,si.m.calkit.std.OpenStandard(f),1,'o'),
            si.m.cal.ReflectCalibrationMeasurement(spRawLoad,si.m.calkit.std.LoadStandard(f),1,'l')]
        cm=si.m.cal.Calibration(1,cl)

        et=cm.ErrorTerms()
        pass

    def testVNASOLImperfectDelay(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        f=si.fd.EvenlySpacedFrequencyList(500.e6,50)

        netListLines=['device R1 2 R 40.0',
                      'device T1 2 tline zc 80.0 td 5e-10',
                      'device I 4 currentcontrolledvoltagesource 1.0',
                      'device R3 1 R 50.0',
                      'device R4 1 R 50.0',
                      'device D3 4 directionalcoupler',
                      'voltagesource VG2 1',
                      'device T2 2 tline zc 35.0 td 1e-9',
                      'connect VG2 1 R1 1',
                      'connect R1 2 T2 1',
                      'connect T1 1 D3 2',
                      'connect T1 2 R2 1',
                      'output I 1',
                      'connect I 1 T2 2',
                      'connect D3 1 I 2',
                      'output D3 3',
                      'connect D3 3 R3 1',
                      'output D3 4',
                      'connect D3 4 R4 1',
                      'device I_2 1 ground',
                      'device I_3 1 open',
                      'connect I 3 I_2 1',
                      'connect I 4 I_3 1',
                      'output I 4']

        tm=si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 ground']).TransferMatrices()
        self.SParameterRegressionChecker(tm.SParameters(), self.NameForTest()+'_ShortXferMatrices.s4p')
        td=si.td.wf.TimeDescriptor(-51e-9,112,1e9)
        iwf=si.td.wf.PulseWaveform(td,Amplitude=1.,StartTime=-1.5e-9,PulseWidth=1.5e-9)
        tmp=si.td.f.TransferMatricesProcessor(tm)
        # The output waveforms are in order V, A, B, I
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawShort=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        if self.plot:
            plt.clf()
            plt.title('short measure waveforms')
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(wfList[2].DelayBy(-1e-9).Times('ns'),wfList[2].DelayBy(1e-9).Values(),label='reflect')
            plt.plot(wfList[1].Times('ns'),wfList[1].Values(),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('short measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('amplitude (dB)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('dB'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('dB'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('short measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('phase (deg)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('deg'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('deg'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

        tm=si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 5e9']).TransferMatrices()
        self.SParameterRegressionChecker(tm.SParameters(), self.NameForTest()+'_OpenXferMatrices.s4p')
        tmp = si.td.f.TransferMatricesProcessor(tm)
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawOpen=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        if self.plot:
            plt.clf()
            plt.title('open measure waveforms')
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(wfList[2].DelayBy(-1e-9).Times('ns'),wfList[2].DelayBy(1e-9).Values(),label='reflect')
            plt.plot(wfList[1].Times('ns'),wfList[1].Values(),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('open measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('amplitude (dB)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('dB'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('dB'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('open measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('phase (deg)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('deg'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('deg'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

        tm=si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 50.0']).TransferMatrices()
        self.SParameterRegressionChecker(tm.SParameters(), self.NameForTest()+'_LoadXferMatrices.s4p')
        tmp = si.td.f.TransferMatricesProcessor(tm)
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawLoad=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        if self.plot:
            plt.clf()
            plt.title('load measure waveforms')
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(wfList[2].DelayBy(-1e-9).Times('ns'),wfList[2].DelayBy(1e-9).Values(),label='reflect')
            plt.plot(wfList[1].Times('ns'),wfList[1].Values(),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('load measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('amplitude (dB)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('dB'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('dB'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('load measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('phase (deg)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('deg'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('deg'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

        tm=si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 20.0']).TransferMatrices()
        self.SParameterRegressionChecker(tm.SParameters(), self.NameForTest()+'_DUTXferMatrices.s4p')
        tmp = si.td.f.TransferMatricesProcessor(tm)
        wfList=tmp.ProcessWaveforms([iwf])
        refwffc=wfList[2].FrequencyContent()
        incwffc=wfList[1].FrequencyContent()
        spRawDUT=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        if self.plot:
            plt.clf()
            plt.title('DUT measure waveforms')
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(wfList[2].DelayBy(-1e-9).Times('ns'),wfList[2].DelayBy(1e-9).Values(),label='reflect')
            plt.plot(wfList[1].Times('ns'),wfList[1].Values(),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('DUT measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('amplitude (dB)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('dB'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('dB'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('DUT measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('phase (deg)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('deg'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('deg'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

        f=spRawDUT.f()
        calStandards=[si.m.calkit.std.ShortStandard(f),si.m.calkit.OpenStandard(f),si.m.calkit.LoadStandard(f)]
        et=[si.m.cal.ErrorTerms().Initialize(1) for _ in range(len(f))]
        Gamma=[[[0.]] for _ in range(len(f))]
        for n in range(len(et)):
            et[n].ReflectCalibration([spRawShort[n][0][0],
                                   spRawOpen[n][0][0],
                                   spRawLoad[n][0][0]],
                                  [calStandards[0][n][0][0],
                                   calStandards[1][n][0][0],
                                   calStandards[2][n][0][0]],
                                  0)
            Gamma[n]=et[n].DutCalculation(spRawDUT[n])
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 5e-4),'s-parameters not equal')

    def testTDRSOLImPerfectButWithLengthDelayCalStd(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        f=si.fd.EvenlySpacedFrequencyList(500.e6,50)
        sp = si.p.SimulatorNumericParser(f)
        netListLines=['device R1 2 R 40.0',
                      'device T1 2 tline zc 60.0 td 1e-9',
                      'device I 4 currentcontrolledvoltagesource 1.0',
                      'device R3 1 R 50.0',
                      'device R4 1 R 50.0',
                      'device D3 4 directionalcoupler',
                      'voltagesource VG2 1',
                      'device T2 2 tline zc 55.0 td 1e-9',
                      'connect VG2 1 R1 1',
                      'connect R1 2 T2 1',
                      'connect T1 1 D3 2',
                      'connect T1 2 R2 1',
                      'output I 1',
                      'connect I 1 T2 2',
                      'connect D3 1 I 2',
                      'output D3 3',
                      'connect D3 3 R3 1',
                      'output D3 4',
                      'connect D3 4 R4 1',
                      'device I_2 1 ground',
                      'device I_3 1 open',
                      'connect I 3 I_2 1',
                      'connect I 4 I_3 1',
                      'output I 4']
        sp.AddLines(netListLines+['device R2 1 shortstd'])
        tm=sp.TransferMatrices()
        td=si.td.wf.TimeDescriptor(-52e-9,129,1e9)
        iwf=si.td.wf.PulseWaveform(td,Amplitude=1.,StartTime=-2e-9,PulseWidth=1e-9)
        tmp=si.td.f.TransferMatricesProcessor(tm)
        # The output waveforms are in order V, A, B, I
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawShort=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        if self.plot:
            plt.clf()
            plt.title('short measure waveforms')
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(owf.Times('ns'),owf.Values(),label='voltage')
            plt.plot(refwf.DelayBy(0).Times('ns'),refwf.DelayBy(0).Values(),label='reflect')
            plt.plot(incwf.Times('ns'),incwf.Values(),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('short measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('amplitude (dB)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('dB'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('dB'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('short measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('phase (deg)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('deg'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('deg'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 openstd']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawOpen=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        if self.plot:
            plt.clf()
            plt.title('open measure waveforms')
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(owf.Times('ns'),owf.Values(),label='voltage')
            plt.plot(refwf.DelayBy(0).Times('ns'),refwf.DelayBy(0).Values(),label='reflect')
            plt.plot(incwf.Times('ns'),incwf.Values(),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('open measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('amplitude (dB)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('dB'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('dB'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('open measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('phase (deg)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('deg'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('deg'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 loadstd']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawLoad=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        if self.plot:
            plt.clf()
            plt.title('load measure waveforms')
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(owf.Times('ns'),owf.Values(),label='voltage')
            plt.plot(refwf.DelayBy(0).Times('ns'),refwf.DelayBy(0).Values(),label='reflect')
            plt.plot(incwf.Times('ns'),incwf.Values(),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('load measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('amplitude (dB)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('dB'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('dB'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('load measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('phase (deg)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('deg'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('deg'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 20.0']).TransferMatrices())
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawDUT=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        if self.plot:
            plt.clf()
            plt.title('DUT measure waveforms')
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(owf.Times('ns'),owf.Values(),label='voltage')
            plt.plot(refwf.DelayBy(0).Times('ns'),refwf.DelayBy(0).Values(),label='reflect')
            plt.plot(incwf.Times('ns'),incwf.Values(),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('DUT measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('amplitude (dB)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('dB'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('dB'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

            plt.clf()
            plt.title('DUT measure frequency content')
            plt.xlabel('frequency (MHz)')
            plt.ylabel('phase (deg)')
            plt.plot(refwffc._DelayBy(-1e-9).Frequencies('MHz'),refwffc._DelayBy(-1e-9).Values('deg'),label='reflect')
            plt.plot(incwffc.Frequencies('MHz'),incwffc.Values('deg'),label='incident')
            plt.legend(loc='upper right')
            plt.show()

        f=spRawDUT.f()
        calStandards=[si.m.calkit.std.ShortStandard(f),si.m.calkit.OpenStandard(f),si.m.calkit.LoadStandard(f)]
        et=[si.m.cal.ErrorTerms().Initialize(1) for _ in range(len(f))]
        Gamma=[[[0.]] for _ in range(len(f))]
        for n in range(len(et)):
            et[n].ReflectCalibration([spRawShort[n][0][0],
                                   spRawOpen[n][0][0],
                                   spRawLoad[n][0][0]],
                                  [calStandards[0][n][0][0],
                                   calStandards[1][n][0][0],
                                   calStandards[2][n][0][0]],
                                  0)
            Gamma[n]=et[n].DutCalculation(spRawDUT[n])
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 1e-3),'s-parameters not equal')


    def testTDRSimulationSOL(self):
        result = self.GetSimulationResultsCheck('TDRSimulationSOL.si')
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]

        tdrWaveforms=dict(zip(outputNames,outputWaveforms))

        wfList=['Short','Open','Load','Dut']
        spDict=dict()

        for name in wfList:
            wf=tdrWaveforms['V'+name]
            refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
            incwf=wf-refwf
            refwffc=refwf.FrequencyContent()
            incwffc=incwf.FrequencyContent()
            spDict[name]=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        f=spDict['Dut'].f()
        calStandards=[si.m.calkit.std.ShortStandard(f),si.m.calkit.OpenStandard(f),si.m.calkit.LoadStandard(f)]
        et=[si.m.cal.ErrorTerms().Initialize(1) for _ in range(len(f))]
        Gamma=[[[0.]] for _ in range(len(f))]
        for n in range(len(et)):
            et[n].ReflectCalibration([spDict['Short'][n][0][0],
                                   spDict['Open'][n][0][0],
                                   spDict['Load'][n][0][0]],
                                  [calStandards[0][n][0][0],
                                   calStandards[1][n][0][0],
                                   calStandards[2][n][0][0]],
                                  0)
            Gamma[n]=et[n].DutCalculation(spDict['Dut'][n])
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSp=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s1p')

        if self.plot:
            plt.clf()
            plt.title('error magnitude')
            plt.xlabel('frequency (GHz)')
            plt.ylabel('amplitude')
            for r in range(DUTCalcSp.m_P):
                for c in range(DUTCalcSp.m_P):
                    plt.semilogy(DUTCalcSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTCalcSp))],label='S'+str(r)+str(c))
            plt.legend(loc='upper right')
            plt.show()


        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')


    def testTDRSimulationSOLT(self):
        result = self.GetSimulationResultsCheck('TDRSimulationSOLTVOnly.si')
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]

        tdrWaveforms=dict(zip(outputNames,outputWaveforms))

        spDict=dict()

        wf=tdrWaveforms['VThru11']
        incwf11=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc11=incwf11.FrequencyContent()
        refwf11=wf-incwf11
        refwffc11=refwf11.FrequencyContent()

        wf=tdrWaveforms['VThru22']
        incwf22=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc22=incwf22.FrequencyContent()
        refwf22=wf-incwf22
        refwffc22=refwf22.FrequencyContent()

        wf=tdrWaveforms['VThru21']
        incwf21=incwf11
        incwffc21=incwf21.FrequencyContent()
        refwf21=wf
        refwffc21=refwf21.FrequencyContent()

        wf=tdrWaveforms['VThru12']
        incwf12=incwf22
        incwffc12=incwf12.FrequencyContent()
        refwf12=wf
        refwffc12=refwf12.FrequencyContent()

        f=incwffc11.FrequencyList()
        spDict['Thru']=si.sp.SParameters(f,[[[refwffc11[n]/incwffc11[n],refwffc12[n]/incwffc12[n]],
                                             [refwffc21[n]/incwffc21[n],refwffc22[n]/incwffc22[n]]]
                                            for n in range(len(f))])

        wf=tdrWaveforms['VDut11']
        incwf11=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc11=incwf11.FrequencyContent()
        refwf11=wf-incwf11
        refwffc11=refwf11.FrequencyContent()

        wf=tdrWaveforms['VDut22']
        incwf22=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc22=incwf22.FrequencyContent()
        refwf22=wf-incwf22
        refwffc22=refwf22.FrequencyContent()

        wf=tdrWaveforms['VDut21']
        incwf21=incwf11
        incwffc21=incwf21.FrequencyContent()
        refwf21=wf
        refwffc21=refwf21.FrequencyContent()

        wf=tdrWaveforms['VDut12']
        incwf12=incwf22
        incwffc12=incwf12.FrequencyContent()
        refwf12=wf
        refwffc12=refwf12.FrequencyContent()

        f=incwffc11.FrequencyList()
        spDict['Dut']=si.sp.SParameters(f,[[[refwffc11[n]/incwffc11[n],refwffc12[n]/incwffc12[n]],
                                             [refwffc21[n]/incwffc21[n],refwffc22[n]/incwffc22[n]]]
                                            for n in range(len(f))])

        wf=tdrWaveforms['VShort1']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Short1']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VOpen1']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Open1']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VLoad1']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Load1']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VShort2']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Short2']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VOpen2']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Open2']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VLoad2']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Load2']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        f=spDict['Dut'].f()
        calStandards=[si.m.calkit.std.ShortStandard(f),
                      si.m.calkit.OpenStandard(f),
                      si.m.calkit.LoadStandard(f),
                      si.m.calkit.ThruStandard(f,100e-12)]
        et=[si.m.cal.ErrorTerms().Initialize(2) for _ in range(len(f))]
        DUT=[[[0.,0.],[0.,0.]] for _ in range(len(f))]
        DUTAlt=[[[0.,0.],[0.,0.]] for _ in range(len(f))]
        for n in range(len(et)):
            et[n].ReflectCalibration([spDict['Short1'][n][0][0],spDict['Open1'][n][0][0],spDict['Load1'][n][0][0]],
                [calStandards[0][n][0][0],calStandards[1][n][0][0],calStandards[2][n][0][0]],0)
            et[n].ReflectCalibration([spDict['Short2'][n][0][0],spDict['Open2'][n][0][0],spDict['Load2'][n][0][0]],
                [calStandards[0][n][0][0],calStandards[1][n][0][0],calStandards[2][n][0][0]],1)
            et[n].InitializeExCalibration()
            et[n].ThruCalibration(spDict['Thru'][n][0][0],spDict['Thru'][n][1][0],calStandards[3][n],1,0)
            et[n].ThruCalibration(spDict['Thru'][n][1][1],spDict['Thru'][n][0][1],calStandards[3][n],0,1)
            DUT[n]=et[n].DutCalculation(spDict['Dut'][n])
            DUTAlt[n]=et[n].DutCalculationAlternate(spDict['Dut'][n])
        DUTCalcSp=si.sp.SParameters(f,DUT)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTCalcAlternateSp=si.sp.SParameters(f,DUTAlt)
        self.SParameterRegressionChecker(DUTCalcAlternateSp, self.NameForTest()+'Alternate_Calc.s2p')
        DUTActualSp=si.m.calkit.ThruStandard(f,offsetDelay=200e-12,offsetZ0=60.0)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')

    def testThruStandard(self):
        Fe=20e9
        N=200
        sp=si.m.calkit.ThruStandard([n*Fe/N for n in range(N+1)],offsetDelay=100e-12,offsetZ0=60,offsetLoss=2.0e9)
        self.SParameterRegressionChecker(sp, self.NameForTest()+'.s2p')

    def testThruStandardCalcZc(self):
        calcZcSave=si.m.calkit.std.Offset.calcZc
        try:
            si.m.calkit.std.Offset.calcZc=True
            Fe=20e9
            N=200
            sp=si.m.calkit.ThruStandard([n*Fe/N for n in range(N+1)],offsetDelay=100e-12,offsetZ0=60,offsetLoss=2.0e9)
            self.SParameterRegressionChecker(sp, self.NameForTest()+'.s2p')
        finally:
            si.m.calkit.std.Offset.calcZc=calcZcSave

    def testTDRSimulationSOLT2(self):
        result = self.GetSimulationResultsCheck('TDRSimulationSOLTVOnlyUnbalanced.si')
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]

        tdrWaveforms=dict(zip(outputNames,outputWaveforms))

        spDict=dict()

        wf=tdrWaveforms['VThru11']
        incwf11=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc11=incwf11.FrequencyContent()
        refwf11=wf-incwf11
        refwffc11=refwf11.FrequencyContent()

        wf=tdrWaveforms['VThru22']
        incwf22=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc22=incwf22.FrequencyContent()
        refwf22=wf-incwf22
        refwffc22=refwf22.FrequencyContent()

        wf=tdrWaveforms['VThru21']
        incwf21=incwf11
        incwffc21=incwf21.FrequencyContent()
        refwf21=wf
        refwffc21=refwf21.FrequencyContent()

        wf=tdrWaveforms['VThru12']
        incwf12=incwf22
        incwffc12=incwf12.FrequencyContent()
        refwf12=wf
        refwffc12=refwf12.FrequencyContent()

        f=incwffc11.FrequencyList()
        spDict['Thru']=si.sp.SParameters(f,[[[refwffc11[n]/incwffc11[n],refwffc12[n]/incwffc12[n]],
                                             [refwffc21[n]/incwffc21[n],refwffc22[n]/incwffc22[n]]]
                                            for n in range(len(f))])

        wf=tdrWaveforms['VEx11']
        incwf11=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc11=incwf11.FrequencyContent()
        refwf11=wf-incwf11
        refwffc11=refwf11.FrequencyContent()

        wf=tdrWaveforms['VEx22']
        incwf22=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc22=incwf22.FrequencyContent()
        refwf22=wf-incwf22
        refwffc22=refwf22.FrequencyContent()

        wf=tdrWaveforms['VEx21']
        incwf21=incwf11
        incwffc21=incwf21.FrequencyContent()
        refwf21=wf
        refwffc21=refwf21.FrequencyContent()

        wf=tdrWaveforms['VEx12']
        incwf12=incwf22
        incwffc12=incwf12.FrequencyContent()
        refwf12=wf
        refwffc12=refwf12.FrequencyContent()

        f=incwffc11.FrequencyList()
        spDict['Ex']=si.sp.SParameters(f,[[[refwffc11[n]/incwffc11[n],refwffc12[n]/incwffc12[n]],
                                             [refwffc21[n]/incwffc21[n],refwffc22[n]/incwffc22[n]]]
                                            for n in range(len(f))])

        wf=tdrWaveforms['VDut11']
        incwf11=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc11=incwf11.FrequencyContent()
        refwf11=wf-incwf11
        refwffc11=refwf11.FrequencyContent()

        wf=tdrWaveforms['VDut22']
        incwf22=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc22=incwf22.FrequencyContent()
        refwf22=wf-incwf22
        refwffc22=refwf22.FrequencyContent()

        wf=tdrWaveforms['VDut21']
        incwf21=incwf11
        incwffc21=incwf21.FrequencyContent()
        refwf21=wf
        refwffc21=refwf21.FrequencyContent()

        wf=tdrWaveforms['VDut12']
        incwf12=incwf22
        incwffc12=incwf12.FrequencyContent()
        refwf12=wf
        refwffc12=refwf12.FrequencyContent()

        f=incwffc11.FrequencyList()
        spDict['Dut']=si.sp.SParameters(f,[[[refwffc11[n]/incwffc11[n],refwffc12[n]/incwffc12[n]],
                                             [refwffc21[n]/incwffc21[n],refwffc22[n]/incwffc22[n]]]
                                            for n in range(len(f))])

        wf=tdrWaveforms['VShort1']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Short1']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VOpen1']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Open1']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VLoad1']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Load1']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VShort2']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Short2']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VOpen2']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Open2']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VLoad2']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Load2']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        f=spDict['Dut'].f()
        calStandards=[si.m.calkit.std.ShortStandard(f),
                      si.m.calkit.OpenStandard(f),
                      si.m.calkit.LoadStandard(f),
                      si.m.calkit.ThruStandard(f,100e-12)]
        et=[si.m.cal.ErrorTerms().Initialize(2) for _ in range(len(f))]
        DUT=[[[0.,0.],[0.,0.]] for _ in range(len(f))]
        for n in range(len(et)):
            et[n].ReflectCalibration([spDict['Short1'][n][0][0],spDict['Open1'][n][0][0],spDict['Load1'][n][0][0]],
                [calStandards[0][n][0][0],calStandards[1][n][0][0],calStandards[2][n][0][0]],0)
            et[n].ReflectCalibration([spDict['Short2'][n][0][0],spDict['Open2'][n][0][0],spDict['Load2'][n][0][0]],
                [calStandards[0][n][0][0],calStandards[1][n][0][0],calStandards[2][n][0][0]],1)
            et[n].ExCalibration(spDict['Ex'][n][1][0],1,0)
            et[n].ExCalibration(spDict['Ex'][n][0][1],0,1)
            et[n].ThruCalibration(spDict['Thru'][n][0][0],spDict['Thru'][n][1][0],calStandards[3][n],1,0)
            et[n].ThruCalibration(spDict['Thru'][n][1][1],spDict['Thru'][n][0][1],calStandards[3][n],0,1)
            DUT[n]=et[n].DutCalculation(spDict['Dut'][n])
        et=[si.m.cal.ErrorTerms(et[n].ET) for n in range(len(f))] # just to make a copy to satisfy coverage
        DUTCalcSp=si.sp.SParameters(f,DUT)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.SParameterFile('BMYchebySParameters.s2p').Resample(DUTCalcSp.f())
        DUTActualSp=si.m.calkit.ThruStandard(f,100e-12)
        DUTActualSp=si.m.calkit.ThruStandard(f,offsetDelay=200e-12,offsetZ0=60.0)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')


    def testTDRSimulationSOLTTwoPortEQ(self):
        result = self.GetSimulationResultsCheck('TDRSimulationSOLTVOnlyUnbalanced.si')
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]

        tdrWaveforms=dict(zip(outputNames,outputWaveforms))

        spDict=dict()

        wf=tdrWaveforms['VThru11']
        incwf11=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc11=incwf11.FrequencyContent()
        refwf11=wf-incwf11
        refwffc11=refwf11.FrequencyContent()

        wf=tdrWaveforms['VThru22']
        incwf22=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc22=incwf22.FrequencyContent()
        refwf22=wf-incwf22
        refwffc22=refwf22.FrequencyContent()

        wf=tdrWaveforms['VThru21']
        incwf21=incwf11
        incwffc21=incwf21.FrequencyContent()
        refwf21=wf
        refwffc21=refwf21.FrequencyContent()

        wf=tdrWaveforms['VThru12']
        incwf12=incwf22
        incwffc12=incwf12.FrequencyContent()
        refwf12=wf
        refwffc12=refwf12.FrequencyContent()

        f=incwffc11.FrequencyList()
        spDict['Thru']=si.sp.SParameters(f,[[[refwffc11[n]/incwffc11[n],refwffc12[n]/incwffc12[n]],
                                             [refwffc21[n]/incwffc21[n],refwffc22[n]/incwffc22[n]]]
                                            for n in range(len(f))])

        wf=tdrWaveforms['VEx11']
        incwf11=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc11=incwf11.FrequencyContent()
        refwf11=wf-incwf11
        refwffc11=refwf11.FrequencyContent()

        wf=tdrWaveforms['VEx22']
        incwf22=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc22=incwf22.FrequencyContent()
        refwf22=wf-incwf22
        refwffc22=refwf22.FrequencyContent()

        wf=tdrWaveforms['VEx21']
        incwf21=incwf11
        incwffc21=incwf21.FrequencyContent()
        refwf21=wf
        refwffc21=refwf21.FrequencyContent()

        wf=tdrWaveforms['VEx12']
        incwf12=incwf22
        incwffc12=incwf12.FrequencyContent()
        refwf12=wf
        refwffc12=refwf12.FrequencyContent()

        f=incwffc11.FrequencyList()
        spDict['Ex']=si.sp.SParameters(f,[[[refwffc11[n]/incwffc11[n],refwffc12[n]/incwffc12[n]],
                                             [refwffc21[n]/incwffc21[n],refwffc22[n]/incwffc22[n]]]
                                            for n in range(len(f))])

        wf=tdrWaveforms['VDut11']
        incwf11=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc11=incwf11.FrequencyContent()
        refwf11=wf-incwf11
        refwffc11=refwf11.FrequencyContent()

        wf=tdrWaveforms['VDut22']
        incwf22=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<10e-12 else 0. for (t,v) in zip(wf.Times(),wf.Values())])
        incwffc22=incwf22.FrequencyContent()
        refwf22=wf-incwf22
        refwffc22=refwf22.FrequencyContent()

        wf=tdrWaveforms['VDut21']
        incwf21=incwf11
        incwffc21=incwf21.FrequencyContent()
        refwf21=wf
        refwffc21=refwf21.FrequencyContent()

        wf=tdrWaveforms['VDut12']
        incwf12=incwf22
        incwffc12=incwf12.FrequencyContent()
        refwf12=wf
        refwffc12=refwf12.FrequencyContent()

        f=incwffc11.FrequencyList()
        spDict['Dut']=si.sp.SParameters(f,[[[refwffc11[n]/incwffc11[n],refwffc12[n]/incwffc12[n]],
                                             [refwffc21[n]/incwffc21[n],refwffc22[n]/incwffc22[n]]]
                                            for n in range(len(f))])

        wf=tdrWaveforms['VShort1']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Short1']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VOpen1']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Open1']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VLoad1']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Load1']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VShort2']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Short2']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VOpen2']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Open2']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        wf=tdrWaveforms['VLoad2']
        refwf=si.td.wf.Waveform(wf.TimeDescriptor(),[0 if abs(t)<10e-12 else v for (t,v) in zip(wf.Times(),wf.Values())])
        incwf=wf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spDict['Load2']=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        f=spDict['Dut'].f()
        calStandards=[si.m.calkit.std.ShortStandard(f),
                      si.m.calkit.OpenStandard(f),
                      si.m.calkit.LoadStandard(f),
                      si.m.calkit.ThruStandard(f,100e-12)]
        et=[si.m.cal.ErrorTerms().Initialize(2) for _ in range(len(f))]
        for n in range(len(et)):
            et[n].ReflectCalibration([spDict['Short1'][n][0][0],spDict['Open1'][n][0][0],spDict['Load1'][n][0][0]],
                [calStandards[0][n][0][0],calStandards[1][n][0][0],calStandards[2][n][0][0]],0)
            et[n].ReflectCalibration([spDict['Short2'][n][0][0],spDict['Open2'][n][0][0],spDict['Load2'][n][0][0]],
                [calStandards[0][n][0][0],calStandards[1][n][0][0],calStandards[2][n][0][0]],1)
            et[n].ExCalibration(spDict['Ex'][n][1][0],1,0)
            et[n].ExCalibration(spDict['Ex'][n][0][1],0,1)
            et[n].ThruCalibration(spDict['Thru'][n][0][0],spDict['Thru'][n][1][0],calStandards[3][n],1,0)
            et[n].ThruCalibration(spDict['Thru'][n][1][1],spDict['Thru'][n][0][1],calStandards[3][n],0,1)

        ED1=[et[n].ET[0][0][0] for n in range(len(et))]
        ER1=[et[n].ET[0][0][1] for n in range(len(et))]
        ES1=[et[n].ET[0][0][2] for n in range(len(et))]
        ED2=[et[n].ET[1][1][0] for n in range(len(et))]
        ER2=[et[n].ET[1][1][1] for n in range(len(et))]
        ES2=[et[n].ET[1][1][2] for n in range(len(et))]
        EX12=[et[n].ET[0][1][0] for n in range(len(et))]
        ET12=[et[n].ET[0][1][1] for n in range(len(et))]
        EL12=[et[n].ET[0][1][2] for n in range(len(et))]
        EX21=[et[n].ET[1][0][0] for n in range(len(et))]
        ET21=[et[n].ET[1][0][1] for n in range(len(et))]
        EL21=[et[n].ET[1][0][2] for n in range(len(et))]

        from numpy import array,identity

        DUT=[(array([[(spDict['Dut'][n][0][0]-ED1[n])/ER1[n],(spDict['Dut'][n][0][1]-EX12[n])/ET12[n]],
                       [(spDict['Dut'][n][1][0]-EX21[n])/ET21[n],(spDict['Dut'][n][1][1]-ED2[n])/ER2[n]]]).dot(
            inv(identity(2)+array([[(spDict['Dut'][n][0][0]-ED1[n])*ES1[n]/ER1[n],(spDict['Dut'][n][0][1]-EX12[n])*EL12[n]/ET12[n]],
                                 [(spDict['Dut'][n][1][0]-EX21[n])*EL21[n]/ET21[n],(spDict['Dut'][n][1][1]-ED2[n])*ES2[n]/ER2[n]]])))).tolist()
                for n in range(len(et))]

        DUTCalcSp=si.sp.SParameters(f,DUT)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.SParameterFile('BMYchebySParameters.s2p').Resample(DUTCalcSp.f())
        DUTActualSp=si.m.calkit.ThruStandard(f,100e-12)
        DUTActualSp=si.m.calkit.ThruStandard(f,offsetDelay=200e-12,offsetZ0=60.0)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')

    def testCalkitWrite(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        calkit = si.m.calkit.CalibrationKit()
        calkit.WriteToFile('default.cstd')

        # cal constants for an Agilent 85052D 3.5mm cal kit
        calkit.Constants.openC0=49.43e-15            # % C0 (fF) - OPEN
        calkit.Constants.openC1=-310.13e-27          # % C1 (1e-27 F/Hz) - OPEN
        calkit.Constants.openC2=23.1682e-36          # % C2 (1e-36 F/Hz^2) - OPEN
        calkit.Constants.openC3=0.15966e-45          # % C3 (1e-45 F/Hz^3) - OPEN
        calkit.Constants.openOffsetDelay=29.243e-12  # % offset delay (pS) - OPEN
        calkit.Constants.openOffsetZ0=50.            # % real(Zo) of offset length - OPEN
        calkit.Constants.openOffsetLoss=2.2e9        # % offset loss (Gohm/s) - OPEN
        calkit.Constants.shortL0=2.0765e-12          # % L0 (pH) - SHORT
        calkit.Constants.shortL1=-108.54e-24         # % L1 (1e-24 H/Hz) - SHORT
        calkit.Constants.shortL2=2.1705e-33          # % L2 (1e-33 H/Hz^2) - SHORT
        calkit.Constants.shortL3=-0.1001e-42         # % L3 (1e-42 H/Hz^3) - SHORT
        calkit.Constants.shortOffsetDelay=31.785e-12 # % offset delay (pS) - SHORT
        calkit.Constants.shortOffsetZ0=50.           # % real(Zo) of offset length - SHORT
        calkit.Constants.shortOffsetLoss=2.36e9      # % offset loss (Gohm/s) - SHORT
        calkit.Constants.loadZ=50.                   # % load resistance (ohm) - LOAD
        calkit.Constants.loadOffsetDelay=0.          # % offset delay (pS) - LOAD
        calkit.Constants.loadOffsetZ0=50.            # % real(Zo) of offset length - LOAD
        calkit.Constants.loadOffsetLoss=0.           # % offset loss (Gohm/s) - LOAD
        calkit.Constants.thruOffsetDelay=94.75e-12   # % offset delay (pS) - THRU
        calkit.Constants.thruOffsetZ0=50.            # % real(Zo) of offset length - THRU
        calkit.Constants.thruOffsetLoss=2.52e9       # % offset loss (Gohm/s) - THRU

        calkit.WriteToFile('Agilent85052D.cstd', 'Agilent 85052D 3.5mm cal kit')

        calkit = si.m.calkit.CalibrationKit('Agilent85052D.cstd',si.fd.EvenlySpacedFrequencyList(20e9,200))

        stdPrefix='Agilent85052D_200_20GHz_'
        calkit.WriteStandardsToFiles(stdPrefix)
        calkit.ReadStandardsFromFiles(stdPrefix)
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.remove(stdPrefix+'Short.s1p')
        os.remove(stdPrefix+'Open.s1p')
        os.remove(stdPrefix+'Load.s1p')
        os.remove(stdPrefix+'Thru.s2p')
        self.SParameterRegressionChecker(calkit.shortStandard, self.NameForTest()+'_ShortStandard.s1p')
        self.SParameterRegressionChecker(calkit.openStandard, self.NameForTest()+'_OpenStandard.s1p')
        self.SParameterRegressionChecker(calkit.loadStandard, self.NameForTest()+'_LoadStandard.s1p')
        self.SParameterRegressionChecker(calkit.thruStandard, self.NameForTest()+'_ThruStandard.s2p')

    def testVNASimulationSOLT(self):
        result = self.GetSimulationResultsCheck('TDRSimulationSOLTUnbalanced.si')
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]

        fr=transferMatrices.FrequencyResponses()

        spDict=dict()

        AShort1=fr[outputNames.index('AShort1')][sourceNames.index('VGLeft')]
        BShort1=fr[outputNames.index('BShort1')][sourceNames.index('VGLeft')]
        f=AShort1.Frequencies()
        spDict['Short1']=si.sp.SParameters(f,[[[BShort1[n]/AShort1[n]]] for n in range(len(f))])

        AShort2=fr[outputNames.index('AShort2')][sourceNames.index('VGRight')]
        BShort2=fr[outputNames.index('BShort2')][sourceNames.index('VGRight')]
        spDict['Short2']=si.sp.SParameters(f,[[[BShort2[n]/AShort2[n]]] for n in range(len(f))])

        AOpen1=fr[outputNames.index('AOpen1')][sourceNames.index('VGLeft')]
        BOpen1=fr[outputNames.index('BOpen1')][sourceNames.index('VGLeft')]
        f=AOpen1.Frequencies()
        spDict['Open1']=si.sp.SParameters(f,[[[BOpen1[n]/AOpen1[n]]] for n in range(len(f))])

        AOpen2=fr[outputNames.index('AOpen2')][sourceNames.index('VGRight')]
        BOpen2=fr[outputNames.index('BOpen2')][sourceNames.index('VGRight')]
        spDict['Open2']=si.sp.SParameters(f,[[[BOpen2[n]/AOpen2[n]]] for n in range(len(f))])

        ALoad1=fr[outputNames.index('ALoad1')][sourceNames.index('VGLeft')]
        BLoad1=fr[outputNames.index('BLoad1')][sourceNames.index('VGLeft')]
        f=ALoad1.Frequencies()
        spDict['Load1']=si.sp.SParameters(f,[[[BLoad1[n]/ALoad1[n]]] for n in range(len(f))])

        ALoad2=fr[outputNames.index('ALoad2')][sourceNames.index('VGRight')]
        BLoad2=fr[outputNames.index('BLoad2')][sourceNames.index('VGRight')]
        spDict['Load2']=si.sp.SParameters(f,[[[BLoad2[n]/ALoad2[n]]] for n in range(len(f))])

        AThru11=fr[outputNames.index('AThru11')][sourceNames.index('VGLeft')]
        AThru21=fr[outputNames.index('AThru21')][sourceNames.index('VGLeft')]
        AThru12=fr[outputNames.index('AThru12')][sourceNames.index('VGRight')]
        AThru22=fr[outputNames.index('AThru22')][sourceNames.index('VGRight')]
        BThru11=fr[outputNames.index('BThru11')][sourceNames.index('VGLeft')]
        BThru21=fr[outputNames.index('BThru21')][sourceNames.index('VGLeft')]
        BThru12=fr[outputNames.index('BThru12')][sourceNames.index('VGRight')]
        BThru22=fr[outputNames.index('BThru22')][sourceNames.index('VGRight')]
        spDict['Thru']=si.sp.SParameters(f,[(array([[BThru11[n],BThru12[n]],[BThru21[n],BThru22[n]]]).dot(
                                            inv(array([[AThru11[n],AThru12[n]],[AThru21[n],AThru22[n]]])))).tolist()
                                            for n in range(len(f))])

        ADut11=fr[outputNames.index('ADut11')][sourceNames.index('VGLeft')]
        ADut21=fr[outputNames.index('ADut21')][sourceNames.index('VGLeft')]
        ADut12=fr[outputNames.index('ADut12')][sourceNames.index('VGRight')]
        ADut22=fr[outputNames.index('ADut22')][sourceNames.index('VGRight')]
        BDut11=fr[outputNames.index('BDut11')][sourceNames.index('VGLeft')]
        BDut21=fr[outputNames.index('BDut21')][sourceNames.index('VGLeft')]
        BDut12=fr[outputNames.index('BDut12')][sourceNames.index('VGRight')]
        BDut22=fr[outputNames.index('BDut22')][sourceNames.index('VGRight')]
        spDict['Dut']=si.sp.SParameters(f,[(array([[BDut11[n],BDut12[n]],[BDut21[n],BDut22[n]]]).dot(
                                            inv(array([[ADut11[n],ADut12[n]],[ADut21[n],ADut22[n]]])))).tolist()
                                            for n in range(len(f))])

        AEx11=fr[outputNames.index('AEx11')][sourceNames.index('VGLeft')]
        AEx21=fr[outputNames.index('AEx21')][sourceNames.index('VGLeft')]
        AEx12=fr[outputNames.index('AEx12')][sourceNames.index('VGRight')]
        AEx22=fr[outputNames.index('AEx22')][sourceNames.index('VGRight')]
        BEx11=fr[outputNames.index('BEx11')][sourceNames.index('VGLeft')]
        BEx21=fr[outputNames.index('BEx21')][sourceNames.index('VGLeft')]
        BEx12=fr[outputNames.index('BEx12')][sourceNames.index('VGRight')]
        BEx22=fr[outputNames.index('BEx22')][sourceNames.index('VGRight')]
        spDict['Ex']=si.sp.SParameters(f,[(array([[BEx11[n],BEx12[n]],[BEx21[n],BEx22[n]]]).dot(
                                            inv(array([[AEx11[n],AEx12[n]],[AEx21[n],AEx22[n]]])))).tolist()
                                            for n in range(len(f))])

        f=spDict['Dut'].f()
        calStandards=[si.m.calkit.std.ShortStandard(f),
                      si.m.calkit.OpenStandard(f),
                      si.m.calkit.LoadStandard(f),
                      si.m.calkit.ThruStandard(f,100e-12)]
        et=[si.m.cal.ErrorTerms().Initialize(2) for _ in range(len(f))]
        DUT=[[[0.,0.],[0.,0.]] for _ in range(len(f))]
        for n in range(len(et)):
            et[n].ReflectCalibration([spDict['Short1'][n][0][0],spDict['Open1'][n][0][0],spDict['Load1'][n][0][0]],
                [calStandards[0][n][0][0],calStandards[1][n][0][0],calStandards[2][n][0][0]],0)
            et[n].ReflectCalibration([spDict['Short2'][n][0][0],spDict['Open2'][n][0][0],spDict['Load2'][n][0][0]],
                [calStandards[0][n][0][0],calStandards[1][n][0][0],calStandards[2][n][0][0]],1)
            et[n].ExCalibration(spDict['Ex'][n][1][0],1,0)
            et[n].ExCalibration(spDict['Ex'][n][0][1],0,1)
            et[n].ThruCalibration(spDict['Thru'][n][0][0],spDict['Thru'][n][1][0],calStandards[3][n],1,0)
            et[n].ThruCalibration(spDict['Thru'][n][1][1],spDict['Thru'][n][0][1],calStandards[3][n],0,1)
            DUT[n]=et[n].DutCalculation(spDict['Dut'][n])
        et=[si.m.cal.ErrorTerms(et[n].ET) for n in range(len(f))] # just to make a copy to satisfy coverage
        DUTCalcSp=si.sp.SParameters(f,DUT)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.SParameterFile('BMYchebySParameters.s2p').Resample(DUTCalcSp.f())
        DUTActualSp=si.m.calkit.ThruStandard(f,100e-12)
        DUTActualSp=si.m.calkit.ThruStandard(f,offsetDelay=200e-12,offsetZ0=60.0)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')

    def testVNASimulationSOLT2(self):
        result = self.GetSimulationResultsCheck('TDRSimulationSOLTUnbalanced.si')
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]

        fr=transferMatrices.FrequencyResponses()

        spDict=dict()

        AShort1=fr[outputNames.index('AShort1')][sourceNames.index('VGLeft')]
        BShort1=fr[outputNames.index('BShort1')][sourceNames.index('VGLeft')]
        f=AShort1.Frequencies()
        spDict['Short1']=si.sp.SParameters(f,[[[BShort1[n]/AShort1[n]]] for n in range(len(f))])

        AShort2=fr[outputNames.index('AShort2')][sourceNames.index('VGRight')]
        BShort2=fr[outputNames.index('BShort2')][sourceNames.index('VGRight')]
        spDict['Short2']=si.sp.SParameters(f,[[[BShort2[n]/AShort2[n]]] for n in range(len(f))])

        AOpen1=fr[outputNames.index('AOpen1')][sourceNames.index('VGLeft')]
        BOpen1=fr[outputNames.index('BOpen1')][sourceNames.index('VGLeft')]
        f=AOpen1.Frequencies()
        spDict['Open1']=si.sp.SParameters(f,[[[BOpen1[n]/AOpen1[n]]] for n in range(len(f))])

        AOpen2=fr[outputNames.index('AOpen2')][sourceNames.index('VGRight')]
        BOpen2=fr[outputNames.index('BOpen2')][sourceNames.index('VGRight')]
        spDict['Open2']=si.sp.SParameters(f,[[[BOpen2[n]/AOpen2[n]]] for n in range(len(f))])

        ALoad1=fr[outputNames.index('ALoad1')][sourceNames.index('VGLeft')]
        BLoad1=fr[outputNames.index('BLoad1')][sourceNames.index('VGLeft')]
        f=ALoad1.Frequencies()
        spDict['Load1']=si.sp.SParameters(f,[[[BLoad1[n]/ALoad1[n]]] for n in range(len(f))])

        ALoad2=fr[outputNames.index('ALoad2')][sourceNames.index('VGRight')]
        BLoad2=fr[outputNames.index('BLoad2')][sourceNames.index('VGRight')]
        spDict['Load2']=si.sp.SParameters(f,[[[BLoad2[n]/ALoad2[n]]] for n in range(len(f))])

        AThru11=fr[outputNames.index('AThru11')][sourceNames.index('VGLeft')]
        AThru21=fr[outputNames.index('AThru21')][sourceNames.index('VGLeft')]
        AThru12=fr[outputNames.index('AThru12')][sourceNames.index('VGRight')]
        AThru22=fr[outputNames.index('AThru22')][sourceNames.index('VGRight')]
        BThru11=fr[outputNames.index('BThru11')][sourceNames.index('VGLeft')]
        BThru21=fr[outputNames.index('BThru21')][sourceNames.index('VGLeft')]
        BThru12=fr[outputNames.index('BThru12')][sourceNames.index('VGRight')]
        BThru22=fr[outputNames.index('BThru22')][sourceNames.index('VGRight')]
        spDict['Thru']=si.sp.SParameters(f,[(array([[BThru11[n],BThru12[n]],[BThru21[n],BThru22[n]]]).dot(
                                            inv(array([[AThru11[n],AThru12[n]],[AThru21[n],AThru22[n]]])))).tolist()
                                            for n in range(len(f))])

        ADut11=fr[outputNames.index('ADut11')][sourceNames.index('VGLeft')]
        ADut21=fr[outputNames.index('ADut21')][sourceNames.index('VGLeft')]
        ADut12=fr[outputNames.index('ADut12')][sourceNames.index('VGRight')]
        ADut22=fr[outputNames.index('ADut22')][sourceNames.index('VGRight')]
        BDut11=fr[outputNames.index('BDut11')][sourceNames.index('VGLeft')]
        BDut21=fr[outputNames.index('BDut21')][sourceNames.index('VGLeft')]
        BDut12=fr[outputNames.index('BDut12')][sourceNames.index('VGRight')]
        BDut22=fr[outputNames.index('BDut22')][sourceNames.index('VGRight')]
        spDict['Dut']=si.sp.SParameters(f,[(array([[BDut11[n],BDut12[n]],[BDut21[n],BDut22[n]]]).dot(
                                            inv(array([[ADut11[n],ADut12[n]],[ADut21[n],ADut22[n]]])))).tolist()
                                            for n in range(len(f))])

        AEx11=fr[outputNames.index('AEx11')][sourceNames.index('VGLeft')]
        AEx21=fr[outputNames.index('AEx21')][sourceNames.index('VGLeft')]
        AEx12=fr[outputNames.index('AEx12')][sourceNames.index('VGRight')]
        AEx22=fr[outputNames.index('AEx22')][sourceNames.index('VGRight')]
        BEx11=fr[outputNames.index('BEx11')][sourceNames.index('VGLeft')]
        BEx21=fr[outputNames.index('BEx21')][sourceNames.index('VGLeft')]
        BEx12=fr[outputNames.index('BEx12')][sourceNames.index('VGRight')]
        BEx22=fr[outputNames.index('BEx22')][sourceNames.index('VGRight')]
        spDict['Ex']=si.sp.SParameters(f,[(array([[BEx11[n],BEx12[n]],[BEx21[n],BEx22[n]]]).dot(
                                            inv(array([[AEx11[n],AEx12[n]],[AEx21[n],AEx22[n]]])))).tolist()
                                            for n in range(len(f))])

        f=spDict['Dut'].f()

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru'].FrequencyResponse(1,1),spDict['Thru'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru1'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru'].FrequencyResponse(2,2),spDict['Thru'].FrequencyResponse(1,2),calStandards[3],1,0,'Thru2'),
            si.m.cal.XtalkCalibrationMeasurement(spDict['Ex'].FrequencyResponse(2,1),0,1,'Ex1'),
            si.m.cal.XtalkCalibrationMeasurement(spDict['Ex'].FrequencyResponse(1,2),1,0,'Ex2')
            ]

        cm=si.m.cal.Calibration(2,f,ml)

        DUTCalcSp=cm.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.m.calkit.ThruStandard(f,offsetDelay=200e-12,offsetZ0=60.0)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')
if __name__ == "__main__":
    unittest.main()
