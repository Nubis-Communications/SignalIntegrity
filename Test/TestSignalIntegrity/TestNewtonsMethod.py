"""
TestNewtonsMethod.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import unittest

import math
import SignalIntegrity as si
from numpy import matrix

class TestNewtonsMethodTests(unittest.TestCase,si.test.RoutineWriterTesterHelper):
    def fsqrt(self,y,x):
        return 0.5*(x*x+y)/x
    def newtonSqrtIterate(self,y,x,I):
        for _ in range(I):
            x=self.fsqrt(y,x)
        return x
    def testNewtonSqrt(self):
        y=0.5
        x=1
        I=5
        x=self.newtonSqrtIterate(y,x,I)
        #print x,math.sqrt(y),x-math.sqrt(y)
        self.assertLessEqual(abs(x-math.sqrt(y)),10e-16)
    def testNewtonSqrtRangeReduction(self):
        Y=32.768
        E=int(math.ceil(math.log(Y,2.)))
        Eeven=E/2*2==E
        y=Y/pow(2.0,E)
        x=1
        I=5
        x=self.newtonSqrtIterate(y,x,I)
        x=x*pow(2.0,E/2)*(math.sqrt(2) if not Eeven else 1.0)
        #print x,math.sqrt(Y),x-math.sqrt(Y)
        self.assertLessEqual(abs(x-math.sqrt(Y)),10e-16)
    def testNewtonSqrtRangeReductionRange(self):
        from random import random
        M=1000
        Y=[random()*100 for _ in range(M)]
        E=[int(math.ceil(math.log(y)/math.log(2))) for y in Y]
        Y=[y/pow(2.0,e) for (y,e) in zip(Y,E)]
        #print min(Y),max(Y)
        self.assertLessEqual(max(Y), 1.0)
        self.assertGreaterEqual(min(Y), 0.5)
    def testNewtonSqrtConstantSeed1(self):
        K=1000
        g=1.
        I=6
        Y=[0.5+float(k)/K*0.5 for k in range(K)]
        X=[[g for _ in Y] for _ in range(I)]
        for i in range(1,I):
            for k in range(len(Y)):
                X[i][k]=self.newtonSqrtIterate(Y[k],X[i-1][k],1)

        import matplotlib.pyplot as plt
        plt.cla()
        for i in range(len(X)):
            plt.semilogy(Y,[abs(x-math.sqrt(y)) for (x,y) in zip(X[i],Y)],label='iteration '+str(i),color='black')
        #plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('y')
        plt.ylabel('absolute error')
        plt.xlim(0.5,1)
        plt.ylim(1e-15,1)
        si.test.PlotTikZ('NewtonSquareRootConstantSeed1.tex',plt)
        #plt.show()
        plt.cla()
    def testNewtonSqrtConstantSeed85(self):
        K=1000
        g=0.85
        I=6
        Y=[0.5+float(k)/K*0.5 for k in range(K)]
        X=[[g for _ in Y] for _ in range(I)]
        for i in range(1,I):
            for k in range(len(Y)):
                X[i][k]=self.newtonSqrtIterate(Y[k],X[i-1][k],1)

        import matplotlib.pyplot as plt
        plt.cla()
        for i in range(len(X)):
            plt.semilogy(Y,[abs(x-math.sqrt(y)) for (x,y) in zip(X[i],Y)],label='iteration '+str(i),color='black')
        #plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('y')
        plt.ylabel('absolute error')
        plt.xlim(0.5,1)
        plt.ylim(1e-15,1)
        si.test.PlotTikZ('NewtonSquareRootConstantSeed85.tex',plt)
        #plt.show()
        plt.cla()
    def testNewtonSqrtConstantSeeded(self):
        K=1000
        seed=[0.72,0.737,0.76,0.78,0.8,0.82,0.84,0.856,0.876,0.892,0.91,0.927,0.943,0.961,0.975,0.993]
        I=6
        Y=[0.5+float(k)/K*0.5 for k in range(K)]
        SI=[int(math.floor(y*32))-16 for y in Y]
        g=[seed[s] for s in SI]
        import copy
        X=[copy.copy(g) for _ in range(I)]
        for i in range(1,I):
            for k in range(len(Y)):
                X[i][k]=self.newtonSqrtIterate(Y[k],X[i-1][k],1)

        import matplotlib.pyplot as plt
        plt.cla()
        for i in range(len(X)):
            plt.semilogy(Y,[abs(x-math.sqrt(y)) for (x,y) in zip(X[i],Y)],label='iteration '+str(i),color='black')
        #plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('y')
        plt.ylabel('absolute error')
        plt.xlim(0.5,1)
        plt.ylim(1e-15,1)
        si.test.PlotTikZ('NewtonSquareRootSeeded.tex',plt)
        #plt.show()
        plt.cla()

        plt.plot(Y,g,color='black',label='seed value')
        plt.plot(Y,[math.sqrt(y) for y in Y],color='gray',label='$\sqrt{y}$')
        plt.xlabel('y')
        plt.ylabel('values')
        plt.xlim(0.5,1)
        plt.ylim(0.7,1)
        plt.legend(loc='lower right',labelspacing=0.1)
        si.test.PlotTikZ('NewtonSquareRootSeeds.tex',plt)
        #plt.show()
        plt.cla()

    def testNewtonSqrtRangeReductionSeeded(self):
        M=1000
        from random import random
        Y=[random()*10 for _ in range(M)]
        error=[abs(self.newtonSquareRoot(y)-math.sqrt(y)) for y in Y]
        self.assertLess(max(error), 10e-15)
    def newtonSquareRoot(self,Y):
        if Y<=0.0: raise ValueError('math domain error')
        if Y<=1e-32: return 0.0
        # in practice, exponent is directly extracted from fp number
        E=int(math.ceil(math.log(Y,2.)))
        Eeven=E/2*2==E
        y=Y/pow(2.0,E) # in practice, is the mantissa of the fp number
        seed=[0.72,0.737,0.76,0.78,0.8,0.82,0.84,0.856,0.876,
              0.892,0.91,0.927,0.943,0.961,0.975,0.993]
        # in practice, seed index taken from upper nybble of mantissa
        si=int(math.floor(y*32))-16
        x=seed[si]
        for _ in range(3): x=(x+y/x)/2.0
        x=x*pow(2.0,E/2)*(1.4142135623730951 if not Eeven else 1.0)
        return x
    def testWriteNewtonSquareRoot(self):
        import os
        self.WriteCode(os.path.basename(__file__).split('.')[0]+'.py', 'newtonSquareRoot', [], printFuncName=True)
    def testCableLinearFit(self):
        import math
        from numpy import matrix
        import SignalIntegrity as si
        sp=si.sp.SParameterFile('cable.s2p')
        s21=sp.FrequencyResponse(2,1)
        f=s21.Frequencies('GHz')
        mS21=s21.Values('mag')
        K=len(f)
        X=[[1,x,math.sqrt(x)] for x in f]
        a=(matrix(X).getI()*[[y] for y in mS21]).tolist()
        yf=(matrix(X)*matrix(a)).tolist()
        r=(matrix(yf)-matrix(y)).tolist()
        sigma=math.sqrt(((matrix(r).H*matrix(r)).tolist()[0][0])/K)
        print '\[a_0 = '+"{:10.4e}".format(a[0][0])+'\]'
        print '\[a_1 = '+"{:10.4e}".format(a[1][0])+'/GHz\]'
        print '\[a_2 = '+"{:10.4e}".format(a[2][0])+'/\sqrt{GHz}\]'
        print '\[\sigma = '+"{:10.4e}".format(sigma)+'\]'
        # pragma: silent exclude
        import matplotlib.pyplot as plt
        plt.cla()
        plt.plot(f,[20*math.log10(y) for y in mS21],label='$\\left|S_{21}\\right|$',color='black')
        plt.plot(f,[20*math.log10(y[0]) for y in yf],label='fitted',color='gray')
        plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        si.test.PlotTikZ('CableFitted.tex',plt)
        #plt.show()
        plt.cla()
    def testWriteNewtonCableFit(self):
        import os
        self.WriteCode(os.path.basename(__file__).split('.')[0]+'.py', 'testCableLinearFit', [], printFuncName=False)
    def testCableLinearConstrainedFit(self):
        import math
        from numpy import matrix
        sp=si.sp.SParameterFile('cable.s2p')
        s21=sp.FrequencyResponse(2,1)
        f=s21.Frequencies('GHz')
        mS21=s21.Values('mag')
        K=len(f)
        X=[[x,math.sqrt(x)] for x in f]
        a=(matrix(X).getI()*[[y-1.0] for y in mS21]).tolist()
        yf=[[y[0]+1.0] for y in (matrix(X)*matrix(a)).tolist()]
        r=(matrix(yf)-matrix([[y] for y in mS21])).tolist()
        sigma=math.sqrt(((matrix(r).H*matrix(r)).tolist()[0][0])/K)
        print '\[a_1 = '+ str(a[0][0])+'/GHz\]'
        print '\[a_2 = '+ str(a[1][0])+ '/\sqrt{GHz}\]'
        print '\[\sigma = '+ str(sigma)+'\]'
        # pragma: silent exclude
        import matplotlib.pyplot as plt
        plt.cla()
        plt.plot(f,[20*math.log10(y) for y in mS21],label='$\\left|S_{21}\\right|$',color='black')
        plt.plot(f,[20*math.log10(y[0]) for y in yf],label='fitted',color='gray')
        plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        si.test.PlotTikZ('CableFittedConstrained.tex',plt)
        #plt.show()
        plt.cla()
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()