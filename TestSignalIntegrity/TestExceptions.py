import unittest

import SignalIntegrity as si

class TestExceptions(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
    def testSystemDescriptionCheckConnections(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 ZI 2 3 ZO 2 4 DV 3',
            'connect ZI 1 DV 2','connect ZI 2 DV 1'])
        sdp.SystemDescription().Print()
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        try:
            ssps.LaTeXSolution().Emit()
        except si.PySIException as e:
            if e.parameter == 'CheckConnections':
                pass
        # exclude
    def testSystemDescriptionCheckConnections2(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 ZI 2 3 ZO 2 4 DV 3',
            'connect ZI 1 DV 2','connect ZI 2 DV 1'])
        sdp.SystemDescription().Print()
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        with self.assertRaises(si.PySIException) as cm:
            ssps.LaTeXSolution().Emit()
        self.assertEqual(cm.exception.parameter,'CheckConnections')
        # exclude
    def testSystemDescriptionWrongDevice(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 ZI 2 3 ZO 2 4 DV 3',
            'connect Z 1 DV 2','connect ZI 2 DV 1'])
        sdp.SystemDescription().Print()
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        with self.assertRaises(si.PySIException) as cm:
            ssps.LaTeXSolution().Emit()
        self.assertEqual(cm.exception.parameter,'CheckConnections')
        # exclude

if __name__ == '__main__':
    unittest.main()

