"""RLGC uncoupled differential transmission line"""

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

class TLineDifferentialRLGCUncoupled(SParameters):
    """s-parameters of analytic uncoupled differential RLGC (telegrapher's) transmission
    line."""
    def __init__(self,f,Rp,Rsep,Lp,Gp,Cp,dfp,Rn,Rsen,Ln,Gn,Cn,dfn,Z0=50.,K=0):
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
        @param Z0 (optional) float reference impedance (defaults to 50 Ohms)
        @param K (optional) integer number of sections (defaults to 0).
        If 0 is specified, then an analytic solution is provided otherwise an approximate solution is provided
        with all parametric values divided into the integer number of sections.
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.Parsers.SystemDescriptionParser import SystemDescriptionParser
        from SignalIntegrity.Lib.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
        from SignalIntegrity.Lib.SParameters.Devices.TLineTwoPortRLGC import TLineTwoPortRLGC
        # pragma: include
        sdp=SystemDescriptionParser()
        sdp.AddLines(['device TP 2','device TN 2',
                      'port 1 TP 1 2 TN 1 3 TP 2 4 TN 2'])
        self.m_sspn=SystemSParametersNumeric(sdp.SystemDescription())
        self.m_spdl=[('TP',TLineTwoPortRLGC(f,Rp,Rsep,Lp,Gp,Cp,dfp,Z0,K)),
                     ('TN',TLineTwoPortRLGC(f,Rn,Rsen,Ln,Gn,Cn,dfn,Z0,K))]
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        for ds in self.m_spdl:
            self.m_sspn.AssignSParameters(ds[0],ds[1][n])
        return self.m_sspn.SParameters()