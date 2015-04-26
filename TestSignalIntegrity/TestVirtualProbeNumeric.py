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
        result = vpp.TransferFunctions()
        ml = vpp.SystemDescription().pMeasurementList
        ol = vpp.SystemDescription().pOutputList
        tf=[]
        tfl=[]
        for o in range(len(ol)):
            tfo=[]
            tfol=[]
            for m in range(len(ml)):
                tfo.append([20.*math.log10(abs(result[n][1].tolist()[o][m])) for n in range(len(f))])
                tfol.append(str(vpp.SystemDescription().pOutputList[o]) + ' due to ' + str(vpp.SystemDescription().pMeasurementList[m]))
            tf.append(tfo)
            tfl.append(tfol)
        fp = [ele/1.e9 for ele in f]
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        for o in range(len(ol)):
            for m in range(len(ml)):
                plt.plot(fp,tf[o][m],label=tfl[o][m])
        plt.legend(loc='upper right')
        #plt.show()
        #plt.savefig('vp.png')
        plt.clf()
        K=2*N
        t=[(k-K/2)*1./Fs for k in range(K)]
        tf=[]
        for o in range(len(ol)):
            tfoc=[]
            for m in range(len(ml)):
                yfp=[result[n][1].tolist()[o][m] for n in range(len(f))]
                ynp=[result[N-nn][1].tolist()[o][m].conjugate() for nn in range(1,len(f)-1)]
                y=yfp+ynp
                td=fft.ifft(y)
                tp=[td[k] for k in range(K/2)]
                tn=[td[k] for k in range(K/2,K)]
                td=tn+tp
                plt.plot(t,td,label=tfl[o][m])
                tfoc.append(td)
            tf.append(tfoc)
        plt.legend(loc='upper right')
        plt.show()
        #plt.savefig('vptd.png')
if __name__ == '__main__':
    unittest.main()
