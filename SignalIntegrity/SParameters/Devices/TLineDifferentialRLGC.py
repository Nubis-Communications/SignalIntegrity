'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.SParameters.SParameters import SParameters

"""
    ports are 1,2,3,4 is +1,-1, +2, -2
"""
class TLineDifferentialRLGC(SParameters):
    def __init__(self,f, Rp, Rsep, Lp, Gp, Cp, dfp,
                         Rn, Rsen, Ln, Gn, Cn, dfn,
                         Cm, dfm, Gm, Lm, Z0, K=0):
        balanced = Rp==Rn and Rsep==Rsen and Lp==Ln and Gp==Gn and Cp==Cn
        uncoupled = Cm==0 and (Cm != 0 and dfm==0) and Gm==0 and Lm==0
        if K != 0 or (not balanced and not uncoupled):
            # pragma: silent exclude
            from SignalIntegrity.SParameters.Devices.TLineDifferentialRLGCApproximate import TLineDifferentialRLGCApproximate
            # pragma: include
            self.sp=TLineDifferentialRLGCApproximate(f,
                        Rp, Rsep, Lp, Gp, Cp, dfp,
                        Rn, Rsen, Ln, Gn, Cn, dfn,
                        Cm, dfm, Gm, Lm, Z0, K)
        elif uncoupled:
            # pragma: silent exclude
            from SignalIntegrity.SParameters.Devices.TLineDifferentialRLGCUncoupled import TLineDifferentialRLGCUncoupled
            # pragma: include
            self.sp=TLineDifferentialRLGCUncoupled(f,
                        Rp, Rsep, Lp, Gp, Cp, dfp,
                        Rn, Rsen, Ln, Gn, Cn, dfn,
                        Z0, K)
        elif balanced:
            # pragma: silent exclude
            from SignalIntegrity.SParameters.Devices.TLineDifferentialRLGCBalanced import TLineDifferentialRLGCBalanced
            # pragma: include
            self.sp=TLineDifferentialRLGCBalanced(f,
                        Rp, Rsep, Lp, Gp, Cp, dfp,
                        Cm, dfm, Gm, Lm, Z0, K)
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        return self.sp[n]