import unittest

from numpy import array

import SignalIntegrity as si

from cStringIO import StringIO
import sys
import os

class TestSystemDescription(unittest.TestCase):
    def testRedirect(self):
        old_stdout = sys.stdout
        testString = "Hi - this is a test"
        sys.stdout = mystdout = StringIO()
        print "This should not print"
        print testString
        sys.stdout = old_stdout
        #print "This should"
        #print mystdout.getvalue()
    def testBasic(self):
        D=si.sd.SystemDescription()
        D.AddDevice('D1',2)
        D.AddDevice('D2',2)
        D.AddDevice('D3',2)
        D.ConnectDevicePort('D1',2,'D2',1)
        D.ConnectDevicePort('D1',2,'D3',1)
        D.AddPort('D1',1,1)
        D.AddPort('D2',2,2)
        D.AddPort('D3',2,3)
        SC=si.sd.SystemSParameters(D)
        n=SC.NodeVector()
        W=SC.WeightsMatrix()
        m=SC.StimulusVector()
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        SC.Print()
        SC[0].Print()
        SC[0][0].Print()
        sys.stdout = old_stdout
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileName='_'.join(self.id().split('.'))+'.txt'
        if not os.path.exists(fileName):
            resultFile=open(fileName,'w')
            resultFile.write(mystdout.getvalue())
            resultFile.close()
            self.assertTrue(False,fileName+ ' not found')
        regressionFile=open(fileName,'rU')
        regression = regressionFile.read()
        regressionFile.close()
        self.assertTrue(regression==mystdout.getvalue(),'System Description incorrect')
    def testSystemDescriptionExampleBlock(self):
        from numpy import array
        D=si.sd.SystemDescription()
        D.AddDevice('D1',2)
        D.AddDevice('D2',2)
        D.ConnectDevicePort('D1',2,'D2',1)
        D.AddPort('D1',1,1)
        D.AddPort('D2',2,2)
        SC=si.sd.SystemSParameters(D)
        n=SC.NodeVector()
        W=SC.WeightsMatrix()
        m=SC.StimulusVector()
        # pragma: exclude
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        # pragma: include
        print 'node vector:'
        print(n)
        print 'weights matrix:'
        print(array(W))
        print 'stimulus vector:'
        print(m)
        AN=SC.PortBNames()
        BN=SC.PortANames()
        print 'AN:'
        print(AN)
        print 'BN:'
        print(BN)
        XN=SC.OtherNames(AN+BN)
        Wba=SC.WeightsMatrix(BN,AN)
        Wbx=SC.WeightsMatrix(BN,XN)
        Wxa=SC.WeightsMatrix(XN,AN)
        Wxx=SC.WeightsMatrix(XN,XN)
        print 'Wba'
        print(Wba)
        print 'Wbx'
        print(Wbx)
        print 'Wxa'
        print(Wxa)
        print 'Wxx'
        print(Wxx)
        # pragma: exclude
        sys.stdout = old_stdout
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileName='_'.join(self.id().split('.'))+'.txt'
        if not os.path.exists(fileName):
            resultFile=open(fileName,'w')
            resultFile.write(mystdout.getvalue())
            resultFile.close()
            self.assertTrue(False,fileName+ ' not found')
        regressionFile=open(fileName,'rU')
        regression = regressionFile.read()
        regressionFile.close()
        self.assertTrue(regression==mystdout.getvalue(),'Test Example incorrect')
if __name__ == '__main__':
    unittest.main()