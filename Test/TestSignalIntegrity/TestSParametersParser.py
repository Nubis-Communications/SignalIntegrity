"""
TestSParametersParser.py
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

class TestSParametersParserTest(unittest.TestCase,si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper):
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
    def id(self):
        return '_'.join(unittest.TestCase.id(self).split('.')[-2:])
    def testSParameterParserWithFiles(self):
        """
        The object of this test is to test whether known devices installed in the SParameter parser
        get recognized and used properly without error and produce the same result whether the device
        gets read from the disk and resampled at s-parameter generation time.
        """
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1'])
        sp=sspnp.SParameters()

        sspnp2=si.p.SystemSParametersNumericParser(fd)
        sspnp2.AddLines(['device D1 2 cable thing',
                        'device D2 2 dbi filter',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1'])

        deviceList={'2 cable thing':si.sp.SParameterFile('cable.s2p').Resample(fd),
                    '2 dbi filter':si.sp.SParameterFile('filter.s2p').Resample(fd)}
        sspnp2.AddKnownDevices(deviceList)
        sp2=sspnp2.SParameters()

        self.assertTrue(self.SParametersAreEqual(sp,sp2,0.001),self.id()+' result not same')
    def testSParametersPostCausal(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post enforce reciprocity',
                        'post enforce passivity',
                        'post enforce causality',
                        'post limit none none',])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def testSParametersPostGarbage(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post garbage',])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sspnp.SParameters()
        self.assertEqual(cm.exception.parameter,si.SignalIntegrityExceptionPostProcessing().parameter)
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()