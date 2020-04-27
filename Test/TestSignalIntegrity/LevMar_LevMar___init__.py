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
        aplusDeltaa[m][0]=a[m][0]+self.m_epsilon
        if Fa is None:
            Fa = self.fF(a)
        dFa = ((array(self.fF(aplusDeltaa))-array(Fa))/self.m_epsilon).tolist()
        return dFa
    def fJ(self,a,Fa=None):
        if Fa is None:
            Fa=self.fF(a)
        M = len(a)
        R = len(Fa)
        J = zeros((R,M)).tolist()
        for m in range(M):
            pFpam=self.fPartialFPartiala(a,m,Fa)
            for r in range(R):
                J[r][m]=pFpam[r][0]
        return J
    def AdjustVariablesAfterIteration(self,a):
        return a
    def Initialize(self,a,y,w=None):
        self.m_a = copy.copy(a)
        self.m_y = copy.copy(y)
        if w is None:
            self.m_sumw=len(y)
            self.m_W=1.0
        else:
            self.m_W = Matrix.diag(w)
            self.m_sumw = 0
            for r in range(w.rows()):
                self.m_sumw = self.m_sumw + w[r][0]
        self.m_Fa = self.fF(self.m_a)
        self.m_r=(array(self.m_Fa)-array(self.m_y)).tolist()
        self.m_mse=math.sqrt((array(self.m_r).conj().T.dot(
            self.m_W).dot(array(self.m_r))).tolist()[0][0].real/self.m_sumw)
        self.m_lambdaTracking = [self.m_lambda]
        self.m_mseTracking = [self.m_mse]
        self.m_J = None
        self.m_H = None
        self.m_D = None
        self.m_JHWr = None
        self.ccm=FitConvergenceMgr()
...
