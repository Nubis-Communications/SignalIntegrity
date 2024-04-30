"""
Converters.py
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

def IdealCurrentToVoltageConverter(Z0=50.):
    """Ideal Current to Voltage Converter  
    Current enters port 1 and exits port 2.
    Port 3 provides an absolute voltage that equals the current flowing between ports 1 and 2.
    @param Z0 (optional) float reference impedance (defaults to 50 ohms)
    @return list of list s-parameter matrix    
    """
    return [[0,1.,0],
            [1.,0,0],
            [1/Z0,-1/Z0,-1.]]

def IdealVoltageToVoltageConverter():
    """Ideal Voltage to Voltage Converter  
    Differential voltage is between ports 2 and 1.
    Port 3 provides an absolute voltage that equals the differential voltage between ports 2 and 1.
    @return list of list s-parameter matrix   
    """
    return [[1.,0,0],
            [0,1.,0],
            [-2.,2.,-1.]]