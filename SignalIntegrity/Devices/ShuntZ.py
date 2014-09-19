from numpy import array

from SignalIntegrity.Conversions import Z0KHelper   

def ShuntZ(Z,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),2)
    Z01=Z0.item(0,0)
    Z02=Z0.item(1,1)
    K1=K.item(0,0)
    K2=K.item(1,1)
    partial=array([[Z*(Z02-Z01)-Z01*Z02,2*K2/K1*Z01*Z],[2*K1/K2*Z02*Z,Z*(Z01-Z02)-Z01*Z02]])
    return (partial*1./(Z01*Z02+Z*(Z01+Z02))).tolist()    
