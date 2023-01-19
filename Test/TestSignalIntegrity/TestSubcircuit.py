"""
TestSubcircuit.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import unittest
import os
import sys
if sys.version_info.major < 3:
    from cStringIO import StringIO
else:
    from io import StringIO

import SignalIntegrity.Lib as si
from numpy import matrix
from numpy import random

class TestSubcircuit(unittest.TestCase,si.test.RoutineWriterTesterHelper,si.test.ResponseTesterHelper):
    def __init__(self, methodName='runTest'):
        si.test.RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def id(self):
        return '.'.join(unittest.TestCase.id(self).split('.')[-3:])
    def testShuntZFourPortSubCircuitNetlistGenerator(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['var $Rsh$ 50.','device R 2 R $Rsh$',
            'port 1 R 2 2 R 1 3 R 2 4 R 1'])
        sdp.WriteToFile('ShuntZFourPort.sub')
    def testShuntZThreePortSubCircuitNetlistGenerator(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['var $Rsh$ 50.','device R 4 subcircuit ShuntZFourPort.sub Rsh $Rsh$',
            'device O 1 open','connect O 1 R 4',
            'port 1 R 1 2 R 3 3 R 2'])
        sdp.WriteToFile('ShuntZThreePort.sub')
    def testShuntZTwoPortSubCircuitNetlistGenerator(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['var $Rsh$ 50.','device R 3 subcircuit ShuntZThreePort.sub Rsh $Rsh$',
            'device G 1 ground','connect G 1 R 3',
            'port 1 R 1 2 R 2'])
        sdp.WriteToFile('ShuntZTwoPort.sub')
    def testSubCircuitUserNetlistGenerator1(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3 subcircuit ShuntZThreePort.sub Rsh 25.',
                      'device G 1 ground','connect D 3 G 1',
                      'port 1 D 1 2 D 2'])
        sdp.WriteToFile('SubCircuitExample1.txt')
    def testSubCircuitExample1(self):
        fl=[0.]
        sspnp = si.p.SystemSParametersNumericParser(fl).File('SubCircuitExample1.txt')
        sp=sspnp.SParameters()
    def testFourPortShunt(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        sspnp = si.p.SystemSParametersNumericParser([0.])
        Z=94.
        sspnp.AddLines(['device D 4 subcircuit ShuntZFourPort.sub Rsh '+str(Z),
                      'port 1 D 1 2 D 2 3 D 3 4 D 4'])
        sp=sspnp.SParameters()
        # pragma: exclude
        sp2 = si.sp.SParameters([0.],[si.dev.ShuntZ(4,Z)])
        self.assertTrue(self.SParametersAreEqual(sp,sp2,0.00001),self.id() + ' incorrect')
    def testThreePortShunt(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        sspnp = si.p.SystemSParametersNumericParser([0.])
        Z=random.random()*200.
        sspnp.AddLines(['device D 3 subcircuit ShuntZThreePort.sub Rsh '+str(Z),
                      'port 1 D 1 2 D 2 3 D 3'])
        sp=sspnp.SParameters()
        # pragma: exclude
        sp2 = si.sp.SParameters([0.],[si.dev.ShuntZ(3,Z)])
        self.assertTrue(self.SParametersAreEqual(sp,sp2,0.00001),self.id() + ' incorrect')
    def testTwoPortShunt(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        sspnp = si.p.SystemSParametersNumericParser([0.])
        Z=random.random()*200.
        sspnp.AddLines(['device D 2 subcircuit ShuntZTwoPort.sub Rsh '+str(Z),
                      'port 1 D 1 2 D 2'])
        sp=sspnp.SParameters()
        # pragma: exclude
        sp2 = si.sp.SParameters([0.],[si.dev.ShuntZ(2,Z)])
        self.assertTrue(self.SParametersAreEqual(sp,sp2,0.00001),self.id() + ' incorrect')
    def testSubCircuitNetlistGenerator2(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines([
            'var $DL$ thru $DR$ thru',
            'device L 2 $DL$','device R 2 $DR$',
            'port 1 L 1 2 R 2','connect L 2 R 1'])
        sdp.WriteToFile('cascade.sub')
    def testSubCircuitUserNetlistGenerator2(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2 subcircuit cascade.sub DL \'file;cable.s2p\' DR \'file;filter.s2p\'',
                      'port 1 D 1 2 D 2'])
        sdp.WriteToFile('SubCircuitExample2.txt')
    def testSubCircuitExample2(self):
        fl=[i*100.*1e6 for i in range(100+1)]
        sspnp = si.p.SystemSParametersNumericParser(fl).File('SubCircuitExample2.txt')
        spres=sspnp.SParameters().WriteToFile('result.s2p')
        # pragma: exclude
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(spres.m_P)+'p'
        self.CheckSParametersResult(spres,spFileName,spFileName)
    def testSubCircuitExample2Code(self):
        self.WriteCode('TestSubcircuit.py','testSubCircuitExample2(self)',self.standardHeader)

if __name__ == "__main__":
    unittest.main()



