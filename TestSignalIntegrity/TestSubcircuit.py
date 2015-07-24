import unittest
import os
from cStringIO import StringIO
import sys
import SignalIntegrity as si
from TestHelpers import *
from numpy import matrix

class TestSubcircuit(unittest.TestCase,RoutineWriterTesterHelper,ResponseTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testSubCircuitNetlistGenerator1(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['var Rsh 50.','device R 2 R Rsh',
            'port 1 R 2 2 R 2 3 R 1'])
        sdp.WriteToFile('ShuntZFourPort.sub')
    def testSubCircuitUserNetlistGenerator1(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3 subcircuit ShuntZFourPort.sub Rsh 25.',
                      'device G 1 ground','connect D 3 G 1',
                      'port 1 D 1 2 D 2'])
        sdp.WriteToFile('SubCircuitExample1.txt')
    def testSubCircuitExample1(self):
        fl=[0.]
        sspnp = si.p.SystemSParametersNumericParser(fl).File('SubCircuitExample1.txt')
        sp=sspnp.SParameters()
        print matrix(sp[0])
    def testSubCircuitCorrectAnswer1(self):
        print matrix(si.dev.ShuntZ(2, 25.))
    def testSubCircuitNetlistGenerator2(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines([
            'var DL thru DR thru',
            'device L 2 DL','device R 2 DR',
            'port 1 L 1 2 R 2','connect L 2 R 1'])
        sdp.WriteToFile('cascade.sub')
    def testSubCircuitUserNetlistGenerator2(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2 subcircuit cascade.sub DL \'file cable.s2p\' DR \'file filter.s2p\'',
                      'port 1 D 1 2 D 2'])
        sdp.WriteToFile('SubCircuitExample2.txt')
    def testSubCircuitExample2(self):
        fl=[i*100.*1e6 for i in range(100+1)]
        sspnp = si.p.SystemSParametersNumericParser(fl).File('SubCircuitExample2.txt')
        spres=sspnp.SParameters().WriteToFile('result.s2p')
        # exclude
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(spres.m_P)+'p'
        self.CheckSParametersResult(spres,spFileName,spFileName)
    def testSubCircuitExample2Code(self):
        self.WriteCode('TestSubcircuit.py','testSubCircuitExample2(self)',self.standardHeader)


        
    
        