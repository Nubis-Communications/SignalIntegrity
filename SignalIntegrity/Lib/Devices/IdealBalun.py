"""
IdealBalun.py
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

def IdealBalun():
    """Ideal Balun

    Port 1 is the single-ended input

    Ports 2 and 3 are the positive and negative single-ended outputs, respectively.

    @return the s-parameter matrix of an ideal balun
    """
    import math
    sqrt2over2=math.sqrt(2.)/2.
    return [[0,sqrt2over2,-sqrt2over2],
            [sqrt2over2,1./2.,1./2.],
            [-sqrt2over2,1./2.,1./2.]]
