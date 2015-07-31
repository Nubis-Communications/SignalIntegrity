from numpy import matrix
from numpy import array

from SignalIntegrity.Conversions import Y2S

def Mutual(Ll,Lr,M,s,Z0=None,K=None):
    try:
        F=1.0/(s*(M*M-Ll*Lr))
    except ZeroDivisionError:
        F=1e25
    YM=matrix([[-Lr,Lr,M,-M],[Lr,-Lr,-M,M],[M,-M,-Ll,Ll],[-M,M,Ll,-Ll]])*F
    return array(Y2S(array(YM).tolist(),Z0,K)).tolist()
