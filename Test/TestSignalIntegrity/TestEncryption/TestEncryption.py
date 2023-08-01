"""
TestEncryption.py
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
import math
import SignalIntegrity as si
import numpy as np
import os

class TestEncryptionTest(unittest.TestCase,
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
        self.UseSinX=SignalIntegrity.App.Preferences['Calculation.UseSinX']
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=True
        self.Caching=SignalIntegrity.App.Preferences['Cache.CacheResults']
        SignalIntegrity.App.Preferences['Cache.CacheResults']=False
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
        SignalIntegrity.App.Preferences['Cache.CacheResults']=self.Caching
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
    def testZippedSParameters(self):
        sf = si.sp.SParameterFile('CoupledMM_no_password.zip')
        fileName='_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile('_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p')
            self.assertTrue(False,fileName + ' does not exist')
        regression = si.sp.SParameterFile(fileName,50.)
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.id()+' result not same')
    def testEncryptedZippedSParameters(self):
        sf = si.sp.SParameterFile('CoupledMM_password.zip',pwd='test')
        fileName='_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile('_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p')
            self.assertTrue(False,fileName + ' does not exist')
        regression = si.sp.SParameterFile(fileName,50.)
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.id()+' result not same')
    def testEncryptedZippedSParametersWrongPassword(self):
        with self.assertRaises(si.SignalIntegrityExceptionSParameterFile) as cm:
            _ = si.sp.SParameterFile('CoupledMM_password.zip')
        self.assertEqual(cm.exception.parameter,'SParameterFile')
    def testZippedSParametersInternalProject(self):
        self.SParameterResultsChecker('CoupledMM_no_password.si')
    def testEncryptedZippedSParametersInternalProject(self):
        self.SParameterResultsChecker('CoupledMM_password.si')
    def testZippedInternalProject(self):
        self.SParameterResultsChecker('tlinetest.si')
    def testEncryptedInternalProject(self):
        self.SParameterResultsChecker('tlinetest_password.si')
    def testEncryptedInternalProjectWrongPassword(self):
        filename='tlinetest_wrongpassword.si'
        pysi=self.Preliminary(filename, True, True)
        result=pysi.CalculateSParameters()
        self.assertIsNone(result, filename+' produced none')
    def testEncriptedProject(self):
        pysi=self.Preliminary('tlinetest.si')
        pysi.SaveProjectToFile('tlinetest.zip')
        self.SParameterResultsChecker('tlinetest.zip')
