import unittest
import os
from cStringIO import StringIO
import sys
import SignalIntegrity as si

class Test(unittest.TestCase):
    def CheckSymbolicResult(self,selfid,symbolic,Text):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileName = '_'.join(selfid.split('.')) + '.tex'
        if not os.path.exists(fileName):
            symbolic.WriteToFile(fileName)
            self.assertTrue(False, fileName + ' not found')
        regression=''
        with open(fileName, 'r') as regressionFile:
            for line in regressionFile:
                regression = regression + line
        comparison = symbolic.Get()
        self.assertTrue(regression == comparison,Text + ' incorrect')
    def testBook(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        parser = si.p.SystemDescriptionParser()
        parser.m_addThru = False
        parser.AddLine('device L 2')
        parser.AddLine('device R 2')
        parser.AddLine('port 1 L 1')
        parser.AddLine('port 2 R 2')
        parser.AddLine('connect L 2 R 1')
        # parser.WriteToFile('book.txt')
        sd = si.sd.SystemSParameters(parser.SystemDescription())
        n = sd.NodeVector()
        W = sd.WeightsMatrix()
        m = sd.StimulusVector()
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        print ('{0:' + str(5 * len(n)) + '}').format('Weights Matrix'),
        print '| {0:4}'.format('n'),
        print '| {0:4} |'.format('m')
        print '----------------------------------------------'
        for r in range(len(n)):
            for c in range(len(sd.NodeVector())):
                print '{0:4}'.format(str(W[r][c])),
            print ' | {0:4}'.format(n[r]),
            print '| {0:4} |'.format(m[r])
        print '----------------------------------------------'
        print '\\left[ \\identity - ' + si.helper.Matrix2LaTeX(W) +\
        '\\right] \\cdot '+ si.helper.Matrix2LaTeX([[i] for i in n]) +\
        ' = '+ si.helper.Matrix2LaTeX([[i] for i in m])
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sys.stdout = old_stdout
        fileName = '_'.join(self.id().split('.')) + '.txt'
        if not os.path.exists(fileName):
            resultFile = open(fileName, 'w')
            resultFile.write(mystdout.getvalue())
            resultFile.close()
            self.assertTrue(False, fileName + ' not found')
        regressionFile = open(fileName, 'r')
        regression = regressionFile.read()
        regressionFile.close()
        self.assertTrue(regression == mystdout.getvalue(), 'Book Example 1 incorrect')
    def testBookSystemDescriptionExample(self):
        sd = si.sd.SystemDescription()
        sd.AddDevice('L', 2)  # add two-port left device
        sd.AddDevice('R', 2)  # add two-port right device
        sd.AddPort('L', 1, 1)  # add a port at port 1 of left device
        sd.AddPort('R', 2, 2)  # add a port at port 2 of right device
        sd.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        sd.Print()  # print the system description
        spc = si.sd.SystemSParameters(sd)
        n = spc.NodeVector()  # get the node vector
        m = spc.StimulusVector()  # get the stimulus vector
        W = spc.WeightsMatrix()  # get the weights matrix
        # print out the vectors and matrices
        print ('{0:' + str(5 * len(n)) + '}').format('Weights Matrix'),
        print '| {0:4}'.format('n'),
        print '| {0:4} |'.format('m')
        print '----------------------------------------------'
        for r in range(len(W)):
            for c in range(len(W[r])):
                print '{0:4}'.format(str(W[r][c])),
            print ' | {0:4}'.format(n[r]),
            print '| {0:4} |'.format(m[r])
        print '----------------------------------------------'
        sys.stdout = old_stdout
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileName = '_'.join(self.id().split('.')) + '.txt'
        if not os.path.exists(fileName):
            resultFile = open(fileName, 'w')
            resultFile.write(mystdout.getvalue())
            resultFile.close()
            self.assertTrue(False, fileName + ' not found')
        regressionFile = open(fileName, 'r')
        regression = regressionFile.read()
        regressionFile.close()
        self.assertTrue(regression == mystdout.getvalue(), 'Book Example System Description incorrect')
    def testBookSymbolicSolution1(self):
        sd = si.sd.SystemDescription()
        sd.AddDevice('S', 2)  # add two-port left device
        sd.AddDevice('\\Gamma t', 1)  # add a termination
        sd.AddPort('S', 1, 1)  # add a port at port 1 of left device
        sd.ConnectDevicePort('S', 2, '\\Gamma t', 1)  # connect the other ports
        spc = si.sd.SystemSParameters(sd)
        symbolic=si.sd.SystemSParametersSymbolic(spc,True,True)
        symbolic.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 1')
    def testBookSymbolicSolution1Parser(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['device S 2','device \\{\\Gamma\\}t 1','port 1 S 1','connect S 2 \\{\\Gamma\\}t 1'])
        sdp.WriteToFile('SymbolicSolution1.txt',False)
        spc = si.sd.SystemSParameters(sdp.SystemDescription())
        symbolic=si.sd.SystemSParametersSymbolic(spc,True,True)
        symbolic.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 1 Parser')
    def testBookSymbolicSolution1ParserFile(self):
        sdp = si.p.SystemDescriptionParser().File('SymbolicSolution1.txt')
        spc = si.sd.SystemSParameters(sdp.SystemDescription())
        symbolic=si.sd.SystemSParametersSymbolic(spc,True,True)
        symbolic.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 1 Parser File')
    def testBookSymbolicSolution2(self):
        sd = si.sd.SystemDescription()
        sd.AddDevice('L', 2)  # add two-port left device
        sd.AddDevice('R', 2)  # add two-port right device
        sd.AddPort('L', 1, 1)  # add a port at port 1 of left device
        sd.AddPort('R', 2, 2)  # add a port at port 2 of right device
        sd.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
        spc = si.sd.SystemSParameters(sd)
        symbolic=si.sd.SystemSParametersSymbolic(spc,True,True)
        symbolic.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 2')
    def testBookSymbolicSolution2Parser(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['device L 2','device R 2','port 1 L 1 2 R 2','connect L 2 R 1'])
        sdp.WriteToFile('SymbolicSolution2.txt',False)
        spc = si.sd.SystemSParameters(sdp.SystemDescription())
        symbolic=si.sd.SystemSParametersSymbolic(spc,True,True)
        symbolic.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 2 Parser')
    def testBookSymbolicSolution2ParserFile(self):
        sdp = si.p.SystemDescriptionParser().File('SymbolicSolution2.txt')
        spc = si.sd.SystemSParameters(sdp.SystemDescription())
        symbolic=si.sd.SystemSParametersSymbolic(spc,True,True)
        symbolic.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 2 Parser File')
    def testBookSymbolicSolution3(self):
        sd = si.sd.SystemDescription()
        sd.AddDevice('L', 2)  # add two-port left device
        sd.AddDevice('R', 2)  # add two-port right device
        sd.AddDevice('M', 2)  # add two-port middle device
        sd.AddDevice('G', 1, [[-1]]) # add a ground
        sd.AddPort('L', 1, 1)  # add a port at port 1 of left device
        sd.AddPort('R', 2, 2)  # add a port at port 2 of right device
        sd.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
        sd.ConnectDevicePort('L', 2, 'M', 1)
        sd.ConnectDevicePort('G', 1, 'M', 2)
        spc = si.sd.SystemSParameters(sd)
        symbolic=si.sd.SystemSParametersSymbolic(spc,True,True)
        symbolic.LaTeXSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 3')
    def testBookSymbolicSolution3Parser(self):
        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['device L 2','device R 2','device M 2','device G 1 ground','port 1 L 1 2 R 2',
            'connect L 2 R 1 M 1','connect G 1 M 2'])
        sdp.WriteToFile('SymbolicSolution3.txt',False)
        spc = si.sd.SystemSParameters(sdp.SystemDescription())
        symbolic=si.sd.SystemSParametersSymbolic(spc,True,True)
        symbolic.LaTeXSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 3 Parser')
    def testBookSymbolicSolution3ParserFile(self):
        sdp = si.p.SystemDescriptionParser().File('SymbolicSolution3.txt')
        spc = si.sd.SystemSParameters(sdp.SystemDescription())
        symbolic=si.sd.SystemSParametersSymbolic(spc,True,True)
        symbolic.LaTeXSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Solution 3 Parser File')
    def testBookSymbolicDeembedding1(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('D',2)
        sd.AddDevice('?',1)
        sd.ConnectDevicePort('D',2,'?',1)
        sd.AddPort('D',1,1)
        spc = si.sd.Deembedder(sd)
        symbolic=si.sd.DeembedderSymbolic(spc,True,True)
        symbolic.SymbolicSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 1')
    def testBookSymbolicDeembedding1Thru(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('D',2)
        sd.AddDevice('?',1)
        sd.ConnectDevicePort('D',2,'?',1)
        sd.AddPort('D',1,1,True)
        spc = si.sd.Deembedder(sd)
        symbolic=si.sd.DeembedderSymbolic(spc,True,True)
        symbolic.SymbolicSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 1 Thru')
    def testBookSymbolicDeembedding1Parser(self):
        dp=si.p.DeembedderParser()
        dp.AddLines(['device D 2','device ? 1','port 1 D 1','connect D 2 ? 1'])
        dp.WriteToFile('SymbolicDeembedding1.txt',False)
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,True,True)
        symbolic.SymbolicSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 1 Parser')
    def testBookSymbolicDeembedding1ParserFile(self):
        dp=si.p.DeembedderParser().File('SymbolicDeembedding1.txt')
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,True,True)
        symbolic.SymbolicSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 1 Parser File')
    def testBookSymbolicDeembedding2(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('L',2)
        sd.AddDevice('?',2)
        sd.AddDevice('R',2)
        sd.AddPort('L',1,1)
        sd.AddPort('R',1,2)
        sd.ConnectDevicePort('L',2,'?',1)
        sd.ConnectDevicePort('R',2,'?',2)
        spc = si.sd.Deembedder(sd)
        symbolic=si.sd.DeembedderSymbolic(spc,True,True)
        symbolic.SymbolicSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 2')
    def testBookSymbolicDeembedding2Parser(self):
        dp=si.p.DeembedderParser()
        dp.AddLines(['device L 2','device ? 2','device R 2','port 1 L 1 2 R 1','connect L 2 ? 1','connect R 2 ? 2'])
        dp.WriteToFile('SymbolicDeembedding2.txt',False)
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,True,True)
        symbolic.SymbolicSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 2 Parser')
    def testBookSymbolicDeembedding2ParserFile(self):
        dp=si.p.DeembedderParser().File('SymbolicDeembedding2.txt')
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,True,True)
        symbolic.SymbolicSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 2 Parser File')
    def testBookSymbolicDeembedding3(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('L',2)
        sd.AddDevice('?',2)
        sd.AddPort('L',1,1)
        sd.AddPort('?',2,2,True)
        sd.ConnectDevicePort('L',2,'?',1)
        spc = si.sd.Deembedder(sd)
        symbolic=si.sd.DeembedderSymbolic(spc,True,True)
        symbolic.SymbolicSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 3')
    def testBookSymbolicDeembedding3Thru(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('L',2)
        sd.AddDevice('?',2)
        sd.AddPort('L',1,1,True)
        sd.AddPort('?',2,2,True)
        sd.ConnectDevicePort('L',2,'?',1)
        spc = si.sd.Deembedder(sd)
        symbolic=si.sd.DeembedderSymbolic(spc,True,True)
        symbolic.SymbolicSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding 3 Thru incorrect')
    def testBookSymbolicDeembedding3Parser(self):
        dp=si.p.DeembedderParser()
        dp.AddLines(['device L 2','device ? 2','port 1 L 1 2 ? 2','connect L 2 ? 1'])
        dp.WriteToFile('SymbolicDeembedding3.txt',False)
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,True,True)
        symbolic.SymbolicSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 3 Parser')
    def testBookSymbolicDeembedding3ParserFile(self):
        dp=si.p.DeembedderParser().File('SymbolicDeembedding3.txt')
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,True,True)
        symbolic.SymbolicSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 3 Parser File')
    def testBookSymbolicDeembedding4(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('F',4)
        sd.AddDevice('?1',1)
        sd.AddDevice('?2',1)
        sd.AddPort('F',1,1)
        sd.AddPort('F',2,2)
        sd.ConnectDevicePort('F',3,'?1',1)
        sd.ConnectDevicePort('F',4,'?2',1)
        spc = si.sd.Deembedder(sd)
        symbolic=si.sd.DeembedderSymbolic(spc,True,True)
        symbolic.SymbolicSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 4')
    def testBookSymbolicDeembedding4Parser(self):
        dp=si.p.DeembedderParser()
        dp.AddLines(['device F 4','device ?1 1','device ?2 1','port 1 F 1 2 F 2',
            'connect F 3 ?1 1','connect F 4 ?2 1'])
        dp.WriteToFile('SymbolicDeembedding4.txt',False)
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,True,True)
        symbolic.SymbolicSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 4 Parser')
    def testBookSymbolicDeembedding4ParserFile(self):
        dp=si.p.DeembedderParser().File('SymbolicDeembedding4.txt')
        spc = si.sd.Deembedder(dp.SystemDescription())
        symbolic=si.sd.DeembedderSymbolic(spc,True,True)
        symbolic.SymbolicSolution()
        self.CheckSymbolicResult(self.id(),symbolic,'Book Example Symbolic Deembedding Solution 4 Parser File')
    def testBookSymbolicVirtualProbe1(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('T',1)
        sd.AddDevice('C',2)
        sd.AddDevice('R',1)
        sd.ConnectDevicePort('T',1,'C',1)
        sd.ConnectDevicePort('C',2,'R',1)
        sd.AssignM('T',1,'m1')
        vp=si.sd.VirtualProbe(sd)
        vp.pMeasurementList = [('T',1)]
        vp.pOutputList = [('R',1)]
        svp=si.sd.VirtualProbeSymbolic(vp,True,True)
        svp.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 1')
    def testBookSymbolicVirtualProbe1Parser(self):
        vpp=si.p.VirtualProbeParser()
        vpp.AddLines(['device T 1','device C 2','device R 1','connect T 1 C 1','connect C 2 R 1',
            'stim m1 T 1','meas T 1','output R 1'])
        vpp.WriteToFile('VirtualProbe1.txt',False)
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,True,True)
        svp.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 1 Parser')
    def testBookSymbolicVirtualProbe1ParserFile(self):
        vpp=si.p.VirtualProbeParser().File('VirtualProbe1.txt')
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,True,True)
        svp.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 1 Parser File')
    def testBookSymbolicVirtualProbe2(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('T',2)
        sd.AddDevice('C',4)
        sd.AddDevice('R',2)
        sd.ConnectDevicePort('T',1,'C',1)
        sd.ConnectDevicePort('T',2,'C',2)
        sd.ConnectDevicePort('C',3,'R',1)
        sd.ConnectDevicePort('C',4,'R',2)
        sd.AssignM('T',1,'m1')
        sd.AssignM('T',2,'m2')
        vp=si.sd.VirtualProbe(sd)
        vp.pMeasurementList = [('T',1),('T',2)]
        vp.pOutputList = [('R',1),('R',2)]
        svp=si.sd.VirtualProbeSymbolic(vp,True,True)
        svp.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 2')
    def testBookSymbolicVirtualProbe2Parser(self):
        vpp=si.p.VirtualProbeParser()
        vpp.AddLines(['device T 2','device C 4','device R 2','connect T 1 C 1','connect T 2 C 2',
            'connect C 3 R 1','connect C 4 R 2','stim m1 T 1','stim m2 T 2','meas T 1 T 2','output R 1 R 2'])
        vpp.WriteToFile('VirtualProbe2.txt',False)
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,True,True)
        svp.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 2 Parser')
    def testBookSymbolicVirtualProbe2ParserFile(self):
        vpp=si.p.VirtualProbeParser().File('VirtualProbe2.txt')
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,True,True)
        svp.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 2 Parser File')
    def testBookSymbolicVirtualProbe3(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('T',2)
        sd.AddDevice('C',4)
        sd.AddDevice('R',2)
        sd.ConnectDevicePort('T',1,'C',1)
        sd.ConnectDevicePort('T',2,'C',2)
        sd.ConnectDevicePort('C',3,'R',1)
        sd.ConnectDevicePort('C',4,'R',2)
        sd.AssignM('T',1,'m1')
        sd.AssignM('T',2,'m2')
        vp=si.sd.VirtualProbe(sd)
        vp.pMeasurementList = [('T',1),('T',2)]
        vp.pOutputList = [('R',1),('R',2)]
        vp.pStimDef = [[1],[-1]]
        svp=si.sd.VirtualProbeSymbolic(vp,True,True)
        svp.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 3')
    def testBookSymbolicVirtualProbe3Parser(self):
        vpp=si.p.VirtualProbeParser()
        vpp.AddLines(['device T 2','device C 4','device R 2','connect T 1 C 1','connect T 2 C 2',
            'connect C 3 R 1','connect C 4 R 2','stim m1 T 1','stim m2 T 2','meas T 1 T 2','output R 1 R 2',
            'stimdef [[1],[-1]]'])
        vpp.WriteToFile('VirtualProbe3.txt',False)
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,True,True)
        svp.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 3 Parser')
    def testBookSymbolicVirtualProbe3ParserFile(self):
        vpp=si.p.VirtualProbeParser().File('VirtualProbe3.txt')
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,True,True)
        svp.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 3 Parser File')
    def testBookSymbolicVirtualProbe4(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('T',2)
        sd.AddDevice('MM1',4,si.dev.MixedModeConverter())
        sd.AddDevice('MM2',4,si.dev.MixedModeConverter())
        sd.AddDevice('C',4)
        sd.AddDevice('R',2)
        sd.ConnectDevicePort('T',1,'MM1',1)
        sd.ConnectDevicePort('T',2,'MM1',2)
        sd.ConnectDevicePort('MM1',3,'MM2',3)
        sd.ConnectDevicePort('MM1',4,'MM2',4)
        sd.ConnectDevicePort('MM2',1,'C',1)
        sd.ConnectDevicePort('MM2',2,'C',2)
        sd.ConnectDevicePort('C',3,'R',1)
        sd.ConnectDevicePort('C',4,'R',2)
        sd.AssignM('T',1,'m1')
        sd.AssignM('T',2,'m2')
        vp=si.sd.VirtualProbe(sd)
        vp.pMeasurementList = [('MM1',3)]
        vp.pOutputList = [('R',1),('R',2)]
        vp.pStimDef = [[1],[-1]]
        svp=si.sd.VirtualProbeSymbolic(vp,True,True)
        svp.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 4')
    def testBookSymbolicVirtualProbe4Parser(self):
        vpp=si.p.VirtualProbeParser()
        vpp.AddLines(['device T 2','device MM1 4 mixedmode','device MM2 4 mixedmode','device C 4',
            'device R 2','connect T 1 MM1 1','connect T 2 MM1 2','connect MM1 3 MM2 3','connect MM1 4 MM2 4',
            'device MM2 1 C 1','device MM2 2 C 2',
            'connect C 3 R 1','connect C 4 R 2','stim m1 T 1 m2 T 2','meas MM1 3','output R 1 R 2',
            'stimdef [[1],[-1]]'])
        vpp.WriteToFile('VirtualProbe4.txt',False)
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,True,True)
        svp.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 4 Parser')
    def testBookSymbolicVirtualProbe4ParserFile(self):
        vpp=si.p.VirtualProbeParser().File('VirtualProbe4.txt')
        vp=si.sd.VirtualProbe(vpp.SystemDescription())
        svp=si.sd.VirtualProbeSymbolic(vp,True,True)
        svp.LaTeXEquations()
        self.CheckSymbolicResult(self.id(),svp,'Book Example Symbolic Virtual Probe 4 Parser File')
if __name__ == "__main__":
    unittest.main()
