"""
EyeDiagramPropertiesDialog.py
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

import math

from SignalIntegrity.App.ConfigurationPropertiesDialog import (
    ConfigurationDialog as PropertiesDialog, ConfigurationPropertyTrueFalseButton as CalculationPropertyTrueFalseButton,
    ConfigurationPropertyChoices as CalculationPropertyChoices, ConfigurationPropertySI as CalculationPropertySI,
    ConfigurationProperty as CalculationProperty, ConfigurationPropertyColor as CalculationPropertyColor)
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
    WaveformTypeChoices=[('Voltage','V'),('Current','A'),('Power','W'),('Fractional Power','FW'),('Current proportional to Power','AW'),('Voltage proportional to Power','VW')]
    RxTxChoices=[('Receiver','Rx'),('Transmitter','Tx'),('Not Applicable','N/A')]
    UpsampleMethodChoices=[('sinx','SinX'),('linear','Linear')]
    def __init__(self,project,parent):
        PropertiesDialog.__init__(self,parent,project,parent.parent,'Eye Diagram Properties')
        self.transient(parent)
        self.LeftFrame=tk.Frame(self.propertyListFrame)
        self.LeftFrame.pack(side=tk.LEFT,fill=tk.X,expand=tk.NO,anchor=tk.NW)
        self.RightFrame=tk.Frame(self.propertyListFrame)
        self.RightFrame.pack(side=tk.LEFT,fill=tk.X,expand=tk.NO,anchor=tk.NW)
        self.GeneralFrame=tk.LabelFrame(self.LeftFrame,text='Eye Image',relief=tk.RIDGE,borderwidth=2)
        self.GeneralFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.ClockRecoveryFrame=tk.LabelFrame(self.LeftFrame,text='Clock Recovery',relief=tk.RIDGE,borderwidth=2)
        self.ClockRecoveryFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.EnhancedPrecisionFrame=tk.LabelFrame(self.LeftFrame,text='Precision',relief=tk.RIDGE,borderwidth=2)
        self.EnhancedPrecisionFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.YAxisFrame=tk.LabelFrame(self.LeftFrame,text='Y Axis',relief=tk.RIDGE,borderwidth=2)
        self.YAxisFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.JitterNoiseFrame=tk.LabelFrame(self.LeftFrame,text='Jitter and Noise',relief=tk.RIDGE,borderwidth=2)
        self.JitterNoiseFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.LogIntensityFrame=tk.LabelFrame(self.LeftFrame,text='Intensity',relief=tk.RIDGE,borderwidth=2)
        self.LogIntensityFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.InvertFrame=tk.LabelFrame(self.LeftFrame,text='Plot Appearance',relief=tk.RIDGE,borderwidth=2)
        self.InvertFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.AutoAlignFrame=tk.LabelFrame(self.LeftFrame,text='Eye Alignment',relief=tk.RIDGE,borderwidth=2)
        self.AutoAlignFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.MeasurementsFrame=tk.LabelFrame(self.RightFrame,text='Measurements',relief=tk.RIDGE,borderwidth=2)
        self.MeasurementsFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.Levels=CalculationProperty(self.GeneralFrame,'Number of Levels',self.onUpdateFromChanges,None,self.project,'Alignment.Levels',tooltip='The number of levels per symbol\nThe PAM of the waveform')
        self.Color=CalculationPropertyColor(self.GeneralFrame,'Color',self.onUpdateFromChanges,None,self.project,'Color',tooltip='The color of the eye in the eye diagram if Invert is True,\notherwise is the background color')
        self.UIFrame=CalculationProperty(self.GeneralFrame,'Number of UI',self.onUpdateFromChanges,None,self.project,'UI',tooltip='The number of unit intervals that will be shown in the eye diagram plot generated')
        self.RowsFrame=CalculationProperty(self.GeneralFrame,'Number of Rows',self.onUpdateFromChanges,None,self.project,'Rows',tooltip='The number of pixels vertically in the raw eye diagram.\nThis is scaled by the factor in \'Scale X\'')
        self.ColsFrame=CalculationProperty(self.GeneralFrame,'Number of Columns',self.onUpdateFromChanges,None,self.project,'Columns',tooltip='The number of pixels horixontally in one UI in the raw eye diagram.\nThis is scaled by the factor in \'Scale Y\'')
        self.SaturationFrame=CalculationPropertySI(self.GeneralFrame,'Saturation',self.onUpdateFromChanges,None,self.project,'Saturation','%')
        self.ScaleXFrame=CalculationPropertySI(self.GeneralFrame,'Scale X',self.onUpdateFromChanges,None,self.project,'ScaleX','%')
        self.ScaleYFrame=CalculationPropertySI(self.GeneralFrame,'Scale Y',self.onUpdateFromChanges,None,self.project,'ScaleY','%')
        self.UpsampleMethod=CalculationPropertyChoices(self.ClockRecoveryFrame,'Upsample Method',self.onUpdateFromChanges,None,self.UpsampleMethodChoices,self.project,'UpsampleMethod')
        self.RecoverClock=CalculationPropertyTrueFalseButton(self.ClockRecoveryFrame,'Recover Clock',self.onUpdateFromChanges,None,self.project,'ClockRecovery.Recover')
        self.RecoverClockTrimLeftRight=CalculationProperty(self.ClockRecoveryFrame,'Points to Trim From Both Sides',self.onUpdateFromChanges,None,self.project,'ClockRecovery.TrimLeftRight')
        self.AutoAlign=CalculationPropertyTrueFalseButton(self.AutoAlignFrame,'Auto Align Eye',self.onUpdateFromChanges,None,self.project,'Alignment.AutoAlign')
        self.BERExponent=CalculationProperty(self.AutoAlignFrame,'BER Exponent for Alignment',self.onUpdateFromChanges,None,self.project,'Alignment.BERForAlignment')
        self.AlignmentMode=CalculationPropertyChoices(self.AutoAlignFrame,'Alignment Mode',self.onUpdateFromChanges,None,self.AlignmentModeChoices,self.project,'Alignment.Mode')
        self.VerticalAlignmentMode=CalculationPropertyChoices(self.AutoAlignFrame,'Vertical Alignment',self.onUpdateFromChanges,None,self.VerticalAlignmentModeChoices,self.project,'Alignment.Vertical')
        self.HorizontalAlignmentMode=CalculationPropertyChoices(self.AutoAlignFrame,'Horizontal Alignment',self.onUpdateFromChanges,None,self.HorizontalAlignmentModeChoices,self.project,'Alignment.Horizontal')
        self.Measurements=CalculationPropertyTrueFalseButton(self.MeasurementsFrame,'Measure Eye Parameters',self.onUpdateFromChanges,None,self.project,'Measure.Measure')
        self.WaveformType=CalculationPropertyChoices(self.MeasurementsFrame,'Waveform Type',self.onUpdateFromChanges,None,self.WaveformTypeChoices,self.project,'Measure.WaveformType')
        self.RxTx=CalculationPropertyChoices(self.MeasurementsFrame,'Reciever or Transmitter',self.onUpdateFromChanges,None,self.RxTxChoices,self.project,'Measure.RxTx')
        self.TxInputPowerAvailable=CalculationPropertyTrueFalseButton(self.MeasurementsFrame,'Input Power Available',self.onUpdateFromChanges,None,self.project,'Measure.TxInputPowerAvailable')
        self.TxInputPowerW=CalculationPropertySI(self.MeasurementsFrame,'Input Power (W)',self.onUpdateFromChanges,None,self.project,'Measure.TxInputPowerW','W')
        self.TxInputPowerdBm=CalculationPropertySI(self.MeasurementsFrame,'Input Power (dBm)',self.onUpdateInputPowerdBm,None,self.project,'Measure.TxInputPowerdBm','dBm')
        self.BERForMeasure=CalculationProperty(self.MeasurementsFrame,'BER Exponent for Measure',self.onUpdateFromChanges,None,self.project,'Measure.BERForMeasure')
        self.DecisionMode=CalculationPropertyChoices(self.MeasurementsFrame,'Decision Level',self.onUpdateFromChanges,None,self.DecisionChoices,self.project,'Decision.Mode')
        self.BathtubFrame=tk.LabelFrame(self.MeasurementsFrame,text='Bathtub Curves',relief=tk.RIDGE,borderwidth=2)
        self.BathtubFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.BathtubCurves=CalculationPropertyTrueFalseButton(self.BathtubFrame,'Measure Bathtub Curves',self.onUpdateFromChanges,None,self.project,'Bathtub.Measure')
        self.DecadesFromJoin=CalculationProperty(self.BathtubFrame,'Decades Above for Fit',self.onUpdateFromChanges,None,self.project,'Bathtub.DecadesFromJoinForFit')
        self.MinPointsForFit=CalculationProperty(self.BathtubFrame,'Minimum Points for Fit',self.onUpdateFromChanges,None,self.project,'Bathtub.MinPointsForFit')
        self.AnnotateFrame=tk.LabelFrame(self.MeasurementsFrame,text='Annotations',relief=tk.RIDGE,borderwidth=2)
        self.AnnotateFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.Annotate=CalculationPropertyTrueFalseButton(self.AnnotateFrame,'Annotate Eye with Measurements',self.onUpdateFromChanges,None,self.project,'Annotation.Annotate')
        self.AnnotationColor=CalculationPropertyColor(self.AnnotateFrame,'Annotation Color',self.onUpdateFromChanges,None,self.project,'Annotation.Color')
        self.MeanLevelsFrame=tk.LabelFrame(self.AnnotateFrame,text='Mean Levels',relief=tk.RIDGE,borderwidth=2)
        self.MeanLevelsFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.AnnotateMeanLevels=CalculationPropertyTrueFalseButton(self.MeanLevelsFrame,'Annotate Mean Levels',self.onUpdateFromChanges,None,self.project,'Annotation.MeanLevels')
        self.LabelMeanLevels=CalculationPropertyTrueFalseButton(self.MeanLevelsFrame,'Label Mean Levels',self.onUpdateFromChanges,None,self.project,'Annotation.LabelMeanLevels')
        self.AnnotateLevelExtents=CalculationPropertyTrueFalseButton(self.AnnotateFrame,'Annotate Level Extents',self.onUpdateFromChanges,None,self.project,'Annotation.LevelExtents')
        self.AnnotateEyeWidth=CalculationPropertyTrueFalseButton(self.AnnotateFrame,'Annotate Eye Width',self.onUpdateFromChanges,None,self.project,'Annotation.EyeWidth')
        self.AnnotateEyeHeight=CalculationPropertyTrueFalseButton(self.AnnotateFrame,'Annotate Eye Height',self.onUpdateFromChanges,None,self.project,'Annotation.EyeHeight')
        self.ContoursFrame=tk.LabelFrame(self.AnnotateFrame,text='Contours',relief=tk.RIDGE,borderwidth=2)
        self.ContoursFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.AnnotateContour=CalculationPropertyTrueFalseButton(self.ContoursFrame,'Annotate Contour',self.onUpdateFromChanges,None,self.project,'Annotation.Contours.Show')
        self.ContourMode=CalculationPropertyChoices(self.ContoursFrame,'Which Contours to Show',self.onUpdateFromChanges,None,self.ContourChoices,self.project,'Annotation.Contours.Which')
        self.EnhancedPrecisionMode=CalculationPropertyChoices(self.EnhancedPrecisionFrame,'Enhanced Precision Mode',self.onUpdateFromChanges,None,self.EnhancedPrecisionChoices,self.project,'EnhancedPrecision.Mode')
        self.EnhancedPrecisionSteps=CalculationProperty(self.EnhancedPrecisionFrame,'Enhanced Precision Steps',self.onUpdateFromChanges,None,self.project,'EnhancedPrecision.FixedEnhancement')
        self.YAxisModeFrame=CalculationPropertyChoices(self.YAxisFrame,'Y Axis',self.onUpdateFromChanges,None,self.YAxisModeChoices,self.project,'YAxis.Mode')
        self.MaxYFrame=CalculationPropertySI(self.YAxisFrame,'Maximum Y',self.onUpdateFromChanges,None,self.project,'YAxis.Max','V')
        self.MinYFrame=CalculationPropertySI(self.YAxisFrame,'Minimum Y',self.onUpdateFromChanges,None,self.project,'YAxis.Min','V')
        self.Mode=CalculationPropertyChoices(self.JitterNoiseFrame,'Eye Mode',self.onUpdateFromChanges,None,self.ModeChoices,self.project,'Mode')
        noiseUnit=None
        self.JitterSeconds=CalculationPropertySI(self.JitterNoiseFrame,'Random Jitter (s)',self.onUpdateFromChanges,None,self.project,'JitterNoise.JitterS','s')
        self.JitterDeterministicPkS=CalculationPropertySI(self.JitterNoiseFrame,'Deterministic Jitter (s, pk)',self.onUpdateFromChanges,None,self.project,'JitterNoise.JitterDeterministicPkS','s')
        self.Noise=CalculationPropertySI(self.JitterNoiseFrame,'Inherent Noise',self.onUpdateNoise,None,self.project,'JitterNoise.Noise',noiseUnit)
        self.ExternalNoise=CalculationPropertySI(self.JitterNoiseFrame,'External Noise',self.onUpdateFromChanges,None,self.project,'JitterNoise.ExternalNoise',noiseUnit)
        self.ExternalNoise.SetReadOnly(True)
        self.TotalNoise=CalculationPropertySI(self.JitterNoiseFrame,'Total Noise',self.onUpdateFromChanges,None,self.project,'JitterNoise.TotalNoise',noiseUnit)
        self.TotalNoise.SetReadOnly(True)
        self.MaxWindowWidthHeightPixels=CalculationPropertySI(self.JitterNoiseFrame,'Max Kernel Pixels',self.onUpdateFromChanges,None,self.project,'JitterNoise.MaxKernelPixels','pixels')
        self.Invert=CalculationPropertyTrueFalseButton(self.InvertFrame,'Invert Plot',self.onUpdateFromChanges,None,self.project,'Invert')
        self.LogIntensity=CalculationPropertyTrueFalseButton(self.LogIntensityFrame,'Log Intensity',self.onUpdateFromChanges,None,self.project,'JitterNoise.LogIntensity.LogIntensity')
        self.MinExponent=CalculationProperty(self.LogIntensityFrame,'Min Exponent',self.onUpdateFromChanges,None,self.project,'JitterNoise.LogIntensity.MinExponent')
        self.MaxExponent=CalculationProperty(self.LogIntensityFrame,'Max Exponent',self.onUpdateFromChanges,None,self.project,'JitterNoise.LogIntensity.MaxExponent')
        self.SaveToPreferencesFrame=tk.Frame(self.RightFrame,relief=tk.RIDGE, borderwidth=5)
        self.SaveToPreferencesFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.SaveToPreferencesButton = tk.Button(self.SaveToPreferencesFrame,text='Save Properties to Global Preferences',command=self.onSaveToPreferences,width=CalculationProperty.labelWidth)
        self.SaveToPreferencesButton.pack(side=tk.TOP,expand=tk.YES)
        self.Finish()
    def Finish(self):
        self.FinishConfiguration()
    def onUpdateInputPowerdBm(self,_):
        self.project['Measure.TxInputPowerW']=10.**(self.project['Measure.TxInputPowerdBm']/10.)*1e-3
        self.TxInputPowerW.UpdateStrings()
        self.UpdateStrings()
    def onUpdateNoise(self,_):
        import numpy as np
        self.project.SetExternalNoise(self.project['JitterNoise.ExternalNoise'])
        self.UpdateStrings()
    def onUpdateFromChanges(self,_):
        self.UpdateStrings()
    def UpdateStrings(self):
        self.RefreshConfiguration()
    def onSaveToPreferences(self):
        self.parent.device.configuration.SaveToPreferences()
