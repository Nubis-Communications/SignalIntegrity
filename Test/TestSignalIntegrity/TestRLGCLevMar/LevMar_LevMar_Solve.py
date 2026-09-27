class LevMar(CallBacker):
...
    def Iterate(self):
        if self.m_Fa is None:
            self.m_Fa=self.fF(self.m_a)
        if self.m_r is None:
            self.m_r=self.m_Fa-self.m_y
        if self.m_J is None:
            self.m_J=self.fJ(self.m_a,self.m_Fa)
        if self.m_H is None:
            self.m_H=self.m_J.conj().T.dot(self.m_W).dot(self.m_J)
        if self.m_JHWr is None:
            self.m_JHWr=self.m_J.conj().T.dot(self.m_W).dot(self.m_r)
        HplD=copy.copy(self.m_H)
        for r in range(HplD.shape[0]): HplD[r][r]*=(1.+self.m_lambda)
        Deltaa=solve(HplD,self.m_JHWr)
        newa=self.m_a-Deltaa
        newa=self.AdjustVariablesAfterIteration(newa)
        newFa = self.fF(newa)
        newr=newFa-self.m_y
        newmse=math.sqrt(newr.conj().T.dot(self.m_W).dot(newr)[0][0].real/self.m_sumw)
        if newmse < self.m_mse:
            self.m_mse = newmse
            self.m_a = newa
            self.m_lambda = max(self.m_lambda/
                self.m_lambdaMultiplier,self.m_lambdamin)
            self.m_Fa = newFa
            self.m_r = newr
            self.m_J = None
            self.m_H = None
            self.m_JHWr = None
        else:
            self.m_lambda = min(self.m_lambda*
                self.m_lambdaMultiplier,self.m_lambdamax)
        self.ccm.IterationResults(self.m_mse, self.m_lambda)
        self.m_lambdaTracking.append(self.m_lambda)
        self.m_mseTracking.append(self.m_mse)
    def Solve(self):
        self.CallBack(0)
        self.Iterate()
        self.m_lastMse=self.m_mse
        self.m_MseAcc=self.m_lastMse
        while self.ccm.Continue():
            self.CallBack(self.ccm._IterationsTaken)
            self.Iterate()
        return self

