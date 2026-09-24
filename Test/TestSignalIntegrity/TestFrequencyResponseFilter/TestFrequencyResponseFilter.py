"""
TestFrequencyResponseFilter.py
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
import SignalIntegrity.App.SignalIntegrityAppHeadless as siapp
import os

class TestFrequencyResponseFilterTest(unittest.TestCase,
        si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper,
        si.test.RoutineWriterTesterHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    epsilon=50e-12

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        #si.test.SignalIntegrityAppTestHelper.forceWritePictures=True
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        self.UseSinX=SignalIntegrity.App.Preferences['Calculation.UseSinX']
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=False
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        os.chdir(self.cwd)
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=self.UseSinX
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        si.test.RoutineWriterTesterHelper.__init__(self)

    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])

    def testFrequencyResponseFilterSParameters(self):
        netlistLines=['device F1 2 frequencyresponsefilter FrequencyResponseFilter.txt dcgain 0',
                      'port 1 F1 1 2 F1 2']
        f=si.fd.EvenlySpacedFrequencyList(100e9,50)
        ssnp=si.p.SystemSParametersNumericParser(f).AddLines(netlistLines)
        sp=ssnp.SParameters()
        self.SParameterRegressionChecker(sp,self.NameForTest()+'.s2p')
    def testMissingFrequencyResponseFile(self):
        with self.assertRaises(si.SignalIntegrityExceptionWaveformFile) as cme:
            sp=si.sp.dev.FrequencyResponseFilter('FrequencyResponseFilterr.txt',normalizedDCGain=None)
    def testFrequencyResponseFileDirectly(self):
        sp=si.sp.dev.FrequencyResponseFilter('FrequencyResponseFilter.txt',normalizedDCGain=None)
        self.SParameterRegressionChecker(sp,self.NameForTest()+'.s2p')
    def testFrequencyResponseFileDC(self):
        sp=si.sp.dev.FrequencyResponseFilter('FrequencyResponseFilter.txt',normalizedDCGain=1.0)
        self.SParameterRegressionChecker(sp,self.NameForTest()+'.s2p')
    def testFrequencyResponseSimulation(self):
        si.test.SignalIntegrityAppTestHelper.plotErrors=True
        self.SimulationResultsChecker('FrequencyResponse.si')
    def testFrequencyResponseFileFromCSVMatchesText(self):
        spText=si.sp.dev.FrequencyResponseFilter('FrequencyResponseFilter.txt',normalizedDCGain=None)
        spCSV=si.sp.dev.FrequencyResponseFilter('FrequencyResponseFilter.csv',normalizedDCGain=None)
        self.assertTrue(self.SParametersAreEqual(spText,spCSV,1e-9),'csv and txt frequency responses differ')
    def testFrequencyResponseFileFromS2P(self):
        sp=si.sp.dev.FrequencyResponseFilter('../../../SignalIntegrity/App/Examples/CableModel/cable.s2p',normalizedDCGain=None)
        self.SParameterRegressionChecker(sp,self.NameForTest()+'.s2p')
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
