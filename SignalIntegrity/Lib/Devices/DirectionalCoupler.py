"""
DirectionalCoupler.py
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

def DirectionalCoupler(ports):
    """DirectionalCoupler
    Directional Coupler
    @param ports integer number of ports (3 or 4)
    @return s-parameter matrix of a three or four port directional coupler
    port 1 and 2 are a thru connection.

    port 3 picks off the wave going from port 1 to 2.

    port 4 (optional) picks off the wave going from port 2 to port 1.

    @note the directional coupler is completely ideal and is not passive
    in that the picked off wave is an exact copy of the wave going between
    the ports specified above.
    """
    if ports==3:
        return [[0,1,0],
                [1,0,0],
                [1,0,0]]
    elif ports==4:
        return [[0,1,0,0],
                [1,0,0,0],
                [1,0,0,0],
                [0,1,0,0]]
