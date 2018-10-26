"""RLGC balanced differential transmission line"""

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

class TLineDifferentialRLGCBalanced(SParameters):
    """s-parameters of analytic balanced differential RLGC (telegrapher's) transmission
    line."""
    def __init__(self,f,R,Rse,L,G,C,df,Cm,dfm,Gm,Lm,Z0=50.,K=0):
        """Constructor

        ports are 1,2,3,4 is +1,-1, +2, -2

        @param f list of float frequencies
        @param R float DC resistance of both legs (Ohms)
        @param Rse float skin-effect resistance of both legs (Ohms/sqrt(Hz))
        @param L float inductance of both legs (H)
        @param G float DC conductance of both legs to ground (S)
        @param C float capacitance of both legs to ground (F)
        @param df float dissipation factor (loss-tangent) of capacitance of both legs to ground
        @param Cm float mutual capacitance (F)
        @param dfm float dissipation factor (loss-tangent) of mutual capacitance (F)
        @param Gm float mutual conductance (S)
        @param Lm float mutual inductance (H)
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
        sdp.AddLines(['device L 4 mixedmode','device R 4 mixedmode','device TE 2',
                      'device TO 2','port 1 L 1 2 L 2 3 R 1 4 R 2','connect L 3 TO 1',
                      'connect R 3 TO 2','connect L 4 TE 1','connect R 4 TE 2'])
        self.m_sspn=SystemSParametersNumeric(sdp.SystemDescription())
        self.m_spdl=[('TE',TLineTwoPortRLGC(f,R,Rse,L+Lm,G,C,df,Z0,K)),
                     ('TO',TLineTwoPortRLGC(f,R,Rse,L-Lm,G+2*Gm,C+2*Cm,
                                        (C*df+2*Cm*dfm)/(C+2*Cm),Z0,K))]
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        for ds in self.m_spdl: self.m_sspn.AssignSParameters(ds[0],ds[1][n])
        return self.m_sspn.SParameters()