"""
TestNonlinearIterations.py
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

import os
import unittest

import SignalIntegrity.Lib as si
import SignalIntegrity.App as siapp

class TestNonlinearIterationTest(unittest.TestCase,
        si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper):
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
        self.Autoshutoff=SignalIntegrity.App.Preferences['Calculation.AutoshutoffIterations']
        SignalIntegrity.App.Preferences['Calculation.AutoshutoffIterations']=False
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        os.chdir(self.cwd)
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation.AutoshutoffIterations']=self.Autoshutoff
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))

    def testNonlinBase(self):
        self.SimulationResultsChecker('DanielTestTwoProbe_nonlin_source.si')

    def testNonlinWPortFail1(self):

        filename = 'DanielTest_port_dependent.si'
        pysi=self.Preliminary(filename)
        result=pysi.Simulate()
        self.assertIsNone(result, filename+' produced something - this is unexpected')

    def testNonlinWPortFail2(self):
        filename = 'DanielTest_port_dependent.si'
        pysi=self.Preliminary(filename)
        result=pysi.CalculateSParameters()
        self.assertIsNone(result, filename+' produced something - this is unexpected')
        
    def testNonlinAutoshutoff(self):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        #Turn on autoshutoff
        SignalIntegrity.App.Preferences['Calculation.AutoshutoffIterations']=True
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()

        #Run test - have to make new file name cause waveform of authoshutoff will be different then large # iterations
        #cause it clips the waveform more
        origFileName = 'DanielTestTwoProbe_nonlin_source.si'
        newFileName = 'DanielTestTwoProbe_nonlin_source_AS.si'
        pysi.OpenProjectFile(origFileName)
        pysi.SaveProjectToFile(newFileName)
        self.SimulationResultsChecker(newFileName)

        SignalIntegrity.App.Preferences['Calculation.AutoshutoffIterations']=False
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()


    def NonlinParameterTest(self, scale = 4, tf_fn = 'scale_nonlin'):
        base_fn = 'DanielTestTwoProbe_nonlin_source_parameterized'
        app=siapp.SignalIntegrityAppHeadless()
        app.OpenProjectFile(base_fn + '.si',{'NLS1_scale':scale, 'tf_fn':tf_fn + '.py'})
        filename='DanielTestTwoProbe_nonlin_source_parameterized'+str(scale)+tf_fn + '.si'
        app.SaveProjectToFile(filename)
        return filename
    
    def testNonlinParameterizedBase(self):
        self.SimulationResultsChecker('DanielTestTwoProbe_nonlin_source_parameterized.py')

    def testNonlinParameterizedParams(self):
        self.SimulationResultsChecker(self.NonlinParameterTest(scale=8, tf_fn='scaledown_nonlin'))

    def testNonlinParameterizedFail1(self):
        filename = (self.NonlinParameterTest(scale=8, tf_fn = 'fake_file'))
        pysi=self.Preliminary(filename)
        result=pysi.Simulate()
        self.assertIsNone(result, filename+' produced something - this is unexpected')

    def testNonlinParameterizedFail2(self):
        filename = (self.NonlinParameterTest(scale=8, tf_fn = 'scale_nonlin_noOutput'))
        pysi=self.Preliminary(filename)
        result=pysi.Simulate()
        self.assertIsNone(result, filename+' produced something - this is unexpected')

    def testNonlinParameterizedFail3(self):
        filename = (self.NonlinParameterTest(scale=8, tf_fn = 'scale_nonlin_error'))
        pysi=self.Preliminary(filename)
        result=pysi.Simulate()
        self.assertIsNone(result, filename+' produced something - this is unexpected')

    def testNonlinParameterizedFail4(self):

        filename = 'DanielTestTwoProbe_nonlin_source_parameterized_missing.py'
        pysi=self.Preliminary(filename)
        result=pysi.Simulate()
        self.assertIsNone(result, filename+' produced something - this is unexpected')

    def testNoNonlin(self):
        self.SimulationResultsChecker('DanielTest_nononlin.si')
    def testNonlinParametersNested(self):
        self.SimulationResultsChecker('DanielTestTwoProbe_nonlin_source_nested.si')

    def testNonlinParametersOtherVarTypes(self):
        self.SimulationResultsChecker('DanielTestTwoProbe_nonlin_source_parameterized_intstrtest.si')

    def NonlinNestedParameterTest(self, scale1 = 2, scale2 = 16):
        base_fn = 'DanielTestTwoProbe_nonlin_source_nested'
        app=siapp.SignalIntegrityAppHeadless()
        app.OpenProjectFile(base_fn + '.si',{'NLS1_scale':scale1, 'VS1_NLS1_scale':scale2})
        filename='DanielTestTwoProbe_nonlin_source_nested'+str(scale1)+ ',' + str(scale2)+ '.si'
        app.SaveProjectToFile(filename)
        return filename
    
    def testNonlinParmetersNested2(self):
        self.SimulationResultsChecker(self.NonlinNestedParameterTest(scale1 = 2, scale2 = 16),)

    def testNonlinParmetersNested2(self):
        self.SimulationResultsChecker('DanielTestTwoProbe_nonlin_twoport_source.si')

    def testNotLongEnoughWaveform(self):
        filename = 'TestNotLongEnoughWaveform.si'
        pysi=self.Preliminary(filename)
        result=pysi.Simulate()
        self.assertIsNone(result, filename+' produced something - this is unexpected')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()