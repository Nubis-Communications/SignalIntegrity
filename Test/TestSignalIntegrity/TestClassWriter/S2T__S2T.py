def S2T(S,lp=None,rp=None):
    P=len(S)
    if not isinstance(lp,list):
        lp=range(1,P//2+1)
        rp=range(P//2+1,P+1)
    I=identity(P).tolist()
    TL=[]
    for r in range(len(lp)):
        TL.append(S[lp[r]-1])
        TL.append(I[lp[r]-1])
    TR=[]
    for r in range(len(rp)):
        TR.append(I[rp[r]-1])
        TR.append(S[rp[r]-1])
    result = (array(TL).dot(inv(array(TR)))).tolist()
    return result
