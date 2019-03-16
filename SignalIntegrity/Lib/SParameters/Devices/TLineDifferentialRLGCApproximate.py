"""telegraphers equation approximate differential transmission line"""

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

from numpy import linalg
import math

from SignalIntegrity.Lib.Conversions import S2T
from SignalIntegrity.Lib.Conversions import T2S
from SignalIntegrity.Lib.SParameters.SParameters import SParameters

class TLineDifferentialRLGCApproximate(SParameters):
    """s-parameters of differential RLGC (telegrapher's) transmission line
    calculated by approximating distributed parameters with a finite number
    of sections specified."""
    rtFraction=.01
    def __init__(self,f, Rp, Rsep, Lp, Gp, Cp, dfp,
                         Rn, Rsen, Ln, Gn, Cn, dfn,
                         Cm, dfm, Gm, Lm, Z0=50., K=0):
        """Constructor

        ports are 1,2,3,4 is +1,-1, +2, -2

        @param f list of float frequencies
        @param Rp float DC resistance of positive leg (Ohms)
        @param Rsep float skin-effect resistance of positive leg (Ohms/sqrt(Hz))
        @param Lp float inductance of positive leg (H)
        @param Gp float DC conductance of positive leg to ground (S)
        @param Cp float capacitance of positive leg to ground (F)
        @param dfp float dissipation factor (loss-tangent) of capacitance of positive leg to ground
        @param Rn float DC resistance of negative leg (Ohms)
        @param Rsen float skin-effect resistance of negative leg (Ohms/sqrt(Hz))
        @param Ln float inductance of negative leg (H)
        @param Gn float DC conductance of negative leg to ground (S)
        @param Cn float capacitance of negative leg to ground (F)
        @param dfn float dissipation factor (loss-tangent) of capacitance of negative leg to ground
        @param Cm float mutual capacitance (F)
        @param dfm float dissipation factor (loss-tangent) of mutual capacitance (F)
        @param Gm float mutual conductance (S)
        @param Lm float mutual inductance (H)
        @param Z0 (optional) float reference impedance (defaults to 50 Ohms)
        @param K (optional) integer number of sections (defaults to 0)
        @note If K=0 is specified, it is modified to a value that will provided a very good numerical
        approximation.

        The calculation is such that round-trip propagation time (twice the electrical length)
        of any one small section is no more than one percent of the fastest possible risetime.
        """
        if K==0:
            """max possible electrical length"""
            Td=math.sqrt((max(Lp,Ln)+Lm)*(max(Cp,Cn)+2*Cm))
            Rt=0.45/f[-1] # fastest risetime
            """sections such that fraction of risetime less than round trip electrical
            length of one section"""
            K=int(math.ceil(Td*2/(Rt*self.rtFraction)))

        self.m_K=K
        # pragma: silent exclude
        from SignalIntegrity.Lib.Devices import SeriesG
        from SignalIntegrity.Lib.Devices import SeriesZ
        from SignalIntegrity.Lib.Devices import TerminationG
        import SignalIntegrity.Lib.SParameters.Devices as dev
        from SignalIntegrity.Lib.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
        from SignalIntegrity.Lib.Parsers.SystemDescriptionParser import SystemDescriptionParser
        # pragma: include
        sdp=SystemDescriptionParser().AddLines([
        'device rsep 2','device rp 2','device lp 2','device gp 1','device cp 1',
        'device rsen 2','device rn 2','device ln 2','device gn 1','device cn 1',
        'device lm 4','device gm 2','device cm 2',
         'connect rp 2 rsep 1','connect rsep 2 lp 1',
         'connect rn 2 rsen 1','connect rsen 2 ln 1',
         'connect lp 2 lm 1','connect ln 2 lm 3',
         'connect lm 2 gp 1 cp 1 gm 1 cm 1','connect lm 4 gn 1 cn 1 gm 2 cm 2',
         'port 1 rp 1 2 rn 1 3 lm 2 4 lm 4'])
        self.m_sspn=SystemSParametersNumeric(sdp.SystemDescription())
        self.m_sspn.AssignSParameters('rp',SeriesZ(Rp/K,Z0))
        self.m_sspn.AssignSParameters('gp',TerminationG(Gp/K,Z0))
        self.m_sspn.AssignSParameters('rn',SeriesZ(Rn/K,Z0))
        self.m_sspn.AssignSParameters('gn',TerminationG(Gn/K,Z0))
        self.m_sspn.AssignSParameters('gm',SeriesG(Gm/K,Z0))
        self.m_spdl=[('rsep',dev.SeriesRse(f,Rsep/K,Z0)),
            ('lp',dev.SeriesL(f,Lp/K,Z0)),('cp',dev.TerminationC(f,Cp/K,Z0,dfp)),
            ('rsen',dev.SeriesRse(f,Rsen/K,Z0)),('ln',dev.SeriesL(f,Ln/K,Z0)),
            ('cn',dev.TerminationC(f,Cn/K,Z0,dfn)),('lm',dev.Mutual(f,Lm/K,Z0)),
            ('cm',dev.SeriesC(f,Cm/K,Z0,dfm))]
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        for ds in self.m_spdl:
            self.m_sspn.AssignSParameters(ds[0],ds[1][n])
        sp=self.m_sspn.SParameters()
        if sp == 1: return sp
        lp=[1,2]; rp=[3,4]
        return T2S(linalg.matrix_power(S2T(sp,lp,rp),self.m_K),lp,rp)
