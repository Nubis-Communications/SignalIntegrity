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

class FitConvergenceMgr(object):
    def __init__(
            self,
            tolerance = 0,
            maxIterations = 1000,
            lambdaStart = 100,
            lambdaChange = 10,
            lambdaMax = 1e10,
            lambdaMin = 1e-10,
            lambdaTimeConstant = 50,
            mseTimeConstant = 50,
            lambdaUnchanging = 2.5,
            mseUnchanging = 2.5,
            bOptimizeAfterMSEMet = False,
            iIterationsAllowedAfterMSEMet = 2
        ):
            self.Initialize(
                tolerance,
                maxIterations,
                lambdaStart,
                lambdaChange,
                lambdaMax,
                lambdaMin,
                lambdaTimeConstant,
                mseTimeConstant,
                lambdaUnchanging,
                mseUnchanging,
                bOptimizeAfterMSEMet,
                iIterationsAllowedAfterMSEMet
            )

    def Initialize(
            self,
            tolerance = .0004,
            maxIterations = 100,
            lambdaStart = 1e3,
            lambdaChange = 10,
            lambdaMax = 1e10,
            lambdaMin = 1e-10,
            lambdaTimeConstant = 5,
            mseTimeConstant = 5,
            lambdaUnchanging = 2.5,
            mseUnchanging = 1.5,
            bOptimizeAfterMSEMet = False,
            iIterationsAllowedAfterMSEMet = 2
        ):
            self._maxIterations = maxIterations
            self._tolerance = tolerance
            self._lambdaTimeConstant = lambdaTimeConstant
            self._mseTimeConstant = mseTimeConstant
            self._lambdaUnchanging = lambdaUnchanging
            self._mseUnchanging = mseUnchanging
            self._lambdaMax = lambdaMax
            self._lambdaMin = lambdaMin
            self._lambdaStart = lambdaStart
            self._lambdaChange = lambdaChange
            self._bOptimizeAfterMSEMet = bOptimizeAfterMSEMet
            self._iIterationsAllowedAfterMSEMet = iIterationsAllowedAfterMSEMet

            self._ValuesTracked = 0

            self._MseTracker=[]
            self._LambdaTracker=[]

            self._mseCoef=1.-math.exp(-1./self._mseTimeConstant)
            self._lamdaCoef=1.-math.exp(-1./self._lambdaTimeConstant)

            self._LatestMse = 0
            self._LatestLambda = 0

            self._MseFilterOutput = 0
            self._LambdaFilterOutput = 0

            self._IterationsTaken = 0
            self._IterationsTakenAfterMSEMet = 0

    def IterationResults(
            self,
            iterationNumber,
            newMse,
            newLambda
        ):
        self._LatestMse = max(newMse,1e-10)
        self._LatestLambda = max(newLambda,1e-10)

        self._IterationsTaken = iterationNumber


        logmse=math.log10(self._LatestMse)
        loglambda=math.log10(self._LatestLambda)

        self._MseFilterOutput=logmse*self._mseCoef+self._MseFilterOutput*(1.-self._mseCoef)
        self._LambdaFilterOutput=loglambda*self._lamdaCoef+self._LambdaFilterOutput*(1-self._lamdaCoef)

        self._LambdaTracker.append(loglambda)
        self._MseTracker.append(logmse)

        self._ValuesTracked=self._ValuesTracked+1

    def LambdaInLimits(self,Lambda):
        return ((Lambda < self._lambdaMax) and (Lambda > self._lambdaMin))

    def Continue(self):
        IterationsExhausted = (self._IterationsTaken >= self._maxIterations)
        LambdaOkay = self.LambdaInLimits(self._LatestLambda)

        if (self._ValuesTracked > self._lambdaTimeConstant):
            LambdaFilterThresholdMet = abs(math.log10(self._LatestLambda) - self._LambdaFilterOutput) < self._lambdaUnchanging
        else: LambdaFilterThresholdMet = False

        if (self._ValuesTracked > self._mseTimeConstant):
            MseFilterThresholdMet =  abs(math.log10(self._LatestMse) - self._MseFilterOutput) < self._mseUnchanging
        else: MseFilterThresholdMet = False

        MseFilterThresholdMet=False
        LambdaFilterThresholdMet=False

        MseToleranceMet = (self._LatestMse < self._tolerance)

        ## if OptimizeAfterMSEMet = true, then when the MSEToleranceMet, do some more specific amount of iterations
        ## to see if we can converge to a better solution.  This allows us to keep the required MSE value low and
        ## still get good convergence when locally available
        IterationsExhaustedAfterMSEMet = False
        if (MseToleranceMet and self._bOptimizeAfterMSEMet):
            IterationsExhaustedAfterMSEMet = (self._IterationsTakenAfterMSEMet >= self._iIterationsAllowedAfterMSEMet)
            self._IterationsTakenAfterMSEMet=self._IterationsTakenAfterMSEMet+1

        Stop = (
            IterationsExhausted                                         or
            IterationsExhaustedAfterMSEMet                              or
            (not LambdaOkay)                                            or
            (LambdaFilterThresholdMet and MseFilterThresholdMet)        or
            (MseToleranceMet and not self._bOptimizeAfterMSEMet)
        )
        
        if Stop:
            print "will stop:"
            if IterationsExhausted: print 'iterations exhausted'
            if IterationsExhaustedAfterMSEMet: print 'iterations exhausted after mse met'
            if not LambdaOkay: print 'lambda not okay'
            if (LambdaFilterThresholdMet and MseFilterThresholdMet): print 'lambda and mse filter met'
            if (MseToleranceMet and not self._bOptimizeAfterMSEMet): print 'mse tolerance met'

        return not Stop
