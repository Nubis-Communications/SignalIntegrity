"""
TestSignalIntegrityApp.py
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

from SignalIntegrity.App.PreferencesFile import PreferencesFile
from SignalIntegrity.App.Preferences import Preferences

class TestProjectFileTest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)

    def setUp(self):
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))


    def tearDown(self):
        if os.path.exists('preferencesOldStyle.xml'):
            os.remove('preferencesOldStyle.xml')
        os.chdir(self.cwd)


    def testProjectFileOldSurvival(self):
        pf=Preferences('preferencesOldStyle.si')
        pf.SaveToFile()


class TestConfigurationFields(unittest.TestCase):
    def setUp(self):
        from SignalIntegrity.App.ProjectFile import VariablesConfiguration
        self.variables=VariablesConfiguration()

    def variable(self,name,value,type='float'):
        from SignalIntegrity.App.ProjectFile import VariableConfiguration
        variable=VariableConfiguration()
        variable['Name'],variable['Value'],variable['Type']=name,str(value),type
        self.variables['Items'].append(variable)
        return variable

    def configuration(self,current=False,eye=False):
        from SignalIntegrity.App.ConfigurationProperty import BindConfiguration
        from SignalIntegrity.App.StatisticalNoisePreferencesFile import VoltageNoiseConfiguration,CurrentNoiseConfiguration
        from SignalIntegrity.App.EyeDiagramPreferencesFile import EyeConfiguration
        return BindConfiguration(EyeConfiguration() if eye else
                                 CurrentNoiseConfiguration() if current else VoltageNoiseConfiguration(),
                                 self.variables,'D1')

    def testLegacyDefaultsAndPartialVisibilityRoundTrip(self):
        import xml.etree.ElementTree as ET
        for parameters in ({},{'current':True},{'eye':True}):
            with self.subTest(parameters=parameters):
                configuration=self.configuration(**parameters)
                self.assertFalse(any(f.visible for f in configuration.configurationFields.values()))
                text=''.join(configuration.OutputXML(''))
                self.assertNotIn('ConfigurationFields',text)
                path=next(iter(configuration.configurationFields))
                configuration.configurationFields[path].visible=True
                configuration.InitFromXML(ET.fromstring(text))
                self.assertFalse(any(f.visible for f in configuration.configurationFields.values()))
                configuration.configurationFields[path].visible=True
                text=''.join(configuration.OutputXML(''))
                restored=self.configuration(**parameters).InitFromXML(ET.fromstring(text))
                self.assertEqual([f.path for f in restored.configurationFields.values() if f.visible],[path])
                self.assertNotIn('ConfigurationFields',restored.ToDictionary())

    def testTypedBindingsNestedReadsAndLiveVariableUpdates(self):
        from SignalIntegrity.App.ConfigurationProperty import ConfigurationError
        configuration=self.configuration(current=True)
        variable=self.variable('bandwidth',2.e9)
        self.variable('enabled','False','string')
        self.variable('mode','ShotNoise','enum')
        self.variable('probe','IP1','string')
        configuration['Enable']='=enabled'
        configuration['Type']='=mode'
        configuration['ShotNoise.NoiseBandwidth']='=bandwidth'
        configuration['ShotNoise.ProbeName']='=probe'
        self.assertIs(configuration['Enable'],False)
        self.assertEqual(configuration['Type'],'ShotNoise')
        self.assertEqual(configuration['ShotNoise']['NoiseBandwidth'],2.e9)
        self.assertEqual(configuration['ShotNoise.ProbeName'],'IP1')
        variable['Value']='3e9'
        self.assertEqual(configuration['ShotNoise.NoiseBandwidth'],3.e9)
        with self.assertRaisesRegex(ConfigurationError,'D1.*ShotNoise.NoiseBandwidth.*does not exist'):
            configuration['ShotNoise.NoiseBandwidth']='=absent'
            configuration['ShotNoise.NoiseBandwidth']
        self.variable('a','=b','string')
        self.variable('b','=a','string')
        configuration['Enable']='=a'
        with self.assertRaisesRegex(ConfigurationError,'cyclic'):
            configuration['Enable']

    def testValidationAndLiteralReplacementLeaveVariablesUnchanged(self):
        from SignalIntegrity.App.ConfigurationProperty import ConfigurationError
        configuration=self.configuration(eye=True)
        variable=self.variable('rows',250)
        configuration['Rows']='=rows'
        field=configuration.configurationFields['Rows']
        self.assertEqual(field.EntryString(),'=rows')
        self.assertIn('250',field.DisplayString())
        field.SetEntry('300')
        self.assertFalse(field.reference)
        self.assertEqual(configuration['Rows'],300)
        self.assertEqual(variable['Value'],'250')
        for value in ('2.5','nan','0'):
            with self.assertRaises(ConfigurationError):
                field.SetEntry(value)
            self.assertEqual(configuration['Rows'],300)
        mode=configuration.configurationFields['Mode']
        with self.assertRaisesRegex(ConfigurationError,'allowed keywords'):
            mode.SetEntry('Jitter & Noise')
        self.assertEqual(configuration['Mode'],'ISI')
        self.assertIn('JitterNoise',mode.Help())

    def testBindingAndCalculatedVisibilitySurviveXML(self):
        import xml.etree.ElementTree as ET
        configuration=self.configuration(eye=True)
        self.variable('noise',.002)
        configuration['JitterNoise.Noise']='=noise'
        field=configuration.configurationFields['JitterNoise.TotalNoise']
        field.visible=True
        text=''.join(configuration.OutputXML(''))
        self.assertNotIn('<TotalNoise>',text)
        restored=self.configuration(eye=True).InitFromXML(ET.fromstring(text))
        self.assertEqual(restored.configurationFields['JitterNoise.Noise'].EntryString(),'=noise')
        self.assertEqual(restored['JitterNoise.Noise'],.002)
        self.assertTrue(restored.configurationFields['JitterNoise.TotalNoise'].visible)

    def testInactiveFieldsAndCalculatedFields(self):
        from SignalIntegrity.App.ConfigurationProperty import ConfigurationError,ValidateConfiguration
        configuration=self.configuration(current=True)
        field=configuration.configurationFields['ShotNoise.MeanCurrent']
        field.visible=True
        self.assertFalse(field.Active())
        configuration['Enable']=True
        configuration['Type']='ShotNoise'
        self.assertTrue(field.Active())
        self.variable('current',.001)
        field.SetEntry('=current')
        configuration['ShotNoise.CurrentSource']='TimeVarying'
        self.assertTrue(field.Computed())
        with self.assertRaisesRegex(ConfigurationError,'calculated'):
            field.SetEntry('.002')
        configuration['ShotNoise.MeanCurrent']=.003
        self.assertEqual(field.reference,'current')
        self.assertEqual(field.Value(),.003)
        configuration['ShotNoise.CurrentSource']='Mean'
        self.assertEqual(field.Value(),.001)
        eye=self.configuration(eye=True)
        self.variable('bad_noise','oops','string')
        eye['JitterNoise.Noise']='=bad_noise'
        ValidateConfiguration(eye)
        eye['Mode']='JitterNoise'
        with self.assertRaises(ConfigurationError):
            ValidateConfiguration(eye)

    def testBoundNoiseMatchesLiteralAndConversionsPreserveLinks(self):
        import numpy as np
        from SignalIntegrity.App.ConfigurationProperty import UpdateConfiguration
        configuration=self.configuration()
        configuration['Enable']=True
        configuration['WhiteNoise.NoiseBandwidth']=2.e9
        self.variable('density',1.e-9)
        self.variable('rms',.123)
        configuration['WhiteNoise.VPerRootHz']='=density'
        configuration['WhiteNoise.VRms']='=rms'
        expected=self.configuration()
        expected['Enable']=True
        expected['WhiteNoise.NoiseBandwidth']=2.e9
        expected['WhiteNoise.VPerRootHz']=1.e-9
        np.testing.assert_array_equal(configuration.SpectralDensity(4.e9,16).Values(),
                                      expected.SpectralDensity(4.e9,16).Values())
        UpdateConfiguration(configuration,'WhiteNoise.VPerRootHz')
        self.assertEqual(configuration.configurationFields['WhiteNoise.VRms'].reference,'rms')
        self.assertEqual(configuration['WhiteNoise.VRms'],.123)

    def testDisablingInvalidNoiseSelectorAndPreservingLiteralMeanCurrent(self):
        configuration=self.configuration(current=True)
        configuration['Enable']=True
        configuration['Type']='=missing'
        configuration.configurationFields['Enable'].SetEntry('False')
        self.assertFalse(configuration['Enable'])
        configuration['Type']='ShotNoise'
        configuration['ShotNoise.MeanCurrent']=.001
        configuration['ShotNoise.CurrentSource']='TimeVarying'
        configuration['ShotNoise.MeanCurrent']=.003
        field=configuration.configurationFields['ShotNoise.MeanCurrent']
        self.assertEqual(field.Value(),.003)
        self.assertEqual(field.EntryString(),'3.0 mA')
        configuration['ShotNoise.CurrentSource']='Mean'
        self.assertEqual(field.Value(),.001)

    def testCopiedConfigurationCanBeReboundToAnotherProject(self):
        import copy
        from SignalIntegrity.App.ProjectFile import VariablesConfiguration,VariableConfiguration
        from SignalIntegrity.App.ConfigurationProperty import BindConfiguration
        configuration=self.configuration()
        self.variable('lanes',2)
        configuration['Lanes']='=lanes'
        duplicate=copy.deepcopy(configuration)
        variables=VariablesConfiguration()
        value=VariableConfiguration()
        value['Name'],value['Value']='lanes','4'
        variables['Items'].append(value)
        BindConfiguration(duplicate,variables)
        self.assertEqual(configuration['Lanes'],2.)
        self.assertEqual(duplicate['Lanes'],4.)

    def testEyeDimensionEditsPreserveSizeAndBoundScale(self):
        configuration=self.configuration(eye=True)
        width=configuration['UI']*configuration['Columns']*configuration['ScaleX']
        height=configuration['Rows']*configuration['ScaleY']
        configuration.configurationFields['Rows'].SetEntry('400')
        configuration.configurationFields['UI'].SetEntry('3')
        self.assertAlmostEqual(configuration['Rows']*configuration['ScaleY'],height)
        self.assertAlmostEqual(configuration['UI']*configuration['Columns']*configuration['ScaleX'],width)
        self.variable('scale',50.)
        configuration['ScaleX']='=scale'
        configuration.configurationFields['Columns'].SetEntry('128')
        self.assertEqual(configuration['ScaleX'],50.)
        self.assertEqual(configuration.configurationFields['ScaleX'].reference,'scale')

    def testVisibilityDoesNotChangeNumericalInputsAndLiveBindingsDo(self):
        configuration=self.configuration()
        original=configuration.ToDictionary()
        configuration.configurationFields['WhiteNoise.NoiseBandwidth'].visible=True
        self.assertEqual(configuration.ToDictionary(),original)
        variable=self.variable('density',1.e-9)
        configuration['WhiteNoise.VPerRootHz']='=density'
        before=configuration.ToDictionary()
        variable['Value']='2e-9'
        self.assertNotEqual(configuration.ToDictionary(),before)

    def testPreferenceDefaultsMaterializeBindingsWithoutLeakingProjectContext(self):
        import xml.etree.ElementTree as ET
        from unittest.mock import patch
        import SignalIntegrity.App
        from SignalIntegrity.App.EyeDiagramConfiguration import EyeDiagramConfiguration
        from SignalIntegrity.App.ConfigurationProperty import BindConfiguration
        configuration=BindConfiguration(EyeDiagramConfiguration(),self.variables)
        self.variable('rows',320)
        configuration['Rows']='=rows'
        configuration.configurationFields['Rows'].visible=True
        preferences=PreferencesFile()
        target=preferences['Devices.EyeDiagram']
        with patch.object(SignalIntegrity.App,'Preferences',preferences),patch.object(preferences,'SaveToFile',create=True):
            configuration.SaveToPreferences()
            self.assertEqual(target['Rows'],320)
            self.assertFalse(target.configurationFields['Rows'].reference)
            self.assertIsNone(getattr(target,'configurationVariables',lambda:None)())
            created=EyeDiagramConfiguration().InitializeFromPreferences()
            self.assertTrue(created.configurationFields['Rows'].visible)
            created.InitFromXML(ET.fromstring('<EyeDiagram><Rows>200</Rows></EyeDiagram>'))
            self.assertEqual(created['Rows'],200)
            self.assertFalse(any(field.visible for field in created.configurationFields.values()))
            self.assertEqual(configuration.configurationFields['Rows'].reference,'rows')
    def testSpectralDensityBrowseUsesResolvedFileAndPreservesCancellation(self):
        import os
        from unittest.mock import patch
        from SignalIntegrity.App.ConfigurationProperty import BrowseConfigurationFile,ConfigurationError
        from SignalIntegrity.App.Files import FileParts
        configuration=self.configuration()
        self.variable('spectrum',os.path.join('noise','source.csv'),'file')
        configuration['SpectralDensityFile.FileName']='=spectrum'
        field=configuration.configurationFields['SpectralDensityFile.FileName']
        project=FileParts(os.path.join(os.getcwd(),'project.si'))
        with patch('SignalIntegrity.App.FilePicker.AskOpenFileName',return_value=None) as picker:
            self.assertEqual(BrowseConfigurationFile(field,'=spectrum',project,None),'')
        self.assertEqual(picker.call_args.kwargs['initialdir'],os.path.join(project.AbsoluteFilePath(),'noise'))
        self.assertEqual(picker.call_args.kwargs['initialfile'],'source.csv')
        self.assertEqual(picker.call_args.kwargs['filetypes'][0][1],('.txt','.csv','.json'))
        self.assertEqual(field.reference,'spectrum')
        with self.assertRaisesRegex(ConfigurationError,'does not exist'):
            BrowseConfigurationFile(field,'=missing',project,None)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()