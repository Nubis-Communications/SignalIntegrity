'''
Created on Jan 26, 2018

@author: pete
'''
import unittest
import SignalIntegrity as si
import math
import cmath
import os

from TestHelpers import SParameterCompareHelper,RoutineWriterTesterHelper

class TestRLGCLevMar(unittest.TestCase,si.test.PySIAppTestHelper,RoutineWriterTesterHelper,SParameterCompareHelper):
    def __init__(self, methodName='runTest'):
        SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.PySIAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        RoutineWriterTesterHelper.__init__(self)
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    def testAAARLGCFit(self):
        sp=si.sp.SParameterFile('cableForRLGC.s2p')
        guess=[1.,114.241e-9,0,43.922e-12,80e-6,100e-6]
        #guess=[0.,114.241e-9,0,43.922e-12,0,0]
        guess=[0,200e-9,0,50e-12,0,0]
        #guess=[19.29331239903912,1.0169921429695769e-07,6.183111656296168e-10,0.007419799613583727,0.0001040252514702244,0.00037025795321293044]
        self.m_fitter=si.fit.RLGCSolver(sp,guess,self.PrintProgress)
        self.m_fitter.Solve()
        print self.m_fitter.Results().tolist()
    def PrintProgress(self,iteration):
        print self.m_fitter.m_iteration,self.m_fitter.m_filterOutput
    def testCompareApproxWithEquation(self):
        return
        Z0=50.
        (R,L,G,C,Rse,df)=[0.,114.241e-9,0,43.922e-12,80e-6,100e-6]
        fList=si.fd.EvenlySpacedFrequencyList(40e9,2000)
        model1=si.sp.dev.ApproximateTwoPortTLine(fList, R, Rse, L, G, C, df, Z0, 100000)
        seriesZ=[Rse*math.sqrt(f)+1j*2.*math.pi*f*L for f in fList]
        shuntY=[G+2.*math.pi*f*C*(1j+df) for f in fList]
        gamma=[cmath.sqrt(z*y) for (z,y) in zip(seriesZ,shuntY)]
        rho=[Z0 if y==0.0 else cmath.sqrt(z/y) for (z,y) in zip(seriesZ,shuntY)]
        D=[1-r*r*cmath.exp(2.*g) for (r,g) in zip(rho,gamma)]
        S11=[r*(1-cmath.exp(2*g))/d for (r,g,d) in zip(rho,gamma,D)]
        S12=[(1.-r*r)*cmath.exp(g)/d for (r,g,d) in zip(rho,gamma,D)]
        model2=si.sp.SParameters(fList,[[[s11,s12],[s12,s11]] for (s11,s12) in zip(S11,S12)])
        self.SParameterRegressionChecker(model1, 'model1.s2p')
        self.SParameterRegressionChecker(model2, 'model2.s2p')
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()