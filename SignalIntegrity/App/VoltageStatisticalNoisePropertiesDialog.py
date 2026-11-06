"""
VoltageStatisticalNoisePropertiesDialog.py
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

class VoltageStatisticalNoisePropertiesDialog(PropertiesDialog):
    NoiseTypeChoices=[('White Noise','WhiteNoise'),('Spectral Density File','SpectralDensityFile'),('Waveform File','WaveformFile'),('Crosstalk (From Probe)','Crosstalk')]
    WhiteNoiseTypeChoices=[('dBm/Hz','dBm/Hz'),('V/sqrt(Hz)','V/sqrt(Hz)'),('V^2/GHz (η0)','V^2/GHz'),('Vrms','Vrms'),('ENOB','ENOB'),('COM TX','COM TX'),('Johnson','Johnson')]
    def __init__(self,project,parent):
        PropertiesDialog.__init__(self,parent,project,parent.parent,'Voltage Statistical Noise Properties')
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
        self.Enable=CalculationPropertyTrueFalseButton(self.GeneralFrame,'Enable Noise',self.onUpdateFromChanges,None,self.project,'Enable',tooltip='Enable noise generation for this device')
        self.NoiseType=CalculationPropertyChoices(self.GeneralFrame,'Noise Type',self.onUpdateFromChanges,None,self.NoiseTypeChoices,self.project,'Type',tooltip="Allowed values: 'WhiteNoise', 'SpectralDensityFile', 'WaveformFile', or 'Crosstalk'.")
        self.Lanes=CalculationProperty(self.GeneralFrame,'Lanes',self.onUpdateFromChanges,None,self.project,'Lanes',tooltip='number of lanes of noise for this source')
        self.WhiteNoisePerLaneLabel = tk.Label(self.WhiteNoiseFrame, text='Per lane:')
        self.WhiteNoisePerLaneLabel.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        self.WhiteNoiseType=CalculationPropertyChoices(self.WhiteNoiseFrame,'White Noise Type',self.onUpdateFromChanges,None,self.WhiteNoiseTypeChoices,self.project,'WhiteNoise.WhiteNoiseType',tooltip="Allowed values: 'dBm/Hz', 'V/sqrt(Hz)', 'V^2/GHz', 'Vrms', 'ENOB', 'COM TX', or 'Johnson'.")
        self.NoisedBmPerHz=CalculationPropertySI(self.WhiteNoiseFrame,'Noise (dBm/Hz)',self.onNoisedBmPerHzChanged,None,self.project,'WhiteNoise.NoisedBmPerHz','dBm/Hz',round=3,tooltip='Noise density in dBm/Hz.')
        self.VPerRootHz=CalculationPropertySI(self.WhiteNoiseFrame,'Noise (V/sqrt(Hz))',self.onVPerRootHzChanged,None,self.project,'WhiteNoise.VPerRootHz','V/sqrt(Hz)',round=3,tooltip='Noise density in V/sqrt(Hz).')
        self.VSquaredPerGHz=CalculationPropertySI(self.WhiteNoiseFrame,'Noise (V^2/GHz (η0))',self.onVSquaredPerGHzChanged,None,self.project,'WhiteNoise.VSquaredPerGHz','V^2/GHz',round=3,tooltip='Noise density in V^2/GHz.')
        self.VRms=CalculationPropertySI(self.WhiteNoiseFrame,'Noise (Vrms)',self.onVRmsChanged,None,self.project,'WhiteNoise.VRms','Vrms',round=3,tooltip='Total noise in Vrms integrated over NoiseBandwidth (i.e., density in V/sqrt(Hz) * sqrt(NoiseBandwidth)).')
        self.ENOB=CalculationPropertySI(self.WhiteNoiseFrame,'ENOB',self.onENOBChanged,None,self.project,'WhiteNoise.SNR.ENOB.ENOB',round=6,tooltip='Effective number of bits used for COM RX noise specification.')
        self.Vpp=CalculationPropertySI(self.WhiteNoiseFrame,'Vpp',self.onVppChanged,None,self.project,'WhiteNoise.SNR.Vpp','V',round=6,tooltip='Peak-to-peak voltage used for COM TX/COM RX derived-noise calculations.')
        self.H0=CalculationPropertySI(self.WhiteNoiseFrame,'h0',self.onComTxParameterChanged,None,self.project,'WhiteNoise.SNR.COM_TX.h0',round=6,tooltip='COM TX FFE cursor tap height used to scale noise density.')
        self.SNRdB=CalculationPropertySI(self.WhiteNoiseFrame,'SNR',self.onComTxParameterChanged,None,self.project,'WhiteNoise.SNR.COM_TX.SNRdB','dB',round=6,tooltip='COM TX signal-to-noise ratio in dB used to derive noise.')
        self.Risetime=CalculationPropertySI(self.WhiteNoiseFrame,'Risetime (20-80)',self.onUpdateFromChanges,None,self.project,'WhiteNoise.SNR.COM_TX.Risetime','s',tooltip='COM TX transmitter 20-80 risetime in seconds used for Gaussian spectral shaping.')
        self.NoiseBandwidth=CalculationPropertySI(self.WhiteNoiseFrame,'Noise Bandwidth',self.onNoiseBandwidthChanged,None,self.project,'WhiteNoise.NoiseBandwidth','Hz',tooltip='Noise bandwidth in Hz used for Vrms integration and white-noise support.')
        self.JohnsonNoiseFrame=tk.Frame(self.WhiteNoiseFrame)
        self.Temperature=CalculationPropertySI(self.JohnsonNoiseFrame,'Temperature (K)',self.onJohnsonParameterChanged,None,self.project,'WhiteNoise.Johnson.Temperature_Kelvin','K',round=3,tooltip='Temperature in Kelvin (default: 25 C).')
        self.Resistance=CalculationPropertySI(self.JohnsonNoiseFrame,'Resistance (ohm)',self.onJohnsonParameterChanged,None,self.project,'WhiteNoise.Johnson.Resistance','ohm',round=3,tooltip='Resistance in ohms (default: 50 ohms).')
        self.SpectralDensityFilePerLaneLabel = tk.Label(self.SpectralDensityFileFrame, text='Per lane:')
        self.SpectralDensityFilePerLaneLabel.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        self.SpectralDensityFileName=CalculationPropertySpectralDensityFileName(self.SpectralDensityFileFrame,'Spectral Density File',self.onUpdateFromChanges,None,fp,self.project,'SpectralDensityFile.FileName',tooltip='Path to the spectral density file describing the noise')
        self.WaveformFilePerLaneLabel = tk.Label(self.WaveformFileFrame, text='Per lane:')
        self.WaveformFilePerLaneLabel.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        self.WaveformFileName=CalculationPropertyFileName(self.WaveformFileFrame,'Waveform File',self.onUpdateFromChanges,None,fp,self.project,'WaveformFile.FileName',tooltip='Path to the waveform file describing the noise')
        self.CrosstalkProbeName=CalculationProperty(self.CrosstalkFrame,'Probe Name',self.onUpdateFromChanges,None,self.project,'Crosstalk.ProbeName',tooltip='Output probe name to use as the crosstalk noise waveform source.')
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
        self.WhiteNoiseFrame.pack_forget()
        self.SpectralDensityFileFrame.pack_forget()
        self.WaveformFileFrame.pack_forget()
        self.CrosstalkFrame.pack_forget()
        self.JohnsonNoiseFrame.pack_forget()
        self.SaveToPreferencesFrame.pack_forget()
        self.NoiseType.Show(enable)
        self.Lanes.Show(enable)
        if enable:
            if noiseType=='WhiteNoise':
                self.WhiteNoiseFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
                if whiteNoiseType=='Johnson':
                    self.JohnsonNoiseFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            elif noiseType=='SpectralDensityFile':
                self.SpectralDensityFileFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            elif noiseType=='WaveformFile':
                self.WaveformFileFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            elif noiseType=='Crosstalk':
                self.CrosstalkFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.SaveToPreferencesFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        showWhiteNoiseControls = enable and noiseType=='WhiteNoise'
        self.WhiteNoiseType.Show(showWhiteNoiseControls)
        self.NoisedBmPerHz.Show(showWhiteNoiseControls and whiteNoiseType=='dBm/Hz')
        self.VPerRootHz.Show(showWhiteNoiseControls and whiteNoiseType=='V/sqrt(Hz)')
        self.VSquaredPerGHz.Show(showWhiteNoiseControls and whiteNoiseType=='V^2/GHz')
        self.VRms.Show(showWhiteNoiseControls and whiteNoiseType=='Vrms')
        self.ENOB.Show(showWhiteNoiseControls and whiteNoiseType=='ENOB')
        self.Vpp.Show(showWhiteNoiseControls and whiteNoiseType in ['ENOB','COM TX'])
        self.H0.Show(showWhiteNoiseControls and whiteNoiseType=='COM TX')
        self.SNRdB.Show(showWhiteNoiseControls and whiteNoiseType=='COM TX')
        self.Risetime.Show(showWhiteNoiseControls and whiteNoiseType=='COM TX')
        self.Temperature.Show(showWhiteNoiseControls and whiteNoiseType=='Johnson')
        self.Resistance.Show(showWhiteNoiseControls and whiteNoiseType=='Johnson')
        self.NoiseBandwidth.Show(showWhiteNoiseControls)
    def onSaveToPreferences(self):
        self.parent.device.configuration.SaveToPreferences()
    def _noiseVrmsFromENOB(self):
        bw = self.project['WhiteNoise.NoiseBandwidth']
        if bw is None or bw <= 0:
            return None
        vpp = self.project['WhiteNoise.SNR.Vpp']
        if vpp is None or vpp <= 0:
            return None
        enob = self.project['WhiteNoise.SNR.ENOB.ENOB']
        snr_db = 6.02 * enob + 1.76
        signal_vrms = vpp / (2.0 * math.sqrt(2.0))
        return signal_vrms / (10.0 ** (snr_db / 20.0))

    def _updateENOBFromVrms(self, noise_vrms):
        vpp = self.project['WhiteNoise.SNR.Vpp']
        if noise_vrms is None or noise_vrms <= 0 or vpp is None or vpp <= 0:
            return
        signal_vrms = vpp / (2.0 * math.sqrt(2.0))
        if signal_vrms <= 0:
            return
        snr_db = 20.0 * math.log10(signal_vrms / noise_vrms)
        self.project['WhiteNoise.SNR.ENOB.ENOB'] = (snr_db - 1.76) / 6.02
        self.ENOB.UpdateStrings()

    def _noiseVrmsFromComTx(self):
        return self.project['WhiteNoise.SNR.COM_TX.h0'] * self.project['WhiteNoise.SNR.Vpp'] / 2.0 * (
            10.0 ** (-self.project['WhiteNoise.SNR.COM_TX.SNRdB'] / 20.0)
        )

    def _noiseVPerRootHzFromJohnson(self):
        import scipy.constants as const
        temperature = self.project['WhiteNoise.Johnson.Temperature_Kelvin']
        resistance = self.project['WhiteNoise.Johnson.Resistance']
        if temperature is None or resistance is None:
            return None
        if temperature < 0 or resistance < 0:
            return None
        return math.sqrt(4.0 * const.k * temperature * resistance)

    def _propagateJohnson(self):
        value = self._noiseVPerRootHzFromJohnson()
        if value is None:
            return
        self.project['WhiteNoise.VPerRootHz'] = value
        self.VPerRootHz.UpdateStrings()
        self._propagateFrom('V/sqrt(Hz)')

    def _updateComTxFromVrms(self, noise_vrms):
        h0 = self.project['WhiteNoise.SNR.COM_TX.h0']
        vpp = self.project['WhiteNoise.SNR.Vpp']
        if noise_vrms is None or noise_vrms <= 0 or h0 is None or h0 <= 0 or vpp is None or vpp <= 0:
            return
        full_scale = h0 * vpp / 2.0
        if full_scale <= 0:
            return
        self.project['WhiteNoise.SNR.COM_TX.SNRdB'] = 20.0 * math.log10(full_scale / noise_vrms)
        self.SNRdB.UpdateStrings()

    def _propagateFrom(self, source_units):
        """Recompute the two non-source noise-level fields from the source field
        using DFTUtilities.ConvertSpectralDensity. Conversions involving 'Vrms'
        are skipped if NoiseBandwidth is not a positive number."""
        from SignalIntegrity.Lib.FrequencyDomain.DFTUtilities import DFTUtilities
        fields = {
            'dBm/Hz':     ('WhiteNoise.NoisedBmPerHz', self.NoisedBmPerHz),
            'V/sqrt(Hz)': ('WhiteNoise.VPerRootHz',    self.VPerRootHz),
            'V^2/GHz':    ('WhiteNoise.VSquaredPerGHz',self.VSquaredPerGHz),
            'Vrms':       ('WhiteNoise.VRms',          self.VRms),
        }
        if source_units == 'ENOB':
            value = self._noiseVrmsFromENOB()
            if value is None:
                return
            self.project['WhiteNoise.VRms'] = value
            self.VRms.UpdateStrings()
            source_units = 'Vrms'
        if source_units == 'COM TX':
            value = self._noiseVrmsFromComTx()
            self.project['WhiteNoise.VRms'] = value
            self.VRms.UpdateStrings()
            source_units = 'Vrms'
        src_key, _ = fields[source_units]
        value = self.project[src_key]
        bw = self.project['WhiteNoise.NoiseBandwidth']
        for to_units, (key, widget) in fields.items():
            if to_units == source_units:
                continue
            needs_bw = (source_units == 'Vrms' or to_units == 'Vrms')
            if needs_bw and (bw is None or bw <= 0):
                continue  # cannot convert without a valid bandwidth
            try:
                converted = DFTUtilities.ConvertSpectralDensity(
                    value, source_units, to_units, bw=bw)
            except (ValueError, ZeroDivisionError):
                continue  # leave stale value rather than crash the UI
            self.project[key] = converted
            widget.UpdateStrings()
        self._updateENOBFromVrms(self.project['WhiteNoise.VRms'])
        self._updateComTxFromVrms(self.project['WhiteNoise.VRms'])

    def onJohnsonParameterChanged(self, _):
        self._propagateJohnson()
        self.UpdateStrings()

    def onNoisedBmPerHzChanged(self, _):
        self._propagateFrom('dBm/Hz')
        self.UpdateStrings()

    def onVPerRootHzChanged(self, _):
        self._propagateFrom('V/sqrt(Hz)')
        self.UpdateStrings()

    def onVRmsChanged(self, _):
        self._propagateFrom('Vrms')
        self.UpdateStrings()

    def onVSquaredPerGHzChanged(self, _):
        self._propagateFrom('V^2/GHz')
        self.UpdateStrings()

    def onENOBChanged(self, _):
        self._propagateFrom('ENOB')
        self.UpdateStrings()

    def onVppChanged(self, _):
        whiteNoiseType = self.project['WhiteNoise.WhiteNoiseType']
        if whiteNoiseType == 'COM TX':
            self._propagateFrom('COM TX')
        else:
            self._propagateFrom('ENOB')
        self.UpdateStrings()

    def onComTxParameterChanged(self, _):
        self._propagateFrom('COM TX')
        self.UpdateStrings()

    def onNoiseBandwidthChanged(self, _):
        # Treat NoiseBandwidth as an input; rebuild the other two level fields
        # from whichever level is currently selected as the specification.
        whiteNoiseType = self.project['WhiteNoise.WhiteNoiseType']
        if whiteNoiseType == 'Johnson':
            self._propagateJohnson()
        elif whiteNoiseType in ('dBm/Hz', 'V/sqrt(Hz)', 'V^2/GHz', 'Vrms', 'ENOB', 'COM TX'):
            self._propagateFrom(whiteNoiseType)
        self.UpdateStrings()
