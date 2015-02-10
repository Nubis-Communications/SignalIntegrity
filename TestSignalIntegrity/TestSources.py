import unittest

import os
from cStringIO import StringIO
import sys
import SignalIntegrity as si

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
        sd = sdp.SystemDescription()
        sd.AssignSParameters('DV',
            si.sy.VoltageControlledVoltageSource('\\alpha'))
        sd.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        sd.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssp=si.sd.SystemSParameters(sdp.SystemDescription())
        ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
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
        sd = sdp.SystemDescription()
        sd.AssignSParameters('DV',
            si.sy.VoltageAmplifierFourPort('\\alpha','Z_i','Z_o'))
        ssp=si.sd.SystemSParameters(sdp.SystemDescription())
        ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
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
        sd = sdp.SystemDescription()
        sd.AssignSParameters('DV',
            si.sy.VoltageControlledVoltageSource('\\alpha'))
        sd.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        sd.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssp=si.sd.SystemSParameters(sdp.SystemDescription())
        ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
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
        sd = sdp.SystemDescription()
        sd.AssignSParameters('DV',
            si.sy.VoltageControlledVoltageSource('\\alpha'))
        sd.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
        sd.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssp=si.sd.SystemSParameters(sd)
        ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
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
        sd = sdp.SystemDescription()
        sd.AssignSParameters('DC',
            [['0','1','0','0'],
            ['1','0','0','0'],
            ['-\\beta','\\beta','1','0'],
            ['\\beta','-\\beta','0','1']])
        sd.AssignSParameters('HIE',
            [['\\frac{h_{ie}}{h_{ie}+2\\cdot Z0}','\\frac{2\\cdot Z0}{h_{ie}+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{h_{ie}+2\\cdot Z0}','\\frac{h_{ie}}{h_{ie}+2\\cdot Z0}']])
        ssp=si.sd.SystemSParameters(sd)
        ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
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
        sd = sdp.SystemDescription()
        sd.AssignSParameters('DC',
            [['0','1','0','0'],
            ['1','0','0','0'],
            ['-\\beta','\\beta','1','0'],
            ['\\beta','-\\beta','0','1']])
        sd.AssignSParameters('HIE',
            [['\\frac{Z_{\pi}}{Z_{\pi}+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_{\pi}+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{Z_{\pi}+2\\cdot Z0}','\\frac{Z_{\pi}}{Z_{\pi}+2\\cdot Z0}']])
        sd.AssignSParameters('ZO',
            [['\\frac{Z_o}{Z_o+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_o+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{Z_o+2\\cdot Z0}','\\frac{Z_o}{Z_o+2\\cdot Z0}']])
        ssp=si.sd.SystemSParameters(sd)
        ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
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
        sd = sdp.SystemDescription()
        sd.AssignSParameters('DV',
            [['1','0','0','0'],
            ['0','1','0','0'],
            ['\\alpha','-\\alpha','0','1'],
            ['-\\alpha','\\alpha','1','0']])
        sd.AssignSParameters('ZI1',
            [['\\frac{Z_i}{Z_i+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_i+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{Z_i+2\\cdot Z0}','\\frac{Z_i}{Z_i+2\\cdot Z0}']])
        sd.AssignSParameters('ZI2',
            [['\\frac{Z_i}{Z_i+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_i+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{Z_i+2\\cdot Z0}','\\frac{Z_i}{Z_i+2\\cdot Z0}']])
        sd.AssignSParameters('ZD',
            [['\\frac{Z_d}{Z_d+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_d+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{Z_d+2\\cdot Z0}','\\frac{Z_d}{Z_d+2\\cdot Z0}']])
        sd.AssignSParameters('ZO',
            [['\\frac{Z_o}{Z_o+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_o+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{Z_o+2\\cdot Z0}','\\frac{Z_o}{Z_o+2\\cdot Z0}']])
        ssp=si.sd.SystemSParameters(sdp.SystemDescription())
        ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
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
        sd = sdp.SystemDescription()
        sd.AssignSParameters('DV',
            [['1','0','0','0'],
            ['0','1','0','0'],
            ['\\alpha','-\\alpha','0','1'],
            ['-\\alpha','\\alpha','1','0']])
        sd.AssignSParameters('ZI1',
            [['\\frac{Z_i}{Z_i+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_i+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{Z_i+2\\cdot Z0}','\\frac{Z_i}{Z_i+2\\cdot Z0}']])
        sd.AssignSParameters('ZI2',
            [['\\frac{Z_i}{Z_i+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_i+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{Z_i+2\\cdot Z0}','\\frac{Z_i}{Z_i+2\\cdot Z0}']])
        sd.AssignSParameters('ZO',
            [['\\frac{Z_o}{Z_o+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_o+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{Z_o+2\\cdot Z0}','\\frac{Z_o}{Z_o+2\\cdot Z0}']])
        ssp=si.sd.SystemSParameters(sdp.SystemDescription())
        ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
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
        sd = sdp.SystemDescription()
        sd.AssignSParameters('VA',si.sd.Device.SymbolicMatrix('VA',4))
        sd.AssignSParameters('ZI1',si.sd.Device.SymbolicMatrix('ZI1',2))
        sd.AssignSParameters('ZI2',si.sd.Device.SymbolicMatrix('ZI2',2))
        ssp=si.sd.SystemSParameters(sdp.SystemDescription())
        ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
        print '\[ ZI1 = ZI2 = '+ si.helper.Matrix2LaTeX(si.sy.SeriesZ('Z_i')) + ' \]'
        print '\[ VA = ' + si.helper.Matrix2LaTeX(si.sy.VoltageAmplifierFourPort('G','Z_d','Z_o')) + ' \]'
        ssps.LaTeXBigSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Operational Amplifier Again')

if __name__ == '__main__':
    unittest.main()

