"""
 Levenberg-Marquardt Algorithm
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

import math
from numpy import zeros,matrix
from SignalIntegrity.CallBacker import CallBacker
import copy
from SignalIntegrity.Fit.FitConvergence import FitConvergenceMgr

class LevMar(CallBacker):
    """Implements the Levenberg-Marquardt algorithm for non-linear fitting

    To use this class, you derive your class for fitting some arbitrary
    function to some data from LeVmar.  The function must contain, at a minimum, an
    __init__ function for construction and a function fF(self,x), which implements
    the function y=f(x) where ideally x is a vector of numbers and y is a vector of
    numbers in matrix form.  In other words, if you are fitting a 3 variable function
    f(a0,a1,a2)=y - you are trying to find the best values of a0, a1, and a2 that
    cause f(a0,a1,a2) to be the closes to y in a least-squares sense, then your
    x would be something like [[a0],[a1],[a2]] and your y would look similar.  In
    this way, x is a 3x1 element matrix.

    During the fit, LevMar will call the function fJ, which in turn calls fPartialFPartialx
    with x and m being the index of the variable in x to take the derivative with respect
    to. If your derived class does not overload fJ and/or fPartialFPartialx, LevMar will
    compute a numerical derivative using the value self.m_epsilon as the delta.  If
    you have analytic derivatives and don't want derivatives calculated numerically,
    you overload fJ and return a matrix that is R x M where R is the number of elements
    in y and M is the number of elements in x where each J[r][m] is the partial derivative
    of F with respect x[m] at element r of the output.
    """
    def __init__(self,callback=None):
        """Constructor
        @param callback a callback function to call during calculation
        """
        self.m_lambda=1000
        self.m_lambdamin=1e-15
        self.m_lambdamax=1e9
        self.m_lambdaMultiplier = 2.
        self.m_epsilon = 1e-19
        self.ccm=FitConvergenceMgr()
        CallBacker.__init__(self,callback)
    def fF(self,x):
        """implements F(x)
        @param x list of lists representing matrix x
        @return F(x) in the overloaded function
        if the function is not overloaded in the derived class, raises an exception
        @throw raise if not overloaded.
        """
        raise
    def fPartialFPartialx(self,x,m,Fx=None):
        """partial derivative of F(x) with respsect to x[m]
        @param x list of lists matrix x
        @param m index of element in x which to take partial derivative with respect to
        @param Fx optional previously calculated F(x) to avoid double calculation
        @return the partial derivative of F(x) with respect to element m in x
        """
        xplusDeltax = x.copy()
        xplusDeltax[m][0]=x[m][0]+self.m_epsilon
        if Fx is None:
            Fx = self.fF(x)
        dFx = (self.fF(xplusDeltax)-Fx)/self.m_epsilon
        return dFx
    def fJ(self,x,Fx=None):
        """Calculates the Jacobian matrix.
        @param x list of lists matrix x
        @param Fx optional previously calculated F(x) to avoid double calculation
        @return the Jacobian matrix 
        The Jacobian matrix is R x M where R is the number of elements in F(x) and M
        is the number of elements in x where each J[r][m] is the partial derivative
        of F with respect x[m] at element r of the output.

        This function can be overloaded in the derived class if analytic partial derivatives are
        known, otherwise numerical partial derivatives are calculated using fPartialFPartialx()
        """
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
        """AdjustVariablesAfterIteration
        @param x list of lists matrix x
        x contains the new variables produced as a result of an iteration

        if not overridden, nothing happens, but if this function is overridden in the derived class,
        it provides an opportunity to make adjustments to the variables.  Examples are things like making
        variables real when during iteration they could become complex or making variables positive.
        The good thing about this function is that these adjustments are made prior to making decisions
        on the success of the iteration meaning that sometime the x resulting from an iteration reduces
        mean-squared error between F(x) and y, but the x values are invalid and only valid after adjustment.
        If, after the adjustment, the mean-squared error is not reduced, the iteration fails.
        """
        return x
    def Initialize(self,x,y,w=None):
        """Initializes the fitter for optimizing the values of F(x) such that they equal y in a weighted
        least-squares sense, with w providing the weights.
        @param x list of lists matrix x
        @param y list of lists matrix y
        @param w (optional) list of lists weights matrix w
        """
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
    def Iterate(self):
        """Performs one iteration.

        Usually, this function should not be used.  It can be used to take each iteration manually.

        Usually Solve() is used, which takes these iterations, but tests convergence and decides
        when the iterating should end.
        """
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
        """Solves for x such that F(x) equals y in a weighted least-squares sense."""
        self.Iterate()
        self.m_lastMse=self.m_mse
        self.m_MseAcc=self.m_lastMse
        while self.ccm.Continue():
            self.CallBack(self.ccm._IterationsTaken)
            self.Iterate()

    ## 
    # @var m_lambda
    # starting value for lambda
    # @var m_lambdamin
    # minimum value of lambda
    # @var m_lambdamax
    # maximum value of lambda
    # @var m_lambdaMultiplier
    # amount to multiply by lambda on successful iterations (and amount to divide lambda by on unsuccessful ones)
    # @var m_epsilon
    # delta used for numerical derivative calculation
    # @var m_iteration
    # iteration number
    #
