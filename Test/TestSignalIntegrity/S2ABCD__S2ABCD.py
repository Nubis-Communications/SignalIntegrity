def S2ABCD(S,Z0=None,K=None):
    S=array(S)
    (Z0,K)=Z0KHelper((Z0,K),len(S))
    Z01=Z0.item(0,0)
    Z02=Z0.item(1,1)
    K1=K.item(0,0)
    K2=K.item(1,1)
    C11=array([[0,K2],[0,K2/Z02]])
    C12=array([[0,K2],[0,-K2/Z02]])
    C21=array([[K1,0],[-K1/Z01,0]])
    C22=array([[K1,0],[K1/Z01,0]])
    result = ((C21+C22.dot(S)).dot(inv(C11+C12.dot(S)))).tolist()
    return result