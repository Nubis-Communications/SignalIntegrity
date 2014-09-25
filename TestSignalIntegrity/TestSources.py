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
        with open(fileName, 'r') as regressionFile:
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
        # exclude
        sdp.WriteToFile('VoltageAmplifier4.txt',False)
        # include
        sd = sdp.SystemDescription()
        sd.AssignSParameters('DV',
            [['1','0','0','0'],
            ['0','1','0','0'],
            ['\\alpha','-\\alpha','0','1'],
            ['-\\alpha','\\alpha','1','0']])
        sd.AssignSParameters('ZI',
            [['\\frac{Z_i}{Z_i+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_i+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{Z_i+2\\cdot Z0}','\\frac{Z_i}{Z_i+2\\cdot Z0}']])
        sd.AssignSParameters('ZO',
            [['\\frac{Z_o}{Z_o+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_o+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{Z_o+2\\cdot Z0}','\\frac{Z_o}{Z_o+2\\cdot Z0}']])
        ssp=si.sd.SystemSParameters(sdp.SystemDescription())
        ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
        ssps.LaTeXBigSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier 4')
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
            [['1','0','0','0'],
            ['0','1','0','0'],
            ['\\alpha','-\\alpha','0','1'],
            ['-\\alpha','\\alpha','1','0']])
        sd.AssignSParameters('ZI',
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
        # exclude
        sdp.WriteToFile('VoltageAmplifier2Full.txt',False)
        # include
        sd = sdp.SystemDescription()
        sd.AssignSParameters('DV',
            [['1','0','0','0'],
            ['0','1','0','0'],
            ['\\alpha','-\\alpha','0','1'],
            ['-\\alpha','\\alpha','1','0']])
        sd.AssignSParameters('ZI',
            [['\\frac{Z_i}{Z_i+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_i+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{Z_i+2\\cdot Z0}','\\frac{Z_i}{Z_i+2\\cdot Z0}']])
        sd.AssignSParameters('ZO',
            [['\\frac{Z_o}{Z_o+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_o+2\\cdot Z0}'],
            ['\\frac{2\\cdot Z0}{Z_o+2\\cdot Z0}','\\frac{Z_o}{Z_o+2\\cdot Z0}']])
        ssp=si.sd.SystemSParameters(sd)
        ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
        ssps.LaTeXBigSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Voltage Amplifier 2 Full')

if __name__ == '__main__':
    unittest.main()

