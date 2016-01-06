'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
def VoltageAmplifier(P,G,Zi,Zo,Z0=50):
    if P==2:
        return VoltageAmplifierTwoPort(G,Zi,Zo,Z0=50.)
    elif P==3:
        return VoltageAmplifierThreePort(G,Zi,Zo,Z0=50.)
    elif P==4:
        return VoltageAmplifierFourPort(G,Zi,Zo,Z0=50.)

def VoltageAmplifierFourPort(G,Zi,Zo,Z0=50.):
    S11=Zi/(Zi+2.*Z0)
    S12=2.*Z0/(Zi+2.*Z0)
    S13=0
    S14=0
    S21=S12
    S22=S11
    S23=0
    S24=0
    S31=2.*Zi*Z0*G/((Zi+2.*Z0)*(Zo+2.*Z0))
    S32=-S31
    S33=Zo/(Zo+2.*Z0)
    S34=2.*Z0/(Zo+2.*Z0)
    S41=S32
    S42=S31
    S43=S34
    S44=S33
    return [[S11,S12,S13,S14],
            [S21,S22,S23,S24],
            [S31,S32,S33,S34],
            [S41,S42,S43,S44]]

def VoltageAmplifierThreePort(G,Zi,Zo,Z0=50.):
    D=-Zo*Zi-2.*Zo*Z0-2.*Zi*Z0-3.*Z0*Z0+G*Zi*Z0
    S11=(-Zo*Zi-2.*Zi*Z0+Z0*Z0+G*Zi*Z0)/D
    S12=-2.*Z0*Z0/D
    S13=-2.*Z0*(Zo+Z0)/D
    S21=-2.*Z0*(G*Zi+Z0)/D
    S22=(Z0*Z0-2.*Zo*Z0+G*Zi*Z0-Zo*Zi)/D
    S23=2.*Z0*(G*Zi-Zi-Z0)/D
    S31=2.*Z0*(-Z0+G*Zi-Zo)/D
    S32=-2.*Z0*(Zi+Z0)/D
    S33=(-Zo*Zi+Z0*Z0-G*Zi*Z0)/D
    return [[S11,S12,S13],
            [S21,S22,S23],
            [S31,S32,S33]]

def VoltageAmplifierTwoPort(G,Zi,Zo,Z0=50.):
    return [[(Zi-Z0)/(Zi+Z0),0.],[2.*G*Zi*Z0/((Zi+Z0)*(Zo+Z0)),(Zo-Z0)/(Zo+Z0)]]

