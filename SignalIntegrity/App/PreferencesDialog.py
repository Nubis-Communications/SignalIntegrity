"""
PreferencesDialog.py
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
from SignalIntegrity.App.CalculationPropertiesProject import PropertiesDialog,CalculationProperty,CalculationPropertyTrueFalseButton,CalculationPropertyColor,CalculationPropertySI
from SignalIntegrity.App.BuildHelpSystem import HelpSystemKeys

class PreferencesDialog(PropertiesDialog):
    def __init__(self, parent,preferences):
        PropertiesDialog.__init__(self,parent,preferences,parent,'Preferences')
        self.fontSizeFrame=CalculationProperty(self.propertyListFrame,'font size',None,self.onUpdatePreferences,preferences,'Appearance.FontSize')
        self.initialGridFrame=CalculationProperty(self.propertyListFrame,'initial grid',None,self.onUpdatePreferences,preferences,'Appearance.InitialGrid')
        self.backgroundColorFrame=CalculationPropertyColor(self.propertyListFrame,'background color',None,self.onUpdateColors,preferences,'Appearance.Color.Background')
        self.foregroundColorFrame=CalculationPropertyColor(self.propertyListFrame,'foreground color',None,self.onUpdateColors,preferences,'Appearance.Color.Foreground')
        #self.activeBackgroundColorFrame=CalculationPropertyColor(self.propertyListFrame,'active background color',None,self.onUpdateColors,preferences,'Appearance.Color.ActiveBackground')
        #self.activeForegroundColorFrame=CalculationPropertyColor(self.propertyListFrame,'active foreground color',None,self.onUpdateColors,preferences,'Appearance.Color.ActiveForeground')
        self.showAllPinNumbers=CalculationPropertyTrueFalseButton(self.propertyListFrame,'show all pin numbers',None,self.onUpdatePreferences,preferences,'Appearance.AllPinNumbersVisible')
        self.useSinX=CalculationPropertyTrueFalseButton(self.propertyListFrame,'use SinX/X for resampling (otherwise linear)',None,self.onUpdatePreferences,preferences,'Calculation.UseSinX')
        self.trySVD=CalculationPropertyTrueFalseButton(self.propertyListFrame,'try SVD in calculations (experimental)',None,self.onUpdatePreferences,preferences,'Calculation.TrySVD')
        self.enforce12458=CalculationPropertyTrueFalseButton(self.propertyListFrame,'enforce 12458 sequence in calculation properties',None,self.onUpdatePreferences,preferences,'Calculation.Enforce12458')
        self.maximumWaveformSize=CalculationPropertySI(self.propertyListFrame,'maximum waveform size',None,self.onUpdatePreferences,preferences,'Calculation.MaximumWaveformSize','pts')
        self.retainRecentFilesFrame=CalculationPropertyTrueFalseButton(self.propertyListFrame,'retain recent project files',None,self.onUpdatePreferences,preferences,'ProjectFiles.RetainLastFilesOpened')
        self.openLastFileFrame=CalculationPropertyTrueFalseButton(self.propertyListFrame,'open last file on start',None,self.onUpdatePreferences,preferences,'ProjectFiles.OpenLastFile')
        self.askSaveCurrentFileFrame=CalculationPropertyTrueFalseButton(self.propertyListFrame,'ask to save current file',None,self.onUpdatePreferences,preferences,'ProjectFiles.AskToSaveCurrentFile')
        self.preferLeCroyWaveform=CalculationPropertyTrueFalseButton(self.propertyListFrame,'prefer saving waveforms in LeCroy format',None,self.onUpdatePreferences,preferences,'ProjectFiles.PreferSaveWaveformsLeCroyFormat')
        self.cacheResult=CalculationPropertyTrueFalseButton(self.propertyListFrame,'cache results',None,self.onUpdatePreferences,preferences,'Cache.CacheResults')
        self.useOnlineHelp=CalculationPropertyTrueFalseButton(self.propertyListFrame,'use online help',None,self.onUpdatePreferences,preferences,'OnlineHelp.UseOnlineHelp')
        self.onlineHelpURL=CalculationProperty(self.propertyListFrame,'online help url',None,self.onUpdatePreferences,preferences,'OnlineHelp.URL')
        self.Finish()
    def onUpdatePreferences(self):
        self.onlineHelpURL.Show(self.project['OnlineHelp.UseOnlineHelp'])
        self.project.SaveToFile()
        HelpSystemKeys.InstallHelpURLBase(self.project['OnlineHelp.UseOnlineHelp'],
                                          self.project['OnlineHelp.URL'])
    def onUpdateColors(self):
        self.parent.UpdateColorsAndFonts()
        self.onUpdatePreferences()
    def Finish(self):
        self.onlineHelpURL.Show(self.project.GetValue('OnlineHelp.UseOnlineHelp'))
        PropertiesDialog.Finish(self)