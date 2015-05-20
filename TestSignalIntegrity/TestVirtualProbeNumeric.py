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

class TestVirtualProbeNumeric(unittest.TestCase):
    def testVirtualProbeDC2008(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir('.//DesignCon2008//')
        Fs=20.e9
        Fe=Fs/2
        N=200
##        si.sp.ResampledSParameters(si.sp.File('XRAY041.s4p'),si.sp.EvenlySpacedFrequencyList(20.0e9,400)).WriteToFile('XRAY041.s4p')
##        return
        vpp=si.p.VirtualProbeNumericParser(si.sp.EvenlySpacedFrequencyList(Fe,N)).File('comparison.txt')
        result = vpp.TransferMatrices()
        result.WriteToFile('vptm.s6p')
        os.remove('vptm.s6p')
        fr=vpp.FrequencyResponses()
        ir=vpp.ImpulseResponses(method='czt',adjustDelay=True)
        ml = vpp.SystemDescription().pMeasurementList
        ol = vpp.SystemDescription().pOutputList
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        for o in range(len(ol)):
            for m in range(len(ml)):
                plt.plot(fr[o][m].Frequencies('GHz'),fr[o][m].Response('dB'),label=str(ol[o])+' due to '+str(ml[m]))
        plt.legend(loc='upper right')
        plt.show()
        #plt.savefig('vp.png')
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        for o in range(len(ol)):
            for m in range(len(ml)):
                plt.plot(ir[o][m].Times('ns'),ir[o][m].Values(),label=str(ol[o])+' due to '+str(ml[m]))
        plt.legend(loc='upper right')
        plt.show()
        #plt.savefig('vptd.png')
        CableTxPWf=si.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.wf.TimeDescriptor(0,20000,20.))
        CableTxMWf=si.wf.WaveformFileAmplitudeOnly('CableTxM.txt',si.wf.TimeDescriptor(0,20000,20.))
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.plot(CableTxPWf.Times(),CableTxPWf.Values(),label='CableTxP')
        plt.plot(CableTxMWf.Times(),CableTxMWf.Values(),label='CableTxM')
        plt.legend(loc='upper right')
        #plt.show()
        CableTxWf=CableTxPWf-CableTxMWf
        D20_2DueToD9_2=ir[ol.index(('D20',2))][ml.index(('D9',2))].FirFilter().FilterWaveform(CableTxPWf)
        D20_2DueToD10_2=ir[ol.index(('D20',2))][ml.index(('D10',2))].FirFilter().FilterWaveform(CableTxMWf)
        D21_2DueToD9_2=ir[ol.index(('D21',2))][ml.index(('D9',2))].FirFilter().FilterWaveform(CableTxPWf)
        D21_2DueToD10_2=ir[ol.index(('D21',2))][ml.index(('D10',2))].FirFilter().FilterWaveform(CableTxMWf)
        D20_2=D20_2DueToD9_2+D20_2DueToD10_2
        D21_2=D21_2DueToD9_2+D21_2DueToD10_2
        D20_2_D21_2Diff = (D20_2-D21_2).OffsetBy(0).DelayBy(-4.7)
        Results=si.wf.AdaptedWaveforms([CableTxWf,D20_2_D21_2Diff])
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.plot(Results[0].Times(),Results[0].Values(),label='DiffIn')
        plt.plot(Results[1].Times(),Results[1].Values(),label='DiffOut')
        plt.legend(loc='upper right')
        plt.show()
        inputWf=[CableTxPWf,CableTxMWf]
        outputWf=vpp.ProcessWaveforms(inputWf)
        DiffIn=(inputWf[0]-inputWf[1])
        DiffOut=(outputWf[ol.index(('D20',2))]-outputWf[ol.index(('D21',2))]).DelayBy(-4.7)
        Results=si.wf.AdaptedWaveforms([DiffIn,DiffOut])
        DiffIn=Results[0]
        DiffOut=Results[1]
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.plot(DiffIn.Times(),DiffIn.Values(),label='DiffIn')
        plt.plot(DiffOut.Times(),DiffOut.Values(),label='DiffOut')
        plt.legend(loc='upper right')
        plt.show()

if __name__ == '__main__':
    unittest.main()
