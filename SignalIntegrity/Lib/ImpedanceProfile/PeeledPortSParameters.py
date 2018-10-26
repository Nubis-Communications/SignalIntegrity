"""
 peeled s-parameters
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
import math
from numpy import matrix,identity

from SignalIntegrity.Lib.Conversions import S2T,T2S
from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.Devices.TLineTwoPortLossless import TLineTwoPortLossless
from SignalIntegrity.Lib.ImpedanceProfile.ImpedanceProfileWaveform import ImpedanceProfileWaveform

class PeeledPortSParameters(SParameters):
    """s-parameters of peeled impedance profile from port
    calculates the impedance profile looking into a port of a device and then assembles
    a transmission line as a cascade of small transmission line sections
    """
    def __init__(self,sp,port,timelen,method='estimated'):
        """Constructor
        @param sp instance of class SParameters of the device
        @param port integer 1 based port to calculate
        @param timelen float time to peel
        @param method string determining method for computing impedance profile
        @remark methods include:
        'estimated' (default) estimate the impedance profile from simulated step response.
        'approximate' use the approximation based on the simulated step response.
        'exact' use the impedance peeling algorithm.
        """
        ip=ImpedanceProfileWaveform(sp,port,method,includePortZ=False)
        Ts=1./ip.td.Fs; sections=int(math.floor(timelen/Ts+0.5))
        tp1=[identity(2) for n in range(len(sp.f()))]
        for k in range(sections):
            tp1=[tp1[n]*matrix(S2T(TLineTwoPortLossless(ip[k],Ts,sp.m_f[n])))
                for n in range(len(sp.m_f))]
        SParameters.__init__(self,sp.m_f,[T2S(tp.tolist()) for tp in tp1])