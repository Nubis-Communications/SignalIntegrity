import unittest

import SignalIntegrity as si
import math
import os
from TestHelpers import *

class TestTline(unittest.TestCase,ResponseTesterHelper):
    def testTline(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=[(n+1)*20e6 for n in range(100)]
        #SParametersAproximateTLineModel(f,Rsp,Lsp,Csp,Gsp,Rsm,Lsm,Csm,Gsm,Lm,Cm,Gm,Z0,K)
        SP=si.dev.ApproximateFourPortTLine(
            f,
                10.,5.85e-8,2e-11,0.01,
                10.,5.85e-8,2e-11,0.01,
                1.35e-8,1.111e-12,1e-30,50,100)
        sf=si.sp.SParameters(f,SP)
        fileName='_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile(fileName)
            self.assertTrue(False,fileName + 'does not exist')
        regression = si.sp.File(fileName)
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.id()+'result not same')
        import matplotlib.pyplot as plt
##        for r in range(4):
##            for c in range(4):
##                y=[20*math.log(abs(SP[n][r][c]),10) for n in range(len(f))]
##                plt.subplot(4,4,r*4+c+1)
##                plt.plot(f,y)
##        plt.show()
    def FourPortTLineModel(self,f,Zo,TDo,Ze,TDe):
        sspp=si.p.SystemSParametersNumericParser(f)
        sspp.AddLines(['device D1 4 tline zc 50. td 1.e-9',
            'device D2 4 tline zc 50. td 1.e-9',
            'device D3 4 tline zc -25. td 1.e-9',
            'device D4 4 tline zc 25. td 1.e-9',
            'device G 1 ground',
            'port 1 D1 1',
            'port 2 D1 2',
            'port 3 D2 3',
            'port 4 D2 4',
            'connect D1 3 D2 1',
            'connect D1 4 D2 2',
            'connect D1 3 D3 1',
            'connect D1 4 D3 2',
            'connect D3 3 D4 1',
            'connect D3 4 D4 2',
            'connect D4 3 G 1',
            'connect D4 4 G 1'
            ])
        return sspp.SParameters()
    def testTline2(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=[(n+1)*20e6 for n in range(100)]
        #SParametersAproximateTLineModel(f,Rsp,Lsp,Csp,Gsp,Rsm,Lsm,Csm,Gsm,Lm,Cm,Gm,Z0,K)
        SP=si.dev.ApproximateFourPortTLine(
            f,
                0.00001,5.85e-8,2e-11,0.00001,
                0.00001,5.85e-8,2e-11,0.00001,
                1.35e-8,1.111e-12,0.00001,50,1000)
        sf=si.sp.SParameters(f,SP)
        #sf=self.FourPortTLineModel(f,50.,1.e-9,50.,1.e-9)
        #sf=si.sp.SParameters(f,[si.p.dev.Tlinef(f,4,50.,1.e-9).SParameters(n) for n in range(len(f))])
        fileName='_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile(fileName)
            self.assertTrue(False,fileName + 'does not exist')
        regression = si.sp.File(fileName)
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.id()+'result not same')
        """
        import matplotlib.pyplot as plt
        for r in range(4):
            for c in range(4):
                y=[20*math.log(abs(sf[n][r][c]+0.001),10) for n in range(len(f))]
                plt.subplot(4,4,r*4+c+1)
                plt.plot(f,y)
        plt.show()
        """
    def testTline3(self):
        """
        this test checks that a four port transmission line approximated as 10,000
        sections of RLGC sections with 1/10,000th of the supplied series resistance
        and inductance, shunt capacitance and conductance, and mutual inductance and
        capacitance is the same the mixed mode model with the differential and common-mode
        impedance and propagation time corresponding to RLGC.

        it tests the old, obsolete four port model which is all lumped components.
        """
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=[(n+1)*200e6 for n in range(50)]
        #SParametersAproximateTLineModel(f,Rsp,Lsp,Csp,Gsp,Rsm,Lsm,Csm,Gsm,Lm,Cm,Gm,Z0,K)
        #differential 90 Ohm, 1 ns - common-mode 20 Ohm 1.2 ns
        Ls=58.5e-9
        Cs=20e-12
        Lm=13.5e-9
        Cm=1.11111111111e-12
        Zd=2.*math.sqrt((Ls-Lm)/(Cs+2.*Cm))
        Zc=0.5*math.sqrt((Ls+Lm)/Cs)
        Td=math.sqrt((Ls-Lm)*(Cs+2.*Cm))
        Tc=math.sqrt((Ls+Lm)*Cs)
        spmodel=si.sp.dev.ApproximateFourPortTLineOld(
            f,
                0.0,Ls,Cs,0.0,
                0.0,Ls,Cs,0.0,
                Lm,Cm,0.0,50.,10000)
        spmodel2=si.sp.dev.MixedModeTLine(f,Zd,Td,Zc,Tc)
        self.assertTrue(self.SParametersAreEqual(spmodel,spmodel2,0.005),self.id()+' result not same')
        """
        import matplotlib.pyplot as plt
        for r in range(4):
            for c in range(4):
                y=[20*math.log(abs(sf[n][r][c]+0.001),10) for n in range(len(f))]
                plt.subplot(4,4,r*4+c+1)
                plt.plot(f,y)
        plt.show()
        """
    def testTline4(self):
        """
        this test checks that a four port transmission line approximated as 10,000
        sections of RLGC sections with 1/10,000th of the supplied series resistance
        and inductance, shunt capacitance and conductance, and mutual inductance and
        capacitance is the same the mixed mode model with the differential and common-mode
        impedance and propagation time corresponding to RLGC.

        it tests the new four port approximate model which consists of two two-port approximate
        models with the mutual inductance, capacitance and inductance added to it.
        """
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=[(n+1)*200e6 for n in range(50)]
        #SParametersAproximateTLineModel(f,Rsp,Lsp,Csp,Gsp,Rsm,Lsm,Csm,Gsm,Lm,Cm,Gm,Z0,K)
        #differential 90 Ohm, 1 ns - common-mode 20 Ohm 1.2 ns
        Ls=58.5e-9
        Cs=20e-12
        Lm=13.5e-9
        Cm=1.11111111111e-12
        Zd=2.*math.sqrt((Ls-Lm)/(Cs+2.*Cm))
        Zc=0.5*math.sqrt((Ls+Lm)/Cs)
        Td=math.sqrt((Ls-Lm)*(Cs+2.*Cm))
        Tc=math.sqrt((Ls+Lm)*Cs)
        spmodel=si.sp.dev.ApproximateFourPortTLine(
            f,
                0.0,Ls,Cs,0.0,
                0.0,Ls,Cs,0.0,
                Lm,Cm,0.0,50.,10000)
        spmodel2=si.sp.dev.MixedModeTLine(f,Zd,Td,Zc,Tc)
        self.assertTrue(self.SParametersAreEqual(spmodel,spmodel2,0.005),self.id()+' result not same')
    def testTline5(self):
        """
        This test checks that the four port transmission line model is the same as
        the two port model connected with ideal transformers.
        The primary of the left most transformer is connected between ports 1 and 3
        The primary of the right most transformer is connected between ports 2 and 4
        the dotted secondary of the left most transformer is connected to the transmission line
        as is the dotted secondary of the right most transformer.
        the undotted secondary connections are to ground.
        """
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=[(n+1)*200e6 for n in range(50)]
        sspnp=si.p.SystemSParametersNumericParser(f)
        sspnp.AddLines(['device T1 4 idealtransformer 1','device T2 4 idealtransformer 1',
            'device TL 2 tline zc 50. td 1e-9','device G 1 ground',
            'port 1 T1 1 2 T2 1 3 T1 2 4 T2 2','connect T1 3 TL 1','connect T2 3 TL 2',
            'connect T1 4 G 1','connect T2 4 G 1'])
        spmodel=sspnp.SParameters()
        #fileNameBase = self.id().split('.')[2].replace('test','')
        #spFileName = fileNameBase +'_1.s4p'
        #self.CheckSParametersResult(spmodel,spFileName,' incorrect')
        spmodel2=si.sp.dev.TLine(f,4,50.,1e-9)
        #spFileName2 = fileNameBase +'_2.s4p'
        #self.CheckSParametersResult(spmodel2,spFileName2,' incorrect')
        self.assertTrue(self.SParametersAreEqual(spmodel,spmodel2,0.00001),self.id()+' result not same')
    def testTline6(self):
        """
        This test checks that the four port transmission line model is the same as
        the two port model connected with mixed mode converters.
        The + and - of the left most mixed mode converter is connected between ports 1 and 3
        The + and - of the right most transformer is connected between ports 2 and 4
        the differential mode output of the mixed mode converters are connected to the transmission line
        the common mode outputs of the mixed mode converters are connected to opens.
        the transmission line is half the impedance
        """
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=[(n+1)*200e6 for n in range(50)]
        sspnp=si.p.SystemSParametersNumericParser(f)
        sspnp.AddLines(['device M1 4 mixedmode','device M2 4 mixedmode',
            'device TL 2 tline zc 25. td 1e-9','device O1 1 open','device O2 1 open',
            'port 1 M1 1 2 M2 1 3 M1 2 4 M2 2','connect M1 3 TL 1','connect M2 3 TL 2',
            'connect M1 4 O1 1','connect M2 4 O2 1'])
        spmodel=sspnp.SParameters()
        #fileNameBase = self.id().split('.')[2].replace('test','')
        #spFileName = fileNameBase +'_1.s4p'
        #self.CheckSParametersResult(spmodel,spFileName,' incorrect')
        spmodel2=si.sp.dev.TLine(f,4,50.,1e-9)
        #spFileName2 = fileNameBase +'_2.s4p'
        #self.CheckSParametersResult(spmodel2,spFileName2,' incorrect')
        self.assertTrue(self.SParametersAreEqual(spmodel,spmodel2,0.00001),self.id()+' result not same')
    def testTline7(self):
        """
        this is the same test as testTline6 except it shows that it doesn't matter if the mixed mode
        converter is a voltage or power version.
        """
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=[(n+1)*200e6 for n in range(50)]
        sspnp=si.p.SystemSParametersNumericParser(f)
        sspnp.AddLines(['device M1 4 mixedmode voltage','device M2 4 mixedmode voltage',
            'device TL 2 tline zc 25. td 1e-9','device O1 1 open','device O2 1 open',
            'port 1 M1 1 2 M2 1 3 M1 2 4 M2 2','connect M1 3 TL 1','connect M2 3 TL 2',
            'connect M1 4 O1 1','connect M2 4 O2 1'])
        spmodel=sspnp.SParameters()
        #fileNameBase = self.id().split('.')[2].replace('test','')
        #spFileName = fileNameBase +'_1.s4p'
        #self.CheckSParametersResult(spmodel,spFileName,' incorrect')
        spmodel2=si.sp.dev.TLine(f,4,50.,1e-9)
        #spFileName2 = fileNameBase +'_2.s4p'
        #self.CheckSParametersResult(spmodel2,spFileName2,' incorrect')
        self.assertTrue(self.SParametersAreEqual(spmodel,spmodel2,0.00001),self.id()+' result not same')

if __name__ == '__main__':
    unittest.main()
