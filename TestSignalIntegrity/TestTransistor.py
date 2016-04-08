import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import matrix
from TestHelpers import *

class TestTransistor(unittest.TestCase,SourcesTesterHelper,RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testTransistorSimpleSymbolic(self):
        symbolic=si.sd.Symbolic(size='small',eqprefix='\\begin{equation}',eqsuffix='\\end{equation}')
        symbolic._AddEq('\\mathbf{S}='+symbolic._LaTeXMatrix(si.sy.TransconductanceAmplifierThreePort('-g_m', 'r_{\\pi}', 'r_o')))
        symbolic.m_lines = [line.replace('--','+') for line in symbolic.m_lines]
        symbolic.Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),symbolic,'Simple Transistor')
    def testTransistorSimpleSymbolic2(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DC 4',
            'device HIE 2',
            'port 1 HIE 1 2 DC 4 3 DC 3',
            'connect HIE 2 DC 1',
            'connect DC 2 DC 4'])
        # pragma: exclude
        # sdp.WriteToFile('TransistorSimpleNetList.txt',False)
        # pragma: include
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('\\beta'))
        ssps.AssignSParameters('HIE',si.sy.SeriesZ('h_{ie}'))
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Simple Transistor 2')
    def testTransistorSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device T 3','device rb 2','device Cm 2','device Cp 2','device rx 2',
                      'device rc 2','device Cc 2',
                      'port 1 rb 1 2 rc 2 3 rx 2 4 Cc 2',
                      'connect rb 2 Cp 1 Cm 1 T 1','connect T 2 rc 1 Cm 2 Cc 1',
                      'connect Cp 2 T 3 rx 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transistor')
    def testTransistorWithShuntsSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device T 3','device rb 2','device Cms 4','device Cps 4','device rx 2',
                      'device rc 2','device Ccs 3',
                      'port 1 rb 1 2 rc 2 3 rx 2 4 Ccs 3',
                      'connect rb 2 Cms 1','connect Cms 3 Cps 1','connect Cps 3 T 1',
                      'connect T 3 Cps 4','connect Cps 2 rx 1','connect T 2 Ccs 1',
                      'connect Ccs 2 Cms 4','connect Cms 2 rc 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        symbolic=si.sd.Symbolic(size='small')
        rb=si.sy.SeriesZ('r_b')
        symbolic._AddEq('\\mathbf{rb}='+ssps._LaTeXMatrix(rb))
        rc=si.sy.SeriesZ('r_c')
        symbolic._AddEq('\\mathbf{rc}='+ssps._LaTeXMatrix(rc))
        rx=si.sy.SeriesZ('r_ex')
        symbolic._AddEq('\\mathbf{rx}='+ssps._LaTeXMatrix(rx))
        Cms=si.sy.ShuntZ(4,'\\frac{1}{C_{\\mu}\\cdot s}')
        symbolic._AddEq('\\mathbf{Cms}='+ssps._LaTeXMatrix(Cms))
        Ccs=si.sy.ShuntZ(3,'\\frac{1}{C_{cs}\\cdot s}')
        symbolic._AddEq('\\mathbf{Ccs}='+ssps._LaTeXMatrix(Ccs))
        Cps=si.sy.ShuntZ(4,'\\frac{1}{C_{\\pi}\\cdot s}')
        symbolic._AddEq('\\mathbf{Cps}='+ssps._LaTeXMatrix(Cps))
        T=si.sy.TransconductanceAmplifier(3,'-g_m', 'r_{\\pi}', 'r_o')
        symbolic._AddEq('\\mathbf{T}=\\ldots')
        symbolic._AddEq(ssps._LaTeXMatrix(T))
        symbolic.m_lines = [line.replace('--','+') for line in symbolic.m_lines]
        symbolic.Emit()
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id()+'Defs',symbolic,'Transistor')
        self.CheckSymbolicResult(self.id(),ssps,'Transistor')
    def testTransistorSymbolicZO(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DC 4',
            'device HIE 2',
            'device ZO 2',
            'port 1 HIE 1 2 DC 4 3 DC 3',
            'connect HIE 2 DC 1',
            'connect DC 2 DC 4',
            'connect ZO 1 DC 3',
            'connect ZO 2 DC 4'])
        # pragma: exclude
        # sdp.WriteToFile('TransistorSimpleNetList.txt',False)
        # pragma: include
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('\\beta'))
        ssps.AssignSParameters('HIE',si.sy.SeriesZ('Z_{\\pi}'))
        ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Transistor Zo')
    def testTransistorSimpleSymbolicCode(self):
        self.WriteCode('TestTransistor.py','testTransistorSimpleSymbolic2(self)',self.standardHeader)
    def testTransistorZoSymbolicCode(self):
        self.WriteCode('TestTransistor.py','testTransistorZOSymbolic(self)',self.standardHeader)
    def testTransistorSymbolicCode(self):
        self.WriteCode('TestTransistor.py','testTransistorSymbolic(self)',self.standardHeader)
    def testTransistorWithShuntsSymbolicCode(self):
        self.WriteCode('TestTransistor.py','testTransistorWithShuntsSymbolic(self)',self.standardHeader)

if __name__ == '__main__':
    unittest.main()

