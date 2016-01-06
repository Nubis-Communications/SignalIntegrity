'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import matrix
from numpy import identity

from Deembedder import Deembedder
from SignalIntegrity.PySIException import PySIExceptionNumeric

class DeembedderNumeric(Deembedder):
    def __init__(self,sd=None):
        Deembedder.__init__(self,sd)
    def CalculateUnknown(self,Sk):
        Bmsd=self.PortANames()
        Amsd=self.PortBNames()
        Adut=self.DutANames()
        Bdut=self.DutBNames()
        # pragma: silent exclude
        K=len(self.PortANames())
        U=len(self.DutANames())
        if U > K: # underconstrained
            raise PySIExceptionNumeric('under-constrained system')
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
                G33I=(matrix(identity(len(Internals)))-
                      matrix(self.WeightsMatrix(Internals,Internals))).getI()
            # pragma: silent exclude indent
            except:
                raise PySIExceptionNumeric('cannot invert G33')
            # pragma: include
            G34=-matrix(self.WeightsMatrix(Internals,Amsd))
            G35=-matrix(self.WeightsMatrix(Internals,Bdut))
            F11=G13*G33I*G34-G14
            F12=G13*G33I*G35-G15
            F21=G23*G33I*G34-G24
            F22=G23*G33I*G35-G25
        else:# no internal nodes
            F11=-G14
            F12=-G15
            F21=-G24
            F22=-G25
        # pragma: silent exclude
        try:
        # pragma: include outdent
            #if long and skinny F12 then
            #F12.getI()=(F12.transpose()*F12).getI()*F12.transpose()
            #if short and fat F12, F12.getI() is wrong
            B=F12.getI()*(Sk-F11)
        # pragma: silent exclude indent
        except:
            raise PySIExceptionNumeric('cannot invert F12')
        # pragma: include
        A=F21+F22*B
        AL=self.Partition(A)# partition for multiple unknown devices
        BL=self.Partition(B)
        # pragma: silent exclude
        try:
        # pragma: include outdent
            Su=[(BL[u]*AL[u].getI()).tolist() for u in range(len(AL))]
        # pragma: silent exclude indent
        except:
            raise PySIExceptionNumeric('cannot invert A')
        # pragma: include
        if (len(Su)==1):# only one result
            return Su[0]# return the one result, not as a list
        return Su# return the list of results