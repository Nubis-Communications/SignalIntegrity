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

class TestUpsampler(unittest.TestCase):
    def testDelay(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir('.//DesignCon2008//')
        CableTxPWf=si.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.wf.TimeDescriptor(0,50,20.))
        CableTxPWfDelayed=copy.deepcopy(CableTxPWf)
        CableTxPWfDelayed.DelayBy(0.3/CableTxPWfDelayed.TimeDescriptor().Fs)
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.plot(CableTxPWfDelayed.Times('ns'),CableTxPWfDelayed.Values(),label='delayed by 0.3 samples added to HorOffset')
        plt.plot(CableTxPWf.Times('ns'),CableTxPWf.Values(),label='not delayed')
        plt.legend(loc='upper right')
        plt.show()
        #plt.savefig('vptd.png')
    def testResampleNoDelay(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir('.//DesignCon2008//')
        CableTxPWf=si.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.wf.TimeDescriptor(0,50,20.))
        CableTxPWfDelayed=copy.deepcopy(CableTxPWf)
        CableTxPWfDelayed.DelayBy(0.0/CableTxPWfDelayed.TimeDescriptor().Fs)
        CableTxPWfDelayed2=si.f.UpsamplerLinear(1,0.0).FilterWaveform(CableTxPWf)
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.plot(CableTxPWfDelayed.Times('ns'),CableTxPWfDelayed.Values(),label='delayed by 0 added to HorOffset')
        plt.plot(CableTxPWfDelayed2.Times('ns'),CableTxPWfDelayed2.Values(),label='delayed by fractional delay of 0')
        plt.legend(loc='upper right')
        plt.show()
        #plt.savefig('vptd.png')
    def testResample(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir('.//DesignCon2008//')
        CableTxPWf=si.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.wf.TimeDescriptor(0,20,20.))
        CableTxPWfDelayed=copy.deepcopy(CableTxPWf)
        FractionalDelay=0.3
        CableTxPWfDelayed.DelayBy(FractionalDelay/CableTxPWfDelayed.TimeDescriptor().Fs)
        CableTxPWfDelayed2=si.f.UpsamplerLinear(1,FractionalDelay,accountForDelay=True).FilterWaveform(CableTxPWf)
        CableTxPWfDelayed3=si.f.UpsamplerLinear(1,FractionalDelay,accountForDelay=True).FilterWaveform(CableTxPWf)
        CableTxPWfDelayed3.DelayBy(FractionalDelay/CableTxPWfDelayed3.TimeDescriptor().Fs)
        CableTxPWfDelayed4=si.f.UpsamplerLinear(1,FractionalDelay,accountForDelay=False).FilterWaveform(CableTxPWf)
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
        #plt.savefig('vptd.png')
    def testChangeSamplePhase(self):
        # to change the sample phase, fractionally delay the waveform - the filter descriptor makes it so
        # the waveform is not actually delayed!  i.e. it accounts for and undoes the delay effect
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir('.//DesignCon2008//')
        CableTxPWf=si.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.wf.TimeDescriptor(0,50,20.))
        CableTxPWfDelayed=copy.deepcopy(CableTxPWf)
        CableTxPWfDelayed=si.f.UpsamplerLinear(1,0.3,accountForDelay=True).FilterWaveform(CableTxPWfDelayed)
        #CableTxPWfDelayed.DelayBy(0.0/CableTxPWfDelayed.TimeDescriptor().Fs)
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.plot(CableTxPWf.Times('ns'),CableTxPWf.Values(),label='original waveform')
        plt.plot(CableTxPWfDelayed.Times('ns'),CableTxPWfDelayed.Values(),label='sample phase changed by 0.3 samples')
        plt.legend(loc='upper right')
        plt.show()
    def testUpsampleNoDelay(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir('.//DesignCon2008//')
        CableTxPWf=si.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.wf.TimeDescriptor(0,50,20.))
        CableTxPWfUpsampled=si.f.UpsamplerLinear(10,0.0).FilterWaveform(CableTxPWf)
        #si.f.UpsamplerLinear(10,0.0).Print()
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        print len(CableTxPWfUpsampled.Times('ns'))
        print len(CableTxPWfUpsampled.Values())
        plt.plot(CableTxPWf.Times('ns'),CableTxPWf.Values(),marker='s',label='original waveform')
        plt.plot(CableTxPWfUpsampled.Times('ns'),CableTxPWfUpsampled.Values(),marker='o',label='upsampled by 10')
        plt.legend(loc='upper right')
        plt.show()
        #plt.savefig('vptd.png')
    def testUpsampleDelay(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir('.//DesignCon2008//')
        CableTxPWf=si.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.wf.TimeDescriptor(0,50,20.))
        CableTxPWfUpsampled=si.f.UpsamplerLinear(10,0.3).FilterWaveform(CableTxPWf)
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        print len(CableTxPWfUpsampled.Times('ns'))
        print len(CableTxPWfUpsampled.Values())
        plt.plot(CableTxPWf.Times('ns'),CableTxPWf.Values(),marker='s',label='original waveform')
        plt.plot(CableTxPWfUpsampled.Times('ns'),CableTxPWfUpsampled.Values(),marker='o',label='upsampled by 10 + sample phase')
        plt.legend(loc='upper right')
        plt.show()
        #plt.savefig('vptd.png')


if __name__ == '__main__':
    unittest.main()
