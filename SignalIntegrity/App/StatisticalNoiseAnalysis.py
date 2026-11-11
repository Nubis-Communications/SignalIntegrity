"""
StatisticalNoiseAnalysis.py
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

class StatisticalNoiseAnalysis(dict):
    def __init__(self, schematic,
                 transferMatrices,
                 output_waveforms,
                 output_waveform_names,
                 transfer_output_names=None,
                 transfer_source_names=None):

        dict.__init__(self)

        try:
            netlist = schematic.NetList()

            if netlist is None:
                return

            if netlist.NoiseSourceNames() is None or len(netlist.NoiseSourceNames()) == 0:
                return

            if transfer_output_names is None:
                transfer_output_names=netlist.OutputNames()
            if transfer_source_names is None:
                transfer_source_names=netlist.SourceNames()

            outputWaveformLabels,sourceNames,transferMatrices = transferMatrices.Keep(
                transfer_output_names,        # outputs
                transfer_source_names,        # sources
                netlist.NoiseOutputNames(),    # outputs to keep
                netlist.NoiseSourceNames()     # sources to keep
                )

            # Align the ideal signal waveforms to the kept output labels (by
            # name) so that the signal-power and SNR references line up with the
            # outputs that were kept for the noise measurements.
            keptOutputWaveforms = []
            for output_name in outputWaveformLabels:
                if output_name in output_waveform_names:
                    keptOutputWaveforms.append(output_waveforms[output_waveform_names.index(output_name)])
                else:
                    keptOutputWaveforms.append(None)

            from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
            fl = EvenlySpacedFrequencyList(transferMatrices.f[-1], len(transferMatrices.f)-1)

            # determine the 'type' (voltage or current) of each output probe.
            # A CurrentOutput probe measures current, so its noise/signal is
            # reported in current units; every other probe reports voltage.
            output_types = {}
            for output_name in outputWaveformLabels:
                output_types[output_name] = 'voltage'
                for device in schematic.deviceList:
                    if device['ref'] is None:
                        continue
                    if device['ref'].GetValue() == output_name:
                        if device['partname'].GetValue() == 'CurrentOutput':
                            output_types[output_name] = 'current'
                        break

            # A full probe-type map keyed by every available output waveform name
            # (not just the kept labels) so that shot-noise sources can validate
            # that a referenced probe is actually a current probe.
            probe_types = {}
            for output_name in output_waveform_names:
                probe_types[output_name] = 'voltage'
                for device in schematic.deviceList:
                    if device['ref'] is None:
                        continue
                    if device['ref'].GetValue() == output_name:
                        if device['partname'].GetValue() == 'CurrentOutput':
                            probe_types[output_name] = 'current'
                        break

            input_types = {}
            inputNoiseSpectralDensityList = []
            for noise_source_ref in netlist.NoiseSourceNames():
                sd = None
                for device in schematic.deviceList:
                    if device['partname'].GetValue() in ['VoltageStatisticalNoiseSource','VoltageStatisticalNoiseSourceProject','CurrentStatisticalNoiseSource','CurrentStatisticalNoiseSourceProject']:
                        if device['ref'].GetValue() == noise_source_ref:
                            input_types[noise_source_ref] = 'current' if device['partname'].GetValue().startswith('Current') else 'voltage'
                            sd = device.SpectralDensity(
                                output_waveforms=output_waveforms,
                                output_waveform_names=output_waveform_names,
                                output_types=probe_types).Resample(fl)
                            inputNoiseSpectralDensityList.append(sd)
                            break

            from SignalIntegrity.Lib.Noise.NoiseAnalysis import NoiseAnalysis

            dict.__init__(self,
                          NoiseAnalysis(
                              output_names = outputWaveformLabels,
                              output_waveforms = keptOutputWaveforms,
                              input_names = sourceNames,
                              transfer_matrices = transferMatrices,
                              input_noise_spectral_density = inputNoiseSpectralDensityList,
                              output_types = output_types,
                              input_types = input_types
                              )
                          )

            # The kept outputs (including eye probes whose 'include in noise' is
            # off) remain in the results dictionary above so their external noise
            # stays available to the eye diagrams.  'noise_display_output_names'
            # is the subset that should actually be shown in the spectral density
            # plots and listed in the noise measurements.
            if 'output_names' in self:
                displayNames = netlist.NoiseDisplayOutputNames()
                self['noise_display_output_names'] = [name for name in self['output_names'] if name in displayNames]
        except Exception as e:
            raise Exception("Error in StatisticalNoiseAnalysis: "+str(e))

    def Noise(self,reference):
        try:
            return self['output_noise_spectral_density'][reference]['rms']
        except Exception as e:
            return 0.0