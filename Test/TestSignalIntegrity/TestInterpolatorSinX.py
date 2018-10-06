"""
TestInterpolatorSinX.py
"""

# Copyright (c) 2018 Teledyne LeCroy, all rights reserved worldwide.
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
from numpy import linalg
from numpy import array
from numpy import matrix
from numpy import fft
from numpy import convolve
import copy
import math
import os

import matplotlib.pyplot as plt

from TestHelpers import *

PlotTestInterpolator=False
PlotRegression=True

class TestInterpolatorSinX(unittest.TestCase,ResponseTesterHelper):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
    def id(self):
        return '.'.join(unittest.TestCase.id(self).split('.')[-3:])
    def testDelaySinX(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        CableTxPWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.td.wf.TimeDescriptor(0,500,20.))
        CableTxPWfDelayed=CableTxPWf.DelayBy(0.3/CableTxPWf.TimeDescriptor().Fs)
        if PlotTestInterpolator:
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(CableTxPWfDelayed.Times('ns'),CableTxPWfDelayed.Values(),label='delayed by 0.3 samples added to HorOffset')
            plt.plot(CableTxPWf.Times('ns'),CableTxPWf.Values(),label='not delayed')
            if PlotRegression:
                regression=si.td.wf.Waveform().ReadFromFile(fileNameBase+'.txt')
                plt.plot(regression.Times('ns'),regression.Values(),label='regression')
            plt.legend(loc='upper right')
            plt.show()
        self.CheckWaveformResult(CableTxPWfDelayed,fileNameBase+'.txt',fileNameBase)
    def testResampleNoDelaySinX(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        CableTxPWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxP.txt')
        CableTxPWfDelayed=CableTxPWf.DelayBy(0.0/CableTxPWf.TimeDescriptor().Fs)
        CableTxPWfDelayed2=si.td.f.InterpolatorFractionalDelayFilterSinX(1,0.0).FilterWaveform(CableTxPWf)
        if PlotTestInterpolator:
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(CableTxPWfDelayed.Times('ns'),CableTxPWfDelayed.Values(),label='delayed by 0 added to HorOffset')
            plt.plot(CableTxPWfDelayed2.Times('ns'),CableTxPWfDelayed2.Values(),label='delayed by fractional delay of 0')
            if PlotRegression:
                regression=si.td.wf.Waveform().ReadFromFile(fileNameBase+'.txt')
                plt.plot(regression.Times('ns'),regression.Values(),label='regression')
            plt.legend(loc='upper right')
            plt.show()
        self.CheckWaveformResult(CableTxPWfDelayed,fileNameBase+'.txt',fileNameBase)
        self.CheckWaveformResult(CableTxPWfDelayed2,fileNameBase+'2.txt',fileNameBase+'2')
    def testResampleSinX(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        CableTxPWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.td.wf.TimeDescriptor(5,0,20.))
        FractionalDelay=0.3
        CableTxPWfDelayed=CableTxPWf.DelayBy(FractionalDelay/CableTxPWf.TimeDescriptor().Fs)
        CableTxPWfDelayed2=si.td.f.InterpolatorFractionalDelayFilterSinX(1,FractionalDelay,accountForDelay=True).FilterWaveform(CableTxPWf)
        CableTxPWfDelayed3=si.td.f.InterpolatorFractionalDelayFilterSinX(1,FractionalDelay,accountForDelay=True).FilterWaveform(CableTxPWf)
        CableTxPWfDelayed3=CableTxPWfDelayed3.DelayBy(FractionalDelay/CableTxPWfDelayed3.TimeDescriptor().Fs)
        CableTxPWfDelayed4=si.td.f.InterpolatorFractionalDelayFilterSinX(1,FractionalDelay,accountForDelay=False).FilterWaveform(CableTxPWf)
        if PlotTestInterpolator:
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(CableTxPWf.Times('ns'),CableTxPWf.Values(),label='original waveform')
            plt.plot(CableTxPWfDelayed.Times('ns'),CableTxPWfDelayed.Values(),label='delayed by HorOffset')
            plt.plot(CableTxPWfDelayed2.Times('ns'),CableTxPWfDelayed2.Values(),label='sample phase changed')
            plt.plot(CableTxPWfDelayed3.Times('ns'),CableTxPWfDelayed3.Values(),label='sample phase changed + delayed')
            plt.plot(CableTxPWfDelayed4.Times('ns'),CableTxPWfDelayed4.Values(),label='fractionally delayed')
            plt.legend(loc='upper right')
            plt.show()
        self.CheckWaveformResult(CableTxPWfDelayed,fileNameBase+'.txt',fileNameBase)
        self.CheckWaveformResult(CableTxPWfDelayed2,fileNameBase+'2.txt',fileNameBase+'2')
        self.CheckWaveformResult(CableTxPWfDelayed3,fileNameBase+'3.txt',fileNameBase+'3')
        self.CheckWaveformResult(CableTxPWfDelayed4,fileNameBase+'4.txt',fileNameBase+ '4')
    def testChangeSamplePhaseSinX(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        # to change the sample phase, fractionally delay the waveform - the filter descriptor makes it so
        # the waveform is not actually delayed!  i.e. it accounts for and undoes the delay effect
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        CableTxPWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.td.wf.TimeDescriptor(0,500,20.))
        CableTxPWfDelayed=si.td.f.InterpolatorFractionalDelayFilterSinX(1,0.3,accountForDelay=True).FilterWaveform(CableTxPWf)
        CableTxPWfDelayed=CableTxPWfDelayed.DelayBy(0.0/CableTxPWfDelayed.TimeDescriptor().Fs)
        if PlotTestInterpolator:
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(CableTxPWf.Times('ns'),CableTxPWf.Values(),label='original waveform')
            plt.plot(CableTxPWfDelayed.Times('ns'),CableTxPWfDelayed.Values(),label='sample phase changed by 0.3 samples')
            if PlotRegression:
                regression=si.td.wf.Waveform().ReadFromFile(fileNameBase+'.txt')
                plt.plot(regression.Times('ns'),regression.Values(),label='regression')
            plt.legend(loc='upper right')
            plt.show()
        self.CheckWaveformResult(CableTxPWfDelayed,fileNameBase+'.txt',fileNameBase)
    def testUpsampleNoDelaySinX(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        CableTxPWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.td.wf.TimeDescriptor(0,500,20.))
        CableTxPWfUpsampled=si.td.f.InterpolatorFractionalDelayFilterSinX(10,0.0).FilterWaveform(CableTxPWf)
        if PlotTestInterpolator:
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(CableTxPWf.Times('ns'),CableTxPWf.Values(),marker='s',label='original waveform')
            plt.plot(CableTxPWfUpsampled.Times('ns'),CableTxPWfUpsampled.Values(),marker='o',label='upsampled by 10')
            if PlotRegression:
                regression=si.td.wf.Waveform().ReadFromFile(fileNameBase+'.txt')
                plt.plot(regression.Times('ns'),regression.Values(),label='regression')
            plt.legend(loc='upper right')
            plt.show()
        self.CheckWaveformResult(CableTxPWfUpsampled,fileNameBase+'.txt',fileNameBase)
    def testUpsampleDelaySinX(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        CableTxPWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.td.wf.TimeDescriptor(0,500,20.))
        CableTxPWfUpsampled=si.td.f.InterpolatorFractionalDelayFilterSinX(10,0.3).FilterWaveform(CableTxPWf)
        if PlotTestInterpolator:
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(CableTxPWf.Times('ns'),CableTxPWf.Values(),marker='s',label='original waveform')
            plt.plot(CableTxPWfUpsampled.Times('ns'),CableTxPWfUpsampled.Values(),marker='o',label='upsampled by 10 + sample phase')
            if PlotRegression:
                regression=si.td.wf.Waveform().ReadFromFile(fileNameBase+'.txt')
                plt.plot(regression.Times('ns'),regression.Values(),label='regression')
            plt.legend(loc='upper right')
            plt.show()
        self.CheckWaveformResult(CableTxPWfUpsampled,fileNameBase+'.txt',fileNameBase)
    def testUpsamplingFilterSinX(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        ft=si.td.f.InterpolatorSinX(10).FilterTaps()
        if PlotTestInterpolator:
            plt.clf()
            plt.xlabel('sample')
            plt.ylabel('coefficient')
            plt.plot([k for k in range(len(ft))],ft,marker='s',label='10x upsampling filter')
            plt.legend(loc='upper right')
            plt.show()
        #self.CheckWaveformResult(CableTxPWfUpsampled,fileNameBase+'.txt',fileNameBase)

if __name__ == '__main__':
    unittest.main()
