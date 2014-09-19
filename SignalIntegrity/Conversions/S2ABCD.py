from numpy import matrix
from numpy import array

from Z0KHelper import Z0KHelper

def S2ABCD(S,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),len(S))
    Z01=Z0.item(0,0)
    Z02=Z0.item(1,1)
    K1=K.item(0,0)
    K2=K.item(1,1)
    C11=matrix([[0,K2],[0,K2/Z02]])
    C12=matrix([[0,K2],[0,-K2/Z02]])
    C21=matrix([[K1,0],[-K1/Z01,0]])
    C22=matrix([[K1,0],[K1/Z01,0]])
    return array((C21+C22*S)*((C11+C12*S).getI())).tolist()
