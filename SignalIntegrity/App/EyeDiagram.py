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
                YAxisMode=SignalIntegrity.App.Project['EyeDiagram.YAxis.Mode'],
                YMax=SignalIntegrity.App.Project['EyeDiagram.YAxis.Max'],
                YMin=SignalIntegrity.App.Project['EyeDiagram.YAxis.Min'],
                NoiseSigma=SignalIntegrity.App.Project['EyeDiagram.JitterNoise.Noise'] if (SignalIntegrity.App.Project['EyeDiagram.Mode'] == 'JitterNoise') else 0,
                Rows=SignalIntegrity.App.Project['EyeDiagram.Rows'],
                Cols=SignalIntegrity.App.Project['EyeDiagram.Columns'],
                BaudRate=self.baudrate,
                prbswf=self.prbswf,
                EnhancementMode=SignalIntegrity.App.Project['EyeDiagram.EnhancedPrecision.Mode'],
                EnhancementSteps=SignalIntegrity.App.Project['EyeDiagram.EnhancedPrecision.FixedEnhancement'],
                BitsPerSymbol=SignalIntegrity.App.Project['EyeDiagram.Alignment.BitsPerSymbol'], # 1 for NRZ, 2 for PAM-4  (3 for PAM-8!?)
                )
        except Exception as e:
            raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Creation Failed.')

        if eyeDiagramBitmap.Bitmap() is None:
            raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Not Created.')

        # if desired, apply jitter and noise to the bitmap
        try:
            applyJitterNoise=(SignalIntegrity.App.Project['EyeDiagram.Mode'] == 'JitterNoise')
            if applyJitterNoise:
                if not self.headless: self.parent.statusbar.set('Applying Jitter and Noise')
                eyeDiagramBitmap.ApplyJitterNoise(
                                NoiseSigma=SignalIntegrity.App.Project['EyeDiagram.JitterNoise.Noise'],
                                JitterSigma=SignalIntegrity.App.Project['EyeDiagram.JitterNoise.JitterS'],
                                DeterministicJitter=SignalIntegrity.App.Project['EyeDiagram.JitterNoise.JitterDeterministicPkS'],
                                MaxPixelsKernel=int(SignalIntegrity.App.Project['EyeDiagram.JitterNoise.MaxKernelPixels']))
        except Exception as e:
            pass
            #raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Jitter/Noise Failed.')

        # if desired, automaticall align the waveform to place the eye at the center.  If measurements are to be performed, the alignment performed
        # to generate the eye extents only
        try:
            if SignalIntegrity.App.Project['EyeDiagram.Alignment.AutoAlign'] or SignalIntegrity.App.Project['EyeDiagram.Measure.Measure']:
                if not self.headless: self.parent.statusbar.set('Aligning Eye Diagram')
                eyeDiagramBitmap.AutoAlign(
                  BERForAlignment=SignalIntegrity.App.Project['EyeDiagram.Alignment.BERForAlignment'], # Exponent of probability contour to align on
                  AlignmentMode=SignalIntegrity.App.Project['EyeDiagram.Alignment.Mode'], # can be 'Horizontal' or 'Vertical'
                  HorizontalAlignment=SignalIntegrity.App.Project['EyeDiagram.Alignment.Horizontal'], # 'Middle' or 'Max' (vertical eye) - alignment will be the horizontal midpoint of one of these two eye possibilities
                  VerticalAlignment=SignalIntegrity.App.Project['EyeDiagram.Alignment.Vertical'], # 'MaxMin' (maximum minimum opening) or 'Max' (maximum opening) 
                  GenerateExtentsOnly=not SignalIntegrity.App.Project['EyeDiagram.Alignment.AutoAlign'] # if this is True, calculations are made only to obtain the extents, to be used in the measurements
                  )
        except Exception as e:
            pass
            #raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Auto-Alignment Failed.')

        try:
            if not self.headless: self.parent.statusbar.set('Measuring Eye Diagram')
            eyeDiagramBitmap.Measure(
                BERForMeasure=SignalIntegrity.App.Project['EyeDiagram.Measure.BERForMeasure'], # Exponent of probability contour to measure
                DecisionMode=SignalIntegrity.App.Project['EyeDiagram.Decision.Mode'] # 'Mid' or 'Best' for independent decision levels
                )
        except Exception as e:
            pass
            #raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Measurement Failed.')

        try:
            if not self.headless: self.parent.statusbar.set('Calculating Bathtub Curves')
            eyeDiagramBitmap.Bathtub()
        except Exception as e:
            pass
            #raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Bathtub Curves Failed.')

        try:
            if SignalIntegrity.App.Project['EyeDiagram.Annotation.Annotate']:
                if not self.headless: self.parent.statusbar.set('Annotating Eye Diagram')
                eyeDiagramBitmap.Annotations(
                                MeanLevels=SignalIntegrity.App.Project['EyeDiagram.Annotation.MeanLevels'],
                                LevelExtents=SignalIntegrity.App.Project['EyeDiagram.Annotation.LevelExtents'],
                                EyeWidth=SignalIntegrity.App.Project['EyeDiagram.Annotation.EyeWidth'],
                                EyeHeight=SignalIntegrity.App.Project['EyeDiagram.Annotation.EyeHeight'],
                                Contours=SignalIntegrity.App.Project['EyeDiagram.Annotation.Contours.Show'],
                                WhichContours=SignalIntegrity.App.Project['EyeDiagram.Annotation.Contours.Which'] # 'Eye' or 'All'
                                )
        except Exception as e:
            pass
            #raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Annotations Failed.')

        try:
            if not self.headless: self.parent.statusbar.set('Creating Image')
            eyeDiagramBitmap.CreateImage(
                        LogIntensity=SignalIntegrity.App.Project['EyeDiagram.JitterNoise.LogIntensity.LogIntensity'],
                        MinExponentLogIntensity=SignalIntegrity.App.Project['EyeDiagram.JitterNoise.LogIntensity.MinExponent'],
                        MaxExponentLogIntensity=SignalIntegrity.App.Project['EyeDiagram.JitterNoise.LogIntensity.MaxExponent'],
                        NumUI=SignalIntegrity.App.Project['EyeDiagram.UI'],
                        Saturation=SignalIntegrity.App.Project['EyeDiagram.Saturation'],
                        InvertImage=SignalIntegrity.App.Project['EyeDiagram.Invert'],
                        Color=SignalIntegrity.App.Project['EyeDiagram.Color'],
                        AnnotationColor=SignalIntegrity.App.Project['EyeDiagram.Annotation.Color'],
                        ScaleX=SignalIntegrity.App.Project['EyeDiagram.ScaleX'],
                        ScaleY=SignalIntegrity.App.Project['EyeDiagram.ScaleY']
                        )
        except Exception as e:
            pass
            #raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Image Creation Failed.')

        try:
            if not self.headless: self.parent.statusbar.set('Calculating Penalties')
            eyeDiagramBitmap.Penalties(SignalIntegrity.App.Project['EyeDiagram.Measure.NoisePenalty'])
        except Exception as e:
            pass
            #raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Penalties Calculation Failed.')

        if not self.headless: self.parent.statusbar.set('Calculation Complete')
        self.measDict=eyeDiagramBitmap.measDict
        self.rawBitmap=eyeDiagramBitmap.Bitmap()
        self.img=eyeDiagramBitmap.img
