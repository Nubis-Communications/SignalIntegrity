from numpy import array

from SignalIntegrity.Conversions import Z0KHelper

def SeriesZZ0K(Z,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),2)
    Z01=Z0.item(0,0)
    Z02=Z0.item(1,1)
    K1=K.item(0,0)
    K2=K.item(1,1)
    return (array([[Z+Z02-Z01,2.*K2/K1*Z01],[2*K1/K2*Z02,Z+Z01-Z02]])*1./(Z+Z01+Z02)).tolist()

def SeriesZ(Z,Z0=50.):
    return [[Z/(Z+2.*Z0),2.*Z0/(Z+2.*Z0)],[2*Z0/(Z+2.*Z0),Z/(Z+2.*Z0)]]
