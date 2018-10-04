"""
Differentiator.py
"""

# Copyright (c) 2018 Teledyne LeCroy, all rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
from SignalIntegrity.FrequencyDomain.FrequencyResponse import FrequencyResponse
from SignalIntegrity.TimeDomain.Waveform.ImpulseResponse import ImpulseResponse

class Differentiator(FrequencyResponse):
    def __init__(self,fl):
        td=fl.TimeDescriptor()
        resp=[0 for k in range(td.K)]
        resp[td.K/2]=td.Fs
        resp[td.K/2+1]=-resp[td.K/2]
        ir=ImpulseResponse(td,resp)
        fr=ir.FrequencyResponse()
        FrequencyResponse.__init__(self,fl,fr.Response())