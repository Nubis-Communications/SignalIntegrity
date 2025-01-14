"""
TestPRBS.py
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
import sys
import os
import unittest
import SignalIntegrity.Lib as si
from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
from numpy import array

class EqualizerFitter(si.fit.LevMar):
    def __init__(self,callback=None):
        si.fit.LevMar.__init__(self,callback)
    def Initialize(self,sampledWf,levels,pre,post):
        self.levels=levels; self.pre=pre; self.post=post
        a=[[0.] for _ in range(pre+post+1)]
        self.x=[[v] for v in sampledWf.Values()]
        y=[[m] for m in self.Decode(self.x)[pre:len(self.x)-post]]
        si.fit.LevMar.Initialize(self,a,y)
        self.m_epsilon=0.0000001
    def Decode(self,x):
        return [self.levels[min(list(zip([abs(v[0]-d)
            for d in self.levels],range(len(self.levels)))))[1]] for v in x]
    def fF(self,a):
        return array([[sum([a[i][0]*self.x[k-i+self.pre][0]
            for i in range(self.pre+self.post+1)])]
                for k in range(self.pre,len(self.x)-self.post)])
    def AdjustVariablesAfterIteration(self,a):
        self.y=[[v] for v in self.Decode(self.x)[self.pre:len(self.x)-self.post]]
        return si.fit.LevMar.AdjustVariablesAfterIteration(self,a)
    def Results(self):
        return self.m_a


class TestPRBSTest(unittest.TestCase,si.test.SignalIntegrityAppTestHelper,si.test.RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        #self.forceWritePictures=True
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        self.UseSinX=SignalIntegrity.App.Preferences['Calculation.UseSinX']
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=False
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        os.chdir(self.cwd)
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=self.UseSinX
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])
    def testPRBS7(self):
        prbs7Calc=si.prbs.PseudoRandomPolynomial(7).Pattern()
        with open('prbs7.txt','rU' if sys.version_info.major < 3 else 'r') as f:
            prbs7Regression=[int(e) for e in f.readline().split()]
        self.assertEqual(prbs7Calc, prbs7Regression, 'prbs 7 failed')
    def testPRBS7Waveform(self):
        risetime=300e-12
        bitrate=1e9
        samplesPerUI=10
        amplitude=0.5
        delay=0.
        wf=si.prbs.PseudoRandomWaveform(7,bitrate,amplitude,risetime,delay,bitrate*samplesPerUI)
        self.WaveformRegressionChecker(wf,self.NameForTest()+'.txt')
    def testMultiLevelPam4PRBS23Waveform(self):
        risetime=300e-12
        baudrate=1e9
        samplesPerUI=10
        amplitude=0.5
        delay=0.
        bitsPerSymbol=2
        td=si.td.wf.TimeDescriptor(0.0,samplesPerUI*(2**7-1),baudrate*10.)
        wf=si.prbs.MultiLevelWaveform(23,baudrate,bitsPerSymbol,amplitude,risetime,delay,td)
        self.WaveformRegressionChecker(wf,self.NameForTest()+'.txt')
    def testMultiLevelPam8PRBS31Waveform(self):
        risetime=300e-12
        baudrate=1e9
        samplesPerUI=10
        amplitude=0.5
        delay=0.
        bitsPerSymbol=3
        td=si.td.wf.TimeDescriptor(0.0,samplesPerUI*(2**7-1),baudrate*10.)
        wf=si.prbs.MultiLevelWaveform(31,baudrate,bitsPerSymbol,amplitude,risetime,delay,td)
        self.WaveformRegressionChecker(wf,self.NameForTest()+'.txt')
    def testPRBS9Waveform(self):
        risetime=300e-12
        bitrate=1e9
        samplesPerUI=10
        amplitude=0.5
        delay=0.
        wf=si.prbs.PseudoRandomWaveform(9,bitrate,amplitude,risetime,delay,bitrate*samplesPerUI)
        self.WaveformRegressionChecker(wf,self.NameForTest()+'.txt')
    def testPRBS11Waveform(self):
        risetime=300e-12
        bitrate=1e9
        samplesPerUI=10
        amplitude=0.5
        delay=0.
        wf=si.prbs.PseudoRandomWaveform(11,bitrate,amplitude,risetime,delay,bitrate*samplesPerUI)
        self.WaveformRegressionChecker(wf,self.NameForTest()+'.txt')
    def testSSPRQWaveform(self):
        risetime=300e-12
        baudrate=1e9
        samplesPerUI=10
        amplitude=0.5
        delay=0.
        td=si.td.wf.TimeDescriptor(0.0,samplesPerUI*(2**16-1),baudrate*10.)
        wf=si.prbs.SSPRQWaveform(baudrate,amplitude,risetime,delay,td)
        self.WaveformRegressionChecker(wf,self.NameForTest()+'.txt')
    def testPRBS93(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            prbsCalc=si.prbs.PseudoRandomPolynomial(93).Pattern()
        self.assertEqual(cm.exception.parameter,'PseudoRandomPolynomial')
    def testPRBS11WaveformWrongRisetime(self):
        risetime=600e-12
        bitrate=1e9
        samplesPerUI=10
        amplitude=0.5
        delay=0.
        with self.assertRaises(si.SignalIntegrityException) as cm:
            wf=si.prbs.PseudoRandomWaveform(11,bitrate,amplitude,risetime,delay,bitrate*samplesPerUI)
        self.assertEqual(cm.exception.parameter,'Waveform')
    def testPRBS7WaveformNoSampleRate(self):
        risetime=300e-12
        bitrate=1e9
        samplesPerUI=10
        amplitude=0.5
        delay=0.
        wf=si.prbs.PseudoRandomWaveform(7,bitrate,amplitude,risetime,delay)
        wf2=si.prbs.PseudoRandomWaveform(7,bitrate,amplitude,risetime,delay,bitrate*samplesPerUI)
        self.assertEqual(wf, wf2, 'prbs no sample rate specified incorrect')
    def testPRBS7WaveformTd(self):
        risetime=300e-12
        bitrate=1e9
        samplesPerUI=10
        amplitude=0.5
        delay=0.
        wf=si.prbs.PseudoRandomWaveform(7,bitrate,amplitude,risetime,delay)
        td=si.td.wf.TimeDescriptor(0.0,samplesPerUI*(2**7-1),bitrate*10.)
        wf2=si.prbs.PseudoRandomWaveform(7,bitrate,amplitude,risetime,delay,td)
        self.assertEqual(wf, wf2, 'prbs with time descriptor incorrect')
    def testClockWaveform(self):
        clockRate=1.234e9
        risetime=200e-12
        delay=25e-9
        Fs=40e9
        td=si.td.wf.TimeDescriptor(-10e-9,int(20e-9*Fs),Fs)
        wf=si.prbs.ClockWaveform(clockRate,1.0,risetime,delay,td)
        wf2=si.prbs.SerialDataWaveform([1,0],clockRate*2.,1.0,risetime,delay,td)
        self.assertEqual(wf, wf2, 'clock waveform incorrect')
    def PrintProgress(self,iteration):
        print(self.m_fitter.ccm._IterationsTaken,self.m_fitter.m_mse)
    def testEqualizerFit(self):
        app=SignalIntegrityAppHeadless()
        app.OpenProjectFile(os.path.realpath('../../SignalIntegrity/App/Examples/PRBSExample/PRBSTest.si'))
        prbswf=app.Simulate().OutputWaveform('Vdiff')
        H=prbswf.td.H; bitrate=5e9; ui=1./bitrate
        dH=int(H/ui)*ui-56e-12+ui
        lastTime=prbswf.Times()[-1]
        dK=int((lastTime-ui-dH)/ui)
        decwftd=si.td.wf.TimeDescriptor(dH,dK,bitrate)
        decwf=si.td.wf.Waveform(decwftd,[prbswf.Measure(t) for t in decwftd.Times()])
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        self.m_fitter=EqualizerFitter(self.PrintProgress)
        self.m_fitter.Initialize(decwf,[-0.25,-0.1667/2.,0.1667/2.,0.25],1,1)
        self.m_fitter.Solve()
        results=self.m_fitter.Results()
        print(results)
        reggressionFile=self.NameForTest()+'.txt'
        if not os.path.exists(reggressionFile):
            resultFile2=open(reggressionFile,'w')
            resultFile2.write(str(results))
            resultFile2.close()
            self.assertTrue(False,reggressionFile+ ' not found')
        with open(reggressionFile,'rU' if sys.version_info.major < 3 else 'r') as f:
            fitRegression=[[float(e)] for e in f.readline().replace(']','').replace('[','').split(',')]
        for (res,reg) in zip(results,fitRegression):
            self.assertAlmostEqual(res[0], reg[0], 4, 'equalizer fit failed')
    @staticmethod
    def EyePattern(project,waveform,delay,bitrate):
        import numpy as np
        import SignalIntegrity.App.SignalIntegrityAppHeadless as siapp
        app=SignalIntegrityAppHeadless()
        app.OpenProjectFile(project)
        prbswf=app.Simulate().OutputWaveform(waveform)
        ui=1./bitrate; times=prbswf.Times()
        timesInBit=[((t-delay)/3./ui-int((t-delay)/3./ui))*3.*ui for t in times]
        from PIL import Image
        R=400; C=600
        EyeWfCols=[int(t/3./ui*C) for t in timesInBit]
        EyeWfRows=[int((v+0.3)/0.6*R) for v in prbswf.Values()]
        bitmap=[[0 for c in range(C)] for _ in range(R)]
        for i in range(len(EyeWfRows)):
            bitmap[EyeWfRows[i]][EyeWfCols[i]]=bitmap[EyeWfRows[i]][EyeWfCols[i]]+1
        maxValue=(max([max(v) for v in bitmap]))
        bitmap=[[int((maxValue - float(bitmap[r][c]))/maxValue*255.0)
                 for c in range(C)] for r in range(R)]
        img=Image.fromarray(np.squeeze(np.asarray(np.array(bitmap))).astype(np.uint8))
        img.save(waveform+'.png')
        # pragma: silent exclude
    @staticmethod
    def EqualizerFit(project,waveform,delay,bitrate):
        import SignalIntegrity.App.SignalIntegrityAppHeadless as siapp
        import SignalIntegrity.Lib as si
        app=SignalIntegrityAppHeadless()
        app.OpenProjectFile(project)
        prbswf=app.Simulate().OutputWaveform(waveform)
        H=prbswf.td.H; ui=1./bitrate
        dH=int(H/ui)*ui-delay+ui; lastTime=prbswf.Times()[-1]; dK=int((lastTime-ui-dH)/ui)
        decwftd=si.td.wf.TimeDescriptor(dH,dK,bitrate)
        decwf=si.td.wf.Waveform(decwftd,[prbswf.Measure(t) for t in decwftd.Times()])
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fitter=EqualizerFitter()
        fitter.Initialize(decwf,[-0.25,-0.1667/2.,0.1667/2.,0.25],1,1)
        fitter.Solve()
        print(fitter.Results())
    def testEyeVdiff(self):
        project=os.path.realpath('../../SignalIntegrity/App/Examples/PRBSExample/PRBSTest.si')
        self.EyePattern(project,'Vdiff',56e-12,5e9)
    def testEyeVeq(self):
        project=os.path.realpath('../../SignalIntegrity/App/Examples/PRBSExample/PRBSTest.si')
        self.EyePattern(project,'Veq',56e-12,5e9)
    def testWriteEyePattern(self):
        self.WriteCode('TestPRBS.py','EyePattern(project,waveform,delay,bitrate)',[],printFuncName=True)
    def testWriteEqualizerFitter(self):
        self.WriteCode('TestPRBS.py','EqualizerFit(project,waveform,delay,bitrate)',[],printFuncName=True)
    def testWriteEqualizerFit(self):
        fileName='TestPRBS.py'
        className='EqualizerFitter'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def ZeroForcingEqualizer(self,project,waveform,bitrate,value,pre,taps):
        import SignalIntegrity.App.SignalIntegrityAppHeadless as siapp; from numpy import array
        from numpy.linalg import inv
        app=SignalIntegrityAppHeadless()
        app.OpenProjectFile(project)
        pulsewf=app.Simulate().OutputWaveform(waveform)
        delay=pulsewf.td.TimeOfPoint(pulsewf.Values().index(max(pulsewf.Values())))
        print('delay: '+str(delay))
        H=pulsewf.td.H; ui=1./bitrate
        startTime=delay-(int((delay-H)/ui)-1)*ui
        endTime=delay+(int((pulsewf.Times()[-1]-delay)/ui-1)*ui)
        M=int((endTime-startTime)/ui+0.5); d=int((delay-startTime)/ui+0.5)
        x=[pulsewf.Measure(startTime+m*ui) for m in range(M)]
        X=[[0 if r-c < 0 else x[r-c] for c in range(taps)] for r in range(M)]
        r=[[value] if r == d+pre else [0] for r in range(len(X))]
        a=[v[0] for v in (inv((array(X).T).dot(array(X))).dot(array(X).T).dot(array(r))).tolist()]
        print('results: '+str(a))
    def testZeroForcingEqualizer(self):
        project=os.path.realpath('../../SignalIntegrity/App/Examples/PRBSExample/PulseTest.si')
        self.ZeroForcingEqualizer(project,'Vdiff',5e9,0.5,1,5)
    def testWriteZeroForcingEqualizer(self):
        self.WriteCode('TestPRBS.py','ZeroForcingEqualizer(self,project,waveform,bitrate,value,pre,taps)',[],printFuncName=True)
if __name__ == "__main__":
    unittest.main()