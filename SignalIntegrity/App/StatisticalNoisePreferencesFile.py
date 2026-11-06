"""
StatisticalNoisePreferencesFile.py
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
from SignalIntegrity.App.ProjectFileBase import XMLConfiguration,XMLPropertyDefaultString,XMLPropertyDefaultInt,XMLPropertyDefaultBool,XMLPropertyDefaultFloat,XMLPropertyDefaultFile
import math

class COM_TXConfiguration(XMLConfiguration):
    def __init__(self, parent=None):
        super().__init__('COM_TX')
        self.parent = parent
        self.Add(XMLPropertyDefaultFloat('h0', 1.0))       # COM TX FFE cursor tap height used to scale noise density.
        self.Add(XMLPropertyDefaultFloat('SNRdB', 33.0))   # COM TX signal-to-noise ratio in dB used to derive noise.
        self.Add(XMLPropertyDefaultFloat('Risetime', 0.0)) # COM TX transmitter 20-80 risetime in seconds used for Gaussian spectral shaping.

    def NoiseBandwidth(self):
        if self.parent is not None:
            return self.parent.NoiseBandwidth()
        return None

    def Vpp(self):
        if self.parent is not None:
            return self.parent['Vpp']
        return None

    def noiseVrms(self):
        return self['h0'] * self.Vpp() / 2.0 * (10.0 ** (-self['SNRdB'] / 20.0))

class ENOBConfiguration(XMLConfiguration):
    def __init__(self, parent=None):
        super().__init__('ENOB')
        self.parent = parent
        self.Add(XMLPropertyDefaultFloat('ENOB', 0.0))  # Effective number of bits used for COM RX noise specification.

    def NoiseBandwidth(self):
        if self.parent is not None:
            return self.parent.NoiseBandwidth()
        return None

    def Vpp(self):
        if self.parent is not None:
            return self.parent['Vpp']
        return None

class SNRConfiguration(XMLConfiguration):
    def __init__(self, parent=None):
        super().__init__('SNR')
        self.parent = parent
        self.Add(XMLPropertyDefaultFloat('Vpp', 1.0))   # Peak-to-peak voltage used for COM TX/COM RX derived-noise calculations.
        self.SubDir(ENOBConfiguration(parent=self))
        self.SubDir(COM_TXConfiguration(parent=self))

    def NoiseBandwidth(self):
        if self.parent is not None:
            return self.parent['NoiseBandwidth']
        return None

class JohnsonNoiseConfiguration(XMLConfiguration):
    def __init__(self, parent=None):
        super().__init__('Johnson')
        self.parent = parent
        self.Add(XMLPropertyDefaultFloat('Temperature_Kelvin', 298.15)) # Temperature in Kelvin (default: 25 C).
        self.Add(XMLPropertyDefaultFloat('Resistance', 50.0))           # Resistance in ohms (default: 50 ohms).

    def NoiseDensity(self):
        import scipy.constants as const
        k_B = const.k
        return math.sqrt(4.0 * k_B * self['Temperature_Kelvin'] * self['Resistance'])

    def NoiseBandwidth(self):
        if self.parent is not None:
            return self.parent['NoiseBandwidth']
        return None

    def SpectralDensity(self, EndFrequency, FrequencyPoints):
        from SignalIntegrity.Lib.FrequencyDomain.SpectralDensity import SpectralDensity
        from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
        fl = EvenlySpacedFrequencyList(EndFrequency, FrequencyPoints)
        noiseDensity = self.NoiseDensity()
        noiseBandwidth = self.NoiseBandwidth()
        return SpectralDensity(
            fl,
            [0.0 if (f == 0.0 or f > noiseBandwidth) else noiseDensity for f in fl])

class VoltageWhiteNoiseConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('WhiteNoise')
        self.Add(XMLPropertyDefaultString('WhiteNoiseType','V/sqrt(Hz)')) # Allowed values: 'dBm/Hz', 'V/sqrt(Hz)', 'V^2/GHz', 'Vrms', 'ENOB', 'COM TX', or 'Johnson'.
        self.Add(XMLPropertyDefaultFloat('NoisedBmPerHz',0.0)) # Noise density in dBm/Hz.
        self.Add(XMLPropertyDefaultFloat('VPerRootHz',0.0))    # Noise density in V/sqrt(Hz).
        self.Add(XMLPropertyDefaultFloat('VSquaredPerGHz',0.0))# Noise density in V^2/GHz.
        self.Add(XMLPropertyDefaultFloat('VRms',0.0))          # Total noise in Vrms integrated over NoiseBandwidth (i.e., density in V/sqrt(Hz) * sqrt(NoiseBandwidth)).
        self.Add(XMLPropertyDefaultFloat('NoiseBandwidth',0.0))# Noise bandwidth in Hz used for Vrms integration and white-noise support.
        self.SubDir(SNRConfiguration(parent=self))
        self.SubDir(JohnsonNoiseConfiguration(parent=self))

    def _noiseVrmsFromComTx(self):
        return self['SNR.COM_TX'].noiseVrms()

    def NoiseDensity(self):
        from SignalIntegrity.Lib.FrequencyDomain.DFTUtilities import DFTUtilities
        spec_type = self['WhiteNoiseType']
        bw = self['NoiseBandwidth']
        if spec_type == 'dBm/Hz':
            value = self['NoisedBmPerHz']
        elif spec_type == 'V/sqrt(Hz)':
            value = self['VPerRootHz']
        elif spec_type == 'V^2/GHz':
            value = self['VSquaredPerGHz']
        elif spec_type == 'Vrms':
            value = self['VRms']
        elif spec_type == 'ENOB':
            if bw is None or bw <= 0:
                raise ValueError('NoiseBandwidth must be > 0 for ENOB specification')
            vpp = self['SNR.Vpp']
            enob = self['SNR.ENOB.ENOB']
            snr_db = 6.02 * enob + 1.76
            signal_vrms = vpp / (2.0 * math.sqrt(2.0))
            value = signal_vrms / (10.0 ** (snr_db / 20.0))
            spec_type = 'Vrms'
        elif spec_type == 'COM TX':
            if bw is None or bw <= 0:
                raise ValueError('NoiseBandwidth must be > 0 for COM TX specification')
            value = self._noiseVrmsFromComTx()
            spec_type = 'Vrms'
        elif spec_type == 'Johnson':
            value = self['Johnson'].NoiseDensity()
            spec_type = 'V/sqrt(Hz)'
        else:
            raise ValueError(f'Unknown WhiteNoiseType: {spec_type}')
        return DFTUtilities.ConvertSpectralDensity(
            value, spec_type, 'V/sqrt(Hz)', bw=bw)

    def SpectralDensity(self, EndFrequency, FrequencyPoints):
        from SignalIntegrity.Lib.FrequencyDomain.SpectralDensity import SpectralDensity
        from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
        fl = EvenlySpacedFrequencyList(EndFrequency, FrequencyPoints)
        noiseDensity = self.NoiseDensity()
        noiseBandwidth = self['NoiseBandwidth']
        spec_type = self['WhiteNoiseType']
        if spec_type == 'COM TX':
            from SignalIntegrity.Lib.TimeDomain.Filters.Risetime.Gaussian import Gaussian
            risetime = self['SNR.COM_TX.Risetime']
            density = []
            for f in fl:
                if f == 0.0 or f > noiseBandwidth:
                    density.append(0.0)
                elif risetime is None or risetime <= 0.0:
                    density.append(noiseDensity)
                else:
                    density.append(noiseDensity * math.exp(-2.0 * (math.pi * f * risetime / Gaussian.a2080) ** 2))
            return SpectralDensity(fl, density)
        return SpectralDensity(
            fl,
            [0.0 if (f == 0.0 or f > noiseBandwidth) else noiseDensity for f in fl])

class CurrentWhiteNoiseConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('WhiteNoise')
        self.Add(XMLPropertyDefaultString('WhiteNoiseType','A/sqrt(Hz)')) # Allowed values: 'dBm/Hz', 'A/sqrt(Hz)', 'A^2/GHz', or 'Arms'.
        self.Add(XMLPropertyDefaultFloat('NoisedBmPerHz',0.0)) # Noise density in dBm/Hz.
        self.Add(XMLPropertyDefaultFloat('APerRootHz',0.0))    # Noise density in A/sqrt(Hz).
        self.Add(XMLPropertyDefaultFloat('ASquaredPerGHz',0.0))# Noise density in A^2/GHz.
        self.Add(XMLPropertyDefaultFloat('ARms',0.0))          # Total noise in Arms integrated over NoiseBandwidth (i.e., density in A/sqrt(Hz) * sqrt(NoiseBandwidth)).
        self.Add(XMLPropertyDefaultFloat('NoiseBandwidth',0.0))# Noise bandwidth in Hz used for Arms integration and white-noise support.

    def NoiseDensity(self):
        from SignalIntegrity.Lib.FrequencyDomain.DFTUtilities import DFTUtilities
        spec_type = self['WhiteNoiseType']
        bw = self['NoiseBandwidth']
        if spec_type == 'dBm/Hz':
            value = self['NoisedBmPerHz']
        elif spec_type == 'A/sqrt(Hz)':
            value = self['APerRootHz']
        elif spec_type == 'A^2/GHz':
            value = self['ASquaredPerGHz']
        elif spec_type == 'Arms':
            value = self['ARms']
        else:
            raise ValueError(f'Unknown WhiteNoiseType: {spec_type}')
        return DFTUtilities.ConvertSpectralDensity(
            value, spec_type, 'A/sqrt(Hz)', bw=bw, reference='current')

    def SpectralDensity(self, EndFrequency, FrequencyPoints):
        from SignalIntegrity.Lib.FrequencyDomain.SpectralDensity import SpectralDensity
        from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
        fl = EvenlySpacedFrequencyList(EndFrequency, FrequencyPoints)
        noiseDensity = self.NoiseDensity()
        noiseBandwidth = self['NoiseBandwidth']
        return SpectralDensity(
            fl,
            [0.0 if (f == 0.0 or f > noiseBandwidth) else noiseDensity for f in fl])

class ShotNoiseConfiguration(XMLConfiguration):
    """Shot noise spectral density for a current noise source.

    Shot noise has a (white) power spectral density S_i(f) = 2*q*I amperes^2/Hz,
    where q is the electron charge and I is the current.  The equivalent
    amplitude spectral density is rho(f) = sqrt(2*q*I) in A/sqrt(Hz).

    Two ways of building the density are supported, selected by 'CurrentSource':
    - 'Mean' : a flat (white) density sqrt(2*q*I) built from the entered
      'MeanCurrent' (the steady-state current).
    - 'TimeVarying' : a colored/shaped density derived from a referenced current
      output probe waveform.  The white shot-noise level of the waveform's mean
      current is shaped by the waveform's own (normalized) spectrum, then the
      equivalent steady-state current that would produce the same total rms over
      the noise bandwidth is written back into 'MeanCurrent'.
    """
    def __init__(self, parent=None):
        super().__init__('ShotNoise')
        self.parent = parent
        self.Add(XMLPropertyDefaultString('CurrentSource','Mean')) # 'Mean' (entered steady-state current) or 'TimeVarying' (from a current probe waveform).
        self.Add(XMLPropertyDefaultFloat('MeanCurrent',0.0))       # Mean (steady-state) current in amperes.
        self.Add(XMLPropertyDefaultString('ProbeName',''))         # Current output probe name used for the time-varying current.
        self.Add(XMLPropertyDefaultFloat('NoiseBandwidth',0.0))    # Noise bandwidth in Hz used to integrate the shot-noise density.

    def SpectralDensity(self, EndFrequency, FrequencyPoints,
                        output_waveforms=None, output_waveform_names=None, output_types=None):
        import scipy.constants as const
        from SignalIntegrity.Lib.FrequencyDomain.SpectralDensity import SpectralDensity
        from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
        q = const.e
        fl = EvenlySpacedFrequencyList(EndFrequency, FrequencyPoints)
        noiseBandwidth = self['NoiseBandwidth']
        currentSource = self['CurrentSource']
        probe_name = self['ProbeName']

        useTimeVarying = (currentSource == 'TimeVarying'
                          and probe_name is not None and probe_name != '')

        if useTimeVarying:
            # An explicitly named probe must exist and must be a current probe.
            if output_waveform_names is None or probe_name not in output_waveform_names:
                raise ValueError(
                    "shot noise current probe '%s' was not found among the output probes"%probe_name)
            if output_types is not None and output_types.get(probe_name,'voltage') != 'current':
                raise ValueError(
                    "shot noise probe '%s' is not a current probe (its units must be amperes)"%probe_name)
            waveform = output_waveforms[output_waveform_names.index(probe_name)]
            values = waveform.Values()
            meanCurrent = abs(sum(values)/len(values)) if len(values) > 0 else 0.0
            # The current waveform's own amplitude spectrum provides the shape.
            currentShape = waveform.SpectralDensity(fl).Values()
            inBandShape = [v for f,v in zip(fl,currentShape)
                           if f != 0.0 and f <= noiseBandwidth]
            refLevel = max(inBandShape) if len(inBandShape) > 0 else 0.0
            whiteLevel = math.sqrt(2.0*q*meanCurrent)
            if refLevel <= 0.0:
                density = [0.0 if (f == 0.0 or f > noiseBandwidth) else whiteLevel
                           for f in fl]
            else:
                density = [0.0 if (f == 0.0 or f > noiseBandwidth)
                           else whiteLevel*(shape/refLevel)
                           for f,shape in zip(fl,currentShape)]
            shotSD = SpectralDensity(fl, density)
            # Write back the equivalent steady-state current that would produce
            # this total rms as a flat white shot-noise density over the band.
            rms = shotSD.TotalRMS()
            if noiseBandwidth > 0:
                self['MeanCurrent'] = rms*rms/(2.0*q*noiseBandwidth)
            return shotSD

        # 'Mean' mode (or an empty/None probe name): flat shot-noise density from
        # the entered steady-state current.
        meanCurrent = abs(self['MeanCurrent'])
        whiteLevel = math.sqrt(2.0*q*meanCurrent)
        return SpectralDensity(
            fl,
            [0.0 if (f == 0.0 or f > noiseBandwidth) else whiteLevel for f in fl])

class SpectralDensityFileConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('SpectralDensityFile')
        self.Add(XMLPropertyDefaultFile('FileName',''))
    def SpectralDensity(self, EndFrequency, FrequencyPoints):
        from SignalIntegrity.Lib.FrequencyDomain.SpectralDensity import SpectralDensity
        from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
        fl = EvenlySpacedFrequencyList(EndFrequency, FrequencyPoints)
        return SpectralDensity().ReadFromFile(self['FileName']).Resample(fl)

class NoiseWaveformFileConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('WaveformFile')
        self.Add(XMLPropertyDefaultFile('FileName',''))
    def SpectralDensity(self, EndFrequency, FrequencyPoints):
        from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
        from SignalIntegrity.Lib.TimeDomain.Waveform import Waveform
        fl  = EvenlySpacedFrequencyList(EndFrequency, FrequencyPoints)
        wf = Waveform().ReadFromFile(self['FileName'])
        return wf.SpectralDensity(fl)

class CrosstalkNoiseFromProbeConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('Crosstalk')
        self.Add(XMLPropertyDefaultString('ProbeName',''))
    def SpectralDensity(self, EndFrequency, FrequencyPoints, output_waveforms=None, output_waveform_names=None):
        from SignalIntegrity.Lib.FrequencyDomain.SpectralDensity import SpectralDensity
        from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
        fl = EvenlySpacedFrequencyList(EndFrequency, FrequencyPoints)
        if output_waveforms is None or output_waveform_names is None:
            return SpectralDensity(fl, [0.0 for _ in fl])
        probe_name = self['ProbeName']
        if probe_name in output_waveform_names:
            waveform = output_waveforms[output_waveform_names.index(probe_name)]
            return waveform.SpectralDensity(fl)
        return SpectralDensity(fl, [0.0 for _ in fl])

class VoltageNoiseConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('VoltageNoise')
        self.Add(XMLPropertyDefaultBool('Enable',False))
        self.Add(XMLPropertyDefaultString('Type','WhiteNoise')) # 'WhiteNoise', 'SpectralDensityFile', 'WaveformFile', or 'Crosstalk' (legacy 'Johnson' is still accepted)
        self.SubDir(VoltageWhiteNoiseConfiguration())
        self.SubDir(SpectralDensityFileConfiguration())
        self.SubDir(NoiseWaveformFileConfiguration())
        self.SubDir(CrosstalkNoiseFromProbeConfiguration())
        self.Add(XMLPropertyDefaultFloat('Lanes',1.0))
    def SpectralDensity(self, EndFrequency, FrequencyPoints, output_waveforms=None, output_waveform_names=None, output_types=None):
        from SignalIntegrity.Lib.FrequencyDomain.SpectralDensity import SpectralDensity
        from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
        import math
        fl = EvenlySpacedFrequencyList(EndFrequency, FrequencyPoints)
        if not self['Enable']:
            return SpectralDensity(fl, [0.0 for _ in fl])
        noiseType = self['Type']
        lanes = self['Lanes']
        if noiseType == 'WhiteNoise':
            return self['WhiteNoise'].SpectralDensity(EndFrequency, FrequencyPoints)*math.sqrt(lanes)
        if noiseType == 'SpectralDensityFile':
            return self['SpectralDensityFile'].SpectralDensity(EndFrequency, FrequencyPoints)*math.sqrt(lanes)
        if noiseType == 'WaveformFile':
            return self['WaveformFile'].SpectralDensity(EndFrequency, FrequencyPoints)*math.sqrt(lanes)
        if noiseType == 'Johnson':
            # Backwards compatibility for existing project files that still store Johnson as a top-level noise type.
            return self['WhiteNoise.Johnson'].SpectralDensity(EndFrequency, FrequencyPoints)*math.sqrt(lanes)
        if noiseType == 'Crosstalk':
            return self['Crosstalk'].SpectralDensity(
                EndFrequency,
                FrequencyPoints,
                output_waveforms=output_waveforms,
                output_waveform_names=output_waveform_names)*math.sqrt(lanes)
        raise ValueError(f'Unknown noise type: {noiseType}')

class CurrentNoiseConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('CurrentNoise')
        self.Add(XMLPropertyDefaultBool('Enable',False))
        self.Add(XMLPropertyDefaultString('Type','WhiteNoise')) # 'WhiteNoise', 'SpectralDensityFile', 'WaveformFile', 'Crosstalk', or 'ShotNoise'
        self.SubDir(CurrentWhiteNoiseConfiguration())
        self.SubDir(SpectralDensityFileConfiguration())
        self.SubDir(NoiseWaveformFileConfiguration())
        self.SubDir(CrosstalkNoiseFromProbeConfiguration())
        self.SubDir(ShotNoiseConfiguration(parent=self))
        self.Add(XMLPropertyDefaultFloat('Lanes',1.0))
    def SpectralDensity(self, EndFrequency, FrequencyPoints, output_waveforms=None, output_waveform_names=None, output_types=None):
        from SignalIntegrity.Lib.FrequencyDomain.SpectralDensity import SpectralDensity
        from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
        import math
        fl = EvenlySpacedFrequencyList(EndFrequency, FrequencyPoints)
        if not self['Enable']:
            return SpectralDensity(fl, [0.0 for _ in fl])
        noiseType = self['Type']
        lanes = self['Lanes']
        if noiseType == 'WhiteNoise':
            return self['WhiteNoise'].SpectralDensity(EndFrequency, FrequencyPoints)*math.sqrt(lanes)
        if noiseType == 'SpectralDensityFile':
            return self['SpectralDensityFile'].SpectralDensity(EndFrequency, FrequencyPoints)*math.sqrt(lanes)
        if noiseType == 'WaveformFile':
            return self['WaveformFile'].SpectralDensity(EndFrequency, FrequencyPoints)*math.sqrt(lanes)
        if noiseType == 'Crosstalk':
            return self['Crosstalk'].SpectralDensity(
                EndFrequency,
                FrequencyPoints,
                output_waveforms=output_waveforms,
                output_waveform_names=output_waveform_names)*math.sqrt(lanes)
        if noiseType == 'ShotNoise':
            return self['ShotNoise'].SpectralDensity(
                EndFrequency,
                FrequencyPoints,
                output_waveforms=output_waveforms,
                output_waveform_names=output_waveform_names,
                output_types=output_types)*math.sqrt(lanes)
        raise ValueError(f'Unknown noise type: {noiseType}')