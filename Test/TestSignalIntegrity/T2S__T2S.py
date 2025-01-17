def T2S(T,lp=None,rp=None):
    P=len(T)//2+len(T[0])//2
    if not isinstance(lp,list):
        lp=range(1,P//2+1)
        rp=range(P//2+1,P+1)
    I=identity(P).tolist()
    SL=[]
    SR=[]
    for p in range(P):
        if (p+1) in rp:
            SL.append(I[2*rp.index(p+1)+1])
            SR.append(I[2*rp.index(p+1)])
        else:
            SL.append(T[2*lp.index(p+1)])
            SR.append(T[2*lp.index(p+1)+1])
    result = (array(SL).dot(inv(array(SR)))).tolist()
    return result