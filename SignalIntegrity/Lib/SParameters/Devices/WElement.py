"""W Element"""

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
import sys

from SignalIntegrity.Lib.Conversions import S2T
from SignalIntegrity.Lib.Conversions import T2S
from SignalIntegrity.Lib.SParameters.SParameters import SParameters

class MaxwellMatrix(list):
    """A Maxwell matrix is a lower triangular matrix that is related to the mutual matrix."""
    def __init__(self,MM):
        """Constructor
        @param MM lower triangular list of list Maxwell matrix
        """
        list.__init__(self,MM)
    def MutualMatrix(self):
        """Mutual matrix
        @return a lower triangular mutual matrix
        """
        wires=len(self)
        Mm=[[None for _ in range(w+1)] for w in range(wires)]
        for r in range(wires):
            Mm[r][r]=sum([self[r][c] if r >= c else self[c][r] for c in range(wires)])
            for c in range(r): Mm[r][c]=-self[r][c]
        return MutualMatrix(Mm)

class MutualMatrix(list):
    """A mutual matrix is a lower triangular matrix that is related to the Maxwell matrix."""
    def __init__(self,Mm):
        """Constructor
        @param Mm lower triangular list of list mutual matrix
        """
        list.__init__(self,Mm)
    def MaxwellMatrix(self):
        """Maxwell matrix
        @return a lower triangular Maxwell matrix
        """
        wires=len(self)
        MM=[[None for _ in range(w+1)] for w in range(wires)]
        for r in range(wires):
            MM[r][r]=sum([(self[r][c] if r >= c else self[c][r]) for c in range(wires)])
            for c in range(r): MM[r][c]=-self[r][c]
        return MaxwellMatrix(MM)

