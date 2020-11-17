"""Equalizer"""

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

from SignalIntegrity.Lib.SParameters.SParameters import SParameters

import cmath

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

class FFE(SParameters):
    """Linear feed-forward equalizer"""
    def __init__(self,f,Td,taps,numPreCursorTaps,Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param Td float time delay of each tap
        @param taps list of float values of the taps
        @param numPreCursorTaps integer number of precursor taps
        @param Z0 float (optional, defaults to 50) reference impedance
        @remark Usually Td is the reciprocal of the baud rate or sometimes, half the reciprocal.
        """
        self.Td=Td
        self.taps=taps
        self.PC=numPreCursorTaps
        SParameters.__init__(self,f,None,Z0)
    def _Evaluate(self,f):
        """Evaluate FFE
        @param f float frequency
        @return FFE evaluated at f
        """
        K=len(self.taps)
        return sum([self.taps[k]*cmath.exp(1j*2.*cmath.pi*f*-(k-self.PC)*self.Td) for k in range(K)])
    def __getitem__(self,n):
        return [[1.,0],[2.*self._Evaluate(self.m_f[n]),-1.]]
