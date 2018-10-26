"""
RaisedCosineFilter.py
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

from SignalIntegrity.Lib.TimeDomain.Filters.FirFilter import FirFilter
from SignalIntegrity.Lib.TimeDomain.Filters.FilterDescriptor import FilterDescriptor
import math

class RaisedCosineFilter(FirFilter):
    """raised cosine filter"""
    def __init__(self,S=1):
        """Constructor
        @param S integer side samples.  The filter is 2*S+1 total samples.
        """
        L=2*S+1
        w=[math.cos(2*math.pi*(k-S)/L)*0.5+0.5 for k in range(L)]
        Scale=sum(w)
        w=[tap/Scale for tap in w]
        FirFilter.__init__(self,FilterDescriptor(1,S,2*S),w)