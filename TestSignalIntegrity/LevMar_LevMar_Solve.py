class LevMar(CallBacker):
...
    def Iterate(self):
        if self.m_Fx is None:
            self.m_Fx=self.fF(self.m_x)
        if self.m_r is None:
            self.m_r=(matrix(self.m_Fx)-matrix(self.m_y)).tolist()
        if self.m_J is None:
            self.m_J=self.fJ(self.m_x,self.m_Fx)
        if self.m_H is None:
            self.m_H=(matrix(self.m_J).getH()*self.m_W*
                      matrix(self.m_J)).tolist()
        if self.m_D is None:
            self.m_D=zeros((len(self.m_H),len(self.m_H[0]))).tolist()
            for r in range(len(self.m_D)):
                self.m_D[r][r]=self.m_H[r][r]
        if self.m_JHWr is None:
            self.m_JHWr = (matrix(self.m_J).getH()*
            self.m_W*matrix(self.m_r)).tolist()
        Deltax=((matrix(self.m_H)+matrix(self.m_D)*
                self.m_lambda).getI()*matrix(self.m_JHWr)).tolist()
        newx=(matrix(self.m_x)-matrix(Deltax)).tolist()
        newx=self.AdjustVariablesAfterIteration(newx)
        newFx = self.fF(newx)
        newr=(matrix(newFx)-matrix(self.m_y)).tolist()
        newmse=math.sqrt((matrix(newr).getH()*self.m_W*
            matrix(newr)).tolist()[0][0].real/self.m_sumw)
        if newmse < self.m_mse:
            self.m_mse = newmse
            self.m_x = newx
            self.m_lambda = max(self.m_lambda/
                self.m_lambdaMultiplier,self.m_lambdamin)
            self.m_Fx = newFx
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

