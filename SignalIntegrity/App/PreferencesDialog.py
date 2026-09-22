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
import tkinter as tk
from tkinter import ttk
from SignalIntegrity.App.CalculationPropertiesProject import PropertiesDialog,CalculationProperty,CalculationPropertyTrueFalseButton,CalculationPropertyColor,CalculationPropertySI
from SignalIntegrity.App.BuildHelpSystem import HelpSystemKeys
from SignalIntegrity.Lib.Encryption import Encryption

class PreferencesDialog(PropertiesDialog):
    def __init__(self, parent,preferences):
        PropertiesDialog.__init__(self,parent,preferences,parent,'Preferences')
        style=ttk.Style()
        style.configure('TNotebook',borderwidth=2)
        style.configure('TNotebook.Tab',padding=[12,4])
        self.notebook=ttk.Notebook(self.propertyListFrame)
        self.notebook.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)
        # each tab body is a recessed panel so it reads as separate from the tab strip
        self.appearanceTab=tk.Frame(self.notebook,relief=tk.GROOVE,borderwidth=2)
        self.cachingTab=tk.Frame(self.notebook,relief=tk.GROOVE,borderwidth=2)
        self.archiveAndRegressionTab=tk.Frame(self.notebook,relief=tk.GROOVE,borderwidth=2)
        self.calculationTab=tk.Frame(self.notebook,relief=tk.GROOVE,borderwidth=2)
        self.notebook.add(self.appearanceTab,text='Appearance')
        self.notebook.add(self.calculationTab,text='Calculation')
        self.notebook.add(self.cachingTab,text='Caching')
        self.notebook.add(self.archiveAndRegressionTab,text='Archive and Regression')

        # Appearance
        self.fontSizeFrame=CalculationProperty(self.appearanceTab,'font size',None,self.onUpdatePreferences,preferences,'Appearance.FontSize')
        self.initialGridFrame=CalculationProperty(self.appearanceTab,'initial grid',None,self.onUpdatePreferences,preferences,'Appearance.InitialGrid')
        self.backgroundColorFrame=CalculationPropertyColor(self.appearanceTab,'background color',None,self.onUpdateColors,preferences,'Appearance.Color.Background')
        self.foregroundColorFrame=CalculationPropertyColor(self.appearanceTab,'foreground color',None,self.onUpdateColors,preferences,'Appearance.Color.Foreground')
        self.roundDisplayedValues=CalculationProperty(self.appearanceTab,'digits to round displayed values',None,self.onUpdatePreferences,preferences,'Appearance.RoundDisplayedValues')
        self.limitText=CalculationProperty(self.appearanceTab,'limit text in displayed values',None,self.onUpdatePreferences,preferences,'Appearance.LimitText')
        self.progressDialog=CalculationPropertyTrueFalseButton(self.appearanceTab,'detached progress bar',None,self.onUpdatePreferences,preferences,'Appearance.ProgressDialog')
        #self.activeBackgroundColorFrame=CalculationPropertyColor(self.appearanceTab,'active background color',None,self.onUpdateColors,preferences,'Appearance.Color.ActiveBackground')
        #self.activeForegroundColorFrame=CalculationPropertyColor(self.appearanceTab,'active foreground color',None,self.onUpdateColors,preferences,'Appearance.Color.ActiveForeground')
        self.showAllPinNumbers=CalculationPropertyTrueFalseButton(self.appearanceTab,'show all pin numbers',None,self.onUpdatePreferences,preferences,'Appearance.AllPinNumbersVisible')
        self.retainRecentFilesFrame=CalculationPropertyTrueFalseButton(self.appearanceTab,'retain recent project files',None,self.onUpdatePreferences,preferences,'ProjectFiles.RetainLastFilesOpened')
        self.openLastFileFrame=CalculationPropertyTrueFalseButton(self.appearanceTab,'open last file on start',None,self.onUpdatePreferences,preferences,'ProjectFiles.OpenLastFile')
        self.openProjectsReadOnlyFrame=CalculationPropertyTrueFalseButton(self.appearanceTab,'open projects read-only by default',None,self.onUpdatePreferences,preferences,'ProjectFiles.OpenProjectsReadOnly')
        self.askSaveCurrentFileFrame=CalculationPropertyTrueFalseButton(self.appearanceTab,'ask to save current file',None,self.onUpdatePreferences,preferences,'ProjectFiles.AskToSaveCurrentFile')
        self.preferLeCroyWaveform=CalculationPropertyTrueFalseButton(self.appearanceTab,'prefer saving waveforms in LeCroy format',None,self.onUpdatePreferences,preferences,'ProjectFiles.PreferSaveWaveformsLeCroyFormat')
        self.parameterizeVisible=CalculationPropertyTrueFalseButton(self.appearanceTab,'parameterize visible properties only',None,self.onUpdatePreferences,preferences,'Variables.ParameterizeOnlyVisible')
        self.OnlineHelpFrame=tk.Frame(self.appearanceTab, relief=tk.RIDGE, borderwidth=5)
        self.OnlineHelpFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.useOnlineHelp=CalculationPropertyTrueFalseButton(self.OnlineHelpFrame,'use online help',None,self.onUpdatePreferences,preferences,'OnlineHelp.UseOnlineHelp')
        self.onlineHelpURL=CalculationProperty(self.OnlineHelpFrame,'online help url',None,self.onUpdatePreferences,preferences,'OnlineHelp.URL')

        # Caching
        self.cacheResult=CalculationPropertyTrueFalseButton(self.cachingTab,'cache results',None,self.onUpdatePreferences,preferences,'Cache.CacheResults')
        self.cacheNumberOfFiles=CalculationProperty(self.cachingTab,'cache files per project',None,self.onUpdatePreferences,preferences,'Cache.NumberOfFiles')
        self.cacheKeepExtraFilesForArchive=CalculationPropertyTrueFalseButton(self.cachingTab,'keep extra cache file for archive',None,self.onUpdatePreferences,preferences,'Cache.KeepExtraFileForArchive')
        self.cacheLogging=CalculationPropertyTrueFalseButton(self.cachingTab,'log cache (for debugging)',None,self.onUpdatePreferences,preferences,'Cache.Logging')
        self.cacheCheckTimes=CalculationPropertyTrueFalseButton(self.cachingTab,'check cache file times',None,self.onUpdatePreferences,preferences,'Cache.CheckTimes')

        # Archive and Regression
        self.archiveCachedResults = CalculationPropertyTrueFalseButton(self.archiveAndRegressionTab,'archive cached results',None,self.onUpdatePreferences,preferences,'ProjectFiles.ArchiveCachedResults')
        self.archiveNonRelativeFiles = CalculationPropertyTrueFalseButton(self.archiveAndRegressionTab,'archive non-relative files',None,self.onUpdatePreferences,preferences,'ProjectFiles.ArchiveNonRelativeFiles')
        self.encryptionPassword = CalculationProperty(self.archiveAndRegressionTab,'password for encryption',None,self.onUpdatePassword,preferences,'ProjectFiles.Encryption.Password')
        self.encryptionEnding = CalculationProperty(self.archiveAndRegressionTab,'file ending for encryption',None,self.onUpdatePassword,preferences,'ProjectFiles.Encryption.Ending')
        self.regressionEnabled = CalculationPropertyTrueFalseButton(self.archiveAndRegressionTab,'enable regression tools',None,self.onUpdatePreferences,preferences,'Features.Regression')
        self.regressionOpenDiffTool = CalculationPropertyTrueFalseButton(self.archiveAndRegressionTab,'open meld on regression failure',None,self.onUpdatePreferences,preferences,'Regression.OpenDiffToolOnFailure')

        # Calculation (calculation properties dialog gating flags on top, core calculation flags below)
        self.calculationPropertiesFrame=tk.Frame(self.calculationTab, relief=tk.RIDGE, borderwidth=5)
        self.calculationPropertiesFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.enforce12458=CalculationPropertyTrueFalseButton(self.calculationPropertiesFrame,'enforce 12458 sequence in calculation properties',None,self.onUpdatePreferences,preferences,'Calculation.Enforce12458')
        self.logarithmicSolutions=CalculationPropertyTrueFalseButton(self.calculationPropertiesFrame,'enable logarithmically spaced frequencies solutions',None,self.onUpdatePreferences,preferences,'Calculation.LogarithmicSolutions')
        self.non50OhmReferenceImpedanceSolutions=CalculationPropertyTrueFalseButton(self.calculationPropertiesFrame,'enable non 50 ohm solutions',None,self.onUpdatePreferences,preferences,'Calculation.Non50OhmSolutions')
        self.allowParallelization=CalculationPropertyTrueFalseButton(self.calculationPropertiesFrame,'enable parallelization of calculations (experimental)',None,self.onUpdatePreferences,preferences,'Calculation.AllowParallelization')
        self.allowMaximumImpulseResponseLength=CalculationPropertyTrueFalseButton(self.calculationPropertiesFrame,'enable maximum impulse response length',None,self.onUpdatePreferences,preferences,'Calculation.AllowMaximumImpulseResponseLength')
        self.allowTimeBefore0=CalculationPropertyTrueFalseButton(self.calculationPropertiesFrame,'allow time before 0 in simulations (experimental)',None,self.onUpdatePreferences,preferences,'Calculation.AllowTimeBefore0')
        self.calculationFrame=tk.Frame(self.calculationTab, relief=tk.RIDGE, borderwidth=5)
        self.calculationFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.useSinX=CalculationPropertyTrueFalseButton(self.calculationFrame,'use SinX/X for resampling (otherwise linear)',None,self.onUpdatePreferences,preferences,'Calculation.UseSinX')
        self.trySVD=CalculationPropertyTrueFalseButton(self.calculationFrame,'try SVD in calculations (experimental)',None,self.onUpdatePreferences,preferences,'Calculation.TrySVD')
        self.allowNonUniqueSolutions=CalculationPropertyTrueFalseButton(self.calculationFrame,'allow non-unique solutions with SVD',None,self.onUpdatePreferences,preferences,'Calculation.AllowNonUniqueSolutions')
        self.checkConditionNumber=CalculationPropertyTrueFalseButton(self.calculationFrame,'check the condition number in calculations',None,self.onUpdatePreferences,preferences,'Calculation.CheckConditionNumber')
        self.multiPortTee=CalculationPropertyTrueFalseButton(self.calculationFrame,'employ multi-port tee elements',None,self.onUpdatePreferences,preferences,'Calculation.MultiPortTee')
        self.ignoreMissingOtherWaveforms=CalculationPropertyTrueFalseButton(self.calculationFrame,'ignore missing other waveforms in calculations',None,self.onUpdatePreferences,preferences,'Calculation.IgnoreMissingOtherWaveforms')
        self.maximumWaveformSize=CalculationPropertySI(self.calculationFrame,'maximum waveform size',None,self.onUpdatePreferences,preferences,'Calculation.MaximumWaveformSize','pts')


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