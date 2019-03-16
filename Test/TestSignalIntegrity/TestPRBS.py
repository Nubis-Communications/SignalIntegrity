"""
TestPRBS.py
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
import sys
import os
import unittest
import SignalIntegrity.Lib as si

class TestPRBSTest(unittest.TestCase,si.test.SignalIntegrityAppTestHelper):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
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
        samplesPerUI=100
        amplitude=0.5
        delay=0.
        wf=si.prbs.PseudoRandomWaveform(7,bitrate,amplitude,risetime,delay,bitrate*samplesPerUI)
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


if __name__ == "__main__":
    unittest.main()