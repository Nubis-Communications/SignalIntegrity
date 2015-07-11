import unittest
import os
from cStringIO import StringIO
import sys
import SignalIntegrity as si
from TestHelpers import *

class Test(unittest.TestCase,RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def CheckSymbolicResult(self,selfid,symbolic,Text):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileName = '_'.join(selfid.split('.')) + '.tex'
        if not os.path.exists(fileName):
            symbolic.WriteToFile(fileName)
            self.assertTrue(False, fileName + ' not found')
        regression=''
        with open(fileName, 'rU') as regressionFile:
            for line in regressionFile:
                regression = regression + line
        comparison = symbolic.Get()
        self.assertTrue(regression == comparison,Text + ' incorrect')
    def testSymbolicSimulatorExample3(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('C',4)
        sd.AddDevice('R',2)
        sd.ConnectDevicePort('C',3,'R',1)
        sd.ConnectDevicePort('C',4,'R',2)
        vp=si.sd.Simulator(sd)
        vp.AddVoltageSource('v1',2)
        vp.ConnectDevicePort('v1',1,'C',1)
        vp.ConnectDevicePort('v1',2,'C',2)
        vp.pOutputList = [('R',1),('R',2)]
        svp=si.sd.SimulatorSymbolic(vp)
        svp.DocStart().LaTeXTransferMatrix().DocEnd().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),svp,'Symbolic Simulator 1')
    def testSymbolicSimulatorExample3p5(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('C',4)
        sd.AddDevice('R',2)
        sd.ConnectDevicePort('C',3,'R',1)
        sd.ConnectDevicePort('C',4,'R',2)
        vp=si.sd.Simulator(sd)
        vp.AddVoltageSource('v1',2)
        vp.AddDevice('G',1,si.dev.Ground())
        vp.ConnectDevicePort('v1',1,'C',1)
        vp.ConnectDevicePort('v1',2,'C',2)
        vp.ConnectDevicePort('v1',1,'G',1)
        vp.pOutputList = [('R',1),('R',2)]
        svp=si.sd.SimulatorSymbolic(vp)
        svp.DocStart().LaTeXTransferMatrix().DocEnd().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),svp,'Symbolic Simulator 1')
    def testSymbolicSimulatorExample4(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('C',4)
        sd.AddDevice('R',2)
        sd.ConnectDevicePort('C',3,'R',1)
        sd.ConnectDevicePort('C',4,'R',2)
        vp=si.sd.Simulator(sd)
        vp.AddVoltageSource('v1',1)
        vp.AddCurrentSource('i1',1)
        vp.ConnectDevicePort('v1',1,'C',1)
        vp.ConnectDevicePort('i1',1,'C',2)
        vp.pOutputList = [('R',1),('R',2)]
        svp=si.sd.SimulatorSymbolic(vp)
        svp.DocStart().LaTeXTransferMatrix().DocEnd().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),svp,'Symbolic Simulator 1')
    def testSimulatorParser(self):
        f=si.fd.EvenlySpacedFrequencyList(20.e9,2000)
        sp = si.p.SimulatorNumericParser(f)
        sp.AddLine('device F 2 file filter.s2p')
        sp.AddLine('device S 2 R 50.')
        sp.AddLine('device R 2 R 50.')
        sp.AddLine('device G 1 ground')
        sp.AddLine('voltagesource V 1')
        sp.AddLine('connect V 1 S 1')
        sp.AddLine('connect S 2 F 1')
        sp.AddLine('connect F 2 R 1')
        sp.AddLine('connect R 2 G 1')
        sp.AddLine('output R 1')
        sp.TransferMatrices().WriteToFile('SimulatorParser.s1p')
if __name__ == "__main__":
    unittest.main()
