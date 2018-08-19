import unittest
import SignalIntegrity as si
from TestSignalIntegrity.TestHelpers import SParameterCompareHelper,RoutineWriterTesterHelper
import os

from numpy import matrix
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
    usePickle=True
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
 
        if not SpAreEqual:
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
        si.wl.WaveletDenoiser.wavelet=si.wl.WaveletDaubechies4()

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

        #self.assertTrue(SpAreEqual,'s-parameters not equal')

        Avg=100000
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
