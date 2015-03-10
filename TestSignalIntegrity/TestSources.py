import unittest

import os
from cStringIO import StringIO
import sys
import SignalIntegrity as si
from numpy import linalg
from numpy import matrix

class TestSources(unittest.TestCase):
    def CheckSymbolicResult(self,selfid,symbolic,Text):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileName = '_'.join(selfid.split('.')) + '.tex'
        fileName = ('_'.join(selfid.split('.')[2:])).replace('test','') + '.tex'
        if not os.path.exists(fileName):
            symbolic.WriteToFile(fileName)
            self.assertTrue(False, fileName + ' not found')
        regression=''
        with open(fileName, 'rU') as regressionFile:
            for line in regressionFile:
                regression = regression + line
        comparison = symbolic.Get()
        self.assertTrue(regression == comparison,Text + ' incorrect with ' + fileName)
    def testVoltageAmplifierFourPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 ZI 2 3 ZO 2 4 DV 3',
            'connect ZI 1 DV 2','connect ZI 2 DV 1','connect ZO 1 DV 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
        ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXBlockSolutionBig().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Four Port')
    def testVoltageAmplifierFourPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4',
            'port 1 DV 1 2 DV 2 3 DV 3 4 DV 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,False)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        ssps.AssignSParameters('DV',si.sy.VoltageAmplifierFourPort('\\alpha','Z_i','Z_o'))
        ssps.LaTeXBlockSolution().Emit()
        # exclude
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
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DV',si.sy.VoltageAmplifierFourPort('\\alpha','Z_i','Z_o'))
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Three Port')
    def testVoltageAmplifierThreePortAlternate(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 3 ZI 2 2 ZO 2',
            'connect ZI 1 DV 2','connect ZI 2 DV 1','connect ZO 1 DV 4','connect DV 3 DV 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
        ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Three Port')
    def testVoltageAmplifierThreePortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 3',
            'port 1 DV 1 2 DV 2 3 DV 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        ssps.AssignSParameters('DV',si.sy.VoltageAmplifierThreePort('\\alpha','Z_i','Z_o'))
        ssps.LaTeXBlockSolution().Emit()
        # exclude
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
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
        ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXBlockSolutionBig().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier 2 Full')
    def testVoltageAmplifierTwoPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device G 1 ground',
            'port 1 DV 1 2 DV 3',
            'connect DV 2 G 1','connect DV 4 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        DV=si.sy.VoltageAmplifier(4,'\\alpha','Z_i','Z_o')
        ssps.AssignSParameters('DV',DV)
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Two Port Full')
    def testVoltageAmplifierTwoPortAlternate(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 3','device G 1 ground',
            'port 1 DV 1 2 DV 2',
            'connect DV 3 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        DV=si.sy.VoltageAmplifier(3,'\\alpha','Z_i','Z_o')
        ssps.AssignSParameters('DV',DV)
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Two Port Alternate')
    def testVoltageAmplifierTwoPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 2',
            'port 1 DV 1 2 DV 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,False)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        DV=si.sy.VoltageAmplifierTwoPort('\\alpha','Z_i','Z_o')
        ssps.AssignSParameters('DV',DV)
        ssps.LaTeXBlockSolution().Emit()
        # exclude
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
    def testSymbolicTransistorSimple(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DC 4',
            'device HIE 2',
            'port 1 HIE 1 2 DC 4 3 DC 3',
            'connect HIE 2 DC 1',
            'connect DC 2 DC 4'])
        # exclude
        # sdp.WriteToFile('TransistorSimpleNetList.txt',False)
        # include
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('\\beta'))
        ssps.AssignSParameters('HIE',si.sy.SeriesZ('h_{ie}'))
        ssps.LaTeXBlockSolutionBig().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Simple Transistor')
    def testSymbolicTransistorZO(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DC 4',
            'device HIE 2',
            'device ZO 2',
            'port 1 HIE 1 2 DC 4 3 DC 3',
            'connect HIE 2 DC 1',
            'connect DC 2 DC 4',
            'connect ZO 1 DC 3',
            'connect ZO 2 DC 4'])
        # exclude
        # sdp.WriteToFile('TransistorSimpleNetList.txt',False)
        # include
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('\\beta'))
        ssps.AssignSParameters('HIE',si.sy.SeriesZ('Z_{\\pi}'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXBlockSolutionBig().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transistor Zo')
    def testOperationalAmplifier(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4',
            'device ZI1 2',
            'device ZI2 2',
            'device ZO 2',
            'device ZD 2',
            'device G 1 ground',
            'port 1 ZI1 1',
            'port 2 ZI2 1',
            'port 3 ZO 2',
            'connect DV 3 G 1',
            'connect ZI1 1 DV 2',
            'connect ZI2 1 DV 1',
            'connect ZI1 2 G 1',
            'connect ZI2 2 G 1',
            'connect ZD 1 ZI1 1',
            'connect ZD 2 ZI2 1',
            'connect ZO 1 DV 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
        ssps.AssignSParameters('ZI1',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZI2',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZD',si.sy.SeriesZ('Z_d'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXBlockSolutionBig().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier 3')
    def testOperationalAmplifierNoZD(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4',
            'device ZI1 2',
            'device ZI2 2',
            'device ZO 2',
            'device G 1 ground',
            'port 1 ZI1 1',
            'port 2 ZI2 1',
            'port 3 ZO 2',
            'connect DV 3 G 1',
            'connect ZI1 1 DV 2',
            'connect ZI2 1 DV 1',
            'connect ZI1 2 G 1',
            'connect ZI2 2 G 1',
            'connect ZO 1 DV 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
        ssps.AssignSParameters('ZI1',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZI2',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXBlockSolutionBig().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier 3')
    def testOperationalAmplifierAgain(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device VA 4',
            'device ZI1 2',
            'device ZI2 2',
            'device G 1 ground',
            'port 1 ZI1 1',
            'port 2 ZI2 1',
            'port 3 VA 3',
            'connect VA 4 G 1',
            'connect ZI1 1 VA 1',
            'connect ZI2 1 VA 2',
            'connect ZI1 2 G 1',
            'connect ZI2 2 G 1'])
        si.sy.SymbolicMatrix(si.sy.SeriesZ('Z_i'),'ZI1 = ZI2',True).Emit()
        si.sy.SymbolicMatrix(si.sy.VoltageAmplifierFourPort('G','Z_d','Z_o'),'VA',True).Emit()
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.LaTeXBlockSolutionBig().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Operational Amplifier Again')
    def testIdealTransformerSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4',
            'device DC 4',
            'port 1 DC 4',
            'port 2 DC 3',
            'port 3 DC 1',
            'port 4 DV 3',
            'connect DC 2 DV 4',
            'connect DC 4 DV 2',
            'connect DC 3 DV 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('a'))
        ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('a'))
        ssps.LaTeXBlockSolutionBig().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Ideal Transformer')
    def testIdealTransformerSymbolic2(self):
        sm = si.sy.SymbolicMatrix(si.sy.IdealTransformer('a'))
        self.CheckSymbolicResult(self.id(),sm,'Ideal Transformer')
    def testIdealTransformerNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        a=10 #turns ratio for ideal transformer
        sdp.AddLines(['device DV 4 voltagecontrolledvoltagesource '+str(a),
            'device DC 4 currentcontrolledcurrentsource '+str(a),
            'port 1 DC 4',
            'port 2 DC 3',
            'port 3 DC 1',
            'port 4 DV 3',
            'connect DC 2 DV 4',
            'connect DC 4 DV 2',
            'connect DC 3 DV 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.IdealTransformer(a)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Ideal Transformer incorrect')
        pass
    def testIdealTransformerNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        a=10 #turns ratio for ideal transformer
        sdp.AddLines(['device D 4 idealtransformer '+str(a),
            'port 1 D 1',
            'port 2 D 2',
            'port 3 D 3',
            'port 4 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.IdealTransformer(a)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Ideal Transformer incorrect')
        pass
    def testVoltageAmplifierTwoPortVoltageSeriesFeedbackAlternate(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device V 4','device F 4','device G 1 ground',
                      'port 1 V 1 2 V 3',
                      'connect V 2 F 3','connect F 4 G 1','connect V 3 F 1',
                      'connect V 4 G 1','connect F 2 G 1'])
        si.sy.SymbolicMatrix(si.sy.VoltageAmplifierFourPort('A','Z_i','Z_o'),'\\mathbf{V}',True).Emit()
        si.sy.SymbolicMatrix(si.sy.VoltageAmplifierFourPort('B','Z_{if}','Z_{of}'),'\\mathbf{F}',True).Emit()
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.LaTeXBlockSolutionBig().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Two Port Voltage Series Feedback')
    def testVoltageAmplifierTwoPortVoltageSeriesFeedback(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device F 2','device G 1 ground',
            'port 1 D 1 2 D 3',
            'connect D 2 F 2','connect D 3 F 1','connect D 4 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('D',si.sy.VoltageAmplifier(4,'\\alpha','Z_i','Z_o'))
        ssps.AssignSParameters('F',si.sy.VoltageAmplifier(2,'\\beta','Z_{if}','Z_{of}'))
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Two Port Voltage Series Feedback')
    def testVoltageAmplifierFourPortVoltageSeriesFeedback(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device F 4',
            'port 1 D 1 2 F 4 3 D 3 4 F 2',
            'connect D 2 F 3','connect D 3 F 1','connect D 4 F 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        DSp=ssps[ssps.IndexOfDevice('D')].pSParameters
        DSp[1][1]=DSp[0][0]
        DSp[1][0]=DSp[0][1]
        DSp[0][2]=0
        DSp[0][3]=0
        DSp[1][2]=0
        DSp[1][3]=0
        DSp[2][1]='-'+DSp[2][0]
        DSp[3][0]='-'+DSp[2][0]
        DSp[3][1]=DSp[2][0]
        DSp[3][2]=DSp[2][3]
        DSp[3][3]=DSp[2][2]
        si.sy.SymbolicMatrix(si.helper.Matrix2Text(DSp),'\\mathbf{D}',True).Emit()
        DSp=ssps[ssps.IndexOfDevice('F')].pSParameters
        DSp[1][1]=DSp[0][0]
        DSp[1][0]=DSp[0][1]
        DSp[0][2]=0
        DSp[0][3]=0
        DSp[1][2]=0
        DSp[1][3]=0
        DSp[2][1]='-'+DSp[2][0]
        DSp[3][0]='-'+DSp[2][0]
        DSp[3][1]=DSp[2][0]
        DSp[3][2]=DSp[2][3]
        DSp[3][3]=DSp[2][2]
        si.sy.SymbolicMatrix(si.helper.Matrix2Text(DSp),'\\mathbf{F}',True).Emit()
        si.sy.SymbolicMatrix(si.sy.VoltageAmplifierFourPort('\\alpha','Z_i','Z_o'),'\\mathbf{D}',True).Emit()
        si.sy.SymbolicMatrix(si.sy.VoltageAmplifierFourPort('\\beta','Z_{if}','Z_{of}'),'\\mathbf{F}',True).Emit()
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Four Port Voltage Series Feedback')
    def testVoltageAmplifierFourPortVoltageSeriesFeedbackAlternate(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device F 4',
            'port 1 D 1 2 F 4 3 D 3 4 F 2',
            'connect D 2 F 3','connect D 3 F 1','connect D 4 F 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        DSp=ssps[ssps.IndexOfDevice('D')].pSParameters
        DSp[1][1]=DSp[0][0]
        DSp[1][0]=DSp[0][1]
        DSp[0][2]=0
        DSp[0][3]=0
        DSp[1][2]=0
        DSp[1][3]=0
        DSp[2][1]='-'+DSp[2][0]
        DSp[3][0]='-'+DSp[2][0]
        DSp[3][1]=DSp[2][0]
        DSp[3][2]=DSp[2][3]
        DSp[3][3]=DSp[2][2]
        DS=si.sy.VoltageAmplifierFourPort('\\alpha','Z_i','Z_o')
        si.sy.SymbolicMatrix([DS[0][0]],'D_{11}',True).Emit()
        si.sy.SymbolicMatrix([DS[0][1]],'D_{12}',True).Emit()
        si.sy.SymbolicMatrix([DS[2][0]],'D_{31}',True).Emit()
        si.sy.SymbolicMatrix([DS[2][2]],'D_{33}',True).Emit()
        si.sy.SymbolicMatrix([DS[2][3]],'D_{34}',True).Emit()
        # exclude
        #si.sy.SymbolicMatrix(si.helper.Matrix2Text(DSp),'\\mathbf{D}',True).Emit()
        # include
        DSp=ssps[ssps.IndexOfDevice('F')].pSParameters
        DSp[1][1]=DSp[0][0]
        DSp[1][0]=DSp[0][1]
        DSp[0][2]=0
        DSp[0][3]=0
        DSp[1][2]=0
        DSp[1][3]=0
        DSp[2][1]='-'+DSp[2][0]
        DSp[3][0]='-'+DSp[2][0]
        DSp[3][1]=DSp[2][0]
        DSp[3][2]=DSp[2][3]
        DSp[3][3]=DSp[2][2]
        FS=si.sy.VoltageAmplifierFourPort('\\beta','Z_{if}','Z_{of}')
        si.sy.SymbolicMatrix([FS[0][0]],'F_{11}',True).Emit()
        si.sy.SymbolicMatrix([FS[0][1]],'F_{12}',True).Emit()
        si.sy.SymbolicMatrix([FS[2][0]],'F_{31}',True).Emit()
        si.sy.SymbolicMatrix([FS[2][2]],'F_{33}',True).Emit()
        si.sy.SymbolicMatrix([FS[2][3]],'F_{34}',True).Emit()
        # exclude
        # si.sy.SymbolicMatrix(si.helper.Matrix2Text(DSp),'\\mathbf{F}',True).Emit()
        # include
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier Four Port Voltage Series Feedback')
    def testCurrentAmplifierFourPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DC 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 DC 2 3 DC 4 4 DC 3',
            'connect ZI 2 DC 1','connect ZO 1 DC 4','connect ZO 2 DC 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('\\beta'))
        ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXBlockSolutionBig().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Four Port')
    def testCurrentAmplifierFourPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DC 4','port 1 DC 1 2 DC 2 3 DC 3 4 DC 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,False)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        ssps.AssignSParameters('DC',si.sy.CurrentAmplifierFourPort('\\beta','Z_i','Z_o'))
        ssps.LaTeXBlockSolution().Emit()
        # exclude
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
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('D',si.sy.CurrentAmplifier(4,'\\beta','Z_i','Z_o'))
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Three Port')
    def testCurrentAmplifierThreePortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','port 1 D 1 2 D 2 3 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        ssps.AssignSParameters('D',si.sy.CurrentAmplifier(3,'\\beta','Z_i','Z_o'))
        ssps.LaTeXBlockSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Three Port Symbolic')
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
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        D=si.sy.CurrentAmplifier(4,'\\beta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Two Port Full')
    def testCurrentAmplifierTwoPortAlternate(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','device G 1 ground',
            'port 1 D 1 2 D 2',
            'connect D 3 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        D=si.sy.CurrentAmplifier(3,'\\beta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current Amplifier Two Port Alternate')
    def testCurrentAmplifierTwoPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2',
            'port 1 D 1 2 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,False)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        D=si.sy.CurrentAmplifierTwoPort('\\beta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXBlockSolution().Emit()
        # exclude
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
    def testTransconductanceAmplifierFourPort(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 ZI 2 3 ZO 1 4 ZO 2',
            'connect ZI 1 D 2','connect ZI 2 D 1',
            'connect ZO 1 D 4','connect ZO 2 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('D',si.sy.VoltageControlledCurrentSource('\\delta'))
        ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXBlockSolutionBig().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transconductance Amplifier Four Port')
    def testTransconductanceAmplifierFourPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 4','port 1 D 1 2 D 2 3 D 3 4 D 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,False)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        ssps.AssignSParameters('D',si.sy.TransconductanceAmplifierFourPort('\\delta','Z_i','Z_o'))
        ssps.LaTeXBlockSolution().Emit()
        # exclude
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
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('D',si.sy.TransconductanceAmplifier(4,'\\delta','Z_i','Z_o'))
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transconductance Amplifier Three Port')
    def testTransconductanceAmplifierThreePortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','port 1 D 1 2 D 2 3 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        ssps.AssignSParameters('D',si.sy.TransconductanceAmplifier(3,'\\delta','Z_i','Z_o'))
        ssps.LaTeXBlockSolution().Emit()
        # exclude
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
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        D=si.sy.TransconductanceAmplifier(4,'\\delta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transconductance Amplifier Two Port Full')
    def testTransconductanceAmplifierTwoPortAlternate(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','device G 1 ground',
            'port 1 D 1 2 D 2',
            'connect D 3 G 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        D=si.sy.TransconductanceAmplifier(3,'\\delta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXBlockSolutionBiggest().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transconductance Amplifier Two Port Alternate')
    def testTransconductanceAmplifierTwoPortSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2',
            'port 1 D 1 2 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,False)
        ssps.m_eqPrefix='\\begin{equation} '
        ssps.m_eqSuffix=' \\end{equation}'
        D=si.sy.TransconductanceAmplifierTwoPort('\\delta','Z_i','Z_o')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXBlockSolution().Emit()
        # exclude
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
    def testTransconductanceAmplifierTwoPortAlternateNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        G=10. # gain
        ZI=1000. # Zin
        ZO=6000. # Zout
        sdp.AddLines(['device D 3 transconductanceamplifier gain '+str(G)+' zi '+str(ZI)+' zo '+str(ZO),
            'device G 1 ground',
            'port 1 D 1 2 D 2',
            'connect D 3 G 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.TransconductanceAmplifier(2,G,ZI,ZO)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Transconductance Amplifier Two Port Alternate incorrect')
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


if __name__ == '__main__':
    unittest.main()

