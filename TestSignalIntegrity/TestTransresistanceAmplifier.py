import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import matrix
from TestHelpers import *

class TestTransresistanceAmplifier(unittest.TestCase,SourcesTesterHelper,RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testTransresistanceAmplifierFourPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 D 2 3 ZO 2 4 D 3',
            'connect ZI 2 D 1','connect ZO 1 D 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('D',si.sy.CurrentControlledVoltageSource('\\gamma'))
        ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXBlockSolutionBig().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transresistance Amplifier Four Port')
    def testTransresistanceAmplifierFourPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','port 1 D 1 2 D 2 3 D 3 4 D 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,False)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        ssps.AssignSParameters('D',si.sy.TransresistanceAmplifierFourPort('\\gamma','Z_i','Z_o'))
        ssps.LaTeXBlockSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transresistance Amplifier Four Port Symbolic')
    def testTransresistanceAmplifierFourPortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2.8 # Zout
        sdp.AddLines(['device D 4 currentcontrolledvoltagesource '+str(G),
            'device ZI 2 R '+str(ZI),
            'device ZO 2 R '+str(ZO),
            'port 1 ZI 1 2 D 2 3 ZO 2 4 D 3',
            'connect ZI 2 D 1','connect ZO 1 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransresistanceAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transresistance Amplifier Four Port incorrect')
    def testTransresistanceAmplifierFourPortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2.8 # Zout
        sdp.AddLines(['device D 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 D 2 3 ZO 2 4 D 3',
            'connect ZI 2 D 1','connect ZO 1 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.CurrentControlledVoltageSource(G))
        sspn.AssignSParameters('ZI',si.dev.SeriesZ(ZI))
        sspn.AssignSParameters('ZO',si.dev.SeriesZ(ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransresistanceAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transresistance Amplifier Four Port incorrect')
    def testTransresistanceAmplifierFourPortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=2.8 # Zout
        sdp.AddLines(['device D 4 transresistanceamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2 3 D 3 4 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransresistanceAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transresistance Amplifier Four Port incorrect')
    def testTransresistanceAmplifierThreePort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4',
            'port 1 D 1 2 D 3 3 D 2',
            'connect D 2 D 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('D',si.sy.TransresistanceAmplifier(4,'\\gamma','Z_i','Z_o'))
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transresistance Amplifier Three Port')
    def testTransresistanceAmplifierThreePortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','port 1 D 1 2 D 2 3 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        ssps.AssignSParameters('D',si.sy.TransresistanceAmplifier(3,'\\gamma','Z_i','Z_o'))
        ssps.LaTeXBlockSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transresistance Amplifier Three Port Symbolic')
    def testTransresistanceAmplifierThreePortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=0.8 # Zout
        sdp.AddLines(['device D 4 transresistanceamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 3 3 D 2',
            'connect D 2 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransresistanceAmplifierThreePort(G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transresistance Amplifier Three Port incorrect')
    def testTransresistanceAmplifierThreePortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=0.8 # Zout
        sdp.AddLines(['device D 4',
            'port 1 D 1 2 D 3 3 D 2',
            'connect D 2 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.TransresistanceAmplifierFourPort(G,ZI,ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransresistanceAmplifierThreePort(G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transresistance Amplifier Three Port incorrect')
    def testTransresistanceAmplifierThreePortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.4 # Zin
        ZO=0.8 # Zout
        sdp.AddLines(['device D 3 transresistanceamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2 3 D 3'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransresistanceAmplifier(3,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transresistance Amplifier Three Port incorrect')
    def testTransresistanceAmplifierTwoPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device G1 1 ground','device G2 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 G1 1','connect D 4 G2 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        D=si.sy.TransresistanceAmplifier(4,'\\gamma','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transresistance Amplifier Two Port Full')
    def testTransresistanceAmplifierTwoPortAlternate(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','device G 1 ground',
            'port 1 D 1 2 D 2',
            'connect D 3 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        D=si.sy.TransresistanceAmplifier(3,'\\gamma','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transresistance Amplifier Two Port Alternate')
    def testTransresistanceAmplifierTwoPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2',
            'port 1 D 1 2 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,False)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        D=si.sy.TransresistanceAmplifierTwoPort('\\gamma','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXBlockSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transresistance Amplifier Two Port Symbolic')
    def testTransresistanceAmplifierTwoPortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.8 # Zin
        ZO=1.9 # Zout
        sdp.AddLines(['device D 4 transresistanceamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'device G 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 D 4 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransresistanceAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transresistance Amplifier Two Port incorrect')
    def testTransresistanceAmplifierTwoPortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.8 # Zin
        ZO=1.9 # Zout
        sdp.AddLines(['device D 4',
            'device G 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 D 4 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.TransresistanceAmplifier(4,G,ZI,ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransresistanceAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transresistance Amplifier Two Port incorrect')
    def testTransresistanceAmplifierTwoPortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.8 # Zin
        ZO=1.9 # Zout
        sdp.AddLines(['device D 2 transresistanceamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransresistanceAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transresistance Amplifier Two Port incorrect')
    def testTransresistanceAmplifierTwoPortAlternateNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1.8 # Zin
        ZO=1.9 # Zout
        sdp.AddLines(['device D 3 transresistanceamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'device G 1 ground',
            'port 1 D 1 2 D 2',
            'connect D 3 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransresistanceAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transresistance Amplifier Two Port Alternate incorrect')
    def testTransresistanceAmplifierFourPortCode(self):
        self.WriteCode('TestTransresistanceAmplifier.py','testTransresistanceAmplifierFourPort(self)',self.standardHeader)
    def testTransresistanceAmplifierThreePortCode(self):
        self.WriteCode('TestTransresistanceAmplifier.py','testTransresistanceAmplifierThreePort(self)',self.standardHeader)
    def testTransresistanceAmplifierThreePortAlternateCode(self):
        self.WriteCode('TestTransresistanceAmplifier.py','testTransresistanceAmplifierThreePortAlternate(self)',self.standardHeader)
    def testTransresistanceAmplifierTwoPortCode(self):
        self.WriteCode('TestTransresistanceAmplifier.py','testTransresistanceAmplifierTwoPort(self)',self.standardHeader)
    def testTransresistanceAmplifierTwoPortAlternateCode(self):
        self.WriteCode('TestTransresistanceAmplifier.py','testTransresistanceAmplifierTwoPortAlternate(self)',self.standardHeader)


if __name__ == '__main__':
    unittest.main()

