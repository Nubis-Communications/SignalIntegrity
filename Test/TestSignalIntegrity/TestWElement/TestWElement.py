"""
TestWElement.py
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
import os

import SignalIntegrity.Lib as si

class TestWElementTest(unittest.TestCase,si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper):
    relearn=True
    debug=False
    checkPictures=True
    keepNewFormats=False
    def __init__(self, methodName='runTest'):
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        os.chdir(self.path)
    def testName(self):
        return '_'.join(unittest.TestCase.id(self).split('.')[-2:])
    def tearDown(self):
        pass
    def testWElementFile(self):
        si.sp.dev.WElementFile('wires_1mil_80um_3.8_3pair.txt')
    def testWElement3Pairs(self):
        f=si.fd.EvenlySpacedFrequencyList(100e9,100)
        sp=si.sp.dev.WElementFile('wires_1mil_80um_3.8_3pair.txt',df=0.001,Z0=50,scale=1./1000.).SParameters(f)
        self.NetListChecker(sp.NetList(),self.testName())
        self.SParameterRegressionChecker(sp,self.testName()+'.s12p')
    def testWElementWireBond(self):
        f=si.fd.EvenlySpacedFrequencyList(100e9,100)
        sp=si.sp.dev.WElementFile('WireBond.txt',df=0.001,Z0=50,scale=1./1000.).SParameters(f)
        self.NetListChecker(sp.NetList(),self.testName())
        self.SParameterRegressionChecker(sp,self.testName()+'.s4p')
    def testWElement3PairsMixedMode(self):
        self.SParameterResultsChecker('WireBond3Pairs.si')
    def testWElementWireBondMixedMode(self):
        self.SParameterResultsChecker('WireBond.si')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()