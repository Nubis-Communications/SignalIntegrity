'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
# note that port 1 is - input, port 2 is + input and port 3 is output
def OperationalAmplifier(Zi,Zd,Zo,G,Z0=50.):
    S11=((-2.*Zi-Zd)*Z0*Z0+Zi*Zi*Zd)/((2.*Zi+Zd)*Z0*Z0+(2.*Zi*Zd+2.*Zi*Zi)*Z0+Zi*Zi*Zd)
    S12=(2.*Zi*Zi*Z0)/((2.*Zi+Zd)*Z0*Z0+(2.*Zi*Zd+2.*Zi*Zi)*Z0+Zi*Zi*Zd)
    S32=2.*G*Zi*Zd*Z0/((Zo+Z0)*((2.*Zi+Zd)*Z0+Zi*Zd))
    S33=(Zo-Z0)/(Zo+Z0)
    return [[S11,S12,0.],[S12,S11,0.],[-S32,S32,S33]]