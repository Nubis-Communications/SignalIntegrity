"""
ShuntZ.py
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

def ShuntZ(P,Z):
    """symbolic shunt impedance
    @param P integer number of ports (1,2,3,4)
    if ports are 1, then returns SignalIntegrity.Symbolic.ShuntZ.ShuntZOnePort \n
    if ports are 2, then returns SignalIntegrity.Symbolic.ShuntZ.ShuntZTwoPort \n
    if ports are 3, then returns SignalIntegrity.Symbolic.ShuntZ.ShuntZThreePort \n
    if ports are 4, then returns SignalIntegrity.Symbolic.ShuntZ.ShuntZFourPort \n
    @param Z string impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    """
    if P==1:
        return ShuntZOnePort(Z)
    elif P==2:
        return ShuntZTwoPort(Z)
    elif P==3:
        return ShuntZThreePort(Z)
    elif P==4:
        return ShuntZFourPort(Z)

def ShuntZFourPort(Z):
    """symbolic four port shunt impedance
    @param Z string impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.ShuntZ.ShuntZFourPort
    @remark Ports 1 and 3 are connected to port 1 of the device D provided.\n
    Ports 2 and 4 are connected to port 2 of the device D provided.\n
    @todo check the port numbering
    """
    D='2\\cdot \\left('+Z+'+Z0\\right)'
    return [['\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}'],
            ['\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}'],
            ['\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}'],
            ['\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}']]

def ShuntZThreePort(Z):
    """symbolic three port shunt impedance
    @param Z string impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.ShuntZ.ShuntZThreePort
    @remark Ports 1 and 2 are connected together and to port 1 impedance.\n
    Port 3 is the other port of the impedance.\n
    @todo check the port numbering
    """
    D='2\\cdot '+Z+'+3\\cdot Z0'
    return [['\\frac{-Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+2\\cdot Z0}{'+D+'}','\\frac{2\\cdot Z0}{'+D+'}'],
            ['\\frac{2\\cdot '+Z+'+2\\cdot Z0}{'+D+'}','\\frac{-Z0}{'+D+'}','\\frac{2\\cdot Z0}{'+D+'}'],
            ['\\frac{2\\cdot Z0}{'+D+'}','\\frac{2\\cdot Z0}{'+D+'}','\\frac{2\\cdot '+Z+'-Z0}{'+D+'}']]

def ShuntZTwoPort(Z):
    """symbolic two port shunt impedance
    @param Z string impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.ShuntZ.ShuntZTwoPort
    @remark Ports 1 and 2 are connected together and to one side of the impedance.\n
    The other side of the impedance is tied to ground.
    """
    D='2\\cdot '+Z+' +Z0'
    return [['\\frac{-Z0}{'+D+'}','\\frac{2\\cdot '+Z+'}{'+D+'}'],
            ['\\frac{2\\cdot '+Z+'}{'+D+'}','\\frac{-Z0}{'+D+'}']]

def ShuntZOnePort(Z):
    """symbolic four port shunt impedance

    This is simply a termination impedance to ground.

    @param Z string impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.TerminationZ.TerminationZ
    """
    return [['\\frac{ '+Z+' -Z0}{ '+Z+' +Z0}']]


