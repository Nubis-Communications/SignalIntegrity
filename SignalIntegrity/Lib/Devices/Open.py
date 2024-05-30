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

import numpy as np

def Open(ports = 1):
    """Open
    Ideal Open
    @param ports integer, optional (defaults to 1) number of ports
    @returns the list of list s-parameter matrix of open.
    For a single port open, this is just [[1.]], otherwise it is a list of list
    identity matrix that is ports x ports. 
    """
    return np.identity(ports).tolist()
