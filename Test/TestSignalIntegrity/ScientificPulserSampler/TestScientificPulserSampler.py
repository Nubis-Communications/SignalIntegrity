"""
TestScientificPulserSampler.py
"""

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
import SignalIntegrity.Lib as si
import os
import csv
from numpy import mean,matrix
from fractions import gcd
import math
import xlrd

class TestScientificPulserSamplerTest(unittest.TestCase,
                                      si.test.SParameterCompareHelper,
                                      si.test.SignalIntegrityAppTestHelper,
                                      si.test.RoutineWriterTesterHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    epsilon=50e-12
    usePickle=False
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    def tearDown(self):
        si.td.wf.Waveform.adaptionStrategy='SinX'
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        si.test.RoutineWriterTesterHelper.__init__(self)
    def NameForTest(self):
        return self.id().split('.')[-1][4:]
    def OutputCalFile(self,outputFileName,shortwf,openwf,loadwf,dutwf=None,baselinewf=None):
        files = [('B1','baseline'),
                 ('C1_1','short'),
                 ('C1_2','open'),
                 ('C1_3','load'),
                 ('1M11','dut')]

        outputLineList=['4002M\n','Debug\n',str(len(files))+'\n']

        for (itemName,itemFile) in files:
            outputLine=itemName

            if itemFile=='baseline': wf=baselinewf
            elif itemFile=='short': wf=shortwf
            elif itemFile=='open': wf=openwf
            elif itemFile=='load': wf=loadwf
            elif itemFile=='dut': wf=dutwf

            if not wf is None:
                waveformLength=len(wf)
                outputLine=outputLine+' '+str(waveformLength)
                for (time,ampl) in zip(wf.Times(),wf.Values()):
                    outputLine=outputLine+' '+str(time)+' '+str(ampl)
            outputLineList.append(outputLine+'\n')

        with open(outputFileName+'.cal','w') as f:
            f.writelines(outputLineList)
    def ReadScientificFileXls(self,filename,Fref,NS,DS,NP,DP,H,K):
        Fref=float(Fref)
        Fs=Fref*NS/DS
        Fp=Fref*NP/DP
        Ts=1./Fs
        Tp=1./Fp
        S=NS*DP
        P=DS*NP
        G=gcd(S,P)
        S=S/G
        P=P/G
        # S samples equals P pulses exactly
        Tseq=Tp/S
        Fseq=1./Tseq
        Ie=[(k*P)%S for k in range(S)]
        for k in range(len(Ie)):
            if Ie[k]==1:
                M=k
    
        with open(filename,'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',',quotechar='\'', quoting=csv.QUOTE_MINIMAL)
            raw = [row[1] for row in reader]
            raw = [float(ele) for ele in raw[1:]]
            mraw=mean(raw)
            raw = [ele-mraw for ele in raw]
    
        wfraw=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.0,len(raw),Fs),raw)
    
        C=len(wfraw)/S
        
        T=C*S
        
        wffolded=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0,S,Fseq),[0 for _ in range(S)])
        for t in range(T):
            ci=((t%S)*P)%S
            wffolded[ci]=wffolded[ci]+wfraw[t]/C
    
        #wffolded=si.wl.WaveletDenoiser().DenoisedWaveform(wffolded,isDerivative=False,mult=3)
        wffc=wffolded.FrequencyContent()
        f=wffc.Frequencies('GHz')
        for n in range(len(f)):
            if f[n]>100.0:
                wffc[n]=0.0
        wffiltered=wffc.Waveform()
        armed=False
        last=0.
        threshold=-0.05
        delay=0.
        for k in range(len(wffiltered)):
            if armed:
                if wffiltered[k]>last:
                    delay=wffiltered.Times()[k-1]
                    break
            elif wffiltered[k]<threshold:
                armed=True
            last=wffiltered[k]
    
        zoomedtd=si.td.wf.TimeDescriptor(delay+H,K,wffolded.TimeDescriptor().Fs)
        wftrimmerfd=zoomedtd/wffolded.TimeDescriptor()
        wftrimmer=si.td.f.WaveformTrimmer(int(wftrimmerfd.TrimLeft()),int(wftrimmerfd.TrimRight()))
        wffolded=wffolded*wftrimmer
        wffolded.td.H=H
        return wffolded
    def testScientificSOLOnePort(self):
        return
        ports=1
        reflectNames=['CalibratedShort2','CalibratedOpen','CalibratedLoad2']
        dutNames=['DUTBp1','DUTLp1']
        TDRWaveformToSParameterConverter.sigmaMultiple=50
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Length=4e-9,
            fd=si.fd.EvenlySpacedFrequencyList(40e9,400),
            Step=False,
            WindowForwardHalfWidthTime=0.2e-9,
            WindowReverseHalfWidthTime=0.0,
            WindowRaisedCosineDuration=0.05e-9,
            Inverted=True,
            Denoise=False
            )
        Fref=1e6
        NS=9999
        DS=100
        NP=100
        DP=1

        for reflectName in reflectNames+dutNames:
            wf=self.ReadScientificFileXls(reflectName+'.csv',Fref,NS,DS,NP,DP)

            rmf=tdr.RawMeasuredSParameters(wf)

            spDict[reflectName]=rmf
            spDict[reflectName+'wf']=wf
            spDict[reflectName+'denoised']=tdr.denoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
            spDict[reflectName+'incidentResponse']=tdr.IncidentFrequencyContent
            spDict[reflectName+'reflectResponse']=tdr.ReflectFrequencyContent[0]
            spDict[reflectName+'IncidentExtractionWindow']=tdr.IncidentExtractionWindow
            spDict[reflectName+'ReflectExtractionWindow']=tdr.ReflectExtractionWindow
            spDict[reflectName+'denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]

        plotthem=True
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
        plt.grid(False)
        #si.test.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.title('derivatives')
        for reflectName in reflectNames:
            wf=spDict[reflectName+'wf'].Derivative(scale=False)
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
        xw=spDict[reflectNames[0]+'IncidentExtractionWindow']
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[reflectNames[0]+'ReflectExtractionWindow']
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('denoised derivatives')
        for reflectName in reflectNames:
            wf=spDict[reflectName+'denoisedDerivative']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
        xw=spDict[reflectNames[0]+'IncidentExtractionWindow']
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[reflectNames[0]+'ReflectExtractionWindow']
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 magnitude')
        for reflectName in reflectNames:
            resp=spDict[reflectName].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label=reflectName)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        plt.legend(loc='upper right')
        plt.grid(False)
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
        plt.grid(False)
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
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 phase')
        for reflectName in reflectNames:
            resp=spDict[reflectName].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('deg'),label=reflectName)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('phase (deg)')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        dutName='DUTLp1'

        f=spDict[dutName].f()

        ck=si.m.calkit.CalibrationKit('CalKitFileFemale.cstd',f)
        #ck.WriteStandardsToFiles('Anritsu')

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['CalibratedShort2'].FrequencyResponse(1,1),ck.shortStandard,0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['CalibratedOpen'].FrequencyResponse(1,1),ck.openStandard,0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['CalibratedLoad2'].FrequencyResponse(1,1),ck.loadStandard,0,'Load1'),
            ]

        cm=si.m.cal.Calibration(ports,f,ml)
        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'ScientificTDR'+str(p+1)+'.s'+str(ports*2)+'p')

        DUTCalcSp=cm.DutCalculation(spDict[dutName])

        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        return
    
    def testScientificSOLOnePort50(self):
        return
        ports=1
        reflectNames=['CalibratedShort50_2','CalibratedOpen50_0','CalibratedLoad50_1']
        dutNames=['DUTBp50_1','DUTLp50_0']
        #TDRWaveformToSParameterConverter.sigmaMultiple=20
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Length=5e-9,
            fd=si.fd.EvenlySpacedFrequencyList(40e9,400),
            Step=False,
            WindowForwardHalfWidthTime=0.5e-9,
            WindowReverseHalfWidthTime=0.0,
            WindowRaisedCosineDuration=0.05e-9,
            Inverted=True,
            Denoise=True
            )
        Fref=1e6
        NS=9999
        DS=100
        NP=50
        DP=1

        for reflectName in reflectNames+dutNames:
            print reflectName
            wf=self.ReadScientificFileXls(reflectName+'.csv',Fref,NS,DS,NP,DP,-0.05e-9,5000)

            rmf=tdr.RawMeasuredSParameters(wf)

            spDict[reflectName]=rmf
            spDict[reflectName+'wf']=wf
            spDict[reflectName+'denoised']=tdr.denoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
            spDict[reflectName+'incidentResponse']=tdr.IncidentFrequencyContent
            spDict[reflectName+'reflectResponse']=tdr.ReflectFrequencyContent[0]
            spDict[reflectName+'incidentExtractionWindow']=tdr.IncidentExtractionWindow
            spDict[reflectName+'reflectExtractionWindow']=tdr.ReflectExtractionWindow    
            spDict[reflectName+'denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]

        plotthem=True
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        for reflectName in reflectNames+dutNames:
            wf=spDict[reflectName+'wf']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
            wf=spDict[reflectName+'denoised']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName+' denoised')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        #si.test.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.title('derivatives')
        for reflectName in reflectNames+dutNames:
            wf=spDict[reflectName+'wf'].Derivative(scale=False)
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
        xw=spDict[reflectNames[0]+'incidentExtractionWindow']
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[reflectNames[0]+'reflectExtractionWindow']
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('denoised derivatives')
        for reflectName in reflectNames+dutNames:
            wf=spDict[reflectName+'denoisedDerivative']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
        xw=spDict[reflectNames[0]+'incidentExtractionWindow']
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[reflectNames[0]+'reflectExtractionWindow']
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        wf=spDict['CalibratedLoad50_1'+'denoisedDerivative']
        xw=spDict['CalibratedLoad50_1'+'incidentExtractionWindow']
        incwf=si.td.wf.Waveform(xw.td,[v*w for (v,w) in zip(wf,xw)])
        wf.adaptionStrategy='linear'
        incwf.td.Fs=500e9
        incwf=incwf*si.td.f.WaveformTrimmer(-50000,-80000)
        incwf=incwf.Adapt(si.td.wf.TimeDescriptor(-20e-9,100000,80e9))
        self.WaveformRegressionChecker(incwf, self.NameForTest()+'_incwf.txt')
        self.WaveformRegressionChecker(incwf.Integral(scale=False), self.NameForTest()+'_stepwf.txt')

        plt.clf()
        plt.title('s11 magnitude')
        for reflectName in reflectNames:
            resp=spDict[reflectName].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label=reflectName)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        plt.legend(loc='upper right')
        plt.grid(False)
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
        plt.grid(False)
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
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 phase')
        for reflectName in reflectNames:
            resp=spDict[reflectName].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('deg'),label=reflectName)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('phase (deg)')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        dutName='DUTLp50_0'

        f=spDict[dutName].f()

        ck=si.m.calkit.CalibrationKit('CalKitFileFemale.cstd',f)
        #ck.WriteStandardsToFiles('Anritsu')
        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['CalibratedShort50_2'].FrequencyResponse(1,1),ck.shortStandard,0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['CalibratedOpen50_0'].FrequencyResponse(1,1),ck.openStandard,0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['CalibratedLoad50_1'].FrequencyResponse(1,1),ck.loadStandard,0,'Load1'),
            ]

        cm=si.m.cal.Calibration(ports,f,ml)
        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],self.NameForTest()+'.s'+str(ports*2)+'p')

        DUTCalcSp=cm.DutCalculation(spDict[dutName])

        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        
        self.OutputCalFile(self.NameForTest(),
                           spDict['CalibratedShort50_2denoisedDerivative'],
                           spDict['CalibratedOpen50_0denoisedDerivative'],
                           spDict['CalibratedLoad50_1denoisedDerivative'],
                           spDict['DUTLp50_0denoisedDerivative'])

        return
    
    def testTrombone(self):
        return
        Fref=1e6
        NS=9999
        DS=100
        NP=100
        DP=1

        waveforms=[self.ReadScientificFileXls('T'+'{:02}'.format(length)+'.csv',Fref,NS,DS,NP,DP) for length in range(0,66)]

        plotthem=True
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        delays=[]
        for wf in waveforms:
            plt.plot(wf.Times('ps'),wf.Values())
            times=wf.Times('ps')
            for k in range(len(times)):
                if times[k]>2800:
                    if (wf[k]>0.01) and (wf[k+1] < wf[k]):
                        delay=times[k]
                        delays.append(delay)
                        print delay
                        break
        plt.xlabel('time (ps)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        #si.test.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        X=[[1.,float(l)] for l in range(0,66)]
        d=[[delay] for delay in delays]
        [[b],[m]]=(matrix(X).getI()*matrix(d)).tolist()

        plt.clf()
        plt.figure(1)
        plt.title('delays')
        plt.xlabel('length (mm)')
        plt.ylabel('delay (ps)')
        plt.plot(range(0,66),delays)
        plt.plot(range(0,66),[length*m+b for length in range(0,66)])
        if plotthem: plt.show()


        print 'propagation velocity: '+str(m/2.)+' ps/mm'
    
    def testNoise(self):
        return
        Fref=1e6
        NS=9999
        DS=100
        NP=50
        DP=1

        wf=self.ReadScientificFileXls('NoiseOnly.csv',Fref,NS,DS,NP,DP)
        wffc=wf.FrequencyContent(si.fd.EvenlySpacedFrequencyList(40e9,200))

        plotthem=True
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('noise')
        plt.xlabel('frequency (GHz)')
        plt.ylabel('spectral density (dBm/GHz)')
        plt.plot(wffc.Frequencies('GHz'),[v+90 for v in wffc.Values('dBmPerHz')])
        if plotthem: plt.show()

    def testScientificSOLOnePortOnWafer(self):
        return
        ports=1
        reflectNames=[('Short','DataCollectedDuringTheWebEx/SHORT 80M_79.99M/Samples_2018_6_6_9_2_37_58'),
                      ('Open','DataCollectedDuringTheWebEx/OPEN 80M_79.99M/Samples_2018_6_6_8_59_54_123'),
                      ('Load','DataCollectedDuringTheWebEx/LOAD 80M_79.99M/Samples_2018_6_6_9_5_6_453')]
        #dutNames=['DUTBp1','DUTLp1']
        TDRWaveformToSParameterConverter.sigmaMultiple=5
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Length=6.4e-9,
            fd=si.fd.EvenlySpacedFrequencyList(40e9,400),
            Step=False,
            WindowForwardHalfWidthTime=0.35e-9,
            WindowReverseHalfWidthTime=0.05e-9,
            WindowRaisedCosineDuration=0.1e-9,
            Inverted=True,
            Denoise=True
            )
        Fref=1e6
        NS=7999
        DS=100
        NP=80
        DP=1

        for (reflectName,fileName) in reflectNames:
            wf=self.ReadScientificFileXls(fileName+'.csv',Fref,NS,DS,NP,DP,-0.4e-9,5000)

            rmf=tdr.RawMeasuredSParameters(wf)

            spDict[reflectName]=rmf
            spDict[reflectName+'wf']=wf
            spDict[reflectName+'denoised']=tdr.denoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
            spDict[reflectName+'incidentResponse']=tdr.IncidentFrequencyContent
            spDict[reflectName+'reflectResponse']=tdr.ReflectFrequencyContent[0]
            spDict[reflectName+'IncidentExtractionWindow']=tdr.IncidentExtractionWindow
            spDict[reflectName+'ReflectExtractionWindow']=tdr.ReflectExtractionWindow
            spDict[reflectName+'denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]

        wf=spDict['Load'+'denoisedDerivative']
        xw=spDict['Load'+'IncidentExtractionWindow']
        incwf=si.td.wf.Waveform(xw.td,[v*w for (v,w) in zip(wf,xw)])
        incwf=wf
        wf.adaptionStrategy='linear'
        incwf.td.Fs=500e9
        incwf=incwf*si.td.f.WaveformTrimmer(-50000,-80000)
        incwf=incwf.Adapt(si.td.wf.TimeDescriptor(-20e-9,100000,80e9))
        self.WaveformRegressionChecker(incwf, self.NameForTest()+'_incwf.txt')
        self.WaveformRegressionChecker(incwf.Integral(scale=False), self.NameForTest()+'_stepwf.txt')

        plotthem=True
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        for (reflectName,fileName) in reflectNames:
            wf=spDict[reflectName+'wf']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
            wf=spDict[reflectName+'denoised']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName+' denoised')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        #si.test.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.title('derivatives')
        for (reflectName,fileName) in reflectNames:
            wf=spDict[reflectName+'wf'].Derivative(scale=False)
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
        xw=spDict[reflectNames[0][0]+'IncidentExtractionWindow']
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[reflectNames[0][0]+'ReflectExtractionWindow']
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('denoised derivatives')
        for (reflectName,fileName) in reflectNames:
            wf=spDict[reflectName+'denoisedDerivative']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
        xw=spDict[reflectNames[0][0]+'IncidentExtractionWindow']
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[reflectNames[0][0]+'ReflectExtractionWindow']
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 magnitude')
        for (reflectName,fileName) in reflectNames:
            resp=spDict[reflectName].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label=reflectName)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('incident spectral density (relative to ideal unit step)')
        for (reflectName,fileName) in reflectNames:
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
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('reflected spectral density (relative to ideal unit step)')
        for (reflectName,fileName) in reflectNames:
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
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 phase')
        for (reflectName,fileName) in reflectNames:
            resp=spDict[reflectName].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('deg'),label=reflectName)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('phase (deg)')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        #dutName='DUTLp1'

        f=spDict['Short'].f()

        ck=si.m.calkit.CalibrationKit('CalKitFileFemale.cstd',f)
        #ck.WriteStandardsToFiles('Anritsu')

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short'].FrequencyResponse(1,1),ck.shortStandard,0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open'].FrequencyResponse(1,1),ck.openStandard,0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load'].FrequencyResponse(1,1),ck.loadStandard,0,'Load1'),
            ]

        cm=si.m.cal.Calibration(ports,f,ml)
        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],self.NameForTest()+'.s'+str(ports*2)+'p')

        self.OutputCalFile(self.NameForTest(), spDict['ShortdenoisedDerivative'], spDict['OpendenoisedDerivative'], spDict['LoaddenoisedDerivative'])
        #DUTCalcSp=cm.DutCalculation(spDict[dutName])

        #self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        return

    def testScientificSOLOnePortOnWaferOffset(self):
        return
        ports=1
        reflectNames=[('Short','DataCollectedDuringTheWebEx/SHORT 80M_79.99M/Samples_2018_6_6_9_2_37_58'),
                      ('Open','DataCollectedDuringTheWebEx/OPEN 80M_79.99M/Samples_2018_6_6_8_59_54_123'),
                      ('Load','DataCollectedDuringTheWebEx/LOAD 80M_79.99M/Samples_2018_6_6_9_5_6_453')]
        #dutNames=['DUTBp1','DUTLp1']


        TDRWaveformToSParameterConverter.sigmaMultiple=5
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Length=6.4e-9,
            fd=si.fd.EvenlySpacedFrequencyList(40e9,400),
            Step=False,
            WindowForwardHalfWidthTime=0.1e-9,
            WindowReverseHalfWidthTime=0.05e-9,
            WindowRaisedCosineDuration=0.1e-9,
            Inverted=True,
            Denoise=True
            )
        Fref=1e6
        NS=7999
        DS=100
        NP=80
        DP=1

        (reflectName,fileName)=reflectNames[2]
        wf=self.ReadScientificFileXls(fileName+'.csv',Fref,NS,DS,NP,DP,-0.4e-9,5000)
        #wf=wf.Derivative(scale=False)
        rmf=tdr.RawMeasuredSParameters(wf)
        loadreflectwf=si.td.wf.Waveform(tdr.denoisedDerivatives[0].td,[x*w for (x,w) in zip(tdr.denoisedDerivatives[0],tdr.ReflectExtractionWindow)])
        offset=-sum(loadreflectwf)/len(loadreflectwf)
        #offset=.1

        for (reflectName,fileName) in reflectNames:
            wf=self.ReadScientificFileXls(fileName+'.csv',Fref,NS,DS,NP,DP,-0.4e-9,5000)
            #wf=wf.Derivative(scale=False)
            wf=wf-offset

            rmf=tdr.RawMeasuredSParameters(wf)

            spDict[reflectName]=rmf
            spDict[reflectName+'wf']=wf
            spDict[reflectName+'denoised']=tdr.denoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
            spDict[reflectName+'incidentResponse']=tdr.IncidentFrequencyContent
            spDict[reflectName+'reflectResponse']=tdr.ReflectFrequencyContent[0]
            spDict[reflectName+'IncidentExtractionWindow']=tdr.IncidentExtractionWindow
            spDict[reflectName+'ReflectExtractionWindow']=tdr.ReflectExtractionWindow
            spDict[reflectName+'denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]

        plotthem=True
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        for (reflectName,fileName) in reflectNames:
            wf=spDict[reflectName+'wf']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
            wf=spDict[reflectName+'denoised']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName+' denoised')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        #si.test.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.title('derivatives')
        for (reflectName,fileName) in reflectNames:
            wf=spDict[reflectName+'wf'].Derivative(scale=False)
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
        xw=spDict[reflectNames[0][0]+'IncidentExtractionWindow']*0.1
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[reflectNames[0][0]+'ReflectExtractionWindow']*0.1
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('denoised derivatives')
        for (reflectName,fileName) in reflectNames:
            wf=spDict[reflectName+'denoisedDerivative']
            plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
        xw=spDict[reflectNames[0][0]+'IncidentExtractionWindow']*0.1
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[reflectNames[0][0]+'ReflectExtractionWindow']*0.1
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 magnitude')
        for (reflectName,fileName) in reflectNames:
            resp=spDict[reflectName].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label=reflectName)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('incident spectral density (relative to ideal unit step)')
        for (reflectName,fileName) in reflectNames:
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
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('reflected spectral density (relative to ideal unit step)')
        for (reflectName,fileName) in reflectNames:
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
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 phase')
        for (reflectName,fileName) in reflectNames:
            resp=spDict[reflectName].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('deg'),label=reflectName)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('phase (deg)')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        #dutName='DUTLp1'

        f=spDict['Short'].f()

        ck=si.m.calkit.CalibrationKit('CalKitFileFemale.cstd',f)
        #ck.WriteStandardsToFiles('Anritsu')

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short'].FrequencyResponse(1,1),ck.shortStandard,0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open'].FrequencyResponse(1,1),ck.openStandard,0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load'].FrequencyResponse(1,1),ck.loadStandard,0,'Load1'),
            ]

        cm=si.m.cal.Calibration(ports,f,ml)
        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'ScientificTDROnWaferOffset'+str(p+1)+'.s'+str(ports*2)+'p')

        self.OutputCalFile('ScientificTDROnWaferOffset', spDict['ShortdenoisedDerivative'], spDict['OpendenoisedDerivative'], spDict['LoaddenoisedDerivative'])
        #DUTCalcSp=cm.DutCalculation(spDict[dutName])

        #self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        return
    def testScientificPulserSamplerScopeWf(self):
        return
        wfList=[('M1--Trace--00002.txt','Short'),
                ('M2--Trace--00002.txt','Open'),
                ('M3--Trace--00002.txt','Load'),
                ('M4--Trace--00002.txt','LpFilt'),
                ('M5--Trace--00002.txt','BpFilt')]

        wfDict=dict()
        for (filename,meas) in wfList:
            with open(filename) as f:
                v=[float(amp) for amp in f.readlines()[3:]]
            wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(-2e-9,len(v),100000e9),v)*si.td.f.WaveformDecimator(100)
            wf=wf-wf.Measure(-250e-12)
            wfDict[meas]=wf
        plotthem=True
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        for (filename,meas) in wfList:
            wf=wfDict[meas]
            plt.plot(wf.Times('ns'),wf.Values(),label=meas)
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        #si.test.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        TDRWaveformToSParameterConverter.sigmaMultiple=5
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Length=6e-9,
            fd=si.fd.EvenlySpacedFrequencyList(40e9,4000),
            Step=False,
            WindowForwardHalfWidthTime=0.15e-9,
            WindowReverseHalfWidthTime=0.05e-9,
            WindowRaisedCosineDuration=0.1e-9,
            Inverted=True,
            Denoise=True
            )

        for (filename,meas) in wfList:
            wf=wfDict[meas]

            rmf=tdr.RawMeasuredSParameters(wf)

            spDict[meas]=rmf
            spDict[meas+'wf']=wf
            spDict[meas+'denoised']=tdr.denoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
            spDict[meas+'incidentResponse']=tdr.IncidentFrequencyContent
            spDict[meas+'reflectResponse']=tdr.ReflectFrequencyContent[0]
            spDict[meas+'IncidentExtractionWindow']=tdr.IncidentExtractionWindow
            spDict[meas+'ReflectExtractionWindow']=tdr.ReflectExtractionWindow
            spDict[meas+'denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]

        plotthem=True
        import matplotlib.pyplot as plt

        plt.clf()
        plt.title('denoised derivatives')
        for (filename,meas) in wfList:
            wf=spDict[meas+'denoisedDerivative']
            plt.plot(wf.Times('ns'),wf.Values(),label=meas)
        xw=spDict[wfList[0][1]+'IncidentExtractionWindow']*.1
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[wfList[0][1]+'ReflectExtractionWindow']*.1
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 magnitude')
        for (filename,meas) in wfList:
            resp=spDict[meas].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('incident spectral density (relative to ideal unit step)')
        for (filename,meas) in wfList:
            resp=spDict[meas+'incidentResponse']
            impulsewf=si.td.wf.Waveform(resp.td)
            impulsewf[0]=1.0
            impulsewffc=impulsewf.FrequencyContent()
            #plt.plot(impulsewffc.Frequencies('GHz'),[v+90 for v in impulsewffc.Values('dBmPerHz')],label=reflectName+' ideal')
            plt.plot(resp.Frequencies('GHz'),
                [(v-i) for (v,i) in zip(resp.Values('dBmPerHz'),impulsewffc.Values('dBmPerHz'))],label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB/GHz)')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('reflected spectral density (relative to ideal unit step)')
        for (filename,meas) in wfList:
            resp=spDict[meas+'reflectResponse']
            impulsewf=si.td.wf.Waveform(resp.td)
            impulsewf[0]=1.0
            impulsewffc=impulsewf.FrequencyContent()
            #plt.plot(impulsewffc.Frequencies('GHz'),[v+90 for v in impulsewffc.Values('dBmPerHz')],label=reflectName+' ideal')
            plt.plot(resp.Frequencies('GHz'),
                [(v-i) for (v,i) in zip(resp.Values('dBmPerHz'),impulsewffc.Values('dBmPerHz'))],label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB/GHz)')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 phase')
        for (filename,meas) in wfList:
            resp=spDict[meas].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('deg'),label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('phase (deg)')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        #dutName='DUTLp1'

        f=spDict['Short'].f()

        ck=si.m.calkit.CalibrationKit('CalKitFileFemale.cstd',f)
        #ck.WriteStandardsToFiles('Anritsu')

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short'].FrequencyResponse(1,1),ck.shortStandard,0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open'].FrequencyResponse(1,1),ck.openStandard,0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load'].FrequencyResponse(1,1),ck.loadStandard,0,'Load1'),
            ]

        ports=1
        cm=si.m.cal.Calibration(ports,f,ml)

        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'ScientificTDRScope'+str(p+1)+'.s'+str(ports*2)+'p')

        self.OutputCalFile('ScientificTDRScope', spDict['ShortdenoisedDerivative'], spDict['OpendenoisedDerivative'], spDict['LoaddenoisedDerivative'])

        dutName='LpFilt'
        DUTCalcSp=cm.DutCalculation(spDict[dutName])

        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_'+dutName+'_Calc.s1p')

        dutName='BpFilt'
        DUTCalcSp=cm.DutCalculation(spDict[dutName])

        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_'+dutName+'_Calc.s1p')

    def testScientificPulserSamplerScopeWfOnWafer(self):
        return
        wfList=[('.\Measurements\M1--Short--00000.txt','Short'),
                ('.\Measurements\M2--Open--00000.txt','Open'),
                ('.\Measurements\M3--Load--00000.txt','Load')]

        wfDict=dict()
        for (filename,meas) in wfList:
            with open(filename) as f:
                v=[float(amp) for amp in f.readlines()[3:]]
            wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(-0.97e-9,len(v),100000e9),v)*si.td.f.WaveformDecimator(100)
            wf=wf-wf.Measure(-0.5e-9)
            wfDict[meas]=wf
        plotthem=True
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        for (filename,meas) in wfList:
            wf=wfDict[meas]
            plt.plot(wf.Times('ns'),wf.Values(),label=meas)
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        #si.test.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        TDRWaveformToSParameterConverter.sigmaMultiple=400
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Length=5e-9,
            fd=si.fd.EvenlySpacedFrequencyList(50e9,5000),
            Step=False,
            WindowForwardHalfWidthTime=0.4e-9,
            WindowReverseHalfWidthTime=0.05e-9,
            WindowRaisedCosineDuration=0.05e-9,
            Inverted=False,
            Denoise=True
            )

        for (filename,meas) in wfList:
            wf=wfDict[meas]

            rmf=tdr.RawMeasuredSParameters(wf)

            spDict[meas]=rmf
            spDict[meas+'wf']=wf
            spDict[meas+'denoised']=tdr.denoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
            spDict[meas+'incidentResponse']=tdr.IncidentFrequencyContent
            spDict[meas+'reflectResponse']=tdr.ReflectFrequencyContent[0]
            spDict[meas+'IncidentExtractionWindow']=tdr.IncidentExtractionWindow
            spDict[meas+'ReflectExtractionWindow']=tdr.ReflectExtractionWindow
            spDict[meas+'denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]

        plotthem=True
        import matplotlib.pyplot as plt

        plt.clf()
        plt.title('denoised derivatives')
        for (filename,meas) in wfList:
            wf=spDict[meas+'denoisedDerivative']
            plt.plot(wf.Times('ns'),wf.Values(),label=meas)
        xw=spDict[wfList[0][1]+'IncidentExtractionWindow']*.4
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[wfList[0][1]+'ReflectExtractionWindow']*.4
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 magnitude')
        for (filename,meas) in wfList:
            resp=spDict[meas].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('incident spectral density (relative to ideal unit step)')
        for (filename,meas) in wfList:
            resp=spDict[meas+'incidentResponse']
            impulsewf=si.td.wf.Waveform(resp.td)
            impulsewf[0]=1.0
            impulsewffc=impulsewf.FrequencyContent()
            #plt.plot(impulsewffc.Frequencies('GHz'),[v+90 for v in impulsewffc.Values('dBmPerHz')],label=reflectName+' ideal')
            plt.plot(resp.Frequencies('GHz'),
                [(v-i) for (v,i) in zip(resp.Values('dBmPerHz'),impulsewffc.Values('dBmPerHz'))],label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB/GHz)')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('reflected spectral density (relative to ideal unit step)')
        for (filename,meas) in wfList:
            resp=spDict[meas+'reflectResponse']
            impulsewf=si.td.wf.Waveform(resp.td)
            impulsewf[0]=1.0
            impulsewffc=impulsewf.FrequencyContent()
            #plt.plot(impulsewffc.Frequencies('GHz'),[v+90 for v in impulsewffc.Values('dBmPerHz')],label=reflectName+' ideal')
            plt.plot(resp.Frequencies('GHz'),
                [(v-i) for (v,i) in zip(resp.Values('dBmPerHz'),impulsewffc.Values('dBmPerHz'))],label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB/GHz)')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 phase')
        for (filename,meas) in wfList:
            resp=spDict[meas].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('deg'),label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('phase (deg)')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        #dutName='DUTLp1'

        f=spDict['Short'].f()

        ck=si.m.calkit.CalibrationKit('CalKitFileFemale.cstd',f)
        #ck.WriteStandardsToFiles('Anritsu')

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short'].FrequencyResponse(1,1),ck.shortStandard,0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open'].FrequencyResponse(1,1),ck.openStandard,0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load'].FrequencyResponse(1,1),ck.loadStandard,0,'Load1'),
            ]

        ports=1
        cm=si.m.cal.Calibration(ports,f,ml)

        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'ScientificTDRScopeOnWafer'+str(p+1)+'.s'+str(ports*2)+'p')

        self.OutputCalFile('ScientificTDRScopeOnWafer', spDict['ShortdenoisedDerivative'], spDict['OpendenoisedDerivative'], spDict['LoaddenoisedDerivative'])

    def testScientificPulserSamplerScopeWfOnWafer2(self):
        wfList=[('Measurements2/M1--Short--00000.txt','Short'),
                ('Measurements2/M2--Open--00000.txt','Open'),
                ('Measurements2/M3--Load--00000.txt','Load')]
        wfDict=dict()
        for (filename,meas) in wfList:
            with open(filename) as f:
                v=[float(amp) for amp in f.readlines()[3:]]
            wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(-0.97e-9,len(v),100000e9),v)*si.td.f.WaveformDecimator(100)
            sum=0.0
            avg=0
            times=wf.Times()
            for k in range(len(wf)):
                if times[k]<-0.1e-9:
                    sum=sum+wf[k]
                    avg=avg+1
            mean=sum/avg
            wf=wf-mean+0.00003
            wfDict[meas]=wf

        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        for (filename,meas) in wfList:
            wf=wfDict[meas]
            plt.plot(wf.Times('ns'),wf.Values(),label=meas)
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        si.m.tdr.TDRWaveformToSParameterConverter.sigmaMultiple=400
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Length=5e-9,
            fd=si.fd.EvenlySpacedFrequencyList(50e9,500),
            Step=False,
            WindowForwardHalfWidthTime=0.4e-9,
            WindowReverseHalfWidthTime=0.05e-9,
            WindowRaisedCosineDuration=0.05e-9,
            Inverted=False,
            Denoise=True
            )

        for (filename,meas) in wfList:
            wf=wfDict[meas]

            rmf=tdr.RawMeasuredSParameters(wf)

            spDict[meas]=rmf
            spDict[meas+'wf']=wf
            spDict[meas+'denoised']=tdr.TrimmedDenoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
            spDict[meas+'incidentResponse']=tdr.IncidentFrequencyContent
            spDict[meas+'reflectResponse']=tdr.ReflectFrequencyContent[0]
            spDict[meas+'IncidentExtractionWindow']=tdr.IncidentExtractionWindow
            spDict[meas+'ReflectExtractionWindow']=tdr.ReflectExtractionWindow
            spDict[meas+'denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]

        wf=spDict['Load'+'denoisedDerivative']
        xw=spDict['Load'+'IncidentExtractionWindow']
        incwf=si.td.wf.Waveform(xw.td,[v*w for (v,w) in zip(wf,xw)])
        wf.adaptionStrategy='linear'
        incwf=incwf*si.td.f.WaveformTrimmer(-50000,-200000)
        incwf=incwf.Adapt(si.td.wf.TimeDescriptor(-60e-9,150000,800e9))
        self.WaveformRegressionChecker(incwf, self.NameForTest()+'_incwf.txt')
        self.WaveformRegressionChecker(incwf.Integral(scale=False), self.NameForTest()+'_stepwf.txt')

        plt.clf()
        plt.figure(1)
        plt.title('tdr steps')
        for (filename,meas) in wfList:
            wf=spDict[meas+'denoised']
            wf=wf*si.td.f.WaveformDecimator(4)
            plt.plot(wf.Times('ns'),wf.Values(),label=meas+' step')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper left')
        plt.grid(False)
        plt.xlim(-1.2,4)
        plt.ylim(-1,8)
        si.test.PlotTikZ(self.NameForTest()+'_step.tex', plt)
        if plotthem: plt.show()


        plt.clf()
        plt.title('denoised derivatives')
        for (filename,meas) in wfList:
            wf=spDict[meas+'denoisedDerivative']
            wf=wf*si.td.f.WaveformDecimator(4)
            plt.plot(wf.Times('ns'),wf.Values(),label=meas)
        xw=spDict[wfList[0][1]+'IncidentExtractionWindow']*.4*si.td.f.WaveformDecimator(4)
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[wfList[0][1]+'ReflectExtractionWindow']*.4*si.td.f.WaveformDecimator(4)
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        plt.xlim(-0.1,1.4)
        plt.ylim(-0.3,0.5)
        si.test.PlotTikZ(self.NameForTest()+'_deriv.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 magnitude')
        for (filename,meas) in wfList:
            resp=spDict[meas].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        plt.legend(loc='lower right')
        plt.grid(False)
        plt.xlim(0,50)
        plt.ylim(-70,10)
        si.test.PlotTikZ(self.NameForTest()+'_s11.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.title('incident spectral density (relative to ideal unit step)')
        for (filename,meas) in wfList:
            resp=spDict[meas+'incidentResponse']
            impulsewf=si.td.wf.Waveform(resp.td)
            impulsewf[0]=1.0
            impulsewffc=impulsewf.FrequencyContent()
            #plt.plot(impulsewffc.Frequencies('GHz'),[v+90 for v in impulsewffc.Values('dBmPerHz')],label=reflectName+' ideal')
            plt.plot(resp.Frequencies('GHz'),
                [(v-i) for (v,i) in zip(resp.Values('dBmPerHz'),impulsewffc.Values('dBmPerHz'))],label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB/GHz)')
        plt.legend(loc='upper right')
        plt.grid(False)
        plt.xlim(0,50)
        plt.ylim(0,14)
        si.test.PlotTikZ(self.NameForTest()+'_incident.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.title('reflected spectral density (relative to ideal unit step)')
        for (filename,meas) in wfList:
            resp=spDict[meas+'reflectResponse']
            impulsewf=si.td.wf.Waveform(resp.td)
            impulsewf[0]=1.0
            impulsewffc=impulsewf.FrequencyContent()
            #plt.plot(impulsewffc.Frequencies('GHz'),[v+90 for v in impulsewffc.Values('dBmPerHz')],label=reflectName+' ideal')
            plt.plot(resp.Frequencies('GHz'),
                [(v-i) for (v,i) in zip(resp.Values('dBmPerHz'),impulsewffc.Values('dBmPerHz'))],label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB/GHz)')
        plt.legend(loc='lower right')
        plt.grid(False)
        plt.xlim(0,50)
        plt.ylim(-60,20)
        si.test.PlotTikZ(self.NameForTest()+'_reflect.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 phase')
        for (filename,meas) in wfList:
            resp=spDict[meas].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('deg'),label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('phase (deg)')
        plt.legend(loc='upper right')
        plt.grid(False)
        plt.xlim(0,50)
        plt.ylim(-200,200)
        si.test.PlotTikZ(self.NameForTest()+'_phase.tex', plt)
        if plotthem: plt.show()

        #dutName='DUTLp1'

        f=spDict['Short'].f()

        ck=si.m.calkit.CalibrationKit('CalKitFileFemale.cstd',f)
        #ck.WriteStandardsToFiles('Anritsu')

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short'].FrequencyResponse(1,1),ck.shortStandard,0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open'].FrequencyResponse(1,1),ck.openStandard,0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load'].FrequencyResponse(1,1),ck.loadStandard,0,'Load1'),
            ]

        ports=1
        cm=si.m.cal.Calibration(ports,f,ml)

        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],self.NameForTest()+'.s'+str(ports*2)+'p')

        self.OutputCalFile(self.NameForTest(), spDict['ShortdenoisedDerivative'], spDict['OpendenoisedDerivative'], spDict['LoaddenoisedDerivative'])

    def testScientificPulserSamplerScopeWfSocketed(self):
        pass
        wfList=[('MeasurementsSocketed/M1--Short--00000.txt','Short'),
                ('MeasurementsSocketed/M2--Open--00000.txt','Open'),
                ('MeasurementsSocketed/M3--Load--00000.txt','Load')]

        wfDict=dict()
        for (filename,meas) in wfList:
            with open(filename) as f:
                v=[float(amp) for amp in f.readlines()[3:]]
            wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(-1.86e-9,len(v),100000e9),v)*si.td.f.WaveformDecimator(100)
            sum=0.0
            avg=0
            times=wf.Times()
            for k in range(len(wf)):
                if times[k]<-0.1e-9:
                    sum=sum+wf[k]
                    avg=avg+1
            mean=sum/avg
            wf=wf-mean+0.00003
            wfDict[meas]=wf
        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        for (filename,meas) in wfList:
            wf=wfDict[meas]
            wf=wf*si.td.f.WaveformDecimator(10)
            plt.plot(wf.Times('ns'),wf.Values(),label=meas)
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        #si.test.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        si.m.tdr.TDRWaveformToSParameterConverter.sigmaMultiple=400
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Length=6e-9,
            fd=si.fd.EvenlySpacedFrequencyList(40e9,400),
            Step=False,
            WindowForwardHalfWidthTime=0.4e-9,
            WindowReverseHalfWidthTime=0.05e-9,
            WindowRaisedCosineDuration=0.05e-9,
            Inverted=True,
            Denoise=True
            )

        for (filename,meas) in wfList:
            wf=wfDict[meas]

            rmf=tdr.RawMeasuredSParameters(wf)

            spDict[meas]=rmf
            spDict[meas+'wf']=wf
            spDict[meas+'denoised']=tdr.TrimmedDenoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
            spDict[meas+'incidentResponse']=tdr.IncidentFrequencyContent
            spDict[meas+'reflectResponse']=tdr.ReflectFrequencyContent[0]
            spDict[meas+'IncidentExtractionWindow']=tdr.IncidentExtractionWindow
            spDict[meas+'ReflectExtractionWindow']=tdr.ReflectExtractionWindow
            spDict[meas+'denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]

        wf=spDict['Load'+'denoisedDerivative']
        xw=spDict['Load'+'IncidentExtractionWindow']
        incwf=si.td.wf.Waveform(xw.td,[v*w for (v,w) in zip(wf,xw)])
        wf.adaptionStrategy='linear'
        incwf=incwf*si.td.f.WaveformTrimmer(-50000,-200000)
        incwf=incwf.Adapt(si.td.wf.TimeDescriptor(-50e-9,150000,800e9))
        self.WaveformRegressionChecker(incwf, self.NameForTest()+'_incwf.txt')
        self.WaveformRegressionChecker(incwf.Integral(scale=False), self.NameForTest()+'_stepwf.txt')

        plotthem=False
        import matplotlib.pyplot as plt

        plt.clf()
        plt.figure(1)
        plt.title('tdr steps')
        for (filename,meas) in wfList:
            wf=spDict[meas+'denoised']
            wf=wf*si.td.f.WaveformDecimator(10)
            plt.plot(wf.Times('ns'),wf.Values(),label=meas+' denoised step')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper left')
        plt.grid(False)
        plt.xlim(-1,2.5)
        plt.ylim(-1,8)
        si.test.PlotTikZ(self.NameForTest()+'_step.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.title('denoised derivatives')
        for (filename,meas) in wfList:
            wf=spDict[meas+'denoisedDerivative']
            wf=wf*si.td.f.WaveformDecimator(10)
            plt.plot(wf.Times('ns'),wf.Values(),label=meas)
        xw=spDict[wfList[0][1]+'IncidentExtractionWindow']*.25*si.td.f.WaveformDecimator(10)
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[wfList[0][1]+'ReflectExtractionWindow']*.25*si.td.f.WaveformDecimator(10)
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        plt.xlim(-0.3333,4.13)
        plt.ylim(-0.1,0.3)
        si.test.PlotTikZ(self.NameForTest()+'_deriv.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 magnitude')
        for (filename,meas) in wfList:
            resp=spDict[meas].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        plt.legend(loc='upper right')
        plt.grid(False)
        plt.xlim(0,40)
        plt.ylim(-70,10)
        si.test.PlotTikZ(self.NameForTest()+'_s11.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.title('incident spectral density (relative to ideal unit step)')
        for (filename,meas) in wfList:
            resp=spDict[meas+'incidentResponse']
            impulsewf=si.td.wf.Waveform(resp.td)
            impulsewf[0]=1.0
            impulsewffc=impulsewf.FrequencyContent()
            #plt.plot(impulsewffc.Frequencies('GHz'),[v+90 for v in impulsewffc.Values('dBmPerHz')],label=reflectName+' ideal')
            plt.plot(resp.Frequencies('GHz'),
                [(v-i) for (v,i) in zip(resp.Values('dBmPerHz'),impulsewffc.Values('dBmPerHz'))],label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB/GHz)')
        plt.legend(loc='upper right')
        plt.xlim(0,40)
        plt.ylim(0,12)
        si.test.PlotTikZ(self.NameForTest()+'_incident.tex', plt)
        plt.grid(False)
        if plotthem: plt.show()

        plt.clf()
        plt.title('reflected spectral density (relative to ideal unit step)')
        for (filename,meas) in wfList:
            resp=spDict[meas+'reflectResponse']
            impulsewf=si.td.wf.Waveform(resp.td)
            impulsewf[0]=1.0
            impulsewffc=impulsewf.FrequencyContent()
            #plt.plot(impulsewffc.Frequencies('GHz'),[v+90 for v in impulsewffc.Values('dBmPerHz')],label=reflectName+' ideal')
            plt.plot(resp.Frequencies('GHz'),
                [(v-i) for (v,i) in zip(resp.Values('dBmPerHz'),impulsewffc.Values('dBmPerHz'))],label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB/GHz)')
        plt.legend(loc='upper right')
        plt.grid(False)
        plt.xlim(0,40)
        plt.ylim(-60,10)
        si.test.PlotTikZ(self.NameForTest()+'_reflect.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 phase')
        for (filename,meas) in wfList:
            resp=spDict[meas].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('deg'),label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('phase (deg)')
        plt.legend(loc='upper right')
        plt.grid(False)
        plt.xlim(0,40)
        plt.ylim(-200,200)
        si.test.PlotTikZ(self.NameForTest()+'_phase.tex', plt)
        if plotthem: plt.show()

        #dutName='DUTLp1'

        f=spDict['Short'].f()

        ck=si.m.calkit.CalibrationKit('CalKitFileFemale.cstd',f)
        #ck.WriteStandardsToFiles('Anritsu')

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short'].FrequencyResponse(1,1),ck.shortStandard,0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open'].FrequencyResponse(1,1),ck.openStandard,0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load'].FrequencyResponse(1,1),ck.loadStandard,0,'Load1'),
            ]

        ports=1
        cm=si.m.cal.Calibration(ports,f,ml)

        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],self.NameForTest()+'.s'+str(ports*2)+'p')

        self.OutputCalFile(self.NameForTest(), spDict['ShortdenoisedDerivative'], spDict['OpendenoisedDerivative'], spDict['LoaddenoisedDerivative'])

    def testScientificPulserSamplerScopeWfSocketedPerfect(self):
        pass
        wfList=[('MeasurementsSocketed/M1--Short--00000.txt','Short'),
                ('MeasurementsSocketed/M2--Open--00000.txt','Open'),
                ('MeasurementsSocketed/M3--Load--00000.txt','Load')]

        wfDict=dict()
        for (filename,meas) in wfList:
            with open(filename) as f:
                v=[float(amp) for amp in f.readlines()[3:]]
            wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(-1.86e-9,len(v),100000e9),v)*si.td.f.WaveformDecimator(100)
            sum=0.0
            avg=0
            times=wf.Times()
            for k in range(len(wf)):
                if times[k]<-0.1e-9:
                    sum=sum+wf[k]
                    avg=avg+1
            mean=sum/avg
            wf=wf-mean+0.00003
            for k in range(len(wf)):
                if (times[k]>= 0.05e-9) and (times[k]<0.114e-9):
                    wf[k]=0.0
            wfDict[meas]=wf

        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        for (filename,meas) in wfList:
            wf=wfDict[meas]
            plt.plot(wf.Times('ns'),wf.Values(),label=meas)
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        if plotthem: plt.show()

        si.m.tdr.TDRWaveformToSParameterConverter.sigmaMultiple=400
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Length=2.75e-9,
            fd=si.fd.EvenlySpacedFrequencyList(40e9,400),
            Step=False,
            WindowForwardHalfWidthTime=0.4e-9,
            WindowReverseHalfWidthTime=0.05e-9,
            WindowRaisedCosineDuration=0.05e-9,
            Inverted=True,
            Denoise=True
            )

        for (filename,meas) in wfList:
            wf=wfDict[meas]

            rmf=tdr.RawMeasuredSParameters(wf)

            spDict[meas]=rmf
            spDict[meas+'wf']=wf
            spDict[meas+'denoised']=tdr.TrimmedDenoisedDerivatives[0].Integral(scale=False,c=wf[0],addPoint=True)
            spDict[meas+'incidentResponse']=tdr.IncidentFrequencyContent
            spDict[meas+'reflectResponse']=tdr.ReflectFrequencyContent[0]
            spDict[meas+'IncidentExtractionWindow']=tdr.IncidentExtractionWindow
            spDict[meas+'ReflectExtractionWindow']=tdr.ReflectExtractionWindow
            spDict[meas+'denoisedDerivative']=tdr.TrimmedDenoisedDerivatives[0]

        wf=spDict['Load'+'denoisedDerivative']
        xw=spDict['Load'+'IncidentExtractionWindow']
        incwf=si.td.wf.Waveform(xw.td,[v*w for (v,w) in zip(wf,xw)])
        wf.adaptionStrategy='linear'
        incwf=incwf*si.td.f.WaveformTrimmer(-50000,-200000)
        incwf=incwf.Adapt(si.td.wf.TimeDescriptor(-20e-9,100000,800e9))
        self.WaveformRegressionChecker(incwf, self.NameForTest()+'_incwf.txt')
        self.WaveformRegressionChecker(incwf.Integral(scale=False), self.NameForTest()+'_stepwf.txt')

        plt.clf()
        plt.figure(1)
        plt.title('tdr steps')
        for (filename,meas) in wfList:
            wf=spDict[meas+'denoised']
            wf=wf*si.td.f.WaveformDecimator(4)
            plt.plot(wf.Times('ns'),wf.Values(),label=meas+' denoised step')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper left')
        plt.grid(False)
        plt.xlim(-.1,0.9)
        plt.ylim(-1,7)
        si.test.PlotTikZ(self.NameForTest()+'_step.tex', plt)
        if plotthem: plt.show()


        plt.clf()
        plt.title('denoised derivatives')
        for (filename,meas) in wfList:
            wf=spDict[meas+'denoisedDerivative']
            wf=wf*si.td.f.WaveformDecimator(4)
            plt.plot(wf.Times('ns'),wf.Values(),label=meas)
        xw=spDict[wfList[0][1]+'IncidentExtractionWindow']*.25*si.td.f.WaveformDecimator(4)
        plt.plot(xw.Times('ns'),xw.Values(),label='incident extractor')
        rxw=spDict[wfList[0][1]+'ReflectExtractionWindow']*.25*si.td.f.WaveformDecimator(4)
        plt.plot(rxw.Times('ns'),rxw.Values(),label='reflect extractor')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(False)
        plt.xlim(-0.2,0.9)
        plt.ylim(-0.1,0.3)
        si.test.PlotTikZ(self.NameForTest()+'_deriv.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 magnitude')
        for (filename,meas) in wfList:
            resp=spDict[meas].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        plt.legend(loc='upper right')
        plt.grid(False)
        plt.xlim(0,40)
        plt.ylim(-60,0)
        si.test.PlotTikZ(self.NameForTest()+'_s11.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.title('incident spectral density (relative to ideal unit step)')
        for (filename,meas) in wfList:
            resp=spDict[meas+'incidentResponse']
            impulsewf=si.td.wf.Waveform(resp.td)
            impulsewf[0]=1.0
            impulsewffc=impulsewf.FrequencyContent()
            #plt.plot(impulsewffc.Frequencies('GHz'),[v+90 for v in impulsewffc.Values('dBmPerHz')],label=reflectName+' ideal')
            plt.plot(resp.Frequencies('GHz'),
                [(v-i) for (v,i) in zip(resp.Values('dBmPerHz'),impulsewffc.Values('dBmPerHz'))],label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB/GHz)')
        plt.legend(loc='upper right')
        plt.grid(False)
        plt.xlim(0,40)
        plt.ylim(4,11)
        si.test.PlotTikZ(self.NameForTest()+'_incident.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.title('reflected spectral density (relative to ideal unit step)')
        for (filename,meas) in wfList:
            resp=spDict[meas+'reflectResponse']
            impulsewf=si.td.wf.Waveform(resp.td)
            impulsewf[0]=1.0
            impulsewffc=impulsewf.FrequencyContent()
            #plt.plot(impulsewffc.Frequencies('GHz'),[v+90 for v in impulsewffc.Values('dBmPerHz')],label=reflectName+' ideal')
            plt.plot(resp.Frequencies('GHz'),
                [(v-i) for (v,i) in zip(resp.Values('dBmPerHz'),impulsewffc.Values('dBmPerHz'))],label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB/GHz)')
        plt.legend(loc='upper right')
        plt.grid(False)
        plt.xlim(0,40)
        plt.ylim(-50,10)
        si.test.PlotTikZ(self.NameForTest()+'_reflect.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.title('s11 phase')
        for (filename,meas) in wfList:
            resp=spDict[meas].FrequencyResponse(1,1)
            plt.plot(resp.Frequencies('GHz'),resp.Values('deg'),label=meas)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('phase (deg)')
        plt.legend(loc='upper right')
        plt.grid(False)
        plt.xlim(0,40)
        plt.ylim(-200,200)
        si.test.PlotTikZ(self.NameForTest()+'_phase.tex', plt)
        if plotthem: plt.show()

        #dutName='DUTLp1'

        f=spDict['Short'].f()

        ck=si.m.calkit.CalibrationKit('CalKitFileFemale.cstd',f)
        #ck.WriteStandardsToFiles('Anritsu')

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short'].FrequencyResponse(1,1),ck.shortStandard,0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open'].FrequencyResponse(1,1),ck.openStandard,0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load'].FrequencyResponse(1,1),ck.loadStandard,0,'Load1'),
            ]

        ports=1
        cm=si.m.cal.Calibration(ports,f,ml)

        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],self.NameForTest()+'.s'+str(ports*2)+'p')

        self.OutputCalFile(self.NameForTest(), spDict['ShortdenoisedDerivative'], spDict['OpendenoisedDerivative'], spDict['LoaddenoisedDerivative'])

if __name__ == "__main__":
    unittest.main()
