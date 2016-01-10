'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import array

from SignalIntegrity.Conversions import Z0KHelper

# pragma: silent exclude
def ShuntZZ0K(Z,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),2)
    Z01=Z0.item(0,0)
    Z02=Z0.item(1,1)
    K1=K.item(0,0)
    K2=K.item(1,1)
    partial=array([[Z*(Z02-Z01)-Z01*Z02,2*K2/K1*Z01*Z],[2*K1/K2*Z02*Z,Z*(Z01-Z02)-Z01*Z02]])
    return (partial*1./(Z01*Z02+Z*(Z01+Z02))).tolist()

def ShuntZ(ports,Z,Z0=50.):
    if ports == 2: return ShuntZTwoPort(Z,Z0)
    elif ports == 3: return ShuntZThreePort(Z,Z0)
    elif ports == 4: return ShuntZFourPort(Z,Z0)
# pragma: include
def ShuntZTwoPort(Z,Z0=50.):
    return [[-Z0*Z0/(Z0*Z0+2.*Z*Z0),2.*Z0*Z/(Z0*Z0+2.*Z*Z0)],
        [2.*Z0*Z/(Z0*Z0+2.*Z*Z0),-Z0*Z0/(Z0*Z0+2.*Z*Z0)]]
# pragma: silent exclude
def ShuntZFourPort(Z,Z0=50.):
    D=2.*(Z+Z0)
    return [[-Z0/D,Z0/D,(2.*Z+Z0)/D,Z0/D],
        [Z0/D,-Z0/D,Z0/D,(2.*Z+Z0)/D],
        [(2.*Z+Z0)/D,Z0/D,-Z0/D,Z0/D],
        [Z0/D,(2.*Z+Z0)/D,Z0/D,-Z0/D]]

def ShuntZThreePort(Z,Z0=50.):
    D=2.*Z+3.*Z0
    return [[-Z0/D,(2.*Z+2.*Z0)/D,2.*Z0/D],
            [(2.*Z+2.*Z0)/D,-Z0/D,2.*Z0/D],
            [2.*Z0/D,2.*Z0/D,(2.*Z-Z0)/D]]

