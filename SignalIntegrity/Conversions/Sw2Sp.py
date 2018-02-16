"""
Converts pseudo-wave s-parameters to power-wave s-parameters
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.
from numpy import matrix

from Z0KHelper import Z0KHelper
from Z0KHelperPW import Z0KHelperPW

## Converts pseudo-wave s-parameters to power-wave s-parameters
#
# @param Sp power-wave based s-parameter matrix to convert
# @param Z0w (optional) the reference impedance of the pseudo-wave based s-parameters (assumed 50 Ohms)
# @param Z0p (optional) the reference impedance of the power-wave based s-parameters (assumed 50 Ohms)
# @param Kw (optional) the scaling factor of the pseudo-wave based s-parameters (assumed to be sqrt(Z0w)
# @param Kp (optional) the scaling factor of the power-wave based s-parameters (assumed to be sqrt(Z0p)
#
# @return the converted s-parameters in power-waves
#
# @see Z0KHelper to see how the reference impedance
# and scaling factor are determined.
def Sw2Sp(Sp,Z0w=None,Z0p=None,Kw=None,Kp=None):
    if Z0p is None:
        Z0p=Z0w
    (Z0w,Kw)=Z0KHelper((Z0w,Kw),len(Sp))
    (Z0p,Kp)=Z0KHelperPW((Z0p,Kp),len(Sp))
    Sp=matrix(Sp)
    Sw=(Kp.getI()*Kw*Z0w.getI()*((Z0w-Z0p.conjugate())+(Z0w+Z0p.conjugate())*Sp)*
        ((Z0w+Z0p)+(Z0w-Z0p)*Sp).getI()*Kp*Kw.getI()*Z0w)
    return Sw