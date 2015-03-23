import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import matrix
from TestHelpers import *

class TestOperationalAmplifier(unittest.TestCase,SourcesTesterHelper,RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
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
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
        ssps.AssignSParameters('ZI1',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZI2',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZD',si.sy.SeriesZ('Z_d'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXSolution(size='big').Emit()
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
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
        ssps.AssignSParameters('ZI1',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZI2',si.sy.SeriesZ('Z_i'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXSolution(size='big').Emit()
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
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.LaTeXSolution(size='big').Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Operational Amplifier Again')
    def testOpAmpNoZD(self):
        self.WriteCode('TestOperationalAmplifier.py','testOperationalAmplifierNoZD(self)',self.standardHeader)
    def testOpAmpAgain(self):
        self.WriteCode('TestOperationalAmplifier.py','testOperationalAmplifierAgain(self)',self.standardHeader)

if __name__ == '__main__':
    unittest.main()

