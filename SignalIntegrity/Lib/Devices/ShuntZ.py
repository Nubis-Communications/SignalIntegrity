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
from numpy import array

from SignalIntegrity.Lib.Conversions import Z0KHelper

# pragma: silent exclude
def ShuntZZ0K(Z,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),2)
    Z01=Z0.item(0,0)
    Z02=Z0.item(1,1)
    K1=K.item(0,0)
    K2=K.item(1,1)
    partial=array([[Z*(Z02-Z01)-Z01*Z02,2*K2/K1*Z01*Z],[2*K1/K2*Z02*Z,Z*(Z01-Z02)-Z01*Z02]])
    return (partial*1./(Z01*Z02+Z*(Z01+Z02))).tolist()

def ShuntZ(ports,Z,Z0=50.):
    """ShuntZ
    Shunt impedance
    @param ports integer number of ports
    @param Z real or complex impedance of two-port impedance.
    @param Z0 (optional) real or complex reference impedance (defaults to 50 Ohms).
    @return list of list s-parameter matrix of a shunt impedance.\n
    @see ShuntZTwoPort
    @see ShuntZThreePort
    @see ShuntZFourPort
    """
    if ports == 2: return ShuntZTwoPort(Z,Z0)
    elif ports == 3: return ShuntZThreePort(Z,Z0)
    elif ports == 4: return ShuntZFourPort(Z,Z0)
# pragma: include
def ShuntZTwoPort(Z,Z0=50.):
    """ShuntZTwoPort
    Two port shunt impedance
    @param Z real or complex impedance of two-port impedance.
    @param Z0 (optional) real or complex reference impedance (defaults to 50 Ohms).
    @return list of list s-parameter matrix of a shunt impedance.\n
    @remark Ports 1 and 2 are connected together and to one side of the impedance.\n
    The other side of the impedance is tied to ground.
    """
    return [[-Z0*Z0/(Z0*Z0+2.*Z*Z0),2.*Z0*Z/(Z0*Z0+2.*Z*Z0)],
        [2.*Z0*Z/(Z0*Z0+2.*Z*Z0),-Z0*Z0/(Z0*Z0+2.*Z*Z0)]]
# pragma: silent exclude
def ShuntZFourPort(Z,Z0=50.):
    """ShuntZFourPort
    Four port shunt impedance
    @param Z real or complex impedance of two-port impedance.
    @param Z0 (optional) real or complex reference impedance (defaults to 50 Ohms).
    @return list of list s-parameter matrix of a shunt impedance.\n
    @remark Ports 1 and 3 are connected to port 1 of the device D provided.\n
    Ports 2 and 4 are connected to port 2 of the device D provided.\n
    @todo check the port numbering
    """
    D=2.*(Z+Z0)
    return [[-Z0/D,Z0/D,(2.*Z+Z0)/D,Z0/D],
        [Z0/D,-Z0/D,Z0/D,(2.*Z+Z0)/D],
        [(2.*Z+Z0)/D,Z0/D,-Z0/D,Z0/D],
        [Z0/D,(2.*Z+Z0)/D,Z0/D,-Z0/D]]

def ShuntZThreePort(Z,Z0=50.):
    """ShuntZThreePort
    Three port shunt impedance
    @param Z real or complex impedance of two-port impedance.
    @param Z0 (optional) real or complex reference impedance (defaults to 50 Ohms).
    @return list of list s-parameter matrix of a shunt impedance.\n
    @remark Ports 1 and 2 are connected together and to port 1 impedance.\n
    Port 3 is the other port of the impedance.\n
    @todo check the port numbering
    """
    D=2.*Z+3.*Z0
    return [[-Z0/D,(2.*Z+2.*Z0)/D,2.*Z0/D],
            [(2.*Z+2.*Z0)/D,-Z0/D,2.*Z0/D],
            [2.*Z0/D,2.*Z0/D,(2.*Z-Z0)/D]]

