"""
TestEncryption.py
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
import math
import SignalIntegrity.Lib as si
import numpy as np
import os
from SignalIntegrity.Lib.Encryption import Encryption

class TestEncryptionTest(unittest.TestCase,
        si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    epsilon=50e-12
    def removeFile(self,filename):
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])
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
        Encryption.password=None
        Encryption.ending='$'
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.removeFile('CoupledMM$.s4p')
        self.removeFile('tlinetest$.si')
        self.removeFile('tlinetest2$.si')
        self.removeFile('TLineModelDiffModeOnly$.si')
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
    def testEncryptionEndingSParametersNoActualEncryption(self):
        with open('CoupledMM.s4p','r') as f:
            linesRegression=f.readlines()
        sf = si.sp.SParameterFile('CoupledMM.s4p')
        self.assertTrue(Encryption.password==None,'encryption password incorrect')
        self.assertTrue(Encryption.ending=='$','encryption ending incorrect')
        sf.WriteToFile('CoupledMM$.s4p')
        with open('CoupledMM$.s4p','r') as f:
            lines=f.readlines()
        self.assertEqual(linesRegression,lines,'regression lines don\'t match')
        sf = si.sp.SParameterFile('CoupledMM$.s4p')
        fileName=self.NameForTest()+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile(fileName)
            self.assertTrue(False,fileName + ' does not exist')
        regression = si.sp.SParameterFile(fileName,50.)
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.NameForTest()+' result not same')
    def testEncryptionEndingSParametersEncrypted(self):
        with open('CoupledMM.s4p','r') as f:
            linesRegression=f.readlines()
        sf = si.sp.SParameterFile('CoupledMM.s4p')
        Encryption(pwd='test',ending='$')
        self.assertTrue(Encryption.password=='test','encryption password incorrect')
        self.assertTrue(Encryption.ending=='$','encryption ending incorrect')
        sf.WriteToFile('CoupledMM$.s4p')
        with open('CoupledMM$.s4p','r') as f:
            lines=f.readlines()
        self.assertNotEqual(linesRegression,lines,'regression lines don\'t match')
        sf = si.sp.SParameterFile('CoupledMM$.s4p')
        fileName=self.NameForTest()+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile(fileName)
            self.assertTrue(False,fileName + ' does not exist')
        regression = si.sp.SParameterFile(fileName,50.)
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.NameForTest()+' result not same')
    def testEncryptionEndingSParametersEncryptedWrongPassword(self):
        with open('CoupledMM.s4p','r') as f:
            linesRegression=f.readlines()
        sf = si.sp.SParameterFile('CoupledMM.s4p')
        Encryption(pwd='test',ending='$')
        self.assertTrue(Encryption.password=='test','encryption password incorrect')
        self.assertTrue(Encryption.ending=='$','encryption ending incorrect')
        sf.WriteToFile('CoupledMM$.s4p')
        with open('CoupledMM$.s4p','r') as f:
            lines=f.readlines()
        self.assertNotEqual(linesRegression,lines,'regression lines don\'t match')
        sf2 = si.sp.SParameterFile('CoupledMM$.s4p')
        self.assertTrue(self.SParametersAreEqual(sf,sf2,0.001),self.NameForTest()+' encrypted result not same')
        Encryption.password=None
        with self.assertRaises(si.SignalIntegrityExceptionSParameterFile) as cm:
            _ = si.sp.SParameterFile('CoupledMM$.s4p')
        self.assertEqual(cm.exception.parameter,'SParameterFile')
        Encryption(pwd='wrong password',ending='')
        with self.assertRaises(si.SignalIntegrityExceptionSParameterFile) as cm:
            _ = si.sp.SParameterFile('CoupledMM$.s4p')
        self.assertEqual(cm.exception.parameter,'SParameterFile')
    def testEncriptedProject(self):
        pysi=self.Preliminary('tlinetest.si')
        Encryption(pwd='test',ending='$')
        pysi.SaveProjectToFile('tlinetest$.si')
        self.SParameterResultsChecker('tlinetest$.si')
    def testEncriptedInternalProject(self):
        import SignalIntegrity.App as siapp
        Encryption(pwd='test',ending='$')
        pysi=self.Preliminary('tlinetest.si')
        internalFile=pysi.Device('D1')['file']['Value']
        self.assertEqual(internalFile, 'TLineModelDiffModeOnly.si', 'internal device incorrect for test')
        pysi.Device('D1')['file']['Value']='TLineModelDiffModeOnly$.si'
        pysi.SaveProjectToFile('tlinetest2$.si')
        pysi=siapp.SignalIntegrityAppHeadless()
        pysi.OpenProjectFile(internalFile)
        pysi.SaveProjectToFile('TLineModelDiffModeOnly$.si')
        self.SParameterResultsChecker('tlinetest2$.si')

if __name__ == "__main__": # pragma: no cover
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()