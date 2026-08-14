"""
PreferencesFile.py
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
from SignalIntegrity.App.ProjectFileBase import XMLConfiguration,XMLPropertyDefaultString,XMLPropertyDefaultInt,XMLPropertyDefaultBool,XMLPropertyDefaultFloat
from SignalIntegrity.App.ProjectFileBase import ProjectFileBase,XMLProperty
from SignalIntegrity.App.SParameterProperties import SParameterProperties

class DeviceConfigurations(XMLConfiguration):
    def __init__(self):
        from StatisticalNoisePreferencesFile import VoltageNoiseConfiguration,CurrentNoiseConfiguration
        from EyeDiagramPreferencesFile import EyeConfiguration
        super().__init__('Devices')
        self.SubDir(EyeConfiguration())
        self.SubDir(VoltageNoiseConfiguration())
        self.SubDir(CurrentNoiseConfiguration())

class Color(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Color')
        self.Add(XMLPropertyDefaultString('Background'))
        self.Add(XMLPropertyDefaultString('Foreground'))
        self.Add(XMLPropertyDefaultString('ActiveBackground'))
        self.Add(XMLPropertyDefaultString('ActiveForeground'))
        self.Add(XMLPropertyDefaultString('DisabledForeground'))
        self.Add(XMLPropertyDefaultString('Plot'))

class Appearance(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Appearance')
        self.Add(XMLPropertyDefaultInt('FontSize',12))
        self.Add(XMLPropertyDefaultInt('InitialGrid',16))
        self.Add(XMLPropertyDefaultFloat('PlotWidth',5))
        self.Add(XMLPropertyDefaultFloat('PlotHeight',2))
        self.Add(XMLPropertyDefaultInt('PlotDPI',100))
        self.Add(XMLPropertyDefaultBool('PlotCursorValues',False))
        self.Add(XMLPropertyDefaultBool('AllPinNumbersVisible',False))
        self.Add(XMLPropertyDefaultBool('GridsOnPlots',True))
        self.Add(XMLPropertyDefaultInt('RoundDisplayedValues',4))
        self.Add(XMLPropertyDefaultInt('LimitText',60))
        self.SubDir(Color())

class Variables(XMLConfiguration):
    def __init__(self):
        super().__init__('Variables')
        self.Add(XMLPropertyDefaultBool('ParameterizeOnlyVisible',True))

class Calculation(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Calculation')
        self.Add(XMLPropertyDefaultBool('TrySVD',True))
        self.Add(XMLPropertyDefaultBool('AllowNonUniqueSolutions',False))
        self.Add(XMLPropertyDefaultBool('CheckConditionNumber',True))
        self.Add(XMLPropertyDefaultBool('UseSinX',True))
        self.Add(XMLPropertyDefaultBool('Enforce12458',True))
        self.Add(XMLPropertyDefaultFloat('MaximumWaveformSize',5e6))
        self.Add(XMLPropertyDefaultBool('MultiPortTee',True))
        self.Add(XMLPropertyDefaultBool('IgnoreMissingOtherWaveforms',True))
        self.Add(XMLPropertyDefaultBool('LogarithmicSolutions',False))
        self.Add(XMLPropertyDefaultBool('Non50OhmSolutions',False))
        self.Add(XMLPropertyDefaultBool('AllowParallelization',False))
        self.Add(XMLPropertyDefaultBool('AllowMaximumImpulseResponseLength',False))
    def ApplyPreferences(self):
        import SignalIntegrity.Lib as si
        si.td.wf.Waveform.adaptionStrategy='SinX' if self['UseSinX'] else 'Linear'
        si.td.wf.Waveform.maximumWaveformSize = self['MaximumWaveformSize']
        si.sd.Numeric.trySVD=self['TrySVD']
        si.sd.Numeric.allowPossibleNonUniqueSolutions=self['AllowNonUniqueSolutions']
        si.sd.Numeric.checkConditionNumber=self['CheckConditionNumber']
        si.p.SystemDescriptionParser.MultiPortTee=self['MultiPortTee']

class Cache(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Cache')
        self.Add(XMLPropertyDefaultBool('CacheResults',True))
        self.Add(XMLPropertyDefaultInt('NumberOfFiles',1))
        self.Add(XMLPropertyDefaultBool('KeepExtraFileForArchive',False))
        self.Add(XMLPropertyDefaultBool('Logging',False))
        self.Add(XMLPropertyDefaultBool('CheckTimes',True))
    def ApplyPreferences(self):
        from SignalIntegrity.Lib.ResultsCache import ResultsCache
        ResultsCache.files_to_keep = self['NumberOfFiles']
        ResultsCache.keep_extra_file_for_archive = self['KeepExtraFileForArchive']
        ResultsCache.logging = self['Logging']
        ResultsCache.check_times = self['CheckTimes']

class LastFiles(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'LastFiles')
        self.Add(XMLPropertyDefaultString('Name'))
        self.Add(XMLPropertyDefaultString('Directory'))

class Encryption(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Encryption')
        self.Add(XMLPropertyDefaultString('Password',''))
        self.Add(XMLPropertyDefaultString('Ending','$'))
    def ApplyPreferences(self):
        from SignalIntegrity.Lib.Encryption import Encryption
        Encryption(pwd=self['Password'],ending=self['Ending'])

class ProjectFiles(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'ProjectFiles')
        self.Add(XMLPropertyDefaultBool('OpenLastFile',True))
        self.Add(XMLPropertyDefaultBool('RetainLastFilesOpened',True))
        self.Add(XMLProperty('LastFile',[LastFiles() for _ in range(4)],'array',arrayType=LastFiles()))
        self.Add(XMLPropertyDefaultBool('AskToSaveCurrentFile',True))
        self.Add(XMLPropertyDefaultBool('PreferSaveWaveformsLeCroyFormat',False))
        self.Add(XMLPropertyDefaultBool('ArchiveCachedResults',False))
        self.SubDir(Encryption())

class OnlineHelp(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'OnlineHelp')
        self.Add(XMLPropertyDefaultBool('UseOnlineHelp',True))
        self.Add(XMLPropertyDefaultString('URL','https://nubis-communications.github.io/SignalIntegrity/SignalIntegrity/App'))

class Features(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Features')
        self.Add(XMLPropertyDefaultBool('NetworkAnalyzerModel',False))
        self.Add(XMLPropertyDefaultBool('StatisticalNoise',False))
        self.Add(XMLPropertyDefaultBool('OpenProjectsReadOnly',True))

class StatisticalNoise(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'StatisticalNoise')
        # Values whose magnitude is below this threshold (rms/linear quantities)
        # are blanked in the statistical noise measurements table.
        self.Add(XMLPropertyDefaultFloat('ZeroThreshold',1e-15))
        # Signal-to-noise ratios above this value (in dB) are considered
        # unphysical (noise effectively zero) and are blanked in the table.
        self.Add(XMLPropertyDefaultFloat('MaximumSNR',150.0))

class PreferencesFile(ProjectFileBase):
    def __init__(self):
        ProjectFileBase.__init__(self)
        self.Add(XMLPropertyDefaultString('Version',None))
        self.SubDir(ProjectFiles())
        self.SubDir(Appearance())
        self.SubDir(Cache())
        self.SubDir(OnlineHelp())
        self.SubDir(Calculation())
        self.SubDir(SParameterProperties(preferences=True))
        self.SubDir(DeviceConfigurations())
        self.SubDir(Variables())
        self.SubDir(Features())
        self.SubDir(StatisticalNoise())
    def HandleBackwardsCompatibility(self):
        self['Devices.EyeDiagram'].HandleBackwardsCompatibility()
    def ApplyPreferences(self):
        self['Calculation'].ApplyPreferences()
        self['ProjectFiles.Encryption'].ApplyPreferences()
        self['Cache'].ApplyPreferences()

