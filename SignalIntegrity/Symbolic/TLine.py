'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
def TLine(P,rho,gamma):
    if P==2:
        return TLineTwoPort(rho,gamma)
    elif P==4:
        return TLineFourPort(rho,gamma)

def TLineRho(Zc,ports=2):
    if ports == 2:
        return ' \\frac{ '+Zc+'-Z0 }{ '+Zc+' + Z0 }'
    elif ports == 4:
        return ' \\frac{ \\frac{ '+Zc+' }{2} - Z0  }{ \\frac{ '+Zc+' }{2} + Z0 }'

def TLineGamma(Td):
    return ' j \\cdot 2 \\pi \\cdot f \\cdot '+Td

def TLineTwoPort(rho,gamma):
    L='e^{-'+gamma+'}'
    L2='e^{-2 \\cdot '+gamma+' } '
    D='1 - \\left[ '+rho+' \\right]^2 \\cdot '+L2
    S1=' \\frac{ '+rho+' \\cdot \\left( 1 - '+L2+' \\right) }{ '+D+' }'
    S2=' \\frac{ '+L+' \\cdot \\left( 1 - \\left[ '+rho+' \\right] ^2 \\right) }{ '+D+' } '
    return [[S1,S2],[S2,S1]]

def TLineFourPort(rho,gamma):
    Y='e^{-'+gamma+' } '
    Y2='e^{-2 \\cdot '+gamma+' } '
    D='2 \\cdot \\left( 1 - '+Y2+' \\cdot \\left[ '+rho+' \\right]^2 \\right)'
    S1= '\\frac{ 1 - '+Y2+' \\cdot \\left[ '+rho+' \\right]^2 + '+rho+' \\cdot \\left( 1 - '+Y2+' \\right) }{ '+D+' } '
    S2= '\\frac{ \\left( 1 - \\left[ '+rho+' \\right]^2 \\right) \\cdot '+Y+' }{ '+D+' } '
    S3= '\\frac{ 1 - '+Y2+' \\cdot \\left[ '+rho+' \\right]^2 - '+rho+' \\cdot \\left( 1 - '+Y2+' \\right)  }{ '+D+' } '
    return [[S1,S2,S3,'-'+S2],
            [S2,S1,'-'+S2,S3],
            [S3,'-'+S2,S1,S2],
            ['-'+S2,S3,S2,S1]]

