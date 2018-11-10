"""
SVD Testing
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

from numpy import array

import SignalIntegrity as si

from numpy import linalg,matrix,identity
from numpy.linalg.linalg import LinAlgError,svd
from numpy import diag

class TestSVDTest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
    def id(self):
        return 'TestSVD.'+'.'.join(unittest.TestCase.id(self).split('.')[-2:])
    def testDecomposition(self):
        Wba=[[-1./3,0],
             [0,-1./3]]
        Wbx=[[0,0,2./3,2./3],
             [2./3,2./3,0,0]]
        Wxx=[[0,0,2./3,-1./3],
             [0,0,-1./3,2./3],
             [2./3,-1./3,0,0],
             [-1./3,2./3,0,0]]
        Wxa=[[2./3,0],
             [2./3,0],
             [0,2./3],
             [0,2./3]]
        I=identity(4).tolist()
        
        S=(matrix(I)-matrix(Wxx)).tolist()
        
        U,s,VH=svd(S)
        
        U=U.tolist()
        s=s.tolist()
        VH=VH.tolist()
        
        res=(matrix(U)*matrix(diag(s))*matrix(VH)).tolist()
        difference = linalg.norm(matrix(res)-matrix(S))
        self.assertTrue(difference<1e-10,'svd exapansion incorrect')
    def testTeeWithDagger(self):
        Wba=[[-1./3,0],
             [0,-1./3]]
        Wbx=[[0,0,2./3,2./3],
             [2./3,2./3,0,0]]
        Wxx=[[0,0,2./3,-1./3],
             [0,0,-1./3,2./3],
             [2./3,-1./3,0,0],
             [-1./3,2./3,0,0]]
        Wxa=[[2./3,0],
             [2./3,0],
             [0,2./3],
             [0,2./3]]
        I=identity(4).tolist()
        
        S=(matrix(I)-matrix(Wxx)).tolist()
        
        numeric=si.sd.Numeric()
        
        res=matrix(Wba)+matrix(Wbx)*numeric.Dagger(matrix(I)-matrix(Wxx),Left=Wbx,Right=Wxa)*matrix(Wxa)
        res=res.tolist()
        corr=si.dev.Thru()
        difference = linalg.norm(matrix(res)-matrix(corr))
        self.assertTrue(difference<1e-10,'svd didnt work')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()