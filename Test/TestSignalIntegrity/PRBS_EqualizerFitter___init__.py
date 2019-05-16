class EqualizerFitter(si.fit.LevMar):
    def __init__(self,callback=None):
        si.fit.LevMar.__init__(self,callback)
    def Initialize(self,decodedWf,levels,pre,post):
        self.levels=levels; self.pre=pre; self.post=post
        a=[[0.] for _ in range(pre+post+1)]
        self.x=[[v] for v in decodedWf.Values()]
        y=[[m] for m in self.Decode(self.x)[pre:len(self.x)-post]]
        si.fit.LevMar.Initialize(self,a,y)
        self.m_epsilon=0.0000001
    def Decode(self,x):
        return [self.levels[min(list(zip([abs(v[0]-d)
            for d in self.levels],range(len(self.levels)))))[1]] for v in x]
    def fF(self,a):
        return [[sum([a[i][0]*self.x[k-i+self.pre][0]
            for i in range(self.pre+self.post+1)])]
                for k in range(self.pre,len(self.x)-self.post)]
    def AdjustVariablesAfterIteration(self,a):
        self.y=[[v] for v in self.Decode(self.x)[self.pre:len(self.x)-self.post]]
        return si.fit.LevMar.AdjustVariablesAfterIteration(self,a)
    def Results(self):
        return self.m_a


