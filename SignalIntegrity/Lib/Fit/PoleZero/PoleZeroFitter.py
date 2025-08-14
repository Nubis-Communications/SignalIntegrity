"""
PoleZeroFitter.py
"""
# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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
import numpy as np

from SignalIntegrity.Lib.Fit.PoleZero.QuadraticComplex import TransferFunctionComplexVectorized
from SignalIntegrity.Lib.Fit.PoleZero.QuadraticMagnitude import TransferFunctionMagnitudeVectorized
from SignalIntegrity.Lib.Fit.PoleZero.BiquadComplex import TransferFunctionBiquadVectorized
from SignalIntegrity.Lib.Fit.PoleZero.PoleZeroGuess import PoleZeroGuess

from SignalIntegrity.Lib.Fit.LevMar import LevMar

class PoleZeroLevMar(LevMar):
    """fits a pole/zero model to a frequency response"""
    def __init__(self,fr,num_zero_pairs,num_pole_pairs,
                 guess=None,
                 max_delay=None,
                 min_delay=0,
                 max_Q=5.,
                 initial_delay=0,
                 LHP_zeros=True,
                 real_zeros=False,
                 fit_type='magnitude',
                 max_iterations=100000,
                 mse_unchanging_threshold=1e-6,
                 initial_lambda=None,
                 lambda_multiplier=None,
                 max_frequency_multiplier=5,
                 tolerance=None,
                 fix_delay=False,
                 fix_gain=False,
                 callback=None):
        """Constructor  
        Initializes the fit of a pole/zero model to a frequency response.
        @param fr instance of class FrequencyResponse to fit to.
        @param num_zero_pairs int number of zero pairs.
        @param num_pole_pairs in number of pole pairs.
        """
        self.num_zero_pairs=num_zero_pairs
        self.num_pole_pairs=num_pole_pairs
        self.min_delay=min_delay
        self.max_delay=max_delay
        self.initial_delay=initial_delay
        self.max_Q=max_Q
        self.LHP_zeros=LHP_zeros
        self.real_zeros=real_zeros
        self.fit_type=fit_type
        self.initial_lambda=initial_lambda
        self.lambda_multiplier=lambda_multiplier
        self.tolerance=tolerance
        self.max_frequency_multiplier = max_frequency_multiplier
        self.fix_delay=fix_delay
        self.fix_gain=fix_gain
        self.f=fr.Frequencies()
        # determine the right scaling factor for frequencies
        # it's the best engineering exponent
        self.mul=math.pow(10,math.floor(math.log10(self.f[-1])/3)*3)
        # scale all of the frequencies by this multiplier
        self.f=[v/self.mul for v in self.f]
        self.w=[2.*math.pi*f for f in self.f]
        self.y=np.array(fr.Values('mag' if self.fit_type == 'magnitude' else None)).reshape(-1, 1)
        self._tf_class = TransferFunctionMagnitudeVectorized if self.fit_type == 'magnitude' else TransferFunctionComplexVectorized
        if guess is None:
            guess=PoleZeroGuess.Guess7(self.f[1], self.f[-1], num_zero_pairs,num_pole_pairs)
            guess[0]=self.y[0][0]
            guess[1]=self.initial_delay*self.mul
        else:
            guess[1]=guess[1]*self.mul
            for s in range(self.num_pole_pairs+self.num_zero_pairs):
                guess[s*2+2+0] = guess[s*2+2+0]/self.mul
        LevMar.__init__(self,callback)
        LevMar.Initialize(self, np.array(guess).reshape(-1,1), np.array(self.y))
        self.ccm.Initialize(tolerance=self.ccm._tolerance,
                            maxIterations=max_iterations,
                            lambdaTimeConstant=self.ccm._lambdaTimeConstant,
                            mseTimeConstant=self.ccm._mseTimeConstant,
                            mseUnchanging=mse_unchanging_threshold,
                            lambdaUnchanging=self.ccm._lambdaUnchanging)
        if self.lambda_multiplier != None:
            self.m_lambdaMultiplier=self.lambda_multiplier
        if self.initial_lambda != None:
            self.m_lambda=self.initial_lambda
        if self.tolerance != None:
            self.ccm._tolerance = self.tolerance
        # self.ccm._lambdaUnchanging=0
        self.ccm._tolerance=0
    def fF(self,a):
        self.tf=self._tf_class(self.w,a,self.num_zero_pairs,self.num_pole_pairs)
        return np.array(self.tf.fF).reshape(-1, 1)
    def fJ(self,a,Fa=None):
        # self.tf=self._tf_class(self.w,a,self.num_zero_pairs,self.num_pole_pairs)
        return np.array(self.tf.fJ)
    def AdjustVariablesAfterIteration(self,a):
        from random import random
        wmax=self.f[-1]*2.*np.pi*self.max_frequency_multiplier
        # variables must be real
        for r in range(len(a)):
            a[r][0]=a[r][0].real
        # for r in range(len(a)):
        #     a[r][0]=a[r][0]+random()/1000000
        # delay greater than minimum
        if self.min_delay != None:
            a[1][0]=max(a[1][0],self.min_delay*self.mul)
        # delay must less than maximum
        if self.max_delay != None:
            a[1][0]=min(a[1][0],self.max_delay*self.mul)
        # Q cant be too high
        for r in range(3,len(a),2):
            a[r][0]=max(min(a[r][0],self.max_Q+random()/100),-self.max_Q-random()/100)
        # poles must be in the LHP
        for r in range(self.num_pole_pairs):
            a[r*2+2+self.num_zero_pairs*2+1][0]=abs(a[r*2+2+self.num_zero_pairs*2+1][0])
        if self.LHP_zeros == True:
            # zeros must be in the LHP
            for r in range(self.num_zero_pairs):
                a[r*2+2+1][0]=abs(a[r*2+2+1][0])
        if self.real_zeros:
            # zeros must be real
            for r in range(self.num_zero_pairs):
                a[r*2+2+1][0]=min(a[r*2+2+1][0],0.5+random()/100)
        # w0 can't be too high
        for r in range(2,len(a),2):
            a[r][0]=abs(a[r][0])
            a[r][0]=min(a[r][0],wmax+random()/100)
        # fix DC gain
        if self.fix_gain:
            a[0][0]=self.y[0][0].real
        return a
    def Results(self):
        results=[self.m_a[r][0].real for r in range(self.m_a.shape[0])]
        results[1]=results[1]/self.mul
        for s in range(self.num_pole_pairs+self.num_zero_pairs):
            results[s*2+2+0]=results[s*2+2+0]*self.mul
        return results
    def PrintResults(self):
        results=[self.m_a[r][0].real for r in range(self.m_a.shape[0])]
        from SignalIntegrity.Lib.ToSI import ToSI
        print(f"Gain: {results[0]} - {ToSI(20.*np.log10(np.abs(results[0])),'dB',round=4)}")
        print(f"Delay: {ToSI(results[1]/self.mul,'s',round=4)}")
        num_zero_pairs=self.num_zero_pairs
        print(f"Number of zero pairs: {num_zero_pairs}")
        for s in range(num_zero_pairs):
            print(f"zero pair: {s+1}")
            print(f"  fz: {ToSI(results[s*2+2+0]*self.mul/(2.*np.pi),'Hz',round=4)}")
            print(f"  Qz: {ToSI(results[s*2+2+1],'',round=4)}")
        num_pole_pairs=self.num_pole_pairs
        print(f"Number of pole pairs: {num_pole_pairs}")
        for s in range(num_pole_pairs):
            print(f"pole pair: {s+1}")
            print(f"  fp: {ToSI(results[(s+num_zero_pairs)*2+2+0]*self.mul/(2.*np.pi),'Hz',round=4)}")
            print(f"  Qp: {ToSI(results[(s+num_zero_pairs)*2+2+1],'',round=4)}")
        return self
    def WriteResultsToFile(self,filename):
        results=[self.m_a[r][0].real for r in range(self.m_a.shape[0])]
        for s in range(self.num_pole_pairs+self.num_zero_pairs):
            results[s*2+2]=results[s*2+2]*self.mul
        results=[self.num_zero_pairs,self.num_pole_pairs]+[self.m_a[r][0].real for r in range(self.m_a.shape[0])]
        with open(filename,'wt') as f:
            for result in results:
                f.write(str(result)+'\n')
        return self
    @staticmethod
    def ReadResultsFile(filename):
        with open(filename,'rt') as f:
            result=f.readlines()
        return [int(result[0]),int(result[1])]+[float(res) for res in result[2:]]
    def WriteGoalToFile(self,filename):
        with open(filename,'wt') as f:
            for n in range(len(self.f)):
                f.write(str(self.f[n])+'\n')
                f.write(str(self.m_y[n][0].real)+'\n')
                f.write(str(self.m_y[n][0].imag)+'\n')
if __name__ == '__main__': # pragma: no cover
    #o=BiquadSection(0.147,0.989,0.119,0.602,0.532)
    o=ZeroPairMagnitude(0.147,0.989,0.119)
    o=PolePairMagnitude(0.147,0.602,0.532)
    pass
