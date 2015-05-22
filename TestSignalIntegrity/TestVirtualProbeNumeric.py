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
        #os.remove('vptm.s6p')
        fr=vpp.FrequencyResponses()
        ir=vpp.ImpulseResponses(method='czt',adjustDelay=True)
        ml = vpp.SystemDescription().pMeasurementList
        ol = vpp.SystemDescription().pOutputList
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        for o in range(len(ol)):
            for m in range(len(ml)):
                plt.plot(fr[o][m].Frequencies('GHz'),fr[o][m].Response('dB'),label=str(ol[o])+' due to '+str(ml[m]))
                fr[o][m].WriteToFile(str(ol[o])+'_due_to_'+str(ml[m])+'.txt')
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
##        CableTxPWf=si.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.wf.TimeDescriptor(0,2000,20.e9))
##        CableTxMWf=si.wf.WaveformFileAmplitudeOnly('CableTxM.txt',si.wf.TimeDescriptor(0,2000,20.e9))
##        CableTxPWf.WriteToFile('CableTxPWf.txt')
##        CableTxMWf.WriteToFile('CableTxMWf.txt')
        ThruBackplaneP=si.wf.WaveformFileAmplitudeOnly('ThruBackplaneP.txt',si.wf.TimeDescriptor(0,2000,20.e9))
        ThruBackplaneM=si.wf.WaveformFileAmplitudeOnly('ThruBackplaneM.txt',si.wf.TimeDescriptor(0,2000,20.e9))
        ThruBackplaneDiff=ThruBackplaneP-ThruBackplaneM
        inputWf=[si.wf.Waveform().ReadFromFile(fileName) for fileName in ['CableTxPWf.txt','CableTxMWf.txt']]
        outputWf=vpp.ProcessWaveforms(inputWf)
        DiffIn=(inputWf[0]-inputWf[1])
        DiffOutTop=(outputWf[ol.index(('D20',2))]-outputWf[ol.index(('D21',2))]).DelayBy(-4.7e-9)
        DiffOutMid=(outputWf[ol.index(('D11',2))]-outputWf[ol.index(('D12',2))]).DelayBy(-4.7e-9)
        DiffOutBot=(outputWf[ol.index(('R1',1))]-outputWf[ol.index(('R2',2))]).DelayBy(-2.325e-9)
        ThruBackplaneDiff.DelayBy(-4.7e-9)
        [DiffIn,ThruBackplaneDiff,DiffOutTop,DiffOutMid,DiffOutBot]=si.wf.AdaptedWaveforms([DiffIn*si.f.Upsampler(10),ThruBackplaneDiff,DiffOutTop,DiffOutMid,DiffOutBot])
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.plot(DiffIn.Times('ns'),DiffIn.Values(),label='DiffIn')
        plt.plot(DiffOutTop.Times('ns'),DiffOutTop.Values(),label='DiffOutTop')
        plt.plot(DiffOutMid.Times('ns'),DiffOutMid.Values(),label='DiffOutMid')
        plt.plot(DiffOutBot.Times('ns'),DiffOutBot.Values(),label='DiffOutBot')
        plt.legend(loc='upper right')
        plt.show()
##        plt.clf()
##        plt.xlabel('time (ns)')
##        plt.ylabel('amplitude')
##        fb=2.501234
##        plt.scatter([(t-0.11) % (1./fb) for t in DiffIn.Times('ns')],DiffIn.Values(),label='DiffIn')
##        plt.scatter([(t-0.11) % (1./fb) for t in DiffOutTop.Times('ns')],DiffOutTop.Values(),label='DiffOutTop')
##        #plt.plot([t % 1./fb for t in DiffOutMid.Times('ns')],DiffOutMid.Values(),label='DiffOutMid')
##        #plt.plot([t % 1./fb for t in DiffOutBot.Times('ns')],DiffOutBot.Values(),label='DiffOutBot')
##        plt.legend(loc='upper right')
##        plt.show()



if __name__ == '__main__':
    unittest.main()
