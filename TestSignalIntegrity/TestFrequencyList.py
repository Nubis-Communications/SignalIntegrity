#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Peter.Pupalaikis
#
# Created:     08/04/2016
# Copyright:   (c) Peter.Pupalaikis 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import unittest
import SignalIntegrity as si
import math
import os
from TestHelpers import SParameterCompareHelper

class TestFrequencyList(unittest.TestCase,SParameterCompareHelper):
    def testGenericVsEvenlySpaced(self):
        Fe=10e9
        N=100
        gfl=si.fd.GenericFrequencyList([float(n)/N*Fe for n in range(N+1)])
        esfl=si.fd.EvenlySpacedFrequencyList(Fe,N)
        # even though the lists are the same, the generic is not technically
        # evenly spaced until converted to such - see next test
        self.assertFalse(gfl==esfl,self.id()+' result incorrect')
    def testGenericVsEvenlySpaced2(self):
        Fe=10e9
        N=100
        gfl=si.fd.GenericFrequencyList([float(n)/N*Fe for n in range(N+1)])
        self.assertTrue(gfl.CheckEvenlySpaced(),self.id()+' should now be evenly spaced')
        esfl=si.fd.EvenlySpacedFrequencyList(Fe,N)
        self.assertTrue(gfl==esfl,self.id()+' result incorrect')
    def testSameGeneric(self):
        Fe=10e9
        N=100
        gfl=si.fd.GenericFrequencyList([float(n)/N*Fe for n in range(N+1)])
        gfl2=si.fd.GenericFrequencyList([float(n)/N*Fe for n in range(N+1)])
        self.assertTrue(gfl==gfl2,self.id()+' result incorrect')
    def testDifferentLengthGeneric(self):
        Fe=10e9
        N=100
        deltaf=Fe/N
        gfl=si.fd.GenericFrequencyList([n*deltaf for n in range(N+1)])
        gfl2=si.fd.GenericFrequencyList([n*deltaf for n in range(N)])
        self.assertFalse(gfl==gfl2,self.id()+' result incorrect')
    def testDifferentValuesGeneric(self):
        Fe=10e9
        N=100
        gfl=si.fd.GenericFrequencyList([float(n)/N*Fe for n in range(N+1)])
        gfl2=si.fd.GenericFrequencyList([float(n)/N*2*Fe for n in range(N+1)])
        self.assertFalse(gfl==gfl2,self.id()+' result incorrect')
    def testDifferentValuesGeneric2(self):
        Fe=10e9
        N=100
        gfl=si.fd.GenericFrequencyList([float(n)/N*Fe for n in range(N+1)])
        gfl2=si.fd.GenericFrequencyList([float(n)/N*Fe for n in range(N+1)])
        gfl2[1]=gfl2[1]+1
        self.assertFalse(gfl==gfl2,self.id()+' result incorrect')
    def testSameEvenlySpaced(self):
        Fe=10e9
        N=100
        esfl=si.fd.EvenlySpacedFrequencyList(Fe,N)
        esfl2=si.fd.EvenlySpacedFrequencyList(Fe,N)
        self.assertTrue(esfl==esfl2,self.id()+' result incorrect')
    def testDifferentLengthEvenlySpaced(self):
        Fe=10e9
        N=100
        deltaf=Fe/N
        esfl=si.fd.EvenlySpacedFrequencyList(Fe+deltaf,N+1)
        esfl2=si.fd.EvenlySpacedFrequencyList(Fe,N)
        self.assertFalse(esfl==esfl2,self.id()+' result incorrect')
    def testDifferentValuesEvenlySpaced(self):
        Fe=10e9
        N=100
        esfl=si.fd.EvenlySpacedFrequencyList(Fe,N)
        esfl2=si.fd.EvenlySpacedFrequencyList(2.*Fe,N)
        self.assertFalse(esfl==esfl2,self.id()+' result incorrect')
    def testValues(self):
        Fe=10e9
        N=100
        gfl=si.fd.GenericFrequencyList([float(n)/N*Fe for n in range(N+1)])
        esfl=si.fd.EvenlySpacedFrequencyList(Fe,N)
        gflf=gfl.Frequencies()
        eslf=esfl.Frequencies()
        self.assertTrue(all([abs(gflf[n]-eslf[n])<1e-6 for n in range(len(gflf))]),self.id()+' result incorrect')
    def testValuesCustom(self):
        Fe=10e9
        N=100
        gfl=si.fd.GenericFrequencyList([float(n)/N*Fe for n in range(N+1)])
        esfl=si.fd.EvenlySpacedFrequencyList(Fe,N)
        gflf=gfl.Frequencies(1e9)
        eslf=esfl.Frequencies(1e9)
        self.assertTrue(all([abs(gflf[n]-eslf[n])<1e-6 for n in range(len(gflf))]),self.id()+' result incorrect')
    def testValuesKHz(self):
        Fe=10e9
        N=100
        gfl=si.fd.GenericFrequencyList([float(n)/N*Fe for n in range(N+1)])
        esfl=si.fd.EvenlySpacedFrequencyList(Fe,N)
        gflf=gfl.Frequencies('KHz')
        eslf=esfl.Frequencies('KHz')
        self.assertTrue(all([abs(gflf[n]-eslf[n])<1e-6 for n in range(len(gflf))]),self.id()+' result incorrect')
    def testValuesMHz(self):
        Fe=10e9
        N=100
        gfl=si.fd.GenericFrequencyList([float(n)/N*Fe for n in range(N+1)])
        esfl=si.fd.EvenlySpacedFrequencyList(Fe,N)
        gflf=gfl.Frequencies('MHz')
        eslf=esfl.Frequencies('MHz')
        self.assertTrue(all([abs(gflf[n]-eslf[n])<1e-6 for n in range(len(gflf))]),self.id()+' result incorrect')
    def testValuesGHz(self):
        Fe=10e9
        N=100
        gfl=si.fd.GenericFrequencyList([float(n)/N*Fe for n in range(N+1)])
        esfl=si.fd.EvenlySpacedFrequencyList(Fe,N)
        gflf=gfl.Frequencies('MHz')
        eslf=esfl.Frequencies('MHz')
        self.assertTrue(all([abs(gflf[n]-eslf[n])<1e-6 for n in range(len(gflf))]),self.id()+' result incorrect')
    def testValuesGenericMul(self):
        Fe=10 # in GHz
        N=100
        gfl=si.fd.GenericFrequencyList([float(n)/N*Fe for n in range(N+1)])*1e9
        gfl2=si.fd.GenericFrequencyList([float(n)/N*Fe*1e9 for n in range(N+1)])
        self.assertTrue(gfl==gfl2,self.id()+' result incorrect')
    def testValuesGenericDiv(self):
        Fe=10e9
        N=100
        gfl=si.fd.GenericFrequencyList([float(n)/N*Fe for n in range(N+1)])/1e9
        gfl2=si.fd.GenericFrequencyList([float(n)/N*Fe/1e9 for n in range(N+1)])
        self.assertTrue(gfl==gfl2,self.id()+' result incorrect')
    def testValuesEvenlySpacedMul(self):
        Fe=10 # in GHz
        N=100
        esfl=si.fd.EvenlySpacedFrequencyList(Fe,N)*1e9
        esfl2=si.fd.EvenlySpacedFrequencyList(Fe*1e9,N)
        self.assertTrue(esfl==esfl2,self.id()+' result incorrect')
    def testValuesEvenlySpacedDiv(self):
        Fe=10e9
        N=100
        esfl=si.fd.EvenlySpacedFrequencyList(Fe,N)/1e9
        esfl2=si.fd.EvenlySpacedFrequencyList(Fe/1e9,N)
        self.assertTrue(esfl==esfl2,self.id()+' result incorrect')

if __name__ == '__main__':
    unittest.main()

