"""
NoiseCalculator.py
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
from SignalIntegrity.Lib.TimeDomain.Filters.TransferMatricesProcessor import TransferMatricesProcessor
from SignalIntegrity.Lib.Exception import SignalIntegrityException
from SignalIntegrity.Lib.FrequencyDomain.FrequencyContent import FrequencyContent
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.Lib.TimeDomain.Waveform.DCWaveform import DCWaveform
import numpy as np

class NoiseCalculator(object):
    """performs noise calculations
    """
    def __init__(self,input_waveforms,output_waveform_labels,transfer_matrices):
        """constructor
        @param input_waveforms dictionary of input waveforms where the key is the name and the value is the waveform
        @param output_waveform_labels list of output waveform names
        @param transfer_matrices instance of class TransferMatrices for processing
        """
        return
        output_noise_per_input_sd_list = []
        input_noise_sd_list = [input_waveforms[key].noise if hasattr(input_waveforms[key],'noise') else None for key in input_waveforms.keys()]
        input_wf_list = [input_waveforms[key] for key in input_waveforms.keys()]
        if any([not noise_sd is None for noise_sd in input_noise_sd_list]):
            try:
                output_noise_per_input_sd_list = TransferMatricesProcessor(transfer_matrices).ProcessNoise(input_noise_sd_list)
            except SignalIntegrityException as e:
                return None
        output_total_noise_sd_list = []
        for input_list in output_noise_per_input_sd_list:
            # input_list is a list of spectral densitys at the output due to each input element
            if any([input_sd is not None for input_sd in input_list]):
                # manage the summing of the noise in quadrature
                output_total_noise_per_this_input = None
                for input_sd in input_list:
                    if not input_sd is None:
                        if not output_total_noise_per_this_input is None:
                            for fi in range(len(input_sd)):
                                output_total_noise_per_this_input[fi] = np.sqrt(abs(output_total_noise_per_this_input[fi])**2 + abs(input_sd[fi])**2)
                        else:
                            output_total_noise_per_this_input = input_sd
                output_total_noise_sd_list.append(output_total_noise_per_this_input)
        noise_waveforms = []
        for input_list in output_noise_per_input_sd_list:
            noise_wf_list_this_output = []
            for sd,wf in zip(input_list,input_wf_list):
                if not sd is None:
                    wf.noise = sd
                noise_wf_list_this_output.append(self.NoiseWaveform(wf))
            noise_waveforms.append(noise_wf_list_this_output)
        total_noise_waveforms=[]
        for output_total_noise_sd in output_total_noise_sd_list:
            pass
    def NoiseWaveform(self,wf):
        """produces a time-domain noise waveform from a spectral density
        @param wf instance of class Waveform
        @return instance of class Waveform containing a time-domain noise waveform  
        The noise is contained as a spectral density in the noise attribute of the waveform.
        returns a waveform of zeros if there is no noise
        """
        if not hasattr(wf,'noise'):
            noise_wf = DCWaveform(0)
            noise_wf.td = wf.td
            return noise_wf
        noise = wf.noise
        wffc=wf
        if not isinstance(wffc,DCWaveform):
            if wffc.td.K//2*2 != wffc.td.K:
                import copy
                wffc=copy.deepcopy(wf)
                td=wffc.td
                td.K=td.K-1
                wffc=wffc.Adapt(td)
        fc=FrequencyContent(wffc)
        fd=fc.FrequencyList()
        phase_list=np.exp(1j*np.random.uniform(0.,2*np.pi,size=len(fd)))
        noise_content=noise.Resample(fd)
        root_delta_f=np.sqrt(fd.Fe/fd.N)
        sqrt2=np.sqrt(2) # sqrt to take it from rms to amplitude for the dft
        for n in range(len(noise_content)):
            fc[n]=noise_content[n]*root_delta_f*(1./sqrt2 if n in [0,fd.N] else sqrt2)*(1. if n in [0,fd.N] else phase_list[n])
        noise_wf=fc.Waveform()
        return noise_wf

