import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import array
from numpy import matrix
import copy
import math
import os

##import matplotlib.pyplot as plt

class TestVirtualProbeNumeric(unittest.TestCase):
    def testVirtualProbeDC2008(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir('.\\DesignCon2008\\')
        f=si.sp.EvenlySpacedFrequencyList(10.0,50)
        #si.sp.ResampledSParameters(si.sp.File('XRAY041.s4p'),si.sp.EvenlySpacedFrequencyList(20.0,400)).WriteToFile('XRAY041.s4p')
        #return
        vpp=si.p.VirtualProbeNumericParser(f).File('comparison.txt')
        result = vpp.TransferFunctions()
        ml = vpp.m_ml
        o1mag = [20.*math.log10(abs(result[n][1][0][0])) for n in range(len(f))]
        o2mag = [20.*math.log10(abs(result[n][1][1][0])) for n in range(len(f))]
        fp = [ele/1.e9 for ele in f]
        labels=[]
        labels.append(str(vpp.SystemDescription().pOutputList[0]) + ' due to ' + str(vpp.SystemDescription().pMeasurementList[0]))
        labels.append(str(vpp.SystemDescription().pOutputList[1]) + ' due to ' + str(vpp.SystemDescription().pMeasurementList[0]))
##        plt.xlabel('frequency (GHz)')
##        plt.ylabel('magnitude (dB)')
##        plt.plot(fp,o1mag,label=labels[0])
##        plt.plot(fp,o2mag,label=labels[1])
##        plt.legend(loc='upper left')
##        plt.show()

if __name__ == '__main__':
    unittest.main()
