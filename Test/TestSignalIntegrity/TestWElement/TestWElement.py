"""
TestWElement.py
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
import os

import SignalIntegrity.Lib as si
from SignalIntegrity.Lib.SParameters.Devices.WElement import MaxwellMatrix,MutualMatrix

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
    def testWElement3Pairs(self):
        f=si.fd.EvenlySpacedFrequencyList(100e9,100)
        sp=si.sp.dev.WElementFile(f,'wires_1mil_80um_3.8_3pair.txt',df=0.001,Z0=50,scale=1./1000.)
        Cm=sp.C0
        Cm2=MaxwellMatrix(MutualMatrix(sp.C0).MaxwellMatrix()).MutualMatrix()
        for r in range(len(Cm)):
            for c in range(len(Cm[r])):
                self.assertAlmostEqual(Cm[r][c],Cm2[r][c],6,'Maxwell matrix incorrect')
        self.NetListChecker(sp.NetList(),self.testName())
        self.SParameterRegressionChecker(sp,self.testName()+'.s12p')
    def testWElementWireBond(self):
        f=si.fd.EvenlySpacedFrequencyList(100e9,100)
        sp=si.sp.dev.WElementFile(f,'WireBond.txt',df=0.001,Z0=50,scale=1./1000.)
        self.NetListChecker(sp.NetList(),self.testName())
        self.SParameterRegressionChecker(sp,self.testName()+'.s4p')
    def testWElementMicrostrip(self):
        f=si.fd.EvenlySpacedFrequencyList(20e9,1000)
        sp=si.sp.dev.WElementFile(f,'microstrip.hspice-w.rlgc',df=0.01,Z0=50,scale=200./1000.)
        self.NetListChecker(sp.NetList(),self.testName())
        self.SParameterRegressionChecker(sp,self.testName()+'.s2p')
    def testWElement3PairsMixedMode(self):
        self.SParameterResultsChecker('WireBond3Pairs.si')
    def testWElementWireBondMixedMode(self):
        self.SParameterResultsChecker('WireBond.si')
    def testWElementParserDeviceOnePair(self):
        f=si.fd.EvenlySpacedFrequencyList(100e9,100)
        sspnp=si.p.SystemSParametersNumericParser(f)
        sspnp.AddLines(['device W1 4 w WireBond.txt df 0.001 scale 0.001','port 1 W1 1 2 W1 2 3 W1 3 4 W1 4'])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,'TestWElementTest_testWElementWireBond.s4p')
    def testWElementParserDeviceThreePairs(self):
        f=si.fd.EvenlySpacedFrequencyList(100e9,100)
        sspnp=si.p.SystemSParametersNumericParser(f)
        sspnp.AddLines(['device W1 12 w wires_1mil_80um_3.8_3pair.txt df 0.001 scale 0.001',
                        'port 1 W1 1 2 W1 2 3 W1 3 4 W1 4 5 W1 5 6 W1 6 7 W1 7 8 W1 8 9 W1 9 10 W1 10 11 W1 11 12 W1 12'])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,'TestWElementTest_testWElement3Pairs.s12p')
    def testWElement3PairsMixedModeWElement(self):
        self.SParameterResultsChecker('WireBond3PairsWElement.si')
    def testWElementWireBondMixedModeWElement(self):
        self.SParameterResultsChecker('WireBondWElement.si')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()