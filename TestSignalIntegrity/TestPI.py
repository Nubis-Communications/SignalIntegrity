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

from TestHelpers import ResponseTesterHelper
from TestHelpers import SourcesTesterHelper

class TestPI(unittest.TestCase,SourcesTesterHelper,ResponseTesterHelper):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        si.td.wf.Waveform.adaptionStrategy='SinX'
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

    def testTransientCurrent(self):
        fileNameBase= '_'.join(self.id().split('.')[-3:])
        snp=si.p.SimulatorNumericParser(si.fd.EvenlySpacedFrequencyList(5e6,10000)).AddLines([
            'device R1 1 R 5.0',
            'device D2 4 currentcontrolledvoltagesource 1.0',
            'device G2 1 ground',
            'device O2 1 open',
            'voltagesource VG1 1',
            'device L4 2 L 0.00022',
            'device C3 2 C 4.7e-06',
            'currentsource CG2 1',
            'output D2 2',
            'connect D2 2 CG2 1 R1 1',
            'connect C3 2 D2 1 L4 2',
            'connect G2 1 D2 3',
            'output D2 4',
            'connect D2 4 O2 1',
            'connect C3 1 L4 1 VG1 1'
            ])
        tm=snp.TransferMatrices()
        td=si.td.wf.TimeDescriptor(-2e-3,int(math.floor((5e-3 - -2e-3)*10e6)),10e6)
        VG1=si.td.wf.StepWaveform(td,5.,-2e-3)
        CG2=si.td.wf.PulseWaveform(td,-0.2,0.,.1e-6)
        si.td.wf.Waveform.adaptionStrategy='SinX'
        tmp=si.td.f.TransferMatricesProcessor(tm)
        [Vout,Iout]=tmp.ProcessWaveforms([VG1,CG2])
        VinMinusVout=si.td.wf.Waveform(Vout.TimeDescriptor(),[5.-v for v in Vout.Values()])
        self.CheckWaveformResult(Iout,'Waveform_'+fileNameBase+'_Iout.txt','current')
        self.CheckWaveformResult(Vout,'Waveform_'+fileNameBase+'_Vout.txt','voltage')
        Voutfd=Vout.FrequencyContent()
        Ioutfd=Iout.FrequencyContent()
        VinMinusVoutfd=VinMinusVout.FrequencyContent()

        plot=False
        if plot:
            import matplotlib.pyplot as plt
            voy=Voutfd.Content('dB')
            ioy=Ioutfd.Content('dB')
            vivoy=VinMinusVoutfd.Content('dB')
            vof=Voutfd.Frequencies('MHz')
            iof=Ioutfd.Frequencies('MHz')
            vivof=VinMinusVoutfd.Frequencies('MHz')
            plt.subplot(1,1,1)
            plt.plot(vof,voy,label='Vout')
            plt.plot(iof,ioy,label='Iout')
            plt.plot(vivof,vivoy,label='Vin-Vout')
            plt.xscale('log')
            plt.show()
            plt.cla()

            zoy=[pow(10.,(voy[n]-ioy[n])/20.) for n in range(len(voy))]
            ziy=[pow(10.,(vivoy[n]-ioy[n])/20.) for n in range(len(voy))]
            zof=Voutfd.Frequencies()
            zif=VinMinusVoutfd.Frequencies()
            plt.subplot(1,1,1)
            plt.plot(zof,zoy,label='Zo')
            plt.plot(zif,ziy,label='Zo')
            plt.xscale('log')
            plt.yscale('log')
            plt.show()

        # make a complex impedance plot
        ZloadFrequencies=[]
        ZloadImpedance=[]
        ZsourceFrequencies=[]
        ZsourceImpedance=[]
        for n in range(len(Voutfd)):
            try:
                Zload=Voutfd.Content()[n]/Ioutfd.Content()[n]
                ZloadFrequencies.append(Voutfd.Frequencies()[n])
                ZloadImpedance.append(Zload)
                Zsource=VinMinusVoutfd.Content()[n]/Ioutfd.Content()[n]
                ZsourceFrequencies.append(Voutfd.Frequencies()[n])
                ZsourceImpedance.append(Zsource)
            except Exception as e:
                raise e
        Zloadfd=si.fd.FrequencyContent(si.fd.GenericFrequencyList(ZloadFrequencies),ZloadImpedance)
        Zsourcefd=si.fd.FrequencyContent(si.fd.GenericFrequencyList(ZsourceFrequencies),ZsourceImpedance)

        plot=False
        if plot:
            import matplotlib.pyplot as plt
            zsy=Zsourcefd.Content('mag')
            zly=Zloadfd.Content('mag')
            zsf=Zsourcefd.Frequencies()
            zlf=Zloadfd.Frequencies()
            plt.subplot(1,1,1)
            plt.plot(zsf,zsy,label='Zsource')
            plt.plot(zlf,zly,label='Zload')
            plt.xscale('log')
            plt.yscale('log')
            plt.show()

    def testVRM(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        si.td.wf.Waveform.adaptionStrategy='Linear'
        fileNameBase= '_'.join(self.id().split('.')[-3:])
        snp=si.p.SimulatorNumericParser(si.fd.EvenlySpacedFrequencyList(5e6,10000)).AddLines([
            'device L1 2 L 0.00022',
            'device C1 1 C 4.7e-06',
            'device R1 1 R 5.0',
            'device D1 4 currentcontrolledvoltagesource 1.0',
            'device G1 1 ground',
            'device O1 1 open',
            'device D2 4 currentcontrolledvoltagesource 1.0',
            'device G2 1 ground',
            'device O2 1 open',
            'device D3 4 voltagecontrolledvoltagesource 1.0',
            'device G3 1 ground',
            'device O3 1 open',
            'currentsource CG2 1',
            'voltagesource VS1 1',
            'device R2 2 R 1000000.0',
            'device C2 2 C 2.2e-09',
            'device D4 4 voltagecontrolledvoltagesource 10.0',
            'device G4 1 ground',
            'device O4 1 open',
            'device R3 2 R 0.1',
            'connect L1 1 D1 2',
            'connect L1 2 R3 1',
            'connect D2 1 D4 1 C2 2 R3 2 C1 1 D3 1',
            'output R1 1',
            'connect R1 1 D2 2 CG2 1',
            'output R2 1',
            'connect R2 1 VS1 1 D1 1 D3 2',
            'connect D1 3 G1 1',
            'output O1 1',
            'connect O1 1 D1 4',
            'connect D2 3 G2 1',
            'output O2 1',
            'connect O2 1 D2 4',
            'connect D3 3 G3 1',
            'output O3 1',
            'connect O3 1 D3 4',
            'connect D4 2 R2 2 C2 1',
            'connect D4 3 G4 1',
            'output O4 1',
            'connect O4 1 D4 4'
        ])
        tm=snp.TransferMatrices()
        self.CheckSParametersResult(tm.SParameters(),fileNameBase+'_TransferMatrices.s6p','transfer matrices')
        VS1=si.td.wf.Waveform().ReadFromFile('pw.txt')
        td=VS1.TimeDescriptor()
        CG2=si.td.wf.PulseWaveform(td,-0.2,1e-3,1e-3)
        tmp=si.td.f.TransferMatricesProcessor(tm)
        [Vout,Vin,Il,Iout,Vl,Vc]=tmp.ProcessWaveforms([CG2,VS1])
        si.td.wf.Waveform.adaptionStrategy='SinX'
        self.CheckWaveformResult(Vout,'Waveform_'+fileNameBase+'_Vout.txt','Vout')
        self.CheckWaveformResult(Vin,'Waveform_'+fileNameBase+'_Vin.txt','Vin')
        self.CheckWaveformResult(Il,'Waveform_'+fileNameBase+'_Il.txt','Il')
        self.CheckWaveformResult(Iout,'Waveform_'+fileNameBase+'_Iout.txt','Iout')
        self.CheckWaveformResult(Vl,'Waveform_'+fileNameBase+'_Vl.txt','Vl')
        self.CheckWaveformResult(Vc,'Waveform_'+fileNameBase+'_Vc.txt','Vc')
    def testVRMVPAlgorithm(self):
        from copy import copy
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileNameBase= '_'.join(self.id().split('.'))
        si.td.wf.Waveform.adaptionStrategy='Linear'
        Vin=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testVRM_Vin.txt')
        Vout=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testVRM_Vout.txt')
        Vlcalc=Vin-Vout
        Vl=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testVRM_Vl.txt')
        L=220e-6
        R=.1
        Il=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testVRM_Il.txt')
        il=copy(Vl.Values())
        vl=Vl.Values()
        il[0]=0.
        T=1./Vl.TimeDescriptor().Fs
        K=Vl.TimeDescriptor().N
        for k in range(1,K):
            il[k]=(vl[k]+L/T*il[k-1])/(L/T+R)
        Ilcalc=si.td.wf.Waveform(Vl.TimeDescriptor(),il)
        C=4.7e-6
        Ioutcalc=Il-Vout.Derivative()*C
        Iout=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testVRM_Iout.txt')
        [Vlcalc,Vl,Ilcalc,Il,Ioutcalc,Iout]=si.td.wf.AdaptedWaveforms([Vlcalc,Vl,Ilcalc,Il,Ioutcalc,Iout])
        si.td.wf.Waveform.adaptionStrategy='SinX'
        plot=False
        if plot:
            import matplotlib.pyplot as plt
            plt.subplot(1,1,1)
            plt.plot(Vlcalc.Times(),Vlcalc.Values(),label='Vlcalc')
            plt.plot(Vl.Times(),Vl.Values(),label='Vl')
            plt.legend(loc='upper right',labelspacing=0.1)
            plt.show()
            plt.cla()

            plt.plot(Ilcalc.Times(),Ilcalc.Values(),label='Ilcalc')
            plt.plot(Il.Times(),Il.Values(),label='Il')
            plt.legend(loc='upper right',labelspacing=0.1)
            plt.show()
            plt.cla()

            plt.plot(Ioutcalc.Times(),Ioutcalc.Values(),label='Ioutcalc')
            plt.plot(Iout.Times(),Iout.Values(),label='Iout')
            plt.legend(loc='upper right',labelspacing=0.1)
            plt.show()
            plt.cla()

    def testDeriv(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileNameBase= '_'.join(self.id().split('.'))
        derivFd=si.fd.Differentiator(si.fd.EvenlySpacedFrequencyList(5e6,10000))
        derivIr=derivFd.ImpulseResponse()
        integralIr=derivIr.Integral()
        plot=False
        if plot:
            import matplotlib.pyplot as plt
            plt.subplot(1,1,1)
            plt.plot(derivFd.Frequencies(),derivFd.Response('dB'),label='deriv')
            plt.legend(loc='upper right',labelspacing=0.1)
            plt.xscale('log')
            plt.show()
            plt.cla()

            plt.plot(derivIr.Times(),derivIr.Values(),label='deriv')
            plt.legend(loc='upper right',labelspacing=0.1)
            plt.show()
            plt.cla()

            plt.plot(integralIr.Times(),integralIr.Values(),label='integral')
            plt.legend(loc='upper right',labelspacing=0.1)
            plt.show()
            plt.cla()

    def testDerivIntegral(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileNameBase= '_'.join(self.id().split('.')[-3:])
        Vout=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testVRM_Vout.txt')
        Il=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testVRM_Il.txt')
        Iout=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testVRM_Iout.txt')
        C=4.7e-6
        VoutDC=Vout.Derivative()*C
        [Il,Iout,VoutDC]=si.td.wf.AdaptedWaveforms([Il,Iout,VoutDC])
        Ioutcalc=Il-VoutDC
        si.td.wf.Waveform.adaptionStrategy='SinX'
        self.CheckWaveformResult(Ioutcalc,'Waveform_'+fileNameBase+'_Ioutcalc.txt','Ioutcalc')
        Ioutcalc2=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testDerivIntegral_Ioutcalc.txt')
        IoutDiff=Ioutcalc-Ioutcalc2

        plot=False
        if plot:
            import matplotlib.pyplot as plt
            plt.subplot(1,1,1)
            plt.plot(Il.Times(),Il.Values(),label='Il')
            plt.plot(VoutDC.Times(),(VoutDC+0.98).Values(),label='VoutDC')
            plt.legend(loc='upper right',labelspacing=0.1)
            plt.show()
            plt.cla()


            plt.plot(Ioutcalc.Times(),Ioutcalc.Values(),label='Ioutcalc')
            plt.plot(Iout.Times(),Iout.Values(),label='Iout')
            plt.legend(loc='upper right',labelspacing=0.1)
            plt.show()
            plt.cla()

            plt.plot(IoutDiff.Times(),IoutDiff.Values(),label='IoutDiff')
            plt.legend(loc='upper right',labelspacing=0.1)
            plt.show()
            plt.cla()

    def testVRMParasitics(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileNameBase= '_'.join(self.id().split('.')[-3:])
        snp=si.p.SimulatorNumericParser(si.fd.EvenlySpacedFrequencyList(5e6,10000)).AddLines([
            'device L1 2 L 0.00022',
            'device C1 1 C 4.7e-06',
            'device R1 1 R 5.0',
            'device D1 4 currentcontrolledvoltagesource 1.0',
            'device G1 1 ground',
            'device O1 1 open',
            'device D2 4 currentcontrolledvoltagesource 1.0',
            'device G2 1 ground',
            'device O2 1 open',
            'device D3 4 voltagecontrolledvoltagesource 1.0',
            'device G3 1 ground',
            'device O3 1 open',
            'currentsource CG2 1',
            'voltagesource VS1 1',
            'device R3 2 R 0.1',
            'device R4 2 R 0.2',
            'device C3 1 C 1e-07',
            'device L2 2 L 1e-07',
            'device R2 2 R 0.2',
            'connect L1 1 D1 2',
            'connect L1 2 R3 1',
            'connect C1 1 L2 1',
            'connect R1 1 CG2 1 D2 2',
            'output R3 2',
            'connect R3 2 D2 1 D3 1 R2 2',
            'output D1 1',
            'connect D1 1 R4 2 C3 1 D3 2',
            'connect D1 3 G1 1',
            'output O1 1',
            'connect O1 1 D1 4',
            'connect D2 3 G2 1',
            'output O2 1',
            'connect O2 1 D2 4',
            'connect D3 3 G3 1',
            'output O3 1',
            'connect O3 1 D3 4',
            'connect VS1 1 R4 1',
            'connect L2 2 R2 1'
        ])
        tm=snp.TransferMatrices()
        self.CheckSParametersResult(tm.SParameters(),fileNameBase+'_TransferMatrices.s5p','transfer matrices')
        VS1=si.td.wf.Waveform().ReadFromFile('pw.txt')
        si.td.wf.Waveform.adaptionStrategy='Linear'
        td=VS1.TimeDescriptor()
        CG2=si.td.wf.PulseWaveform(td,-0.2,1e-3,1e-3)
        tmp=si.td.f.TransferMatricesProcessor(tm)
        [Vout,Vin,Il,Iout,Vl]=tmp.ProcessWaveforms([CG2,VS1])
        si.td.wf.Waveform.adaptionStrategy='SinX'
        self.CheckWaveformResult(Vout,'Waveform_'+fileNameBase+'_Vout.txt','Vout')
        self.CheckWaveformResult(Vin,'Waveform_'+fileNameBase+'_Vin.txt','Vin')
        self.CheckWaveformResult(Il,'Waveform_'+fileNameBase+'_Il.txt','Il')
        self.CheckWaveformResult(Iout,'Waveform_'+fileNameBase+'_Iout.txt','Iout')
        self.CheckWaveformResult(Vl,'Waveform_'+fileNameBase+'_Vl.txt','Vl')
        
    def testVRMComplicatedProcessing(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileNameBase= '_'.join(self.id().split('.'))
        Vout=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testVRMParasitics_Vout.txt')
        Vin=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testVRMParasitics_Vin.txt')
        Vlcalc=Vin-Vout
        K=Vlcalc.TimeDescriptor().N
        T=1./Vlcalc.TimeDescriptor().Fs
        L=220e-6
        R=.1
        C=4.7e-6
        Lc=100e-9
        Rc=200e-3
        
        A=T*T/(T*T+Lc*C+Rc*C*T)
        print A
        il=[0. for k in range(len(Vlcalc))]
        vl=Vlcalc.Values()
        il[0]=vl[0]*T/(L+R*T)
        for k in range(1,K):
            il[k]=vl[k]*T/(L+R*T)+il[k-1]*L/(L+R*T)
        Ilcalc=si.td.wf.Waveform(Vlcalc.TimeDescriptor(),il)
        iout=[0. for k in range(len(Ilcalc))]
        vout=Vout.Values()
        
        il=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testVRMParasitics_Il.txt').Values()
        
        ilz0=1.
        ilz1=-C*A*(2*Lc+Rc*T)/(T*T)
        ilz2=Lc*C*A/(T*T)
        voutz0=-C/T*A
        voutz1=C/T*A
        ioutz1=C*A*(2*Lc+Rc*T)/(T*T)
        ioutz2=-Lc*C*A/(T*T)

        iout[0]=il[0]*ilz0+vout[0]*voutz0
        iout[1]=il[1]*ilz0+il[0]*ilz1+vout[1]*voutz0+vout[0]*voutz1+iout[0]*ioutz1
        for k in range(2,K):
            iout[k]=il[k]*ilz0+il[k-1]*ilz1+il[k-2]*ilz2+vout[k]*voutz0+vout[k-1]*voutz1+iout[k-1]*ioutz1+iout[k-2]*ioutz2
        
        Ioutcalc=si.td.wf.Waveform(Vlcalc.TimeDescriptor(),iout)

        Il=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testVRMParasitics_Il.txt')
        Vl=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testVRMParasitics_Vl.txt')
        Iout=si.td.wf.Waveform().ReadFromFile('Waveform_TestPI_TestPI_testVRMParasitics_Iout.txt')
 
        plot=False
        if plot:
            import matplotlib.pyplot as plt
            plt.subplot(1,1,1)
            plt.plot(Ilcalc.Times(),Ilcalc.Values(),label='Ilcalc')
            plt.plot(Il.Times(),Il.Values(),label='Il')
            plt.legend(loc='upper right',labelspacing=0.1)
            plt.show()
            plt.cla()

            plt.plot(Ioutcalc.Times(),Ioutcalc.Values(),label='Ioutcalc')
            plt.plot(Iout.Times(),Iout.Values(),label='Iout')
            plt.legend(loc='upper right',labelspacing=0.1)
            plt.show()
            plt.cla()

    def testNoise(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileNameBase= '_'.join(self.id().split('.'))
        td=si.td.wf.TimeDescriptor(0.,10000,20e9)
        nwf=si.td.wf.NoiseWaveform(td,.1)
        plot=False
        if plot:
            import matplotlib.pyplot as plt
            plt.subplot(1,1,1)
            plt.plot(nwf.Times(),nwf.Values(),label='nwf')
            plt.legend(loc='upper right',labelspacing=0.1)
            plt.show()
            plt.cla()

if __name__ == '__main__':
    unittest.main()
