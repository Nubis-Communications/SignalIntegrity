"""
 Conversion of TDR waveforms to raw measured s-parameters
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

import copy
import math

from SignalIntegrity.Lib.TimeDomain.Filters import WaveformTrimmer
from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.Wavelets.WaveletDenoiser import WaveletDenoiser
from SignalIntegrity.Lib.TimeDomain.Waveform import Waveform

class TDRWaveformToSParameterConverter(object):
    """Class for converting TDR waveforms to raw measured s-parameters"""
    sigmaMultiple=5.
    taper=True
    def __init__(self,
                 WindowForwardHalfWidthTime=0,
                 WindowReverseHalfWidthTime=None,
                 WindowRaisedCosineDuration=0,
                 Step=True,
                 Length=0,
                 Denoise=False,
                 DenoisePercent=30.,
                 Inverted=False,
                 fd=None
                 ):
        """Constructor
        @param WindowForwardHalfWidthTime (optional) float amount of time in extraction window on
        forward side of incident wave (defaults to 0).
        @param WindowReverseHalfWidthTime (optional) float amount of time in extraction window on
        reverse side of incident wave (defaults to None).
        @param WindowRaisedCosineDuration (optional) float amount of time to taper extraction
        window with raised cosine (defaults to 0).
        @param Step (optional) boolean True if waveforms are steps, False if waveforms are
        impulses (defaults to True).
        @param Length (optional) float length of time to clip waveform to (defaults to 0 meaning no clipping).
        @param Denoise (optiona) boolean whether to perform wavelet denoising (defaults to False).
        @param DenoisePercent (optional) percent of end portion of the waveform used
        during denoising for noise statistics estimation (defaults to 30 percent).
        @param Inverted (optional) boolean whether the waveform is inverted
        (defaults to False).
        @param fd (optional) instance of class FrequencyList used to define desired
        frequencies for the s-parameters (defaults to None).
        @note if fd is None or not provided, then the frequencies will correspond to
        the time descriptor of the trimmed waveform.
        @see TimeDescriptor
        @note if WindowReverseHalfWidthTime is None, then it defaults to the WindowForwardHalfWidthTime
        """
        self.wfhwt=WindowForwardHalfWidthTime
        self.wrhwt = self.wfhwt if WindowReverseHalfWidthTime is None\
            else WindowReverseHalfWidthTime
        self.wrcdr=WindowRaisedCosineDuration
        self.step=Step
        self.length=Length
        self.denoise=Denoise
        self.denoisePercent=DenoisePercent
        self.inverted=Inverted
        self.fd=fd
    def RawMeasuredSParameters(self,wfList):
        """RawMeasuredSParameters
        @param wfList list of lists of waveforms of measurements.
        @return instance of class SParameters containing the raw measured
        s-parameters of the DUT.

        Each element at index d in wfList is a list of waveforms where
        the zero based dth waveform contains the incident and the others don't.
        (i.e. they are the waveforms measured at the ports of the DUT when zero
        based port d is driven).

        For a P port DUT, wfList must be PxP.
        @note for one port measurements, wfList can be a single measurement (as opposed
        to a 1x1 list of list of one element).
        """
        # pragma: silent exclude
        wfList=copy.deepcopy(wfList)
        if isinstance(wfList, Waveform):
            wfList=[wfList]
        # pragma: silent include
        ports=len(wfList)
        S=[[None for _ in range(ports)] for _ in range(ports)]
        for d in range(ports):
            # pragma: silent exclude
            if isinstance(wfList[d],Waveform):
                wfList[d]=[wfList[d]]
            # pragma: include
            fc=self.Convert(wfList[d],d)
            for o in range(ports):
                S[o][d]=fc[o]
        f=S[0][0].Frequencies()
        return SParameters(f,
            [[[S[r][c][n] for c in range(ports)] for r in range(ports)]
            for n in range(len(f))])
    def Convert(self,wfListProvided,incidentIndex=0):
        # pragma: silent exclude
        wfList=copy.deepcopy(wfListProvided)
        if isinstance(wfList, Waveform):
            wfList=[wfList]
        # pragma: silent include
        if self.step:
            wfList=[wf.Derivative(removePoint=False,scale=False)
                    for wf in wfList]
        if self.inverted:
            wfList=[wf*-1. for wf in wfList]
        # pragma: silent exclude
        self.derivatives=copy.deepcopy(wfList)
        # pragma: silent include
        if self.denoise:
            wfList=[WaveletDenoiser.DenoisedWaveform(
                wf,isDerivative=self.step,
                mult=self.sigmaMultiple,
                pct=self.denoisePercent)
                    for wf in wfList]
        # pragma: silent exclude
        self.denoisedDerivatives=copy.deepcopy(wfList)
        # pragma: silent include
        if self.length!=0:
            lengthSamples=int(self.length*
                wfList[incidentIndex].td.Fs+0.5)
            wfList=[wf*WaveformTrimmer(0,wf.td.K-lengthSamples)
                for wf in wfList]
        # pragma: silent exclude
        self.TrimmedDenoisedDerivatives=copy.deepcopy(wfList)
        # pragma: silent include
        incwf=copy.deepcopy(wfList[incidentIndex])
        # pragma: silent exclude
        self.TrimmedDenoisedIncidentDesignated=copy.deepcopy(incwf)
        # pragma: silent include
        maxValueIndex=0
        maxValue=incwf[0]
        for k in range(1,len(incwf)):
            if incwf[k]>maxValue:
                maxValue=incwf[k]
                maxValueIndex=k
        forwardSamples=int(self.wfhwt*incwf.td.Fs)
        reverseSamples=int(self.wrhwt*incwf.td.Fs)
        raisedCosineSamples=int(self.wrcdr*incwf.td.Fs)
        (incidentExtractionWindow,reflectExtractionWindow)=self._ExtractionWindows(
            incwf.td,forwardSamples,reverseSamples,raisedCosineSamples,maxValueIndex)
        # pragma: silent exclude
        self.IncidentExtractionWindow=copy.deepcopy(incidentExtractionWindow)
        self.ReflectExtractionWindow=copy.deepcopy(reflectExtractionWindow)
        # pragma: silent include
        incwf=Waveform(incwf.td,[x*w 
            for (x,w) in zip(incwf.Values(),incidentExtractionWindow.Values())])
        wfList=[Waveform(wf.td,[x*w
            for (x,w) in zip(wf.Values(),reflectExtractionWindow.Values())])
                for wf in wfList]
        #wfList[incidentIndex]=wfList[incidentIndex]-incwf
        # pragma: silent exclude
        self.IncidentWaveform=copy.deepcopy(incwf)
        self.ReflectWaveforms=copy.deepcopy(wfList)
        # pragma: silent include    
        incwffc=incwf.FrequencyContent(self.fd)
        res=[wf.FrequencyContent(self.fd) for wf in wfList]
        # pragma: silent exclude
        self.IncidentFrequencyContent=copy.deepcopy(incwffc)
        self.ReflectFrequencyContent=copy.deepcopy(res)
        # pragma: silent include        
        for fc in res:
            for n in range(len(fc)):
                fc[n]=fc[n]/incwffc[n]
        # pragma: silent exclude
        if (len(res)==1) and (isinstance(wfListProvided,Waveform)):
            res=res[0]
        # pragma: include
        return res
    def _ExtractionWindows(self,td,forwardSamples,reverseSamples,
            raisedCosineSamples,maxValueIndex):
        incidentExtractionWindow=Waveform(td)
        reflectExtractionWindow=Waveform(td)
        for k in range(td.K):
            if k<maxValueIndex-reverseSamples-raisedCosineSamples:
                incidentExtractionWindow[k]=0.0
                reflectExtractionWindow[k]=0.0
            elif k<maxValueIndex-reverseSamples and raisedCosineSamples>0:
                si=k-(maxValueIndex-reverseSamples)
                f=float(si)/raisedCosineSamples
                incidentExtractionWindow[k]=(math.cos(f*math.pi)+1.)/2.
                reflectExtractionWindow[k]=0.0
            elif k<=maxValueIndex+forwardSamples:
                incidentExtractionWindow[k]=1.0
                reflectExtractionWindow[k]=0.0
            elif k<=maxValueIndex+forwardSamples+raisedCosineSamples and raisedCosineSamples>0:
                si=k-(maxValueIndex+forwardSamples)
                f=float(si)/raisedCosineSamples
                incidentExtractionWindow[k]=(math.cos(f*math.pi)+1.)/2.
                reflectExtractionWindow[k]=1.-incidentExtractionWindow[k]
            elif k>=td.K-1-raisedCosineSamples and raisedCosineSamples>0:
                si=k-(td.K-1-raisedCosineSamples)
                f=float(si)/raisedCosineSamples
                incidentExtractionWindow[k]=0.
                reflectExtractionWindow[k]=(math.cos(f*math.pi)+1.)/2.
            else:
                incidentExtractionWindow[k]=0.
                reflectExtractionWindow[k]=1.
        if not self.taper:
            reflectExtractionWindow=Waveform(td,[1.0-v for v in incidentExtractionWindow])
        return (incidentExtractionWindow,reflectExtractionWindow)