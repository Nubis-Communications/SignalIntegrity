# Copyright (c) 2018 Teledyne LeCroy, all rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import unittest
import SignalIntegrity as si
from TestSignalIntegrity.TestHelpers import SParameterCompareHelper,RoutineWriterTesterHelper
import os

from numpy import matrix,mean
import math
import xlrd

from SignalIntegrity.Measurement import CalKit
from SignalIntegrity.Measurement.TDR.TDRWaveformToSParameterConverter import TDRWaveformToSParameterConverter
from SignalIntegrity.Wavelets import WaveletDaubechies16
from SignalIntegrity.Wavelets.WaveletDenoiser import WaveletDenoiser
class TestSequidTest(unittest.TestCase,SParameterCompareHelper,si.test.PySIAppTestHelper,RoutineWriterTesterHelper):
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
    def __init__(self, methodName='runTest'):
        SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.PySIAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        RoutineWriterTesterHelper.__init__(self)
    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])
    def ReadSequidFileXls(self,filename):
        book=xlrd.open_workbook(filename,encoding_override='ascii')
        sheet=book.sheet_by_index(0)
        (rows,cols)=(sheet.nrows,sheet.ncols)
        times=[c.value for c in sheet.col_slice(0,2,rows-2)]
        volts=[c.value for c in sheet.col_slice(3,2,rows-2)]
        Fs=1./mean([times[k]-times[k-1] for k in range(1,len(times))])
        wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(times[0],len(times),Fs),volts)
        return wf
    def testSequidSOLOnePort(self):
        ports=1
        reflectNames=['Short','Open','Load']
        dutNames=['BPFilter','LPFilter']
        TDRWaveformToSParameterConverter.sigmaMultiple=50

        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(Length=50e-9,
            WindowReverseHalfWidthTime=3e-9,
            WindowForwardHalfWidthTime=1e-9,
            WindowRaisedCosineDuration=1e-9,
              Denoise=True,
              fd=si.fd.EvenlySpacedFrequencyList(16e9,800)
              )
        tdr.taper=False
        WaveletDenoiser.wavelet=si.wl.WaveletDaubechies4()

        for reflectName in reflectNames+dutNames:
            wf=self.ReadSequidFileXls(reflectName+'200.xls')

            rmf=tdr.RawMeasuredSParameters(wf)

            spDict[reflectName]=rmf
            spDict[reflectName+'wf']=wf
            spDict[reflectName+'denoised']=tdr.denoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
            spDict[reflectName+'incidentResponse']=tdr.IncidentFrequencyContent
            spDict[reflectName+'reflectResponse']=tdr.ReflectFrequencyContent[0]
            spDict[reflectName+'incidentExtractionWindow']=tdr.IncidentExtractionWindow
            spDict[reflectName+'reflectExtractionWindow']=tdr.ReflectExtractionWindow
            spDict[reflectName+'denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]
            self.WaveformRegressionChecker(spDict[reflectName+'wf'],self.NameForTest()+reflectName+'wf')
            self.WaveformRegressionChecker(spDict[reflectName+'denoised'],self.NameForTest()+reflectName+'denoised')
            self.WaveformRegressionChecker(spDict[reflectName+'incidentExtractionWindow'],self.NameForTest()+reflectName+'extractionWindow')
            #self.WaveformRegressionChecker(spDict[reflectName+'reflectExtractionWindow'],self.NameForTest()+reflectName+'reflectExtractionWindow')
            self.WaveformRegressionChecker(spDict[reflectName+'denoisedDerivative'],self.NameForTest()+reflectName+'denoisedDerivative')

        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        for reflectName in reflectNames:
            wf=spDict[reflectName+'wf']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
            wf=spDict[reflectName+'denoised']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName+' denoised')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(True)
        #self.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.title('derivatives')
        for reflectName in reflectNames:
            wf=spDict[reflectName+'wf'].Derivative(scale=False)
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
        xw=spDict[reflectNames[0]+'incidentExtractionWindow']
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[reflectNames[0]+'reflectExtractionWindow']
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(True)
        if plotthem: plt.show()

        plt.clf()
        plt.title('denoised derivatives')
        for reflectName in reflectNames:
            wf=spDict[reflectName+'denoisedDerivative']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
        xw=spDict[reflectNames[0]+'incidentExtractionWindow']
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[reflectNames[0]+'reflectExtractionWindow']
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(True)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 magnitude')
        for reflectName in reflectNames:
            resp=spDict[reflectName].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label=reflectName)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        plt.legend(loc='upper right')
        plt.grid(True)
        if plotthem: plt.show()

        plt.clf()
        plt.title('incident spectral density (relative to ideal unit step)')
        for reflectName in reflectNames:
            resp=spDict[reflectName+'incidentResponse']
            impulsewf=si.td.wf.Waveform(resp.td)
            impulsewf[0]=1.0
            impulsewffc=impulsewf.FrequencyContent()
            #plt.plot(impulsewffc.Frequencies('GHz'),[v+90 for v in impulsewffc.Values('dBmPerHz')],label=reflectName+' ideal')
            plt.plot(resp.Frequencies('GHz'),
                [(v-i) for (v,i) in zip(resp.Values('dBmPerHz'),impulsewffc.Values('dBmPerHz'))],label=reflectName)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB/GHz)')
        plt.legend(loc='upper right')
        plt.grid(True)
        if plotthem: plt.show()

        plt.clf()
        plt.title('reflected spectral density (relative to ideal unit step)')
        for reflectName in reflectNames:
            resp=spDict[reflectName+'reflectResponse']
            impulsewf=si.td.wf.Waveform(resp.td)
            impulsewf[0]=1.0
            impulsewffc=impulsewf.FrequencyContent()
            #plt.plot(impulsewffc.Frequencies('GHz'),[v+90 for v in impulsewffc.Values('dBmPerHz')],label=reflectName+' ideal')
            plt.plot(resp.Frequencies('GHz'),
                [(v-i) for (v,i) in zip(resp.Values('dBmPerHz'),impulsewffc.Values('dBmPerHz'))],label=reflectName)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB/GHz)')
        plt.legend(loc='upper right')
        plt.grid(True)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 phase')
        for reflectName in reflectNames:
            resp=spDict[reflectName].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('deg'),label=reflectName)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('phase (deg)')
        plt.legend(loc='upper right')
        plt.grid(True)
        if plotthem: plt.show()

        dutName='LPFilter'

        f=spDict[dutName].f()

        ck=si.m.calkit.CalibrationKit('CalKitFile.cstd',f)
        #ck.WriteStandardsToFiles('Anritsu')

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short'].FrequencyResponse(1,1),ck.shortStandard,0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open'].FrequencyResponse(1,1),ck.openStandard,0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load'].FrequencyResponse(1,1),ck.loadStandard,0,'Load1'),
            ]

        cm=si.m.cal.Calibration(ports,f,ml)
        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'sequidTDR'+str(p+1)+'.s'+str(ports*2)+'p')

        DUTCalcSp=cm.DutCalculation(spDict[dutName])

        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        return
        #DUTActualSp=si.sp.dev.TLine(f,2,40,300e-12)
        #self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s1p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-3)

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

        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')

if __name__ == "__main__":
    unittest.main()
