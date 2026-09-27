"""
TestCascading.py
"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import unittest

from random import random
from numpy import array
from numpy.linalg import det

import SignalIntegrity.Lib as si

class TestCascadingTest(unittest.TestCase):
    @staticmethod
    def RandomComplexNumber():
        return (-1+random()*2.)+1j*(-1+random()*2.)
    def testCascading(self):
        SL=[[SL11,SL12],[SL21,SL22]]=\
            [[self.RandomComplexNumber(),self.RandomComplexNumber()],
            [self.RandomComplexNumber(),self.RandomComplexNumber()]]
        SR=[[SR11,SR12],[SR21,SR22]]=\
            [[self.RandomComplexNumber(),self.RandomComplexNumber()],
            [self.RandomComplexNumber(),self.RandomComplexNumber()]]
        TL=[[TL11,TL12],[TL21,TL22]]=si.cvt.S2T(SL)
        TR=[[TR11,TR12],[TR21,TR22]]=si.cvt.S2T(SR)
        T=[[T11,T12],[T21,T22]]=(array(TL).dot(array(TR))).tolist()
        S=[[S11,S12],[S21,S22]]=si.cvt.T2S(T)
        # this is presumably the right answer
        #
        # now check the math in the book
        TLc=[[TLc11,TLc12],[TLc21,TLc22]]=(1./SL21*array([[-det(array(SL)),SL11],[-SL22,1.]])).tolist()
        self.assertAlmostEqual(TLc11, TL11, 12, 'TL11 incorrect')
        self.assertAlmostEqual(TLc12, TL12, 12, 'TL12 incorrect')
        self.assertAlmostEqual(TLc21, TL21, 12, 'TL21 incorrect')
        self.assertAlmostEqual(TLc22, TL22, 12, 'TL22 incorrect')
        TRc=[[TRc11,TRc12],[TRc21,TRc22]]=(1./SR21*array([[-det(array(SR)),SR11],[-SR22,1.]])).tolist()
        self.assertAlmostEqual(TRc11, TR11, 12, 'TR11 incorrect')
        self.assertAlmostEqual(TRc12, TR12, 12, 'TR12 incorrect')
        self.assertAlmostEqual(TRc21, TR21, 12, 'TR21 incorrect')
        self.assertAlmostEqual(TRc22, TR22, 12, 'TR22 incorrect')
        Tc=[[Tc11,Tc12],[Tc21,Tc22]]=(1./(SL21*SR21)*array([[det(array(SL))*det(array(SR))-SL11*SR22,SL11-det(array(SL))*SR11],
                                                            [det(array(SR))*SL22-SR22,1.-SL22*SR11]])).tolist()
        self.assertAlmostEqual(Tc11, T11, 12, 'T11 incorrect')
        self.assertAlmostEqual(Tc12, T12, 12, 'T12 incorrect')
        self.assertAlmostEqual(Tc21, T21, 12, 'T21 incorrect')
        self.assertAlmostEqual(Tc22, T22, 12, 'T22 incorrect')
        Sc=[[Sc11,Sc12],[Sc21,Sc22]]=(1./T22*array([[T12,det(array(T))],[1.,-T21]])).tolist()
        self.assertAlmostEqual(Sc11, S11, 12, 'S11 incorrect')
        self.assertAlmostEqual(Sc12, S12, 12, 'S12 incorrect')
        self.assertAlmostEqual(Sc21, S21, 12, 'S21 incorrect')
        self.assertAlmostEqual(Sc22, S22, 12, 'S22 incorrect')
        Sc=[[Sc11,Sc12],[Sc21,Sc22]]=(1./(1.-SL22*SR11)*array([[SL11-SR11*det(array(SL)),SL12*SR12],
                                                                [SL21*SR21,SR22-SL22*det(array(SR))]])).tolist()
        self.assertAlmostEqual(Sc11, S11, 12, 'S11 incorrect')
        self.assertAlmostEqual(Sc12, S12, 12, 'S12 incorrect')
        self.assertAlmostEqual(Sc21, S21, 12, 'S21 incorrect')
        self.assertAlmostEqual(Sc22, S22, 12, 'S22 incorrect')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()