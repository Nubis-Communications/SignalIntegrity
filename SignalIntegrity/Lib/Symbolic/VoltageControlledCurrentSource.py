"""
VoltageControlledCurrentSource.py
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

def VoltageControlledCurrentSource(G):
    """symbolic voltage controlled current source
    @param G string transconductance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of
    SignalIntegrity.Lib.Devices.VoltageControlledCurrentSource.VoltageControlledCurrentSource
    """
    return  [['1','0','0','0'],
            ['0','1','0','0'],
            ['2\\cdot '+G+' \\cdot Z0','-2\\cdot '+G+' \\cdot Z0','1','0'],
            ['-2\\cdot '+G+' \\cdot Z0','2\\cdot '+G+' \\cdot Z0','0','1']]
