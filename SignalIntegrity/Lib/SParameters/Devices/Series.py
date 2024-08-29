"""two-port device placed in series with multiple instances"""

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

import numpy as np
from SignalIntegrity.Lib.SParameters.SParameters import SParameters

class Series(SParameters):
    """s-parameters of two port device placed in series with itself multiple times"""
    def __init__(self,f: float, name: str, numberInSeries: float, lp: list =[1], rp: list =[2], Z0: float =50, **kwargs):
        """Constructor
        @param f list of float frequencies
        @param name string file name of s-parameter file to read
        @param numberInSeries float number of instances to place in series
        @param lp list of ints left ports in order
        @param rp list of ints right ports in order
        @param Z0 (optional) float reference impedance (defaults to 50 ohms)
        @param **kwargs dict (optional, defaults to {}) dictionary of arguments for the file
        @remark The number of left ports ought to equal the number of right ports, otherwise you should
        expect this fail.
        """
        self.m_K=numberInSeries
        # pragma: silent exclude
        from SignalIntegrity.Lib.SParameters.SParameterFile import SParameterFile
        # pragma: include
        self.lp=lp
        self.rp=rp
        self.m_dev=SParameterFile(name,None,None,**kwargs).Resample(f).SetReferenceImpedance(Z0)
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n: int):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        # pragma: silent exclude
        from scipy import linalg
        from SignalIntegrity.Lib.Conversions import S2T
        from SignalIntegrity.Lib.Conversions import T2S
        from SignalIntegrity.Lib.Conversions import ReferenceImpedance
        # pragma: include
        try:
            sp=T2S(linalg.fractional_matrix_power(S2T(self.m_dev[n],self.lp,self.rp),self.m_K),self.lp,self.rp)
            sp=ReferenceImpedance(sp,self.m_Z0,self.m_dev.m_Z0)
        except np.linalg.LinAlgError:
            P=len(self.lp)+len(self.rp)
            sp=[[0 for _ in range(P)] for __ in range(P)]
        return sp
