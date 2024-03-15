"""
TransresistanceAmplifier.py
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

from SignalIntegrity.Lib.Helpers.lfrac import lfrac

def TransresistanceAmplifier(P,G,Zi,Zo):
    """symbolic 2,3, and 4 port transresistance amplifier
    @param P integer number of ports (2,3,4)\n
    if ports are 2, then returns SignalIntegrity.Symbolic.TransresistanceAmplifier.TransresistanceAmplifierTwoPort\n
    if ports are 3, then returns SignalIntegrity.Symbolic.TransresistanceAmplifier.TransresistanceAmplifierThreePort\n
    if ports are 4, then returns SignalIntegrity.Symbolic.TransresistanceAmplifier.TransresistanceAmplifierFourPort
    @param G string transresistance
    @param Zi string input impedance
    @param Zo string output impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    """
    if P==2:
        return TransresistanceAmplifierTwoPort(G,Zi,Zo)
    elif P==3:
        return TransresistanceAmplifierThreePort(G,Zi,Zo)
    elif P==4:
        return TransresistanceAmplifierFourPort(G,Zi,Zo)

def TransresistanceAmplifierFourPort(G,Zi,Zo):
    """symbolic four port transresistance amplifier
    @param G string transresistance
    @param Zi string input impedance
    @param Zo string output impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.TransresistanceAmplifier.TransresistanceAmplifierFourPort
    """
    D11=lfrac(Zi,Zi+'+2\\cdot Z0')
    D12=lfrac('2\\cdot Z0',Zi+'+2\\cdot Z0')
    D31=lfrac('2\\cdot '+G+'\\cdot Z0',' ('+Zo+'+2\\cdot Z0 )\\cdot ('+Zi+'+2\\cdot Z0 )')
    D33=lfrac(Zo,Zo+'+2\\cdot Z0')
    D34=lfrac('2\\cdot Z0',Zo+'+2\\cdot Z0')
    return [[D11,D12,'0','0'],
            [D12,D11,'0','0'] ,
            [D31,'-'+D31,D33,D34],
            ['-'+D31,D31,D34,D33]]

def TransresistanceAmplifierThreePort(G,Zi,Zo):
    """symbolic three port transresistance amplifier
    @param G string transresistance
    @param Zi string input impedance
    @param Zo string output impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.TransresistanceAmplifier.TransresistanceAmplifierThreePort
    """
    D='3\\cdot Z0^2+ (2\\cdot '+Zo+'+2\\cdot '+Zi+'-'+G+' )\\cdot Z0+'+Zo+'\\cdot '+Zi
    S11=lfrac(Zo+'\\cdot '+Zi+'+Z0\\cdot  (2\\cdot '+Zi+'-'+G+' )-Z0^2',D)
    S12=lfrac('2\\cdot Z0^2',D)
    S13=lfrac('2\\cdot Z0^2+2\\cdot '+Zo+'\\cdot Z0',D)
    S21=lfrac('2\\cdot Z0^2+2\\cdot '+G+'\\cdot Z0',D)
    S22=lfrac(Zo+'\\cdot '+Zi+'+Z0\\cdot  (2\\cdot '+Zo+'-'+G+' )-Z0^2',D)
    S23=lfrac('2\\cdot Z0^2+Z0\\cdot  (2\\cdot '+Zi+'-2\\cdot '+G+' )',D)
    S31=lfrac('2\\cdot Z0^2+Z0\\cdot  (2\\cdot '+Zo+'-2\\cdot '+G+' )',D)
    S32=lfrac('2\\cdot Z0^2+2\\cdot '+Zi+'\\cdot Z0',D)
    S33=lfrac(Zo+'\\cdot '+Zi+'-Z0^2+'+G+'\\cdot Z0',D)
    return [[S11,S12,S13],
            [S21,S22,S23],
            [S31,S32,S33]]

def TransresistanceAmplifierTwoPort(G,Zi,Zo):
    """symbolic two port transresistance amplifier
    @param G string transresistance
    @param Zi string input impedance
    @param Zo string output impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.TransresistanceAmplifier.TransresistanceAmplifierTwoPort
    """
    return [[lfrac(Zi+' - Z0',Zi+' + Z0'),'0'],
            [lfrac('2\\cdot '+G+' \\cdot Z0',' ( '+Zi+' +Z0 )\\cdot ( '+Zo+' + Z0 )'),lfrac(Zo+' - Z0',Zo+' + Z0')]]
