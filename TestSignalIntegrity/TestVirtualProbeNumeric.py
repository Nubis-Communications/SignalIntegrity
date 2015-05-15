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
        N=400
##        si.sp.ResampledSParameters(si.sp.File('XRAY041.s4p'),si.sp.EvenlySpacedFrequencyList(20.0e9,400)).WriteToFile('XRAY041.s4p')
##        return
        vpp=si.p.VirtualProbeNumericParser(si.sp.EvenlySpacedFrequencyList(Fe,N)).File('comparison.txt')
        result = vpp.TransferMatrices()
        result.WriteToFile('vptm.s6p')
        os.remove('vptm.s6p')
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
        #plt.show()
        #plt.savefig('vp.png')
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        for o in range(len(ol)):
            for m in range(len(ml)):
                plt.plot(ir[o][m].ns(),ir[o][m].Response(),label=str(ol[o])+' due to '+str(ml[m]))
        plt.legend(loc='upper right')
        #plt.show()
        #plt.savefig('vptd.png')
        with open('CableTxP.txt','rb') as f:
            CableTxP = [float(line) for line in f]
        CableTxPt = [k/40. for k in range(len(CableTxP))]
        with open('CableTxM.txt','rb') as f:
            CableTxM = [float(line) for line in f]
        CableTxMt = [k/40. for k in range(len(CableTxM))]
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.plot(CableTxPt,CableTxP,label='CableTxP')
        plt.plot(CableTxMt,CableTxM,label='CableTxM')
        plt.legend(loc='upper right')
        #plt.show()
        CableTx=[CableTxP[k]-CableTxM[k] for k in range(max(len(CableTxP),len(CableTxM)))]
        CableTxt=[k/40.-2.3 for k in range(len(CableTx))]
        D20_2DueToD9_2=convolve(ir[2][0].Response(),CableTxP,'same')
        D20_2DueToD10_2=convolve(ir[2][1].Response(),CableTxM,'same')
        D21_2DueToD9_2=convolve(ir[3][0].Response(),CableTxP,'same')
        D21_2DueToD10_2=convolve(ir[3][1].Response(),CableTxM,'same')
        D20_2=[D20_2DueToD9_2[k]+D20_2DueToD10_2[k] for k in range(max(len(D20_2DueToD9_2),len(D20_2DueToD10_2)))]
        D21_2=[D21_2DueToD9_2[k]+D21_2DueToD10_2[k] for k in range(max(len(D21_2DueToD9_2),len(D21_2DueToD10_2)))]
        D20_2t=[k/40.-2.3 for k in range(len(D20_2))]
        D21_2t=[k/40.-2.3 for k in range(len(D21_2))]
        D20_2_D21_2Diff = [D20_2[k]-D21_2[k] for k in range(max(len(D20_2),len(D21_2)))]
        D20_2_D21_2Difft=[k/40.-2.3+7.65-len(ir[2][0].Response())/2./40. for k in range(len(D20_2_D21_2Diff))]
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        #plt.plot(D20_2t,D20_2,label='D20_2')
        #plt.plot(D21_2t,D21_2,label='D21_2')
        plt.plot(CableTxt,CableTx,label='DiffIn')
        plt.plot(D20_2_D21_2Difft,D20_2_D21_2Diff,label='DiffOut')
        plt.legend(loc='upper right')
        #plt.show()



if __name__ == '__main__':
    unittest.main()
