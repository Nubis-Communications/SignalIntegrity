"""
PreferencesDialog.py
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
from SignalIntegrity.App.CalculationPropertiesProject import PropertiesDialog,CalculationProperty,CalculationPropertyTrueFalseButton,CalculationPropertyColor,CalculationPropertySI
from SignalIntegrity.App.BuildHelpSystem import HelpSystemKeys
from SignalIntegrity.Lib.Encryption import Encryption

class PreferencesDialog(PropertiesDialog):
    def __init__(self, parent,preferences):
        PropertiesDialog.__init__(self,parent,preferences,parent,'Preferences')
        self.fontSizeFrame=CalculationProperty(self.propertyListFrame,'font size',None,self.onUpdatePreferences,preferences,'Appearance.FontSize')
        self.initialGridFrame=CalculationProperty(self.propertyListFrame,'initial grid',None,self.onUpdatePreferences,preferences,'Appearance.InitialGrid')
        self.backgroundColorFrame=CalculationPropertyColor(self.propertyListFrame,'background color',None,self.onUpdateColors,preferences,'Appearance.Color.Background')
        self.foregroundColorFrame=CalculationPropertyColor(self.propertyListFrame,'foreground color',None,self.onUpdateColors,preferences,'Appearance.Color.Foreground')
        self.roundDisplayedValues=CalculationProperty(self.propertyListFrame,'digits to round displayed values',None,self.onUpdatePreferences,preferences,'Appearance.RoundDisplayedValues')
        self.limitText=CalculationProperty(self.propertyListFrame,'limit text in displayed values',None,self.onUpdatePreferences,preferences,'Appearance.LimitText')
        #self.activeBackgroundColorFrame=CalculationPropertyColor(self.propertyListFrame,'active background color',None,self.onUpdateColors,preferences,'Appearance.Color.ActiveBackground')
        #self.activeForegroundColorFrame=CalculationPropertyColor(self.propertyListFrame,'active foreground color',None,self.onUpdateColors,preferences,'Appearance.Color.ActiveForeground')
        self.showAllPinNumbers=CalculationPropertyTrueFalseButton(self.propertyListFrame,'show all pin numbers',None,self.onUpdatePreferences,preferences,'Appearance.AllPinNumbersVisible')
        self.useSinX=CalculationPropertyTrueFalseButton(self.propertyListFrame,'use SinX/X for resampling (otherwise linear)',None,self.onUpdatePreferences,preferences,'Calculation.UseSinX')
        self.trySVD=CalculationPropertyTrueFalseButton(self.propertyListFrame,'try SVD in calculations (experimental)',None,self.onUpdatePreferences,preferences,'Calculation.TrySVD')
        self.allowNonUniqueSolutions=CalculationPropertyTrueFalseButton(self.propertyListFrame,'allow non-unique solutions with SVD',None,self.onUpdatePreferences,preferences,'Calculation.AllowNonUniqueSolutions')
        self.checkConditionNumber=CalculationPropertyTrueFalseButton(self.propertyListFrame,'check the condition number in calculations',None,self.onUpdatePreferences,preferences,'Calculation.CheckConditionNumber')
        self.multiPortTee=CalculationPropertyTrueFalseButton(self.propertyListFrame,'employ multi-port tee elements',None,self.onUpdatePreferences,preferences,'Calculation.MultiPortTee')
        self.enforce12458=CalculationPropertyTrueFalseButton(self.propertyListFrame,'enforce 12458 sequence in calculation properties',None,self.onUpdatePreferences,preferences,'Calculation.Enforce12458')
        self.logarithmicSolutions=CalculationPropertyTrueFalseButton(self.propertyListFrame,'enable logarithmically spaced frequencies solutions',None,self.onUpdatePreferences,preferences,'Calculation.LogarithmicSolutions')
        self.non50OhmReferenceImpedanceSolutions=CalculationPropertyTrueFalseButton(self.propertyListFrame,'enable non 50 ohm solutions',None,self.onUpdatePreferences,preferences,'Calculation.Non50OhmSolutions')
        self.ignoreMissingOtherWaveforms=CalculationPropertyTrueFalseButton(self.propertyListFrame,'ignore missing other waveforms in calculations',None,self.onUpdatePreferences,preferences,'Calculation.IgnoreMissingOtherWaveforms')
        self.maximumWaveformSize=CalculationPropertySI(self.propertyListFrame,'maximum waveform size',None,self.onUpdatePreferences,preferences,'Calculation.MaximumWaveformSize','pts')
        self.allowTimeBefore0=CalculationPropertyTrueFalseButton(self.propertyListFrame,'allow time before 0 in simulations',None,self.onUpdatePreferences,preferences,'Calculation.AllowTimeBefore0')
        self.retainRecentFilesFrame=CalculationPropertyTrueFalseButton(self.propertyListFrame,'retain recent project files',None,self.onUpdatePreferences,preferences,'ProjectFiles.RetainLastFilesOpened')
        self.openLastFileFrame=CalculationPropertyTrueFalseButton(self.propertyListFrame,'open last file on start',None,self.onUpdatePreferences,preferences,'ProjectFiles.OpenLastFile')
        self.askSaveCurrentFileFrame=CalculationPropertyTrueFalseButton(self.propertyListFrame,'ask to save current file',None,self.onUpdatePreferences,preferences,'ProjectFiles.AskToSaveCurrentFile')
        self.preferLeCroyWaveform=CalculationPropertyTrueFalseButton(self.propertyListFrame,'prefer saving waveforms in LeCroy format',None,self.onUpdatePreferences,preferences,'ProjectFiles.PreferSaveWaveformsLeCroyFormat')
        import tkinter as tk
        self.CacheFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.CacheFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.cacheResult=CalculationPropertyTrueFalseButton(self.CacheFrame,'cache results',None,self.onUpdatePreferences,preferences,'Cache.CacheResults')
        self.cacheNumberOfFiles=CalculationProperty(self.CacheFrame,'cache files per project',None,self.onUpdatePreferences,preferences,'Cache.NumberOfFiles')
        self.cacheKeepExtraFilesForArchive=CalculationPropertyTrueFalseButton(self.CacheFrame,'keep extra cache file for archive',None,self.onUpdatePreferences,preferences,'Cache.KeepExtraFileForArchive')
        self.cacheLogging=CalculationPropertyTrueFalseButton(self.CacheFrame,'log cache (for debugging)',None,self.onUpdatePreferences,preferences,'Cache.Logging')
        self.cacheCheckTimes=CalculationPropertyTrueFalseButton(self.CacheFrame,'check cache file times',None,self.onUpdatePreferences,preferences,'Cache.CheckTimes')
        self.parameterizeVisible=CalculationPropertyTrueFalseButton(self.propertyListFrame,'parameterize visible properties only',None,self.onUpdatePreferences,preferences,'Variables.ParameterizeOnlyVisible')
        self.encryptionPassword = CalculationProperty(self.propertyListFrame,'password for encryption',None,self.onUpdatePassword,preferences,'ProjectFiles.Encryption.Password')
        self.encryptionEnding = CalculationProperty(self.propertyListFrame,'file ending for encryption',None,self.onUpdatePassword,preferences,'ProjectFiles.Encryption.Ending')
        self.archiveCachedResults = CalculationPropertyTrueFalseButton(self.propertyListFrame,'archive cached results',None,self.onUpdatePreferences,preferences,'ProjectFiles.ArchiveCachedResults')
        self.OnlineHelpFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.OnlineHelpFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.useOnlineHelp=CalculationPropertyTrueFalseButton(self.OnlineHelpFrame,'use online help',None,self.onUpdatePreferences,preferences,'OnlineHelp.UseOnlineHelp')
        self.onlineHelpURL=CalculationProperty(self.OnlineHelpFrame,'online help url',None,self.onUpdatePreferences,preferences,'OnlineHelp.URL')
        self.Finish()

    def onUpdatePreferences(self):
        self.onlineHelpURL.Show(self.project['OnlineHelp.UseOnlineHelp'])
        self.cacheNumberOfFiles.Show(self.project['Cache.CacheResults'])
        self.cacheKeepExtraFilesForArchive.Show(self.project['Cache.CacheResults'] and (self.project['Cache.NumberOfFiles'] > 1))
        self.project.SaveToFile()
        HelpSystemKeys.InstallHelpURLBase(self.project['OnlineHelp.UseOnlineHelp'],
                                          self.project['OnlineHelp.URL'])
    def onUpdateColors(self):
        self.parent.UpdateColorsAndFonts()
        self.onUpdatePreferences()

    def onUpdatePassword(self):
        pwd = self.project['ProjectFiles.Encryption.Password']
        if pwd in ['','None',None]:
            pwd = None
        ending = self.project['ProjectFiles.Encryption.Ending']
        if ending in ['','None',None]:
            ending = '$'
            self.project['ProjectFiles.Encryption.Ending'] = ending
        Encryption(pwd=pwd,ending=ending)
        self.onUpdatePreferences()

    def Finish(self):
        self.onlineHelpURL.Show(self.project.GetValue('OnlineHelp.UseOnlineHelp'))
        self.cacheNumberOfFiles.Show(self.project['Cache.CacheResults'])
        self.cacheKeepExtraFilesForArchive.Show(self.project['Cache.CacheResults'] and (self.project['Cache.NumberOfFiles'] > 1))
        PropertiesDialog.Finish(self)