"""
scale_nonlin.py
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

from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from Amplifier import amplifier_iip2_iip3_slew
#Code which will be run by a dependent voltage source to perform voltage transformation
#This transform processes its first input waveform.
# inputs: inputWaveforms - dictionary containing Waveform to utilize
# outputs: outputWaveform - set to transformed Waveform

inputWaveform = input_waveform_1

if iteration <0:
    outputWaveform = inputWaveform
else:

    x = inputWaveform.Values()
    fs = inputWaveform.TimeDescriptor().Fs

    outputWaveform_values = amplifier_iip2_iip3_slew(
        x,
        fs,
        0.0,
        IIP2,
        IIP3,
        bandwidth,
        slewrate,
    );

    outputWaveform = Waveform(inputWaveform.TimeDescriptor(), list(outputWaveform_values))
