import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import matrix
from TestHelpers import *

class TestTransistor(unittest.TestCase,SourcesTesterHelper,RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
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
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('\\beta'))
        ssps.AssignSParameters('HIE',si.sy.SeriesZ('h_{ie}'))
        ssps.LaTeXSolution(size='big').Emit()
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
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('\\beta'))
        ssps.AssignSParameters('HIE',si.sy.SeriesZ('Z_{\\pi}'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXSolution(size='big').Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transistor Zo')
    def testSymbolicTransistorSimpleCode(self):
        self.WriteCode('TestTransistor.py','testSymbolicTransistorSimple(self)',self.standardHeader)
    def testSymbolicTransistorZoCode(self):
        self.WriteCode('TestTransistor.py','testSymbolicTransistorZO(self)',self.standardHeader)

if __name__ == '__main__':
    unittest.main()

