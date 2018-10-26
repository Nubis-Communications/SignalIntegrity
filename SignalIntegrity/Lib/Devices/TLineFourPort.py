"""
TLineFourPort.py
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

import cmath


def TLineFourPort(Zc,gamma,Z0=50.):
    """TLineFourPort
    Ideal Four-port Transmission Line
    @param Zc float or complex characteristic impedance
    @param gamma float or complex propagation constant
    @param Z0 (optional) float or complex reference impedance Z0 (defaults to 50 Ohms).
    @return the s-parameter matrix of a four-port transmission line
    @remark This is actually an oddball construction and should not be confused with a typical differential
    transmission line.\n
    The symbol looks like a two-port transmission line with it's outer conductor exposed as ports on each
    side.\n
    Port 1 is the left side and port 2 is the right side of the two-port transmission line.\n
    Port 3 is the left, exposed, outer conductor and port 4 is the right, exposed outer conductor.\n
    @note this device is functionally equivalent to the two-port transmission line TLineTwoPort() when
    ports 3 and 4 are grounded.
    """
    """
              +-----------------------+
             / \                       \
      1 ----+-  |     Z    Td           +----- 2
             \ /                       /
           +--+-----------------------+--+
           |                             |
      3 ---+                             +---- 4

    ports 1 and 2 are the input and output
    ports 3 and 4 are the outer conductor
    """
    p=(Zc-Z0)/(Zc+Z0)
    a=(1.-3.*p)/(p-3.)
    # pragma: silent exclude
#     this calculation for a is the same as:
#     a=(Zc-2.*Z0)/(Zc+2.*Z0) or
#     a=(Zc/2.-Z0)/(Zc/2.+Z0)
    # pragma: include
    Y=cmath.exp(-gamma)
    D=2.*(1-Y*Y*a*a)
    S1=(1.-Y*Y*a*a+a*(1.-Y*Y))/D
    S2=(1.-a*a)*Y/D
    S3=((1.-Y*Y*a*a)-a*(1.-Y*Y))/D
    return [[S1,S2,S3,-S2],
            [S2,S1,-S2,S3],
            [S3,-S2,S1,S2],
            [-S2,S3,S2,S1]]
