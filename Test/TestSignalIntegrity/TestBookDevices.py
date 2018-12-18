"""
TestBookDevices.py
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
from SignalIntegrity.App import SignalIntegrityAppHeadless
from SignalIntegrity.App import TpX
from SignalIntegrity.App import TikZ
import SignalIntegrity.Lib as si
import os

class TestBookDevicesTest(unittest.TestCase,si.test.SignalIntegrityAppTestHelper):
    checkPictures=True
    def __init__(self, methodName='runTest'):
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.abspath('../../../SignalIntegrityBook/SignalIntegrityApp'))
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        #si.test.SignalIntegrityAppTestHelper.forceWritePictures=True
        os.chdir(self.path)
        self.book=os.path.exists('../../../../SignalIntegrityBook/')
    def testBookDevices(self):
        filesList=[
            'File.si',
            'Open.si',
            'Port.si',
            'Stim.si',
            'Ground.si',
            'Mutual.si',
            'System.si',
            'Unknown.si',
            'Inductor.si',
            'Resistor.si',
            'Capacitor.si',
            'OpenTLine.si',
            'CurrentSource.si',
            'TLine.si',
            'VoltageSource.si',
            'CurrentAmplifier.si',
            'IdealTransformer.si',
            'VoltageAmplifier.si',
            'CurrentOutputProbe.si',
            'TelegrapherTwoPort.si',
            'VoltageOutputProbe.si',
            'TelegrapherFourPort.si',
            'VoltageMeasureProbe.si',
            'CurrentSineGenerator.si',
            'CurrentStepGenerator.si',
            'OperationalAmplifier.si',
            'VoltageSineGenerator.si',
            'VoltageSourceOnePort.si',
            'VoltageStepGenerator.si',
            'CurrentPulseGenerator.si',
            'VoltageNoiseGenerator.si',
            'VoltagePulseGenerator.si',
            'PowerMixedModeConverter.si',
            'TransresistanceAmplifier.si',
            'TransconductanceAmplifier.si',
            'VoltageMixedModeConverter.si',
            'DirectionalCoupler.si',
            'CurrentControlledCurrentSource.si',
            'CurrentControlledVoltageSource.si',
            'DifferentialVoltageOutputProbe.si',
            'VoltageControlledCurrentSource.si',
            'VoltageControlledVoltageSource.si',
        ]
        for filename in filesList:
            self.setUp()
            if not 'SignalIntegrityBook' in filename or self.book:
                #print filename
                os.chdir(self.path)
                from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
                import SignalIntegrity.App.Project
                pysi=SignalIntegrityAppHeadless()
                SignalIntegrity.App.Preferences['Appearance.AllPinNumbersVisible']=True
                self.assertTrue(pysi.OpenProjectFile(os.path.realpath(filename)),filename + ' couldnt be opened')
                SignalIntegrity.App.Project['Drawing.DrawingProperties.Grid']=16.
                pysi.SaveProjectToFile(filename)
                self.PictureChecker(pysi,filename)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