class WElement(SParameters):
    """s-parameters of of a W element is
    calculated by approximating distributed parameters with a finite number
    of sections specified."""
    rtFraction=.01
    def __init__(self,f, wires, R, Rse, df, Cm, Gm, Lm, Z0=50., K=0, scale=1.):
        """Constructor  
        ports are 1,2,3,4, etc. on left and W, W+1, W+2, W+4, etc. on right where W=wires
        and wire 1 is port 1 to P, wire 2 is port 2 to (P+1), etc.  This is a P=2*w port device.
        @param f list of float frequencies
        @param wires integer number of wires
        @param R list of float DC resistance of wire (ohms)
        @param Rse list of float skin-effect resistance of wire (ohms/sqrt(Hz))
        @param df list of list of float dissipation factor (loss-tangent) of capacitance (unitless)
        @param C list of list of float mutual capacitance (self capacitance on diagonal) (F)
        @param G list of list of float mutual conductance (self conductance on diagonal) (S)
        @param L list of list of float mutual inductance (self inductance on diagonal) (H)
        @param Z0 (optional) float reference impedance (defaults to 50 ohms)
        @param K (optional) integer number of sections (defaults to 0)
        @param scale (optional) float amount to scale the line by (assuming all other values are per unit)
        @note If K=0 is specified, it is modified to a value that will provided a very good numerical
        approximation.  

        The calculation is such that round-trip propagation time (twice the electrical length)
        of any one small section is no more than one percent of the fastest possible risetime.
        """
        R=[r*scale for r in R]; Rse=[rse*scale for rse in Rse]; Cm=[[cm*scale for cm in cmr] for cmr in Cm];
        Gm=[[gm*scale for gm in gmr] for gmr in Gm]; Lm=[[lm*scale for lm in lmr] for lmr in Lm]
        K=int(K*scale+0.5)
        if K==0:
            maxL=0.0; maxLm=0.0
            for r in range(len(Lm)):
                for c in range(len(Lm[r])):
                    if r==c: maxL=max(maxL,Lm[r][c])
                    else: maxLm=max(maxLm,Lm[r][c])
            maxC=0.0; maxCm=0.0
            for r in range(len(Cm)):
                for c in range(len(Cm[r])):
                    if r==c: maxC=max(maxC,Cm[r][c])
                    else: maxCm=max(maxCm,Cm[r][c])
            """max possible electrical length and fastest risetime"""
            Td=math.sqrt((maxL+maxLm)*(maxC+2*maxCm)); Rt=0.45/f[-1]
            """sections such that fraction of risetime less than round trip electrical
            length of one section"""
            K=int(math.ceil(Td*2/(Rt*self.rtFraction)))
        self.m_K=K
        # build the netlist
        # pragma: silent exclude
        from SignalIntegrity.Lib.Devices import SeriesG
        from SignalIntegrity.Lib.Devices import SeriesZ
        from SignalIntegrity.Lib.Devices import TerminationG
        import SignalIntegrity.Lib.SParameters.Devices as dev
        from SignalIntegrity.Lib.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
        from SignalIntegrity.Lib.Parsers.SystemDescriptionParser import SystemDescriptionParser
        # pragma: include
        # first all of the devices
        sdp=SystemDescriptionParser().AddLines(['device R_'+str(w+1)+' 2' for w in range(wires)])
        sdp.AddLines(['device Rse_'+str(w+1)+' 2' for w in range(wires)])
        sdp.AddLines(['device L_'+str(w+1)+' 2' for w in range(wires)])
        sdp.AddLines(['device G_'+str(w+1)+' 1' for w in range(wires)])
        sdp.AddLines(['device C_'+str(w+1)+' 1' for w in range(wires)])
        for w in range(wires-1):
            for o in range(w+1,wires):
                suffix='_'+str(w+1)+'_'+str(o+1)
                sdp.AddLines(['device M'+suffix+' 4','device C'+suffix+' 2','device G'+suffix+' 2'])
        sdp.AddLines(['port '+str(w+1)+' R_'+str(w+1)+' 1' for w in range(wires)])
        sdp.AddLines(['port '+str(w+wires+1)+' C_'+str(w+1)+' 1' for w in range(wires)])

        # connect all of the devices
        sdp.AddLines(['connect R_'+str(w+1)+' 2 Rse_'+str(w+1)+' 1' for w in range(wires)])
        sdp.AddLines(['connect Rse_'+str(w+1)+' 2 L_'+str(w+1)+' 1' for w in range(wires)])
        for w in range(wires):
            DeviceFromString='L_'+str(w+1)
            DeviceFromPin=2
            CapacitorConductanceConnectionString='C_'+str(w+1)+' 1 G_'+str(w+1)+' 1'
            for o in range(wires):
                if (o==w):
                    continue
                if (o>w):
                    actualFrom=w
                    actualTo=o
                    actualInputPin=1
                    nextOutputPin=2
                    CapacitorConductanceConnectionString+=' C_'+str(w+1)+'_'+str(o+1)+' 1 G_'+str(w+1)+'_'+str(o+1)+' 1'
                else:
                    actualFrom=o
                    actualTo=w
                    actualInputPin=3
                    nextOutputPin=4
                    CapacitorConductanceConnectionString+=' C_'+str(o+1)+'_'+str(w+1)+' 2 G_'+str(o+1)+'_'+str(w+1)+' 2'

                DeviceToString='M_'+str(actualFrom+1)+'_'+str(actualTo+1)
                sdp.AddLine('connect '+DeviceFromString+' '+str(DeviceFromPin)+' '+DeviceToString+' '+str(actualInputPin))
                DeviceFromString=DeviceToString
                DeviceFromPin=nextOutputPin
            # finally, connect this last device output to the capacitances and conductances
            sdp.AddLine('connect '+DeviceFromString+' '+str(DeviceFromPin)+' '+CapacitorConductanceConnectionString)
        # make the system description and assign the s-parameters
        self.m_sspn=SystemSParametersNumeric(sdp.SystemDescription())
        self.NetListLines=sdp.m_lines
        # frequency independent get assigned directly
        for w in range(wires):
            self.m_sspn.AssignSParameters('R_'+str(w+1),SeriesZ(R[w]/K,Z0))
            self.m_sspn.AssignSParameters('G_'+str(w+1),TerminationG(Gm[w][w]/K,Z0))
            for o in range(w+1,wires):
                self.m_sspn.AssignSParameters('G_'+str(w+1)+'_'+str(o+1),SeriesG(Gm[o][w]/K,Z0)) # [o][w] not [w][o] to allow lower triangular
        # now for frequency dependent ones
        self.m_spdl=[]
        for w in range(wires):
            self.m_spdl.append(('Rse_'+str(w+1),dev.SeriesRse(f,Rse[w]/K,Z0)))
            self.m_spdl.append(('C_'+str(w+1),dev.TerminationC(f,Cm[w][w]/K,Z0,df[w][w])))
            self.m_spdl.append(('L_'+str(w+1),dev.SeriesL(f,Lm[w][w]/K,Z0)))
            for o in range(w+1,wires):
                self.m_spdl.append(('M_'+str(w+1)+'_'+str(o+1),dev.Mutual(f,Lm[o][w]/K,Z0))) # see note about [o][w] order above
                self.m_spdl.append(('C_'+str(w+1)+'_'+str(o+1),dev.SeriesC(f,Cm[o][w]/K,Z0,df[o][w])))
        SParameters.__init__(self,f,None,Z0)
    def NetList(self):
        """NetList
        @return the netlist formed for a W element.
        @remark this is really for testing only.
        """
        return self.NetListLines
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        for ds in self.m_spdl: self.m_sspn.AssignSParameters(ds[0],ds[1][n])
        sp=self.m_sspn.SParameters()
        if sp == 1: return sp
        lp=[w+1 for w in range(len(sp)//2)]; rp=[w+len(sp)//2+1 for w in range(len(sp)//2)]
        return T2S(linalg.matrix_power(S2T(sp,lp,rp),self.m_K),lp,rp)

class WElementFile(WElement):
    """W element file."""
    def __init__(self,f,filename,df=0.,Z0=50., K=0, scale=1.):
        """Constructor
        @param string filename of W element file.
        @param float (optional, defaults to 0.) dissipation factor to be added to W elements.
        @param float (optional, defaults to 50.) reference impedance.
        @param int (optional, defaults to 0.) number of sections to be used for approximation.
        @param float (optional, defaults to 1.) scale factor to scale result by.
        @remark dissipation factor does not seem to be included in W elements, which is surprising, which
        neccessitates the addition through an argument until I better understand this.
        @remark If sections are specified as 0, the number of sections used for the approximation will be determined
        automatically based on capacitances and inductances supplied, and the final end frequency for the s-parameters.
        """
        self.Z0=Z0
        self.K=K
        self.scale=scale
        with open(filename,'rU' if sys.version_info.major < 3 else 'r') as fi:
            lines=fi.readlines()
        self.numbersList=[]
        for line in lines:
            if len(line)==0: continue
            elif line[0]=='*': continue
            elif len(line.strip(' '))==0: continue
            tokens=line.split()
            if len(tokens)>0:
                self.numbersList.extend(tokens)
        self.idx=0
        self.wires=int(self._ReadToken())
        self.L0=[[float(self._ReadToken()) for _ in range(w+1)] for w in range(self.wires)]
        CM=[[float(self._ReadToken()) for _ in range(w+1)] for w in range(self.wires)]
        # CM is a Maxwell capacitance matrix.  It needs to be converted to a mutual capacitance matrix
        self.C0=MaxwellMatrix(CM).MutualMatrix()
        self.R0=[[float(self._ReadToken()) for _ in range(w+1)] for w in range(self.wires)]
        self.G0=[[float(self._ReadToken()) for _ in range(w+1)] for w in range(self.wires)]
        self.Rs=[[float(self._ReadToken()) for _ in range(w+1)] for w in range(self.wires)]
        self.Gd=[[float(self._ReadToken()) for _ in range(w+1)] for w in range(self.wires)]
        self.df=[[df for _ in range(w+1)] for w in range(self.wires)]
        WElement.__init__(self,f,self.wires,[self.R0[w][w] for w in range(self.wires)],[self.Rs[w][w] for w in range(self.wires)],
                        self.df,self.C0,self.G0,self.L0,self.Z0,self.K,self.scale)
    def _ReadToken(self):
        """Reads a single numeric token in string form from the W element file.
        @return string numeric token.
        """
        value=self.numbersList[self.idx]
        self.idx+=1
        return value
