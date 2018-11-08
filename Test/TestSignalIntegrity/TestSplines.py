"""
TestSplines.py
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
import unittest
import SignalIntegrity.Lib as si
import os
from numpy import absolute

class TestSplines(unittest.TestCase):
    def testIt(self):
        x=[1.,2.,4.,8.,9.,12.,20.,21.,25.,30.]
        y=[1.,-1.,5.,6.,9.,8.,4.,2.,-5.,1.]
        P=si.spl.Spline(x,y)
        mathCadPoly = [[1.0, -3.0295104059198885, 0.0, 1.0295104059198885],
                       [-0.9999999999999929, 0.0590208118397797, 3.088531217759666, -0.809020811839777],
                       [5.000000000000007, 2.7048959408011157, -1.765593653278997, 0.2879674170196796],
                       [5.999999999999659, 2.402582731513718, 1.6900153509571574, -1.092598082470918],
                       [9.000000000000057, 2.5048191860153253, -1.5877788964555961, 0.21390935222423677],
                       [8.0, -1.2463016826638587, 0.33740527356253525, -0.030514695403694104],
                       [4.000000000000796, -1.7066388231725114, -0.39494741612612216, 0.1015862392986879],
                       [2.0, -2.1917749375287485, -0.09018869823005948, 0.05015810815306164],
                       [-5.0, -0.5056953320222703, 0.5117085996066799, -0.034113906640445335]]

        maxError=max([max([absolute(ac-ar) for (ac,ar) in zip(AC,AR)]) for (AC,AR) in zip(P.m_A,mathCadPoly)])
        self.assertTrue(maxError<1e-10,'spline polynomial wrong')

        fileName='splinesTest.txt'
        if not os.path.exists(fileName):
            P.WriteToFile(fileName)
            self.fail(fileName + ' not found')
        else:
            P.ReadFromFile(fileName)

        maxError=max([max([absolute(ac-ar) for (ac,ar) in zip(AC,AR)]) for (AC,AR) in zip(P.m_A,mathCadPoly)])
        self.assertTrue(maxError<1e-10,'spline polynomial regression wrong')

        P.WriteToFile('temp'+fileName)
        P.ReadFromFile('temp'+fileName)
        os.remove('temp'+fileName)

        maxError=max([max([absolute(ac-ar) for (ac,ar) in zip(AC,AR)]) for (AC,AR) in zip(P.m_A,mathCadPoly)])
        self.assertTrue(maxError<1e-10,'spline polynomial read/write wrong')

        import matplotlib.pyplot as plt
        K=100
        x2=[float(k)/K*32. for k in range(100)]
        y2=[P.Evaluate(x2i) for x2i in x2]
        plt.plot(x,y)
        plt.plot(x2,y2)
        plt.title('TestSplines')
        #plt.show()

        epsilon = 0.000000001
        plt.cla()
        y3=[P.EvaluateDerivative(x2i) for x2i in x2]
        y3approx=[(P.Evaluate(x2i+epsilon)-P.Evaluate(x2i))/epsilon for x2i in x2]
        plt.plot(x2,y3)
        plt.plot(x2,y3approx)
        plt.title('TestSplines')
        #plt.show()

        maxError=max([absolute(y3approxi-y3i) for (y3approxi,y3i) in zip(y3approx,y3)])
        self.assertTrue(maxError<1e-4,'spline polynomial derivative wrong')

        plt.cla()
        y4=[P.EvaluateSecondDerivative(x2i) for x2i in x2]
        y4approx=[(P.EvaluateDerivative(x2i+epsilon)-P.EvaluateDerivative(x2i))/epsilon for x2i in x2]
        plt.plot(x2,y4)
        plt.plot(x2,y4approx)
        plt.title('TestSplines')
        #plt.show()

        maxError=max([absolute(y4approxi-y4i) for (y4approxi,y4i) in zip(y4approx,y4)])
        self.assertTrue(maxError<1e-4,'spline polynomial second derivative wrong')

if __name__ == '__main__':
    unittest.main()

