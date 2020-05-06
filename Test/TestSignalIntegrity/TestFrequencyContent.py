"""
TestFrequencyContent.py
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
import math
import os

class TestFrequencyContentTest(unittest.TestCase,si.test.SParameterCompareHelper):
    epsilon=1e-10
    def testFrequencyContentDCSamePoints(self):
        """
        This simple test tests whether a waveform equals the same waveform converted to frequency content and back again
        with no special numbers of points or anything.
        """
        K=20
        td=si.td.wf.TimeDescriptor(-1e-9,K,10e9)
        wf=si.td.wf.Waveform(td,[0 for _ in range(K)])
        wf[td.IndexOfTime(0.0)]=1.
        fc=si.fd.FrequencyContent(wf)
        wf2=fc.Waveform()
        for k in range(len(wf2)):
            if wf2[k]<self.epsilon:
                wf2[k]=0.
        self.assertEqual(wf,wf2,'waveforms not equal')
    def testFrequencyContentDCSamePointsDescriptor(self):
        """
        This simple test tests whether a waveform equals the same waveform converted to frequency content and back again
        with no special numbers of points or anything.  But it does pass in a descriptor to convert back to
        """
        K=20
        td=si.td.wf.TimeDescriptor(-1e-9,K,10e9)
        wf=si.td.wf.Waveform(td,[0 for _ in range(K)])
        wf[td.IndexOfTime(0.0)]=1.
        fc=si.fd.FrequencyContent(wf)
        wf2=fc.Waveform(td)
        for k in range(len(wf2)):
            if wf2[k]<self.epsilon:
                wf2[k]=0.
        self.assertEqual(wf,wf2,'waveforms not equal')
    def testFrequencyContentDCLessPointsReverse(self):
        """
        This test case takes a waveform and converts it to frequency content, but converts it back again using a time
        descriptor with a few points trimmed from each side and compares the result to the original waveform with the same
        points trimmed.
        """
        K=20
        td=si.td.wf.TimeDescriptor(-1e-9,K,10e9)
        wf=si.td.wf.Waveform(td,[0 for _ in range(K)])
        wf[td.IndexOfTime(0.0)]=1.
        fc=si.fd.FrequencyContent(wf)
        wt=si.td.f.WaveformTrimmer(2,2)
        trimmedtd=td*wt
        wf=wf*wt
        wf2=fc.Waveform(trimmedtd)
        for k in range(len(wf2)):
            if wf2[k]<self.epsilon:
                wf2[k]=0.
        self.assertEqual(wf,wf2,'waveforms not equal')
    @unittest.expectedFailure
    def testFrequencyContentDCLessPointsForward(self):
        """
        This test case takes a waveform and converts it to frequency content with a frequency descriptor corresponding to
        the time descriptor with a few points trimmed from each side, then back again, and compares it to the original
        waveform with a few points trimmed from each side.

        This test fails until I decide what I really want to do
        """
        K=20
        td=si.td.wf.TimeDescriptor(-1e-9,K,10e9)
        wf=si.td.wf.Waveform(td,[0 for _ in range(K)])
        wf[td.IndexOfTime(0.0)]=1.
        wt=si.td.f.WaveformTrimmer(2,2)
        trimmedtd=td*wt
        fc=si.fd.FrequencyContent(wf,trimmedtd.FrequencyList())
        wf=wf*wt
        wf2=fc.Waveform(trimmedtd)
        for k in range(len(wf2)):
            if wf2[k]<self.epsilon:
                wf2[k]=0.
        self.assertEqual(wf,wf2,'waveforms not equal')
    def testFrequencyContentLimitedNoLimitSame(self):
        """
        This test checks that the limited content is the same if the
        end frequency is unchanged
        """
        K=20
        Fs=10e9
        td=si.td.wf.TimeDescriptor(-1e-9,K,Fs)
        wf=si.td.wf.Waveform(td,[0 for _ in range(K)])
        wf[td.IndexOfTime(0.0)]=1.
        Fe=Fs/2
        import copy
        fc=wf.FrequencyContent()
        fclimited=copy.deepcopy(fc)
        fclimited.LimitEndFrequency(Fe)
        self.assertEqual(fc,fclimited,'limited content should be equal')
    def testFrequencyContentLimitedNoLimitSlightlyHigher(self):
        """
        This test checks that the limited content is the same if the
        end frequency is unchanged
        """
        K=20
        Fs=10e9
        td=si.td.wf.TimeDescriptor(-1e-9,K,Fs)
        wf=si.td.wf.Waveform(td,[0 for _ in range(K)])
        wf[td.IndexOfTime(0.0)]=1.
        Fe=Fs/2+0.1
        import copy
        fc=wf.FrequencyContent()
        fclimited=copy.copy(fc).LimitEndFrequency(Fe)
        self.assertEqual(fc,fclimited,'limited content should be equal')
    def testFrequencyContentLimitedNoLimitSlightlyLower(self):
        """
        This test checks that the limited content is the same if the
        end frequency is unchanged
        """
        K=20
        Fs=10e9
        td=si.td.wf.TimeDescriptor(-1e-9,K,Fs)
        wf=si.td.wf.Waveform(td,[0 for _ in range(K)])
        wf[td.IndexOfTime(0.0)]=1.
        Fe=Fs/2-0.1
        import copy
        fc=wf.FrequencyContent()
        fclimited=copy.copy(fc).LimitEndFrequency(Fe)
        self.assertEqual(fc,fclimited,'limited content should be equal')
    def testFrequencyContentLimitedNoLimitMuchHigher(self):
        """
        This test checks that the limited content is the same if the
        end frequency is unchanged
        """
        K=20
        Fs=10e9
        td=si.td.wf.TimeDescriptor(-1e-9,K,Fs)
        wf=si.td.wf.Waveform(td,[0 for _ in range(K)])
        wf[td.IndexOfTime(0.0)]=1.
        Fe=Fs
        import copy
        fc=wf.FrequencyContent()
        fclimited=copy.copy(fc).LimitEndFrequency(Fe)
        self.assertEqual(fc,fclimited,'limited content should be equal')
    def testFrequencyContentLimited(self):
        """
        This test checks that the limited content is the same if the
        end frequency is unchanged
        """
        K=20
        Fs=10e9
        td=si.td.wf.TimeDescriptor(-1e-9,K,Fs)
        wf=si.td.wf.Waveform(td,[0 for _ in range(K)])
        wf[td.IndexOfTime(0.0)]=1.
        Fe=Fs/4
        import copy
        fc=wf.FrequencyContent()
        fclimited=copy.copy(fc).LimitEndFrequency(Fe)
        self.assertEqual(len(fclimited),(len(fc)-1)/2+1,'limited content wrong number of points')
        self.assertEqual(fclimited.Frequencies()[-1],Fe,'limited content wrong end frequency')

if __name__ == '__main__':
    unittest.main()

