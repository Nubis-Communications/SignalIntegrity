#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Peter.Pupalaikis
#
# Created:     18/04/2016
# Copyright:   (c) Peter.Pupalaikis 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------



import unittest
import SignalIntegrity as si
import math
import os
from TestHelpers import SParameterCompareHelper
from TestHelpers import SourcesTesterHelper

class TestPI(unittest.TestCase,SParameterCompareHelper,SourcesTesterHelper):
    def testRLCOnePort(self):
        # one port impedance calculation based on s11
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        DecadeStart=1
        Decades=7
        K=100
        f=[pow(10.,float(k)/K*Decades+DecadeStart) for k in range(K)]
        Z0=50
        R=0.004
        L=5.4e-9
        C=810e-6
        sspp=si.p.SystemSParametersNumericParser(f).AddLines([
            'device R1 2 R '+str(R),
            'device L1 2 L '+str(L),
            'device C1 2 C '+str(C),
            'device G1 1 ground',
            'port 1 R1 1',
            'connect R1 2 L1 1',
            'connect C1 1 L1 2',
            'connect G1 1 C1 2'
        ])
        sp=sspp.SParameters()

        plot=False
        if plot:
            import matplotlib.pyplot as plt
            S11=sp.Response(1,1)
            y=[20*math.log10(abs(s11)) for s11 in S11]
            plt.subplot(1,1,1)
            plt.plot(f,y)
            plt.show()
            plt.cla()

            S11=sp.Response(1,1)
            y=[20*math.log10(abs(s11)) for s11 in S11]
            plt.subplot(1,1,1)
            plt.xscale('log')
            plt.plot(f,y)
            plt.show()
            plt.cla()

            y=[abs(Z0*(1+s11)/(1-s11)) for s11 in S11]
            plt.subplot(1,1,1)
            plt.xscale('log')
            plt.yscale('log')
            plt.plot(f,y)
            plt.show()
            plt.cla()

        S=[1j*2.*math.pi*fr for fr in f]
        self.assertTrue(self.SParametersAreEqual(
            si.sp.SParameters(f,[[[R+L*s+1./(C*s)]] for s in S]),
            si.sp.SParameters(f,[[[Z0*(1+s11)/(1-s11)]] for s11 in sp.Response(1,1)]),
            1e-9),
            'one port impedance measurement method incorrect')

    def testRLCTwoPort(self):
        # two port shunt impedance calculation based on s21
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        DecadeStart=1
        Decades=7
        K=100
        f=[pow(10.,float(k)/K*Decades+DecadeStart) for k in range(K)]
        Z0=50.
        R=0.004
        L=5.4e-9
        C=810e-6
        sspp=si.p.SystemSParametersNumericParser(f).AddLines([
            'device R1 2 R '+str(R),
            'device L1 2 L '+str(L),
            'device C1 2 C '+str(C),
            'device G1 1 ground',
            'port 2 R1 1',
            'port 1 R1 1',
            'connect R1 2 L1 1',
            'connect C1 1 L1 2',
            'connect G1 1 C1 2'
            ])
        sp=sspp.SParameters()
        S21=sp.Response(2,1)

        plot=False
        if plot:
            import matplotlib.pyplot as plt

            y=[20*math.log10(abs(s21)) for s21 in S21]
            plt.subplot(1,1,1)
            plt.plot(f,y)
            plt.show()
            plt.cla()

            y=[20*math.log10(abs(s21)) for s21 in S21]
            plt.subplot(1,1,1)
            plt.xscale('log')
            plt.plot(f,y)
            plt.show()
            plt.cla()

            y=[abs(Z0/2.*(s21)/(1-s21)) for s21 in S21]
            plt.subplot(1,1,1)
            plt.xscale('log')
            plt.yscale('log')
            plt.plot(f,y)
            plt.show()
            plt.cla()

        S=[1j*2.*math.pi*fr for fr in f]
        self.assertTrue(self.SParametersAreEqual(
            si.sp.SParameters(f,[[[R+L*s+1./(C*s)]] for s in S]),
            si.sp.SParameters(f,[[[Z0/2.*(s21)/(1-s21)]] for s21 in sp.Response(2,1)]),
            1e-9),
            'two port impedance measurement method incorrect')

    def testSymbolicParasiticR(self):
        sdp=si.p.SystemDescriptionParser().AddLines([
            'device R1 2',
            'device R2 2',
            'device R3 1',
            'port 1 R1 1',
            'port 2 R2 1',
            'connect R2 2 R1 2 R3 1'
            ])
        sd=sdp.SystemDescription()
        sd.AssignSParameters('R1',si.sy.SeriesZ('Zp'))
        sd.AssignSParameters('R2',si.sy.SeriesZ('Zp'))
        sd.AssignSParameters('R3',si.sy.ShuntZ(1,'Zd'))
        ssps=si.sd.SystemSParametersSymbolic(sd)
        #ssps.DocStart()
        ssps.LaTeXSolution(size='big')
        #ssps.DocEnd()
        ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,self.id()+' incorrect')
    def testNumericTwoPortParasiticCase0(self):
        # prove that if all parasitics are zero, that the S21 method provides
        # the exact answer for R
        Z0=50.
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sdp=si.p.SystemDescriptionParser().AddLines([
            'device Rp1 2',
            'device Rp2 2',
            'device R 2',
            'device Rb1 2',
            'device Rb2 2',
            'device G1 1 ground',
            'device G2 1 ground',
            'port 1 Rp1 1',
            'port 2 Rp2 1',
            'connect Rp2 2 Rp1 2 R 1',
            'connect Rb1 2 Rb2 2 R 2',
            'connect G1 1 Rb1 1',
            'connect G2 1 Rb2 1'
            ])
        sd=sdp.SystemDescription()
        Rp=1e-9
        Rb=1e-8
        R=.001
        sd.AssignSParameters('Rp1',si.dev.SeriesZ(Rp))
        sd.AssignSParameters('Rp2',si.dev.SeriesZ(Rp))
        sd.AssignSParameters('Rb1',si.dev.SeriesZ(Rb))
        sd.AssignSParameters('Rb2',si.dev.SeriesZ(Rb))
        sd.AssignSParameters('R',si.dev.SeriesZ(R))
        sspn=si.sd.SystemSParametersNumeric(sd)
        spm=sspn.SParameters()
        s21=spm[1][0]
        Rcalc=Z0/2.*(s21)/(1-s21)
        self.assertAlmostEqual(R,Rcalc,None,'resistance incorrect')

    def testNumericTwoPortParasiticCase1(self):
        # prove that if Rb nonzero, that the S21 method provides
        # R = R + Rb/2
        Z0=50.
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sdp=si.p.SystemDescriptionParser().AddLines([
            'device Rp1 2',
            'device Rp2 2',
            'device R 2',
            'device Rb1 2',
            'device Rb2 2',
            'device G1 1 ground',
            'device G2 1 ground',
            'port 1 Rp1 1',
            'port 2 Rp2 1',
            'connect Rp2 2 Rp1 2 R 1',
            'connect Rb1 2 Rb2 2 R 2',
            'connect G1 1 Rb1 1',
            'connect G2 1 Rb2 1'
            ])
        sd=sdp.SystemDescription()
        Rp=1e-9
        Rb=.001
        R=.001
        sd.AssignSParameters('Rp1',si.dev.SeriesZ(Rp))
        sd.AssignSParameters('Rp2',si.dev.SeriesZ(Rp))
        sd.AssignSParameters('Rb1',si.dev.SeriesZ(Rb))
        sd.AssignSParameters('Rb2',si.dev.SeriesZ(Rb))
        sd.AssignSParameters('R',si.dev.SeriesZ(R))
        sspn=si.sd.SystemSParametersNumeric(sd)
        spm=sspn.SParameters()
        s21=spm[1][0]
        Rcalc=Z0/2.*(s21)/(1-s21)
        self.assertAlmostEqual(R+Rb/2,Rcalc,None,'resistance incorrect')

    def testNumericTwoPortParasiticCase2(self):
        # prove that if Rb and Rp nonzero, that the S21 method provides
        # R = R + Rb/2
        Z0=50.
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sdp=si.p.SystemDescriptionParser().AddLines([
            'device Rp1 2',
            'device Rp2 2',
            'device R 2',
            'device Rb1 2',
            'device Rb2 2',
            'device G1 1 ground',
            'device G2 1 ground',
            'port 1 Rp1 1',
            'port 2 Rp2 1',
            'connect Rp2 2 Rp1 2 R 1',
            'connect Rb1 2 Rb2 2 R 2',
            'connect G1 1 Rb1 1',
            'connect G2 1 Rb2 1'
            ])
        sd=sdp.SystemDescription()
        Rp=.001
        Rb=.001
        R=.001
        sd.AssignSParameters('Rp1',si.dev.SeriesZ(Rp))
        sd.AssignSParameters('Rp2',si.dev.SeriesZ(Rp))
        sd.AssignSParameters('Rb1',si.dev.SeriesZ(Rb))
        sd.AssignSParameters('Rb2',si.dev.SeriesZ(Rb))
        sd.AssignSParameters('R',si.dev.SeriesZ(R))
        sspn=si.sd.SystemSParametersNumeric(sd)
        spm=sspn.SParameters()
        s21=spm[1][0]
        Rcalc=Z0/2.*(s21)/(1-s21)
        self.assertAlmostEqual(R+Rb/2,Rcalc,6,'resistance incorrect')

    def testNumericTwoPortParasiticCase3(self):
        # prove that if Rp nonzero, that the S21 method provides
        # provides almost exact measurement of R
        Z0=50.
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sdp=si.p.SystemDescriptionParser().AddLines([
            'device Rp1 2',
            'device Rp2 2',
            'device R 2',
            'device Rb1 2',
            'device Rb2 2',
            'device G1 1 ground',
            'device G2 1 ground',
            'port 1 Rp1 1',
            'port 2 Rp2 1',
            'connect Rp2 2 Rp1 2 R 1',
            'connect Rb1 2 Rb2 2 R 2',
            'connect G1 1 Rb1 1',
            'connect G2 1 Rb2 1'
            ])
        sd=sdp.SystemDescription()
        Rp=.001
        Rb=1e-8
        R=.001
        sd.AssignSParameters('Rp1',si.dev.SeriesZ(Rp))
        sd.AssignSParameters('Rp2',si.dev.SeriesZ(Rp))
        sd.AssignSParameters('Rb1',si.dev.SeriesZ(Rb))
        sd.AssignSParameters('Rb2',si.dev.SeriesZ(Rb))
        sd.AssignSParameters('R',si.dev.SeriesZ(R))
        sspn=si.sd.SystemSParametersNumeric(sd)
        spm=sspn.SParameters()
        s21=spm[1][0]
        Rcalc=Z0/2.*(s21)/(1-s21)
        self.assertAlmostEqual(R,Rcalc,6,'resistance incorrect')

    def testSymbolicParasiticRFourPort(self):
        sdp=si.p.SystemDescriptionParser().AddLines([
            'device Rp1 2',
            'device Rp2 2',
            'device R 2',
            'device Rb1 2',
            'device Rb2 2',
            'device MM1 4 mixedmode',
            'device MM2 4 mixedmode',
            'port 1 MM2 3',
            'port 2 MM1 3',
            'connect Rp1 1 MM2 1',
            'connect Rp2 2 Rp1 2 R 1',
            'connect Rp2 1 MM1 1',
            'connect Rb1 2 Rb2 2 R 2',
            'connect MM2 2 Rb1 1',
            'connect Rb2 1 MM1 2',
            'port 4 MM1 4',
            'port 3 MM2 4'
            ])
        sd=sdp.SystemDescription()
        sd.AssignSParameters('Rp1',si.sy.SeriesZ('Zp'))
        sd.AssignSParameters('Rp2',si.sy.SeriesZ('Zp'))
        sd.AssignSParameters('Rb1',si.sy.SeriesZ('Zb'))
        sd.AssignSParameters('Rb2',si.sy.SeriesZ('Zb'))
        sd.AssignSParameters('R',si.sy.SeriesZ('Z'))
        ssps=si.sd.SystemSParametersSymbolic(sd)
        #ssps.DocStart()
        ssps.LaTeXSolution(size='big')
        #ssps.DocEnd()
        ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,self.id()+' incorrect')

    def testSymbolicParasiticRFourPortWithShunt(self):
        sdp=si.p.SystemDescriptionParser().AddLines([
            'device Rp1 2',
            'device Rp2 2',
            'device R 4',
            'device Rb1 2',
            'device Rb2 2',
            'device MM1 4 mixedmode',
            'device MM2 4 mixedmode',
            'port 1 MM2 3',
            'port 2 MM1 3',
            'port 4 MM1 4',
            'port 3 MM2 4',
            'connect Rp1 1 MM2 1',
            'connect Rp2 1 MM1 1',
            'connect Rb1 1 MM2 2',
            'connect Rb2 1 MM1 2',
            'connect Rp1 2 R 1',
            'connect Rp2 2 R 3',
            'connect Rb1 2 R 2',
            'connect Rb2 2 R 4'
            ])
        sd=sdp.SystemDescription()
        sd.AssignSParameters('Rp1',si.sy.SeriesZ('Zp'))
        sd.AssignSParameters('Rp2',si.sy.SeriesZ('Zp'))
        sd.AssignSParameters('Rb1',si.sy.SeriesZ('Zb'))
        sd.AssignSParameters('Rb2',si.sy.SeriesZ('Zb'))
        sd.AssignSParameters('R',si.sy.ShuntZ(4,'Z'))
        ssps=si.sd.SystemSParametersSymbolic(sd)
        #ssps.DocStart()
        ssps.LaTeXSolution(size='big')
        #ssps.DocEnd()
        ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,self.id()+' incorrect')

    def testSymbolicParasiticRFourPortWithShunt2(self):
        sdp=si.p.SystemDescriptionParser().AddLines([
            'device Rp1 2',
            'device Rp2 2',
            'device R 4',
            'device Rb1 2',
            'device Rb2 2',
            'device MM1 4 mixedmode',
            'device MM2 4 mixedmode',
            'port 1 MM2 3',
            'port 2 MM1 3',
            'port 4 MM1 4',
            'port 3 MM2 4',
            'connect Rp1 1 MM2 1',
            'connect Rp2 1 MM1 1',
            'connect Rb1 1 MM2 2',
            'connect Rb2 1 MM1 2',
            'connect Rp1 2 R 1',
            'connect Rp2 2 R 3',
            'connect Rb1 2 R 2',
            'connect Rb2 2 R 4'
            ])
        sd=sdp.SystemDescription()
        sd.AssignSParameters('Rp1',[['P1','P2'],['P2','P1']])
        sd.AssignSParameters('Rp2',[['P1','P2'],['P2','P1']])
        sd.AssignSParameters('Rb1',[['B1','B2'],['B2','B1']])
        sd.AssignSParameters('Rb2',[['B1','B2'],['B2','B1']])
        sd.AssignSParameters('R',[['Z1','-Z1','Z2','-Z1'],['-Z1','Z1','-Z1','Z2'],
            ['Z2','-Z1','Z1','-Z1'],['-Z1','Z2','-Z1','Z1']])
        ssps=si.sd.SystemSParametersSymbolic(sd,size='small')
        ssps.DocStart()
        ssps._AddEq('P1='+si.sy.SeriesZ('Zp')[0][0])
        ssps._AddEq('P2='+si.sy.SeriesZ('Zp')[0][1])
        ssps._AddEq('B1='+si.sy.SeriesZ('Zb')[0][0])
        ssps._AddEq('B2='+si.sy.SeriesZ('Zb')[0][1])
        ssps._AddEq('Z1='+si.sy.ShuntZ(4,'Z')[0][0])
        ssps._AddEq('Z2='+si.sy.ShuntZ(4,'Z')[0][2])
        ssps=si.sd.SystemSParametersSymbolic(sd)
        #ssps.DocStart()
        ssps.LaTeXSolution(size='big')
        #ssps.DocEnd()
        ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,self.id()+' incorrect')

    def testSymbolicParasiticRFourPortWithShunt3(self):
        sdp=si.p.SystemDescriptionParser().AddLines([
            'device Rp1 2',
            'device Rp2 2',
            'device R 4',
            'device Rb1 2',
            'device Rb2 2',
            'device MM1 4 mixedmode',
            'device MM2 4 mixedmode',
            'port 1 MM2 3',
            'port 2 MM1 3',
            'port 4 MM1 4',
            'port 3 MM2 4',
            'connect Rp1 1 MM2 1',
            'connect Rp2 1 MM1 1',
            'connect Rb1 1 MM2 2',
            'connect Rb2 1 MM1 2',
            'connect Rp1 2 R 1',
            'connect Rp2 2 R 3',
            'connect Rb1 2 R 2',
            'connect Rb2 2 R 4'
            ])
        sd=sdp.SystemDescription()
        sd.AssignSParameters('Rp1',[['PL1','PL2'],['PL2','PL1']])
        sd.AssignSParameters('Rp2',[['PR1','PR2'],['PR2','PR1']])
        sd.AssignSParameters('Rb1',[['BL1','BL2'],['BL2','BL1']])
        sd.AssignSParameters('Rb2',[['BR1','BR2'],['BR2','BR1']])
        sd.AssignSParameters('R',[['Z1','-Z1','Z2','-Z1'],['-Z1','Z1','-Z1','Z2'],
            ['Z2','-Z1','Z1','-Z1'],['-Z1','Z2','-Z1','Z1']])
        ssps=si.sd.SystemSParametersSymbolic(sd,size='small')
        #ssps.DocStart()
        ssps._AddEq('PL1='+si.sy.SeriesZ('Zpl')[0][0])
        ssps._AddEq('PL2='+si.sy.SeriesZ('Zpl')[0][1])
        ssps._AddEq('PR1='+si.sy.SeriesZ('Zpr')[0][0])
        ssps._AddEq('PR2='+si.sy.SeriesZ('Zpr')[0][1])
        ssps._AddEq('BL1='+si.sy.SeriesZ('Zbl')[0][0])
        ssps._AddEq('BL2='+si.sy.SeriesZ('Zbl')[0][1])
        ssps._AddEq('BR1='+si.sy.SeriesZ('Zbr')[0][0])
        ssps._AddEq('BR2='+si.sy.SeriesZ('Zbr')[0][1])
        ssps._AddEq('Z1='+si.sy.ShuntZ(4,'Z')[0][0])
        ssps._AddEq('Z2='+si.sy.ShuntZ(4,'Z')[0][2])
        ssps.LaTeXSolution(size='big')
        #ssps.DocEnd()
        ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,self.id()+' incorrect')

    def testNumericParasiticRFourPortWithShunt(self):
        sdp=si.p.SystemDescriptionParser().AddLines([
            'device Rp1 2',
            'device Rp2 2',
            'device R 4',
            'device Rb1 2',
            'device Rb2 2',
            'device MM1 4 mixedmode',
            'device MM2 4 mixedmode',
            'port 1 MM2 3',
            'port 2 MM1 3',
            'port 4 MM1 4',
            'port 3 MM2 4',
            'connect Rp1 1 MM2 1',
            'connect Rp2 1 MM1 1',
            'connect Rb1 1 MM2 2',
            'connect Rb2 1 MM1 2',
            'connect Rp1 2 R 1',
            'connect Rp2 2 R 3',
            'connect Rb1 2 R 2',
            'connect Rb2 2 R 4'
            ])
        sd=sdp.SystemDescription()
        Rp1=0.095590
        Rp2=0.053934
        Rb1=0.046207
        Rb2=0.086222
        R=0.1
        Z0=50.
        sd.AssignSParameters('Rp1',si.dev.SeriesZ(Rp1))
        sd.AssignSParameters('Rp2',si.dev.SeriesZ(Rp2))
        sd.AssignSParameters('Rb1',si.dev.SeriesZ(Rb1))
        sd.AssignSParameters('Rb2',si.dev.SeriesZ(Rb2))
        sd.AssignSParameters('R',si.dev.ShuntZ(4,R))
        sspn=si.sd.SystemSParametersNumeric(sd)
        spm=sspn.SParameters()
        sdd21=spm[1][0]
        Rcalc=Z0*(sdd21)/(1-sdd21)
        # good to three decimal places
        self.assertAlmostEqual(R,Rcalc,3,'resistance incorrect')
        EstimatedError=-1./4*(2*Rp1+2*Rp2+2*Rb1+2*Rb2)*R/Z0
        EstimatedErrorSmallerTerm=-1./4*(Rb1*Rp2-Rp1*Rp2-Rb1*Rb2+Rb2*Rp1)/Z0
        # good to three decimal places
        self.assertAlmostEqual(Rcalc-R,EstimatedError+EstimatedErrorSmallerTerm,6,'estimated error incorrect')
        # check bracketing of error
        maxp=max(Rp1,Rp2,Rb1,Rb2)
        maxEstimatedError=-2./Z0*maxp*R
        self.assertTrue(maxEstimatedError<EstimatedError+EstimatedErrorSmallerTerm,'max esimated error incorrect')
        # check error bounds
        # parasitics always cause lower calculation, so check that calculation is indeed lower
        # but not lower than predicted by error.
        # i.e.       R+maxError < Rcalc < R (remember, max error is negative)
        self.assertTrue(Rcalc<R,'calculated R not less than actual R')
        self.assertTrue(R+maxEstimatedError<Rcalc,'calculated error bounds incorrect')
if __name__ == '__main__':
    unittest.main()
