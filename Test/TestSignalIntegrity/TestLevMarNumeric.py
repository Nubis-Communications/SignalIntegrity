"""
TestLevMarNumeric.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
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
from numpy import array

class QuadraticFitter(si.fit.LevMar):
    def Initialize(self,a,x,y):
        self.m_x=x
        si.fit.LevMar.Initialize(self, a, y)
        self.m_epsilon=1e-6
    def fF(self,a):
        return array([[sum([a[m][0]*pow(x[0],m) for m in range(len(a))])] for x in self.m_x])

class QuadraticFitterIllFormed(si.fit.LevMar):
    def Initialize(self,a,x,y):
        self.m_x=x
        si.fit.LevMar.Initialize(self, a, y)
        self.m_epsilon=1e-3

class TestLevMarNumericTest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
    def testLevMarNumeric(self):
        """tests fitting of a simple quadratic to some data.\n
        The data is in x as a list of list matrix style vector.
        The correct coeficients are in a as a list list style vector.
        y is a vectory created where:\n
        y[m][0] = a[0][0]+*a[1][0]*x[m][0]+*a[2][0]*x[m][0]^2
        """
        a=[[1.],[2.],[3.]]
        x=[[0.],[1.],[2.],[3.],[4.],[5.]]
        y=[[sum([a[m][0]*pow(xv[0],m) for m in range(len(a))])] for xv in x]
        qf=QuadraticFitter()
        qf.Initialize(array([[1.] for _ in a]), x, y)
        qf.Solve()
        ac=qf.m_a
        fity=array([[sum([ac[m][0]*pow(xv[0],m) for m in range(len(ac))])] for xv in x])
        maxError=max([abs(fv[0]-yv[0])/abs(yv[0])*100.0 for fv,yv in zip(fity,y)])
        self.assertLess(maxError, 0.1, 'quadratic fit failed') 
    def testLevMarNumericIllFormed(self):
        """tests that LevMar throws correct exception when non-overloaded
        class created"""
        a=[[1.],[2.],[3.]]
        x=[[0.],[1.],[2.],[3.],[4.],[5.]]
        y=[[sum([a[m][0]*pow(xv[0],m) for m in range(len(a))])] for xv in x]
        qf=QuadraticFitterIllFormed()
        with self.assertRaises(si.SignalIntegrityException) as cm:
            qf.Initialize([[1] for _ in a], x, y)
            qf.Solve()
        self.assertEqual(cm.exception.parameter,'Fitter')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()