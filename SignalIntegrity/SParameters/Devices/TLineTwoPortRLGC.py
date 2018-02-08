'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
import math,cmath

from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.Devices.TLineTwoPort import TLineTwoPort

class TLineTwoPortRLGC(SParameters):
    def __init__(self,f,R,Rse,L,G,C,df,Z0,K=0):
        # pragma: silent exclude
        from SignalIntegrity.SParameters.Devices.TLineTwoPortRLGCAnalytic import TLineTwoPortRLGCAnalytic
        from SignalIntegrity.SParameters.Devices.TLineTwoPortRLGCApproximate import TLineTwoPortRLGCApproximate
        # pragma: include
        if K==0: self.sp=TLineTwoPortRLGCAnalytic(f,R,Rse,L,G,C,df,Z0)
        else: self.sp=TLineTwoPortRLGCApproximate(f,R,Rse,L,G,C,df,Z0,K)
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        return self.sp[n]
