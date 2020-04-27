class LevMar(CallBacker):
...
    def Iterate(self):
        if self.m_Fa is None:
            self.m_Fa=self.fF(self.m_a)
        if self.m_r is None:
            self.m_r=(array(self.m_Fa)-array(self.m_y)).tolist()
        if self.m_J is None:
            self.m_J=self.fJ(self.m_a,self.m_Fa)
        if self.m_H is None:
            self.m_H=(array(self.m_J).conj().T.dot(self.m_W).dot(
                      array(self.m_J))).tolist()
        if self.m_D is None:
            self.m_D=zeros((len(self.m_H),len(self.m_H[0]))).tolist()
            for r in range(len(self.m_D)):
                self.m_D[r][r]=self.m_H[r][r]
        if self.m_JHWr is None:
            self.m_JHWr = (array(self.m_J).conj().T.dot(
            self.m_W).dot(array(self.m_r))).tolist()
        Deltaa=(inv(array(self.m_H)+array(self.m_D).dot(
                self.m_lambda)).dot(array(self.m_JHWr))).tolist()
        newa=(array(self.m_a)-array(Deltaa)).tolist()
        newa=self.AdjustVariablesAfterIteration(newa)
        newFa = self.fF(newa)
        newr=(array(newFa)-array(self.m_y)).tolist()
        newmse=math.sqrt(array(newr).conj().T.dot(self.m_W).dot(
            array(newr)).tolist()[0][0].real/self.m_sumw)
        if newmse < self.m_mse:
            self.m_mse = newmse
            self.m_a = newa
            self.m_lambda = max(self.m_lambda/
                self.m_lambdaMultiplier,self.m_lambdamin)
            self.m_Fa = newFa
            self.m_r = newr
            self.m_J = None
            self.m_H = None
            self.m_D = None
            self.m_JHWr = None
        else:
            self.m_lambda = min(self.m_lambda*
                self.m_lambdaMultiplier,self.m_lambdamax)
        self.ccm.IterationResults(self.m_mse, self.m_lambda)
        self.m_lambdaTracking.append(self.m_lambda)
        self.m_mseTracking.append(self.m_mse)
    def Solve(self):
        self.Iterate()
        self.m_lastMse=self.m_mse
        self.m_MseAcc=self.m_lastMse
        while self.ccm.Continue():
            self.CallBack(self.ccm._IterationsTaken)
            self.Iterate()
        return self

