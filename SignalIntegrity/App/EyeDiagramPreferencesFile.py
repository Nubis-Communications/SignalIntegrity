"""
EyeDiagramPreferencesFile.py
"""
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# Copyright (c) 2021-2025 Nubis Communications, Inc.
# Copyright (c) 2026 Ciena, Inc.
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

class EyeYAxisConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('YAxis')
        self.Add(XMLPropertyDefaultString('Mode','Auto'))
        self.Add(XMLPropertyDefaultFloat('Max',1.0))
        self.Add(XMLPropertyDefaultFloat('Min',0.0))

class EyeLogIntensityConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('LogIntensity')
        self.Add(XMLPropertyDefaultBool('LogIntensity',False))
        self.Add(XMLPropertyDefaultFloat('MinExponent',-12))
        self.Add(XMLPropertyDefaultFloat('MaxExponent',0))

class EyeJitterNoiseConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('JitterNoise')
        self.Add(XMLPropertyDefaultFloat('JitterS',0))
        self.Add(XMLPropertyDefaultFloat('JitterDeterministicPkS',0))
        self.Add(XMLPropertyDefaultFloat('Noise',0.0)) # this is actually fixed, inherent noise -- left this name for backward compatibility
        self.Add(XMLPropertyDefaultFloat('ExternalNoise',0.0,write=False))
        self.Add(XMLPropertyDefaultFloat('TotalNoise',0.0,write=False))
        self.Add(XMLPropertyDefaultInt('MaxKernelPixels',100000))
        self.SubDir(EyeLogIntensityConfiguration())

class EyeAlignmentConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('Alignment')
        self.Add(XMLPropertyDefaultBool('AutoAlign',False))
        self.Add(XMLPropertyDefaultFloat('BERForAlignment',-3))
        self.Add(XMLPropertyDefaultInt('BitsPerSymbol',None,write=False))
        self.Add(XMLPropertyDefaultInt('Levels',2))
        self.Add(XMLPropertyDefaultString('Mode','Horizontal')) # 'Horizontal' or 'Vertical'
        self.Add(XMLPropertyDefaultString('Horizontal','Middle')) # 'Middle' or 'Max' (vertical eye)
        self.Add(XMLPropertyDefaultString('Vertical','MaxMin')) # 'MaxMin' (maximum minimum opening) or 'Max' (maximum opening) 
    def HandleBackwardsCompatibility(self):
        if self['BitsPerSymbol'] != None:
            self['Levels'] = 2**self['BitsPerSymbol']

class BathtubConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('Bathtub')
        self.Add(XMLPropertyDefaultBool('Measure',False))
        self.Add(XMLPropertyDefaultFloat('DecadesFromJoinForFit',0.5))
        self.Add(XMLPropertyDefaultInt('MinPointsForFit',6))

class DecisionConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('Decision')
        self.Add(XMLPropertyDefaultString('Mode','Mid')) # 'Mid' or 'Best' for independent decision levels

class EyeEnhancedPrecisionConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('EnhancedPrecision')
        self.Add(XMLPropertyDefaultString('Mode','Auto'))
        self.Add(XMLPropertyDefaultInt('FixedEnhancement',10))

class EyeMeasureConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('Measure')
        self.Add(XMLPropertyDefaultBool('Measure',False))
        self.Add(XMLPropertyDefaultString('WaveformType','V')) # 'V', 'A', 'W', 'FW', 'AW', 'VW'
        self.Add(XMLPropertyDefaultString('RxTx','Rx')) # 'Rx', 'Tx', 'N/A'
        self.Add(XMLPropertyDefaultBool('TxInputPowerAvailable',False))
        self.Add(XMLPropertyDefaultFloat('TxInputPowerW',0))
        self.Add(XMLPropertyDefaultFloat('TxInputPowerdBm',0,write=False))
        self.Add(XMLPropertyDefaultFloat('BERForMeasure',-6))

class EyeContourConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('Contours')
        self.Add(XMLPropertyDefaultBool('Show',False))
        self.Add(XMLPropertyDefaultString('Which','Eye')) # 'Eye' or 'All'

class EyeAnnotationConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('Annotation')
        self.Add(XMLPropertyDefaultBool('Annotate',False))
        self.Add(XMLPropertyDefaultString('Color','#ffffff'))
        self.Add(XMLPropertyDefaultBool('MeanLevels',True))
        self.Add(XMLPropertyDefaultBool('LabelMeanLevels',False))
        self.Add(XMLPropertyDefaultBool('LevelExtents',False))
        self.Add(XMLPropertyDefaultBool('EyeWidth',True))
        self.Add(XMLPropertyDefaultBool('EyeHeight',True))
        self.SubDir(EyeContourConfiguration())

class ClockRecoveryConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('ClockRecovery')
        self.Add(XMLPropertyDefaultBool('Recover',False))
        self.Add(XMLPropertyDefaultInt('TrimLeftRight',20))

class EyeConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('EyeDiagram')
        self.Add(XMLPropertyDefaultString('Color','#ffffff'))
        self.Add(XMLPropertyDefaultInt('UI',3))
        self.Add(XMLPropertyDefaultInt('Rows',200))
        self.Add(XMLPropertyDefaultInt('Columns',200))
        self.Add(XMLPropertyDefaultFloat('Saturation',20))
        self.Add(XMLPropertyDefaultFloat('ScaleX',75.))
        self.Add(XMLPropertyDefaultFloat('ScaleY',150.))
        self.Add(XMLPropertyDefaultString('Mode','ISI'))
        self.Add(XMLPropertyDefaultBool('Invert',True))
        self.SubDir(ClockRecoveryConfiguration())
        self.SubDir(EyeYAxisConfiguration())
        self.SubDir(EyeJitterNoiseConfiguration())
        self.SubDir(EyeAlignmentConfiguration())
        self.SubDir(EyeEnhancedPrecisionConfiguration())
        self.SubDir(EyeMeasureConfiguration())
        self.SubDir(EyeAnnotationConfiguration())
        self.SubDir(DecisionConfiguration())
        self.SubDir(BathtubConfiguration())
    def HandleBackwardsCompatibility(self):
        self['Alignment'].HandleBackwardsCompatibility()
