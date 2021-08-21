"""
TestLeCroyWaveforms.py
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
import numpy as np
import math

class TestLeCroyWaveformsTest(unittest.TestCase):

    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])

    def Check(self,name,wf,wf2,amplitude):
        # calculate a reasonable error
        SNRdB=90. # give it 90 dB dynamic range
        SignaldBm=20.*math.log10(amplitude/math.sqrt(2.))+13.010
        NoisedBm=SignaldBm-SNRdB
        Noiserms=pow(10.,(NoisedBm-13.010)/20.)
        # make the max error three sigma
        wf.epsilon = 3.*Noiserms
        plotThem=False
        if plotThem:
            import matplotlib.pyplot as plt
            plt.plot(wf.Times(),wf.Values(),label='original')
            plt.plot(wf2.Times(),wf2.Values(),label='LeCroy')
            plt.legend()
            plt.show()
        self.assertEqual(wf,wf2,name+': waveforms not equal')

    def testLeCroyWaveforms(self):
        filename='LeCroyWaveform.trc'
        amplitude=1
        td=si.td.wf.TimeDescriptor(-10e-9,200e-9*1e9,1e9)
        wf=si.td.wf.SineWaveform(td,Frequency=100.123456789e6,Amplitude=amplitude)
        wf.WriteLeCroyWaveform(filename)
        wf2=si.td.wf.Waveform().ReadLeCroyWaveform(filename)
        os.remove(filename)
        self.Check(self.NameForTest(), wf, wf2, amplitude)

    def testWriteTrc(self):
        filename='LeCroyWaveform.trc'
        amplitude=1
        td=si.td.wf.TimeDescriptor(-10e-9,200e-9*1e9,1e9)
        wf=si.td.wf.SineWaveform(td,Frequency=100.123456789e6,Amplitude=amplitude)
        wf.WriteToFile(filename)
        wf2=si.td.wf.Waveform().ReadFromFile(filename)
        os.remove(filename)
        self.Check(self.NameForTest(), wf, wf2, amplitude)

    def testLeCroyWaveformsNoExt(self):
        filename='LeCroyWaveform'
        amplitude=1
        td=si.td.wf.TimeDescriptor(-10e-9,200e-9*1e9,1e9)
        wf=si.td.wf.SineWaveform(td,Frequency=100.123456789e6,Amplitude=amplitude)
        wf.WriteLeCroyWaveform(filename)
        wf2=si.td.wf.Waveform().ReadLeCroyWaveform(filename)
        os.remove(filename+'.trc')
        self.Check(self.NameForTest(), wf, wf2, amplitude)

    def testWrongExtWrite(self):
        filename='LeCroyWaveform.wav'
        amplitude=1
        td=si.td.wf.TimeDescriptor(-10e-9,200e-9*1e9,1e9)
        wf=si.td.wf.SineWaveform(td,Frequency=100.123456789e6,Amplitude=amplitude)
        with self.assertRaises(si.SignalIntegrityExceptionWaveformFile) as e:
            wf.WriteLeCroyWaveform(filename)

    def testEmptyWrite(self):
        filename='LeCroyWaveform.trc'
        wf=si.td.wf.Waveform()
        with self.assertRaises(si.SignalIntegrityExceptionWaveformFile) as e:
            wf.WriteLeCroyWaveform(filename)

    def testWrongExtRead(self):
        filename='LeCroyWaveform.wav'
        with self.assertRaises(si.SignalIntegrityExceptionWaveformFile) as e:
            wf2=si.td.wf.Waveform().ReadLeCroyWaveform(filename)

    def testFileNotFound(self):
        filename='nonexistent.trc'
        with self.assertRaises(si.SignalIntegrityExceptionWaveformFile) as e:
            wf2=si.td.wf.Waveform().ReadLeCroyWaveform(filename)

    def testLongWaveform(self):
        filename='LeCroyWaveform.trc'
        amplitude=1
        td=si.td.wf.TimeDescriptor(-10e-9,int(1000000),1e9)
        wf=si.td.wf.SineWaveform(td,Frequency=100.123456789e6,Amplitude=amplitude)
        wf.WriteLeCroyWaveform(filename)
        wf2=si.td.wf.Waveform().ReadLeCroyWaveform(filename)
        os.remove(filename)
        self.Check(self.NameForTest(), wf, wf2, amplitude)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()