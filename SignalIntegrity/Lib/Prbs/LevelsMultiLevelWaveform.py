"""
 levels defined multi-level waveform
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

import math

from SignalIntegrity.Lib.TimeDomain.Waveform import Waveform
from SignalIntegrity.Lib.Prbs.PseudoRandomPolynomial import PseudoRandomPolynomial
from SignalIntegrity.Lib.Prbs.SerialDataWaveform import SerialDataWaveform

class LevelsMultiLevelWaveform(Waveform):
    """a PRBS multi-level waveform with a given PRBS polynomial"""
    def __init__(self,polynomial,baudrate,levels=2,symbols=1,amplitude=1.0,risetime=0.,delay=0.,td=None):
        """constructor
        @param polynomial integer polynomial number
        @param baudrate, amplitude, risetime, delay, td all pertain to the derived SerialDataWaveform class
        @see SerialDataWaveform
        @param levels integer (defaults to 2) are the number of levels (i.e. the PAM of the waveform).
        @param symbols integer (defaults to 1) are the number of symbols to be used for encoding
        @return self, a waveform.
        @throw SignalIntegrityWaveform exception is raised if the polynomial number cannot be found
        @see PseudoRandomPolynomial
        @note the pseudo-random bits are grouped for each symbol.
        """
        bits_per_symbol = math.log2(levels)
        if float(round(bits_per_symbol)) == bits_per_symbol:
            # the bits per symbol resolves to an integer number (NRZ, PAM4, PAM8, etc.)
            from SignalIntegrity.Lib.Prbs.MultiLevelWaveform import MultiLevelWaveform
            Waveform.__init__(self,
                  MultiLevelWaveform(polynomial,
                                     baudrate,
                                     round(bits_per_symbol),
                                     amplitude,
                                     risetime,
                                     delay,
                                     td))
            return
        total_symbols=int(math.ceil(td.Duration()*baudrate))
        bits_per_symbol = math.log2(levels)
        bits_per_block = math.floor(symbols*bits_per_symbol)
        pattern=PseudoRandomPolynomial(polynomial).Pattern(int(math.ceil(total_symbols*bits_per_symbol))) if isinstance(polynomial,int) else polynomial
        # first generate the levels at the baudrate
        pattern_length=len(pattern)
        symbol_count = 0
        levels_list = []
        index_in_pattern = 0
        while symbol_count <= total_symbols:
            block_number=0
            for _ in range(bits_per_block):
                block_number = block_number * 2 + pattern[index_in_pattern]
                index_in_pattern = (index_in_pattern + 1) % pattern_length
            # this block will now be encoded in the number of symbols specified
            block_levels=[]
            for _ in range(symbols):
                level=math.floor(block_number % levels + 0.5)
                block_levels.append(level)
                symbol_count = symbol_count + 1
                if symbol_count >=total_symbols:
                    break
                block_number = math.floor((block_number - level)/levels + 0.5)
            levels_list.extend(block_levels)
        # levels_list now contains the value of each level for the number of symbols specified by total_symbols
        # each level is in 0 <= level <= levels - 1.
        # the total symbols are for the duration of the waveform.
        levels_amplitude_list = [-amplitude + level_index * 2 * amplitude / (levels - 1) for level_index in range(levels)]
        levels_list = [levels_amplitude_list[level] for level in levels_list]
        Waveform.__init__(self,td,None)
        UI=1/baudrate
        times=self.td.Times()
        for k in range(len(self)):
            self[k] = levels_list[int((times[k]-delay-1/(2.*td.Fs))/UI)]