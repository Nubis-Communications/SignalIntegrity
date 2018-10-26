"""
TestInterpolatorLinear.py
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

import copy
import os

import matplotlib.pyplot as plt

PlotTestInterpolatorLinear=False
PlotRegression=True

class TestInterpolatorLinear(unittest.TestCase,si.test.ResponseTesterHelper):
    def id(self):
        return '.'.join(unittest.TestCase.id(self).split('.')[-3:])
    def testDelayLinear(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        CableTxPWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.td.wf.TimeDescriptor(0,50,20.))
        CableTxPWfDelayed=CableTxPWf.DelayBy(0.3/CableTxPWf.TimeDescriptor().Fs)
        if PlotTestInterpolatorLinear:
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
    def testResampleNoDelayLinear(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        CableTxPWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxP.txt')
        CableTxPWfDelayed=copy.deepcopy(CableTxPWf)
        CableTxPWfDelayed.DelayBy(0.0/CableTxPWfDelayed.TimeDescriptor().Fs)
        CableTxPWfDelayed2=si.td.f.InterpolatorFractionalDelayFilterLinear(1,0.0).ProcessWaveform(CableTxPWf)
        if PlotTestInterpolatorLinear:
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(CableTxPWfDelayed.Times('ns'),CableTxPWfDelayed.Values(),label='delayed by 0 added to HorOffset')
            plt.plot(CableTxPWfDelayed2.Times('ns'),CableTxPWfDelayed2.Values(),label='delayed by fractional delay of 0')
            if PlotRegression:
                regression=si.td.wf.Waveform().ReadFromFile(fileNameBase+'.txt')
                plt.plot(regression.Times('ns'),regression.Values(),label='regression')
                regression2=si.td.wf.Waveform().ReadFromFile(fileNameBase+'2.txt')
                plt.plot(regression.Times('ns'),regression.Values(),label='regression2')
            plt.legend(loc='upper right')
            plt.show()
        self.CheckWaveformResult(CableTxPWfDelayed,fileNameBase+'.txt',fileNameBase)
        self.CheckWaveformResult(CableTxPWfDelayed2,fileNameBase+'2.txt',fileNameBase+'2')
    def testResampleLinear(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        CableTxPWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.td.wf.TimeDescriptor(5,0,20.))
        FractionalDelay=0.3
        CableTxPWfDelayed=CableTxPWf.DelayBy(FractionalDelay/CableTxPWf.TimeDescriptor().Fs)
        CableTxPWfDelayed2=si.td.f.InterpolatorFractionalDelayFilterLinear(1,FractionalDelay,accountForDelay=True).FilterWaveform(CableTxPWf)
        CableTxPWfDelayed3=si.td.f.InterpolatorFractionalDelayFilterLinear(1,FractionalDelay,accountForDelay=True).FilterWaveform(CableTxPWf)
        CableTxPWfDelayed3=CableTxPWfDelayed3.DelayBy(FractionalDelay/CableTxPWfDelayed3.TimeDescriptor().Fs)
        CableTxPWfDelayed4=si.td.f.InterpolatorFractionalDelayFilterLinear(1,FractionalDelay,accountForDelay=False).FilterWaveform(CableTxPWf)
        if PlotTestInterpolatorLinear:
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
    def testChangeSamplePhaseLinear(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        # to change the sample phase, fractionally delay the waveform - the filter descriptor makes it so
        # the waveform is not actually delayed!  i.e. it accounts for and undoes the delay effect
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        CableTxPWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.td.wf.TimeDescriptor(0,50,20.))
        #CableTxPWfDelayed=copy.deepcopy(CableTxPWf)
        CableTxPWfDelayed=si.td.f.InterpolatorFractionalDelayFilterLinear(1,0.3,accountForDelay=True).FilterWaveform(CableTxPWf)
        #CableTxPWfDelayed.DelayBy(0.0/CableTxPWfDelayed.TimeDescriptor().Fs)
        if PlotTestInterpolatorLinear:
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
    def testChangeSamplePhaseLinearNegative(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        # to change the sample phase, fractionally delay the waveform - the filter descriptor makes it so
        # the waveform is not actually delayed!  i.e. it accounts for and undoes the delay effect
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        CableTxPWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.td.wf.TimeDescriptor(0,50,20.))
        #CableTxPWfDelayed=copy.deepcopy(CableTxPWf)
        CableTxPWfDelayed=si.td.f.InterpolatorFractionalDelayFilterLinear(1,-0.3,accountForDelay=True).FilterWaveform(CableTxPWf)
        #CableTxPWfDelayed.DelayBy(0.0/CableTxPWfDelayed.TimeDescriptor().Fs)
        if PlotTestInterpolatorLinear:
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
    def testUpsampleNoDelayLinear(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        CableTxPWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.td.wf.TimeDescriptor(0,50,20.))
        CableTxPWfUpsampled=si.td.f.InterpolatorFractionalDelayFilterLinear(10,0.0).FilterWaveform(CableTxPWf)
        if PlotTestInterpolatorLinear:
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
    def testUpsampleDelayLinear(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        CableTxPWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.td.wf.TimeDescriptor(0,50,20.))
        CableTxPWfUpsampled=si.td.f.InterpolatorFractionalDelayFilterLinear(10,0.3).FilterWaveform(CableTxPWf)
        if PlotTestInterpolatorLinear:
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
    def testSimpleLinear(self):
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        impulseWf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(-2,5,1),[0,0,1,0,0])
        fdpWf=impulseWf*si.td.f.FractionalDelayFilterLinear(0.3,accountForDelay=True)
        fdnWf=impulseWf*si.td.f.FractionalDelayFilterLinear(-0.3,accountForDelay=True)
        self.CheckWaveformResult(fdpWf,fileNameBase+'p.txt',fileNameBase)
        self.CheckWaveformResult(fdnWf,fileNameBase+'n.txt',fileNameBase)
        if PlotTestInterpolatorLinear:
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(impulseWf.Times(),impulseWf.Values(),marker='s',label='original waveform')
            plt.plot(fdpWf.Times(),fdpWf.Values(),marker='o',label='linear fractional delay .3')
            plt.plot(fdnWf.Times(),fdnWf.Values(),marker='o',label='linear fractional delay -.3')
            if PlotRegression:
                regression=si.td.wf.Waveform().ReadFromFile(fileNameBase+'.txt')
                plt.plot(regression.Times(),regression.Values(),label='regression')
            plt.legend(loc='upper right')
            plt.show()

if __name__ == '__main__':
    unittest.main()
