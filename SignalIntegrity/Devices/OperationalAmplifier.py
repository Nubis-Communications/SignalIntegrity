# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

def OperationalAmplifier(Zi,Zd,Zo,G,Z0=50.):
    """OperationalAmplifier
    Operational Amplifier
    @param Zi real or complex input impedance between each plus and minus input port
    to ground.
    @param Zd real or complex input impedance across the plus and minus inputs.
    @param Zo real or complex output impedance.
    @param G real or complex gain of the op-amp.
    @param Z0 (optional) real or complex reference impedance (default is 50 Ohms).
    @return the list of list s-parameter matrix of the s-parameters of a three port op-amp.
    Port 1 is - input, port 2 is + input and port 3 is output
    @attention This device is completely wrong and should not be used.  The documentation
    is correct, but the s-parameters are such that Zi is the series impedance between port
    1 and the op-amp input, which is incorrect.  The input impedance should be port 1 to 
    ground, as indicated (this is the same for port 2).
    @todo Fix the operational amplifier, which is completely wrong and should not be used.
    """
    S11=((-2.*Zi-Zd)*Z0*Z0+Zi*Zi*Zd)/((2.*Zi+Zd)*Z0*Z0+(2.*Zi*Zd+2.*Zi*Zi)*Z0+Zi*Zi*Zd)
    S12=(2.*Zi*Zi*Z0)/((2.*Zi+Zd)*Z0*Z0+(2.*Zi*Zd+2.*Zi*Zi)*Z0+Zi*Zi*Zd)
    S32=2.*G*Zi*Zd*Z0/((Zo+Z0)*((2.*Zi+Zd)*Z0+Zi*Zd))
    S33=(Zo-Z0)/(Zo+Z0)
    return [[S11,S12,0.],[S12,S11,0.],[-S32,S32,S33]]