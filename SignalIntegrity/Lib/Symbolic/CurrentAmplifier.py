"""
CurrentAmplifier.py
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

def CurrentAmplifier(P,G,Zi,Zo):
    """symbolic 2,3, and 4 port current amplifier
    @param P integer number of ports (2,3,4)\n
    if ports are 2, then returns SignalIntegrity.Symbolic.CurrentAmplifier.CurrentAmplifierTwoPort\n
    if ports are 3, then returns SignalIntegrity.Symbolic.CurrentAmplifier.CurrentAmplifierThreePort\n
    if ports are 4, then returns SignalIntegrity.Symbolic.CurrentAmplifier.CurrentAmplifierFourPort
    @param G string current gain
    @param Zi string input impedance
    @param Zo string output impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    """
    if P==2:
        return CurrentAmplifierTwoPort(G,Zi,Zo)
    elif P==3:
        return CurrentAmplifierThreePort(G,Zi,Zo)
    elif P==4:
        return CurrentAmplifierFourPort(G,Zi,Zo)

def CurrentAmplifierFourPort(G,Zi,Zo):
    """symbolic four port current amplifier
    @param G string current gain
    @param Zi string input impedance
    @param Zo string output impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.CurrentAmplifier.CurrentAmplifierFourPort
    """
    return [[lfrac(Zi,Zi+'+2\\cdot Z0'),lfrac('2\\cdot Z0',Zi+'+2\\cdot Z0'),'0','0'],
            [lfrac('2\\cdot Z0',Zi+'+2\\cdot Z0'),lfrac(Zi,Zi+'+2\\cdot Z0'),'0','0'],
            [lfrac('2\\cdot '+Zo+'\\cdot Z0\\cdot '+G,' ('+Zi+'+2\\cdot Z0 )\\cdot ('+Zo+'+2\\cdot Z0 )'),
            '-'+lfrac('2\\cdot '+Zo+'\\cdot Z0\\cdot '+G,' ('+Zi+'+2\\cdot Z0 )\\cdot ('+Zo+'+2\\cdot Z0 )'),
            lfrac(Zo,Zo+'+2\\cdot Z0'),lfrac('2\\cdot Z0',Zo+'+2\\cdot Z0')],
            ['-'+lfrac('2\\cdot '+Zo+'\\cdot Z0\\cdot '+G,' ('+Zi+'+2\\cdot Z0 )\\cdot ('+Zo+'+2\\cdot Z0 )'),
            lfrac('2\\cdot '+Zo+'\\cdot Z0\\cdot '+G,' ('+Zi+'+2\\cdot Z0 )\\cdot ('+Zo+'+2\\cdot Z0 )'),
            lfrac('2\\cdot Z0',Zo+'+2\\cdot Z0'),lfrac(Zo,Zo+'+2\\cdot Z0')]]

def CurrentAmplifierThreePort(G,Zi,Zo):
    """symbolic three port current amplifier
    @param G string current gain
    @param Zi string input impedance
    @param Zo string output impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.CurrentAmplifier.CurrentAmplifierThreePort
    """
    D='3\\cdot Z0^2+ (2\\cdot '+Zo+'+2\\cdot '+Zi+'-'+G+'\\cdot '+Zo+' )\\cdot Z0+'+Zo+'\\cdot '+Zi
    S11=lfrac(Zo+'\\cdot '+Zi+'+Z0\\cdot  (2\\cdot '+Zi+'-'+G+'\\cdot '+Zo+' )-Z0^2',D)
    S12=lfrac('2\\cdot Z0^2',D)
    S13=lfrac('2\\cdot Z0^2+2\\cdot '+Zo+'\\cdot Z0',D)
    S21=lfrac('2\\cdot Z0^2+2\\cdot '+G+'\\cdot '+Zo+'\\cdot Z0',D)
    S22=lfrac(Zo+'\\cdot '+Zi+'+Z0\\cdot  (2\\cdot '+Zo+'-'+G+'\\cdot '+Zo+' )-Z0^2',D)
    S23=lfrac('2\\cdot Z0^2+Z0\\cdot  (2\\cdot '+Zi+'-2\\cdot '+G+'\\cdot '+Zo+' )',D)
    S31=lfrac('2\\cdot Z0^2+Z0\\cdot  (2\\cdot '+Zo+'-2\\cdot '+G+'\\cdot '+Zo+' )',D)
    S32=lfrac('2\\cdot Z0^2+2\\cdot '+Zi+'\\cdot Z0',D)
    S33=lfrac(Zo+'\\cdot '+Zi+'-Z0^2+'+G+'\\cdot '+Zo+'\\cdot Z0',D)
    return [[S11,S12,S13],
            [S21,S22,S23],
            [S31,S32,S33]]

def CurrentAmplifierThreePortWithoutDenom(G,Zi,Zo):
    """symbolic three port current amplifier without denominator
    @param G string current gain
    @param Zi string input impedance
    @param Zo string output impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.CurrentAmplifier.CurrentAmplifierThreePort
    @remark this returns the s-parameter matrix without the denominator element
    @see CurrentAmplifierThreePortDenom
    """
    S11=Zo+'\\cdot '+Zi+'+Z0\\cdot  (2\\cdot '+Zi+'-'+G+'\\cdot '+Zo+' )-Z0^2'
    S12='2\\cdot Z0^2'
    S13='2\\cdot Z0^2+2\\cdot '+Zo+'\\cdot Z0'
    S21='2\\cdot Z0^2+2\\cdot '+G+'\\cdot '+Zo+'\\cdot Z0'
    S22=Zo+'\\cdot '+Zi+'+Z0\\cdot  (2\\cdot '+Zo+'-'+G+'\\cdot '+Zo+' )-Z0^2'
    S23='2\\cdot Z0^2+Z0\\cdot  (2\\cdot '+Zi+'-2\\cdot '+G+'\\cdot '+Zo+' )'
    S31='2\\cdot Z0^2+Z0\\cdot  (2\\cdot '+Zo+'-2\\cdot '+G+'\\cdot '+Zo+' )'
    S32='2\\cdot Z0^2+2\\cdot '+Zi+'\\cdot Z0'
    S33=Zo+'\\cdot '+Zi+'-Z0^2+'+G+'\\cdot '+Zo+'\\cdot Z0'
    return [[S11,S12,S13],
            [S21,S22,S23],
            [S31,S32,S33]]

def CurrentAmplifierThreePortDenom(G,Zi,Zo):
    """symbolic three port current amplifier denominator
    @param G string current gain
    @param Zi string input impedance
    @param Zo string output impedance
    @return the denominator element common in the s-parameter matrix as a string
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.CurrentAmplifier.CurrentAmplifierThreePort
    @see CurrentAmplifierThreePortWithoutDenom
    """
    D='3\\cdot Z0^2+ (2\\cdot '+Zo+'+2\\cdot '+Zi+'-'+G+'\\cdot '+Zo+' )\\cdot Z0+'+Zo+'\\cdot '+Zi
    return D

def CurrentAmplifierTwoPort(G,Zi,Zo):
    """symbolic two port current amplifier
    @param G string current gain
    @param Zi string input impedance
    @param Zo string output impedance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of SignalIntegrity.Lib.Devices.CurrentAmplifier.CurrentAmplifierTwoPort
    """
    return [[lfrac(Zi+' - Z0',Zi+' + Z0'),'0'],
            [lfrac('2\\cdot '+G+' \\cdot '+Zo+' \\cdot Z0',' ( '+Zi+' +Z0 )\\cdot ( '+Zo+' + Z0 )'),lfrac(Zo+' - Z0',Zo+' + Z0')]]
