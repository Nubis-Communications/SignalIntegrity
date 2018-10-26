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

def OperationalAmplifier(Zi,Zd,Zo,G,Z0=50.):
    """OperationalAmplifier
    Operational Amplifier
    @param Zi real or complex input impedance between each plus and minus input port
    to ground.
    @param Zd real or complex input impedance across the plus and minus inputs.
    @param Zo real or complex output impedance.
    @param G real or complex gain of the op-amp.
    @param Z0 (optional) real or complex reference impedance (default is 50 Ohms).
    @return the list of list s-parameter matrix of the s-parameters of a three port op-amp.
    Port 1 is - input, port 2 is + input and port 3 is output
    """
    S11=((-2.*Zi-Zd)*Z0*Z0+Zi*Zi*Zd)/((2.*Zi+Zd)*Z0*Z0+(2.*Zi*Zd+2.*Zi*Zi)*Z0+Zi*Zi*Zd)
    S12=(2.*Zi*Zi*Z0)/((2.*Zi+Zd)*Z0*Z0+(2.*Zi*Zd+2.*Zi*Zi)*Z0+Zi*Zi*Zd)
    S32=2.*G*Zi*Zd*Z0/((Zo+Z0)*((2.*Zi+Zd)*Z0+Zi*Zd))
    S33=(Zo-Z0)/(Zo+Z0)
    return [[S11,S12,0.],[S12,S11,0.],[-S32,S32,S33]]