# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

import cmath

def ReferenceImpedanceTransformer(Z0f,Z0i=None,Kf=None,Ki=None):
    """AtPackage si.dev.ReferenceImpedanceTransformer
    Reference impedance transformer
    @param Z0f real or complex output reference impedance.
    @param Z0i real or complex input reference impedance.
    @param Kf (optional) real or complex scaling factor for the output (defaults to sqrt(Z0f))
    @param Ki (optional) real or complex scaling factor for the input (defaults to sqrt(Z0i))
    @return the list of list s-parameter matrix for a reference impedance transformer.
    @todo put Z0i=50.0 in the input arguments and remove check within the code
    @todo needs port numbering
    """
    Z0f=float(Z0f.real)+float(Z0f.imag)*1j
    if Z0i is None:
        Z0i=50.0
    Z0i=float(Z0i.real)+float(Z0i.imag)*1j
    if Kf is None:
        Kf=cmath.sqrt(Z0f)
    if Ki is None:
        Ki=cmath.sqrt(Z0i)
    Kf=float(Kf.real)+float(Kf.imag)*1j
    Ki=float(Ki.real)+float(Ki.imag)*1j
    p=(Z0f-Z0i)/(Z0f+Z0i)
    return [[p,(1.0-p)*Kf/Ki],[(1.0+p)*Ki/Kf,-p]]
