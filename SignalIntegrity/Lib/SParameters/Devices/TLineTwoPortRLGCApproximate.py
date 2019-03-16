"""telegraphers numerical approximate transmission line"""

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

from SignalIntegrity.Lib.SParameters.SParameters import SParameters

class TLineTwoPortRLGCApproximate(SParameters):
    """s-parameters of two port RLGC (telegrapher's) transmission line
    calculated by approximating distributed parameters with a finite number
    of sections specified."""
    rtFraction=.01
    def __init__(self,f, R, Rse, L, G, C, df, Z0=50., K=0):
        """Constructor
        @param f list of float frequencies
        @param R float DC series resistance (Ohms)
        @param Rse float series skin-effect resistance (Ohms/sqrt(Hz))
        @param L float series inductance (H)
        @param G float DC conductance to ground (S)
        @param C float capacitance to ground (F)
        @param df float dissipation factor (loss-tangent) of capacitance to ground
        @param Z0 (optional) float reference impedance (defaults to 50 Ohms)
        @param K (optional) integer number of sections (defaults to zero)
        @note If K=0 is specified, it is modified to a value that will provided a very good numerical
        approximation.

        The calculation is such that round-trip propagation time (twice the electrical length)
        of any one small section is no more than one percent of the fastest possible risetime.
        """
        if K==0:
            """max possible electrical length"""
            Td=math.sqrt(L*C)
            Rt=0.45/f[-1] # fastest risetime
            """sections such that fraction of risetime less than round trip
            electrical length of one section"""
            K=int(math.ceil(Td*2/(Rt*self.rtFraction)))

        self.m_K=K
        # pragma: silent exclude
        from SignalIntegrity.Lib.Devices import SeriesZ
        from SignalIntegrity.Lib.Devices import TerminationG
        from SignalIntegrity.Lib.SParameters.Devices.TerminationC import TerminationC
        from SignalIntegrity.Lib.SParameters.Devices.SeriesL import SeriesL
        from SignalIntegrity.Lib.SParameters.Devices.SeriesRse import SeriesRse
        from SignalIntegrity.Lib.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
        from SignalIntegrity.Lib.Parsers.SystemDescriptionParser import SystemDescriptionParser
        # pragma: include
        sdp=SystemDescriptionParser().AddLines(['device R 2','device Rse 2',
        'device L 2','device C 1','device G 1','connect R 2 Rse 1',
        'connect Rse 2 L 1','connect L 2 G 1 C 1','port 1 R 1 2 G 1'])
        self.m_sspn=SystemSParametersNumeric(sdp.SystemDescription())
        self.m_sspn.AssignSParameters('R',SeriesZ(R/K,Z0))
        self.m_sspn.AssignSParameters('G',TerminationG(G/K,Z0))
        self.m_spdl=[('Rse',SeriesRse(f,Rse/K,Z0)),
                     ('L',SeriesL(f,L/K,Z0)),
                     ('C',TerminationC(f,C/K,Z0,df))]
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        # pragma: silent exclude
        from numpy import linalg
        from SignalIntegrity.Lib.Conversions import S2T
        from SignalIntegrity.Lib.Conversions import T2S
        # pragma: include
        for ds in self.m_spdl: self.m_sspn.AssignSParameters(ds[0],ds[1][n])
        sp=self.m_sspn.SParameters()
        return T2S(linalg.matrix_power(S2T(sp),self.m_K))
