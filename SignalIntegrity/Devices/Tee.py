from numpy import empty

def Tee(P=None):
    if P is None:
        P=3
    mat=empty((P,P))
    mat.fill(2.0/P)
    for r in range(P):
        mat.itemset((r,r),(2.0-P)/P)
    return mat.tolist()  
