"""
Performs Device Deembedding Numerically
@see [US patent 8,566,058 B2](https://patents.google.com/patent/US8566058B2)
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

from numpy import matrix
from numpy import identity

from SignalIntegrity.Lib.SystemDescriptions.Deembedder import Deembedder
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionNumeric
from SignalIntegrity.Lib.SystemDescriptions.Numeric import Numeric

class DeembedderNumeric(Deembedder,Numeric):
    """
    Performs numerical device deembedding
    @see [US patent 8,566,058 B2](https://patents.google.com/patent/US8566058B2)
    """
    def __init__(self,sd=None):
        """Constructor
        @param sd (optional) instance of class SystemDescription
        """
        Deembedder.__init__(self,sd)
    def CalculateUnknown(self,Sk):
        """Calculates the unknown s-parameters

        @param Sk instance of class SParameters containing the s-parameters of
        the known device

        calculates unknown devices in the system, effectively deembedding the
        surrounding network
        """
        Bmsd=self.PortANames()
        Amsd=self.PortBNames()
        Adut=self.DutANames()
        Bdut=self.DutBNames()
        # pragma: silent exclude
        K=len(self.PortANames())
        U=len(self.DutANames())
        if U > K: # underconstrained
            raise SignalIntegrityExceptionNumeric('under-constrained system')
        # pragma: include
        Internals=self.OtherNames(Bmsd+Amsd+Adut+Bdut)
        G14=-matrix(self.WeightsMatrix(Bmsd,Amsd))
        G15=-matrix(self.WeightsMatrix(Bmsd,Bdut))
        G24=-matrix(self.WeightsMatrix(Adut,Amsd))
        G25=-matrix(self.WeightsMatrix(Adut,Bdut))
        if len(Internals)>0:# internal nodes
            G13=-matrix(self.WeightsMatrix(Bmsd,Internals))
            G23=-matrix(self.WeightsMatrix(Adut,Internals))
            # pragma: silent exclude
            try:
            # pragma: include outdent
                G33=matrix(identity(len(Internals)))-\
                    matrix(self.WeightsMatrix(Internals,Internals))
                G34=-matrix(self.WeightsMatrix(Internals,Amsd))
                G35=-matrix(self.WeightsMatrix(Internals,Bdut))
                F11=self.Dagger(G33,Left=G13,Right=G34,Mul=True)-G14
                F12=self.Dagger(G33,Left=G13,Right=G35,Mul=True)-G15
                F21=self.Dagger(G33,Left=G23,Right=G34,Mul=True)-G24
                F22=self.Dagger(G33,Left=G23,Right=G35,Mul=True)-G25
            # pragma: silent exclude indent
            except:
                raise SignalIntegrityExceptionNumeric('cannot invert G33')
            # pragma: include
        else:# no internal nodes
            F11=-G14; F12=-G15; F21=-G24; F22=-G25
        # pragma: silent exclude
        try:
        # pragma: include outdent
            #if long and skinny F12 then
            #F12.getI()=(F12.transpose()*F12).getI()*F12.transpose()
            #if short and fat F12, F12.getI() is wrong
            B=self.Dagger(F12,Right=(Sk-F11),Mul=True)
        # pragma: silent exclude indent
        except:
            raise SignalIntegrityExceptionNumeric('cannot invert F12')
        # pragma: include
        A=F21+F22*B
        AL=self.Partition(A)# partition for multiple unknown devices
        BL=self.Partition(B)
        # pragma: silent exclude
        try:
        # pragma: include outdent
            Su=[self.Dagger(AL[u],Left=BL[u],Mul=True).tolist() for u in range(len(AL))]
        # pragma: silent exclude indent
        except:
            raise SignalIntegrityExceptionNumeric('cannot invert A')
        # pragma: include
        if (len(Su)==1): return Su[0]# return the one result, not as a list
        return Su# return the list of results
