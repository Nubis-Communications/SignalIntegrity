"""
VoltageAmplifier.py
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

from SignalIntegrity.Lib.Helpers.lfrac import lfrac

def VoltageAmplifier(P,G,Zi,Zo):
    """symbolic 2,3, and 4 port voltage amplifier
    @param P integer number of ports (2,3,4)\n
    if ports are 2, then returns SignalIntegrity.Symbolic.VoltageAmplifier.VoltageAmplifierTwoPort\n
    if ports are 3, then returns SignalIntegrity.Symbolic.VoltageAmplifier.VoltageAmplifierThreePort\n
    if ports are 4, then returns SignalIntegrity.Symbolic.VoltageAmplifier.VoltageAmplifierFourPort
    @param G string voltage gain
    @param Zi string input impedance
    @param Zo string output impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    """
    if P==2:
        return VoltageAmplifierTwoPort(G,Zi,Zo)
    elif P==3:
        return VoltageAmplifierThreePort(G,Zi,Zo)
    elif P==4:
        return VoltageAmplifierFourPort(G,Zi,Zo)

def VoltageAmplifierFourPort(G,Zi,Zo):
    """symbolic four port current amplifier
    @param G string voltage gain
    @param Zi string input impedance
    @param Zo string output impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.VoltageAmplifier.VoltageAmplifierFourPort
    """
    return [[lfrac(Zi,Zi+'+2\\cdot Z0'),lfrac('2\\cdot Z0',Zi+'+2\\cdot Z0'),'0','0'],
            [lfrac('2\\cdot Z0',Zi+'+2\\cdot Z0'),lfrac(Zi,Zi+'+2\\cdot Z0'),'0','0'],
            [lfrac('2\\cdot '+Zi+'\\cdot Z0\\cdot '+G,' ('+Zi+'+2\\cdot Z0 )\\cdot ('+Zo+'+2\\cdot Z0 )'),
            '-'+lfrac('2\\cdot '+Zi+'\\cdot Z0\\cdot '+G,' ('+Zi+'+2\\cdot Z0 )\\cdot ('+Zo+'+2\\cdot Z0 )'),
            lfrac(Zo,Zo+'+2\\cdot Z0'),lfrac('2\\cdot Z0',Zo+'+2\\cdot Z0')],
            ['-'+lfrac('2\\cdot '+Zi+'\\cdot Z0\\cdot '+G,' ('+Zi+'+2\\cdot Z0 )\\cdot ('+Zo+'+2\\cdot Z0 )'),
            lfrac('2\\cdot '+Zi+'\\cdot Z0\\cdot '+G,' ('+Zi+'+2\\cdot Z0 )\\cdot ('+Zo+'+2\\cdot Z0 )'),
            lfrac('2\\cdot Z0',Zo+'+2\\cdot Z0'),lfrac(Zo,Zo+'+2\\cdot Z0')]]

def VoltageAmplifierThreePort(G,Zi,Zo):
    """symbolic three port voltage amplifier
    @param G string voltage gain
    @param Zi string input impedance
    @param Zo string output impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.VoltageAmplifier.VoltageAmplifierThreePort
    """
    D='-'+Zo+'\\cdot '+Zi+'-2\\cdot '+Zo+'\\cdot Z0-2\\cdot '+Zi+'\\cdot Z0-3\\cdot Z0^2+'+G+'\\cdot '+Zi+'\\cdot Z0'
    S11=lfrac('-'+Zo+'\\cdot '+Zi+'-2\\cdot '+Zi+'\\cdot Z0+Z0^2+'+G+'\\cdot '+Zi+'\\cdot Z0',D)
    S12=lfrac('-2\\cdot Z0^2',D)
    S13=lfrac('-2\\cdot Z0\\cdot ('+Zo+' +Z0 )',D)
    S21=lfrac('-2\\cdot Z0 \\cdot ('+G+'\\cdot '+Zi+' +Z0 )',D)
    S22=lfrac('Z0^2-2\\cdot '+Zo+'\\cdot Z0+'+G+'\\cdot '+Zi+'\\cdot Z0-'+Zo+'\\cdot '+Zi,D)
    S23=lfrac('2\\cdot Z0\\cdot ('+G+'\\cdot '+Zi+'-'+Zi+'-Z0 )',D)
    S31=lfrac('2\\cdot Z0\\cdot (-Z0+'+G+'\\cdot '+Zi+'-'+Zo+' )',D)
    S32=lfrac('-2\\cdot Z0\\cdot ('+Zi+'+Z0 )',D)
    S33=lfrac('-'+Zo+'\\cdot '+Zi+'+Z0^2-'+G+'\\cdot '+Zi+'\\cdot Z0',D)
    return [[S11,S12,S13],
            [S21,S22,S23],
            [S31,S32,S33]]

def VoltageAmplifierThreePortWithoutDenom(G,Zi,Zo):
    """symbolic three port voltage amplifier without denominator
    @param G string voltage gain
    @param Zi string input impedance
    @param Zo string output impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.VoltageAmplifier.VoltageAmplifierThreePort
    @remark this returns the s-parameter matrix without the denominator element
    @see VoltageAmplifierThreePortDenom
    """
    S11='-'+Zo+'\\cdot '+Zi+'-2\\cdot '+Zi+'\\cdot Z0+Z0^2+'+G+'\\cdot '+Zi+'\\cdot Z0'
    S12='-2\\cdot Z0^2'
    S13='-2\\cdot Z0\\cdot ('+Zo+' +Z0 )'
    S21='-2\\cdot Z0 \\cdot ('+G+'\\cdot '+Zi+' +Z0 )'
    S22='Z0^2-2\\cdot '+Zo+'\\cdot Z0+'+G+'\\cdot '+Zi+'\\cdot Z0-'+Zo+'\\cdot '+Zi
    S23='2\\cdot Z0\\cdot ('+G+'\\cdot '+Zi+'-'+Zi+'-Z0 )'
    S31='2\\cdot Z0\\cdot (-Z0+'+G+'\\cdot '+Zi+'-'+Zo+' )'
    S32='-2\\cdot Z0\\cdot ('+Zi+'+Z0 )'
    S33='-'+Zo+'\\cdot '+Zi+'+Z0^2-'+G+'\\cdot '+Zi+'\\cdot Z0'
    return [[S11,S12,S13],
            [S21,S22,S23],
            [S31,S32,S33]]

def VoltageAmplifierThreePortDenom(G,Zi,Zo):
    """symbolic three port voltage amplifier denominator
    @param G string voltage gain
    @param Zi string input impedance
    @param Zo string output impedance
    @return the denominator element common in the s-parameter matrix as a string
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.VoltageAmplifier.VoltageAmplifierThreePort
    @see VoltageAmplifierThreePortWithoutDenom
    """
    D='-'+Zo+'\\cdot '+Zi+'-2\\cdot '+Zo+'\\cdot Z0-2\\cdot '+Zi+'\\cdot Z0-3\\cdot Z0^2+'+G+'\\cdot '+Zi+'\\cdot Z0'
    return D

def VoltageAmplifierTwoPort(G,Zi,Zo):
    """symbolic two port voltage amplifier
    @param G string voltage gain
    @param Zi string input impedance
    @param Zo string output impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.VoltageAmplifier.VoltageAmplifierTwoPort
    """
    return [[lfrac(Zi+' - Z0',Zi+' + Z0'),'0'],
            [lfrac('2\\cdot '+G+' \\cdot '+Zi+' \\cdot Z0',' ( '+Zi+' +Z0 )\\cdot ( '+Zo+' + Z0 )'),lfrac(Zo+' - Z0',Zo+' + Z0')]]
