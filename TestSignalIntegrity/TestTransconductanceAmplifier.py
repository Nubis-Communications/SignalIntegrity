import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import matrix
from TestHelpers import SourcesTesterHelper
from TestHelpers import RoutineWriterTesterHelper

class TestTransconductanceAmplifier(unittest.TestCase,SourcesTesterHelper,RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testTransconductanceAmplifierFourPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 ZI 2 3 ZO 1 4 ZO 2',
            'connect ZI 1 D 2','connect ZI 2 D 1',
            'connect ZO 1 D 4','connect ZO 2 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('D',si.sy.VoltageControlledCurrentSource('\\delta'))
        ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transconductance Amplifier Four Port')
    def testTransconductanceAmplifierFourPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','port 1 D 1 2 D 2 3 D 3 4 D 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
        ssps.AssignSParameters('D',si.sy.TransconductanceAmplifierFourPort('\\delta','Z_i','Z_o'))
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transconductance Amplifier Four Port Symbolic')
    def testTransconductanceAmplifierFourPortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=4000 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device D 4 voltagecontrolledcurrentsource '+str(G),
            'device ZI 2 R '+str(ZI),
            'device ZO 2 R '+str(ZO),
            'port 1 ZI 1 2 ZI 2 3 ZO 1 4 ZO 2',
            'connect ZI 1 D 2','connect ZI 2 D 1',
            'connect ZO 1 D 4','connect ZO 2 D 3'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransconductanceAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transconductance Amplifier Four Port incorrect')
    def testTransconductanceAmplifierFourPortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=4000 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device D 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 ZI 2 3 ZO 1 4 ZO 2',
            'connect ZI 1 D 2','connect ZI 2 D 1',
            'connect ZO 1 D 4','connect ZO 2 D 3'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.VoltageControlledCurrentSource(G))
        sspn.AssignSParameters('ZI',si.dev.SeriesZ(ZI))
        sspn.AssignSParameters('ZO',si.dev.SeriesZ(ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransconductanceAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transconductance Amplifier Four Port incorrect')
    def testTransconductanceAmplifierFourPortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=4000 # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device D 4 transconductanceamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2 3 D 3 4 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransconductanceAmplifier(4,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transconductance Amplifier Four Port incorrect')
    def testTransconductanceAmplifierThreePort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4',
            'port 1 D 1 2 D 3 3 D 2',
            'connect D 2 D 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('D',si.sy.TransconductanceAmplifier(4,'\\delta','Z_i','Z_o'))
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transconductance Amplifier Three Port')
    def testTransconductanceAmplifierThreePortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','port 1 D 1 2 D 2 3 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small',
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
        ssps.AssignSParameters('D',si.sy.TransconductanceAmplifier(3,'\\delta','Z_i','Z_o'))
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transconductance Amplifier Three Port Symbolic')
    def testTransconductanceAmplifierThreePortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=4000. # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device D 4 transconductanceamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 3 3 D 2',
            'connect D 2 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransconductanceAmplifierThreePort(G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transconductance Amplifier Three Port incorrect')
    def testTransconductanceAmplifierThreePortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=4000. # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device D 4',
            'port 1 D 1 2 D 3 3 D 2',
            'connect D 2 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.TransconductanceAmplifierFourPort(G,ZI,ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransconductanceAmplifierThreePort(G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transconductance Amplifier Three Port incorrect')
    def testTransconductanceAmplifierThreePortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=4000. # Zin
        ZO=2000 # Zout
        sdp.AddLines(['device D 3 transconductanceamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2 3 D 3'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransconductanceAmplifier(3,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transconductance Amplifier Three Port incorrect')
    def testTransconductanceAmplifierTwoPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device G1 1 ground','device G2 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 G1 1','connect D 4 G2 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        D=si.sy.TransconductanceAmplifier(4,'\\delta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transconductance Amplifier Two Port Full')
    def testTransconductanceAmplifierTwoPortAlternate(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','device G 1 ground',
            'port 1 D 1 2 D 2',
            'connect D 3 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        D=si.sy.TransconductanceAmplifier(3,'\\delta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transconductance Amplifier Two Port Alternate')
    def testTransconductanceAmplifierTwoPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2',
            'port 1 D 1 2 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
        D=si.sy.TransconductanceAmplifierTwoPort('\\delta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transconductance Amplifier Two Port Symbolic')
    def testTransconductanceAmplifierTwoPortNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=6000. # Zout
        sdp.AddLines(['device D 4 transconductanceamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'device G 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 D 4 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransconductanceAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transconductance Amplifier Two Port incorrect')
    def testTransconductanceAmplifierTwoPortNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=6000. # Zout
        sdp.AddLines(['device D 4',
            'device G 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 D 4 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.AssignSParameters('D',si.dev.TransconductanceAmplifier(4,G,ZI,ZO))
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransconductanceAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transconductance Amplifier Two Port incorrect')
    def testTransconductanceAmplifierTwoPortNumeric3(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=6000. # Zout
        sdp.AddLines(['device D 2 transconductanceamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'port 1 D 1 2 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransconductanceAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transconductance Amplifier Two Port incorrect')
    def testTransconductanceAmplifierFourPortCode(self):
        self.WriteCode('TestTransconductanceAmplifier.py','testTransconductanceAmplifierFourPort(self)',self.standardHeader)
    def testTransconductanceAmplifierThreePortCode(self):
        self.WriteCode('TestTransconductanceAmplifier.py','testTransconductanceAmplifierThreePort(self)',self.standardHeader)
    def testTransconductanceAmplifierThreePortAlternateCode(self):
        self.WriteCode('TestTransconductanceAmplifier.py','testTransconductanceAmplifierThreePortAlternate(self)',self.standardHeader)
    def testTransconductanceAmplifierTwoPortCode(self):
        self.WriteCode('TestTransconductanceAmplifier.py','testTransconductanceAmplifierTwoPort(self)',self.standardHeader)
    def testTransconductanceAmplifierTwoPortAlternateCode(self):
        self.WriteCode('TestTransconductanceAmplifier.py','testTransconductanceAmplifierTwoPortAlternate(self)',self.standardHeader)

if __name__ == '__main__':
    unittest.main()
