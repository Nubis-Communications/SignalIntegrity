"""
DCWaveform.py
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
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform

class DCWaveform(Waveform):
    def __init__(self,value):
        Waveform.__init__(self)
        list.__init__(self,[value])
    def Value(self):
        return self[0]
    def __getitem__(self,item):
        return Waveform.__getitem__(self,0)
    def TrueWaveform(self):
        """a true waveform where the samples adhere to the time descriptor
        @return instance of class Waveform
        """
        return Waveform(self.td,[self[k] for k in range(self.td.K)])