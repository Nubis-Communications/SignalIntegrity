"""
Open.py
"""
import numpy

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
def Open(numports = 1):
    """Open
    Ideal Open
    @returns the list of list s-parameter matrix of open.
    this is simply a 1x1 matrix containing 1, or [[1]] for 1 port 
    """
    if (numports == 1):
        return [[1.]]
    else:
        s_params = [[0]*numports for i in range(numports)]
        for i in range(numports):
            s_params[i][i] = 1
        return s_params

    
