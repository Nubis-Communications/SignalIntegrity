class TLineTwoPortRLGC(SParameters):
    def __init__(self,f,R,Rse,L,G,C,df,Z0=50.,K=0,scale=1.):
        if K==0: self.sp=TLineTwoPortRLGCAnalytic(f,R,Rse,L,G,C,df,Z0,scale)
        else: self.sp=TLineTwoPortRLGCApproximate(f,R,Rse,L,G,C,df,Z0,K,scale)
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        return self.sp[n]
