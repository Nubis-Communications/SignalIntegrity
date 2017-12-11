import unittest
import SignalIntegrity as si
from TestHelpers import SParameterCompareHelper
import os

from SignalIntegrity.Test import PySIAppTestHelper
import matplotlib.pyplot as plt
from TestHelpers import RoutineWriterTesterHelper

class TestSPARQSolt(unittest.TestCase,SParameterCompareHelper,PySIAppTestHelper,RoutineWriterTesterHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    def __init__(self, methodName='runTest'):
        SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        PySIAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        RoutineWriterTesterHelper.__init__(self)
    def testSPARQSOLPerfectButWithLength(self):
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

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 5e9']).TransferMatrices())
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
            Gamma[n]=[[et[n].DutCalculation(spRawDUT[n])]]
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 1e-6),'s-parameters not equal')

    def testSPARQSOLImPerfectButWithLength(self):
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

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 5e9']).TransferMatrices())
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
            Gamma[n]=[[et[n].DutCalculation(spRawDUT[n])]]
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

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 5e9']).TransferMatrices())
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
            Gamma[n]=[[et[n].DutCalculation(spRawDUT[n])]]
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 1e-6),'s-parameters not equal')
        return
        
        
        cl=[si.m.cal.ReflectCalibrationMeasurement(spRawShort,si.m.calkit.std.ShortStandard(f),1,'s'),
            si.m.cal.ReflectCalibrationMeasurement(spRawOpen,si.m.calkit.std.OpenStandard(f),1,'o'),
            si.m.cal.ReflectCalibrationMeasurement(spRawLoad,si.m.calkit.std.LoadStandard(f),1,'l')]
        cm=si.m.cal.CalibrationMeasurements(1,cl)

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

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 5e9']).TransferMatrices())
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
            Gamma[n]=[[et[n].DutCalculation(spRawDUT[n])]]
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 1e-6),'s-parameters not equal')
        return

        cl=[si.m.cal.ReflectCalibrationMeasurement(spRawShort,si.m.calkit.std.ShortStandard(f),1,'s'),
            si.m.cal.ReflectCalibrationMeasurement(spRawOpen,si.m.calkit.std.OpenStandard(f),1,'o'),
            si.m.cal.ReflectCalibrationMeasurement(spRawLoad,si.m.calkit.std.LoadStandard(f),1,'l')]
        cm=si.m.cal.CalibrationMeasurements(1,cl)

        et=cm.ErrorTerms()

    def testSPARQSOLClosedForm(self):
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
        self.assertTrue(self.SParametersAreEqual(sp, regression,1e-3),spfilename + ' incorrect')
        os.chdir(currentDirectory)
    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])
    def testSPARQSOLPerfectButWithLengthDelay(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        f=si.fd.EvenlySpacedFrequencyList(500.e6,50)
        sp = si.p.SimulatorNumericParser(f)
        netListLines=['device R1 2 R 50.0',
                      'device T1 2 tline zc 50.0 td 5e-10',
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
        owf=tmp.ProcessWaveforms([iwf])[0]
        refwf=si.td.wf.Waveform(owf.TimeDescriptor(),[0 if abs(t)<1e-12 else v for (t,v) in zip(owf.Times(),owf.Values())])
        incwf=owf-refwf
        refwffc=refwf.FrequencyContent()
        incwffc=incwf.FrequencyContent()
        spRawShort=si.sp.SParameters(refwffc.FrequencyList(),[[[r/i]] for (r,i) in zip(refwffc.Values(),incwffc.Values())])

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 5e9']).TransferMatrices())
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
            Gamma[n]=[[et[n].DutCalculation(spRawDUT[n])]]
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 1e-6),'s-parameters not equal')

    def testSPARQSOLImPerfectButWithLengthDelay(self):
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
                      'device T2 2 tline zc 55.0 td 5e-10',
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

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 5e9']).TransferMatrices())
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
            Gamma[n]=[[et[n].DutCalculation(spRawDUT[n])]]
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

        tmp = si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(f).AddLines(netListLines+['device R2 1 R 5e9']).TransferMatrices())
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
            Gamma[n]=[[et[n].DutCalculation(spRawDUT[n])]]
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 1e-6),'s-parameters not equal')
        return
        
        
        cl=[si.m.cal.ReflectCalibrationMeasurement(spRawShort,si.m.calkit.std.ShortStandard(f),1,'s'),
            si.m.cal.ReflectCalibrationMeasurement(spRawOpen,si.m.calkit.std.OpenStandard(f),1,'o'),
            si.m.cal.ReflectCalibrationMeasurement(spRawLoad,si.m.calkit.std.LoadStandard(f),1,'l')]
        cm=si.m.cal.CalibrationMeasurements(1,cl)

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
            Gamma[n]=[[et[n].DutCalculation(spRawDUT[n])]]
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 5e-4),'s-parameters not equal')

    def testSPARQSOLImPerfectButWithLengthDelayCalStd(self):
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
                      'device T2 2 tline zc 55.0 td 5e-10',
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
        td=si.td.wf.TimeDescriptor(-50.5e-9,112,1e9)
        iwf=si.td.wf.PulseWaveform(td,Amplitude=1.,StartTime=-1e-9,PulseWidth=1e-9)
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
            Gamma[n]=[[et[n].DutCalculation(spRawDUT[n])]]
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSP=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSP, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSP, 1e-3),'s-parameters not equal')

    def testTDRSimulationSOL(self):
        result = self.SimulationResultsChecker('TDRSimulationSOL.xml')
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
            Gamma[n]=[[et[n].DutCalculation(spDict['Dut'][n])]]
        DUTCalcSp=si.sp.SParameters(f,Gamma)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        DUTActualSp=si.sp.SParameters(f,[si.dev.TerminationZ(20.0) for _ in f])
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s1p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')

    def testTDRSimulationSOLT(self):
        result = self.SimulationResultsChecker('TDRSimulationSOLTVOnly.xml')
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
        for n in range(len(et)):
            et[n].ReflectCalibration([spDict['Short1'][n][0][0],spDict['Open1'][n][0][0],spDict['Load1'][n][0][0]],
                [calStandards[0][n][0][0],calStandards[1][n][0][0],calStandards[2][n][0][0]],0)
            et[n].ReflectCalibration([spDict['Short2'][n][0][0],spDict['Open2'][n][0][0],spDict['Load2'][n][0][0]],
                [calStandards[0][n][0][0],calStandards[1][n][0][0],calStandards[2][n][0][0]],1)
            et[n].ThruCalibration(spDict['Thru'][n][0][0],spDict['Thru'][n][1][0],calStandards[3][n],1,0)
            et[n].ThruCalibration(spDict['Thru'][n][1][1],spDict['Thru'][n][0][1],calStandards[3][n],0,1)
            DUT[n]=et[n].DutCalculation(spDict['Dut'][n])
        DUTCalcSp=si.sp.SParameters(f,DUT)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.SParameterFile('BMYchebySParameters.s2p').Resample(DUTCalcSp.f())
        DUTActualSp=si.m.calkit.ThruStandard(f,100e-12)
        DUTActualSp=si.m.calkit.ThruStandard(f,offsetDelay=200e-12,offsetZ0=60.0)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')
    def testThruStandard(self):
        Fe=20e9
        N=200
        sp=si.m.calkit.ThruStandard([n*Fe/N for n in range(N+1)],offsetDelay=100e-12,offsetZ0=60,offsetLoss=2.0e9)
        self.SParameterRegressionChecker(sp, self.NameForTest()+'.s2p')
    def testWriteErrorTermsCode(self):
        fileName="../SignalIntegrity/Measurement/Calibration/ErrorTerms.py"
        className='ErrorTerms'
        defName=['ReflectCalibration','ThruCalibration','ExCalibration','DutCalculation','Fixture']
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
        #self.WriteCode('TestSystemDescription.py','testSystemDescriptionExampleBlock(self)',self.standardHeader)
    def testTDRSimulationSOLT2(self):
        result = self.SimulationResultsChecker('TDRSimulationSOLTVOnlyUnbalanced.xml')
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
        result = self.SimulationResultsChecker('TDRSimulationSOLTVOnlyUnbalanced.xml')
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
        
        from numpy import matrix,identity

        DUT=[(matrix([[(spDict['Dut'][n][0][0]-ED1[n])/ER1[n],(spDict['Dut'][n][0][1]-EX12[n])/ET12[n]],
                       [(spDict['Dut'][n][1][0]-EX21[n])/ET21[n],(spDict['Dut'][n][1][1]-ED2[n])/ER2[n]]])*\
            (identity(2)+matrix([[(spDict['Dut'][n][0][0]-ED1[n])*ES1[n]/ER1[n],(spDict['Dut'][n][0][1]-EX12[n])*EL12[n]/ET12[n]],
                                 [(spDict['Dut'][n][1][0]-EX21[n])*EL21[n]/ET21[n],(spDict['Dut'][n][1][1]-ED2[n])*ES2[n]/ER2[n]]])).getI()).tolist()
                for n in range(len(et))]

        DUTCalcSp=si.sp.SParameters(f,DUT)
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.SParameterFile('BMYchebySParameters.s2p').Resample(DUTCalcSp.f())
        DUTActualSp=si.m.calkit.ThruStandard(f,100e-12)
        DUTActualSp=si.m.calkit.ThruStandard(f,offsetDelay=200e-12,offsetZ0=60.0)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')

if __name__ == "__main__":
    unittest.main()
