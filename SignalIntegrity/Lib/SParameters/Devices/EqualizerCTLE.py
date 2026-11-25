"""EqualizerCTLE"""

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

from SignalIntegrity.Lib.SParameters.SParameters import SParameters
import math

class CTLE(SParameters):
    """Continuous time linear equalizer"""
    def __init__(self,f,gDC,gDC2,fz,fLF,fp1,fp2,Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param gDC float DC gain in dB
        @param gDC2 float DC gain at peaking point in dB
        @param fz float frequency of zero
        @param fLF float LF frequency
        @param fp1 float first pole frequency
        @param fp2 float second pole frequency
        @param Z0 float (optional, defaults to 50) reference impedance
        """
        self.powgDC=pow(10.,gDC/20.); self.powgDC2=pow(10.,gDC2/20.)
        self.joverfz=1j/fz; self.joverfLF=1j/fLF; self.joverfp1=1j/fp1; self.joverfp2=1j/fp2
        SParameters.__init__(self,f,None,Z0)
    def _Evaluate(self,f):
        """Evaluate CTLE
        @param f float frequency
        @return CTLE evaluated at f
        """
        N=(self.powgDC+self.joverfz*f)*(self.powgDC2+self.joverfLF*f)
        D=(1.+self.joverfp1*f)*(1.+self.joverfp2*f)*(1.+self.joverfLF*f)
        return N/D
    def __getitem__(self,n):
        return [[1.,0],[2.*self._Evaluate(self.m_f[n]),-1.]]

class CTLE_standard(CTLE):
    """CTLE with zero and pole frequencies defined as baud-rate fractions."""
    def __init__(self,f,baudRate,gDC=-2.,gDC2=0.,fz_divisor=2.5,
                 flf_divisor=80.,fp1_divisor=2.5,fp2_divisor=1.,Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param baudRate float positive baud rate
        @param gDC float DC gain in dB (defaults to -2)
        @param gDC2 float DC gain at peaking point in dB (defaults to 0)
        @param fz_divisor float positive scaled-zero divisor (defaults to 2.5)
        @param flf_divisor float positive LF divisor (defaults to 80)
        @param fp1_divisor float positive first-pole divisor (defaults to 2.5)
        @param fp2_divisor float positive second-pole divisor (defaults to 1)
        @param Z0 float reference impedance (defaults to 50)
        """
        if not math.isfinite(baudRate) or baudRate<=0:
            raise ValueError('baud rate must be positive and finite')
        for name,value in [('fz_divisor',fz_divisor),('flf_divisor',flf_divisor),
                           ('fp1_divisor',fp1_divisor),('fp2_divisor',fp2_divisor)]:
            if not math.isfinite(value) or value<=0:
                raise ValueError(name+' must be positive and finite')
        CTLE.__init__(self,f,gDC,gDC2,baudRate/fz_divisor,baudRate/flf_divisor,
                      baudRate/fp1_divisor,baudRate/fp2_divisor,Z0)
