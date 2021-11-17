"""
EyeDiagram.py
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
    import tkMessageBox as messagebox
else:
    import tkinter as tk
    from tkinter import messagebox

from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionEyeDiagram
from SignalIntegrity.Lib.Eye.EyeDiagramBitmap import EyeDiagramBitmap

import SignalIntegrity.App.Project
import SignalIntegrity.App.Preferences

class EyeDiagram(object):
    def __init__(self,parent,name,headless=False):
        self.parent=parent
        self.headless=headless
        self.name=name

    def Image(self):
        return self.img

    def BitMap(self):
        return self.rawBitmap

    def Measurements(self):
        return self.measDict

    def CalculateEyeDiagram(self,cacheFileName,callback=None):
        self.img=None
        self.rawBitmap=None
        self.measDict=None
        self.annotationBitmap=None

        if not self.headless: self.parent.statusbar.set('Creating Eye Diagram')
        # calculate the bitmap directly from the serial data waveform supplied
        try:
            eyeDiagramBitmap=EyeDiagramBitmap(
                callback=callback,
                cacheFileName=cacheFileName+'_'+self.name if SignalIntegrity.App.Preferences['Cache.CacheResults'] else None,
                YAxisMode=self.config['YAxis.Mode'],
                YMax=self.config['YAxis.Max'],
                YMin=self.config['YAxis.Min'],
                Rows=self.config['Rows'],
                Cols=self.config['Columns'],
                BaudRate=self.baudrate,
                prbswf=self.prbswf,
                EnhancementMode=self.config['EnhancedPrecision.Mode'],
                EnhancementSteps=self.config['EnhancedPrecision.FixedEnhancement'],
                BitsPerSymbol=self.config['Alignment.BitsPerSymbol'], # 1 for NRZ, 2 for PAM-4  (3 for PAM-8!?)
                )
        except Exception as e:
            raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Creation Failed.')

        if eyeDiagramBitmap.Bitmap() is None:
            raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Not Created.')

        # if desired, apply jitter and noise to the bitmap
        try:
            applyJitterNoise=(self.config['Mode'] == 'JitterNoise')
            if applyJitterNoise:
                if not self.headless: self.parent.statusbar.set('Applying Jitter and Noise')
                eyeDiagramBitmap.ApplyJitterNoise(
                                NoiseSigma=self.config['JitterNoise.Noise'],
                                JitterSigma=self.config['JitterNoise.JitterS'],
                                DeterministicJitter=self.config['JitterNoise.JitterDeterministicPkS'],
                                MaxPixelsKernel=int(self.config['JitterNoise.MaxKernelPixels']))
        except Exception as e:
            pass
            #raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Jitter/Noise Failed.')

        # if desired, automatically align the waveform to place the eye at the center.
        try:
            if self.config['Alignment.AutoAlign']:
                if not self.headless: self.parent.statusbar.set('Aligning Eye Diagram')
                eyeDiagramBitmap.AutoAlign(
                  BERForAlignment=self.config['Alignment.BERForAlignment'], # Exponent of probability contour to align on
                  AlignmentMode=self.config['Alignment.Mode'], # can be 'Horizontal' or 'Vertical'
                  HorizontalAlignment=self.config['Alignment.Horizontal'], # 'Middle' or 'Max' (vertical eye) - alignment will be the horizontal midpoint of one of these two eye possibilities
                  VerticalAlignment=self.config['Alignment.Vertical'], # 'MaxMin' (maximum minimum opening) or 'Max' (maximum opening) 
                  )
        except Exception as e:
            pass
            #raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Auto-Alignment Failed.')

        try:
            if self.config['Measure.Measure']:
                if not self.headless: self.parent.statusbar.set('Measuring Eye Diagram')
                eyeDiagramBitmap.Measure(
                    BERForMeasure=self.config['Measure.BERForMeasure'], # Exponent of probability contour to measure
                    DecisionMode=self.config['Decision.Mode'] # 'Mid' or 'Best' for independent decision levels
                    )
        except Exception as e:
            pass
            #raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Measurement Failed.')

        try:
            if self.config['Bathtub.Measure']:
                if not self.headless: self.parent.statusbar.set('Calculating Bathtub Curves')
                eyeDiagramBitmap.Bathtub(
                    DecadesFromJoin=self.config['Bathtub.DecadesFromJoinForFit'],
                    MinPointsForFit=self.config['Bathtub.MinPointsForFit']
                    )
        except Exception as e:
            pass
            #raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Bathtub Curves Failed.')

        try:
            if self.config['Measure.Measure'] and self.config['Annotation.Annotate']:
                if not self.headless: self.parent.statusbar.set('Annotating Eye Diagram')
                eyeDiagramBitmap.Annotations(
                                MeanLevels=self.config['Annotation.MeanLevels'],
                                LevelExtents=self.config['Annotation.LevelExtents'],
                                EyeWidth=self.config['Annotation.EyeWidth'],
                                EyeHeight=self.config['Annotation.EyeHeight'],
                                Contours=self.config['Annotation.Contours.Show'],
                                WhichContours=self.config['Annotation.Contours.Which'] # 'Eye' or 'All'
                                )
        except Exception as e:
            pass
            #raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Annotations Failed.')

        try:
            if not self.headless: self.parent.statusbar.set('Creating Image')
            eyeDiagramBitmap.CreateImage(
                        LogIntensity=self.config['JitterNoise.LogIntensity.LogIntensity'],
                        MinExponentLogIntensity=self.config['JitterNoise.LogIntensity.MinExponent'],
                        MaxExponentLogIntensity=self.config['JitterNoise.LogIntensity.MaxExponent'],
                        NumUI=self.config['UI'],
                        Saturation=self.config['Saturation'],
                        InvertImage=self.config['Invert'],
                        Color=self.config['Color'],
                        AnnotationColor=self.config['Annotation.Color'],
                        ScaleX=self.config['ScaleX'],
                        ScaleY=self.config['ScaleY']
                        )
        except Exception as e:
            pass
            #raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Image Creation Failed.')

        if SignalIntegrity.App.Preferences['Features.OpticalMeasurements']:
            try:
                if self.config['Measure.Measure']:
                    if not self.headless: self.parent.statusbar.set('Calculating Penalties')
                    eyeDiagramBitmap.Penalties(self.config['Measure.NoisePenalty'])
            except Exception as e:
                pass
                #raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Penalties Calculation Failed.')

        if not self.headless: self.parent.statusbar.set('Calculation Complete')
        self.measDict=eyeDiagramBitmap.measDict
        self.rawBitmap=eyeDiagramBitmap.Bitmap()
        self.img=eyeDiagramBitmap.img
