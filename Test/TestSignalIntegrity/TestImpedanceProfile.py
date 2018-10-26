"""
TestImpedanceProfile.py
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
from numpy import matrix
import math
import cmath
from numpy import linalg
from numpy import array
import os

import matplotlib
matplotlib.use('Tkagg')

class TestImpedanceProfile(unittest.TestCase,si.test.SParameterCompareHelper,
                           si.test.SignalIntegrityAppTestHelper,si.test.RoutineWriterTesterHelper):
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
        return '_'.join(self.id().split('.')[-2:])
    def testImpedanceProfileCable(self):
        sp = si.sp.SParameterFile('cable.s2p',50.)
        Zc = si.ip.ImpedanceProfile(sp,100,2).Z()
        """
        import matplotlib.pyplot as plt
        plt.plot(Zc)
        plt.show()
        """
        pass
    def testImpedanceProfileContrived(self):
        N=1000
        f=[20.e9*n/N for n in range(N+1)]
        Td=1./(4.*f[N])
        gamma=[1j*2.*math.pi*fe*Td for fe in f]
        Zc = [50.,55.,50.,45.,60.,52.,50.,50.,50.]
        Z0=50.
        rho = [(Z-Z0)/(Z+Z0) for Z in Zc]
        Gsp=[]
        for n in range(N+1):
            T = [si.cvt.S2T(si.dev.IdealTransmissionLine(rho[m],gamma[n])) for m in range(len(rho))]
            tacc=matrix([[1.,0.],[0.,1.]])
            for m in range(len(rho)):
                tacc=tacc*matrix(T[m])
            G=si.cvt.T2S(tacc.tolist())
            Gsp.append(G)
        sp = si.sp.SParameters(f,Gsp,Z0)
        ip = si.ip.ImpedanceProfile(sp,len(Zc),1)
        Zc2 =ip.Z()
        """
        import matplotlib.pyplot as plt
        plt.plot(Zc)
        plt.show()
        """
#       print Zc2 # should be equal to Zc
        difference = linalg.norm(array(Zc2)-array(Zc))
        self.assertTrue(difference<1e-4,'contrived impedance profile incorrect')
        sp2=ip.SParameters(f)
        self.assertTrue(self.SParametersAreEqual(sp, sp2, 0.0001),'impedance profile reassembled s-parameters incorrect')
    def testCableDeembed(self):
        sp = si.sp.SParameterFile('cable.s2p',50.)
        ip = si.ip.ImpedanceProfile(sp,12,1)
        Zc = ip.Z()
        """
        import matplotlib.pyplot as plt
        plt.plot(Zc)
        plt.show()
        """
        spls=ip.SParameters(sp.f())
        spls.WriteToFile('cableLeftSide.s2p')
        ip = si.ip.ImpedanceProfile(sp,12,2)
        Zc = ip.Z()
        """
        import matplotlib.pyplot as plt
        plt.plot(Zc)
        plt.show()
        """
        sprs=ip.SParameters(sp.f())
        sprs.WriteToFile('cableRightSide.s2p')
        dp = si.p.DeembedderNumericParser(sp.f())
        dp.AddLines(['unknown ?1 2',
                     'device L 2 file cableLeftSide.s2p',
                     'device R 2 file cableRightSide.s2p',
                     'port 1 L 1 2 R 1',
                     'connect L 2 ?1 1',
                     'connect R 2 ?1 2',
                     'system file cable.s2p'])
        cd = dp.Deembed()
        fileName='cableDeembedded.s2p'
        self.SParameterRegressionChecker(cd, fileName)
    def AssembleLine(self,Zc):
        netListLine=[]
        td=si.td.wf.TimeDescriptor(0,200,20e9)
        Td=1./td.Fs/2*4
        for (z,e) in zip(Zc,range(len(Zc))):
            netListLine.append('device T'+str(e)+' 2 tline zc '+str(z)+' td '+str(Td))
        for e in range(1,len(Zc)):
            netListLine.append('connect T'+str(e-1)+' 2 T'+str(e)+' 1')
        netListLine.append('device R1 1 R 50')
        netListLine.append('connect T'+str(len(Zc)-1)+' 2 R1 1')
        netListLine.append('port 1 T0 1')
        sp=si.p.SystemSParametersNumericParser(f=td.FrequencyList()).AddLines(netListLine).SParameters()
        sp.SetReferenceImpedance(50.0)
        return sp
    def testAssembled(self):
        spDict=dict()
        Zc = [50.,55.,52.,45.,60.]
        for e in range(len(Zc)):
            ZSingle=[50 for _ in Zc]
            ZSingle=[Zc[e] for _ in range(len(Zc))]
            ZSingle=[ZSingle[e] if i>=e else 50 for i in range(len(Zc))]
            spDict[str(e)]=self.AssembleLine(ZSingle)
        spDict['all']=self.AssembleLine(Zc)

        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        td=spDict[str(e)].FrequencyResponse(1,1).ImpulseResponse().td
        impulsewf=si.td.wf.Waveform(td,[1 if abs(t)<= 25e-12 else 0 for t in td.Times()])
        for e in range(len(Zc)):
            wf=spDict[str(e)].FrequencyResponse(1,1).ImpulseResponse()+impulsewf
            plt.plot(wf.Times('ns'),wf.Values(),label=str(e))
        wf=spDict['all'].FrequencyResponse(1,1).ImpulseResponse()
        plt.plot(wf.Times('ns'),wf.Values(),label='all')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(True)
        #si.test.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        for e in range(len(Zc)):
            wf=(spDict[str(e)].FrequencyResponse(1,1).ImpulseResponse()+impulsewf).Integral(addPoint=True,scale=False)
            plt.plot(wf.Times('ns'),wf.Values(),label=str(e))
        wf=(spDict['all'].FrequencyResponse(1,1).ImpulseResponse()+impulsewf).Integral(addPoint=True,scale=False)
        plt.plot(wf.Times('ns'),wf.Values(),label='all')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(True)
        #si.test.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
#         for e in range(len(Zc)):
#             wf=spDict[str(e)].FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
#             plt.plot(wf.Times('ns'),wf.Values(),label=str(e))
        wf=spDict['all'].FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
        plt.plot(wf.Times('ns'),wf.Values(),label='all')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(True)
        #si.test.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.figure(1)
        #plt.title('impedance')
#         for e in range(len(Zc)):
#             wf=spDict[str(e)].FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
#             plt.plot(wf.Times('ns'),wf.Values(),label=str(e))
        wf=spDict['all'].FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
        wfApprox=spDict['all'].FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
        Z0=50.0
        wfActual=si.td.wf.Waveform(wf.td,Z0)
        for k in range(len(wf)):
            wf[k]=Z0*(1+wf[k])/(1-wf[k])
            wfApprox[k]=Z0+2*Z0*wfApprox[k]
            if wfActual.td[k]>0.:
                e=int(wfActual.td[k]/(50e-12*4))
                if e < len(Zc):
                    wfActual[k]=Zc[e]
                else:
                    wfActual[k]=50.0
        wf.td=si.td.wf.TimeDescriptor(wf.td.H/2,wf.td.K,wf.td.Fs*2)
        wfApprox.td=si.td.wf.TimeDescriptor(wfApprox.td.H/2,wfApprox.td.K,wfApprox.td.Fs*2)
        wfActual.td=si.td.wf.TimeDescriptor(wfActual.td.H/2,wfActual.td.K,wfActual.td.Fs*2)
        plt.plot(wf.Times('ns'),wf.Values(),label='Z estimated',color='black')
        plt.plot(wfApprox.Times('ns'),wfApprox.Values(),label='Z approximated',linestyle='--',color='black')
        plt.plot(wfActual.Times('ns'),wfActual.Values(),label='Z actual',linewidth=2,color='black')
        plt.xlim(0.0,1)
        plt.ylim(44,61)
        plt.xlabel('time (ns)')
        plt.ylabel('Z (Ohms)')
        plt.legend(loc='upper right')
        #plt.grid(True)
        #si.test.PlotTikZ('SimulationExperimentImpedance.tex', plt)
        if plotthem: plt.show()

        Z0=50.
        plotthem=False
        plt.clf()
        sp=spDict['all']
        sp.SetReferenceImpedance(Z0)
        td=sp.m_f.TimeDescriptor()
        ipwf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0+1/(td.Fs*4),td.K/2,td.Fs*2),si.ip.ImpedanceProfile(spDict['all'],td.K/2,1).Z())
        plt.plot(ipwf.Times('ns'),ipwf.Values(),label='Z calculated',color='black')
        plt.plot(wfActual.Times('ns'),wfActual.Values(),label='Z actual',linewidth=2,color='black')
        plt.xlim(0.0,1)
        plt.ylim(44,61)
        plt.xlabel('time (ns)')
        plt.ylabel('Z (Ohms)')
        plt.legend(loc='upper right')
        #plt.grid(True)
        if plotthem: plt.show()
    def testImpedanceProfileWaveformNoPortZAlignedInterface(self):
        Zc = [50.,55.,52.,45.,60.]
        Z0=50.0
        sp=self.AssembleLine(Zc).SetReferenceImpedance(Z0)
        wf=sp.FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
        wfActual=si.td.wf.Waveform(wf.td,Z0)
        for k in range(len(wf)):
            if wfActual.td[k]>0.:
                e=int(wfActual.td[k]/(50e-12*4))
                if e < len(Zc):
                    wfActual[k]=Zc[e]
                else:
                    wfActual[k]=50.0
        wfActual.td=si.td.wf.TimeDescriptor(wfActual.td.H/2,wfActual.td.K,wfActual.td.Fs*2)
        wfExact=si.ip.ImpedanceProfileWaveform(sp,includePortZ=False,align='interface')
        wfEstimated=si.ip.ImpedanceProfileWaveform(sp,method='estimated',includePortZ=False,align='interface')
        wfApprox=si.ip.ImpedanceProfileWaveform(sp,method='approximate',includePortZ=False,align='interface')

        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.plot(wfExact.Times('ps'),wfExact.Values(),label='Z exact',color='black',marker='o')
        plt.plot(wfEstimated.Times('ps'),wfEstimated.Values(),label='Z estimated',color='black')
        plt.plot(wfApprox.Times('ps'),wfApprox.Values(),label='Z approximated',linestyle='--',color='black')
        #plt.plot(wfActual.Times('ns'),wfActual.Values(),label='Z actual',linewidth=2,color='black')
        plt.xlim(0.0,1000)
        plt.ylim(44,61)
        plt.xlabel('time (ps)')
        plt.ylabel('Z (Ohms)')
        plt.legend(loc='upper right')
        #plt.grid(True)
        #si.test.PlotTikZ('SimulationExperimentImpedance.tex', plt)
        if plotthem: plt.show()

        self.WaveformRegressionChecker(wfActual, 'Waveform_'+self.NameForTest()+'_Actual.txt')
        self.WaveformRegressionChecker(wfExact, 'Waveform_'+self.NameForTest()+'_Exact.txt')
        self.WaveformRegressionChecker(wfEstimated, 'Waveform_'+self.NameForTest()+'_Estimated.txt')
        self.WaveformRegressionChecker(wfApprox, 'Waveform_'+self.NameForTest()+'_Approx.txt')

    def testImpedanceProfileWaveformPortZAlignedInterface(self):
        Zc = [50.,55.,52.,45.,60.]
        Z0=50.0
        sp=self.AssembleLine(Zc).SetReferenceImpedance(Z0)
        wf=sp.FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
        wfActual=si.td.wf.Waveform(wf.td,Z0)
        for k in range(len(wf)):
            if wfActual.td[k]>0.:
                e=int(wfActual.td[k]/(50e-12*4))
                if e < len(Zc):
                    wfActual[k]=Zc[e]
                else:
                    wfActual[k]=50.0
        wfActual.td=si.td.wf.TimeDescriptor(wfActual.td.H/2,wfActual.td.K,wfActual.td.Fs*2)
        wfExact=si.ip.ImpedanceProfileWaveform(sp,includePortZ=True,align='interface')
        wfEstimated=si.ip.ImpedanceProfileWaveform(sp,method='estimated',includePortZ=True,align='interface')
        wfApprox=si.ip.ImpedanceProfileWaveform(sp,method='approximate',includePortZ=True,align='interface')

        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.plot(wfExact.Times('ps'),wfExact.Values(),label='Z exact',color='black',marker='o')
        plt.plot(wfEstimated.Times('ps'),wfEstimated.Values(),label='Z estimated',color='black')
        plt.plot(wfApprox.Times('ps'),wfApprox.Values(),label='Z approximated',linestyle='--',color='black')
        #plt.plot(wfActual.Times('ns'),wfActual.Values(),label='Z actual',linewidth=2,color='black')
        plt.xlim(0.0,1000)
        plt.ylim(44,61)
        plt.xlabel('time (ps)')
        plt.ylabel('Z (Ohms)')
        plt.legend(loc='upper right')
        #plt.grid(True)
        #si.test.PlotTikZ('SimulationExperimentImpedance.tex', plt)
        if plotthem: plt.show()

        self.WaveformRegressionChecker(wfActual, 'Waveform_'+self.NameForTest()+'_Actual.txt')
        self.WaveformRegressionChecker(wfExact, 'Waveform_'+self.NameForTest()+'_Exact.txt')
        self.WaveformRegressionChecker(wfEstimated, 'Waveform_'+self.NameForTest()+'_Estimated.txt')
        self.WaveformRegressionChecker(wfApprox, 'Waveform_'+self.NameForTest()+'_Approx.txt')

    def testImpedanceProfileWaveformNoPortZAlignedMiddle(self):
        Zc = [50.,55.,52.,45.,60.]
        Z0=50.0
        sp=self.AssembleLine(Zc).SetReferenceImpedance(Z0)
        wf=sp.FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
        wfActual=si.td.wf.Waveform(wf.td,Z0)
        for k in range(len(wf)):
            if wfActual.td[k]>0.:
                e=int(wfActual.td[k]/(50e-12*4))
                if e < len(Zc):
                    wfActual[k]=Zc[e]
                else:
                    wfActual[k]=50.0
        wfActual.td=si.td.wf.TimeDescriptor(wfActual.td.H/2,wfActual.td.K,wfActual.td.Fs*2)
        wfExact=si.ip.ImpedanceProfileWaveform(sp,includePortZ=False,align='middle')
        wfEstimated=si.ip.ImpedanceProfileWaveform(sp,method='estimated',includePortZ=False,align='middle')
        wfApprox=si.ip.ImpedanceProfileWaveform(sp,method='approximate',includePortZ=False,align='middle')

        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.plot(wfExact.Times('ps'),wfExact.Values(),label='Z exact',color='black',marker='o')
        plt.plot(wfEstimated.Times('ps'),wfEstimated.Values(),label='Z estimated',color='black')
        plt.plot(wfApprox.Times('ps'),wfApprox.Values(),label='Z approximated',linestyle='--',color='black')
        #plt.plot(wfActual.Times('ns'),wfActual.Values(),label='Z actual',linewidth=2,color='black')
        plt.xlim(0.0,1000)
        plt.ylim(44,61)
        plt.xlabel('time (ps)')
        plt.ylabel('Z (Ohms)')
        plt.legend(loc='upper right')
        #plt.grid(True)
        #si.test.PlotTikZ('SimulationExperimentImpedance.tex', plt)
        if plotthem: plt.show()

        self.WaveformRegressionChecker(wfActual, 'Waveform_'+self.NameForTest()+'_Actual.txt')
        self.WaveformRegressionChecker(wfExact, 'Waveform_'+self.NameForTest()+'_Exact.txt')
        self.WaveformRegressionChecker(wfEstimated, 'Waveform_'+self.NameForTest()+'_Estimated.txt')
        self.WaveformRegressionChecker(wfApprox, 'Waveform_'+self.NameForTest()+'_Approx.txt')

    def testImpedanceProfileWaveformPortZAlignedMiddle(self):
        Zc = [50.,55.,52.,45.,60.]
        Z0=50.0
        sp=self.AssembleLine(Zc).SetReferenceImpedance(Z0)
        wf=sp.FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
        wfActual=si.td.wf.Waveform(wf.td,Z0)
        for k in range(len(wf)):
            if wfActual.td[k]>0.:
                e=int(wfActual.td[k]/(50e-12*4))
                if e < len(Zc):
                    wfActual[k]=Zc[e]
                else:
                    wfActual[k]=50.0
        wfActual.td=si.td.wf.TimeDescriptor(wfActual.td.H/2,wfActual.td.K,wfActual.td.Fs*2)
        wfExact=si.ip.ImpedanceProfileWaveform(sp,includePortZ=True,align='middle')
        wfEstimated=si.ip.ImpedanceProfileWaveform(sp,method='estimated',includePortZ=True,align='middle')
        wfApprox=si.ip.ImpedanceProfileWaveform(sp,method='approximate',includePortZ=True,align='middle')

        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.plot(wfExact.Times('ps'),wfExact.Values(),label='Z exact',color='black',marker='o')
        plt.plot(wfEstimated.Times('ps'),wfEstimated.Values(),label='Z estimated',color='black')
        plt.plot(wfApprox.Times('ps'),wfApprox.Values(),label='Z approximated',linestyle='--',color='black')
        #plt.plot(wfActual.Times('ns'),wfActual.Values(),label='Z actual',linewidth=2,color='black')
        plt.xlim(0.0,1000)
        plt.ylim(44,61)
        plt.xlabel('time (ps)')
        plt.ylabel('Z (Ohms)')
        plt.legend(loc='upper right')
        #plt.grid(True)
        #si.test.PlotTikZ('SimulationExperimentImpedance.tex', plt)
        if plotthem: plt.show()

        self.WaveformRegressionChecker(wfActual, 'Waveform_'+self.NameForTest()+'_Actual.txt')
        self.WaveformRegressionChecker(wfExact, 'Waveform_'+self.NameForTest()+'_Exact.txt')
        self.WaveformRegressionChecker(wfEstimated, 'Waveform_'+self.NameForTest()+'_Estimated.txt')
        self.WaveformRegressionChecker(wfApprox, 'Waveform_'+self.NameForTest()+'_Approx.txt')

    def testWriteImpedanceProfileWaveform(self):
        fileName="../../SignalIntegrity/Lib/ImpedanceProfile/ImpedanceProfileWaveform.py"
        className='ImpedanceProfileWaveform'
        defName=['__init__']
        self.WriteClassCode(fileName,className,defName)

    def testWriteImpedanceProfile(self):
        fileName="../../SignalIntegrity/Lib/ImpedanceProfile/ImpedanceProfile.py"
        className='ImpedanceProfile'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)

    def AssembleNastyLine(self,Zc,Tds):
        netListLine=[]
        td=si.td.wf.TimeDescriptor(0,200,20e9)
        for (z,e,Td) in zip(Zc,range(len(Zc)),Tds):
            netListLine.append('device T'+str(e)+' 2 tline zc '+str(z)+' td '+str(Td))
        for e in range(1,len(Zc)):
            netListLine.append('connect T'+str(e-1)+' 2 T'+str(e)+' 1')
        netListLine.append('device R1 1 R 50.0')
        netListLine.append('connect T'+str(len(Zc)-1)+' 2 R1 1')
        netListLine.append('port 1 T0 1')
        sp=si.p.SystemSParametersNumericParser(f=td.FrequencyList()).AddLines(netListLine).SParameters()
        sp.SetReferenceImpedance(50.0)
        return sp
    def testAssembleNastyLine(self):
        Zc = [50.,55.,52.,45.,60.]
        td=si.td.wf.TimeDescriptor(0,200,20e9)
        TdIdeal=1./td.Fs/2*4
        TdAdjust=[.1*TdIdeal,-.2*TdIdeal,0.,.3*TdIdeal,-.1*TdIdeal]
        Td=[TdIdeal+Tdi for Tdi in TdAdjust]
#         Td=[TdIdeal for _ in range(len(Zc))]
#         Td[0]=Td[0]/8
        TdTime=[0]+[sum(Td[:e]) for e in range(1,len(Td))]
        sp=self.AssembleNastyLine(Zc,Td)

        si.td.wf.Waveform.adaptionStrategy='Linear'

        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        td=sp.FrequencyResponse(1,1).ImpulseResponse().td
        impulsewf=si.td.wf.Waveform(td,[1 if abs(t)<= 25e-12 else 0 for t in td.Times()])
        wf=sp.FrequencyResponse(1,1).ImpulseResponse()*si.td.f.RaisedCosineFilter()
        plt.plot(wf.Times('ns'),wf.Values(),label='all')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(True)
        #si.test.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
        wf=(sp.FrequencyResponse(1,1).ImpulseResponse()+impulsewf).Integral(addPoint=True,scale=False)*si.td.f.RaisedCosineFilter()
        plt.plot(wf.Times('ns'),wf.Values(),label='all')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(True)
        #si.test.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.figure(1)
        plt.title('waveforms')
#         for e in range(len(Zc)):
#             wf=spDict[str(e)].FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
#             plt.plot(wf.Times('ns'),wf.Values(),label=str(e))
        wf=sp.FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)*si.td.f.RaisedCosineFilter()
        plt.plot(wf.Times('ns'),wf.Values(),label='all')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.legend(loc='upper right')
        plt.grid(True)
        #si.test.PlotTikZ('waveforms.tex', plt.gcf())
        if plotthem: plt.show()

        plt.clf()
        plt.figure(1)
        #plt.title('impedance')
#         for e in range(len(Zc)):
#             wf=spDict[str(e)].FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
#             plt.plot(wf.Times('ns'),wf.Values(),label=str(e))
        wf=sp.FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
        wfApprox=sp.FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
        Z0=50.0
        wfActual=si.td.wf.Waveform(wf.td,Z0)
        for k in range(len(wf)):
            wf[k]=Z0*(1+wf[k])/(1-wf[k])
            wfApprox[k]=Z0+2*Z0*wfApprox[k]
            t=wfActual.td[k]/2.
            foundOne=False
            for m in range(len(Td)):
                if (t>TdTime[m]) and (t <= (TdTime[m]+Td[m])):
                    e=m
                    foundOne=True
            if foundOne:
                wfActual[k]=Zc[e]
        wf.td=si.td.wf.TimeDescriptor(wf.td.H/2,wf.td.K,wf.td.Fs*2)
        wfApprox.td=si.td.wf.TimeDescriptor(wfApprox.td.H/2,wfApprox.td.K,wfApprox.td.Fs*2)
        wfActual.td=si.td.wf.TimeDescriptor(wfActual.td.H/2,wfActual.td.K,wfActual.td.Fs*2)
        plt.plot(wf.Times('ns'),wf.Values(),label='Z estimated',color='black')
        plt.plot(wfApprox.Times('ns'),wfApprox.Values(),label='Z approximated',linestyle='--',color='black')
        plt.plot(wfActual.Times('ns'),wfActual.Values(),label='Z actual',linewidth=2,color='black')
        plt.xlim(0.0,1)
        plt.ylim(44,61)
        plt.xlabel('time (ns)')
        plt.ylabel('Z (Ohms)')
        plt.legend(loc='upper right')
        #plt.grid(True)
        #si.test.PlotTikZ('SimulationExperimentImpedance.tex', plt)
        if plotthem: plt.show()

        plotthem=False
        Z0=50.
        plt.clf()
        sp.SetReferenceImpedance(Z0)
        td=sp.m_f.TimeDescriptor()
        ip=si.ip.ImpedanceProfile(sp,td.K/2,1)
        ipwf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(ip.DelaySection()/2,len(ip),1./ip.DelaySection()),ip.Z())
        plt.plot(ipwf.Times('ns'),ipwf.Values(),label='Z calculated',color='black')
        plt.plot(wfActual.Times('ns'),wfActual.Values(),label='Z actual',linewidth=2,color='black')
        plt.xlim(0.0,1)
        plt.ylim(44,61)
        plt.xlabel('time (ns)')
        plt.ylabel('Z (Ohms)')
        plt.legend(loc='upper right')
        #plt.grid(True)
        if plotthem: plt.show()

        wfExact=si.ip.ImpedanceProfileWaveform(sp,includePortZ=True,align='middle')*si.td.f.RaisedCosineFilter(1)
        wfEstimated=si.ip.ImpedanceProfileWaveform(sp,method='estimated',includePortZ=True,align='middle')*si.td.f.RaisedCosineFilter(1)
        wfApprox=si.ip.ImpedanceProfileWaveform(sp,method='approximate',includePortZ=True,align='middle')*si.td.f.RaisedCosineFilter(1)

        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.plot(wfExact.Times('ps'),wfExact.Values(),label='Z exact',color='black',marker='o')
        plt.plot(wfEstimated.Times('ps'),wfEstimated.Values(),label='Z estimated',color='black')
        plt.plot(wfApprox.Times('ps'),wfApprox.Values(),label='Z approximated',linestyle='--',color='black')
        plt.plot(wfActual.Times('ps'),wfActual.Values(),label='Z actual',linewidth=2,color='black')
        plt.xlim(0.0,1000)
        plt.ylim(44,61)
        plt.xlabel('time (ps)')
        plt.ylabel('Z (Ohms)')
        plt.legend(loc='upper right')
        #plt.grid(True)
        #si.test.PlotTikZ('SimulationExperimentImpedance.tex', plt)
        if plotthem: plt.show()

    def AssembleNastyLineOpen(self,Zc,Tds):
        netListLine=[]
        td=si.td.wf.TimeDescriptor(0,200,20e9)
        for (z,e,Td) in zip(Zc,range(len(Zc)),Tds):
            netListLine.append('device T'+str(e)+' 2 tline zc '+str(z)+' td '+str(Td))
        for e in range(1,len(Zc)):
            netListLine.append('connect T'+str(e-1)+' 2 T'+str(e)+' 1')
        netListLine.append('device R1 1 open')
        netListLine.append('connect T'+str(len(Zc)-1)+' 2 R1 1')
        netListLine.append('port 1 T0 1')
        sp=si.p.SystemSParametersNumericParser(f=td.FrequencyList()).AddLines(netListLine).SParameters()
        sp.SetReferenceImpedance(50.0)
        return sp
    def testAssembleNastyLineOpen(self):
        Zc = [50.,55.,52.,45.,60.]
        td=si.td.wf.TimeDescriptor(0,200,20e9)
        TdIdeal=1./td.Fs/2*4
        TdAdjust=[.1*TdIdeal,-.2*TdIdeal,0.,.3*TdIdeal,-.1*TdIdeal]
        Td=[TdIdeal+Tdi for Tdi in TdAdjust]
        TdTime=[0]+[sum(Td[:e]) for e in range(1,len(Td))]

        sp=self.AssembleNastyLineOpen(Zc,Td)

        si.td.wf.Waveform.adaptionStrategy='Linear'
        si.td.f.RaisedCosineFilter(1).Print()
        wfExact=si.ip.ImpedanceProfileWaveform(sp,includePortZ=True,align='middle')*si.td.f.RaisedCosineFilter(1)
        wfEstimated=si.ip.ImpedanceProfileWaveform(sp,method='estimated',includePortZ=True,align='middle')*si.td.f.RaisedCosineFilter(1)
        wfApprox=si.ip.ImpedanceProfileWaveform(sp,method='approximate',includePortZ=True,align='middle')*si.td.f.RaisedCosineFilter(1)

        wf=sp.FrequencyResponse(1,1).ImpulseResponse().Integral(addPoint=True,scale=False)
        Z0=50.0
        wfActual=si.td.wf.Waveform(wf.td,Z0)
        for k in range(len(wf)):
            wf[k]=Z0*(1+wf[k])/(1-wf[k])
            t=wfActual.td[k]/2.
            foundOne=False
            for m in range(len(Td)):
                if (t>TdTime[m]) and (t <= (TdTime[m]+Td[m])):
                    e=m
                    foundOne=True
            if foundOne:
                wfActual[k]=Zc[e]
        wfActual.td=si.td.wf.TimeDescriptor(wfActual.td.H/2,wfActual.td.K,wfActual.td.Fs*2)

        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.plot(wfExact.Times('ps'),wfExact.Values(),label='Z exact',color='black',marker='o')
        plt.plot(wfEstimated.Times('ps'),wfEstimated.Values(),label='Z estimated',color='black')
        plt.plot(wfApprox.Times('ps'),wfApprox.Values(),label='Z approximated',linestyle='--',color='black')
        plt.plot(wfActual.Times('ps'),wfActual.Values(),label='Z actual',linewidth=2,color='black')
        plt.xlim(0.0,1000)
        plt.ylim(44,61)
        plt.xlabel('time (ps)')
        plt.ylabel('Z (Ohms)')
        plt.legend(loc='upper right')
        #plt.grid(True)
        #si.test.PlotTikZ('SimulationExperimentImpedance.tex', plt)
        if plotthem: plt.show()
    def testPeelCableforRLGC(self):
        sp=si.sp.SParameterFile('cableForRLGCCausal.s2p')
        port1Impedance=si.ip.ImpedanceProfileWaveform(sp,port=1,
            method='estimated',adjustForDelay=False,includePortZ=False)
        port2Impedance=si.ip.ImpedanceProfileWaveform(sp,port=2,
            method='estimated',adjustForDelay=False,includePortZ=False)

        timelen=66e-12
        sp1=si.ip.PeeledPortSParameters(sp,1,timelen)
        sp2=si.ip.PeeledPortSParameters(sp,2,timelen)

        port1peeled=si.ip.ImpedanceProfileWaveform(sp1,port=1,
            method='estimated',adjustForDelay=False,includePortZ=False)
        port2peeled=si.ip.ImpedanceProfileWaveform(sp2,port=1,
            method='estimated',adjustForDelay=False,includePortZ=False)

        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.plot(port1Impedance.Times('ps'),port1Impedance.Values(),label='port 1',color='black')
        plt.plot(port1peeled.Times('ps'),port1peeled.Values(),label='port 1 peeled',color='black')
        #plt.plot(port2Impedance.Times('ps'),port2Impedance.Values(),label='port 2',color='black')
        plt.xlim(0.0,1000)
        plt.ylim(44,61)
        plt.xlabel('time (ps)')
        plt.ylabel('Z (Ohms)')
        plt.legend(loc='upper right')
        #plt.grid(True)
        #si.test.PlotTikZ('SimulationExperimentImpedance.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.plot(port1Impedance.Times('ps'),port2Impedance.Values(),label='port 2',color='black')
        plt.plot(port1peeled.Times('ps'),port2peeled.Values(),label='port 2 peeled',color='black')
        #plt.plot(port2Impedance.Times('ps'),port2Impedance.Values(),label='port 2',color='black')
        plt.xlim(0.0,1000)
        plt.ylim(44,61)
        plt.xlabel('time (ps)')
        plt.ylabel('Z (Ohms)')
        plt.legend(loc='upper right')
        #plt.grid(True)
        #si.test.PlotTikZ('SimulationExperimentImpedance.tex', plt)
        if plotthem: plt.show()

        sspdn=si.p.DeembedderNumericParser(sp.f()).AddLines(['unknown S 2','device D1 2 tline zc 50 td 66e-12','device D2 2 tline zc 50 td 66e-12',
             'connect D1 2 S 1','connect D2 2 S 2','port 1 D1 1','port 2 D2 1'])
        dsp=sspdn.Deembed(sp).EnforceCausality()
        self.SParameterRegressionChecker(dsp, self.NameForTest()+'_gated.s2p')

        sddn=si.sd.DeembedderNumeric(si.p.DeembedderParser().AddLines(['unknown S 2','device D1 2','device D2 2',
            'connect D1 2 S 1','connect D2 2 S 2','port 1 D1 1 2 D2 1']).SystemDescription())
        spd=[]
        for n in range(len(sp)):
            sddn.AssignSParameters('D1',sp1[n])
            sddn.AssignSParameters('D2',sp2[n])
            spd.append(sddn.CalculateUnknown(sp[n]))
        dsp=si.sp.SParameters(sp.f(),spd)

        self.SParameterRegressionChecker(dsp, self.NameForTest()+'_deembedded.s2p')

        dsp=dsp.EnforceCausality()
        self.SParameterRegressionChecker(dsp, self.NameForTest()+'_deembedded_causal.s2p')
    def testZZZLaunchDeembeddingExample(self):
        # ZZZ to make sure it occurs last, since it depends on other measurement
        sp=si.sp.SParameterFile('cableForRLGCCausal.s2p')
        dsp=self.DeembedLaunch(sp,[66e-12,66e-12])
        self.SParameterRegressionChecker(dsp, 'TestImpedanceProfile_testPeelCableforRLGC_deembedded.s2p')
    def DeembedLaunch(self,sp,timelen):
        spp=[si.ip.PeeledPortSParameters(sp,p+1,timelen[p]) for p in range(2)]
        sddn=si.sd.DeembedderNumeric(si.p.DeembedderParser().AddLines(['unknown S 2',
            'device D1 2','device D2 2','connect D1 2 S 1','connect D2 2 S 2',
            'port 1 D1 1 2 D2 1']).SystemDescription())
        spd=[]
        for n in range(len(sp)):
            for p in range(2):
                sddn.AssignSParameters('D'+str(p+1),spp[p][n])
            spd.append(sddn.CalculateUnknown(sp[n]))
        return si.sp.SParameters(sp.f(),spd)
    def PeelLaunch(self,sp,timelen):
        spp=[si.ip.PeeledPortSParameters(sp,p+1,timelen[p])
            for p in range(sp.m_P)]
        sddp=si.p.DeembedderParser().AddLine('unknown S '+str(sp.m_P))
        for ps in [str(p+1) for p in range(sp.m_P)]:
            sddp.AddLines(['device D'+ps+' 2','connect D'+ps+' 2 S '+ps,'port '+ps+' D'+ps+' 1'])
        sddn=si.sd.DeembedderNumeric(sddp.SystemDescription()); spd=[]
        for n in range(len(sp)):
            for p in range(sp.m_P): sddn.AssignSParameters('D'+str(p+1),spp[p][n])
            spd.append(sddn.CalculateUnknown(sp[n]))
        return si.sp.SParameters(sp.f(),spd)
    def testWritePeeledLaunches(self):
        fileName="../../SignalIntegrity/Lib/ImpedanceProfile/PeeledLaunches.py"
        className='PeeledLaunches'
        defName=['__init__']
        self.WriteClassCode(fileName, className, defName)
    def testWritePeeledPortSParameters(self):
        fileName="../../SignalIntegrity/Lib/ImpedanceProfile/PeeledPortSParameters.py"
        className='PeeledPortSParameters'
        defName=['__init__']
        self.WriteClassCode(fileName, className, defName)
    def testZZZLaunchDeembeddingExample2(self):
        # ZZZ to make sure it occurs last, since it depends on other measurement
        sp=si.sp.SParameterFile('cableForRLGCCausal.s2p')
        dsp=si.ip.PeeledLaunches(sp,[66e-12,66e-12])
        self.SParameterRegressionChecker(dsp, 'TestImpedanceProfile_testPeelCableforRLGC_deembedded.s2p')
    def testStepResponseGamma(self):
        fl=si.fd.EvenlySpacedFrequencyList(10e9,50)
        td=si.td.wf.TimeDescriptor(-3.5e-9,11.5e-9*20e9,20e9)
        openStepWf=si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(fl).
            AddLines(['voltagesource VG1 1','device R1 2 R 50.0','device T1 2 tline zc 50.0 td 1e-09',
             'device O1 1 open','connect R1 1 VG1 1','output T1 1','connect T1 1 R1 2',
             'connect O1 1 T1 2']).TransferMatrices()).\
             ProcessWaveforms([si.td.wf.StepWaveform(td)])[0]
        shortStepWf=si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(fl).
            AddLines(['voltagesource VG1 1','device R1 2 R 50.0','device T1 2 tline zc 50.0 td 1e-09',
             'device O1 1 ground','connect R1 1 VG1 1','output T1 1','connect T1 1 R1 2',
             'connect O1 1 T1 2']).TransferMatrices()).\
             ProcessWaveforms([si.td.wf.StepWaveform(td)])[0]
        loadStepWf=si.td.f.TransferMatricesProcessor(si.p.SimulatorNumericParser(fl).
            AddLines(['voltagesource VG1 1','device R1 2 R 50.0','device T1 2 tline zc 50.0 td 1e-09',
             'device O1 1 R 50','connect R1 1 VG1 1','output T1 1','connect T1 1 R1 2',
             'connect O1 1 T1 2']).TransferMatrices()).\
             ProcessWaveforms([si.td.wf.StepWaveform(td)])[0]
        fl=si.fd.EvenlySpacedFrequencyList(10e9,100)
        openSpIp=si.p.SystemSParametersNumericParser(fl).\
            AddLines(['device T1 2 tline zc 50.0 td 1e-09','device O1 1 open',
                      'port 1 T1 1','connect T1 2 O1 1']).SParameters().FrequencyResponse(1,1).ImpulseResponse()
        openSpSp=openSpIp.Integral(scale=False)
        shortSpIp=si.p.SystemSParametersNumericParser(fl).\
            AddLines(['device T1 2 tline zc 50.0 td 1e-09','device O1 1 ground',
                      'port 1 T1 1','connect T1 2 O1 1']).SParameters().FrequencyResponse(1,1).ImpulseResponse()
        shortSpSp=shortSpIp.Integral(scale=False)
        loadSpIp=si.p.SystemSParametersNumericParser(fl).\
            AddLines(['device T1 2 tline zc 50.0 td 1e-09','device O1 1 R 50',
                      'port 1 T1 1','connect T1 2 O1 1']).SParameters().FrequencyResponse(1,1).ImpulseResponse()
        loadSpSp=loadSpIp.Integral(scale=False)

        openStepWf=si.td.wf.Waveform(openStepWf.td,[math.floor(v*2.+0.5)/2. for v in openStepWf])
        shortStepWf=si.td.wf.Waveform(shortStepWf.td,[math.floor(v*2.+0.5)/2. for v in shortStepWf])
        loadStepWf=si.td.wf.Waveform(loadStepWf.td,[math.floor(v*2.+0.5)/2. for v in loadStepWf])
        openSpIp=si.td.wf.Waveform(openSpIp.td,[math.floor(v+0.5) for v in openSpIp])
        shortSpIp=si.td.wf.Waveform(shortSpIp.td,[math.floor(v+0.5) for v in shortSpIp])
        loadSpIp=si.td.wf.Waveform(loadSpIp.td,[math.floor(v+0.5) for v in loadSpIp])
        openSpSp=si.td.wf.Waveform(openSpSp.td,[math.floor(v+0.5) for v in openSpSp])
        shortSpSp=si.td.wf.Waveform(loadSpSp.td,[math.floor(v+0.5) for v in shortSpSp])
        loadSpSp=si.td.wf.Waveform(loadSpSp.td,[math.floor(v+0.5) for v in loadSpSp])

        plotthem=False
        import matplotlib.pyplot as plt
        plt.clf()
        plt.plot(openStepWf.Times('ns'),openStepWf.Values(),label='open',color='black')
        plt.plot(loadStepWf.Times('ns'),loadStepWf.Values(),label='load',color='black')
        plt.plot(shortStepWf.Times('ns'),shortStepWf.Values(),label='short',color='black')
        plt.xlim(-1.0,5.0)
        plt.ylim(-0.2,1.2)
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude (V)')
        plt.legend(loc='upper left')
        #plt.grid(True)
        #si.test.PlotTikZ('GammaStepResponse.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.plot(openSpIp.Times('ns'),openSpIp.Values(),label='open',color='black')
        plt.plot(loadSpIp.Times('ns'),loadSpIp.Values(),label='load',color='black')
        plt.plot(shortSpIp.Times('ns'),shortSpIp.Values(),label='short',color='black')
        plt.xlim(-1.0,5.0)
        plt.ylim(-1.2,1.2)
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude (V)')
        plt.legend(loc='upper left')
        #plt.grid(True)
        #si.test.PlotTikZ('GammaSParameterImpulseResponse.tex', plt)
        if plotthem: plt.show()

        plt.clf()
        plt.plot(openSpSp.Times('ns'),openSpSp.Values(),label='open',color='black')
        plt.plot(loadSpSp.Times('ns'),loadSpSp.Values(),label='load',color='black')
        plt.plot(shortSpSp.Times('ns'),shortSpSp.Values(),label='short',color='black')
        plt.xlim(-1.0,5.0)
        plt.ylim(-1.2,1.2)
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude (V)')
        plt.legend(loc='upper left')
        #plt.grid(True)
        #si.test.PlotTikZ('GammaSParameterImpulseResponseIntegrated.tex', plt)
        if plotthem: plt.show()

        self.WaveformRegressionChecker(openStepWf,self.NameForTest()+'_openStepWf')
        self.WaveformRegressionChecker(shortStepWf,self.NameForTest()+'_shortStepWf')
        self.WaveformRegressionChecker(loadStepWf,self.NameForTest()+'_loadStepWf')
        self.WaveformRegressionChecker(openSpIp,self.NameForTest()+'_openSpIp')
        self.WaveformRegressionChecker(shortSpIp,self.NameForTest()+'_shortSpIp')
        self.WaveformRegressionChecker(loadSpIp,self.NameForTest()+'_loadSpIp')
        self.WaveformRegressionChecker(openSpSp,self.NameForTest()+'_openSpSp')
        self.WaveformRegressionChecker(shortSpSp,self.NameForTest()+'_shortSpSp')
        self.WaveformRegressionChecker(loadSpSp,self.NameForTest()+'_loadSpSp')

if __name__ == "__main__":
    unittest.main()