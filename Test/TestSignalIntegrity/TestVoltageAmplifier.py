"""
TestVoltageAmplifier.py
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
import os

import SignalIntegrity.Lib as si
from numpy import linalg,matrix

class TestVoltageAmplifier(unittest.TestCase,si.test.SourcesTesterHelper,si.test.RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        si.test.RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    def tearDown(self):
        pass
    def testVoltageAmplifierFourPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device ZI 2','device ZO 2','connect ZI 1 DV 2',
            'connect ZI 2 DV 1','connect ZO 1 DV 4','port 1 ZI 1 2 ZI 2 3 ZO 2 4 DV 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
        ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Four Port')
    def testVoltageAmplifierFourPortShunt(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device ZI 4','device ZO 2',
            'port 1 ZI 1 2 ZI 2 3 ZO 2 4 DV 3',
            'connect ZI 3 DV 2','connect ZI 4 DV 1','connect ZO 1 DV 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
        ssps.AssignSParameters('ZI',si.sy.ShuntZ(4,'Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Four Port')
    def testVoltageAmplifierFourPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4',
            'port 1 DV 1 2 DV 2 3 DV 3 4 DV 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
        ssps.AssignSParameters('DV',si.sy.VoltageAmplifier(4,'\\alpha','Z_i','Z_o'))
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Four Port Symbolic')
    def testVoltageAmplifierFourPortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device DV 4 voltagecontrolledvoltagesource '+str(G),
            'device ZI 2 R '+str(ZI),
            'device ZO 2 R '+str(ZO),
            'port 1 ZI 1 2 ZI 2 3 ZO 2 4 DV 3',
            'connect ZI 1 DV 2','connect ZI 2 DV 1','connect ZO 1 DV 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.VoltageAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Voltage Amplifier Four Port incorrect')
    def testVoltageAmplifierFourPortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device DV 4',
            'device ZI 2',
            'device ZO 2',
            'port 1 ZI 1 2 ZI 2 3 ZO 2 4 DV 3',
            'connect ZI 1 DV 2','connect ZI 2 DV 1','connect ZO 1 DV 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('DV',si.dev.VoltageControlledVoltageSource(G))
        sspn.AssignSParameters('ZI',si.dev.SeriesZ(ZI))
        sspn.AssignSParameters('ZO',si.dev.SeriesZ(ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.VoltageAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Voltage Amplifier Four Port incorrect')
    def testVoltageAmplifierFourPortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device D 4 voltageamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2 3 D 3 4 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.VoltageAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Voltage Amplifier Four Port incorrect')
    def testVoltageAmplifierThreePort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4',
            'port 1 DV 1 2 DV 3 3 DV 2',
            'connect DV 2 DV 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('DV',si.sy.VoltageAmplifier(4,'\\alpha','Z_i','Z_o'))
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Three Port')
    def testVoltageAmplifierThreePortAlternate(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 3 ZI 2 2 ZO 2',
            'connect ZI 1 DV 2','connect ZI 2 DV 1','connect ZO 1 DV 4','connect DV 3 DV 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
        ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Three Port')
    def testVoltageAmplifierThreePortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 3',
            'port 1 DV 1 2 DV 2 3 DV 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small',
            eqprefix='\\begin{multline} ',eqsuffix=' \\end{multline}')
        ssps.AssignSParameters('DV',si.sy.VoltageAmplifier(3,'\\alpha','Z_i','Z_o'))
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        ssps.m_lines[0]=ssps.m_lines[0].replace('\\mathbf{S} = ','\\mathbf{S} =\\ldots\\\\ ')
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Three Port Symbolic')
    def testVoltageAmplifierThreePortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device DV 4 voltageamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 DV 1 2 DV 3 3 DV 2',
            'connect DV 2 DV 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.VoltageAmplifierThreePort(G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Voltage Amplifier Three Port incorrect')
    def testVoltageAmplifierThreePortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device DV 4',
            'port 1 DV 1 2 DV 3 3 DV 2',
            'connect DV 2 DV 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('DV',si.dev.VoltageAmplifierFourPort(G,ZI,ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.VoltageAmplifierThreePort(G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Voltage Amplifier Three Port incorrect')
    def testVoltageAmplifierThreePortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device D 3 voltageamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2 3 D 3'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.VoltageAmplifier(3,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Voltage Amplifier Three Port incorrect')
    def testVoltageAmplifierThreePortAlternateNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device DV 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 3 ZI 2 2 ZO 2',
            'connect ZI 1 DV 2','connect ZI 2 DV 1','connect ZO 1 DV 4','connect DV 3 DV 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('DV',si.dev.VoltageControlledVoltageSource(G))
        sspn.AssignSParameters('ZI',si.dev.SeriesZ(ZI))
        sspn.AssignSParameters('ZO',si.dev.SeriesZ(ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.VoltageAmplifier(3,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Voltage Amplifier Three Port Alternate incorrect')
    def testVoltageAmplifier2(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4',
            'device ZI 2',
            'device ZO 2',
            'device G 1 ground',
            'port 1 ZI 1',
            'port 2 ZO 2',
            'connect ZI 1 DV 2',
            'connect ZI 2 G 1',
            'connect DV 1 G 1',
            'connect ZO 1 DV 4',
            'connect DV 3 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
        ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier 2 Full')
    def testVoltageAmplifierTwoPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device G 1 ground','port 1 DV 1 2 DV 3',
            'connect DV 2 G 1','connect DV 4 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        DV=si.sy.VoltageAmplifier(4,'\\alpha','Z_i','Z_o')
        ssps.AssignSParameters('DV',DV)
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Two Port Full')
    def testVoltageAmplifierTwoPortAlternate(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 3','device G 1 ground',
            'port 1 DV 1 2 DV 2',
            'connect DV 3 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        DV=si.sy.VoltageAmplifier(3,'\\alpha','Z_i','Z_o')
        ssps.AssignSParameters('DV',DV)
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Two Port Alternate')
    def testVoltageAmplifierTwoPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 2',
            'port 1 DV 1 2 DV 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
        DV=si.sy.VoltageAmplifier(2,'\\alpha','Z_i','Z_o')
        ssps.AssignSParameters('DV',DV)
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Two Port Symbolic')
    def testVoltageAmplifierTwoPortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device DV 4 voltageamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'device G 1 ground',
            'port 1 DV 1 2 DV 3',
            'connect DV 2 DV 4 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.VoltageAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Voltage Amplifier Two Port incorrect')
    def testVoltageAmplifierTwoPortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device DV 4',
            'device G 1 ground',
            'port 1 DV 1 2 DV 3',
            'connect DV 2 DV 4 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('DV',si.dev.VoltageAmplifier(4,G,ZI,ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.VoltageAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Voltage Amplifier Two Port incorrect')
    def testVoltageAmplifierTwoPortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device D 2 voltageamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.VoltageAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Voltage Amplifier Two Port incorrect')
    def testVoltageAmplifierTwoPortAlternateNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device DV 3 voltageamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'device G 1 ground',
            'port 1 DV 1 2 DV 2',
            'connect DV 3 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.VoltageAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Voltage Amplifier Two Port Alternate incorrect')
    def testVoltageAmplifierTwoPortVoltageSeriesFeedbackAlternate(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device V 4','device F 4','device G 1 ground',
                      'port 1 V 1 2 V 3',
                      'connect V 2 F 3','connect F 4 G 1','connect V 3 F 1',
                      'connect V 4 G 1','connect F 2 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps._AddEq('\\mathbf{V}='+ssps._LaTeXMatrix(si.sy.VoltageAmplifier(4,'A','Z_i','Z_o')))
        ssps._AddEq('\\mathbf{F}='+ssps._LaTeXMatrix(si.sy.VoltageAmplifier(4,'B','Z_{if}','Z_{of}')))
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Two Port Voltage Series Feedback')
    def testVoltageAmplifierTwoPortVoltageSeriesFeedback(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device F 2','device G 1 ground','port 1 D 1 2 D 3',
            'connect D 2 F 2','connect D 3 F 1','connect D 4 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('D',si.sy.VoltageAmplifier(4,'\\alpha','Z_i','Z_o'))
        ssps.AssignSParameters('F',si.sy.VoltageAmplifier(2,'\\beta','Z_{if}','Z_{of}'))
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Two Port Voltage Series Feedback')
    def testVoltageAmplifierFourPortVoltageSeriesFeedback(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device F 4',
            'port 1 D 1 2 F 4 3 D 3 4 F 2',
            'connect D 2 F 3','connect D 3 F 1','connect D 4 F 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        DSp=ssps[ssps.IndexOfDevice('D')].SParameters
        DSp[1][1]=DSp[0][0]; DSp[1][0]=DSp[0][1]
        DSp[0][2]=0; DSp[0][3]=0; DSp[1][2]=0; DSp[1][3]=0
        DSp[2][1]='-'+DSp[2][0]; DSp[3][0]='-'+DSp[2][0]
        DSp[3][1]=DSp[2][0]; DSp[3][2]=DSp[2][3]; DSp[3][3]=DSp[2][2]
        ssps._AddEq('\\mathbf{D}='+ssps._LaTeXMatrix(si.helper.Matrix2Text(DSp)))
        DSp=ssps[ssps.IndexOfDevice('F')].SParameters
        DSp[1][1]=DSp[0][0]; DSp[1][0]=DSp[0][1]
        DSp[0][2]=0; DSp[0][3]=0; DSp[1][2]=0; DSp[1][3]=0
        DSp[2][1]='-'+DSp[2][0]; DSp[3][0]='-'+DSp[2][0]
        DSp[3][1]=DSp[2][0]; DSp[3][2]=DSp[2][3]; DSp[3][3]=DSp[2][2]
        ssps._AddEq('\\mathbf{F}='+ssps._LaTeXMatrix(si.helper.Matrix2Text(DSp)))
        ssps._AddEq('\\mathbf{D}='+ssps._LaTeXMatrix(si.sy.VoltageAmplifier(4,'\\alpha','Z_i','Z_o')))
        ssps._AddEq('\\mathbf{F}='+ssps._LaTeXMatrix(si.sy.VoltageAmplifier(4,'\\beta','Z_{if}','Z_{of}')))
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Four Port Voltage Series Feedback')
    def testVoltageAmplifierFourPortVoltageSeriesFeedbackAlternate(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device F 4','connect D 2 F 3',
            'connect D 3 F 1','connect D 4 F 2','port 1 D 1 2 F 4 3 D 3 4 F 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        DSp=ssps[ssps.IndexOfDevice('D')].SParameters
        DSp[1][1]=DSp[0][0]; DSp[1][0]=DSp[0][1]
        DSp[0][2]=0; DSp[0][3]=0; DSp[1][2]=0; DSp[1][3]=0
        DSp[2][1]='-'+DSp[2][0]; DSp[3][0]='-'+DSp[2][0]
        DSp[3][1]=DSp[2][0]; DSp[3][2]=DSp[2][3]; DSp[3][3]=DSp[2][2]
        DS=si.sy.VoltageAmplifier(4,'\\alpha','Z_i','Z_o')
        ssps._AddEq('D_{11}={\\scriptstyle '+DS[0][0]+'}')
        ssps._AddEq('D_{12}={\\scriptstyle '+DS[0][1]+'}')
        ssps._AddEq('D_{31}={\\scriptstyle '+DS[2][0]+'}')
        ssps._AddEq('D_{33}={\\scriptstyle '+DS[2][2]+'}')
        ssps._AddEq('D_{34}={\\scriptstyle '+DS[2][3]+'}')
        # pragma: exclude
        #si.sy.SymbolicMatrix(si.helper.Matrix2Text(DSp),'\\mathbf{D}',True).Emit()
        # pragma: include
        DSp=ssps[ssps.IndexOfDevice('F')].SParameters
        DSp[1][1]=DSp[0][0]; DSp[1][0]=DSp[0][1]
        DSp[0][2]=0; DSp[0][3]=0; DSp[1][2]=0; DSp[1][3]=0
        DSp[2][1]='-'+DSp[2][0]; DSp[3][0]='-'+DSp[2][0]
        DSp[3][1]=DSp[2][0]; DSp[3][2]=DSp[2][3]; DSp[3][3]=DSp[2][2]
        FS=si.sy.VoltageAmplifier(4,'\\beta','Z_{if}','Z_{of}')
        ssps._AddEq('F_{11}={\\scriptstyle '+FS[0][0]+'}')
        ssps._AddEq('F_{12}={\\scriptstyle '+FS[0][1]+'}')
        ssps._AddEq('F_{31}={\\scriptstyle '+FS[2][0]+'}')
        ssps._AddEq('F_{33}={\\scriptstyle '+FS[2][2]+'}')
        ssps._AddEq('F_{34}={\\scriptstyle '+FS[2][3]+'}')
        # pragma: exclude
        # si.sy.SymbolicMatrix(si.helper.Matrix2Text(DSp),'\\mathbf{F}',True).Emit()
        # pragma: include
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Four Port Voltage Series Feedback')
    def testVoltageAmplifierVoltageSeriesFeedbackConjecture(self):
        sdp=si.p.SystemDescriptionParser()
        alpha=100. # gain
        Zi=2000. # Zin
        Zo=2. # Zout
        beta=0.
        Zif=1000.
        Zof=1.
        sdp.AddLines(['device D 4 voltageamplifier gain '+str(alpha)+' zi '+str(Zi)+' zo '+str(Zo),
            'device DF 2 voltageamplifier gain '+str(beta)+' zi '+str(Zif)+' zo '+str(Zof),
            'device G 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 DF 2','connect D 3 DF 1','connect D 4 G 1'])
        rescalc=si.sd.SystemSParametersNumeric(sdp.SystemDescription()).SParameters()
        rescorrect=si.dev.VoltageAmplifier(2,alpha*Zif/(Zo+Zif)*Zi/(Zi+Zof),Zi+Zof,Zo*Zif/(Zo+Zif))
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Voltage Amplifier Feedback incorrect')
    def testVoltageAmplifierVoltageSeriesFeedbackConjecture2(self):
        sdp=si.p.SystemDescriptionParser()
        alpha=10000. # gain
        Zi=2000. # Zin
        Zo=2. # Zout
        beta=0.1
        Zif=1000.
        Zof=1.
        sdp.AddLines(['device D 4 voltageamplifier gain '+str(alpha)+' zi '+str(Zi)+' zo '+str(Zo),
            'device DF 2 voltageamplifier gain '+str(beta)+' zi '+str(Zif)+' zo '+str(Zof),
            'device G 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 DF 2','connect D 3 DF 1','connect D 4 G 1'])
        AV=alpha*Zif/(Zo+Zif)*Zi/(Zi+Zof) # amplifier gain taking feedback network loading into account
        Ziff=Zi+Zof # input impedance taking feedback network into account
        Zoff=Zo*Zif/(Zo+Zif) # output impedance taking feedback network into account
        # now account for effects of feedback
        D=(1.+beta*AV)
        Zoff=Zoff/D # output impedance lowered
        Ziff=Ziff*D # input impedance raised
        A=AV/D # gain desensitized
        rescalc=si.sd.SystemSParametersNumeric(sdp.SystemDescription()).SParameters()
        rescorrect=si.dev.VoltageAmplifier(2,A,Ziff,Zoff)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-4,'Voltage Amplifier Feedback incorrect')
    def testVoltageAmplifierFourPortCode(self):
        self.WriteCode('TestVoltageAmplifier.py','testVoltageAmplifierFourPort(self)',self.standardHeader)
    def testVoltageAmplifierFourPortShuntCode(self):
        self.WriteCode('TestVoltageAmplifier.py','testVoltageAmplifierFourPortShunt(self)',self.standardHeader)
    def testVoltageAmplifierThreePortCode(self):
        self.WriteCode('TestVoltageAmplifier.py','testVoltageAmplifierThreePort(self)',self.standardHeader)
    def testVoltageAmplifierThreePortAlternateCode(self):
        self.WriteCode('TestVoltageAmplifier.py','testVoltageAmplifierThreePortAlternate(self)',self.standardHeader)
    def testVoltageAmplifierTwoPortCode(self):
        self.WriteCode('TestVoltageAmplifier.py','testVoltageAmplifierTwoPort(self)',self.standardHeader)
    def testVoltageAmplifierTwoPortAlternateCode(self):
        self.WriteCode('TestVoltageAmplifier.py','testVoltageAmplifierTwoPortAlternate(self)',self.standardHeader)
    def testVoltageAmplifierFourPortVoltageSeriesFeedbackCode(self):
        self.WriteCode('TestVoltageAmplifier.py','testVoltageAmplifierFourPortVoltageSeriesFeedback(self)',self.standardHeader)
    def testVoltageAmplifierTwoPortVoltageSeriesFeedbackCode(self):
        self.WriteCode('TestVoltageAmplifier.py','testVoltageAmplifierTwoPortVoltageSeriesFeedback(self)',self.standardHeader)
    def testVoltageAmplifierFourPortVoltageSeriesFeedbackAlternateCode(self):
        self.WriteCode('TestVoltageAmplifier.py','testVoltageAmplifierFourPortVoltageSeriesFeedbackAlternate(self)',self.standardHeader)

if __name__ == '__main__':
    unittest.main()

