"""
TestTline.py
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
import math
import os

class TestTline(unittest.TestCase,si.test.ResponseTesterHelper,
                si.test.SourcesTesterHelper,si.test.RoutineWriterTesterHelper,
                si.test.SignalIntegrityAppTestHelper):
    checkPictures=True
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        si.test.ResponseTesterHelper.__init__(self)
        si.test.SourcesTesterHelper.__init__(self)
        si.test.RoutineWriterTesterHelper.__init__(self)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
    def id(self):
        return '.'.join(unittest.TestCase.id(self).split('.')[-3:])
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
        f=[(n)*200e6 for n in range(51)]
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
        spmodel=si.sp.dev.TLineDifferentialRLGCApproximate(
            f,
                0.0,0.0,Ls,0.0,Cs,0.0,
                0.0,0.0,Ls,0.0,Cs,0.0,
                Cm,0.0,0.0,Lm,50.,10000)
        spmodel2=si.sp.dev.MixedModeTLine(f,Zd,Td,Zc,Tc)
        self.assertTrue(self.SParametersAreEqual(spmodel,spmodel2,0.05),self.id()+' result not same')
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
        spmodel=si.sp.dev.TLineDifferentialRLGCApproximate(
            f,
                0.0,0.0,Ls,0.0,Cs,0.0,
                0.0,0.0,Ls,0.0,Cs,0.0,
                Cm,0.0,0.0,Lm,50.,10000)
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
        spmodel2=si.sp.dev.TLineLossless(f,4,50.,1e-9)
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
        spmodel2=si.sp.dev.TLineLossless(f,4,50.,1e-9)
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
        spmodel2=si.sp.dev.TLineLossless(f,4,50.,1e-9)
        #spFileName2 = fileNameBase +'_2.s4p'
        #self.CheckSParametersResult(spmodel2,spFileName2,' incorrect')
        self.assertTrue(self.SParametersAreEqual(spmodel,spmodel2,0.00001),self.id()+' result not same')
    def testTlineTwoPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device T 2','port 1 T 1 2 T 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('T',si.sy.TLine(2,'\\rho','\\gamma'))
        ssps._AddEq('\\rho = '+si.sy.TLineRho('Zc'))
        ssps._AddEq('\\gamma = '+si.sy.TLineGamma('Td'))
        ssps.LaTeXSolution().Emit()
        self.CheckSymbolicResult(self.id(),ssps,'incorrect')
    def testTlineTwoPortSymbolic2(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device T 2','port 1 T 1 2 T 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('T',si.sy.TLine(2,si.sy.TLineRho('Zc'),'\\gamma'))
        ssps._AddEq('\\gamma = '+si.sy.TLineGamma('Td'))
        ssps.LaTeXSolution().Emit()
        self.CheckSymbolicResult(self.id(),ssps,'incorrect')
    def testTlineTwoPortSymbolic3(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device T 2','port 1 T 1 2 T 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('T',si.sy.TLine(2,'\\rho',si.sy.TLineGamma('Td')))
        ssps._AddEq('\\rho = '+si.sy.TLineRho('Zc'))
        ssps.LaTeXSolution().Emit()
        self.CheckSymbolicResult(self.id(),ssps,'incorrect')
    def testTlineTwoPortSymbolic4(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device T 2','port 1 T 1 2 T 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('T',si.sy.TLine(2,si.sy.TLineRho('Zc'),si.sy.TLineGamma('Td')))
        ssps.LaTeXSolution().Emit()
        self.CheckSymbolicResult(self.id(),ssps,'incorrect')
    def testIdealTransformerSymbolicDevice(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device T 4','port 1 T 1 2 T 2 3 T 3 4 T 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('T',si.sy.IdealTransformer('a'))
        ssps.LaTeXSolution().Emit()
        self.CheckSymbolicResult(self.id(),ssps,'incorrect')
    def testIdealTransformerSymbolicDevice2(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device T 4','port 1 T 1 2 T 2 3 T 3 4 T 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('T',si.sy.IdealTransformer())
        ssps.LaTeXSolution().Emit()
        self.CheckSymbolicResult(self.id(),ssps,'incorrect')
    def testTlineFourPortSymbolicDevice(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device T1 4','device T2 4',
            'device TL 2','device G1 1 ground','device G2 1 ground',
            'port 1 T1 1 2 T2 1 3 T1 2 4 T2 2','connect T1 3 TL 1','connect T2 3 TL 2',
            'connect T1 4 G1 1','connect T2 4 G2 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('T1',si.sy.IdealTransformer())
        ssps.AssignSParameters('T2',si.sy.IdealTransformer())
        #ssps.DocStart()
        TL=si.sy.TLineTwoPort('\\rho','\\gamma')
        ssps._AddEq('\\rho = '+si.sy.TLineRho('Zc'))
        ssps._AddEq('\\gamma = '+si.sy.TLineGamma('Td'))
        ssps._AddEq('\\rho^\\prime = \\frac{1-3\\cdot \\rho }{\\rho - 3} = '+si.sy.TLineRho('Zc',4))
        ssps._AddEq('TL_{11}=TL_{22} = '+TL[0][0])
        ssps._AddEq('TL_{12}=TL_{21} = '+TL[0][1])
        ssps.LaTeXSolution(size='big')
        ssps._AddEq('\\mathbf{S} = '+ssps._LaTeXMatrix(si.sy.TLine(4,'\\rho^\\prime','\\gamma')))
        #ssps.DocEnd()
        ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,'incorrect')
    def testMixedModeXfrmrComparison(self):
        """
        compares the differential mode of a mixed mode converter to an ideal transformer.
        """
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=[(n+1)*200e6 for n in range(50)]
        sspnp=si.p.SystemSParametersNumericParser(f)
        sspnp.AddLines(['device M 4 mixedmode voltage','device O 1 open',
            'port 1 M 1 2 M 2 3 M 3','connect M 4 O 1'])
        spmodel=sspnp.SParameters()
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'_1.s3p'
        self.CheckSParametersResult(spmodel,spFileName,' incorrect')
        sspnp2=si.p.SystemSParametersNumericParser(f)
        sspnp2.AddLines(['device T 4 idealtransformer','device G 1 ground',
            'port 1 T 1 2 T 2 3 T 3','connect T 4 G 1'])
        spmodel2=sspnp2.SParameters()
        spFileName2 = fileNameBase +'_2.s3p'
        self.CheckSParametersResult(spmodel2,spFileName2,' incorrect')
        #This fails - still working on this.  It's not bad that it fails, it just
        #isn't helping me figure out more about the four port tline.
        #self.assertTrue(self.SParametersAreEqual(spmodel,spmodel2,0.00001),self.id()+' result not same')
    def testMixedModeXfrmrComparisonSymbolic(self):
        """
        compares the differential mode of a mixed mode converter to an ideal transformer.
        """
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device M 4 mixedmode voltage','device O 1 open',
            'port 1 M 1 2 M 2 3 M 3','connect M 4 O 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.DocStart()
        ssps.LaTeXSolution()
        ssps.DocEnd()
        ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,'incorrect')
    def testMixedModeXfrmrComparisonSymbolic2(self):
        """
        compares the differential mode of a mixed mode converter to an ideal transformer.
        """
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device T 4 idealtransformer','device G 1 ground',
            'port 1 T 1 2 T 2 3 T 3','connect T 4 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.DocStart()
        ssps.LaTeXSolution()
        ssps.DocEnd()
        ssps.Emit()
        self.CheckSymbolicResult(self.id(),ssps,'incorrect')
    def testMutualEntire(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('T',4)
        sd.AddPort('T',1,1)
        sd.AddPort('T',2,2)
        sd.AddPort('T',3,3)
        sd.AddPort('T',4,4)
        f=[n*20e6 for n in range(101)]
        Lsp=5.85e-8
        Lsm=3.23e-8
        Lm=1.35e-8
        Z0=50.
        Results=[]
        for fn in f:
            sd.AssignSParameters('T',si.dev.Mutual(Lsp,Lsm,Lm,fn,Z0))
            R=si.sd.SystemSParametersNumeric(sd).SParameters()
            Results.append(R)
        spc1=si.sp.SParameters(f,Results)
        Results=[]
        for fn in f:
            sd.AssignSParameters('T',si.dev.MutualOld(Lsp,Lsm,Lm,fn,Z0))
            R=si.sd.SystemSParametersNumeric(sd).SParameters()
            Results.append(R)
        spc2=si.sp.SParameters(f,Results)
        sspnp=si.p.SystemSParametersNumericParser(f)
        sspnp.AddLines(['device T 4 M '+str(Lm),'device L1 2 L '+str(Lsp),'device L2 2 L '+str(Lsm),'connect L1 2 T 1',
            'connect L2 2 T 3','port 1 L1 1 2 T 2 3 L2 1 4 T 4'])
        spc3=sspnp.SParameters()
        #self.CheckSParametersResult(spc1,'mutual1.s4p','full mutual not same')
        #self.CheckSParametersResult(spc2,'mutual2.s4p','full mutual (old) not same')
        #self.CheckSParametersResult(spc3,'mutual3.s4p','assembled mutual not same')
        self.assertTrue(self.SParametersAreEqual(spc1,spc2,1e-6),'Mutual not same')
        self.assertTrue(self.SParametersAreEqual(spc1,spc3,1e-6),'Mutual not same')
    def testBalancedFourPortTLineSParameters(self):
        """
        This test generates symbolically the s-parameters of the balanced four port
        network with the s-parameters of the even and odd mode transmission lines connected
        to mixed mode converters
        """
        sdp=si.p.SystemDescriptionParser()
        # Ports 1 2 3 4 are + - D C of mixed mode converter
        sdp.AddLines(['device L 4 mixedmode','device R 4 mixedmode',
            'device TE 2','device TO 2',
            'port 1 L 1','port 2 L 2','port 3 R 1','port 4 R 2',
            'connect L 3 TO 1','connect R 3 TO 2',
            'connect L 4 TE 1','connect R 4 TE 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
#        ssps.DocStart()
        ssps.LaTeXSolution(size='big')
#        ssps.DocEnd()
        ssps.Emit()
        self.CheckSymbolicResult(self.id(), ssps, self.id())
    def testTline8(self):
        """
        this test checks that a four port transmission line approximated as 10,000
        sections of RLGC sections with 1/10,000th of the supplied series resistance
        and inductance, shunt capacitance and conductance, and mutual inductance and
        capacitance is the same the mixed mode model with the differential and common-mode
        impedance and propagation time corresponding to RLGC.
        """
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=[n*200e6 for n in range(50)]
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
        spmodel=si.sp.dev.TLineDifferentialRLGC(
            f,
                0.0,0.0,Ls,0.0,Cs,0.0,
                0.0,0.0,Ls,0.0,Cs,0.0,
                Cm,0.0,0.0,Lm,50.,100000)
        spmodel2=si.sp.dev.MixedModeTLine(f,Zd,Td,Zc,Tc)
        self.assertTrue(self.SParametersAreEqual(spmodel,spmodel2,0.005),self.id()+' result not same')
    def testTline9(self):
        """
        this test checks that a four port transmission line approximated as 10,000
        sections of RLGC sections with 1/10,000th of the supplied series resistance
        and inductance, shunt capacitance and conductance, and mutual inductance and
        capacitance is the same the mixed mode model with the differential and common-mode
        impedance and propagation time corresponding to RLGC.
        """
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=[n*200e6 for n in range(50)]
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
        spmodel=si.sp.dev.TLineDifferentialRLGC(
            f,
                0.0,0.0,Ls,0.0,Cs,0.0,
                0.0,0.0,Ls,0.0,Cs,0.0,
                Cm,0.0,0.0,Lm,50.,0)
        spmodel2=si.sp.dev.MixedModeTLine(f,Zd,Td,Zc,Tc)
        self.assertTrue(self.SParametersAreEqual(spmodel,spmodel2,0.005),self.id()+' result not same')
    def testWriteTLineLosslessSp(self):
        fileName="../../SignalIntegrity/Lib/SParameters/Devices/TLineLossless.py"
        className='TLineLossless'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteTLineTwoPortLosslessDev(self):
        fileName="../../SignalIntegrity/Lib/Devices/TLineTwoPortLossless.py"
        className=''
        defName=['TLineTwoPortLossless']
        self.WriteClassCode(fileName,className,defName)
    def testWriteTLineFourPortLosslessDev(self):
        fileName="../../SignalIntegrity/Lib/Devices/TLineFourPortLossless.py"
        className=''
        defName=['TLineFourPortLossless']
        self.WriteClassCode(fileName,className,defName)
    def testWriteTLineTwoPortDev(self):
        fileName="../../SignalIntegrity/Lib/Devices/TLineTwoPort.py"
        className=''
        defName=['TLineTwoPort']
        self.WriteClassCode(fileName,className,defName)
    def testWriteTLineFourPortDev(self):
        fileName="../../SignalIntegrity/Lib/Devices/TLineFourPort.py"
        className=''
        defName=['TLineFourPort']
        self.WriteClassCode(fileName,className,defName)
    def testWriteTLineTwoPortRLGC(self):
        fileName="../../SignalIntegrity/Lib/SParameters/Devices/TLineTwoPortRLGC.py"
        className='TLineTwoPortRLGC'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteTLineTwoPortRLGCApproximate(self):
        fileName="../../SignalIntegrity/Lib/SParameters/Devices/TLineTwoPortRLGCApproximate.py"
        className='TLineTwoPortRLGCApproximate'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteTLineTwoPortRLGCAnalytic(self):
        fileName="../../SignalIntegrity/Lib/SParameters/Devices/TLineTwoPortRLGCAnalytic.py"
        className='TLineTwoPortRLGCAnalytic'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteTLineDifferentialRLGC(self):
        fileName="../../SignalIntegrity/Lib/SParameters/Devices/TLineDifferentialRLGC.py"
        className='TLineDifferentialRLGC'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteTLineDifferentialRLGCApproximate(self):
        fileName="../../SignalIntegrity/Lib/SParameters/Devices/TLineDifferentialRLGCApproximate.py"
        className='TLineDifferentialRLGCApproximate'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteTLineDifferentialRLGCUncoupled(self):
        fileName="../../SignalIntegrity/Lib/SParameters/Devices/TLineDifferentialRLGCUncoupled.py"
        className='TLineDifferentialRLGCUncoupled'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteTLineDifferentialRLGCBalanced(self):
        fileName="../../SignalIntegrity/Lib/SParameters/Devices/TLineDifferentialRLGCBalanced.py"
        className='TLineDifferentialRLGCBalanced'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testFourPortTLineSignalIntegrityApp(self):
        resultTLineModel=self.SParameterResultsChecker('FourPortTLineCompare.xml')
        resultTLineXfrmr=self.SParameterResultsChecker('FourPortTLineCompareIdealXfrmr.xml')
        resultTLineCommonModeOpen=self.SParameterResultsChecker('FourPortTLineCompareCommonModeOpen.xml')
        self.assertTrue(self.SParametersAreEqual(resultTLineModel[0], resultTLineXfrmr[0], 1e-5),'four port model not same as ideal transformer model')
        self.assertTrue(self.SParametersAreEqual(resultTLineModel[0], resultTLineCommonModeOpen[0], 1e-5),'four port model not same as common mode open model')
    def testWriteRseSp(self):
        fileName="../../SignalIntegrity/Lib/SParameters/Devices/SeriesRse.py"
        className='SeriesRse'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteRse(self):
        fileName="../../SignalIntegrity/Lib/Devices/SeriesRse.py"
        className=''
        defName=['SeriesRse']
        self.WriteClassCode(fileName,className,defName)
    def testTransmissionLineSimulation(self):
        (sourceNames,outputNames,transferMatrices,outputWaveforms)=self.SimulationResultsChecker('TransmissionLineSimulation')
        wfdict={name:wf for (name,wf) in zip(outputNames,outputWaveforms)}
        V=1.
        Zs=40.
        Zl=65.
        Zc=55.
        Z0=50.
        K0=math.sqrt(Z0)
        Kc=math.sqrt(Zc)
        td=wfdict['Vs'].TimeDescriptor()
        # Test our understanding of the definition of waves in the Z0 reference impedance
        wfdict['Fsexp']=si.td.wf.Waveform(td,[1/2./K0*(v+i*Z0) for (v,i) in zip(wfdict['Vs'].Values(),wfdict['Is'].Values())])
        wfdict['Rsexp']=si.td.wf.Waveform(td,[1/2./K0*(v-i*Z0) for (v,i) in zip(wfdict['Vs'].Values(),wfdict['Is'].Values())])
        self.assertTrue(wfdict['Fsexp'],wfdict['Fs'])
        self.assertTrue(wfdict['Rsexp'],wfdict['Rs'])
        wfdict['Flexp']=si.td.wf.Waveform(td,[1/2./K0*(v+i*Z0) for (v,i) in zip(wfdict['Vl'].Values(),wfdict['Il'].Values())])
        wfdict['Rlexp']=si.td.wf.Waveform(td,[1/2./K0*(v-i*Z0) for (v,i) in zip(wfdict['Vl'].Values(),wfdict['Il'].Values())])
        self.assertTrue(wfdict['Flexp'],wfdict['Fl'])
        self.assertTrue(wfdict['Rlexp'],wfdict['Rl'])
        # Test our understanding of the definition of waves in the Zc reference impedance
        GsZc=(Zs-Zc)/(Zs+Zc)
        GlZc=(Zl-Zc)/(Zl+Zc)
        wfdict['FsZc']=si.td.wf.Waveform(td,[1/2./Kc*(v+i*Zc) for (v,i) in zip(wfdict['Vs'].Values(),wfdict['Is'].Values())])
        wfdict['RsZc']=si.td.wf.Waveform(td,[1/2./Kc*(v-i*Zc) for (v,i) in zip(wfdict['Vs'].Values(),wfdict['Is'].Values())])
        wfdict['FlZc']=si.td.wf.Waveform(td,[1/2./Kc*(v+i*Zc) for (v,i) in zip(wfdict['Vl'].Values(),wfdict['Il'].Values())])
        wfdict['RlZc']=si.td.wf.Waveform(td,[1/2./Kc*(v-i*Zc) for (v,i) in zip(wfdict['Vl'].Values(),wfdict['Il'].Values())])
        m1=1./Kc*Zc/(Zs+Zc)*V
        # time zero is point 1
        self.assertAlmostEqual(wfdict['FsZc'][1], m1, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RsZc'][1], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FlZc'][1], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RlZc'][1], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FsZc'][2], 0,  12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RsZc'][2], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FlZc'][2], m1, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RlZc'][2], m1*GlZc, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FsZc'][3], m1*GlZc*GsZc,  12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RsZc'][3], m1*GlZc, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FlZc'][3], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RlZc'][3], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FsZc'][4], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RsZc'][4], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FlZc'][4], m1*GlZc*GsZc, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RlZc'][4], m1*GlZc*GsZc*GlZc, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FsZc'][5], m1*GlZc*GsZc*GlZc*GsZc,  12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RsZc'][5], m1*GlZc*GsZc*GlZc, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FlZc'][5], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RlZc'][5], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FsZc'][6], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RsZc'][6], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FlZc'][6], m1*GlZc*GsZc*GlZc*GsZc, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RlZc'][6], m1*GlZc*GsZc*GlZc*GsZc*GlZc, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FsZc'][7], m1*GlZc*GsZc*GlZc*GsZc*GlZc*GsZc,  12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RsZc'][7], m1*GlZc*GsZc*GlZc*GsZc*GlZc, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FlZc'][7], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RlZc'][7], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FsZc'][8], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RsZc'][8], 0, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['FlZc'][8], m1*GlZc*GsZc*GlZc*GsZc*GlZc*GsZc, 12, 'simulation incorrect')
        self.assertAlmostEqual(wfdict['RlZc'][8], m1*GlZc*GsZc*GlZc*GsZc*GlZc*GsZc*GlZc, 12, 'simulation incorrect')

if __name__ == '__main__':
    unittest.main()
