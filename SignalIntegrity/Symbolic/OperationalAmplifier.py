'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
# note that port 1 is - input, port 2 is + input and port 3 is output
def OperationalAmplifier(Zi,Zd,Zo,G):
    S11='\\frac{\\left(-2\\cdot '+Zi+' - '+Zd+' \\right)\\cdot Z0^2+ '+Zi+' ^2\\cdot '+Zd+' }{\\left(2\\cdot '+Zi+' + '+Zd+' \\right)\\cdot Z0^2+\\left(2\\cdot '+Zi+' \\cdot '+Zd+' +2\\cdot '+Zi+' ^2\\right)\\cdot Z0+ '+Zi+' ^2\\cdot '+Zd+' }'
    S12='\\frac{2\\cdot '+Zi+' ^2\\cdot Z0}{\\left(2\\cdot '+Zi+' + '+Zd+' \\right)\\cdot Z0^2+\\left(2\\cdot '+Zi+' \\cdot '+Zd+' +2\\cdot '+Zi+' ^2\\right)\\cdot Z0+ '+Zi+' ^2\\cdot '+Zd+' }'
    S32='\\frac{2\\cdot '+G+' \\cdot '+Zi+' \\cdot '+Zd+' \\cdot Z0}{\\left( '+Zo+' +Z0\\right)\\cdot \\left(\\left(2\\cdot '+Zi+' + '+Zd+' \\right)\\cdot Z0+ '+Zi+' \\cdot '+Zd+' \\right)}'
    S33='\\frac{ '+Zo+' -Z0}{ '+Zo+' +Z0}'
    return [[S11,S12,'0'],[S12,S11,'0'],['-'+S32,S32,S33]]