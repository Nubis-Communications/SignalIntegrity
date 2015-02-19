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
        self.assertTrue(regression == comparison,Text + ' incorrect')
    def testVoltageAmplifier4(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4',
            'device ZI 2',
            'device ZO 2',
            'port 1 ZI 1',
            'port 2 ZI 2',
            'port 3 ZO 2',
            'port 4 DV 3',
            'connect ZI 1 DV 2',
            'connect ZI 2 DV 1',
            'connect ZO 1 DV 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
        ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXBigSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier 4')
    def testVoltageAmplifier4Symbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4',
            'port 1 DV 1',
            'port 2 DV 2',
            'port 3 DV 3',
            'port 4 DV 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DV',si.sy.VoltageAmplifierFourPort('\\alpha','Z_i','Z_o'))
        ssps.LaTeXSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier 4 Symbolic')
    def testVoltageAmplifier3(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4',
            'device ZI 2',
            'device ZO 2',
            'device G 1 ground',
            'port 1 ZI 1',
            'port 2 ZI 2',
            'port 3 ZO 2',
            'connect DV 3 G 1',
            'connect ZI 1 DV 2',
            'connect ZI 2 DV 1',
            'connect ZO 1 DV 4'])
        sdp.WriteToFile('VoltageAmplifier3.txt',False)
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
        ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXBigSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier 3')
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
        ssps.LaTeXBigSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier 2 Full')
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
        ssps.LaTeXBigSolution().Emit()
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
        ssps.LaTeXBigSolution().Emit()
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
        ssps.LaTeXBigSolution().Emit()
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
        ssps.LaTeXBigSolution().Emit()
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
        ssps.LaTeXBigSolution().Emit()
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
        ssps.LaTeXBigSolution().Emit()
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

if __name__ == '__main__':
    unittest.main()

