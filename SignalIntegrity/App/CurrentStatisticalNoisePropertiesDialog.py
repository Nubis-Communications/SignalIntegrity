"""
CurrentStatisticalNoisePropertiesDialog.py
"""

# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# Copyright (c) 2021-2025 Nubis Communications, Inc.
# Copyright (c) 2026 Ciena, Inc.
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
import os
import math

from SignalIntegrity.App.CalculationPropertiesProject import PropertiesDialog,CalculationPropertyTrueFalseButton,CalculationPropertyChoices,CalculationPropertySI,CalculationProperty,CalculationPropertyFileName,CalculationPropertySpectralDensityFileName
import SignalIntegrity.App.Project
from SignalIntegrity.App.Files import FileParts

class CurrentStatisticalNoisePropertiesDialog(PropertiesDialog):
    NoiseTypeChoices=[('White Noise','WhiteNoise'),('Spectral Density File','SpectralDensityFile'),('Waveform File','WaveformFile'),('Crosstalk (From Probe)','Crosstalk'),('Shot Noise','ShotNoise')]
    WhiteNoiseTypeChoices=[('dBm/Hz','dBm/Hz'),('A/sqrt(Hz)','A/sqrt(Hz)'),('A^2/GHz','A^2/GHz'),('Arms','Arms')]
    ShotNoiseCurrentSourceChoices=[('Mean','Mean'),('Time-Varying Current','TimeVarying')]
    def __init__(self,project,parent):
        PropertiesDialog.__init__(self,parent,project,parent.parent,'Current Statistical Noise Properties')
        self.transient(parent)
        fp=FileParts(os.getcwd())
        self.GeneralFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.GeneralFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.WhiteNoiseFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.WhiteNoiseFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.SpectralDensityFileFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.SpectralDensityFileFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.WaveformFileFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.WaveformFileFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.CrosstalkFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.CrosstalkFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.ShotNoiseFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.ShotNoiseFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.Enable=CalculationPropertyTrueFalseButton(self.GeneralFrame,'Enable Noise',self.onUpdateFromChanges,None,self.project,'Enable',tooltip='Enable noise generation for this device')
        self.NoiseType=CalculationPropertyChoices(self.GeneralFrame,'Noise Type',self.onUpdateFromChanges,None,self.NoiseTypeChoices,self.project,'Type',tooltip="Allowed values: 'WhiteNoise', 'SpectralDensityFile', 'WaveformFile', or 'Crosstalk'.")
        self.Lanes=CalculationProperty(self.GeneralFrame,'Lanes',self.onUpdateFromChanges,None,self.project,'Lanes',tooltip='number of lanes of noise for this source')
        self.WhiteNoisePerLaneLabel = tk.Label(self.WhiteNoiseFrame, text='Per lane:')
        self.WhiteNoisePerLaneLabel.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        self.WhiteNoiseType=CalculationPropertyChoices(self.WhiteNoiseFrame,'White Noise Type',self.onUpdateFromChanges,None,self.WhiteNoiseTypeChoices,self.project,'WhiteNoise.WhiteNoiseType',tooltip="Allowed values: 'dBm/Hz', 'A/sqrt(Hz)', 'A^2/GHz', or 'Arms'.")
        self.NoisedBmPerHz=CalculationPropertySI(self.WhiteNoiseFrame,'Noise (dBm/Hz)',self.onNoisedBmPerHzChanged,None,self.project,'WhiteNoise.NoisedBmPerHz','dBm/Hz',round=3,tooltip='Noise density in dBm/Hz.')
        self.APerRootHz=CalculationPropertySI(self.WhiteNoiseFrame,'Noise (A/sqrt(Hz))',self.onAPerRootHzChanged,None,self.project,'WhiteNoise.APerRootHz','A/sqrt(Hz)',round=3,tooltip='Noise density in A/sqrt(Hz).')
        self.ASquaredPerGHz=CalculationPropertySI(self.WhiteNoiseFrame,'Noise (A^2/GHz)',self.onASquaredPerGHzChanged,None,self.project,'WhiteNoise.ASquaredPerGHz','A^2/GHz',round=3,tooltip='Noise density in A^2/GHz.')
        self.ARms=CalculationPropertySI(self.WhiteNoiseFrame,'Noise (Arms)',self.onARmsChanged,None,self.project,'WhiteNoise.ARms','Arms',round=3,tooltip='Total noise in Arms integrated over NoiseBandwidth (i.e., density in A/sqrt(Hz) * sqrt(NoiseBandwidth)).')
        self.NoiseBandwidth=CalculationPropertySI(self.WhiteNoiseFrame,'Noise Bandwidth',self.onNoiseBandwidthChanged,None,self.project,'WhiteNoise.NoiseBandwidth','Hz',tooltip='Noise bandwidth in Hz used for Arms integration and white-noise support.')
        self.SpectralDensityFilePerLaneLabel = tk.Label(self.SpectralDensityFileFrame, text='Per lane:')
        self.SpectralDensityFilePerLaneLabel.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        self.SpectralDensityFileName=CalculationPropertySpectralDensityFileName(self.SpectralDensityFileFrame,'Spectral Density File',self.onUpdateFromChanges,None,fp,self.project,'SpectralDensityFile.FileName',tooltip='Path to the spectral density file describing the noise')
        self.WaveformFilePerLaneLabel = tk.Label(self.WaveformFileFrame, text='Per lane:')
        self.WaveformFilePerLaneLabel.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        self.WaveformFileName=CalculationPropertyFileName(self.WaveformFileFrame,'Waveform File',self.onUpdateFromChanges,None,fp,self.project,'WaveformFile.FileName',tooltip='Path to the waveform file describing the noise')
        self.CrosstalkProbeName=CalculationProperty(self.CrosstalkFrame,'Probe Name',self.onUpdateFromChanges,None,self.project,'Crosstalk.ProbeName',tooltip='Output probe name to use as the crosstalk noise waveform source.')
        self.ShotNoiseCurrentSource=CalculationPropertyChoices(self.ShotNoiseFrame,'Current Source',self.onUpdateFromChanges,None,self.ShotNoiseCurrentSourceChoices,self.project,'ShotNoise.CurrentSource',tooltip='Mean or time-varying current used to build the shot-noise spectral density.')
        self.ShotNoiseMeanCurrent=CalculationPropertySI(self.ShotNoiseFrame,'Mean (steady-state) Current',self.onUpdateFromChanges,None,self.project,'ShotNoise.MeanCurrent','A',round=3,tooltip='Mean (steady-state) current in amperes.  For time-varying mode this is recomputed as the equivalent steady-state current after analysis.')
        self.ShotNoiseProbeName=CalculationProperty(self.ShotNoiseFrame,'Probe Name',self.onUpdateFromChanges,None,self.project,'ShotNoise.ProbeName',tooltip='Current output probe name whose time-varying current shapes the shot-noise spectral density.')
        self.ShotNoiseBandwidth=CalculationPropertySI(self.ShotNoiseFrame,'Noise Bandwidth',self.onUpdateFromChanges,None,self.project,'ShotNoise.NoiseBandwidth','Hz',tooltip='Noise bandwidth in Hz used to integrate the shot-noise spectral density.')
        self.SaveToPreferencesFrame=tk.Frame(self.propertyListFrame,relief=tk.RIDGE, borderwidth=5)
        self.SaveToPreferencesFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.SaveToPreferencesButton = tk.Button(self.SaveToPreferencesFrame,text='Save Properties to Global Preferences',command=self.onSaveToPreferences,width=CalculationProperty.labelWidth)
        self.SaveToPreferencesButton.pack(side=tk.TOP,expand=tk.YES)
        self.Finish()
    def Finish(self):
        self.UpdateStrings()
        PropertiesDialog.Finish(self)
    def onUpdateFromChanges(self,_):
        self.UpdateStrings()
    def UpdateStrings(self):
        enable=self.project['Enable']
        noiseType=self.project['Type']
        whiteNoiseType=self.project['WhiteNoise.WhiteNoiseType']
        shotNoiseCurrentSource=self.project['ShotNoise.CurrentSource']
        self.WhiteNoiseFrame.pack_forget()
        self.SpectralDensityFileFrame.pack_forget()
        self.WaveformFileFrame.pack_forget()
        self.CrosstalkFrame.pack_forget()
        self.ShotNoiseFrame.pack_forget()
        self.SaveToPreferencesFrame.pack_forget()
        self.NoiseType.Show(enable)
        self.Lanes.Show(enable)
        if enable:
            if noiseType=='WhiteNoise':
                self.WhiteNoiseFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            elif noiseType=='SpectralDensityFile':
                self.SpectralDensityFileFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            elif noiseType=='WaveformFile':
                self.WaveformFileFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            elif noiseType=='Crosstalk':
                self.CrosstalkFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            elif noiseType=='ShotNoise':
                self.ShotNoiseFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.SaveToPreferencesFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        showWhiteNoiseControls = enable and noiseType=='WhiteNoise'
        self.WhiteNoiseType.Show(showWhiteNoiseControls)
        self.NoisedBmPerHz.Show(showWhiteNoiseControls and whiteNoiseType=='dBm/Hz')
        self.APerRootHz.Show(showWhiteNoiseControls and whiteNoiseType=='A/sqrt(Hz)')
        self.ASquaredPerGHz.Show(showWhiteNoiseControls and whiteNoiseType=='A^2/GHz')
        self.ARms.Show(showWhiteNoiseControls and whiteNoiseType=='Arms')
        self.NoiseBandwidth.Show(showWhiteNoiseControls)
        showShotNoiseControls = enable and noiseType=='ShotNoise'
        self.ShotNoiseCurrentSource.Show(showShotNoiseControls)
        self.ShotNoiseMeanCurrent.Show(showShotNoiseControls)
        self.ShotNoiseProbeName.Show(showShotNoiseControls and shotNoiseCurrentSource=='TimeVarying')
        self.ShotNoiseBandwidth.Show(showShotNoiseControls)
    def onSaveToPreferences(self):
        self.parent.device.configuration.SaveToPreferences()

    def _propagateFrom(self, source_units):
        """Recompute the non-source noise-level fields from the source field
        using DFTUtilities.ConvertSpectralDensity with a current reference.
        Conversions involving 'Arms' are skipped if NoiseBandwidth is not a
        positive number."""
        from SignalIntegrity.Lib.FrequencyDomain.DFTUtilities import DFTUtilities
        fields = {
            'dBm/Hz':     ('WhiteNoise.NoisedBmPerHz', self.NoisedBmPerHz),
            'A/sqrt(Hz)': ('WhiteNoise.APerRootHz',    self.APerRootHz),
            'A^2/GHz':    ('WhiteNoise.ASquaredPerGHz',self.ASquaredPerGHz),
            'Arms':       ('WhiteNoise.ARms',          self.ARms),
        }
        src_key, _ = fields[source_units]
        value = self.project[src_key]
        bw = self.project['WhiteNoise.NoiseBandwidth']
        for to_units, (key, widget) in fields.items():
            if to_units == source_units:
                continue
            needs_bw = (source_units == 'Arms' or to_units == 'Arms')
            if needs_bw and (bw is None or bw <= 0):
                continue  # cannot convert without a valid bandwidth
            try:
                converted = DFTUtilities.ConvertSpectralDensity(
                    value, source_units, to_units, bw=bw, reference='current')
            except (ValueError, ZeroDivisionError):
                continue  # leave stale value rather than crash the UI
            self.project[key] = converted
            widget.UpdateStrings()

    def onNoisedBmPerHzChanged(self, _):
        self._propagateFrom('dBm/Hz')
        self.UpdateStrings()

    def onAPerRootHzChanged(self, _):
        self._propagateFrom('A/sqrt(Hz)')
        self.UpdateStrings()

    def onARmsChanged(self, _):
        self._propagateFrom('Arms')
        self.UpdateStrings()

    def onASquaredPerGHzChanged(self, _):
        self._propagateFrom('A^2/GHz')
        self.UpdateStrings()

    def onNoiseBandwidthChanged(self, _):
        # Treat NoiseBandwidth as an input; rebuild the other level fields
        # from whichever level is currently selected as the specification.
        whiteNoiseType = self.project['WhiteNoise.WhiteNoiseType']
        if whiteNoiseType in ('dBm/Hz', 'A/sqrt(Hz)', 'A^2/GHz', 'Arms'):
            self._propagateFrom(whiteNoiseType)
        self.UpdateStrings()
