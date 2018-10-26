"""
IdealTransformer.py
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

def IdealTransformer(a=1.):
    """Ideal Transformer

    Ports 1 and 2 are the primary.

    Ports 3 and 4 are the secondary.

    The dot is on ports 1 and 3.

    a is the turns ratio specified as (secondary/primary) windings

    @param a float (optional) turns ratio (defaults to 1)
    @return the s-parameter matrix of an ideal transformer
    """
    a=float(a)
    D=a*a+1.
    return [[1./D,a*a/D,a/D,-a/D],
            [a*a/D,1./D,-a/D,a/D],
            [a/D,-a/D,a*a/D,1./D],
            [-a/D,a/D,1./D,a*a/D]]
