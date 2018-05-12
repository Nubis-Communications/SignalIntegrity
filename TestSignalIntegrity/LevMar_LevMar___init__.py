class LevMar(CallBacker):
    def __init__(self,callback=None):
        self.m_lambda=1000
        self.m_lambdamin=1e-15
        self.m_lambdamax=1e9
        self.m_lambdaMultiplier = 2.
        self.m_epsilon = 1e-19
        self.ccm=FitConvergenceMgr()
        CallBacker.__init__(self,callback)
    def fF(self,x):
        raise
    def fPartialFPartialx(self,x,m,Fx=None):
        xplusDeltax = x.copy()
        xplusDeltax[m][0]=x[m][0]+self.m_epsilon
        if Fx is None:
            Fx = self.fF(x)
        dFx = (self.fF(xplusDeltax)-Fx)/self.m_epsilon
        return dFx
    def fJ(self,x,Fx=None):
        if Fx is None:
            Fx=self.fF(x)
        M = x.rows()
        R = Fx.rows()
        J = zeros((R,M)).tolist()
        for m in range(M):
            pFpxm=self.fPartialFPartialx(x,m,Fx)
            for r in range(R):
                J[r][m]=pFpxm[r][0]
        return J
    @staticmethod
    def AdjustVariablesAfterIteration(x):
        return x
    def Initialize(self,x,y,w=None):
        self.m_x = copy.copy(x)
        self.m_y = copy.copy(y)
        if w is None:
            self.m_sumw=len(y)
            self.m_W=1.0
        else:
            self.m_W = Matrix.diag(w)
            self.m_sumw = 0
            for r in range(w.rows()):
                self.m_sumw = self.m_sumw + w[r][0]
        self.m_Fx = self.fF(self.m_x)
        self.m_r=(matrix(self.m_Fx)-matrix(self.m_y)).tolist()
        self.m_mse=math.sqrt((matrix(self.m_r).getH()*
            self.m_W*matrix(self.m_r)).tolist()[0][0].real/self.m_sumw)
        self.m_lambdaTracking = [self.m_lambda]
        self.m_mseTracking = [self.m_mse]
        self.m_J = None
        self.m_H = None
        self.m_D = None
        self.m_JHWr = None
        self.ccm=FitConvergenceMgr()
...
