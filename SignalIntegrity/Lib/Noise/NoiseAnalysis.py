"""
NoiseAnalysis.py
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
import math

class NoiseAnalysis(dict):
    """Computes and organizes the results of a linear noise analysis.
    Given a set of noise sources (inputs), the transfer functions from those
    sources to a set of observation points (outputs), and the ideal signal
    waveforms at those outputs, this class propagates each input noise spectral
    density to every output, sums the contributions, and derives a collection
    of summary metrics (rms, dBm, spectral densities, and signal-to-noise
    ratios).

    The class subclasses ``dict``; all results are stored as keys on the
    instance.  Every input and output may be designated as either a
    ``'voltage'`` or a ``'current'`` quantity via the ``input_types`` and
    ``output_types`` arguments.  The declared type selects the neutral rms
    interpretation ('rms' is a voltage rms in volts or a current rms in amps)
    and the power law used when converting to dBm (P = V**2/R for voltages,
    P = I**2*R for currents).

    The following keys are populated on the instance (all dictionaries are
    keyed by the corresponding input or output name unless noted):

    - ``'output_names'`` / ``'input_names'``: the ordered name lists.
    - ``'output_types'`` / ``'input_types'``: the name-to-type maps.
    - ``'transfer_matrices'``: the transfer matrices passed in.
    - ``'input_noise_spectral_density_list'``: list of input spectral
      densities (in the input order).
    - ``'input_noise_spectral_density'``: per-input dict with keys
      ``'spectrum'``, ``'type'``, ``'dBm'`` and ``'rms'``.
    - ``'output_noise_spectral_density_list'``: list of total output noise
      spectral densities (in the output order).
    - ``'output_noise_spectral_density'``: per-output dict with keys
      ``'spectrum'``, ``'type'``, ``'dBm'``, ``'rms'``, and the frequency
      normalized values ``'rms/sqrt(Hz)'``, ``'rms/sqrt(GHz)'``,
      ``'dBm/Hz'`` and ``'dBm/GHz'``.
    - ``'signal_noise_spectral_density_list'`` /
      ``'signal_noise_spectral_density'``: the spectral density of the ideal
      signal at each output (used as the reference for SNR calculations).
    - ``'signal_to_noise_ratio'``: per-output dict with ``'SNR'`` and
      ``'SalzSNR'`` in dB.
    - ``'contributions'``: per-output, per-input dict giving the individual
      noise contribution of each input to each output, with keys
      ``'spectrum'``, ``'type'``, ``'dBm'``, ``'rms'``, ``'SNR'`` and
      ``'SalzSNR'``.
    """

    def __init__(self, output_names, output_waveforms, input_names, transfer_matrices, input_noise_spectral_density,
                 output_types=None, input_types=None):
        """Constructs a NoiseAnalysis result dictionary.
        @param output_names list of str names of the observation points
            (outputs) in the order they appear in the transfer matrices.
        @param output_waveforms list of the ideal signal waveforms at each
            output, in the same order as output_names.  Each waveform must
            provide a ``SpectralDensity()`` method and is used as the signal
            reference for the SNR metrics.
        @param input_names list of str names of the noise sources (inputs) in
            the order they appear in the transfer matrices.
        @param transfer_matrices the transfer matrices describing the linear
            mapping from every input noise source to every output.
        @param input_noise_spectral_density list of spectral density objects,
            one per input (in input_names order), giving the noise spectral
            density injected at each input.
        @param output_types (optional) dict mapping each output name to either
            ``'voltage'`` or ``'current'``.  Defaults to ``'voltage'`` for
            every output when omitted.
        @param input_types (optional) dict mapping each input name to either
            ``'voltage'`` or ``'current'``.  Defaults to ``'voltage'`` for
            every input when omitted.

        If input_names is empty the instance is left empty (no analysis is
        performed).
        """
        dict.__init__(self)

        if len(input_names) == 0:
            return

        # output_types/input_types map each output/input name to either
        # 'voltage' or 'current'.  When not supplied, everything defaults to
        # 'voltage' (the historical behavior).  The 'type' determines the
        # neutral units ('rms' is a voltage rms or a current rms) and the power
        # law used for the dBm conversion.
        if output_types is None:
            output_types = {name: 'voltage' for name in output_names}
        if input_types is None:
            input_types = {name: 'voltage' for name in input_names}

        def output_type(name):
            return output_types.get(name, 'voltage')

        def input_type(name):
            return input_types.get(name, 'voltage')

        self['output_names'] = output_names
        self['input_names'] = input_names
        self['output_types'] = output_types
        self['input_types'] = input_types
        self['transfer_matrices'] = transfer_matrices
        self['input_noise_spectral_density_list'] = input_noise_spectral_density
        self['input_noise_spectral_density'] = {key: {'spectrum': sd, 'type': input_type(key), 'dBm': sd.TotaldBm(reference=input_type(key)), 'rms': sd.TotalRMS() } for key, sd in zip(input_names, input_noise_spectral_density)}

        from SignalIntegrity.Lib.Noise.NoiseTransferMatricesProcessor import NoiseTransferMatricesProcessor

        noiseTransferMatricesProcessor = NoiseTransferMatricesProcessor(transfer_matrices)
        outputNoiseSpectralDensityList = noiseTransferMatricesProcessor.ProcessNoise(input_noise_spectral_density)

        self['output_noise_spectral_density_list'] = outputNoiseSpectralDensityList
        self['output_noise_spectral_density'] = {key: {'spectrum': sd, 'type': output_type(key), 'dBm': sd.TotaldBm(reference=output_type(key)), 'rms': sd.TotalRMS() } for key, sd in zip(output_names, outputNoiseSpectralDensityList)}


        self['signal_noise_spectral_density_list'] = [signal.SpectralDensity() for signal in output_waveforms]
        self['signal_noise_spectral_density'] = {key: {'spectrum': sd, 'type': output_type(key), 'dBm': sd.TotaldBm(reference=output_type(key)), 'rms': sd.TotalRMS() } for key,sd in zip(output_names,self['signal_noise_spectral_density_list'])}

        self['signal_to_noise_ratio'] = {key: {'SNR': self['output_noise_spectral_density'][key]['spectrum'].SNRdB(self['signal_noise_spectral_density'][key]['spectrum'],other_is_signal_or_noise='signal'),
                                               'SalzSNR': self['output_noise_spectral_density'][key]['spectrum'].SalzSNRdB(self['signal_noise_spectral_density'][key]['spectrum'],other_is_signal_or_noise='signal')
                                               } for key in output_names}
        
        endFrequencyList = [sd.Frequencies('GHz')[-1] for sd in outputNoiseSpectralDensityList]
        for key,fe in zip(self['output_noise_spectral_density'].keys(),endFrequencyList):
            sdv = self['output_noise_spectral_density'][key]
            sdv['rms/sqrt(Hz)'] = sdv['rms']/math.sqrt(fe*1e9)
            sdv['rms/sqrt(GHz)'] = sdv['rms']/math.sqrt(fe)
            sdv['dBm/Hz'] = sdv['dBm'] - 10.*math.log10(fe*1e9)
            sdv['dBm/GHz'] = sdv['dBm'] - 10.*math.log10(fe)

        contributions = noiseTransferMatricesProcessor.Contributions
        self['contributions'] = {key: {input_names[i]:
                                       {'spectrum': contributions[o][i],
                                        'type': output_type(key),
                                        'dBm': contributions[o][i].TotaldBm(reference=output_type(key)),
                                        'rms': contributions[o][i].TotalRMS()
                                        } for i in range(len(input_names))} for o, key in enumerate(output_names)}

        for o in self['contributions'].keys():
            for i in self['contributions'][o].keys():
                self['contributions'][o][i]['SNR'] = self['signal_noise_spectral_density'][o]['dBm'] - self['contributions'][o][i]['dBm']
                self['contributions'][o][i]['SalzSNR'] = self['contributions'][o][i]['spectrum'].SalzSNRdB(self['signal_noise_spectral_density'][o]['spectrum'],other_is_signal_or_noise='signal')
        pass