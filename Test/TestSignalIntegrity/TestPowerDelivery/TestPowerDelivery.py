"""
TestPowerDelivery.py
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

import SignalIntegrity.Lib as si
from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
from random import random
from numpy import array
from math import sqrt
import os

class TestPowerDeliveryTest(unittest.TestCase):
    def setUp(self):
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        unittest.TestCase.setUp(self)
    def tearDown(self):
        os.chdir(self.cwd)
        unittest.TestCase.tearDown(self)
    def testPowerDelivery(self):
        proj=SignalIntegrityAppHeadless()
        proj.OpenProjectFile('PowerDelivery.si')
        res=proj.Simulate()
        vgnames=res[0]
        onames=res[1]
        TM=res[2][0]
        V=[[None],[None]]
        V[vgnames.index('VG1')][0]=(-1+random()*2.)+1j*(-1+random()*2.)
        V[vgnames.index('VG2')][0]=(-1+random()*2.)+1j*(-1+random()*2.)
        b=[v[0] for v in (array(TM).dot(array(V))).tolist()]
        A1=b[onames.index('A1')]/sqrt(50.)
        A2=b[onames.index('A2')]/sqrt(50.)
        B1=b[onames.index('B1')]/sqrt(50.)
        B2=b[onames.index('B2')]/sqrt(50.)
        V1=b[onames.index('V1')]
        V2=b[onames.index('V2')]
        I1=b[onames.index('I1')]
        I2=b[onames.index('I2')]
        pvi=V1*I1.conjugate()+V2*I2.conjugate()
        pab=abs(A1)*abs(A1)+abs(A2)*abs(A2)-abs(B1)*abs(B1)-abs(B2)*abs(B2)
        A=array([[A1],[A2]])
        B=array([[B1],[B2]])
        pab2=(A.conj().T.dot(A)-B.conj().T.dot(B)).tolist()[0][0]
        self.assertAlmostEqual(pvi, pab, 12, 'power delivered incorrect')
        self.assertAlmostEqual(pvi, pab2, 12, 'power delivered incorrect')
        pass
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()