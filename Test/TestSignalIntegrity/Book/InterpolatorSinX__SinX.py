def SinX(S,U,F):
    k=np.arange(2*U*S+1)
    arg=k/float(U)-F-S
    with np.errstate(divide='ignore',invalid='ignore'):
        main=np.sin(np.pi*arg)/(np.pi*arg)*\
            (1./2.+1./2.*np.cos(np.pi*(k/float(U)-S)/S))
    sl=np.where(arg==0,1.,main)
    s=np.sum(sl)/U
    return (sl/s).tolist()

