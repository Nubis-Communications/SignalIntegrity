class LevMar(CallBacker):
    def __init__(self,callback=None):
        self.m_lambda=1000
        self.m_lambdamin=1e-15
        self.m_lambdamax=1e9
        self.m_lambdaMultiplier = 2.
        self.m_epsilon = 1e-19
        self.ccm=FitConvergenceMgr()
        CallBacker.__init__(self,callback)
    def fF(self,a):
        raise SignalIntegrityExceptionFitter('fF must be overloaded')
    def fPartialFPartiala(self,a,m,Fa=None):
        aplusDeltaa = copy.copy(a)
        aplusDeltaa[m][0]=aplusDeltaa[m][0]+self.m_epsilon
        if Fa is None:
            Fa = self.fF(a)
        dFa = (self.fF(aplusDeltaa)-Fa)/self.m_epsilon
        return dFa
    def fJ(self,a,Fa=None):
        if Fa is None:
            Fa=self.fF(a)
        M = len(a)
        R = len(Fa)
        J = zeros((R,M))
        for m in range(M):
            pFpam=self.fPartialFPartiala(a,m,Fa)
            for r in range(R):
                J[r][m]=pFpam[r][0]
        return J
    def AdjustVariablesAfterIteration(self,a):
        return a
    def Initialize(self,a,y,w=None):
        self.m_a = copy.copy(array(a))
        self.m_y = copy.copy(array(y))
        if w is None:
            self.m_sumw=len(y)
            self.m_W=1.0
        else:
            self.m_W = diag(w)
            self.m_sumw = 0
            for r in range(w.rows()):
                self.m_sumw = self.m_sumw + w[r][0]
        self.m_Fa = self.fF(self.m_a)
        self.m_r=self.m_Fa-self.m_y
        self.m_mse=math.sqrt(self.m_r.conj().T.dot(self.m_W).dot(
            self.m_r)[0][0].real/self.m_sumw)
        self.m_lambdaTracking = [self.m_lambda]
        self.m_mseTracking = [self.m_mse]
        self.m_J = None
        self.m_H = None
        self.m_JHWr = None
        self.ccm=FitConvergenceMgr()
...
