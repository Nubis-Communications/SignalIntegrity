'''
Created on Jan 26, 2018

@author: pete
'''
import unittest
import SignalIntegrity as si
import math
import cmath
import os
from numpy import zeros,matrix
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
        return
        sp=si.sp.SParameterFile('cableForRLGC.s2p')
        guess=[1.,114.241e-9,0,43.922e-12,80e-6,100e-6]
        #guess=[0.,114.241e-9,0,43.922e-12,0,0]
        guess=[0,200e-9,0,50e-12,0,0]
        #guess=[19.29331239903912,1.0169921429695769e-07,6.183111656296168e-10,0.007419799613583727,0.0001040252514702244,0.00037025795321293044]
        self.m_fitter=si.fit.RLGCFitter(sp,guess,self.PrintProgress)
        self.m_fitter.Solve()
        print self.m_fitter.Results()
    def testRLGCTestFitExact(self):
        return
        (R,L,G,C,Rse,df)=[1.,114.241e-9,0,43.922e-12,80e-6,100e-6]
        Z0=50.
        fList=[f for f in si.fd.EvenlySpacedFrequencyList(40e9,1000)[1:]]
        self.sp=si.sp.dev.TLineTwoPortRLGC(fList, R, Rse, L, G, C, df, Z0)
        guess=[1.,114.241e-9,0,43.922e-12,80e-6,100e-6]
        guess=[0.,115e-9,0,40e-12,0,0]
        #guess=[0,200e-9,0,50e-12,0,0]
        #guess=[19.29331239903912,1.0169921429695769e-07,6.183111656296168e-10,0.007419799613583727,0.0001040252514702244,0.00037025795321293044]
        self.plotInitialized=False
        self.m_fitter=si.fit.RLGCFitter(self.sp,guess,self.PlotResult)
        self.m_fitter.m_ConverganceThreshold=6
        self.m_fitter.Solve()
        print self.m_fitter.Results()
        (R,L,G,C,Rse,df)=[r[0] for r in self.m_fitter.Results()]
        fitsp=si.sp.dev.TLineTwoPortRLGC(fList, R, Rse, L, G, C, df, Z0)
        SpAreEqual=self.SParametersAreEqual(sp, fitsp,1e-3)
        if  not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(self.sp.m_P):
                    for c in range(self.sp.m_P):
                        plt.semilogy(self.sp.f(),[abs(fitsp[n][r][c]-self.sp[n][r][c]) for n in range(len(self.sp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()
        self.assertTrue(SpAreEqual,'RLGC fit did not succeed')
    def PrintProgress(self,iteration):
        print self.m_fitter.m_iteration,self.m_fitter.m_mse,self.m_fitter.m_filterOutput
    def PlotResult(self,iteration):
        self.PrintProgress(iteration)
        import matplotlib.pyplot as plt
        if not self.plotInitialized:
            plt.gcf()
            plt.clf()
            plt.title('s-parameter compare')
            plt.xlabel('frequency (Hz)')
            plt.ylabel('amplitude')
            plt.legend(loc='upper right')
            plt.grid(True)
            self.plotInitialized=False
        (R,L,G,C,Rse,df)=[r[0] for r in self.m_fitter.Results()]
        print R
        fList=self.m_fitter.f
        Z0=self.m_fitter.Z0
        fitsp=si.sp.dev.TLineTwoPortRLGC(fList, R, Rse, L, G, C, df, Z0)
        for r in range(fitsp.m_P):
            for c in range(fitsp.m_P):
                plt.semilogy(self.sp.f(),[abs(fitsp[n][r][c]-self.sp[n][r][c]) for n in range(len(fitsp))],label='S'+str(r+1)+str(c+1))
        plt.show(block=False)
    def testCompareApproxWithEquation(self):
        return
        Z0=50.
        (R,L,G,C,Rse,df)=[0.,114.241e-9,0,43.922e-12,80e-6,100e-6]
        fList=si.fd.EvenlySpacedFrequencyList(40e9,2000)
        model1=si.sp.dev.TLineTwoPortRLGCApproximate(fList, R, Rse, L, G, C, df, Z0, 100000)
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
    def testRLGCExtractExact(self):
        return
        (R,L,G,C,Rse,df)=[5,45e-9,0.01,22.2222e-12,0,0]
        (R,L,G,C,Rse,df)=[0.,114.241e-9,0,43.922e-12,80e-6,100e-6]
        Z0=50
        Tdest=math.sqrt(L*C)
        print Tdest
        fList=[f for f in si.fd.EvenlySpacedFrequencyList(40e9,200)[1:]]
        sp=si.sp.dev.TLineTwoPortRLGC(fList, R, Rse, L, G, C, df, Z0)
        S11=sp.FrequencyResponse(1,1)
        S12=sp.FrequencyResponse(1,2)
        ra=[(s11*s11+1-s12*s12)/(2*s11) for (s11,s12) in zip(S11.Response(),S12.Response())]
        rb=[cmath.sqrt(s11*s11*s11*s11-2*s11*s11-2*s11*s11*s12*s12+1-2*s12*s12+s12*s12*s12*s12)/(2*s11) for (s11,s12) in zip(S11.Response(),S12.Response())]
        rho=[ra-rb for (ra,rb) in zip(ra,rb)]
        la=[(r*r-1)/(2*s12*r*r) for (r,s12) in zip(rho,S12.Response())]
        lb=[cmath.sqrt(1-2*r*r+r*r*r*r+4*s12*s12*r*r)/(2*s12*r*r)  for (r,s12) in zip(rho,S12.Response())]
        Ls=[la+lb for (la,lb) in zip(la,lb)]
        Zc=[-Z0*(r+1)/(r-1) for r in rho]
        gamma=[-(cmath.log(l*cmath.exp(1j*2*math.pi*f*Tdest))-1j*2*math.pi*f*Tdest) for (l,f) in zip(Ls,fList)]
        Y=[g/zc for (g,zc) in zip(gamma,Zc)]
        Z=[g*zc for (g,zc) in zip(gamma,Zc)]
        Rr=[z.real for z in Z]
        L=[z.imag/(2.*math.pi*f) for (z,f) in zip(Z,fList)]
        Gr=[y.real for y in Y]
        C=[y.imag/(2.*math.pi*f) for (y,f) in zip(Y,fList)]
        import matplotlib.pyplot as plt
        plt.clf()
        plt.title('s-parameter compare')
        plt.xlabel('frequency (GHz)')
        plt.ylabel('amplitude')
        plt.semilogy([f/1e9 for f in fList],C,label='C')
        plt.semilogy([f/1e9 for f in fList],L,label='L')
        plt.semilogy([f/1e9 for f in fList],Rr,label='R')
        plt.semilogy([f/1e9 for f in fList],Gr,label='G')
        plt.legend(loc='upper right')
        plt.grid(True)
        plt.show()
        (Rx,Rsex,Lx)=(matrix([[1.,math.sqrt(f),1j*2*math.pi*f] for f in fList]).getI()*matrix([[z] for z in Z])).tolist()
        print(Rx[0].real,Rsex[0].real,Lx[0].real)
    def testRLGCExtract(self):
        return
        sp=si.sp.SParameterFile('cableForRLGC.s2p')
        Z0=50
        Tdest=2.24e-9
        fList=sp.m_f[1:]
        S11=sp.Response(1,1)[1:]
        S12=sp.Response(1,2)[1:]
        ra=[(s11*s11+1-s12*s12)/(2*s11) for (s11,s12) in zip(S11,S12)]
        rb=[cmath.sqrt(s11*s11*s11*s11-2*s11*s11-2*s11*s11*s12*s12+1-2*s12*s12+s12*s12*s12*s12)/(2*s11) for (s11,s12) in zip(S11,S12)]
        rho=[ra-rb for (ra,rb) in zip(ra,rb)]
        la=[(r*r-1)/(2*s12*r*r) for (r,s12) in zip(rho,S12)]
        lb=[cmath.sqrt(1-2*r*r+r*r*r*r+4*s12*s12*r*r)/(2*s12*r*r)  for (r,s12) in zip(rho,S12)]
        Ls=[la+lb for (la,lb) in zip(la,lb)]
        Zc=[-Z0*(r+1)/(r-1) for r in rho]
        gamma=[-(cmath.log(l*cmath.exp(1j*2*math.pi*f*Tdest))-1j*2*math.pi*f*Tdest) for (l,f) in zip(Ls,fList)]
        Y=[g/zc for (g,zc) in zip(gamma,Zc)]
        Z=[g*zc for (g,zc) in zip(gamma,Zc)]
        Rr=[abs(z.real) for z in Z]
        L=[z.imag/(2.*math.pi*f) for (z,f) in zip(Z,fList)]
        Gr=[abs(y.real) for y in Y]
        C=[y.imag/(2.*math.pi*f) for (y,f) in zip(Y,fList)]
        print Zc
        import matplotlib.pyplot as plt
        plt.clf()
        plt.title('s-parameter compare')
        plt.xlabel('frequency (GHz)')
        plt.ylabel('amplitude')
        plt.semilogy([f/1e9 for f in fList],C,label='C')
        plt.semilogy([f/1e9 for f in fList],L,label='L')
        plt.semilogy([f/1e9 for f in fList],Rr,label='R')
        plt.semilogy([f/1e9 for f in fList],Gr,label='G')
        plt.legend(loc='upper right')
        plt.grid(True)
        plt.show()
        (Rx,Rsex,Lx)=(matrix([[1.,math.sqrt(f),1j*2*math.pi*f] for f in fList]).getI()*matrix([[z] for z in Z])).tolist()
        print(Rx[0].real,Rsex[0].real,Lx[0].real)
    def testWriteRLGCfFCode(self):
        fileName="../SignalIntegrity/Fit/RLGC.py"
        className='RLGCFitter'
        defName=['__init__','fF']
        self.WriteClassCode(fileName,className,defName)
    def testWriteRLGCfJCode(self):
        fileName="../SignalIntegrity/Fit/RLGC.py"
        className='RLGCFitter'
        defName=['fJ']
        self.WriteClassCode(fileName,className,defName)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()