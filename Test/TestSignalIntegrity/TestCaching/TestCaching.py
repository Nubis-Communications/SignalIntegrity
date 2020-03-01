"""
TestCaching.py
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
import shutil
from App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless


class TestCachingTest(unittest.TestCase,
                      si.test.SParameterCompareHelper,
                      si.test.SignalIntegrityAppTestHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True

    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))

    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])

    def setUp(self):
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        shutil.copyfile('./Base/TopWaveformGeneratorBase.si','./TopWaveformGenerator.si')
        shutil.copyfile('./Base/MiddleWaveformGeneratorBase.si','./MiddleWaveformGenerator.si')
        shutil.copyfile('./Base/BottomWaveformGeneratorBase.si','./BottomWaveformGenerator.si')
        #shutil.copyfile('./Base/TopSParameterGeneratorBase.si','./TopSParameterGenerator.si')
        shutil.copyfile('./Base/MiddleSParameterGeneratorBase.si','./MiddleSParameterGenerator.si')
        shutil.copyfile('./Base/BottomSParameterGeneratorBase.si','./BottomSParameterGenerator.si')
        try:
            os.remove('./TopWaveformGenerator_cachedTransferMatrices.p')
        except FileNotFoundError:
            pass
        try:
            os.remove('./MiddleWaveformGenerator_cachedTransferMatrices.p')
        except FileNotFoundError:
            pass
        try:
            os.remove('./BottomWaveformGenerator_cachedTransferMatrices.p')
        except FileNotFoundError:
            pass
        try:
            os.remove('./TopSParameterGenerator_cachedSParameters.p')
        except FileNotFoundError:
            pass
        try:
            os.remove('./MiddleSParameterGenerator_cachedSParameters.p')
        except FileNotFoundError:
            pass
        try:
            os.remove('./BottomSParameterGenerator_cachedSParameters.p')
        except FileNotFoundError:
            pass
        
    def tearDown(self):
        os.remove('./TopWaveformGenerator.si')
        os.remove('./MiddleWaveformGenerator.si')
        os.remove('./BottomWaveformGenerator.si')
        #os.remove('./TopSParameterGenerator.si')
        os.remove('./MiddleSParameterGenerator.si')
        os.remove('./BottomSParameterGenerator.si')
        try:
            os.remove('./TopWaveformGenerator_cachedTransferMatrices.p')
        except FileNotFoundError:
            pass
        try:
            os.remove('./MiddleWaveformGenerator_cachedTransferMatrices.p')
        except FileNotFoundError:
            pass
        try:
            os.remove('./BottomWaveformGenerator_cachedTransferMatrices.p')
        except FileNotFoundError:
            pass
        try:
            os.remove('./TopSParameterGenerator_cachedSParameters.p')
        except FileNotFoundError:
            pass
        try:
            os.remove('./MiddleSParameterGenerator_cachedSParameters.p')
        except FileNotFoundError:
            pass
        try:
            os.remove('./BottomSParameterGenerator_cachedSParameters.p')
        except FileNotFoundError:
            pass
        os.chdir(self.cwd)
        unittest.TestCase.tearDown(self)

    def testRunInitial(self):
        """
        This test simply tests that the normal results are as expected
        """
        self.SimulationResultsChecker('TopWaveformGenerator.si')

    def testWaveform50(self):
        proj=SignalIntegrityAppHeadless()
        proj.OpenProjectFile('TopWaveformGenerator.si')
        (sourceNames,outputNames,transferMatrices,outputWaveforms)=proj.Simulate()
        self.WaveformRegressionChecker(outputWaveforms[0], 'Waveform50.txt')

    def testRunChangeBottomResistor(self):
        """
        This test runs the simulation as normally, but then goes to the bottom project and changes
        the resistance value from 50 to 40 ohms.  This ought to cause a recalculation, but it doesn't,
        so the test fails, in that it actually equals Waveform50, not Waveform40.
        """
        proj=SignalIntegrityAppHeadless()
        proj.OpenProjectFile('TopWaveformGenerator.si')
        (sourceNames,outputNames,transferMatrices,outputWaveforms)=proj.Simulate()
        
        proj=SignalIntegrityAppHeadless()
        proj.OpenProjectFile('BottomSParameterGenerator.si')
        for part in proj.Drawing.schematic.deviceList:
            if part['partname'].GetValue() == 'Resistor':
                part['r'].SetValueFromString('40')
        proj.SaveProject()
        
        proj=SignalIntegrityAppHeadless()
        proj.OpenProjectFile('TopWaveformGenerator.si')
        (sourceNames,outputNames,transferMatrices,outputWaveforms)=proj.Simulate()
        # this test will fail until caching is properly implemented...
        self.WaveformRegressionChecker(outputWaveforms[0], 'Waveform40.txt')

    def testAAARunChangeBottomResistorFirst(self):
        """
        This test edits the bottom project and changes the resistance value from 50 to 40 ohms.
        This causes the expected failure that results from the already saved correct test result expecting 50.
        """
        #self.SimulationResultsChecker('TopWaveformGenerator.si')
        
        proj=SignalIntegrityAppHeadless()
        proj.OpenProjectFile('BottomSParameterGenerator.si')
        for part in proj.Drawing.schematic.deviceList:
            if part['partname'].GetValue() == 'Resistor':
                part['r'].SetValueFromString('40')
        proj.SaveProject()

        proj=SignalIntegrityAppHeadless()
        proj.OpenProjectFile('TopWaveformGenerator.si')
        (sourceNames,outputNames,transferMatrices,outputWaveforms)=proj.Simulate()
        self.WaveformRegressionChecker(outputWaveforms[0], 'Waveform40.txt')

if __name__ == "__main__":
    import sys;sys.argv = ['', 'TestCachingTest.testRunChangeBottomResistor']
    unittest.main()