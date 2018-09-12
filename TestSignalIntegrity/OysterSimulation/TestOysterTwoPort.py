import unittest
import SignalIntegrity as si
from TestSignalIntegrity.TestHelpers import SParameterCompareHelper,RoutineWriterTesterHelper
import os

from numpy import matrix,mean
import math
from SignalIntegrity.Measurement.TDR.TDRWaveformToSParameterConverter import TDRWaveformToSParameterConverter

#------------------------------------------------------------------------------ 
# this class tries to speed things up a bit using a pickle containing the simulation
# results from a simulation that is used for every test.  If the pickle 'simresults.p'
# exists, it will load this pickle as the complete set of simulation results - you must
# delete this pickle if you change any of the schematics and expect them to produce
# different results.  This pickle will get rewritten by one of the classes as the simulation
# results are produced only once by the first test to produce them so it doesn't really matter
# who writes the pickle.
# you must set usePickle to True for it to perform this caching.  It cuts the time from about
# 1 minute to about 20 seconds
#------------------------------------------------------------------------------ 
class TestOysterTest(unittest.TestCase,
        SParameterCompareHelper,si.test.PySIAppTestHelper,RoutineWriterTesterHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    epsilon=50e-12
    usePickle=False
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    def tearDown(self):
        si.m.tdr.TDRWaveformToSParameterConverter.taper=True
        si.wl.WaveletDenoiser.wavelet=si.wl.WaveletDaubechies16()
        si.td.wf.Waveform.adaptionStrategy='SinX'
    def __init__(self, methodName='runTest'):
        SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.PySIAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        RoutineWriterTesterHelper.__init__(self)
    def GetSimulationResultsCheck(self,filename):
        if not hasattr(TestOysterTest, 'simdict'):
            TestOysterTest.simdict=dict()
            if TestOysterTest.usePickle:
                try:
                    import pickle
                    TestOysterTest.simdict=pickle.load(open("simresults.p","rb"))
                except:
                    pass
        if filename in TestOysterTest.simdict:
            return TestOysterTest.simdict[filename]
        TestOysterTest.simdict[filename] = self.SimulationResultsChecker(filename)
        return TestOysterTest.simdict[filename]
    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])
    def NoisyWaveforms(self,wfList):
        return wfList # no noise for now
        sigma=707e-6/math.sqrt(10000)
        newwfList=[r+si.td.wf.NoiseWaveform(r.TimeDescriptor(),sigma) for r in wfList]
        return newwfList
    def ResampleSParameterFile(self,filename,ports):
        """This is no longer needed, but retained for reference on ways to resample s-parameters"""
        uf=si.fd.EvenlySpacedFrequencyList(400e9,40000)
        utd=uf.TimeDescriptor()
        sp=si.sp.SParameterFile(filename+'.s'+str(ports)+'p')
        si.td.wf.Waveform.adaptionStrategy='SinX'
        si.td.f.InterpolatorSinX.S=4
        si.td.f.FractionalDelayFilterSinX.S=4
        spufr=[[si.td.wf.ImpulseResponse((sp.FrequencyResponse(r+1,c+1).ImpulseResponse()*si.td.f.WaveformTrimmer(-5000,-5000)).Adapt(utd)*0.1).FrequencyResponse() for c in range(ports)] for r in range(ports)]
        usp=si.sp.SParameters(uf,[[[spufr[r][c][n] for c in range(ports)] for r in range(ports)] for n in range(len(uf))])
        si.td.wf.Waveform.adaptionStrategy='SinX'
        si.td.f.InterpolatorSinX.S=64
        si.td.f.FractionalDelayFilterSinX.S=64
        self.SParameterRegressionChecker(usp, filename+'_upsampled.s'+str(ports)+'p')
    def testAAAAUpsampleBaseSParameters(self):
        """These are no longer used as there is no need for upsampled fixture testing"""
        return
        self.ResampleSParameterFile('TeledyneRelayClosed', 2)
        self.ResampleSParameterFile('Short6', 1)
        self.ResampleSParameterFile('Open6', 1)
        self.ResampleSParameterFile('WeinschelLoad', 1)
        self.ResampleSParameterFile('SemiRigidCable1', 2)
        self.ResampleSParameterFile('SemiRigidCable2', 2)
        self.ResampleSParameterFile('ScientificPulserSamplerScopeWfOnWafer2', 2)
        self.ResampleSParameterFile('Cable1_resampled', 2)
        self.ResampleSParameterFile('Cable2_resampled', 2)
        self.ResampleSParameterFile('Diplexer', 3)
        self.ResampleSParameterFile('Adapter', 2)
    def testAAAOysterCalStandardSimulation(self):
        return
        ports=2
        f=si.fd.EvenlySpacedFrequencyList(40e9,8000)
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Step=False,Inverted=False,Length=50e-9,
            WindowRaisedCosineDuration=50e-12,
            WindowReverseHalfWidthTime=500e-12,
            WindowForwardHalfWidthTime=50e-12,Denoise=False,
            fd=f)

        si.td.wf.Waveform.adaptionStrategy='Linear'

        result = self.GetSimulationResultsCheck('OysterCalStandardSimulation.xml')
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]

        spDict['CalShort']=tdr.RawMeasuredSParameters(outputWaveforms[outputNames.index('Short')])
        spDict['CalOpen']=tdr.RawMeasuredSParameters(outputWaveforms[outputNames.index('Open')])
        spDict['CalLoad']=tdr.RawMeasuredSParameters(outputWaveforms[outputNames.index('Load')])
        spDict['CalThru']=tdr.RawMeasuredSParameters([[outputWaveforms[outputNames.index('Thru11')],outputWaveforms[outputNames.index('Thru21')]],
                                                   [outputWaveforms[outputNames.index('Thru12')],outputWaveforms[outputNames.index('Thru22')]]])

        self.SParameterRegressionChecker(spDict['CalShort'], 'CalShort.s1p')
        self.SParameterRegressionChecker(spDict['CalOpen'], 'CalOpen.s1p')
        self.SParameterRegressionChecker(spDict['CalLoad'], 'CalLoad.s1p')
        self.SParameterRegressionChecker(spDict['CalThru'], 'CalThru.s2p')
    def testOysterTwoPort(self):
        pass
        ports=2
        f=si.fd.EvenlySpacedFrequencyList(40e9,8000)
        reflectNames=['Short','Open','Load']
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Step=False,Inverted=False,Length=50e-9,
            WindowRaisedCosineDuration=50e-12,
            WindowReverseHalfWidthTime=800e-12,
            WindowForwardHalfWidthTime=500e-12,Denoise=False,
            fd=f)
        si.wl.WaveletDenoiser.wavelet=si.wl.WaveletDaubechies4()

        #sigma=1e-18
        si.td.wf.Waveform.adaptionStrategy='Linear'

        result = self.GetSimulationResultsCheck('OysterSimulationTwoPort.xml')
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=self.NoisyWaveforms(result[3])

        reflectName='Short'
        portName='1'
        baseName=reflectName+portName
        wf=outputWaveforms[outputNames.index(reflectName)]
        spDict[baseName]=tdr.RawMeasuredSParameters(wf)
        spDict[baseName+'_wf']=wf
        spDict[baseName+'_denoised']=tdr.denoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
        spDict[baseName+'_incidentResponse']=tdr.IncidentFrequencyContent
        spDict[baseName+'_reflectResponse']=tdr.ReflectFrequencyContent[0]
        spDict[baseName+'_IncidentExtractionWindow']=tdr.IncidentExtractionWindow
        spDict[baseName+'_ReflectExtractionWindow']=tdr.ReflectExtractionWindow
        spDict[baseName+'_denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]

        reflectName='Short'
        portName='2'
        baseName=reflectName+portName
        wf=outputWaveforms[outputNames.index(reflectName)]
        spDict[baseName]=tdr.RawMeasuredSParameters(wf)
        spDict[baseName+'_wf']=wf
        spDict[baseName+'_denoised']=tdr.denoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
        spDict[baseName+'_incidentResponse']=tdr.IncidentFrequencyContent
        spDict[baseName+'_reflectResponse']=tdr.ReflectFrequencyContent[0]
        spDict[baseName+'_IncidentExtractionWindow']=tdr.IncidentExtractionWindow
        spDict[baseName+'_ReflectExtractionWindow']=tdr.ReflectExtractionWindow
        spDict[baseName+'_denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]

        reflectName='Open'
        portName='1'
        baseName=reflectName+portName
        wf=outputWaveforms[outputNames.index(reflectName)]
        spDict[baseName]=tdr.RawMeasuredSParameters(wf)
        spDict[baseName+'_wf']=wf
        spDict[baseName+'_denoised']=tdr.denoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
        spDict[baseName+'_incidentResponse']=tdr.IncidentFrequencyContent
        spDict[baseName+'_reflectResponse']=tdr.ReflectFrequencyContent[0]
        spDict[baseName+'_IncidentExtractionWindow']=tdr.IncidentExtractionWindow
        spDict[baseName+'_ReflectExtractionWindow']=tdr.ReflectExtractionWindow
        spDict[baseName+'_denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]
        self.SParameterRegressionChecker(spDict[baseName], self.NameForTest()+'_'+baseName+'_RawSp.s1p')

        reflectName='Open'
        portName='2'
        baseName=reflectName+portName
        wf=outputWaveforms[outputNames.index(reflectName)]
        spDict[baseName]=tdr.RawMeasuredSParameters(wf)
        spDict[baseName+'_wf']=wf
        spDict[baseName+'_denoised']=tdr.denoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
        spDict[baseName+'_incidentResponse']=tdr.IncidentFrequencyContent
        spDict[baseName+'_reflectResponse']=tdr.ReflectFrequencyContent[0]
        spDict[baseName+'_IncidentExtractionWindow']=tdr.IncidentExtractionWindow
        spDict[baseName+'_ReflectExtractionWindow']=tdr.ReflectExtractionWindow
        spDict[baseName+'_denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]

        reflectName='Load'
        portName='1'
        baseName=reflectName+portName
        wf=outputWaveforms[outputNames.index(reflectName)]
        spDict[baseName]=tdr.RawMeasuredSParameters(wf)
        spDict[baseName+'_wf']=wf
        spDict[baseName+'_denoised']=tdr.denoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
        spDict[baseName+'_incidentResponse']=tdr.IncidentFrequencyContent
        spDict[baseName+'_reflectResponse']=tdr.ReflectFrequencyContent[0]
        spDict[baseName+'_IncidentExtractionWindow']=tdr.IncidentExtractionWindow
        spDict[baseName+'_ReflectExtractionWindow']=tdr.ReflectExtractionWindow
        spDict[baseName+'_denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]

        reflectName='Load'
        portName='2'
        baseName=reflectName+portName
        wf=outputWaveforms[outputNames.index(reflectName)]
        spDict[baseName]=tdr.RawMeasuredSParameters(wf)
        spDict[baseName+'_wf']=wf
        spDict[baseName+'_denoised']=tdr.denoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
        spDict[baseName+'_incidentResponse']=tdr.IncidentFrequencyContent
        spDict[baseName+'_reflectResponse']=tdr.ReflectFrequencyContent[0]
        spDict[baseName+'_IncidentExtractionWindow']=tdr.IncidentExtractionWindow
        spDict[baseName+'_ReflectExtractionWindow']=tdr.ReflectExtractionWindow
        spDict[baseName+'_denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]

        spDict['Thru']=tdr.RawMeasuredSParameters([[outputWaveforms[outputNames.index('Thru11')],outputWaveforms[outputNames.index('Thru21')]],
                                                   [outputWaveforms[outputNames.index('Thru12')],outputWaveforms[outputNames.index('Thru22')]]])
        spDict['DUT']=tdr.RawMeasuredSParameters([[outputWaveforms[outputNames.index('DUT11')],outputWaveforms[outputNames.index('DUT21')]],
                                                   [outputWaveforms[outputNames.index('DUT12')],outputWaveforms[outputNames.index('DUT22')]]])

        baseNames=['Short1','Open1','Load1']

        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        for reflectName in baseNames:
            wf=spDict[reflectName+'_wf']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
            wf=spDict[reflectName+'_denoised']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName+' denoised')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        #PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.title('derivatives')
        for reflectName in baseNames:
            wf=spDict[reflectName+'_wf'].Derivative(scale=False)
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
        xw=spDict[baseNames[0]+'_IncidentExtractionWindow']*0.06
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[baseNames[0]+'_ReflectExtractionWindow']*0.06
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('denoised derivatives')
        for reflectName in baseNames:
            wf=spDict[reflectName+'_denoisedDerivative']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
        xw=spDict[baseNames[0]+'_IncidentExtractionWindow']*0.35
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[baseNames[0]+'_ReflectExtractionWindow']*0.35
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        calStandards=[self.SParameterResultsChecker('OysterFixtureShort.xml')[0],
              self.SParameterResultsChecker('OysterFixtureOpen.xml')[0],
              self.SParameterResultsChecker('OysterFixtureLoad.xml')[0],
              self.SParameterResultsChecker('OysterFixtureThru.xml')[0]]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru'].FrequencyResponse(1,1),spDict['Thru'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru'].FrequencyResponse(2,2),spDict['Thru'].FrequencyResponse(1,2),calStandards[3].PortReorder([2,1]),1,0,'Thru122'),
            ]

        cm=si.m.cal.Calibration(ports,f,ml).CalculateErrorTerms()
        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],self.NameForTest()+'OysterFixtureFile'+str(p+1)+'.s'+str(ports*2)+'p')

        DUTRawCalcSp=cm.DutCalculation(spDict['DUT'])
        self.SParameterRegressionChecker(DUTRawCalcSp, self.NameForTest()+'_RawCalc.s2p')

        DUTCalcSp=self.DeembeddingResultsChecker('OysterFixtureDeembed.xml')[1][0]
        DUTActualSp=self.SParameterResultsChecker('OysterDut.xml')[0]
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-2)

        si.test.PySIAppTestHelper.plotErrors=False

        if True:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        #self.assertTrue(SpAreEqual,'s-parameters not equal')

        self.SParameterResultsChecker('OysterDeembeddingFixture.xml')[0]
        NewFixture1=self.SParameterResultsChecker('OysterErrorTermsDeembed1.xml')[0]
        NewFixture2=self.SParameterResultsChecker('OysterErrorTermsDeembed2.xml')[0]

        for n in range(len(cm)):
            S1=NewFixture1[n]
            S2=NewFixture2[n]
 
            S131=S1[2][0]
            ED1=S1[0][0]
            ER1=S1[0][2]
            EX21=S1[1][0]
            ET21=S1[1][3]
            ES1=S1[2][2]
            EL21=S1[3][3]
 
            S242=S2[3][1]
            EX12=S2[0][1]
            ET12=S2[0][2]
            ED2=S2[1][1]
            ER2=S2[1][3]
            EL12=S2[2][2]
            ES2=S2[3][3]

            ER1=ER1*S131
            ET21=ET21*S131

            ER2=ER2*S242
            ET12=ET12*S242

            cm.ET[n]=si.m.cal.ErrorTerms([[[ED1,ER1,ES1],[EX12,ET12,EL12]],
                      [[EX21,ET21,EL21],[ED2,ER2,ES2]]])
 
        FixtureNew=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(FixtureNew[p],self.NameForTest()+'OysterFixtureFileNew'+str(p+1)+'.s'+str(ports*2)+'p')
 
        DUTCalcNewSp=cm.DutCalculation(spDict['DUT'])
        self.SParameterRegressionChecker(DUTCalcNewSp, self.NameForTest()+'_NewCalc.s2p')
 
        SpAreEqual=self.SParametersAreEqual(DUTCalcNewSp, DUTActualSp,1e-2)
 
        si.test.PySIAppTestHelper.plotErrors=False
 
        if True:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcNewSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()
 
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcNewSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcNewSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()
 
        #self.assertTrue(SpAreEqual,'s-parameters not equal')

        self.SParameterResultsChecker('OysterDeembeddingFixture.xml')[0]
        self.SParameterResultsChecker('OysterErrorTermsDeembed1.xml')[0]
        self.SParameterResultsChecker('OysterErrorTermsDeembed2.xml')[0]

        short1=self.SParameterResultsChecker('OysterShort1')[0]
        short2=self.SParameterResultsChecker('OysterShort2')[0]
        open1=self.SParameterResultsChecker('OysterOpen1')[0]
        open2=self.SParameterResultsChecker('OysterOpen2')[0]
        load1=self.SParameterResultsChecker('OysterLoad1')[0]
        load2=self.SParameterResultsChecker('OysterLoad2')[0]
        thru1=self.SParameterResultsChecker('OysterThru1')[0]
        thru2=self.SParameterResultsChecker('OysterThru2')[0]

        calStandards=[si.m.calkit.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(short1.FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(short2.FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(open1.FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(open2.FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(load1.FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(load2.FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ThruCalibrationMeasurement(thru1.FrequencyResponse(1,1),thru1.FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(thru2.FrequencyResponse(2,2),thru2.FrequencyResponse(1,2),calStandards[3],1,0,'Thru122'),
            ]

        cmnewer=si.m.cal.Calibration(ports,f,ml).CalculateErrorTerms()
        FixtureNewer=cmnewer.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(FixtureNewer[p],self.NameForTest()+'OysterFixtureFileNewer'+str(p+1)+'.s'+str(ports*2)+'p')

        DUTCalcNewerSp=cmnewer.DutCalculation(spDict['DUT'])
        self.SParameterRegressionChecker(DUTCalcNewerSp, self.NameForTest()+'_NewerCalc.s2p')

        SpAreEqual=self.SParametersAreEqual(DUTCalcNewerSp, DUTActualSp,1e-2)

        si.test.PySIAppTestHelper.plotErrors=False

        if True:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcNewerSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcNewerSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcNewerSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(SpAreEqual,'s-parameters not equal')

    def testZOysterMonteCarlo(self):
        return
        ports=2
        f=si.fd.EvenlySpacedFrequencyList(40e9,8000)
        reflectNames=['Short','Open','Load']
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Step=False,Inverted=False,Length=50e-9,
            WindowRaisedCosineDuration=50e-12,
            WindowReverseHalfWidthTime=800e-12,
            WindowForwardHalfWidthTime=500e-12,Denoise=True,
            fd=f)
        si.wl.WaveletDenoiser.wavelet=si.wl.WaveletDaubechies16()

        #sigma=1e-18
        si.td.wf.Waveform.adaptionStrategy='Linear'

        result = self.GetSimulationResultsCheck('OysterMonteCarlo.xml')
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]

        filename='TestOysterTest_testOysterTwoPortOysterFixtureFileNewer'

        cm=si.m.cal.Calibration(ports,f)

        Fixtures = [si.sp.SParameterFile(filename+str(p+1)+'.s'+str(cm.ports*2)+'p')
                    for p in range(cm.ports)]

        cm.ET=[si.m.cal.ErrorTerms().Initialize(cm.ports) for _ in range(len(f))]
        for n in range(len(cm)):
            for r in range(cm.ports):
                for c in range(cm.ports):
                    if r==c:
                        EDr=Fixtures[c][n][r][c]
                        ERr=Fixtures[c][n][r][cm.ports+r]
                        ESr=Fixtures[c][n][cm.ports+r][cm.ports+r]
                        cm.ET[n][r][c]=[EDr,ERr,ESr]
                    else:
                        EXrc=Fixtures[c][n][r][c]
                        ETrc=Fixtures[c][n][r][cm.ports+r]
                        ELrc=Fixtures[c][n][cm.ports+r][cm.ports+r]
                        cm.ET[n][r][c]=[EXrc,ETrc,ELrc]

        FixtureNewer=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(FixtureNewer[p],self.NameForTest()+'OysterFixtureFileNewerTest'+str(p+1)+'.s'+str(ports*2)+'p')

        wfName='Load1'

        wf=outputWaveforms[outputNames.index(wfName)]
        sp=tdr.RawMeasuredSParameters(wf)
        DUTCalcNewerSp=cm.DutCalculation(sp)
        self.SParameterRegressionChecker(DUTCalcNewerSp, self.NameForTest()+'_'+wfName+'Calc.s1p')

        si.test.PySIAppTestHelper.plotErrors=False

        if si.test.PySIAppTestHelper.plotErrors:
            import matplotlib.pyplot as plt
            for r in range(DUTCalcNewerSp.m_P):
                for c in range(DUTCalcNewerSp.m_P):
                    plt.clf()
                    plt.title('S'+str(r+1)+str(c+1))
                    plt.plot(DUTCalcNewerSp.FrequencyResponse(r+1,c+1).Frequencies('GHz'),DUTCalcNewerSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                    plt.xlabel('frequency (GHz)')
                    plt.ylabel('amplitude (dB)')
                    plt.ylim(ymin=-60,ymax=30)
                    plt.legend(loc='upper right')
                    plt.grid(True)
                    plt.show()

        rawwf=outputWaveforms[outputNames.index(wfName)]
        Avg=1000000
        sigma=707e-6/math.sqrt(Avg)
        TDRWaveformToSParameterConverter.sigmaMultiple=5
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Step=False,Inverted=False,Length=50e-9,
            WindowRaisedCosineDuration=50e-12,
            WindowReverseHalfWidthTime=800e-12,
            WindowForwardHalfWidthTime=500e-12,Denoise=False,
            fd=f)
        si.wl.WaveletDenoiser.wavelet=si.wl.WaveletDaubechies16()

        Num=10
        res=[None for _ in range(Num)]
        plotthem=False

        for n in range(Num):
            print 'wf: '+str(n)
            wf=rawwf+si.td.wf.NoiseWaveform(rawwf.td,sigma)
            sp=tdr.RawMeasuredSParameters(wf)

            if plotthem:
                plt.clf()
                plt.title('denoised derivatives')
                wf=tdr.TrimmedDenoisedDerivatives[0]
                plt.plot(wf.Times('ns'),wf.Values(),label=wfName)
                xw=tdr.IncidentExtractionWindow*0.35
                plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
                rxw=tdr.ReflectExtractionWindow*0.35
                plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
                plt.xlabel('time (ns)')
                plt.ylabel('amplitude')
                plt.legend(loc='upper right')
                plt.grid(False)
                if plotthem: plt.show()

            res[n]=cm.DutCalculation(sp)

        import matplotlib.pyplot as plt
        plt.clf()
        plt.title(wfName+' with '+str(Avg)+' averages')
        for sp in res:
            plt.plot(sp.FrequencyResponse(1,1).Frequencies('GHz'),sp.FrequencyResponse(1,1).Values('dB'))
        plt.xlabel('frequency (GHz)')
        plt.ylabel('amplitude (dB)')
        plt.ylim(ymin=-60,ymax=30)
        plt.grid(True)
        plt.show()

    def testZOysterMonteCarloThru(self):
        return
        ports=2
        f=si.fd.EvenlySpacedFrequencyList(40e9,8000)
        reflectNames=['Short','Open','Load']
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Step=False,Inverted=False,Length=50e-9,
            WindowRaisedCosineDuration=50e-12,
            WindowReverseHalfWidthTime=800e-12,
            WindowForwardHalfWidthTime=500e-12,Denoise=True,
            fd=f)
        si.wl.WaveletDenoiser.wavelet=si.wl.WaveletDaubechies4()

        #sigma=1e-18
        si.td.wf.Waveform.adaptionStrategy='Linear'

        result = self.GetSimulationResultsCheck('OysterMonteCarlo.xml')
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]

        filename='TestOysterTest_testOysterTwoPortOysterFixtureFileNewer'

        cm=si.m.cal.Calibration(ports,f)

        Fixtures = [si.sp.SParameterFile(filename+str(p+1)+'.s'+str(cm.ports*2)+'p')
                    for p in range(cm.ports)]

        cm.ET=[si.m.cal.ErrorTerms().Initialize(cm.ports) for _ in range(len(f))]
        for n in range(len(cm)):
            for r in range(cm.ports):
                for c in range(cm.ports):
                    if r==c:
                        EDr=Fixtures[c][n][r][c]
                        ERr=Fixtures[c][n][r][cm.ports+r]
                        ESr=Fixtures[c][n][cm.ports+r][cm.ports+r]
                        cm.ET[n][r][c]=[EDr,ERr,ESr]
                    else:
                        EXrc=Fixtures[c][n][r][c]
                        ETrc=Fixtures[c][n][r][cm.ports+r]
                        ELrc=Fixtures[c][n][cm.ports+r][cm.ports+r]
                        cm.ET[n][r][c]=[EXrc,ETrc,ELrc]

        FixtureNewer=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(FixtureNewer[p],self.NameForTest()+'OysterFixtureFileNewerTest'+str(p+1)+'.s'+str(ports*2)+'p')

        wfName='Thru'
        wf11=outputWaveforms[outputNames.index(wfName+'11')]
        wf21=outputWaveforms[outputNames.index(wfName+'21')]
        wf22=outputWaveforms[outputNames.index(wfName+'22')]
        wf12=outputWaveforms[outputNames.index(wfName+'12')]
        sp=tdr.RawMeasuredSParameters([[wf11,wf21],[wf12,wf22]])

        DUTCalcNewerSp=cm.DutCalculation(sp)
        self.SParameterRegressionChecker(DUTCalcNewerSp, self.NameForTest()+'_'+wfName+'Calc.s2p')

        si.test.PySIAppTestHelper.plotErrors=True

        if si.test.PySIAppTestHelper.plotErrors:
            import matplotlib.pyplot as plt
            for r in range(DUTCalcNewerSp.m_P):
                for c in range(DUTCalcNewerSp.m_P):
                    plt.clf()
                    plt.title('S'+str(r+1)+str(c+1))
                    plt.plot(DUTCalcNewerSp.FrequencyResponse(r+1,c+1).Frequencies('GHz'),DUTCalcNewerSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                    plt.xlabel('frequency (GHz)')
                    plt.ylabel('amplitude (dB)')
                    plt.ylim(ymin=-60,ymax=30)
                    plt.legend(loc='upper right')
                    plt.grid(True)
                    plt.show()

        rawwf11=outputWaveforms[outputNames.index(wfName+'11')]
        rawwf21=outputWaveforms[outputNames.index(wfName+'21')]
        rawwf22=outputWaveforms[outputNames.index(wfName+'22')]
        rawwf12=outputWaveforms[outputNames.index(wfName+'12')]

        Avg=10000
        sigma=707e-6/math.sqrt(Avg)
        TDRWaveformToSParameterConverter.sigmaMultiple=5
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Step=False,Inverted=False,Length=50e-9,
            WindowRaisedCosineDuration=50e-12,
            WindowReverseHalfWidthTime=800e-12,
            WindowForwardHalfWidthTime=500e-12,Denoise=False,
            fd=f)
        si.wl.WaveletDenoiser.wavelet=si.wl.WaveletDaubechies16()

        Num=10
        res=[None for _ in range(Num)]
        plotthem=False

        for n in range(Num):
            print 'wf: '+str(n)
            wf11=rawwf11+si.td.wf.NoiseWaveform(rawwf11.td,sigma)
            wf12=rawwf12+si.td.wf.NoiseWaveform(rawwf12.td,sigma)
            wf21=rawwf21+si.td.wf.NoiseWaveform(rawwf21.td,sigma)
            wf22=rawwf22+si.td.wf.NoiseWaveform(rawwf22.td,sigma)
            sp=tdr.RawMeasuredSParameters([[wf11,wf21],[wf12,wf22]])

            res[n]=cm.DutCalculation(sp)

        si.test.PySIAppTestHelper.plotErrors=True

        if si.test.PySIAppTestHelper.plotErrors:
            import matplotlib.pyplot as plt
            for r in range(DUTCalcNewerSp.m_P):
                for c in range(DUTCalcNewerSp.m_P):
                    plt.clf()
                    plt.title('S'+str(r+1)+str(c+1))
                    for n in range(Num):
                        plt.plot(res[n].FrequencyResponse(r+1,c+1).Frequencies('GHz'),res[n].FrequencyResponse(r+1,c+1).Values('dB'))
                    plt.xlabel('frequency (GHz)')
                    plt.ylabel('amplitude (dB)')
                    plt.ylim(ymin=-60,ymax=30)
                    plt.legend(loc='upper right')
                    plt.grid(True)
                    plt.show()

    def testOysterIdealThruRecovery(self):
        pass
        ports=2
        f=si.fd.EvenlySpacedFrequencyList(40e9,8000)
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Step=False,Inverted=False,Length=50e-9,
            WindowRaisedCosineDuration=50e-12,
            WindowReverseHalfWidthTime=800e-12,
            WindowForwardHalfWidthTime=500e-12,Denoise=True,
            fd=f)
        #si.m.tdr.TDRWaveformToSParameterConverter.sigmaMultiple=0.
        si.wl.WaveletDenoiser.wavelet=si.wl.WaveletDaubechies16()

        #sigma=1e-18
        si.td.wf.Waveform.adaptionStrategy='Linear'

        result = self.GetSimulationResultsCheck('OysterSimulationTwoPort.xml')
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=self.NoisyWaveforms(result[3])

        spDict['Short1']=tdr.RawMeasuredSParameters(outputWaveforms[outputNames.index('Short')])
        spDict['Short2']=tdr.RawMeasuredSParameters(outputWaveforms[outputNames.index('Short')])
        spDict['Open1']=tdr.RawMeasuredSParameters(outputWaveforms[outputNames.index('Open')])
        spDict['Open2']=tdr.RawMeasuredSParameters(outputWaveforms[outputNames.index('Open')])
        spDict['Load1']=tdr.RawMeasuredSParameters(outputWaveforms[outputNames.index('Load')])
        spDict['Load2']=tdr.RawMeasuredSParameters(outputWaveforms[outputNames.index('Load')])
        spDict['Thru']=tdr.RawMeasuredSParameters([[outputWaveforms[outputNames.index('Thru11')],outputWaveforms[outputNames.index('Thru21')]],
                                                   [outputWaveforms[outputNames.index('Thru12')],outputWaveforms[outputNames.index('Thru22')]]])
        spDict['DUT']=tdr.RawMeasuredSParameters([[outputWaveforms[outputNames.index('IThru11')],outputWaveforms[outputNames.index('IThru21')]],
                                                   [outputWaveforms[outputNames.index('IThru12')],outputWaveforms[outputNames.index('IThru22')]]])

        calStandards=[self.SParameterResultsChecker('OysterFixtureShort.xml')[0],
              self.SParameterResultsChecker('OysterFixtureOpen.xml')[0],
              self.SParameterResultsChecker('OysterFixtureLoad.xml')[0],
              self.SParameterResultsChecker('OysterFixtureThru.xml')[0]]

#         calStandards=[si.sp.SParameterFile('CalShort.s1p'),
#               si.sp.SParameterFile('CalOpen.s1p'),
#               si.sp.SParameterFile('CalLoad.s1p'),
#               si.sp.SParameterFile('CalThru.s2p')]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru'].FrequencyResponse(1,1),spDict['Thru'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru'].FrequencyResponse(2,2),spDict['Thru'].FrequencyResponse(1,2),calStandards[3].PortReorder([2,1]),1,0,'Thru122'),
            ]

        cm=si.m.cal.Calibration(ports,f,ml).CalculateErrorTerms()
        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],self.NameForTest()+'OysterFixtureFile'+str(p+1)+'.s'+str(ports*2)+'p')

        DUTRawCalcSp=cm.DutCalculation(spDict['DUT'])
        self.SParameterRegressionChecker(DUTRawCalcSp, self.NameForTest()+'_RawCalc.s2p')

        DUTCalcSp=self.DeembeddingResultsChecker('OysterFixtureIdealThruDeembed.xml')[1][0]
        DUTActualSp=si.sp.dev.TLineLossless(f,2,50.,0.)
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-2)

        si.test.PySIAppTestHelper.plotErrors=True

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(SpAreEqual,'s-parameters not equal')
        return

        Avg=10000
        sigma=707e-6/math.sqrt(Avg)

        Num=5
        res=[None for _ in range(Num)]
        plotthem=False

        rawwf11=outputWaveforms[outputNames.index('IThru11')]
        rawwf21=outputWaveforms[outputNames.index('IThru21')]
        rawwf12=outputWaveforms[outputNames.index('IThru12')]
        rawwf22=outputWaveforms[outputNames.index('IThru22')]
        pysi=self.Preliminary('OysterFixtureIdealThruDeembedMonteCarlo.xml')

        for n in range(Num):
            print 'wf: '+str(n)
            wf11=rawwf11+si.td.wf.NoiseWaveform(rawwf11.td,sigma)
            wf12=rawwf12+si.td.wf.NoiseWaveform(rawwf12.td,sigma)
            wf21=rawwf21+si.td.wf.NoiseWaveform(rawwf21.td,sigma)
            wf22=rawwf22+si.td.wf.NoiseWaveform(rawwf22.td,sigma)
            sp=tdr.RawMeasuredSParameters([[wf11,wf21],[wf12,wf22]])
            res[n]=cm.DutCalculation(sp)
            res[n].WriteToFile(self.NameForTest()+'_RawCalcMonteCarlo.s2p')
            result=pysi.Deembed()
            res[n]=result[1][0]

        si.test.PySIAppTestHelper.plotErrors=True

        if si.test.PySIAppTestHelper.plotErrors:
            import matplotlib.pyplot as plt
            for r in range(res[0].m_P):
                for c in range(res[0].m_P):
                    plt.clf()
                    plt.title('S'+str(r+1)+str(c+1)+' with '+str(Avg)+ 'averages')
                    for n in range(Num):
                        plt.plot(res[n].FrequencyResponse(r+1,c+1).Frequencies('GHz'),res[n].FrequencyResponse(r+1,c+1).Values('dB'))
                    plt.xlabel('frequency (GHz)')
                    plt.ylabel('amplitude (dB)')
                    plt.ylim(ymin=-60,ymax=30)
                    plt.legend(loc='upper right')
                    plt.grid(True)
                    plt.show()
    def PutWaveform(self,oyster,wf):
        import win32com.client as win32
        import array
        oyster.PutMeasurement(
            win32.VARIANT(win32.pythoncom.VT_R8 | win32.pythoncom.VT_BYREF | win32.pythoncom.VT_ARRAY,
            array.array('d',wf.Times())),
            win32.VARIANT(win32.pythoncom.VT_R8 | win32.pythoncom.VT_BYREF | win32.pythoncom.VT_ARRAY,
            array.array('d',wf.Values())))
    def PutSettings(self,oyster,sdict):
        for key in sdict:
            attr=key
            value=sdict[key]
            from win32com.client.dynamic import _GetDescInvokeType
            import pythoncom
            if oyster.__LazyMap__(attr):
                if attr in oyster._olerepr_.propMapPut:
                    entry = oyster._olerepr_.propMapPut[attr]
                    invoke_type = _GetDescInvokeType(entry, pythoncom.INVOKE_PROPERTYPUT)
                    oyster._oleobj_.Invoke(entry.dispid, 0, invoke_type, 0, value)
    def GetOysterSParameterResult(self,oyster):
        import win32com.client as win32
        import array
        numPorts=oyster.NumPortsInMeasurement
        numPoints=oyster.NumPoints
        Fe=oyster.EndFrequency
        sp=si.sp.SParameters(si.fd.EvenlySpacedFrequencyList(Fe,numPoints),[[[0.0 for _ in range(numPorts)] for _ in range(numPorts)] for _ in range(numPoints+1)])
        for r in range(numPorts):
            for c in range(numPorts):
                resrvar=oyster.NewResults('s['+str(r+1)+']['+str(c+1)+'],Real')
                rescvar=oyster.NewResults('s['+str(r+1)+']['+str(c+1)+'],Imag')
                for n in range(numPoints+1):
                    sp[n][r][c]=resrvar[n][1]+1j*rescvar[n][1]
        return sp
    def testComObject(self):
        pass
        import os
        # uncomment next two lines for debugging
        #print os.getpid()
        #raw_input('press key to continue')
        import win32com.client as win32
        Short1=si.td.wf.Waveform().ReadFromFile('OysterSimulationTwoPort_Short.txt')
        Short2=Short1
        Short3=Short1
        Short4=Short1
        Open1=si.td.wf.Waveform().ReadFromFile('OysterSimulationTwoPort_Open.txt')
        Open2=Open1
        Open3=Open1
        Open4=Open1
        Load1=si.td.wf.Waveform().ReadFromFile('OysterSimulationTwoPort_Load.txt')
        Load2=Load1
        Load3=Load1
        Load4=Load1
        Thru1211=si.td.wf.Waveform().ReadFromFile('OysterSimulationTwoPort_Thru11.txt')
        Thru1212=si.td.wf.Waveform().ReadFromFile('OysterSimulationTwoPort_Thru12.txt')
        Thru1221=si.td.wf.Waveform().ReadFromFile('OysterSimulationTwoPort_Thru21.txt')
        Thru1222=si.td.wf.Waveform().ReadFromFile('OysterSimulationTwoPort_Thru22.txt')
        Thru3411=Thru1211
        Thru3421=Thru1221
        Thru3412=Thru1212
        Thru3422=Thru1222
        Thru1411=Thru1211
        Thru1421=Thru1221
        Thru1412=Thru1212
        Thru1422=Thru1222
        Thru2311=Thru1211
        Thru2321=Thru1221
        Thru2312=Thru1212
        Thru2322=Thru1222
        Dut1211=si.td.wf.Waveform().ReadFromFile('OysterSimulationTwoPort_Dut11.txt')
        Dut1212=si.td.wf.Waveform().ReadFromFile('OysterSimulationTwoPort_Dut12.txt')
        Dut1221=si.td.wf.Waveform().ReadFromFile('OysterSimulationTwoPort_Dut21.txt')
        Dut1222=si.td.wf.Waveform().ReadFromFile('OysterSimulationTwoPort_Dut22.txt')

        wfDict={'S,S,S,S,X,X,X,X,X,X':{1:{1:{'wf':Short1,'name':'Short1'}},
                                       2:{2:{'wf':Short2,'name':'Short2'}},
                                       3:{3:{'wf':Short3,'name':'Short3'}},
                                       4:{4:{'wf':Short4,'name':'Short4'}}},
                'O,O,O,O,X,X,X,X,X,X':{1:{1:{'wf':Open1,'name':'Open1'}},
                                       2:{2:{'wf':Open2,'name':'Open2'}},
                                       3:{3:{'wf':Open3,'name':'Open3'}},
                                       4:{4:{'wf':Open4,'name':'Open4'}}},
                'L,L,L,L,X,X,X,X,X,X':{1:{1:{'wf':Load1,'name':'Load1'}},
                                       2:{2:{'wf':Load2,'name':'Load2'}},
                                       3:{3:{'wf':Load3,'name':'Load3'}},
                                       4:{4:{'wf':Load4,'name':'Load4'}}},
                'RS2,RS1,RS4,RS3,X,X,X,X,X,X':{1:{1:{'wf':Thru1211,'name':'Thru1211'},
                                                  2:{'wf':Thru1221,'name':'Thru1221'}},
                                               2:{1:{'wf':Thru1212,'name':'Thru1212'},
                                                  2:{'wf':Thru1222,'name':'Thru1222'}},
                                               3:{3:{'wf':Thru3411,'name':'Thru3411'},
                                                  4:{'wf':Thru3421,'name':'Thru3421'}},
                                               4:{3:{'wf':Thru3412,'name':'Thru3412'},
                                                  4:{'wf':Thru3422,'name':'Thru3422'}}},
                'RS4,RS3,RS2,RS1,X,X,X,X,X,X':{1:{1:{'wf':Thru1411,'name':'Thru1411'},
                                                  4:{'wf':Thru1421,'name':'Thru1421'}},
                                               4:{1:{'wf':Thru1412,'name':'Thru1412'},
                                                  4:{'wf':Thru1422,'name':'Thru1422'}},
                                               2:{2:{'wf':Thru2311,'name':'Thru2311'},
                                                  3:{'wf':Thru2321,'name':'Thru2321'}},
                                               3:{2:{'wf':Thru2312,'name':'Thru2312'},
                                                  3:{'wf':Thru2322,'name':'Thru2322'}}},
                'D1,D2,D3,D4,X,X,X,X,X,X':{1:{1:{'wf':Dut1211,'name':'Dut1211'},
                                              2:{'wf':Dut1221,'name':'Dut1221'}},
                                           2:{1:{'wf':Dut1212,'name':'Dut1212'},
                                              2:{'wf':Dut1222,'name':'Dut1222'}}}
                }
        oyster = win32.Dispatch(r'OysterSparameterCalcSvr.OysterCalc')

        oysterExpertSettings = {
            'InputIsAnImpulse':'True',
            'IncidentEdgeTime':800e-12,
            'ModelName':'RP4004E',
            'SerialNumber':'123456',
            'IncidentEdgeTime':800e-12,
            'IncidentEdgeSides':500-12,
            'CalibrationFilesPath':str(os.getcwd()),
            'WaveletDenoisingEnabled':'False',
            'UseOMP':'True',
            'BaselineEnabled':'False',
            'SecondTierCalibrationFactoryEnabled':'False',
            'DeEmbedCables':'True',
            'CableFileNames':str(os.getcwd())+'\\Cable1_resampled.s2p,'+str(os.getcwd())+'\\Cable2_resampled.s2p,'+str(os.getcwd())+'\\Cable1_resampled.s2p,'+str(os.getcwd())+'\\Cable2_resampled.s2p',
            'DebugMode':'False'
            }

        dutMeasurementSettings = {
            'NumPortsInMeasurement':2,
            'NumPoints':8000,
            'EndFrequency':40e9,
            }


        self.PutSettings(oyster, oysterExpertSettings)
        self.PutSettings(oyster, dutMeasurementSettings)

        #self.DebugMode = 'True'

