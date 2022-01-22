"""
TestRLGC.py
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
import os

class TestRLGC(unittest.TestCase,si.test.SParameterCompareHelper,si.test.CallbackTesterHelper):
    def __init__(self, methodName='runTest'):
        si.test.CallbackTesterHelper.__init__(self)
        self.path=os.path.dirname(os.path.realpath(__file__))
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        os.chdir(self.path)
    def id(self):
        return '.'.join(unittest.TestCase.id(self).split('.')[-1:]).replace('test','')
    def testRLGCFitFromFile(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        rlgc=si.fit.RLGCFitFromFile(fd,'../../SignalIntegrity/App/Examples/HDMICable/HDMIThruPortsPeeled.si').Fit()
        spFileName=self.id()+'.s2p'
        if not os.path.exists(spFileName):
            rlgc.WriteToFile(spFileName)
        sp=si.sp.SParameterFile(spFileName)
        self.assertTrue(self.SParametersAreEqual(rlgc,sp,0.001),self.id()+'result not same')
    def testRLGCFitFromFileUnCached(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        rlgc=si.fit.RLGCFitFromFile(fd,'../../SignalIntegrity/App/Examples/HDMICable/HDMIThruPortsPeeled.si')
        spFileName=self.id()+'.s2p'
        if not os.path.exists(spFileName):
            rlgc.Fit().WriteToFile(spFileName)
        sp=si.sp.SParameterFile(spFileName)
        res=rlgc[1]
        corr=sp[1]
        for r in range(len(corr)):
            for c in range(len(corr[r])):
                self.assertAlmostEqual(res[r][c],corr[r][c],6,self.id()+'result not same')

if __name__ == '__main__':
    unittest.main()
