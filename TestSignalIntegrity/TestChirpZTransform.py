import unittest
import SignalIntegrity as si
import math
import os
from TestHelpers import *

class TestChirpZTransform(unittest.TestCase,SParameterCompareHelper):
    def testCZTResampleSame(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.File('TestDut.s4p')
        sf2=si.czt.CZTResample(sf,20.e9,200,False)
        sf2.WriteToFile('TestDutCmp.s4p')
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testCZTResampleHigherFreq(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.File('TestDut.s4p')
        sf2=si.czt.CZTResample(si.czt.CZTResample(sf,40.e9,400),20.e9,200)
        sf2.WriteToFile('TestDutCmp.s4p')
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testCZTResampleHigherRes(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.File('TestDut.s4p')
        sf2=si.czt.CZTResample(si.czt.CZTResample(sf,20.e9,400),20.e9,200)
        sf2.WriteToFile('TestDutCmp.s4p')
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testNewResamplerSpline(self):
        Fe=20.e9
        Np=400
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.File('TestDut.s4p')
        f2=[Fe/Np*n for n in range(Np+1)]
        sf2=si.sp.ResampledSParameters(sf,f2)
        sf3=si.sp.ResampledSParameters(sf,si.sp.FrequencyList().SetEvenlySpaced(Fe,Np),method='spline')
        #sf2.WriteToFile('TestDutCmp2.s4p')
        #sf3.WriteToFile('TestDutCmp3.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf3,0.001),self.id()+'result not same')
    def testNewResamplerCZT(self):
        Fe=20.e9
        Np=400
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.File('TestDut.s4p')
        f2=[Fe/Np*n for n in range(Np+1)]
        sf2=si.czt.CZTResample(sf,Fe,Np)
        sf3=si.sp.ResampledSParameters(sf,si.sp.FrequencyList().SetEvenlySpaced(Fe,Np),method='czt')
        #sf2.WriteToFile('TestDutCmp2.s4p')
        #sf3.WriteToFile('TestDutCmp3.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf3,0.001),self.id()+'result not same')
    def testNewResamplerCZTLowSpeed(self):
        Fe=20.e9
        Np=400
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.File('TestDut.s4p')
        f2=[Fe/Np*n for n in range(Np+1)]
        sf2=si.czt.CZTResample(sf,Fe,Np)
        sf3=si.sp.ResampledSParameters(sf,si.sp.FrequencyList().SetEvenlySpaced(Fe,Np),method='czt',speed='slow')
        #sf2.WriteToFile('TestDutCmp2.s4p')
        #sf3.WriteToFile('TestDutCmp3.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf3,0.001),self.id()+'result not same')
    def testNewResamplerCZTImposeReal(self):
        Fe=20.e9
        Np=400
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.File('TestDut.s4p')
        f2=[Fe/Np*n for n in range(Np+1)]
        sf2=si.czt.CZTResample(sf,Fe,Np,imposeRealness=True)
        sf3=si.sp.ResampledSParameters(sf,si.sp.FrequencyList().SetEvenlySpaced(Fe,Np),method='czt',enforceReal=True)
        #sf2.WriteToFile('TestDutCmp2.s4p')
        #sf3.WriteToFile('TestDutCmp3.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf3,0.001),self.id()+'result not same')

if __name__ == '__main__':
    unittest.main()