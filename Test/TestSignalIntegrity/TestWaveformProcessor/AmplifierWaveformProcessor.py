"""
amplifier.py
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

# <waveform-processor-interface>
# {
#   "version": 1,
#   "ports": {"inputs": 1, "outputs": 1},
#   "variables": [
#     {"name": "IIP2", "description": "Second-order input intercept point", "type": "float", "default": 18.0, "units": "dBm", "visible": true, "read_only": false, "in_cache": true},
#     {"name": "IIP3", "description": "Third-order input intercept point", "type": "float", "default": 0.0, "units": "dBm", "visible": true, "read_only": false, "in_cache": true},
#     {"name": "bandwidth", "description": "Small-signal bandwidth", "type": "float", "default": 120000000000.0, "units": "Hz", "visible": true, "read_only": false, "in_cache": true},
#     {"name": "slewrate", "description": "Slew rate limit", "type": "float", "default": 60000000000.0, "units": "V/s", "visible": true, "read_only": false, "in_cache": true}
#   ]
# }
# </waveform-processor-interface>

from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from Amplifier import amplifier_iip2_iip3_slew
#Code which will be run by a dependent voltage source to perform voltage transformation
#This transform processes its first input waveform.
# inputs: inputWaveforms - dictionary containing Waveform to utilize
# outputs: outputWaveform - set to transformed Waveform

x = input_waveform_1.Values()
fs =input_waveform_1.TimeDescriptor().Fs

outputWaveform_values = amplifier_iip2_iip3_slew(
        x,
        fs,
        0.0,
        IIP2,
        IIP3,
        bandwidth,
        slewrate,
);

output_waveform_1 = Waveform(input_waveform_1.TimeDescriptor(), list(outputWaveform_values))

