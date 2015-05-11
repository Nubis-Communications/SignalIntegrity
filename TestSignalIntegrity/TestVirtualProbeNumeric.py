import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import array
from numpy import matrix
from numpy import fft
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
        N=400
##        si.sp.ResampledSParameters(si.sp.File('XRAY041.s4p'),si.sp.EvenlySpacedFrequencyList(20.0e9,400)).WriteToFile('XRAY041.s4p')
##        return
        vpp=si.p.VirtualProbeNumericParser(si.sp.EvenlySpacedFrequencyList(Fe,N)).File('comparison.txt')
        result = vpp.TransferMatrices()
        result.WriteToFile('vptm.s6p')
        fr=vpp.FrequencyResponses()
        ir=vpp.ImpulseResponses()
        ml = vpp.SystemDescription().pMeasurementList
        ol = vpp.SystemDescription().pOutputList
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        for o in range(len(ol)):
            for m in range(len(ml)):
                plt.plot(fr[o][m].GHz(),fr[o][m].dB(),label=str(ol[o])+' due to '+str(ml[m]))
        plt.legend(loc='upper right')
        plt.show()
        #plt.savefig('vp.png')
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        for o in range(len(ol)):
            for m in range(len(ml)):
                plt.plot(ir[o][m].ns(),ir[o][m].Response(),label=str(ol[o])+' due to '+str(ml[m]))
        plt.legend(loc='upper right')
        plt.show()
        #plt.savefig('vptd.png')
if __name__ == '__main__':
    unittest.main()
