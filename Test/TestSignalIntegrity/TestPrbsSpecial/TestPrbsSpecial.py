"""
TestPrbsSpecial.py
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
import os

class TestPrbsSpecialTest(unittest.TestCase):
    def testPRBS13Q(self):
        td = si.td.wf.TimeDescriptor(HorOffset=0, NumPts=len(si.prbs.PRBS13QWaveform.pattern)//2, SampleRate = 1)
        prbs13q = si.prbs.PRBS13QWaveform(baudrate=1, amplitude=1, risetime = 0, delay = 0, td=td)
        with open(os.path.dirname(os.path.abspath(__file__))+'/'+'PRBS13Q.txt','rt') as f:
            lines=f.readlines()
        self.assertEqual(len(prbs13q),len(lines),'PRBS13Q waveform length incorrect')
        for k in range(len(lines)):
            lines[k]=float(lines[k].strip())
        self.assertEqual(prbs13q.Values(),lines,'PRBS13Q waveform incorrect')
    def testSSPRQ(self):
        td = si.td.wf.TimeDescriptor(HorOffset=0, NumPts=len(si.prbs.SSPRQWaveform.pattern)//2, SampleRate = 1)
        ssprq = si.prbs.SSPRQWaveform(baudrate=1, amplitude=1, risetime = 0, delay = 0, td=td)
        with open(os.path.dirname(os.path.abspath(__file__))+'/'+'SSPRQ.txt','rt') as f:
            lines=f.readlines()
        self.assertEqual(len(ssprq),len(lines),'SSPRQ waveform length incorrect')
        for k in range(len(lines)):
            lines[k]=float(lines[k].strip())
        self.assertEqual(ssprq.Values(),lines,'SSPRQ waveform incorrect')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()