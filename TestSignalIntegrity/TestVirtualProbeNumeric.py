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
        f=si.sp.EvenlySpacedFrequencyList(Fe,N)
##        si.sp.ResampledSParameters(si.sp.File('XRAY041.s4p'),si.sp.EvenlySpacedFrequencyList(20.0e9,400)).WriteToFile('XRAY041.s4p')
##        return
        vpp=si.p.VirtualProbeNumericParser(f).File('comparison.txt')
        result = vpp.TransferMatrices()
        fr=vpp.FrequencyResponses()
        ir=vpp.ImpulseResponses()
        ml = vpp.SystemDescription().pMeasurementList
        ol = vpp.SystemDescription().pOutputList
        tfl=[[str(ol[o])+' due to '+str(ml[m])
            for m in range(len(ml))] for o in range(len(ol))]
        fp = [ele/1.e9 for ele in f]
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        for o in range(len(ol)):
            for m in range(len(ml)):
                plt.plot(fp,fr[o][m].dB(),label=tfl[o][m])
        plt.legend(loc='upper right')
        #plt.show()
        #plt.savefig('vp.png')
        plt.clf()
        for o in range(len(ol)):
            for m in range(len(ml)):
                plt.plot(ir[o][m].Time(),ir[o][m].Response(),label=tfl[o][m])
        plt.legend(loc='upper right')
        #plt.show()
        #plt.savefig('vptd.png')
if __name__ == '__main__':
    unittest.main()
