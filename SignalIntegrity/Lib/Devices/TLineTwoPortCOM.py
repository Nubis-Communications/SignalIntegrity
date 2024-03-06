"""
TLineTwoPortCOM.py
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
import cmath,math
from SignalIntegrity.Lib.Devices.TLineTwoPort import TLineTwoPort

def TLineTwoPortCOM(f,gamma_0,a_1,a_2,tau,Zc,d,Z0=50.):
    """TLineTwoPortCOM
    COM Two-port Transmission Line
    @param f float frequency in Hz
    @param gamma_0 float transmission line gamma_0 in units 1/mm
    @param a_1 float transmission line parameter in units sqrt(ns)/mm
    @param a_2 float transmission line parameter in units ns/mm
    @param tau float transmission line parameter in units ns/mm
    @param Z_c float differential mode characterisitic impedance in units of ohms
    @param d float length in units mm 
    @param Z0 (optional) float or complex reference impedance Z0 (defaults to 50 ohms).
    @return the s-parameter matrix of a COM defined two-port transmission line  
    @see https://www.ieee802.org/3/bj/public/mar14/healey_3bj_01_0314.pdf
    """
    f_GHz = f/1e9
    if f == 0:
        gamma = 0
    else:
        gamma_1 = a_1*(1+1j)
        gamma_2 = a_2*(1-1j*2./math.pi*math.log(f_GHz))+1j*2*math.pi*tau
        gamma = gamma_0+gamma_1*math.sqrt(f_GHz)+gamma_2*f_GHz
    return TLineTwoPort(Zc/2.,gamma*d,Z0)
