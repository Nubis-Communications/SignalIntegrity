"""
EyeDiagramPropertiesDialog.py
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
import sys

if sys.version_info.major < 3:
    import Tkinter as tk
else:
    import tkinter as tk

import math

from SignalIntegrity.App.CalculationPropertiesProject import PropertiesDialog,CalculationPropertyTrueFalseButton,CalculationPropertyChoices,CalculationPropertySI,CalculationProperty,CalculationPropertyColor
import SignalIntegrity.App.Project

class EyeDiagramPropertiesDialog(PropertiesDialog):
    YAxisModeChoices={('Auto','Auto'),('Fixed','Fixed')}
    ModeChoices=[('ISI Only','ISI'),('Jitter & Noise','JitterNoise')]
    EnhancedPrecisionChoices=[('Auto','Auto'),('Fixed','Fixed'),('None','None')]
    def __init__(self,parent):
        PropertiesDialog.__init__(self,parent,SignalIntegrity.App.Project['EyeDiagram'],parent,'Eye Diagram Properties')
        self.pixelsX=int(self.project['UI']*self.project['Columns']*self.project['ScaleX']/100.)
        self.pixelsY=int(self.project['Rows']*self.project['ScaleY']/100.)
        self.EyeFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.EyeFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.AutoAlignFrame=tk.Frame(self.EyeFrame, relief=tk.RIDGE, borderwidth=5)
        self.AutoAlignFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.EnhancedPrecisionFrame=tk.Frame(self.EyeFrame, relief=tk.RIDGE, borderwidth=5)
        self.EnhancedPrecisionFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.YAxisFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.YAxisFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.JitterNoiseFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.JitterNoiseFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.AutoAlign=CalculationPropertyTrueFalseButton(self.AutoAlignFrame,'Auto Align Eye',self.onUpdateFromChanges,None,self.project,'Alignment.AutoAlign')
        self.BERExponent=CalculationProperty(self.AutoAlignFrame,'BER Exponent for Alignment',self.onUpdateFromChanges,None,self.project,'Alignment.BERForAlignment')
        self.BitsPerSymbol=CalculationProperty(self.AutoAlignFrame,'Bits per Symbol',self.onUpdateFromChanges,None,self.project,'Alignment.BitsPerSymbol')
        self.EnhancedPrecisionMode=CalculationPropertyChoices(self.EnhancedPrecisionFrame,'Enhanced Precision Mode',self.onUpdateFromChanges,None,self.EnhancedPrecisionChoices,self.project,'EnhancedPrecision.Mode')
        self.EnhancedPrecisionSteps=CalculationProperty(self.EnhancedPrecisionFrame,'Enhanced Precision Steps',self.onUpdateFromChanges,None,self.project,'EnhancedPrecision.FixedEnhancement')
        self.Color=CalculationPropertyColor(self.EyeFrame,'Color',self.onUpdateFromChanges,None,self.project,'Color')
        self.UIFrame=CalculationProperty(self.EyeFrame,'Number of UI',self.onUpdateUI,None,self.project,'UI')
        self.RowsFrame=CalculationProperty(self.EyeFrame,'Number of Rows',self.onUpdateRows,None,self.project,'Rows')
        self.ColsFrame=CalculationProperty(self.EyeFrame,'Number of Columns',self.onUpdateCols,None,self.project,'Columns')
        self.SaturationFrame=CalculationPropertySI(self.EyeFrame,'Saturation',self.onUpdateFromChanges,None,self.project,'Saturation','%')
        self.ScaleXFrame=CalculationPropertySI(self.EyeFrame,'Scale X',self.onUpdateScaleX,None,self.project,'ScaleX','%')
        self.ScaleYFrame=CalculationPropertySI(self.EyeFrame,'Scale Y',self.onUpdateScaleY,None,self.project,'ScaleY','%')
        self.YAxisModeFrame=CalculationPropertyChoices(self.YAxisFrame,'Y Axis',self.onUpdateFromChanges,None,self.YAxisModeChoices,self.project,'YAxis.Mode')
        self.MaxYFrame=CalculationPropertySI(self.YAxisFrame,'Maximum Y',self.onUpdateFromChanges,None,self.project,'YAxis.Max','V')
        self.MinYFrame=CalculationPropertySI(self.YAxisFrame,'Minimum Y',self.onUpdateFromChanges,None,self.project,'YAxis.Min','V')
        self.Mode=CalculationPropertyChoices(self.JitterNoiseFrame,'Eye Mode',self.onUpdateFromChanges,None,self.ModeChoices,self.project,'Mode')
        self.JitterSeconds=CalculationPropertySI(self.JitterNoiseFrame,'Random Jitter (s)',self.onUpdateFromChanges,None,self.project,'JitterNoise.JitterS','s')
        self.JitterDeterministicPkS=CalculationPropertySI(self.JitterNoiseFrame,'Deterministic Jitter (s, pk)',self.onUpdateFromChanges,None,self.project,'JitterNoise.JitterDeterministicPkS','s')
        self.Noise=CalculationPropertySI(self.JitterNoiseFrame,'Noise',self.onUpdateFromChanges,None,self.project,'JitterNoise.Noise','V')
        self.MaxWindowWidthHeightPixels=CalculationPropertySI(self.JitterNoiseFrame,'Max Kernel Pixels',self.onUpdateFromChanges,None,self.project,'JitterNoise.MaxKernelPixels','pixels')
        self.Invert=CalculationPropertyTrueFalseButton(self.EyeFrame,'Invert Plot',self.onUpdateFromChanges,None,self.project,'Invert')
        self.LogIntensityFrame=tk.Frame(self.JitterNoiseFrame)
        self.LogIntensityFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.LogIntensity=CalculationPropertyTrueFalseButton(self.LogIntensityFrame,'Log Intensity',self.onUpdateFromChanges,None,self.project,'JitterNoise.LogIntensity.LogIntensity')
        self.MinExponent=CalculationProperty(self.LogIntensityFrame,'Min Exponent',self.onUpdateFromChanges,None,self.project,'JitterNoise.LogIntensity.MinExponent')
        self.MaxExponent=CalculationProperty(self.LogIntensityFrame,'Max Exponent',self.onUpdateFromChanges,None,self.project,'JitterNoise.LogIntensity.MaxExponent')
        self.SaveToPreferencesFrame=tk.Frame(self.propertyListFrame,relief=tk.RIDGE, borderwidth=5)
        self.SaveToPreferencesFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.SaveToPreferencesButton = tk.Button(self.SaveToPreferencesFrame,text='Save Properties to Global Preferences',command=self.onSaveToPreferences,width=CalculationProperty.entryWidth)
        self.SaveToPreferencesButton.pack(side=tk.TOP,expand=tk.YES,anchor=tk.E)
        self.Finish()
    def Finish(self):
        self.UpdateStrings()
        PropertiesDialog.Finish(self)
    def onUpdateUI(self,_):
        self.project['ScaleX']=self.pixelsX/(self.project['UI']*self.project['Columns'])*100.
        self.UpdateStrings()
    def onUpdateRows(self,_):
        self.project['ScaleY']=self.pixelsY/self.project['Rows']*100.
        self.UpdateStrings()
    def onUpdateCols(self,_):
        self.project['ScaleX']=self.pixelsX/(self.project['UI']*self.project['Columns'])*100.
        self.UpdateStrings()
    def onUpdateScaleX(self,_):
        self.pixelsX=int(self.project['UI']*self.project['Columns']*self.project['ScaleX']/100.)
        self.UpdateStrings()
    def onUpdateScaleY(self,_):
        self.pixelsY=int(self.project['Rows']*self.project['ScaleY']/100.)
        self.UpdateStrings()
    def onUpdateFromChanges(self,_):
        self.UpdateStrings()
    def UpdateStrings(self):
        showEye=True
        autoAlign=self.project['Alignment.AutoAlign']
        auto=(self.project['YAxis.Mode']=='Auto' and showEye)
        showEnhancedPrecisionSteps = (self.project['EnhancedPrecision.Mode'] == 'Fixed')
        self.BERExponent.Show(autoAlign)
        self.BitsPerSymbol.Show(autoAlign)
        self.EnhancedPrecisionSteps.Show(showEnhancedPrecisionSteps)
        self.MaxYFrame.Show(not auto and showEye)
        self.MinYFrame.Show(not auto and showEye)
        self.UIFrame.Show(showEye)
        self.RowsFrame.Show(showEye)
        self.ColsFrame.Show(showEye)
        self.SaturationFrame.Show(showEye)
        self.ScaleXFrame.Show(showEye)
        self.ScaleYFrame.Show(showEye)
        self.YAxisModeFrame.Show(showEye)
        self.UIFrame.UpdateStrings()
        self.RowsFrame.UpdateStrings()
        self.ColsFrame.UpdateStrings()
        self.SaturationFrame.UpdateStrings()
        self.ScaleXFrame.UpdateStrings()
        self.ScaleYFrame.UpdateStrings()
        jitterNoiseMode=(self.project['Mode'] == 'JitterNoise')
        self.LogIntensityFrame.pack_forget()
        self.JitterSeconds.Show(jitterNoiseMode)
        self.JitterDeterministicPkS.Show(jitterNoiseMode)
        self.Noise.Show(jitterNoiseMode)
        self.MaxWindowWidthHeightPixels.Show(jitterNoiseMode)
        self.LogIntensity.Show(jitterNoiseMode)
        self.LogIntensityFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        logIntensity=self.project['JitterNoise.LogIntensity.LogIntensity']
        self.MinExponent.Show(jitterNoiseMode and logIntensity)
        self.MaxExponent.Show(jitterNoiseMode and logIntensity)
    def onSaveToPreferences(self):
        import SignalIntegrity.App.Preferences
        import copy
        SignalIntegrity.App.Preferences.dict['EyeDiagram']=copy.deepcopy(self.project['EyeDiagram'])
        SignalIntegrity.App.Preferences.SaveToFile()
