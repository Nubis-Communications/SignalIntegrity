"""single-ended telegraphers transmission line"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

import math,cmath

from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.Devices.TLineTwoPort import TLineTwoPort

class TLineTwoPortRLGC(SParameters):
    """s-parameters of single-ended RLGC (telegraphers) transmission line"""
    def __init__(self,f,R,Rse,L,G,C,df,Z0,K=0):
        """Constructor
        @param f list of float frequencies
        @param R float DC series resistance (Ohms)
        @param Rse float series skin-effect resistance (Ohms/sqrt(Hz))
        @param L float series inductance (H)
        @param G float DC conductance to ground (S)
        @param C float capacitance to ground (F)
        @param df float dissipation factor (loss-tangent) of capacitance to ground
        @param Z0 float reference impedance
        @param K (optional) integer number of sections (defaults to zero)
        @note K=0 specifies the analytic transmission line calculation TLineTwoPortRLGCAnalytic.\n
        Otherwise, non-zero K specifies the numerical approximation TLineTwoPortRLGCApproximate.\n
        """
        # pragma: silent exclude
        from SignalIntegrity.SParameters.Devices.TLineTwoPortRLGCAnalytic import TLineTwoPortRLGCAnalytic
        from SignalIntegrity.SParameters.Devices.TLineTwoPortRLGCApproximate import TLineTwoPortRLGCApproximate
        # pragma: include
        if K==0: self.sp=TLineTwoPortRLGCAnalytic(f,R,Rse,L,G,C,df,Z0)
        else: self.sp=TLineTwoPortRLGCApproximate(f,R,Rse,L,G,C,df,Z0,K)
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        return self.sp[n]
