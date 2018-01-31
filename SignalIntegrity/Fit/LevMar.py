'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''

import math
from numpy import zeros,matrix
from SignalIntegrity.CallBacker import CallBacker
import copy

class LevMar(CallBacker):
    def __init__(self,callback=None):
        self.m_lambda=1
        self.m_lambdamin=1e-15
        self.m_lambdamax=1e9
        self.m_lambdaMultiplier = 10.
        self.m_epsilon = 1e-19
        self.m_iteration=0
        self.m_ConverganceThreshold=7
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
    def Iterate(self):
        self.m_iteration=self.m_iteration+1
        if self.m_Fx is None:
            self.m_Fx=self.fF(self.m_x)
        if self.m_r is None:
            self.m_r=(matrix(self.m_Fx)-matrix(self.m_y)).tolist()
        if self.m_J is None:
            self.m_J=self.fJ(self.m_x,self.m_Fx)
        if self.m_H is None:
            self.m_H=(matrix(self.m_J).getH()*self.m_W*matrix(self.m_J)).tolist()
        if self.m_D is None:
            self.m_D=zeros((len(self.m_H),len(self.m_H[0]))).tolist()
            for r in range(len(self.m_D)):
                self.m_D[r][r]=self.m_H[r][r]
        if self.m_JHWr is None:
            self.m_JHWr = (matrix(self.m_J).getH()*self.m_W*matrix(self.m_r)).tolist()
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
            self.m_lambda = max(self.m_lambda/self.m_lambdaMultiplier,self.m_lambdamin)
            self.m_Fx = newFx
            self.m_r = newr
            self.m_J = None
            self.m_H = None
            self.m_D = None
            self.m_JHWr = None
        else:
            self.m_lambda = min(self.m_lambda*self.m_lambdaMultiplier,self.m_lambdamax)
        self.m_lambdaTracking.append(self.m_lambda)
        self.m_mseTracking.append(self.m_mse)
    def TestConvergance(self):
        self.m_MseChange=self.m_mse-self.m_lastMse
        self.m_lastMse=self.m_mse
        self.m_MseAcc=0.95*self.m_MseAcc+0.05*self.m_MseChange
        try:
            self.m_filterOutput=-math.log10(-self.m_MseAcc)
        except:
            self.m_filterOutput=0.
        if self.m_filterOutput > self.m_ConverganceThreshold:
            return True
        if self.m_lambda == self.m_lambdamin:
            return True
        if self.m_lambda == self.m_lambdamax:
            return True
        return False
    def Solve(self):
        self.Iterate()
        self.m_lastMse=self.m_mse
        self.m_MseAcc=self.m_lastMse
        while not self.TestConvergance():
            self.CallBack(self.m_iteration)
            self.Iterate()

