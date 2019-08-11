"""
TestCurrentAmplifier.py
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
from numpy import linalg
from numpy import matrix

class TestCurrentAmplifier(unittest.TestCase,si.test.SourcesTesterHelper,si.test.RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        si.test.RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testCurrentAmplifierFourPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DC 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 DC 2 3 DC 4 4 DC 3',
            'connect ZI 2 DC 1','connect ZO 1 DC 4','connect ZO 2 DC 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('\\beta'))
        ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Four Port')
    def testCurrentAmplifierFourPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DC 4','port 1 DC 1 2 DC 2 3 DC 3 4 DC 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
        ssps.AssignSParameters('DC',si.sy.CurrentAmplifier(4,'\\beta','Z_i','Z_o'))
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Four Port Symbolic')
    def testCurrentAmplifierFourPortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device DC 4 currentcontrolledcurrentsource '+str(G),
            'device ZI 2 R '+str(ZI),
            'device ZO 2 R '+str(ZO),
            'port 1 ZI 1 2 DC 2 3 DC 4 4 DC 3',
            'connect ZI 2 DC 1','connect ZO 1 DC 4','connect ZO 2 DC 3'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Four Port incorrect')
    def testCurrentAmplifierFourPortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device DC 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 DC 2 3 DC 4 4 DC 3',
            'connect ZI 2 DC 1','connect ZO 1 DC 4','connect ZO 2 DC 3'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('DC',si.dev.CurrentControlledCurrentSource(G))
        sspn.AssignSParameters('ZI',si.dev.SeriesZ(ZI))
        sspn.AssignSParameters('ZO',si.dev.SeriesZ(ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Four Port incorrect')
    def testCurrentAmplifierFourPortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device D 4 currentamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2 3 D 3 4 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Four Port incorrect')
    def testCurrentAmplifierThreePort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4',
            'port 1 D 1 2 D 3 3 D 2',
            'connect D 2 D 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('D',si.sy.CurrentAmplifier(4,'\\beta','Z_i','Z_o'))
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Three Port')
    def testCurrentAmplifierThreePortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','port 1 D 1 2 D 2 3 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small',
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
        ssps.AssignSParameters('D',si.sy.CurrentAmplifier(3,'\\beta','Z_i','Z_o'))
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Three Port Symbolic')
    def testCurrentAmplifierThreePortSymbolic2(self):
        symbolic=si.sd.Symbolic(size='small')
        S=si.sy.CurrentAmplifierThreePortWithoutDenom('\\beta','Z_i','Z_o')
        D=si.sy.CurrentAmplifierThreePortDenom('\\beta','Z_i','Z_o')
        symbolic._AddEq('\\mathbf{S}=\\frac{1}{'+D+'}')
        symbolic._AddEq('\\cdot '+symbolic._LaTeXMatrix(S))
        symbolic.Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Current Amplifier Three Port Symbolic 2')
    def testCurrentAmplifierThreePortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device D 4 currentamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 3 3 D 2',
            'connect D 2 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifierThreePort(G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Three Port incorrect')
    def testCurrentAmplifierThreePortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device D 4',
            'port 1 D 1 2 D 3 3 D 2',
            'connect D 2 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.CurrentAmplifierFourPort(G,ZI,ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifierThreePort(G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Three Port incorrect')
    def testCurrentAmplifierThreePortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device D 3 currentamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2 3 D 3'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(3,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Three Port incorrect')
    def testCurrentAmplifierTwoPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device G1 1 ground','device G2 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 G1 1','connect D 4 G2 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        D=si.sy.CurrentAmplifier(4,'\\beta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Two Port Full')
    def testCurrentAmplifierTwoPortAlternate(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','device G 1 ground',
            'port 1 D 1 2 D 2',
            'connect D 3 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        D=si.sy.CurrentAmplifier(3,'\\beta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Two Port Alternate')
    def testCurrentAmplifierTwoPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2',
            'port 1 D 1 2 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
        D=si.sy.CurrentAmplifier(2,'\\beta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Two Port Symbolic')
    def testCurrentAmplifierTwoPortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device D 4 currentamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'device G 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 D 4 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Two Port incorrect')
    def testCurrentAmplifierTwoPortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device D 4',
            'device G 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 D 4 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.CurrentAmplifier(4,G,ZI,ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Two Port incorrect')
    def testCurrentAmplifierTwoPortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device D 2 currentamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Two Port incorrect')
    def testCurrentAmplifierTwoPortAlternateNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=1.4 # Zout
        sdp.AddLines(['device D 3 currentamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'device G 1 ground',
            'port 1 D 1 2 D 2',
            'connect D 3 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.CurrentAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Current Amplifier Two Port Alternate incorrect')
    def testCurrentAmplifierFourPortCode(self):
        self.WriteCode('TestCurrentAmplifier.py','testCurrentAmplifierFourPort(self)',self.standardHeader)
    def testCurrentAmplifierThreePortCode(self):
        self.WriteCode('TestCurrentAmplifier.py','testCurrentAmplifierThreePort(self)',self.standardHeader)
    def testCurrentAmplifierThreePortAlternateCode(self):
        self.WriteCode('TestCurrentAmplifier.py','testCurrentAmplifierThreePortAlternate(self)',self.standardHeader)
    def testCurrentAmplifierTwoPortCode(self):
        self.WriteCode('TestCurrentAmplifier.py','testCurrentAmplifierTwoPort(self)',self.standardHeader)
    def testCurrentAmplifierTwoPortAlternateCode(self):
        self.WriteCode('TestCurrentAmplifier.py','testCurrentAmplifierTwoPortAlternate(self)',self.standardHeader)

if __name__ == '__main__':
    unittest.main()

