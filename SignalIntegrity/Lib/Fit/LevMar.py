"""
 Levenberg-Marquardt Algorithm
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

import math
from numpy import zeros,array,diag
from numpy.linalg import inv,LinAlgError,lstsq,solve
from SignalIntegrity.Lib.CallBacker import CallBacker
import copy
from SignalIntegrity.Lib.Fit.FitConvergence import FitConvergenceMgr
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionFitter

class LevMar(CallBacker):
    """Implements the Levenberg-Marquardt algorithm for non-linear fitting  
    To use this class, you derive your class for fitting some arbitrary
    function to some data from LeVmar.  The function must contain, at a minimum, an
    __init__ function for construction and a function fF(self,a), which implements
    the function y=f(a) where ideally a is a vector of numbers and y is a vector of
    numbers in matrix form.  In other words, if you are fitting a 3 variable function
    f(a0,a1,a2)=y - you are trying to find the best values of a0, a1, and a2 that
    cause f(a0,a1,a2) to be the closes to y in a least-squares sense, then your
    a would be something like [[a0],[a1],[a2]] and your y would look similar.  In
    this way, a is a 3x1 element matrix.  
    During the fit, LevMar will call the function fJ, which in turn calls fPartialFPartiala
    with a and m being the index of the variable in a to take the derivative with respect
    to. If your derived class does not overload fJ and/or fPartialFPartiala, LevMar will
    compute a numerical derivative using the value self.m_epsilon as the delta.  If
    you have analytic derivatives and don't want derivatives calculated numerically,
    you overload fJ and return a matrix that is R a M where R is the number of elements
    in y and M is the number of elements in a where each J[r][m] is the partial derivative
    of F with respect a[m] at element r of the output.
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
    def fF(self,a):
        """implements F(a)
        @param a list of lists representing matrix a
        @return F(a) in the overloaded function
        if the function is not overloaded in the derived class, raises an exception
        @throw raise if not overloaded.
        """
        raise SignalIntegrityExceptionFitter('fF must be overloaded')
    def fPartialFPartiala(self,a,m,Fa=None):
        """partial derivative of F(a) with respect to a[m]
        @param a list of lists matrix a
        @param m index of element in a which to take partial derivative with respect to
        @param Fa optional previously calculated F(a) to avoid double calculation
        @return the partial derivative of F(a) with respect to element m in a
        """
        aplusDeltaa = copy.copy(a)
        aplusDeltaa[m][0]=aplusDeltaa[m][0]+self.m_epsilon
        if Fa is None:
            Fa = self.fF(a)
        dFa = (self.fF(aplusDeltaa)-Fa)/self.m_epsilon
        return dFa
    def fJ(self,a,Fa=None):
        """Calculates the Jacobian matrix.
        @param a list of lists matrix a
        @param Fa optional previously calculated F(a) to avoid double calculation
        @return the Jacobian matrix 
        The Jacobian matrix is R x M where R is the number of elements in F(a) and M
        is the number of elements in a where each J[r][m] is the partial derivative
        of F with respect a[m] at element r of the output.

        This function can be overloaded in the derived class if analytic partial derivatives are
        known, otherwise numerical partial derivatives are calculated using fPartialFPartiala()
        """
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
        """AdjustVariablesAfterIteration
        @param a list of lists matrix a
        a contains the new variables produced as a result of an iteration

        if not overridden, nothing happens, but if this function is overridden in the derived class,
        it provides an opportunity to make adjustments to the variables.  Examples are things like making
        variables real when during iteration they could become complex or making variables positive.
        The good thing about this function is that these adjustments are made prior to making decisions
        on the success of the iteration meaning that sometime the a resulting from an iteration reduces
        mean-squared error between F(a) and y, but the a values are invalid and only valid after adjustment.
        If, after the adjustment, the mean-squared error is not reduced, the iteration fails.
        """
        return a
    def Initialize(self,a,y,w=None):
        """Initializes the fitter for optimizing the values of F(a) such that they equal y in a weighted
        least-squares sense, with w providing the weights.
        @param a list of lists matrix a
        @param y list of lists matrix y
        @param w (optional) list of lists weights matrix w
        """
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
    def Iterate(self):
        """Performs one iteration.  
        Usually, this function should not be used.  It can be used to take each iteration manually.  
        Usually Solve() is used, which takes these iterations, but tests convergence and decides
        when the iterating should end.
        """
        if self.m_Fa is None:
            self.m_Fa=self.fF(self.m_a)
        if self.m_r is None:
            self.m_r=self.m_Fa-self.m_y
        if self.m_J is None:
            self.m_J=self.fJ(self.m_a,self.m_Fa)
        # pragma: silent exclude
        if self.m_J.shape[1]>self.m_J.shape[0]: # fat matrix - underconstrained
            if self.m_H is None:
                self.m_H=lstsq(self.m_J,self.m_r,0.001)[0]
            Deltaa=self.m_H/float(self.m_lambda)
        else:
            # pragma: include outdent
            if self.m_H is None:
                self.m_H=self.m_J.conj().T.dot(self.m_W).dot(self.m_J)
            if self.m_JHWr is None:
                self.m_JHWr=self.m_J.conj().T.dot(self.m_W).dot(self.m_r)
            HplD=copy.copy(self.m_H)
            for r in range(HplD.shape[0]): HplD[r][r]*=(1.+self.m_lambda)
            # pragma: silent exclude
            try:
                # pragma: include outdent
                Deltaa=solve(HplD,self.m_JHWr)
            # pragma: silent exclude indent
            except LinAlgError:
                Deltaa=lstsq(HplD,self.m_JHWr,0.001)[0]
        # pragma: include indent
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
        """Solves for a such that F(a) equals y in a weighted least-squares sense."""
        self.Iterate()
        self.m_lastMse=self.m_mse
        self.m_MseAcc=self.m_lastMse
        while self.ccm.Continue():
            self.CallBack(self.ccm._IterationsTaken)
            self.Iterate()
        return self

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
    # @var ccm
    # instance of class FitConvergenceMgr that monitors and determines convergence.