#     [propget, id(49), helpstring("property ResultType")] HRESULT ResultType([out, retval] BSTR* pVal);
#     [propput, id(49), helpstring("property ResultType")] HRESULT ResultType([in] BSTR newVal);
#     [propget, id(50), helpstring("property ResultIncidentPort")] HRESULT ResultIncidentPort([out, retval] LONG* pVal);
#     [propput, id(50), helpstring("property ResultIncidentPort")] HRESULT ResultIncidentPort([in] LONG newVal);
#     [propget, id(51), helpstring("property ResultReflectPort")] HRESULT ResultReflectPort([out, retval] LONG* pVal);
#     [propput, id(51), helpstring("property ResultReflectPort")] HRESULT ResultReflectPort([in] LONG newVal);
#     [propget, id(52), helpstring("property ResultStatus")] HRESULT ResultStatus([out, retval] BSTR* pVal);
#     [propget, id(53), helpstring("property ResultNumPoints")] HRESULT ResultNumPoints([out, retval] LONG* pVal);
#     [propget, id(54), helpstring("property ResultNumPorts")] HRESULT ResultNumPorts([out, retval] LONG* pVal);
#     
#     [id(56), helpstring("method ClearDutMeasures")] HRESULT ClearDutMeasures(void);
#     [id(57), helpstring("method ClearCalibrationMeasures")] HRESULT ClearCalibrationMeasures(void);
#     [propget, id(60), helpstring("property ResultFileName")] HRESULT ResultFileName([out, retval] BSTR* pVal);
#     [propput, id(60), helpstring("property ResultFileName")] HRESULT ResultFileName([in] BSTR newVal);
#     [id(61), helpstring("method WriteResultToFile")] HRESULT WriteResultToFile(void);
#     [propget, id(62), helpstring("property EnforcePassivity")] HRESULT EnforcePassivity([out, retval] BSTR* pVal);
#     [propput, id(62), helpstring("property EnforcePassivity")] HRESULT EnforcePassivity([in] BSTR newVal);
#     [propget, id(65), helpstring("property DeEmbedFixture")] HRESULT DeEmbedFixture([out, retval] BSTR* pVal);
#     [propput, id(65), helpstring("property DeEmbedFixture")] HRESULT DeEmbedFixture([in] BSTR newVal);
#     [propget, id(66), helpstring("property FixtureFileName")] HRESULT FixtureFileName([out, retval] BSTR* pVal);
#     [propput, id(66), helpstring("property FixtureFileName")] HRESULT FixtureFileName([in] BSTR newVal);
#     [propget, id(67), helpstring("property EnforceReciprocity")] HRESULT EnforceReciprocity([out, retval] BSTR* pVal);
#     [propput, id(67), helpstring("property EnforceReciprocity")] HRESULT EnforceReciprocity([in] BSTR newVal);
#     [propget, id(72), helpstring("property DutToConverterPinDefinitions")] HRESULT DutToConverterPinDefinitions([out, retval] BSTR* pVal);
#     [propput, id(72), helpstring("property DutToConverterPinDefinitions")] HRESULT DutToConverterPinDefinitions([in] BSTR newVal);
#     [propget, id(73), helpstring("property UserPortDefinitions")] HRESULT UserPortDefinitions([out, retval] BSTR* pVal);
#     [propput, id(73), helpstring("property UserPortDefinitions")] HRESULT UserPortDefinitions([in] BSTR newVal);
#     [propget, id(74), helpstring("property ConvertToUserSParameters")] HRESULT ConvertToUserSParameters([out, retval] BSTR* pVal);
#     [propput, id(74), helpstring("property ConvertToUserSParameters")] HRESULT ConvertToUserSParameters([in] BSTR newVal);    
#     [propget, id(75), helpstring("property AccumulateResults")] HRESULT AccumulateResults([out, retval] BSTR* pVal);
#     [propput, id(75), helpstring("property AccumulateResults")] HRESULT AccumulateResults([in] BSTR newVal);
#     [propget, id(76), helpstring("property AccumulationCount")] HRESULT AccumulationCount([out, retval] LONG* pVal);
#     [propget, id(77), helpstring("property AccumulationCountMax")] HRESULT AccumulationCountMax([out, retval] LONG* pVal);
#     [propput, id(77), helpstring("property AccumulationCountMax")] HRESULT AccumulationCountMax([in] LONG newVal);
#     [id(78), helpstring("method ClearDutAccumulation")] HRESULT ClearDutAccumulation(void);
#     [propget, id(79), helpstring("property RelaySettings")] HRESULT RelaySettings([out, retval] BSTR* pVal);
#     [propget, id(80), helpstring("property IsCalibrationMeasurement")] HRESULT IsCalibrationMeasurement([out, retval] BSTR* pVal);
#     [propget, id(81), helpstring("property IsDutMeasurement")] HRESULT IsDutMeasurement([out, retval] BSTR* pVal);
#     [propget, id(83), helpstring("property WaveletDenoisingType")] HRESULT WaveletDenoisingType([out, retval] LONG* pVal);
#     [propput, id(83), helpstring("property WaveletDenoisingType")] HRESULT WaveletDenoisingType([in] LONG newVal);
#     [propget, id(84), helpstring("property WindowEnabled")] HRESULT WindowEnabled([out, retval] BSTR* pVal);
#     [propput, id(84), helpstring("property WindowEnabled")] HRESULT WindowEnabled([in] BSTR newVal);
#     [propget, id(85), helpstring("property WindowLength")] HRESULT WindowLength([out, retval] DOUBLE* pVal);
#     [propput, id(85), helpstring("property WindowLength")] HRESULT WindowLength([in] DOUBLE newVal);
#     [propget, id(86), helpstring("property WaveletDenoisingAutoThresholdBandTimePercent")] HRESULT WaveletDenoisingAutoThresholdBandTimePercent([out, retval] DOUBLE* pVal);
#     [propput, id(86), helpstring("property WaveletDenoisingAutoThresholdBandTimePercent")] HRESULT WaveletDenoisingAutoThresholdBandTimePercent([in] DOUBLE newVal);
#     [propget, id(87), helpstring("property WaveletDenoisingAutoThresholdSDevMultiplier")] HRESULT WaveletDenoisingAutoThresholdSDevMultiplier([out, retval] DOUBLE* pVal);
#     [propput, id(87), helpstring("property WaveletDenoisingAutoThresholdSDevMultiplier")] HRESULT WaveletDenoisingAutoThresholdSDevMultiplier([in] DOUBLE newVal);
#     [propget, id(89), helpstring("property ManualCalUseCalKit")] HRESULT ManualCalUseCalKit([out, retval] BSTR* pVal);
#     [propput, id(89), helpstring("property ManualCalUseCalKit")] HRESULT ManualCalUseCalKit([in] BSTR newVal);
#     [propget, id(90), helpstring("property ManualCalKitFileName")] HRESULT ManualCalKitFileName([out, retval] BSTR* pVal);
#     [propput, id(90), helpstring("property ManualCalKitFileName")] HRESULT ManualCalKitFileName([in] BSTR newVal);
#     [propget, id(91), helpstring("property ManualCalStandardFileNames")] HRESULT ManualCalStandardFileNames([out, retval] BSTR* pVal);
#     [propput, id(91), helpstring("property ManualCalStandardFileNames")] HRESULT ManualCalStandardFileNames([in] BSTR newVal);
#     [propget, id(96), helpstring("property UserConnectionString")] HRESULT UserConnectionString([out, retval] BSTR* pVal);
#     [propget, id(97), helpstring("property UserConnectionStringDefault")] HRESULT UserConnectionStringDefault([out, retval] BSTR* pVal);
#     [propget, id(99), helpstring("property SaveStepsToFileCalOnly")] HRESULT SaveStepsToFileCalOnly([out, retval] BSTR* pVal);
#     [propput, id(99), helpstring("property SaveStepsToFileCalOnly")] HRESULT SaveStepsToFileCalOnly([in] BSTR newVal);
#     [propget, id(100), helpstring("property SaveStepsToFileCompleteFileName")] HRESULT SaveStepsToFileCompleteFileName([out, retval] BSTR* pVal);
#     [propput, id(100), helpstring("property SaveStepsToFileCompleteFileName")] HRESULT SaveStepsToFileCompleteFileName([in] BSTR newVal);
#     [id(101), helpstring("method SaveStepsToFile")] HRESULT SaveStepsToFile(void);
#     [id(102), helpstring("method ReadStepsFromFile")] HRESULT ReadStepsFromFile(void);
#     [propget, id(103), helpstring("property GeneratePossibleFrequencyNumPoints")] HRESULT GeneratePossibleFrequencyNumPoints([in] DOUBLE dDesiredEndFrequency, [out, retval] VARIANT* pVal);
#     [propget, id(104), helpstring("property MaxNumPoints")] HRESULT MaxNumPoints([out, retval] LONG* pVal);
#     [propput, id(104), helpstring("property MaxNumPoints")] HRESULT MaxNumPoints([in] LONG newVal);
#     [propget, id(105), helpstring("property MaxEndFrequency")] HRESULT MaxEndFrequency([out, retval] DOUBLE* pVal);
#     [propput, id(105), helpstring("property MaxEndFrequency")] HRESULT MaxEndFrequency([in] DOUBLE newVal);
#     [propget, id(106), helpstring("property CausalityEnforcementEnabled")] HRESULT CausalityEnforcementEnabled([out, retval] BSTR* pVal);
#     [propput, id(106), helpstring("property CausalityEnforcementEnabled")] HRESULT CausalityEnforcementEnabled([in] BSTR newVal);
#     [propget, id(107), helpstring("property CausalityMaxImpulseLength")] HRESULT CausalityMaxImpulseLength([out, retval] DOUBLE* pVal);
#     [propput, id(107), helpstring("property CausalityMaxImpulseLength")] HRESULT CausalityMaxImpulseLength([in] DOUBLE newVal);
#     [propget, id(108), helpstring("property CausalityPhasesToCheck")] HRESULT CausalityPhasesToCheck([out, retval] LONG* pVal);
#     [propput, id(108), helpstring("property CausalityPhasesToCheck")] HRESULT CausalityPhasesToCheck([in] LONG newVal);
#     [propget, id(109), helpstring("property CausalityEnforcementUseFastMethod")] HRESULT CausalityEnforcementUseFastMethod([out, retval] BSTR* pVal);
#     [propput, id(109), helpstring("property CausalityEnforcementUseFastMethod")] HRESULT CausalityEnforcementUseFastMethod([in] BSTR newVal);
#     [propget, id(110), helpstring("property DirectCZT")] HRESULT DirectCZT([out, retval] BSTR* pVal);
#     [propput, id(110), helpstring("property DirectCZT")] HRESULT DirectCZT([in] BSTR newVal);
#     [propget, id(111), helpstring("property FastCZTAlgorithmType")] HRESULT FastCZTAlgorithmType([out, retval] LONG* pVal);
#     [propput, id(111), helpstring("property FastCZTAlgorithmType")] HRESULT FastCZTAlgorithmType([in] LONG newVal);
#     [propget, id(112), helpstring("property UseManualCal")] HRESULT UseManualCal([out, retval] BSTR* pVal);
#     [propput, id(112), helpstring("property UseManualCal")] HRESULT UseManualCal([in] BSTR newVal);
#     [propget, id(116), helpstring("property AdapterFileNames")] HRESULT AdapterFileNames([out, retval] BSTR* pVal);
#     [propput, id(116), helpstring("property AdapterFileNames")] HRESULT AdapterFileNames([in] BSTR newVal);
#     [propget, id(117), helpstring("property UseDirectSParameterMeasurement")] HRESULT UseDirectSParameterMeasurement([out, retval] BSTR* pVal);
#     [propput, id(117), helpstring("property UseDirectSParameterMeasurement")] HRESULT UseDirectSParameterMeasurement([in] BSTR newVal);
#     [id(118), helpstring("method PutMeasuredSParameters")] HRESULT PutMeasuredSParameters([in] BSTR FileNameAndPortnumbers);
#     [id(119), helpstring("method SelfTest")] HRESULT SelfTest([in] BSTR ArgList, [in] BSTR LogName, [out] BOOL * pSucceeded);
#     [propget, id(120), helpstring("property NewResults")] HRESULT NewResults([in] BSTR ResultString, [out, retval] VARIANT* pVal);
#     [propget, id(121), helpstring("property CalibratedStepResponseRiseTime")] HRESULT CalibratedStepResponseRiseTime([out, retval] DOUBLE* pVal);
#     [propput, id(121), helpstring("property CalibratedStepResponseRiseTime")] HRESULT CalibratedStepResponseRiseTime([in] DOUBLE newVal);
#     [id(122), helpstring("method GetListOfRequiredAndNeededMeasurements")] HRESULT GetListOfRequiredAndNeededMeasurements([out, retval] BSTR* sResult);
#     [propget, id(123), helpstring("property AbortFlag")] HRESULT AbortFlag([out, retval] BOOL* pVal);
#     [propput, id(123), helpstring("property AbortFlag")] HRESULT AbortFlag([in] BOOL newVal);
#     [propget, id(124), helpstring("property CalibratedStepResponseUpSampleStep")] HRESULT CalibratedStepResponseUpSampleStep([out, retval] BSTR* pVal);
#     [propput, id(124), helpstring("property CalibratedStepResponseUpSampleStep")] HRESULT CalibratedStepResponseUpSampleStep([in] BSTR newVal);
#     [propget, id(125), helpstring("property UpSampleFactor")] HRESULT UpSampleFactor([out, retval] LONG* pVal);
#     [propput, id(125), helpstring("property UpSampleFactor")] HRESULT UpSampleFactor([in] LONG newVal);
#     [id(126), helpstring("method InstallSParametersFromFile")] HRESULT InstallSParametersFromFile([in] BSTR spFileName);
#     [propget, id(127), helpstring("property UpSamplerSampleDistance")] HRESULT UpSamplerSampleDistance([out, retval] LONG* pVal);
#     [propput, id(127), helpstring("property UpSamplerSampleDistance")] HRESULT UpSamplerSampleDistance([in] LONG newVal);
#     [propget, id(130), helpstring("property WindowTDRNumPointsInTransition")] HRESULT WindowTDRNumPointsInTransition([out, retval] LONG* pVal);
#     [propput, id(130), helpstring("property WindowTDRNumPointsInTransition")] HRESULT WindowTDRNumPointsInTransition([in] LONG newVal);
#     [propget, id(132), helpstring("property CacheAlways")] HRESULT CacheAlways([out, retval] BSTR* pVal);
#     [propput, id(132), helpstring("property CacheAlways")] HRESULT CacheAlways([in] BSTR newVal);
#     [propget, id(133), helpstring("property ResampleToBase")] HRESULT ResampleToBase([out, retval] BSTR* pVal);
#     [propput, id(133), helpstring("property ResampleToBase")] HRESULT ResampleToBase([in] BSTR newVal);
#     [propget, id(134), helpstring("property CableShrinkageFactorPercentString")] HRESULT CableShrinkageFactorPercentString([out, retval] BSTR* pVal);
#     [propput, id(134), helpstring("property CableShrinkageFactorPercentString")] HRESULT CableShrinkageFactorPercentString([in] BSTR newVal);
#     [propget, id(135), helpstring("property CableShrinkageApply")] HRESULT CableShrinkageApply([out, retval] BSTR* pVal);
#     [propput, id(135), helpstring("property CableShrinkageApply")] HRESULT CableShrinkageApply([in] BSTR newVal);
#     [propget, id(138), helpstring("property ParkedRelaySetting")] HRESULT ParkedRelaySetting([out, retval] BSTR* pVal);
#     [propget, id(139), helpstring("property DUTCalculatorStatusString")] HRESULT DUTCalculatorStatusString([out, retval] BSTR* pVal);
#     [propget, id(140), helpstring("property PercentageTaskLeft")] HRESULT PercentageTaskLeft([out, retval] DOUBLE* pVal);
#     [propget, id(141), helpstring("property AllNecessaryFilesArePresentStatus")] HRESULT AllNecessaryFilesArePresentStatus([out, retval] BSTR* pVal);
#     [propget, id(143), helpstring("property SecondTierCalibrationUserEnabled")] HRESULT SecondTierCalibrationUserEnabled([out, retval] BSTR* pVal);
#     [propput, id(143), helpstring("property SecondTierCalibrationUserEnabled")] HRESULT SecondTierCalibrationUserEnabled([in] BSTR newVal);
#     [propget, id(144), helpstring("property SecondTierCalibrationFilePath")] HRESULT SecondTierCalibrationFilePath([out, retval] BSTR* pVal);
#     [propput, id(144), helpstring("property SecondTierCalibrationFilePath")] HRESULT SecondTierCalibrationFilePath([in] BSTR newVal);
#     [propget, id(145), helpstring("property SecondTierCalibrationFileName")] HRESULT SecondTierCalibrationFileName([out, retval] BSTR* pVal);
#     [propput, id(145), helpstring("property SecondTierCalibrationFileName")] HRESULT SecondTierCalibrationFileName([in] BSTR newVal);
#     [propget, id(146), helpstring("property SecondTierCalibrationFileType")] HRESULT SecondTierCalibrationFileType([out, retval] BSTR* pVal);
#     [propput, id(146), helpstring("property SecondTierCalibrationFileType")] HRESULT SecondTierCalibrationFileType([in] BSTR newVal);
#     [propget, id(150), helpstring("property SecondTierCalibrationWriteResult")] HRESULT SecondTierCalibrationWriteResult([out, retval] BSTR* pVal);
#     [propput, id(150), helpstring("property SecondTierCalibrationWriteResult")] HRESULT SecondTierCalibrationWriteResult([in] BSTR newVal);
#     [propget, id(151), helpstring("property WaveletSmoothingEnabled")] HRESULT WaveletSmoothingEnabled([out, retval] BSTR* pVal);
#     [propput, id(151), helpstring("property WaveletSmoothingEnabled")] HRESULT WaveletSmoothingEnabled([in] BSTR newVal);
#     [propget, id(152), helpstring("property WaveletSmoothingType")] HRESULT WaveletSmoothingType([out, retval] LONG* pVal);
#     [propput, id(152), helpstring("property WaveletSmoothingType")] HRESULT WaveletSmoothingType([in] LONG newVal);
#     [propget, id(153), helpstring("property WaveletSmoothingLevels")] HRESULT WaveletSmoothingLevels([out, retval] LONG* pVal);
#     [propput, id(153), helpstring("property WaveletSmoothingLevels")] HRESULT WaveletSmoothingLevels([in] LONG newVal);
#     [propget, id(154), helpstring("property WaveletSmoothingThresholdPercentMax")] HRESULT WaveletSmoothingThresholdPercentMax([out, retval] DOUBLE* pVal);
#     [propput, id(154), helpstring("property WaveletSmoothingThresholdPercentMax")] HRESULT WaveletSmoothingThresholdPercentMax([in] DOUBLE newVal);
#     [propget, id(155), helpstring("property WaveletSmoothingPhasesToCheck")] HRESULT WaveletSmoothingPhasesToCheck([out, retval] LONG* pVal);
#     [propput, id(155), helpstring("property WaveletSmoothingPhasesToCheck")] HRESULT WaveletSmoothingPhasesToCheck([in] LONG newVal);
#     [propget, id(156), helpstring("property BaselineFilterEnabled")] HRESULT BaselineFilterEnabled([out, retval] BSTR* pVal);
#     [propput, id(156), helpstring("property BaselineFilterEnabled")] HRESULT BaselineFilterEnabled([in] BSTR newVal);
#     [propget, id(157), helpstring("property BaselineFilterCutoff")] HRESULT BaselineFilterCutoff([out, retval] DOUBLE* pVal);
#     [propput, id(157), helpstring("property BaselineFilterCutoff")] HRESULT BaselineFilterCutoff([in] DOUBLE newVal);
#     [propget, id(158), helpstring("property BaselineFilterCoefficients")] HRESULT BaselineFilterCoefficients([out, retval] LONG* pVal);
#     [propput, id(158), helpstring("property BaselineFilterCoefficients")] HRESULT BaselineFilterCoefficients([in] LONG newVal);
#     [propget, id(159), helpstring("property WindowMaxLengthCalibration")] HRESULT WindowMaxLengthCalibration([out, retval] DOUBLE* pVal);
#     [propput, id(159), helpstring("property WindowMaxLengthCalibration")] HRESULT WindowMaxLengthCalibration([in] DOUBLE newVal);
#     [propget, id(160), helpstring("property WindowMaxLengthMeasurement")] HRESULT WindowMaxLengthMeasurement([out, retval] DOUBLE* pVal);
#     [propput, id(160), helpstring("property WindowMaxLengthMeasurement")] HRESULT WindowMaxLengthMeasurement([in] DOUBLE newVal);    
#     [propget, id(163), helpstring("property ReferenceImpedanceResult")] HRESULT ReferenceImpedanceResult([out, retval] DOUBLE* pVal);
#     [propput, id(163), helpstring("property ReferenceImpedanceResult")] HRESULT ReferenceImpedanceResult([in] DOUBLE newVal);
#     [propget, id(164), helpstring("property CausalityImpulseResponseLimitingEnabled")] HRESULT CausalityImpulseResponseLimitingEnabled([out, retval] BSTR* pVal);
#     [propput, id(164), helpstring("property CausalityImpulseResponseLimitingEnabled")] HRESULT CausalityImpulseResponseLimitingEnabled([in] BSTR newVal);
#     [propget, id(165), helpstring("property CausalityMaxNegativeImpulseLength")] HRESULT CausalityMaxNegativeImpulseLength([out, retval] DOUBLE* pVal);
#     [propput, id(165), helpstring("property CausalityMaxNegativeImpulseLength")] HRESULT CausalityMaxNegativeImpulseLength([in] DOUBLE newVal);
#     [propget, id(166), helpstring("property CausalityMaxImpulseLengthPossible")] HRESULT CausalityMaxImpulseLengthPossible([out, retval] DOUBLE* pVal);
#     [propput, id(166), helpstring("property CausalityMaxImpulseLengthPossible")] HRESULT CausalityMaxImpulseLengthPossible([in] DOUBLE newVal);
#     [propget, id(167), helpstring("property DutSparqPortMapping")] HRESULT DutSparqPortMapping([out, retval] BSTR* pVal);
#     [propput, id(167), helpstring("property DutSparqPortMapping")] HRESULT DutSparqPortMapping([in] BSTR newVal);
#     [propget, id(168), helpstring("property CSTCFilePath")] HRESULT CSTCFilePath([out, retval] BSTR* pVal);
#     [propput, id(168), helpstring("property CSTCFilePath")] HRESULT CSTCFilePath([in] BSTR newVal);
#     [propget, id(169), helpstring("property CSTCFileName")] HRESULT CSTCFileName([out, retval] BSTR* pVal);
#     [propput, id(169), helpstring("property CSTCFileName")] HRESULT CSTCFileName([in] BSTR newVal);
#     [propget, id(170), helpstring("property CSTCType")] HRESULT CSTCType([out, retval] BSTR* pVal);
#     [propput, id(170), helpstring("property CSTCType")] HRESULT CSTCType([in] BSTR newVal);
#     [propget, id(171), helpstring("property CSTCWaveletSmoothingEnabled")] HRESULT CSTCWaveletSmoothingEnabled([out, retval] BSTR* pVal);
#     [propput, id(171), helpstring("property CSTCWaveletSmoothingEnabled")] HRESULT CSTCWaveletSmoothingEnabled([in] BSTR newVal);
#     [propget, id(172), helpstring("property CSTCWaveletSmoothingPhasesToCheck")] HRESULT CSTCWaveletSmoothingPhasesToCheck([out, retval] LONG* pVal);
#     [propput, id(172), helpstring("property CSTCWaveletSmoothingPhasesToCheck")] HRESULT CSTCWaveletSmoothingPhasesToCheck([in] LONG newVal);
#     [propget, id(173), helpstring("property CSTCWaveletSmoothingType")] HRESULT CSTCWaveletSmoothingType([out, retval] LONG* pVal);
#     [propput, id(173), helpstring("property CSTCWaveletSmoothingType")] HRESULT CSTCWaveletSmoothingType([in] LONG newVal);
#     [propget, id(174), helpstring("property CSTCWaveletSmoothingLevels")] HRESULT CSTCWaveletSmoothingLevels([out, retval] LONG* pVal);
#     [propput, id(174), helpstring("property CSTCWaveletSmoothingLevels")] HRESULT CSTCWaveletSmoothingLevels([in] LONG newVal);
#     [propget, id(175), helpstring("property CSTCWaveletSmoothingThresholdPercentMax")] HRESULT CSTCWaveletSmoothingThresholdPercentMax([out, retval] DOUBLE* pVal);
#     [propput, id(175), helpstring("property CSTCWaveletSmoothingThresholdPercentMax")] HRESULT CSTCWaveletSmoothingThresholdPercentMax([in] DOUBLE newVal);
#     [propget, id(176), helpstring("property CSTCCausalityImpulseResponseLimitingEnabled")] HRESULT CSTCCausalityImpulseResponseLimitingEnabled([out, retval] BSTR* pVal);
#     [propput, id(176), helpstring("property CSTCCausalityImpulseResponseLimitingEnabled")] HRESULT CSTCCausalityImpulseResponseLimitingEnabled([in] BSTR newVal);
#     [propget, id(177), helpstring("property CSTCCausalityMaxImpulseLength")] HRESULT CSTCCausalityMaxImpulseLength([out, retval] DOUBLE* pVal);
#     [propput, id(177), helpstring("property CSTCCausalityMaxImpulseLength")] HRESULT CSTCCausalityMaxImpulseLength([in] DOUBLE newVal);
#     [propget, id(178), helpstring("property CSTCNumPorts")] HRESULT CSTCNumPorts([out, retval] LONG* pVal);
#     [propput, id(178), helpstring("property CSTCNumPorts")] HRESULT CSTCNumPorts([in] LONG newVal);
#     [propget, id(179), helpstring("property CSTCNumPoints")] HRESULT CSTCNumPoints([out, retval] LONG* pVal);
#     [propput, id(179), helpstring("property CSTCNumPoints")] HRESULT CSTCNumPoints([in] LONG newVal);
#     [propget, id(180), helpstring("property CSTCEndFrequency")] HRESULT CSTCEndFrequency([out, retval] DOUBLE* pVal);
#     [propput, id(180), helpstring("property CSTCEndFrequency")] HRESULT CSTCEndFrequency([in] DOUBLE newVal);
#     [id(181), helpstring("method ConvertSecondTierCalibration")] HRESULT ConvertSecondTierCalibration(void);
#     [propget, id(182), helpstring("property CalculateErrors")] HRESULT CalculateErrors([out, retval] BSTR* pVal);
#     [propput, id(182), helpstring("property CalculateErrors")] HRESULT CalculateErrors([in] BSTR newVal);
#     [propget, id(184), helpstring("property GatingEnabled")] HRESULT GatingEnabled([out, retval] BSTR* pVal);
#     [propput, id(184), helpstring("property GatingEnabled")] HRESULT GatingEnabled([in] BSTR newVal);
#     [propget, id(185), helpstring("property GatingPeeling")] HRESULT GatingPeeling([out, retval] BSTR* pVal);
#     [propput, id(185), helpstring("property GatingPeeling")] HRESULT GatingPeeling([in] BSTR newVal);
#     [propget, id(186), helpstring("property GatingZc")] HRESULT GatingZc([out, retval] BSTR* pVal);
#     [propput, id(186), helpstring("property GatingZc")] HRESULT GatingZc([in] BSTR newVal);
#     [propget, id(187), helpstring("property GatingTd")] HRESULT GatingTd([out, retval] BSTR* pVal);
#     [propput, id(187), helpstring("property GatingTd")] HRESULT GatingTd([in] BSTR newVal);
#     [propget, id(188), helpstring("property GatingLdB")] HRESULT GatingLdB([out, retval] BSTR* pVal);
#     [propput, id(188), helpstring("property GatingLdB")] HRESULT GatingLdB([in] BSTR newVal);
#     [propget, id(189), helpstring("property GatingElementsPath")] HRESULT GatingElementsPath([out, retval] BSTR* pVal);
#     [propput, id(189), helpstring("property GatingElementsPath")] HRESULT GatingElementsPath([in] BSTR newVal);
#     [propget, id(190), helpstring("property SParameterFileNameAndIndices")] HRESULT SParameterFileNameAndIndices([out, retval] BSTR* pVal);
#     [propput, id(190), helpstring("property SParameterFileNameAndIndices")] HRESULT SParameterFileNameAndIndices([in] BSTR newVal);
#     [propget, id(191), helpstring("property SParameterMeasurementFileReadStatusIsValid")] HRESULT SParameterMeasurementFileReadStatusIsValid([out, retval] BSTR* pVal);
#     [id(192), helpstring("method PutSParameterMeasurements")] HRESULT PutSParameterMeasurements(void);
#     [propget, id(195), helpstring("property WriteToFileFrequencyFormat")] HRESULT WriteToFileFrequencyFormat([out, retval] BSTR* pVal);
#     [propput, id(195), helpstring("property WriteToFileFrequencyFormat")] HRESULT WriteToFileFrequencyFormat([in] BSTR newVal);
#     [propget, id(196), helpstring("property WriteToFileSparameterFormat")] HRESULT WriteToFileSparameterFormat([out, retval] BSTR* pVal);
#     [propput, id(196), helpstring("property WriteToFileSparameterFormat")] HRESULT WriteToFileSparameterFormat([in] BSTR newVal);
#     [propget, id(197), helpstring("property WriteToFileStatus")] HRESULT WriteToFileStatus([out, retval] BSTR* pVal);
#     [propget, id(198), helpstring("property ReadTwoPortFixtures")] HRESULT ReadTwoPortFixtures([out, retval] BSTR* pVal);
#     [propput, id(198), helpstring("property ReadTwoPortFixtures")] HRESULT ReadTwoPortFixtures([in] BSTR newVal);
#     [propget, id(199), helpstring("property IsMixedModeConfiguration")] HRESULT IsMixedModeConfiguration([out, retval] BSTR* pVal);
#     [propget, id(200), helpstring("property LEDsToTurnOn")] HRESULT LEDsToTurnOn([out, retval] BSTR* pVal);
#     [id(201), helpstring("method SParameterImporterModeConversion")] HRESULT SParameterImporterModeConversion(void);
#     [propget, id(202), helpstring("property IsModeConversionStringValid")] HRESULT IsModeConversionStringValid([out, retval] BSTR* pVal);
#     [propget, id(203), helpstring("property SParameterImporterInUse")] HRESULT SParameterImporterInUse([out, retval] BSTR* pVal);
#     [propget, id(204), helpstring("property ImporterInputDutToConverterPinDefinitions")] HRESULT ImporterInputDutToConverterPinDefinitions([out, retval] BSTR* pVal);
#     [propget, id(205), helpstring("property ImporterInputUserPortDefinitions")] HRESULT ImporterInputUserPortDefinitions([out, retval] BSTR* pVal);
#     [propget, id(206), helpstring("property ImporterSerialNumber")] HRESULT ImporterSerialNumber([out, retval] BSTR* pVal);
#     [propget, id(207), helpstring("property ImporterMode")] HRESULT ImporterMode([out, retval] BSTR* pVal);
#     [propget, id(208), helpstring("property SaveStepsToFileStatus")] HRESULT SaveStepsToFileStatus([out, retval] BSTR* pVal);    
#     [propget, id(209), helpstring("property ImporterUniformFrequencySpacing")] HRESULT ImporterUniformFrequencySpacing([out, retval] BSTR* pVal);
#     [id(211), helpstring("method SParameterImporterPerformGating")] HRESULT SParameterImporterPerformGating(void);
#     
#     [propget, id(248), helpstring("property WriteToFilePutHeaderInformation")] HRESULT WriteToFilePutHeaderInformation([out, retval] BSTR* pVal);
#     [propput, id(248), helpstring("property WriteToFilePutHeaderInformation")] HRESULT WriteToFilePutHeaderInformation([in] BSTR newVal);
#     [propget, id(249), helpstring("property AcquisitionOnlyMode")] HRESULT AcquisitionOnlyMode([out, retval] BSTR* pVal);
#     [propput, id(249), helpstring("property AcquisitionOnlyMode")] HRESULT AcquisitionOnlyMode([in] BSTR newVal);
#     [propget, id(252), helpstring("property InputIsAnImpulse")] HRESULT InputIsAnImpulse([out, retval] BSTR* pVal);
#     [propput, id(252), helpstring("property InputIsAnImpulse")] HRESULT InputIsAnImpulse([in] BSTR newVal);
#     [propget, id(253), helpstring("property InputImpulseLeftWidth")] HRESULT InputImpulseLeftWidth([out, retval] DOUBLE* pVal);
#     [propput, id(253), helpstring("property InputImpulseLeftWidth")] HRESULT InputImpulseLeftWidth([in] DOUBLE newVal);
#     [propget, id(254), helpstring("property InputImpulseRightWidth")] HRESULT InputImpulseRightWidth([out, retval] DOUBLE* pVal);
#     [propput, id(254), helpstring("property InputImpulseRightWidth")] HRESULT InputImpulseRightWidth([in] DOUBLE newVal);

        numSwitchSettings = oyster.NumSwitchSettingsRequired
        for s in range(numSwitchSettings):
            oyster.SwitchSettingNumber = s
            relaySettings=oyster.RelaySettings
            measurementName = oyster.MeasurementName
            pulserString=oyster.PulsersToTurnOn
            pulserList=[int(p) for p in pulserString.split(',')]
            samplerString=oyster.SamplersToMeasure
            samplersList=[[int(sa) for sa in p.split(',')] for p in samplerString.split(';')]
            for d in range(len(pulserList)):
                drivenPort=pulserList[d]
                oyster.DrivenPort=drivenPort
                for m in range(len(samplersList[d])):
                    #print s,d,m
                    measuredPort=samplersList[d][m]
                    oyster.MeasuredPort=measuredPort
                    print relaySettings+' driven: '+str(drivenPort)+' meas: '+str(measuredPort)+' name: '+wfDict[relaySettings][drivenPort][measuredPort]['name']
                    self.PutWaveform(oyster,wfDict[relaySettings][drivenPort][measuredPort]['wf'])
        oyster.Calculate()
        #oyster.ResultFileName = self.NameForTest()
        #oyster.WriteResultToFile()
        sp = self.GetOysterSParameterResult(oyster)
        self.SParameterRegressionChecker(sp, self.NameForTest()+'.s2p')
    def testCis(self):
        return
        acquireWaveform=True
        if acquireWaveform:
            ls=si.oy.LeCroyScope('10.30.5.12')
            #ls.Command('*rst')
            ls.Command('TRMD SINGLE')
            ls.Query('*opc?')
            inr=int(ls.Query('INR?'))
            retries=0
            while (inr&1==0) and (retries < 100):
                import time
                time.sleep(0.1)
                retries=retries+1
                inr=int(ls.Query('INR?'))
            plswf=ls.ReadWaveform('C1')
            clkwf=ls.ReadWaveform('C2')
            #clkwf.WriteToFile('CISTestClk.txt')
            thwf=ls.ReadWaveform('C3')
            #thwf.WriteToFile('CISTestTh.txt')
            trendwf=ls.ReadWaveform('F3')
        else:
            clkwf=si.td.wf.Waveform().ReadFromFile('CISTestClk.txt')
            thwf=si.td.wf.Waveform().ReadFromFile('CISTestTh.txt')
        crossingTimes=[]
        clkTs=1./clkwf.td.Fs
        clkTimes=clkwf.Times()
        for k in range(1,len(clkwf)): # record crossing times
            if clkwf[k]>0. and clkwf[k-1]<=0.:
                crossingTimes.append(clkTimes[k-1]+(0.-clkwf[k-1])/(clkwf[k]-clkwf[k-1])*(clkTimes[k]-clkTimes[k-1]))
        deltas=[crossingTimes[k]-crossingTimes[k-1] for k in range(1,len(crossingTimes))]
        print min(deltas),max(deltas)
        Fss=[1/d for d in deltas]
        print mean(Fss)
        thsamples=[thwf.Measure(t) for t in crossingTimes]
        plssamples=[plswf.Measure(t) for t in crossingTimes]
        S=8192
        F=6145
        K=len(thsamples)
        reorderedSamples=[0. for _ in range(S)]
        reorderedPulserStrobe=[0. for _ in range(S)]
        averages=[0. for _ in range(S)]
        s=0
        for k in range(K):
            #reorderedSamples[s]=reorderedSamples[s]+thsamples[k]
            #averages[s]=averages[s]+1
            averages[k%S]=averages[k%S]+1
            reorderedSamples[k%S]=reorderedSamples[k%S]+thsamples[s]
            reorderedPulserStrobe[k%S]=reorderedPulserStrobe[k%S]+plssamples[s]
            s=(s+F)%S
        print min(averages)
        wfReord=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,S,204.8e9),[r/a for (r,a) in zip(reorderedSamples,averages)])
        plsReord=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,S,204.8e9),[r/a for (r,a) in zip(reorderedPulserStrobe,averages)])
        #plsReord=plsReord*si.td.f.RaisedCosineFilter(5)
        #wfReord=wfReord*si.td.f.RaisedCosineFilter(5)
        import matplotlib.pyplot as plt
        plt.clf()
        plt.title('CIS waveform')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.plot(wfReord.Times('ns'),wfReord.Values())
        plt.plot(plsReord.Times('ns'),plsReord.Values())
        plt.grid(True)
        plt.show()

        sampledElements=trendwf.Values()
        K=len(sampledElements)
        reorderedSamples=[0. for _ in range(S)]
        averages=[0. for _ in range(S)]
        s=0
        for k in range(K):
            #reorderedSamples[s]=reorderedSamples[s]+thsamples[k]
            #averages[s]=averages[s]+1
            averages[k%S]=averages[k%S]+1
            reorderedSamples[k%S]=reorderedSamples[k%S]+sampledElements[s]
            s=(s+F)%S
        print min(averages)
        wfReord=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,S,204.8e9),[r/a for (r,a) in zip(reorderedSamples,averages)])

        plt.clf()
        plt.title('CIS waveform')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.plot(wfReord.Times('ns'),wfReord.Values())
        plt.grid(True)
        plt.show()

    def testCis2(self):
        return
        ls=si.oy.LeCroyScope('10.30.5.12')
        #ls.Command('*rst')
        ls.Command('TRMD SINGLE')
        ls.Query('*opc?')
        inr=int(ls.Query('INR?'))
        retries=0
        while (inr&1==0) and (retries < 100):
            import time
            time.sleep(0.1)
            retries=retries+1
            inr=int(ls.Query('INR?'))
        trendwf=ls.ReadWaveform('F3')
        plswf=ls.ReadWaveform('F4')
        S=8192
        F=6145
        sampledElements=trendwf.Values()
        plsElements=plswf.Values()
        K=len(sampledElements)
        reorderedSamples=[0. for _ in range(S)]
        reorderedPulse=[0 for _ in range(S)]
        averages=[0. for _ in range(S)]
        s=0
        for k in range(K):
            averages[k%S]=averages[k%S]+1
            reorderedSamples[k%S]=reorderedSamples[k%S]+sampledElements[s]
            reorderedPulse[k%S]=reorderedPulse[k%S]+plsElements[s]
            s=(s+F)%S
        print min(averages)
        wfReord=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,S,204.8e9),[r/a for (r,a) in zip(reorderedSamples,averages)])
        plsReord=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,S,204.8e9),[r/a for (r,a) in zip(reorderedPulse,averages)])
        import matplotlib.pyplot as plt
        plt.clf()
        plt.title('CIS waveform')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.plot(wfReord.Times('ns'),wfReord.Values())
        plt.plot(plsReord.Times('ns'),plsReord.Values())
        plt.grid(True)
        plt.show()
    def testAAAMakeFixtures(self):
        serialNumberString='123456'
        res=self.SParameterResultsChecker('OysterFixtureShort.xml')[0]
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I1_1.s1p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I2_1.s1p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I3_1.s1p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I4_1.s1p')
        res=self.SParameterResultsChecker('OysterFixtureOpen.xml')[0]
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I1_2.s1p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I2_2.s1p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I3_2.s1p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I4_2.s1p')
        res=self.SParameterResultsChecker('OysterFixtureLoad.xml')[0]
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I1_3.s1p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I2_3.s1p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I3_3.s1p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I4_3.s1p')
        res=self.SParameterResultsChecker('OysterFixtureThru.xml')[0]
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I1_I2.s2p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I3_I4.s2p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I1_I4.s2p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I2_I3.s2p')
        res=self.SParameterResultsChecker('OysterFixtureOutput.xml')[0]
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I1_O1.s2p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I2_O2.s2p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I3_O3.s2p')
        self.SParameterRegressionChecker(res,serialNumberString+'_'+'I4_O4.s2p')

    def testZZZZRunAfterAllTestsCompleted(self):
        if TestOysterTest.usePickle:
            if not os.path.exists('simresults.p'):
                import pickle
                pickle.dump(self.simdict,open("simresults.p","wb"))

if __name__ == "__main__":
    runProfiler=False
    if runProfiler:
        import cProfile
        cProfile.run('unittest.main()','stats')
        import pstats
        p = pstats.Stats('stats')
        p.strip_dirs().sort_stats('cumulative').print_stats(30)
    else:
        unittest.main()
