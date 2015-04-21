import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import array
from numpy import matrix
import copy
import math
import os

import matplotlib.pyplot as plt

class TestVirtualProbeNumeric(unittest.TestCase):
    def testVirtualProbeDC2008(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir('.\\DesignCon2008\\')
        f=si.sp.EvenlySpacedFrequencyList(10.0e9,400)
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
        plt.show()

if __name__ == '__main__':
    unittest.main()
