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

class EyeDiagramPropertiesDialog(PropertiesDialog):
    YAxisModeChoices={('Auto','Auto'),('Fixed','Fixed')}
    ModeChoices=[('ISI Only','ISI'),('Jitter & Noise','JitterNoise')]
    def __init__(self,parent,project):
        PropertiesDialog.__init__(self,parent,project,parent.parent,'Eye Diagram Properties')
        self.pixelsX=int(self.project['EyeDiagram.UI']*self.project['EyeDiagram.Columns']*self.project['EyeDiagram.ScaleX']/100.)
        self.pixelsY=int(self.project['EyeDiagram.Rows']*self.project['EyeDiagram.ScaleY']/100.)
        self.EyeFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.EyeFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.YAxisFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.YAxisFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.JitterNoiseFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.JitterNoiseFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.Color=CalculationPropertyColor(self.EyeFrame,'Color',self.onUpdateColor,None,project,'EyeDiagram.Color')
        self.UIFrame=CalculationProperty(self.EyeFrame,'Number of UI',self.onUpdateUI,None,project,'EyeDiagram.UI')
        self.RowsFrame=CalculationProperty(self.EyeFrame,'Number of Rows',self.onUpdateRows,None,project,'EyeDiagram.Rows')
        self.ColsFrame=CalculationProperty(self.EyeFrame,'Number of Columns',self.onUpdateCols,None,project,'EyeDiagram.Columns')
        self.SaturationFrame=CalculationPropertySI(self.EyeFrame,'Saturation',self.onUpdateSaturation,None,project,'EyeDiagram.Saturation','%')
        self.ScaleXFrame=CalculationPropertySI(self.EyeFrame,'Scale X',self.onUpdateScaleX,None,project,'EyeDiagram.ScaleX','%')
        self.ScaleYFrame=CalculationPropertySI(self.EyeFrame,'Scale Y',self.onUpdateScaleY,None,project,'EyeDiagram.ScaleY','%')
        self.YAxisModeFrame=CalculationPropertyChoices(self.YAxisFrame,'Y Axis',self.onUpdateYAxisMode,None,self.YAxisModeChoices,project,'EyeDiagram.YAxis.Mode')
        self.MaxYFrame=CalculationPropertySI(self.YAxisFrame,'Maximum Y',self.onUpdateSaturation,None,project,'EyeDiagram.YAxis.Max','V')
        self.MinYFrame=CalculationPropertySI(self.YAxisFrame,'Minimum Y',self.onUpdateSaturation,None,project,'EyeDiagram.YAxis.Min','V')
        self.Mode=CalculationPropertyChoices(self.JitterNoiseFrame,'Eye Mode',None,self.onUpdateCalculate,self.ModeChoices,project,'EyeDiagram.Mode')
        self.JitterSeconds=CalculationPropertySI(self.JitterNoiseFrame,'Random Jitter (s)',self.onUpdateJitterSeconds,None,project,'EyeDiagram.JitterNoise.JitterS','s')
        self.JitterDeterministicPkS=CalculationPropertySI(self.JitterNoiseFrame,'Deterministic Jitter (s, pk)',self.onUpdateDeterministicJitterSeconds,None,project,'EyeDiagram.JitterNoise.JitterDeterministicPkS','s')
        self.Noise=CalculationPropertySI(self.JitterNoiseFrame,'Noise',self.onUpdateNoise,None,project,'EyeDiagram.JitterNoise.Noise','V')
        self.MaxWindowWidthHeightPixels=CalculationPropertySI(self.JitterNoiseFrame,'Max Kernel Pixels',self.onUpdateMaxWindowWidthHeightPixels,None,project,'EyeDiagram.JitterNoise.MaxKernelPixels','pixels')
        self.Invert=CalculationPropertyTrueFalseButton(self.EyeFrame,'Invert Plot',self.onUpdateInvert,None,project,'EyeDiagram.Invert')
        self.LogIntensityFrame=tk.Frame(self.JitterNoiseFrame)
        self.LogIntensityFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.LogIntensity=CalculationPropertyTrueFalseButton(self.LogIntensityFrame,'Log Intensity',self.onUpdateLogIntensity,None,project,'EyeDiagram.JitterNoise.LogIntensity.LogIntensity')
        self.MinExponent=CalculationProperty(self.LogIntensityFrame,'Min Exponent',self.onUpdateMinExponent,None,project,'EyeDiagram.JitterNoise.LogIntensity.MinExponent')
        self.MaxExponent=CalculationProperty(self.LogIntensityFrame,'Max Exponent',self.onUpdateMaxExponent,None,project,'EyeDiagram.JitterNoise.LogIntensity.MaxExponent')
        self.SaveToPreferencesFrame=tk.Frame(self.propertyListFrame,relief=tk.RIDGE, borderwidth=5)
        self.SaveToPreferencesFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.SaveToPreferencesButton = tk.Button(self.SaveToPreferencesFrame,text='Save Properties to Global Preferences',command=self.onSaveToPreferences,width=CalculationProperty.entryWidth)
        self.SaveToPreferencesButton.pack(side=tk.TOP,expand=tk.YES,anchor=tk.E)
        self.Finish()
    def Finish(self):
        self.UpdateStrings(calculate=False)
        PropertiesDialog.Finish(self)
    def onUpdateCalculate(self):
        self.UpdateStrings()
    def onUpdateColor(self,_):
        self.UpdateStrings()
    def onUpdateUI(self,_):
        self.project['EyeDiagram.ScaleX']=self.pixelsX/(self.project['EyeDiagram.UI']*self.project['EyeDiagram.Columns'])*100.
        self.UpdateStrings()
    def onUpdateRows(self,_):
        self.project['EyeDiagram.ScaleY']=self.pixelsY/self.project['EyeDiagram.Rows']*100.
        self.UpdateStrings()
    def onUpdateCols(self,_):
        self.project['EyeDiagram.ScaleX']=self.pixelsX/(self.project['EyeDiagram.UI']*self.project['EyeDiagram.Columns'])*100.
        self.UpdateStrings()
    def onUpdateScaleX(self,_):
        self.pixelsX=int(self.project['EyeDiagram.UI']*self.project['EyeDiagram.Columns']*self.project['EyeDiagram.ScaleX']/100.)
        self.UpdateStrings()
    def onUpdateScaleY(self,_):
        self.pixelsY=int(self.project['EyeDiagram.Rows']*self.project['EyeDiagram.ScaleY']/100.)
        self.UpdateStrings()
    def onUpdateSaturation(self,_):
        self.UpdateStrings()
    def onUpdateYAxisMode(self,_):
        self.UpdateStrings()
    def onUpdateMaxY(self,_):
        self.UpdateStrings()
    def onUpdateMinY(self,_):
        self.UpdateStrings()
    def UpdateStrings(self,calculate=True):
        showEye=True
        auto=(self.project['EyeDiagram.YAxis.Mode']=='Auto' and showEye)
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
        jitterNoiseMode=(self.project['EyeDiagram.Mode'] == 'JitterNoise')
        self.LogIntensityFrame.pack_forget()
        self.JitterSeconds.Show(jitterNoiseMode)
        self.JitterDeterministicPkS.Show(jitterNoiseMode)
        self.Noise.Show(jitterNoiseMode)
        self.MaxWindowWidthHeightPixels.Show(jitterNoiseMode)
        self.LogIntensity.Show(jitterNoiseMode)
        self.LogIntensityFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        logIntensity=self.project['EyeDiagram.JitterNoise.LogIntensity.LogIntensity']
        self.MinExponent.Show(jitterNoiseMode and logIntensity)
        self.MaxExponent.Show(jitterNoiseMode and logIntensity)
    def onUpdateJitterSeconds(self,_):
        self.UpdateStrings()
    def onUpdateDeterministicJitterSeconds(self,_):
        self.UpdateStrings()
    def onUpdateNoise(self,_):
        self.UpdateStrings()
    def onUpdateMaxWindowWidthHeightPixels(self,_):
        self.UpdateStrings()
    def onUpdateMinExponent(self,_):
        self.UpdateStrings()
    def onUpdateMaxExponent(self,_):
        self.UpdateStrings()
    def onUpdateInvert(self,_):
        self.UpdateStrings()
    def onUpdateLogIntensity(self,_):
        self.UpdateStrings()
    def onSaveToPreferences(self):
        import SignalIntegrity.App.Preferences
        import copy
        SignalIntegrity.App.Preferences.dict['EyeDiagram']=copy.deepcopy(self.project['EyeDiagram'])
        SignalIntegrity.App.Preferences.SaveToFile()
