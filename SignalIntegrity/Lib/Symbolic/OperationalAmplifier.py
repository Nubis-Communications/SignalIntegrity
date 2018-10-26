"""
OperationalAmplifier.py
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

def OperationalAmplifier(Zi,Zd,Zo,G):
    """symbolic operationalAmplifier
    Operational Amplifier

    Port 1 is - input, port 2 is + input and port 3 is output

    @param Zi string input impedance between each plus and minus input port
    to ground.
    @param Zd string input impedance across the plus and minus inputs.
    @param Zo string output impedance.
    @param G string gain of the op-amp.
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.OperationalAmplifier.OperationalAmplifier
    """
    S11='\\frac{\\left(-2\\cdot '+Zi+' - '+Zd+' \\right)\\cdot Z0^2+ '+Zi+' ^2\\cdot '+Zd+' }{\\left(2\\cdot '+Zi+' + '+Zd+' \\right)\\cdot Z0^2+\\left(2\\cdot '+Zi+' \\cdot '+Zd+' +2\\cdot '+Zi+' ^2\\right)\\cdot Z0+ '+Zi+' ^2\\cdot '+Zd+' }'
    S12='\\frac{2\\cdot '+Zi+' ^2\\cdot Z0}{\\left(2\\cdot '+Zi+' + '+Zd+' \\right)\\cdot Z0^2+\\left(2\\cdot '+Zi+' \\cdot '+Zd+' +2\\cdot '+Zi+' ^2\\right)\\cdot Z0+ '+Zi+' ^2\\cdot '+Zd+' }'
    S32='\\frac{2\\cdot '+G+' \\cdot '+Zi+' \\cdot '+Zd+' \\cdot Z0}{\\left( '+Zo+' +Z0\\right)\\cdot \\left(\\left(2\\cdot '+Zi+' + '+Zd+' \\right)\\cdot Z0+ '+Zi+' \\cdot '+Zd+' \\right)}'
    S33='\\frac{ '+Zo+' -Z0}{ '+Zo+' +Z0}'
    return [[S11,S12,'0'],[S12,S11,'0'],['-'+S32,S32,S33]]