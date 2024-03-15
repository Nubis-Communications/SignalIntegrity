"""
TestResponse.py
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
from numpy import empty
import os
import math
import cmath
import matplotlib.pyplot as plt

class TestResponse(unittest.TestCase,si.test.ResponseTesterHelper):
    def id(self):
        return '.'.join(unittest.TestCase.id(self).split('.')[-3:])
    def testResampleResponseCompareSpline(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        newf=si.fd.EvenlySpacedFrequencyList(100*100e6,100)
        tdsp=si.sp.SParameterFile('TestDut.s4p',50.)
        tdspres1=tdsp.Resample(newf)

        tdresp = [[tdsp.Response(o+1,i+1) for o in range(tdsp.m_P)] for i in range(tdsp.m_P)]
        tdrespf = tdsp.f()

        tdrespres = [[si.fd.FrequencyResponse(tdrespf,tdresp[o][i]).Resample(newf)
            for o in range(tdsp.m_P)] for i in range(tdsp.m_P)]

        tddres2=[empty((tdsp.m_P,tdsp.m_P)).tolist() for np in range(len(newf))]
        for np in range(len(newf)):
            for o in range(len(tdrespres)):
                for i in range(len(tdrespres[0])):
                    tddres2[np][o][i]=tdrespres[o][i][np]

        tdspres2 = si.sp.SParameters(newf,tddres2)

##        tdspres1.WriteToFile('tdspres1spline.s4p')
##        tdspres2.WriteToFile('tdspres2spline.s4p')
        self.assertTrue(self.SParametersAreEqual(tdspres1,tdspres2,0.001),self.id()+'result not same')
    def testResampleResponseCompareCZT(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        newf=si.fd.EvenlySpacedFrequencyList(100*100e6,100)
        tdsp=si.sp.SParameterFile('TestDut.s4p',50.)
        tdspres1=tdsp.Resample(newf)

        tdresp = [[tdsp.Response(o+1,i+1) for o in range(tdsp.m_P)] for i in range(tdsp.m_P)]
        tdrespf = tdsp.f()

        tdrespres = [[si.fd.FrequencyResponse(tdrespf,tdresp[o][i]).Resample(newf)
            for o in range(tdsp.m_P)] for i in range(tdsp.m_P)]

        tddres2=[empty((tdsp.m_P,tdsp.m_P)).tolist() for np in range(len(newf))]
        for np in range(len(newf)):
            for o in range(len(tdrespres)):
                for i in range(len(tdrespres[0])):
                    tddres2[np][o][i]=tdrespres[o][i][np]

        tdspres2 = si.sp.SParameters(newf,tddres2)

##        tdspres1.WriteToFile('tdspres1czt.s4p')
##        tdspres2.WriteToFile('tdspres2czt.s4p')
        self.assertTrue(self.SParametersAreEqual(tdspres1,tdspres2,0.001),self.id()+'result not same')
    def testResampleResponseCompareCZT2(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        newf=si.fd.EvenlySpacedFrequencyList(100*100e6,100)
        tdsp=si.sp.SParameterFile('TestDut.s4p',50.)
        tdspres1=tdsp.Resample(newf)

        tdresp = [[tdsp.Response(o+1,i+1) for o in range(tdsp.m_P)] for i in range(tdsp.m_P)]
        tdrespf = tdsp.f()

        tdrespres = [[si.fd.FrequencyResponse(tdrespf,tdresp[o][i]).Resample(newf)
            for o in range(tdsp.m_P)] for i in range(tdsp.m_P)]

        tddres2=[empty((tdsp.m_P,tdsp.m_P)).tolist() for np in range(len(newf))]
        for np in range(len(newf)):
            for o in range(len(tdrespres)):
                for i in range(len(tdrespres[0])):
                    tddres2[np][o][i]=tdrespres[o][i][np]

        tdspres2 = si.sp.SParameters(newf,tddres2)

##        tdspres1.WriteToFile('tdspres1czt2.s4p')
##        tdspres2.WriteToFile('tdspres2czt2.s4p')
        self.assertTrue(self.SParametersAreEqual(tdspres1,tdspres2,0.001),self.id()+'result not same')
    def testResampleResponseFilter(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        filtersp=si.sp.SParameterFile('filter.s2p',50.)
        filtersp=filtersp.Resample(si.fd.EvenlySpacedFrequencyList(2e9,200))
        filterres=filtersp.Resample(si.fd.EvenlySpacedFrequencyList(2e9,4000))
        if not os.path.exists('filterres.s2p'):
            filterres.WriteToFile('filterres.s2p')
        regression=si.sp.SParameterFile('filterres.s2p',50.)
        self.assertTrue(self.SParametersAreEqual(filterres,regression,0.001),self.id()+'result not same')
    def irc(self):
        x = [0,0,0,0,0,0,0,0,0,0,1.5,0,-0.5,0,0,0,0,0,0,0]
        td = si.td.wf.TimeDescriptor(-9.8,20,1.)
        return si.td.wf.ImpulseResponse(td,x)
    def frc(self):
        return self.irc().FrequencyResponse()
    def Checkit(self,selfid,x,origin=None,plotResponseResults=False):
        plotResponseResults=plotResponseResults or False
        fileName = '_'.join(selfid.split('.')) + '.txt'
        fileName = ('_'.join(selfid.split('.')[2:])).replace('test','') + '.txt'
        if isinstance(x,si.fd.FrequencyResponse):
            fileName='FrequencyResponse_'+fileName
            if plotResponseResults == True:
                regression = self.GetFrequencyResponseResult(fileName)
                plt.clf()
                plt.title(fileName)
                plt.xlabel('frequency')
                plt.ylabel('magnitude')
                if not origin is None:
                    plt.plot(origin.Frequencies(),origin.Response('mag'),linewidth=3.0,label='origin')
                plt.plot(x.Frequencies(),x.Response('mag'),marker='o',label='result')
                if not regression is None:
                    plt.plot(regression.Frequencies(),regression.Response('mag'),label='regression')
                plt.legend(loc='upper right')
                plt.show()
                plt.clf()
                plt.title(fileName)
                plt.xlabel('frequency')
                plt.ylabel('phase (deg)')
                if not origin is None:
                    plt.plot(origin.Frequencies(),origin.Response('deg'),linewidth=3.0,label='origin')
                plt.plot(x.Frequencies(),x.Response('deg'),marker='o',label='original')
                if not regression is None:
                    plt.plot(regression.Frequencies(),regression.Response('deg'),label='regression')
                plt.legend(loc='upper right')
                plt.show()
            self.CheckFrequencyResponseResult(x,fileName,fileName+' incorrect')
        if isinstance(x,si.td.wf.Waveform):
            fileName='Waveform_'+fileName
            if plotResponseResults == True:
                regression = self.GetWaveformResult(fileName)
                plt.clf()
                plt.title(fileName)
                plt.xlabel('time')
                plt.ylabel('amplitude')
                if not origin is None:
                    plt.plot(origin.Times(),origin.Values(),linewidth=3.0,label='origin')
                plt.plot(x.Times(),x.Values(),marker='o',label='result')
                if not regression is None:
                    plt.plot(regression.Times(),regression.Values(),label='regression')
                plt.legend(loc='upper right')
                plt.show()
            self.CheckWaveformResult(x,fileName,fileName+' incorrect')
    def testfrc(self):
        frc=self.frc()
        self.Checkit(self.id(),frc,None,False)
    def testfrcSumCosines(self):
        frc=self.frc()
        f=frc.FrequencyList()
        irc=self.irc()
        t=irc.TimeDescriptor()
        cs=[1./t.K*sum([abs(frc[n])*(2. if 0<n<f.N else 1.)*math.cos(2.*math.pi*f[n]*t[k]+cmath.phase(frc[n])) for n in range(len(f))]) for k in range(len(t))]
        irc2=si.td.wf.ImpulseResponse(t,cs)
        self.Checkit(self.id(),irc2,irc,False)
    def testfrcWriteRead(self):
        frc=self.frc()
        frc.WriteToFile('frcwr.txt')
        frc2=si.fd.FrequencyResponse().ReadFromFile('frcwr.txt')
        os.remove('frcwr.txt')
        self.Checkit(self.id(),frc2,frc,False)
    def testRes_N_10_Fe_0p5(self):
        Np=10
        Fep=0.5
        frc=self.frc()
        frr=frc.Resample(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np),False)
        self.Checkit(self.id(),frr,frc,False)
    def testRes_N_9_Fe_0p45(self):
        Np=9
        Fep=0.45
        frc=self.frc()
        frr=frc.Resample(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np),False)
        self.Checkit(self.id(),frr,frc,False)
    def testRes_N_20_Fe_0p5(self):
        Np=20
        Fep=0.5
        frc=self.frc()
        frr=frc.Resample(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np),False)
        self.Checkit(self.id(),frr,frc,False)
    def testRes_N_20_Fe_1(self):
        Np=20
        Fep=1.
        frc=self.frc()
        frr=frc.Resample(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np),False)
        self.Checkit(self.id(),frr,frc,False)
    def testRes_N_53_Fe_0p435(self):
        Np=53
        Fep=0.435
        frc=self.frc()
        frr=frc.Resample(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np),False)
        self.Checkit(self.id(),frr,frc,False)
    def testRes_N_23_Fe_0p6(self):
        Np=23
        Fep=0.6
        frc=self.frc()
        frr=frc.Resample(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np),False)
        self.Checkit(self.id(),frr,frc,False)
    def testirc(self):
        irc=self.irc()
        self.Checkit(self.id(),irc,None,False)
    def testRes_K_20_Fs_1(self):
        Kp=20
        Fsp=1.0
        irc=self.irc()
        irr=irc.Resample(si.td.wf.TimeDescriptor(0,Kp,Fsp))
        self.Checkit(self.id(),irr,irc,False)
    def testRes_K_106_Fs_1p345(self):
        Kp=106
        Fsp=1.345
        irc=self.irc()
        irr=irc.Resample(si.td.wf.TimeDescriptor(0,Kp,Fsp))
        self.Checkit(self.id(),irr,irc,False)
    def testRes_K_106_Fs_1p345_fr(self):
        Kp=106
        Fsp=1.345
        irc=self.irc()
        irr=irc.Resample(si.td.wf.TimeDescriptor(0,Kp,Fsp))
        frc=irc.FrequencyResponse()
        frr=irr.FrequencyResponse()
        self.Checkit(self.id(),frr,frc,False)
    def testRes_Fs_2(self):
        Kp=0
        Fsp=2.
        irc=self.irc()
        irr=irc.Resample(Fsp)
        self.Checkit(self.id(),irr,irc,False)
    def testRes_Fs_1(self):
        Kp=0
        Fsp=1.
        irc=self.irc()
        irr=irc.Resample(Fsp)
        self.Checkit(self.id(),irr,irc,False)
    def testResUneven(self):
        frc=self.frc()
        f=frc.FrequencyList().Frequencies()
        r=frc.Response()
        del f[3]
        del r[3]
        frc2=si.fd.FrequencyResponse(f,r)
        self.Checkit(self.id(),frc2,None,False)
    def testResUneven_N_20_Fe_0p5(self):
        Np=20
        Fep=0.5
        frc=self.frc()
        f=frc.FrequencyList().Frequencies()
        r=frc.Response()
        del f[3]
        del r[3]
        frc2=si.fd.FrequencyResponse(f,r)
        frr=frc2.Resample(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc2,False)
    def testResUneven_Fs_1(self):
        Fsp=1
        frc=self.frc()
        irc=frc.ImpulseResponse()
        f=frc.FrequencyList().Frequencies()
        r=frc.Response()
        del f[3]
        del r[3]
        frc2=si.fd.FrequencyResponse(f,r)
        irr=frc2.ImpulseResponse(Fsp)
        self.Checkit(self.id(),irr,irc,False)
    def testfrcUnevenWriteRead(self):
        frc=self.frc()
        f=frc.FrequencyList().Frequencies()
        r=frc.Response()
        del f[3]
        del r[3]
        frc=si.fd.FrequencyResponse(f,r).WriteToFile('frcwr.txt')
        frc2=si.fd.FrequencyResponse().ReadFromFile('frcwr.txt')
        os.remove('frcwr.txt')
        self.Checkit(self.id(),frc2,frc,False)
    def testfrcne(self):
        frc=self.frc()
        frc2=frc
        self.assertTrue(not frc != frc2,self.id()+'result not same')
    def testircTrim(self):
        irc=self.irc()
        irc2=irc.TrimToThreshold(0.01)
        self.Checkit(self.id(),irc2,irc,False)
    def testircTrimTofrToir(self):
        irc=self.irc()
        irc2=irc.TrimToThreshold(0.01)
        irc2=irc2.FrequencyResponse().ImpulseResponse()
        self.Checkit(self.id(),irc2,irc,False)
    def testircTrimTofr(self):
        irc=self.irc()
        frc=irc.FrequencyResponse()
        irc2=irc.TrimToThreshold(0.01)
        frc2=irc2.FrequencyResponse()
        self.Checkit(self.id(),frc2,frc,False)
    def testircTrimTofrResample(self):
        irc=self.irc()
        frc=irc.FrequencyResponse()
        irc2=irc.TrimToThreshold(0.01)
        frc2=irc2.FrequencyResponse(frc.FrequencyList())
        self.Checkit(self.id(),frc2,frc,False)
    def testTrimPathological1(self):
        ir=si.td.wf.ImpulseResponse(si.td.wf.TimeDescriptor(-1,3,1),[1,2,3])
        ir=ir.TrimToThreshold(0.001)
        self.Checkit(self.id(),ir,None,False)
    def testTrimPathological2(self):
        ir=si.td.wf.ImpulseResponse(si.td.wf.TimeDescriptor(-1,4,1),[1,2,3,0])
        ir=ir.TrimToThreshold(0.001)
        self.Checkit(self.id(),ir,None,False)
    def testTrimPathological3(self):
        ir=si.td.wf.ImpulseResponse(si.td.wf.TimeDescriptor(-1,4,1),[0,1,2,3])
        ir=ir.TrimToThreshold(0.001)
        self.Checkit(self.id(),ir,None,False)
    def testResponsedB(self):
        fr=self.frc()
        mag=fr.Response('mag')
        dB=fr.Response('dB')
        corr=[20.*math.log10(magv) for magv in mag]
        regression=si.fd.FrequencyResponse(fr.FrequencyList(),corr)
        calc=si.fd.FrequencyResponse(fr.FrequencyList(),dB)
        self.assertTrue(regression == calc,'dB incorrect')
    def testResponseMag(self):
        fr=self.frc()
        r=fr.Response()
        mag=fr.Response('mag')
        corr=[abs(rv) for rv in r]
        regression=si.fd.FrequencyResponse(fr.FrequencyList(),corr)
        calc=si.fd.FrequencyResponse(fr.FrequencyList(),mag)
        self.assertTrue(regression == calc,'mag incorrect')
    def testResponseRI(self):
        fr=self.frc()
        re=fr.Response('real')
        im=fr.Response('imag')
        corr=[v[0]+1j*v[1] for v in zip(re,im)]
        regression=si.fd.FrequencyResponse(fr.FrequencyList(),corr)
        calc=fr
        self.assertTrue(regression == calc,'real/imag incorrect')
    def testResponsedeg(self):
        fr=self.frc()
        deg=fr.Response('deg')
        rad=fr.Response('rad')
        corr=[v/2./math.pi*360.0 for v in rad]
        regression=si.fd.FrequencyResponse(fr.FrequencyList(),corr)
        calc=si.fd.FrequencyResponse(fr.FrequencyList(),deg)
        self.assertTrue(regression == calc,'deg incorrect')
    def testfrpadnone(self):
        fr=self.frc()
        fr2=fr._Pad(fr.FrequencyList().N)
        self.assertTrue(len(fr)==len(fr2),'pad no points incorrect')
        self.assertTrue(all([r==r2 for (r,r2) in zip(fr,fr2)]),'pad no points incorrect')
    def testResUnevenNoDescriptor(self):
        frc=self.frc()
        f=frc.FrequencyList().Frequencies()
        r=frc.Response()
        del f[3]
        del r[3]
        frc2=si.fd.FrequencyResponse(f,r)
        irr=frc2.ImpulseResponse()
        self.assertTrue(irr is None,'uneven points no descriptor incorrect')
    def testRes_N_11_Fe_0p5(self):
        Np=11
        Fep=0.5
        frc=self.frc()
        frr=frc.Resample(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np),False)
        self.Checkit(self.id(),frr,frc,False)
    def testRes_N_11_Fe_0p45(self):
        Np=11
        Fep=0.45
        frc=self.frc()
        frr=frc.Resample(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np))
        self.Checkit(self.id(),frr,frc,False)
        frr=frc.ResampleCZT(si.fd.EvenlySpacedFrequencyList(Fep,Np),False)
        self.Checkit(self.id(),frr,frc,False)
    def test_SparqResampling(self):
        K=10240
        Fs=5e6*40960
        td=si.td.wf.TimeDescriptor(0.,K,Fs)
        x=[1. for k in range(K)]
        ir=si.td.wf.ImpulseResponse(td,x)
        fr=ir.FrequencyResponse(si.fd.EvenlySpacedFrequencyList(40e9,8000))
        pass
    def testTimeDelay(self):
        irc=self.irc()
        TD1=irc._FractionalDelayTime()
        frc=irc.FrequencyResponse()
        TD2=frc._FractionalDelayTime()
        self.assertAlmostEqual(TD1,TD2,None,'TimeDelay incorrect')
if __name__ == '__main__':
    unittest.main()