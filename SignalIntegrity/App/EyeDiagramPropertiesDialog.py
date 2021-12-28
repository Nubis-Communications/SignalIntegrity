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
    AlignmentModeChoices=[('Horizontal','Horizontal'),('Vertical','Vertical')]
    VerticalAlignmentModeChoices=[('Max of Smallest Eye','MaxMin'),('Maximum Eye','Max')]
    HorizontalAlignmentModeChoices=[('MidPoint of Middle Eye','Middle'),('Midpoint of Widest Eye','Max')]
    ContourChoices=[('All Contours','All'),('Only Contours inside Eye','Eye')]
    DecisionChoices=[('Midpoint of Eye','Mid'),('Best Decision Point','Best')]
    def __init__(self,project,parent):
        PropertiesDialog.__init__(self,parent,project,parent.parent,'Eye Diagram Properties')
        self.transient(parent)
        self.pixelsX=int(self.project['UI']*self.project['Columns']*self.project['ScaleX']/100.)
        self.pixelsY=int(self.project['Rows']*self.project['ScaleY']/100.)
        self.LeftFrame=tk.Frame(self.propertyListFrame)
        self.LeftFrame.pack(side=tk.LEFT,fill=tk.X,expand=tk.NO,anchor=tk.NW)
        self.RightFrame=tk.Frame(self.propertyListFrame)
        self.RightFrame.pack(side=tk.LEFT,fill=tk.X,expand=tk.NO,anchor=tk.NW)
        self.GeneralFrame=tk.Frame(self.LeftFrame, relief=tk.RIDGE, borderwidth=5)
        self.GeneralFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.EnhancedPrecisionFrame=tk.Frame(self.LeftFrame, relief=tk.RIDGE, borderwidth=5)
        self.EnhancedPrecisionFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.YAxisFrame=tk.Frame(self.LeftFrame, relief=tk.RIDGE, borderwidth=5)
        self.YAxisFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.JitterNoiseFrame=tk.Frame(self.LeftFrame, relief=tk.RIDGE, borderwidth=5)
        self.JitterNoiseFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.LogIntensityFrame=tk.Frame(self.LeftFrame, relief=tk.RIDGE, borderwidth=5)
        self.LogIntensityFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.AutoAlignFrame=tk.Frame(self.RightFrame, relief=tk.RIDGE, borderwidth=5)
        self.AutoAlignFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.MeasurementsFrame=tk.Frame(self.RightFrame, relief=tk.RIDGE, borderwidth=5)
        self.MeasurementsFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.BitsPerSymbol=CalculationProperty(self.GeneralFrame,'Bits per Symbol',self.onUpdateFromChanges,None,self.project,'Alignment.BitsPerSymbol',tooltip='The number of bits transmitted per symbol\n1=NRZ, or PAM-2, 2=PAM-4, 3=PAM-8')
        self.Color=CalculationPropertyColor(self.GeneralFrame,'Color',self.onUpdateFromChanges,None,self.project,'Color',tooltip='The color of the eye in the eye diagram if Invert is True,\notherwise is the background color')
        self.UIFrame=CalculationProperty(self.GeneralFrame,'Number of UI',self.onUpdateUI,None,self.project,'UI',tooltip='The number of unit intervals that will be shown in the eye diagram plot generated')
        self.RowsFrame=CalculationProperty(self.GeneralFrame,'Number of Rows',self.onUpdateRows,None,self.project,'Rows',tooltip='The number of pixels vertically in the raw eye diagram.\nThis is scaled by the factor in \'Scale X\'')
        self.ColsFrame=CalculationProperty(self.GeneralFrame,'Number of Columns',self.onUpdateCols,None,self.project,'Columns',tooltip='The number of pixels horixontally in one UI in the raw eye diagram.\nThis is scaled by the factor in \'Scale Y\'')
        self.SaturationFrame=CalculationPropertySI(self.GeneralFrame,'Saturation',self.onUpdateFromChanges,None,self.project,'Saturation','%')
        self.ScaleXFrame=CalculationPropertySI(self.GeneralFrame,'Scale X',self.onUpdateScaleX,None,self.project,'ScaleX','%')
        self.ScaleYFrame=CalculationPropertySI(self.GeneralFrame,'Scale Y',self.onUpdateScaleY,None,self.project,'ScaleY','%')
        self.AutoAlign=CalculationPropertyTrueFalseButton(self.AutoAlignFrame,'Auto Align Eye',self.onUpdateFromChanges,None,self.project,'Alignment.AutoAlign')
        self.BERExponent=CalculationProperty(self.AutoAlignFrame,'BER Exponent for Alignment',self.onUpdateFromChanges,None,self.project,'Alignment.BERForAlignment')
        self.AlignmentMode=CalculationPropertyChoices(self.AutoAlignFrame,'Alignment Mode',self.onUpdateFromChanges,None,self.AlignmentModeChoices,self.project,'Alignment.Mode')
        self.VerticalAlignmentMode=CalculationPropertyChoices(self.AutoAlignFrame,'Vertical Alignment',self.onUpdateFromChanges,None,self.VerticalAlignmentModeChoices,self.project,'Alignment.Vertical')
        self.HorizontalAlignmentMode=CalculationPropertyChoices(self.AutoAlignFrame,'Horizontal Alignment',self.onUpdateFromChanges,None,self.HorizontalAlignmentModeChoices,self.project,'Alignment.Horizontal')
        self.Measurements=CalculationPropertyTrueFalseButton(self.MeasurementsFrame,'Measure Eye Parameters',self.onUpdateFromChanges,None,self.project,'Measure.Measure')
        self.BERForMeasure=CalculationProperty(self.MeasurementsFrame,'BER Exponent for Measure',self.onUpdateFromChanges,None,self.project,'Measure.BERForMeasure')
        if SignalIntegrity.App.Preferences['Features.OpticalMeasurements']:
            self.NoisePenalty=CalculationPropertySI(self.MeasurementsFrame,'Noise Penalty',self.onUpdateFromChanges,None,self.project,'Measure.NoisePenalty','dB')
        self.DecisionMode=CalculationPropertyChoices(self.MeasurementsFrame,'Decision Level',self.onUpdateFromChanges,None,self.DecisionChoices,self.project,'Decision.Mode')
        self.BathtubFrame=tk.Frame(self.MeasurementsFrame,relief=tk.RIDGE, borderwidth=5)
        self.BathtubFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.BathtubCurves=CalculationPropertyTrueFalseButton(self.BathtubFrame,'Measure Bathtub Curves',self.onUpdateFromChanges,None,self.project,'Bathtub.Measure')
        self.DecadesFromJoin=CalculationProperty(self.BathtubFrame,'Decades Above for Fit',self.onUpdateFromChanges,None,self.project,'Bathtub.DecadesFromJoinForFit')
        self.MinPointsForFit=CalculationProperty(self.BathtubFrame,'Minimum Points for Fit',self.onUpdateFromChanges,None,self.project,'Bathtub.MinPointsForFit')
        self.AnnotateFrame=tk.Frame(self.MeasurementsFrame,relief=tk.RIDGE, borderwidth=5)
        self.AnnotateFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.Annotate=CalculationPropertyTrueFalseButton(self.AnnotateFrame,'Annotate Eye with Measurements',self.onUpdateFromChanges,None,self.project,'Annotation.Annotate')
        self.AnnotationColor=CalculationPropertyColor(self.AnnotateFrame,'Annotation Color',self.onUpdateFromChanges,None,self.project,'Annotation.Color')
        self.AnnotateMeanLevels=CalculationPropertyTrueFalseButton(self.AnnotateFrame,'Annotate Mean Levels',self.onUpdateFromChanges,None,self.project,'Annotation.MeanLevels')
        self.AnnotateLevelExtents=CalculationPropertyTrueFalseButton(self.AnnotateFrame,'Annotate Level Extents',self.onUpdateFromChanges,None,self.project,'Annotation.LevelExtents')
        self.AnnotateEyeWidth=CalculationPropertyTrueFalseButton(self.AnnotateFrame,'Annotate Eye Width',self.onUpdateFromChanges,None,self.project,'Annotation.EyeWidth')
        self.AnnotateEyeHeight=CalculationPropertyTrueFalseButton(self.AnnotateFrame,'Annotate Eye Height',self.onUpdateFromChanges,None,self.project,'Annotation.EyeHeight')
        self.ContoursFrame=tk.Frame(self.AnnotateFrame, relief=tk.RIDGE, borderwidth=5)
        self.ContoursFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.AnnotateContour=CalculationPropertyTrueFalseButton(self.ContoursFrame,'Annotate Contour',self.onUpdateFromChanges,None,self.project,'Annotation.Contours.Show')
        self.ContourMode=CalculationPropertyChoices(self.ContoursFrame,'Which Contours to Show',self.onUpdateFromChanges,None,self.ContourChoices,self.project,'Annotation.Contours.Which')
        self.EnhancedPrecisionMode=CalculationPropertyChoices(self.EnhancedPrecisionFrame,'Enhanced Precision Mode',self.onUpdateFromChanges,None,self.EnhancedPrecisionChoices,self.project,'EnhancedPrecision.Mode')
        self.EnhancedPrecisionSteps=CalculationProperty(self.EnhancedPrecisionFrame,'Enhanced Precision Steps',self.onUpdateFromChanges,None,self.project,'EnhancedPrecision.FixedEnhancement')
        self.YAxisModeFrame=CalculationPropertyChoices(self.YAxisFrame,'Y Axis',self.onUpdateFromChanges,None,self.YAxisModeChoices,self.project,'YAxis.Mode')
        self.MaxYFrame=CalculationPropertySI(self.YAxisFrame,'Maximum Y',self.onUpdateFromChanges,None,self.project,'YAxis.Max','V')
        self.MinYFrame=CalculationPropertySI(self.YAxisFrame,'Minimum Y',self.onUpdateFromChanges,None,self.project,'YAxis.Min','V')
        self.Mode=CalculationPropertyChoices(self.JitterNoiseFrame,'Eye Mode',self.onUpdateFromChanges,None,self.ModeChoices,self.project,'Mode')
        self.JitterSeconds=CalculationPropertySI(self.JitterNoiseFrame,'Random Jitter (s)',self.onUpdateFromChanges,None,self.project,'JitterNoise.JitterS','s')
        self.JitterDeterministicPkS=CalculationPropertySI(self.JitterNoiseFrame,'Deterministic Jitter (s, pk)',self.onUpdateFromChanges,None,self.project,'JitterNoise.JitterDeterministicPkS','s')
        self.Noise=CalculationPropertySI(self.JitterNoiseFrame,'Noise',self.onUpdateFromChanges,None,self.project,'JitterNoise.Noise','V')
        self.MaxWindowWidthHeightPixels=CalculationPropertySI(self.JitterNoiseFrame,'Max Kernel Pixels',self.onUpdateFromChanges,None,self.project,'JitterNoise.MaxKernelPixels','pixels')
        self.Invert=CalculationPropertyTrueFalseButton(self.LeftFrame,'Invert Plot',self.onUpdateFromChanges,None,self.project,'Invert')
        self.LogIntensity=CalculationPropertyTrueFalseButton(self.LogIntensityFrame,'Log Intensity',self.onUpdateFromChanges,None,self.project,'JitterNoise.LogIntensity.LogIntensity')
        self.MinExponent=CalculationProperty(self.LogIntensityFrame,'Min Exponent',self.onUpdateFromChanges,None,self.project,'JitterNoise.LogIntensity.MinExponent')
        self.MaxExponent=CalculationProperty(self.LogIntensityFrame,'Max Exponent',self.onUpdateFromChanges,None,self.project,'JitterNoise.LogIntensity.MaxExponent')
        self.SaveToPreferencesFrame=tk.Frame(self.RightFrame,relief=tk.RIDGE, borderwidth=5)
        self.SaveToPreferencesFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.SaveToPreferencesButton = tk.Button(self.SaveToPreferencesFrame,text='Save Properties to Global Preferences',command=self.onSaveToPreferences,width=CalculationProperty.labelWidth)
        self.SaveToPreferencesButton.pack(side=tk.TOP,expand=tk.YES)
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
        measure=self.project['Measure.Measure']
        annotate=self.project['Annotation.Annotate']
        contours=self.project['Annotation.Contours.Show']
        bathtub=self.project['Bathtub.Measure']
        self.BathtubFrame.pack_forget()
        self.AnnotateFrame.pack_forget()
        self.DecisionMode.Show(measure)
        self.BERForMeasure.Show(measure)
        if SignalIntegrity.App.Preferences['Features.OpticalMeasurements']:
            self.NoisePenalty.Show(measure)
        if measure:
            self.BathtubFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            self.AnnotateFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.BathtubCurves.Show(measure)
        self.DecadesFromJoin.Show(measure and bathtub)
        self.MinPointsForFit.Show(measure and bathtub)
        self.Annotate.Show(measure)
        self.ContoursFrame.pack_forget()
        self.AnnotationColor.Show(measure and annotate)
        self.AnnotateMeanLevels.Show(measure and annotate)
        self.AnnotateLevelExtents.Show(measure and annotate)
        self.AnnotateEyeWidth.Show(measure and annotate)
        self.AnnotateEyeHeight.Show(measure and annotate)
        if measure and annotate:
            self.ContoursFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.AnnotateContour.Show(measure and annotate)
        self.ContourMode.Show(measure and annotate and contours)
        self.BERExponent.Show(autoAlign)
        self.AlignmentMode.Show(autoAlign)
        self.VerticalAlignmentMode.Show(autoAlign and (self.project['Alignment.Mode']=='Vertical'))
        self.HorizontalAlignmentMode.Show(autoAlign and (self.project['Alignment.Mode']=='Horizontal'))
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
        self.JitterSeconds.Show(jitterNoiseMode)
        self.JitterDeterministicPkS.Show(jitterNoiseMode)
        self.Noise.Show(jitterNoiseMode)
        self.MaxWindowWidthHeightPixels.Show(jitterNoiseMode)
        logIntensity=self.project['JitterNoise.LogIntensity.LogIntensity']
        self.MinExponent.Show(logIntensity)
        self.MaxExponent.Show(logIntensity)
    def onSaveToPreferences(self):
        self.parent.device.configuration.SaveToPreferences()
