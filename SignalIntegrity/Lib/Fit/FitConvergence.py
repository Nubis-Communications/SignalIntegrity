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

class SimpleIIRFilter(object):
    def __init__(self,timeconstant):
        self.coef=1.-math.exp(-1./timeconstant)
        self.first=True
        self.output=0.
        self.delta=0.
    def Output(self,inputValue=None):
        if inputValue is None:
            return self.output
        if self.first:
            self.first=False
            newOutput=inputValue
            self.output=inputValue
        else:
            newOutput=inputValue*self.coef+self.output*(1-self.coef)
        self.delta=newOutput-self.output
        self.output=newOutput
        return self.output
    def Delta(self):
        return self.delta

class TwoTapBoxcarFilter(object):
    def __init__(self):
        self.z0=0.
        self.z1=0.
        self.output=0.
    def Output(self,inputValue=None):
        if inputValue is None:
            return self.output
        self.z1=self.z0
        self.z0=inputValue
        output=(self.z0+self.z1)/2.
        self.delta=output-self.output
        self.output=output
        return self.output
    def Delta(self):
        return self.delta

class FitConvergenceMgr(object):
    def __init__(self):
            self.Initialize()

    def Initialize(
            self,
            tolerance = 1e-6,
            maxIterations = 10000,
            lambdaTimeConstant = 50,
            mseTimeConstant = 50,
            mseUnchanging = 0.001,
            lambdaUnchanging=0.005
        ):
            self._maxIterations = maxIterations
            self._tolerance = tolerance
            self._lambdaTimeConstant = lambdaTimeConstant
            self._lambdaUnchanging = 5
            self._mseTimeConstant=mseTimeConstant
            self._mseUnchanging = mseUnchanging
            self._lambdaUnchanging = lambdaUnchanging

            self.mseFilter=SimpleIIRFilter(mseTimeConstant)
            self.lambdaFilter=SimpleIIRFilter(lambdaTimeConstant)
            self.deltaMseFilter=TwoTapBoxcarFilter()
            self.deltaLambdaFilter=TwoTapBoxcarFilter()

            self._IterationsTaken = 0

            self._Mse = 1e-10
            self._Lambda = 100.

            self._LogMse=0.
            self._LogLambda=0.

            self._FilteredLogMse=0.
            self._FilteredLogLambda=0.
            self._FilteredLogDeltaMse=0.
            self._FilteredLogDeltaLambda=0.
            self._LogDeltaMse=0.
            self._LogDeltaLambda=0.

            self._LogMseTracker=[]
            self._LogLambdaTracker=[]
            self._LogDeltaMseTracker=[]
            self._LogDeltaLambdaTracker=[]
            self._FilteredLogMseTracker=[]
            self._FilteredLogLambdaTracker=[]
            self._FilteredLogDeltaMseTracker=[]
            self._FilteredLogDeltaLambdaTracker=[]

    def IterationResults(
            self,
            newMse,
            newLambda
        ):

        newMse=max(newMse,1e-10)

        self._Mse = newMse
        self._Lambda = newLambda

        del newMse
        del newLambda

        self._LogMse=math.log10(self._Mse)
        self._LogLambda=math.log10(self._Lambda)

        self._FilteredLogMse=self.deltaMseFilter.Output(self.mseFilter.Output(self._LogMse))
        self._FilteredLogLambda=self.deltaLambdaFilter.Output(self.lambdaFilter.Output(self._LogLambda))
        self._FilteredLogDeltaMse=abs(self.deltaLambdaFilter.Delta())
        self._FilteredLogDeltaLambda=abs(self.deltaMseFilter.Delta())

        self._IterationsTaken = self._IterationsTaken + 1

        self._LogMseTracker.append(self._LogMse)
        self._LogLambdaTracker.append(self._LogLambda)
        self._FilteredLogMseTracker.append(self._FilteredLogMse)
        self._FilteredLogLambdaTracker.append(self._FilteredLogLambda)
        self._FilteredLogDeltaMseTracker.append(self._FilteredLogDeltaMse)
        self._FilteredLogDeltaLambdaTracker.append(self._FilteredLogDeltaLambda)

    def Continue(self):
        IterationsExhausted = (self._IterationsTaken >= self._maxIterations)

        MseToleranceMet = (self._Mse < self._tolerance)

        if (self._IterationsTaken > self._lambdaTimeConstant):
            LambdaFilterThresholdMet = self._FilteredLogDeltaLambda < self._lambdaUnchanging
        else: LambdaFilterThresholdMet = False

        if (self._IterationsTaken > self._mseTimeConstant):
            MseFilterThresholdMet =  self._FilteredLogDeltaMse < self._mseUnchanging
        else: MseFilterThresholdMet = False

        lambdaOkay=True

        Stop = (
            IterationsExhausted                                         or
            (not lambdaOkay)                                            or
            (LambdaFilterThresholdMet and MseFilterThresholdMet)        or
            MseToleranceMet
        )

        return not Stop

    def PlotConvergence(self):
            iterations=range(len(self._LogMseTracker))

            import matplotlib.pyplot as plt
            plt.clf()
            plt.title('mse convergance')
            plt.xlabel('iteration')
            plt.ylabel('mse')
            plt.plot(iterations,self._LogMseTracker,label='logmse')
            plt.plot(iterations,self._LogLambdaTracker,label='loglambda')
            plt.plot(iterations,self._FilteredLogLambdaTracker,label='floglambda')
            plt.plot(iterations,self._FilteredLogMseTracker,label='flogmse')
            plt.plot(iterations,self._FilteredLogDeltaMseTracker,label='flogdeltamse')
            plt.plot(iterations,self._FilteredLogDeltaLambdaTracker,label='flogdeltalambda')

            plt.legend(loc='upper right')
            plt.grid(True)
            plt.show()
