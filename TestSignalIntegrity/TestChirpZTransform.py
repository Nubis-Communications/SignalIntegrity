import unittest
import SignalIntegrity as si
import math
import os
from TestHelpers import *

class TestChirpZTransform(unittest.TestCase,SParameterCompareHelper):
    def testCZTResampleSame(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.File('TestDut.s4p')
        sf2=sf.Resample(si.sp.EvenlySpacedFrequencyList(20.e9,200))
        sf2.WriteToFile('TestDutCmp.s4p')
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testCZTResampleHigherFreq(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.File('TestDut.s4p')
        sf2=sf.Resample(si.sp.EvenlySpacedFrequencyList(40.e9,400)).Resample(si.sp.EvenlySpacedFrequencyList(20.e9,200))
        sf2.WriteToFile('TestDutCmp.s4p')
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testCZTResampleHigherRes(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.File('TestDut.s4p')
        sf2=sf.Resample(si.sp.EvenlySpacedFrequencyList(20.e9,400)).Resample(si.sp.EvenlySpacedFrequencyList(20.e9,200))
        sf2.WriteToFile('TestDutCmp.s4p')
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testNewResamplerSpline(self):
        Fe=20.e9
        Np=400
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.File('TestDut.s4p')
        f2=[Fe/Np*n for n in range(Np+1)]
        sf2=sf.Resample(f2)
        sf3=sf.Resample(si.sp.EvenlySpacedFrequencyList(Fe,Np))
        self.assertTrue(self.SParametersAreEqual(sf2,sf3,0.001),self.id()+'result not same')

if __name__ == '__main__':
    unittest.main()