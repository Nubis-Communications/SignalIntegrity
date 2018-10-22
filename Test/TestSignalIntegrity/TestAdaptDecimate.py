"""
TestAdaptDecimate.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
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
from TestHelpers import *
import numpy as np
import math

class TestAdaptDecimate(unittest.TestCase,RoutineWriterTesterHelper,ResponseTesterHelper,SourcesTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def tearDown(self):
        si.td.wf.Waveform.adaptionStrategy='SinX'
    def testAdaptDecimatebyHand(self):
        td=si.td.wf.TimeDescriptor(-1e-6,2000,1e9)
        wf=si.td.wf.SineWaveform(td)
        wf.adaptionStrategy='Linear'
        tda=si.td.wf.TimeDescriptor(td.H+20.76543/td.Fs,td.K/50-10,td.Fs/50.0)
        wfdes=si.td.wf.SineWaveform(tda)

        ad=tda/wf.TimeDescriptor()
        f=ad.D-int(ad.D)
        if not f==0.0:
            wffd=wf*(si.td.f.FractionalDelayFilterSinX(f,True) if wf.adaptionStrategy=='SinX'
                else si.td.f.FractionalDelayFilterLinear(f,True))
        else:
            wffd=wf
        td=wffd.TimeDescriptor()

        ad=tda/wffd.TimeDescriptor()
        df=int(round(1/ad.U))
        dph= int(round(ad.TrimLeft())) % df
        v=wffd.Values()
        dv=[v[k*df+dph] for k in range((len(v)-dph)/df)]
        tdd=si.td.wf.TimeDescriptor(td.H+dph/td.Fs,len(dv),td.Fs/df)
        wfd=si.td.wf.Waveform(tdd,dv)

        ad=tda/wfd.TimeDescriptor()
        tr=si.td.f.WaveformTrimmer(max(0,int(round(ad.TrimLeft()))),
                           max(0,int(round(ad.TrimRight()))))
        wfa=wfd*tr

        fb=tda/wfa.TimeDescriptor()

        plotit=False
        if plotit:
            fb.Print()
            import matplotlib.pyplot as plt
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(wf.Times('ns'),wf.Values(),label='input waveform')
            plt.plot(wfdes.Times('ns'),wfdes.Values(),marker='o',label='desired waveform')
            plt.plot(wfa.Times('ns'),wfa.Values(),label='adapted waveform')
            plt.legend(loc='upper right')
            plt.show()
        else:
            self.assertEqual(tda, wfa.TimeDescriptor(), 'desired time descriptor not met')
            self.assertEqual(len(wfa.Values()),len(wfdes.Values()),msg='waveforms are not the same size!')
            for k in range(len(wfa)):
                self.assertAlmostEqual(wfa[k], wfdes[k],delta=1e-5,msg='desired waveform not the same by: '+str(abs(wfa[k]-wfdes[k])))

    def testAdaptDecimatePySI(self):
        td=si.td.wf.TimeDescriptor(-1e-6,2000,1e9)
        wf=si.td.wf.SineWaveform(td)
        wf.adaptionStrategy='Linear'
        tda=si.td.wf.TimeDescriptor(td.H+20.76543/td.Fs,td.K/50-10,td.Fs/50.0)
        wfdes=si.td.wf.SineWaveform(tda)

        wfa=wf.Adapt(tda)

        fb=tda/wfa.TimeDescriptor()

        plotit=False
        if plotit:
            fb.Print()
            import matplotlib.pyplot as plt
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(wf.Times('ns'),wf.Values(),label='input waveform')
            plt.plot(wfdes.Times('ns'),wfdes.Values(),marker='o',label='desired waveform')
            plt.plot(wfa.Times('ns'),wfa.Values(),label='adapted waveform')
            plt.legend(loc='upper right')
            plt.show()
        else:
            self.assertEqual(tda, wfa.TimeDescriptor(), 'desired time descriptor not met')
            self.assertEqual(len(wfa.Values()),len(wfdes.Values()),msg='waveforms are not the same size!')
            for k in range(len(wfa)):
                self.assertAlmostEqual(wfa[k], wfdes[k],delta=1e-5,msg='desired waveform not the same by: '+str(abs(wfa[k]-wfdes[k])))

    def testUpsampleDecimatePySI(self):
        td=si.td.wf.TimeDescriptor(-1e-6,2000,1e9)
        wf=si.td.wf.SineWaveform(td)
        wf.adaptionStrategy='Linear'
        tda=si.td.wf.TimeDescriptor(td.H+130.76543/td.Fs,td.K*0.08-20,80e6)
        wfdes=si.td.wf.SineWaveform(tda)

        wfa=wf.Adapt(tda)

        fb=tda/wfa.TimeDescriptor()

        plotit=False
        if plotit:
            fb.Print()
            import matplotlib.pyplot as plt
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(wf.Times('ns'),wf.Values(),label='input waveform')
            plt.plot(wfdes.Times('ns'),wfdes.Values(),marker='o',label='desired waveform')
            plt.plot(wfa.Times('ns'),wfa.Values(),label='adapted waveform')
            plt.legend(loc='upper right')
            plt.show()
        else:
            self.assertEqual(tda, wfa.TimeDescriptor(), 'desired time descriptor not met')
            self.assertEqual(len(wfa.Values()),len(wfdes.Values()),msg='waveforms are not the same size!')
            for k in range(len(wfa)):
                self.assertAlmostEqual(wfa[k], wfdes[k],delta=1e-5,msg='desired waveform not the same by: '+str(abs(wfa[k]-wfdes[k])))

if __name__ == "__main__":
    unittest.main()