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

    def testLeCroyWaveforms(self):
        filename='LeCroyWaveform.trc'
        amplitude=1
        td=si.td.wf.TimeDescriptor(-10e-9,200e-9*1e9,1e9)
        wf=si.td.wf.SineWaveform(td,Frequency=100.123456789e6,Amplitude=amplitude)
        wf.WriteLeCroyWaveform(filename)
        wf2=si.td.wf.Waveform().ReadLeCroyWaveform(filename)
        os.remove(filename)
        # calculate a reasonable error
        SNRdB=90. # give it 80 dB dynamic range
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
        self.assertEqual(wf,wf2,'waveforms not equal')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()