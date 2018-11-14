"""
TestExceptions.py
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

import SignalIntegrity.Lib as si

class TestExceptions(unittest.TestCase,si.test.SParameterCompareHelper):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        si.sd.Numeric.trySVD=True
        unittest.TestCase.setUp(self)
    def tearDown(self):
        si.sd.Numeric.trySVD=True
        unittest.TestCase.tearDown(self)
    def testSystemDescriptionCheckConnections(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 ZI 2 3 ZO 2 4 DV 3',
            'connect ZI 1 DV 2','connect ZI 2 DV 1'])
        #sdp.SystemDescription().Print()
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        try:
            ssps.LaTeXSolution().Emit()
        except si.SignalIntegrityException as e:
            if e == si.SignalIntegrityExceptionSystemDescription:
                pass
    def testSystemDescriptionCheckConnections2(self):
        sdp=si.p.SystemDescriptionParser()
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        try:
            ssps.LaTeXSolution().Emit()
        except si.SignalIntegrityException as e:
            if e == si.SignalIntegrityExceptionSystemDescription:
                pass
    def testSystemDescriptionCheckConnections3(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 ZI 2 3 ZO 2 4 DV 3',
            'connect ZI 1 DV 2','connect ZI 2 DV 1'])
        #sdp.SystemDescription().Print()
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        with self.assertRaises(si.SignalIntegrityException) as cm:
            ssps.LaTeXSolution().Emit()
        self.assertEqual(cm.exception.parameter,'SystemDescription')
    def testSystemDescriptionWrongDevice(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 ZI 2 3 ZO 2 4 DV 3',
            'connect Z 1 DV 2','connect ZI 2 DV 1'])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sdp.SystemDescription().Print()
        self.assertEqual(cm.exception.parameter,'SystemDescription')
    def testSystemDescriptionWrongConnection(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device ZI 2','device ZO 2',
            'port 1 ZI 1 2 ZI 2 3 ZO 2 4 DV 3',
            'connect ZI 3 DV 2','connect ZI 2 DV 1'])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sdp.SystemDescription().Print()
        self.assertEqual(cm.exception.parameter,'SystemDescription')
    def testSystemDescriptionDuplicateName(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4','device DV 2'])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sdp.SystemDescription().Print()
        self.assertEqual(cm.exception.parameter,'SystemDescription')
    def testSimulatorNoOutputProbes(self):
        sp=si.p.SimulatorParser()
        sp.AddLines(['voltagesource VS1 1','device G1 1 ground','connect G1 1 VS1 1'])
        ss=si.sd.SimulatorSymbolic(sp.SystemDescription(),size='small')
        with self.assertRaises(si.SignalIntegrityException) as cm:
            ss.LaTeXTransferMatrix()
        self.assertEqual(cm.exception.parameter,'Simulator')
    def testSimulatorNoSources(self):
        sp=si.p.SimulatorParser()
        sp.AddLines(['device R1 1 R 50.0','device R2 1 R 50.0','output R2 1','connect R2 1 R1 1'])
        ss=si.sd.SimulatorSymbolic(sp.SystemDescription(),size='small')
        with self.assertRaises(si.SignalIntegrityException) as cm:
            ss.LaTeXTransferMatrix()
        self.assertEqual(cm.exception.parameter,'Simulator')
    def testSimulatorNumericalError(self):
        """
        Here, a voltage source is tied directly to ground and the output cannot be determined.
        without trySVD, it correctly raises an exception.
        """
        sp=si.p.SimulatorParser()
        sp.AddLines(['voltagesource VS1 1','device G1 1 ground','output G1 1','connect G1 1 VS1 1'])
        sn=si.sd.SimulatorNumeric(sp.SystemDescription())
        si.sd.Numeric.trySVD=False
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sn.TransferMatrix()
        si.sd.Numeric.trySVD=True
        self.assertEqual(cm.exception.parameter,'Simulator')
    @unittest.expectedFailure
    def testSimulatorNumericalErrorNonsenseResult(self):
        """
        This is a known problem in the trySVD code.
        trySVD resolves many problems due to indeterminate internal things, with a good, final determinate
        answer, but in this case, trySVD allows the computation of the voltage with a voltage source tied
        directly to ground.  This is something that needs to be fixed in the future and is why trySVD
        is currently experimental.
        """
        sp=si.p.SimulatorParser()
        sp.AddLines(['voltagesource VS1 1','device G1 1 ground','output G1 1','connect G1 1 VS1 1'])
        sn=si.sd.SimulatorNumeric(sp.SystemDescription())
        si.sd.Numeric.trySVD=True
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sn.TransferMatrix()
        self.assertEqual(cm.exception.parameter,'Simulator')
    def testSimulatorNumericalErrorSymbolic(self):
        sp=si.p.SimulatorParser()
        sp.AddLines(['voltagesource VS1 1','device G1 1 ground','output G1 1','connect G1 1 VS1 1'])
        ss=si.sd.SimulatorSymbolic(sp.SystemDescription())
        ss.DocStart()
        ss.LaTeXEquations()
        ss.DocEnd()
        ss.WriteToFile('SimulatorNumericalErrorSymbolic')
        #self.assertEqual(cm.exception.parameter,'Simulator')
    def testVirtualProbeNoOutputProbes(self):
        sp=si.p.VirtualProbeParser()
        #sp.AddLines(['device T 1','device C 2','device R 1','connect T 1 C 1','connect C 2 R 1','stim m1 T 1','meas T 1','output R 1'])
        sp.AddLines(['device T 1','device C 2','device R 1','connect T 1 C 1','connect C 2 R 1','stim m1 T 1','meas T 1'])
        ss=si.sd.VirtualProbeSymbolic(sp.SystemDescription(),size='small')
        with self.assertRaises(si.SignalIntegrityException) as cm:
            ss.LaTeXTransferMatrix()
        self.assertEqual(cm.exception.parameter,'VirtualProbe')
    def testVirtualProbeNoStims(self):
        sp=si.p.VirtualProbeParser()
        #sp.AddLines(['device T 1','device C 2','device R 1','connect T 1 C 1','connect C 2 R 1','stim m1 T 1','meas T 1','output R 1'])
        sp.AddLines(['device T 1','device C 2','device R 1','connect T 1 C 1','connect C 2 R 1','meas T 1','output R 1'])
        ss=si.sd.VirtualProbeSymbolic(sp.SystemDescription(),size='small')
        with self.assertRaises(si.SignalIntegrityException) as cm:
            ss.LaTeXTransferMatrix()
        self.assertEqual(cm.exception.parameter,'VirtualProbe')
    def testVirtualProbeNoMeasures(self):
        sp=si.p.VirtualProbeParser()
        #sp.AddLines(['device T 1','device C 2','device R 1','connect T 1 C 1','connect C 2 R 1','stim m1 T 1','meas T 1','output R 1'])
        sp.AddLines(['device T 1','device C 2','device R 1','connect T 1 C 1','connect C 2 R 1','stim m1 T 1','output R 1'])
        ss=si.sd.VirtualProbeSymbolic(sp.SystemDescription(),size='small')
        with self.assertRaises(si.SignalIntegrityException) as cm:
            ss.LaTeXTransferMatrix()
        self.assertEqual(cm.exception.parameter,'VirtualProbe')
    def testVirtualProbeNumericalError(self):
        sp=si.p.VirtualProbeParser()
        sp.AddLines(['device T 1','device C 1','device R 1','device G 1 ground','connect T 1 C 1','connect G 1 R 1','stim m1 T 1','meas T 1','output R 1'])
        sn=si.sd.VirtualProbeNumeric(sp.SystemDescription())
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sn.TransferMatrix()
        self.assertEqual(cm.exception.parameter,'VirtualProbe')
    def testVirtualProbeWrongStimdef(self):
        sp=si.p.VirtualProbeParser()
        #sp.AddLines(['device T 1','device C 2','device R 1','connect T 1 C 1','connect C 2 R 1','stim m1 T 1','meas T 1','output R 1'])
        sp.AddLines(['device T 1 termination','device C 2 thru','device R 1 termination','connect T 1 C 1','connect C 2 R 1','stim m1 T 1','meas T 1','output R 1','stimdef [[1.,1.],[1.,1.]]'])
        vpn=si.sd.VirtualProbeNumeric(sp.SystemDescription())
        with self.assertRaises(si.SignalIntegrityException) as cm:
            vpn.TransferMatrix()
        self.assertEqual(cm.exception.parameter,'VirtualProbe')
    def testSParameterFileWrongExtension(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sp=si.sp.SParameterFile('test.txt')
        self.assertEqual(cm.exception.parameter,'SParameterFile')
    def testWaveformFileNonexsistent(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            wf=si.td.wf.Waveform().ReadFromFile('IHopeThisFileDoesntExist.txt')
        self.assertEqual(cm.exception.parameter,'WaveformFile')
    def testSParameterNumericalError(self):
        sp=si.p.SystemSParametersNumericParser(f=[0])
        sp.AddLines(['device T1 2 tline zc 40.0 td 3e-10',
                     'device T2 2 tline zc 55.0 td 4e-10',
                     'device T3 4 tline zc 50.0 td 6e-10',
                     'port 1 T3 1',
                     'connect T3 1 T1 1',
                     'port 2 T3 3',
                     'connect T3 3 T2 1',
                     'port 3 T3 2',
                     'connect T3 2 T1 2',
                     'port 4 T3 4',
                     'connect T3 4 T2 2'])
        si.sd.Numeric.trySVD=False
        try:
            spBlock=sp.SParameters(solvetype='block')
            blockSucceeded=True
        except:
            blockSucceeded=False

        try:
            spDirect=sp.SParameters(solvetype='direct')
            directSucceeded=True
        except:
            directSucceeded=False

        si.sd.Numeric.trySVD=True
        # originally, I thought that when the direct method succeeded, that there was something wrong
        # with the block method.  But there was a condition number check on the block method and the
        # condition number was poor - I added a check in the direct method and now the direct method fails.
        # The correct assertion is that they both fail
#         self.assertTrue(directSucceeded,'this used to work - something really broke')
#         self.assertTrue(blockSucceeded,'direct succeed, but block failed - a known bug waiting to be fixed')
# 
#         if (blockSucceeded and directSucceeded):
#             self.assertTrue(self.SParametersAreEqual(spBlock, spDirect, 1e-4))
#         # if I made it here, this bug is now fixed

        self.assertTrue((not blockSucceeded) and (not directSucceeded),'this calculation should fail because of poor condition number')

    def testSParameterNumericalErrorFixed(self):
        sp=si.p.SystemSParametersNumericParser(f=[0])
        sp.AddLines(['device T1 2 tline zc 40.0 td 3e-10',
                     'device T2 2 tline zc 55.0 td 4e-10',
                     'device T3 4 tline zc 50.0 td 6e-10',
                     'port 1 T3 1',
                     'connect T3 1 T1 1',
                     'port 2 T3 3',
                     'connect T3 3 T2 1',
                     'port 3 T3 2',
                     'connect T3 2 T1 2',
                     'port 4 T3 4',
                     'connect T3 4 T2 2'])

        try:
            spBlock=sp.SParameters(solvetype='block')
            blockSucceeded=True
        except:
            blockSucceeded=False

        try:
            spDirect=sp.SParameters(solvetype='direct')
            directSucceeded=True
        except:
            directSucceeded=False

        # originally, I thought that when the direct method succeeded, that there was something wrong
        # with the block method.  But there was a condition number check on the block method and the
        # condition number was poor - I added a check in the direct method and now the direct method fails.
        # The correct assertion is that they both fail

        self.assertTrue(directSucceeded,'this used to work - something really broke')
        self.assertTrue(blockSucceeded,'direct succeed, but block failed - a known bug waiting to be fixed')

        if (blockSucceeded and directSucceeded):
            self.assertTrue(self.SParametersAreEqual(spBlock, spDirect, 1e-4))
        # if I made it here, this bug is now fixed
#
#         self.assertTrue((not blockSucceeded) and (not directSucceeded),'this calculation should fail because of poor condition number')

    def testSParameterExceptionNoFrequency(self):
        sp=si.p.SystemSParametersNumericParser()
        sp.AddLines(['device T1 2 tline zc 40.0 td 3e-10',
                     'device T2 2 tline zc 55.0 td 4e-10',
                     'device T3 4 tline zc 50.0 td 6e-10',
                     'port 1 T3 1',
                     'connect T3 1 T1 1',
                     'port 2 T3 3',
                     'connect T3 3 T2 1',
                     'port 3 T3 2',
                     'connect T3 2 T1 2',
                     'port 4 T3 4',
                     'connect T3 4 T2 2'])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sp.SParameters(solvetype='direct')
        
        self.assertEquals(cm.exception.message,'frequency dependent device tline could not be instantiated because no frequencies provided','wrong device parser exception')
    def testWaveformExceptionAddIllegal(self):
        """test exception generated by adding waveform to something illegal"""
        wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.0,5,1e9),[1.,2.,3.,4.,5.])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            wf=wf+"string"
        self.assertEquals(cm.exception.parameter,si.SignalIntegrityExceptionWaveform().parameter)
    def testWaveformExceptionMulIllegal(self):
        """test exception generated by multiplying waveform by something illegal"""
        wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.0,5,1e9),[1.,2.,3.,4.,5.])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            wf=wf*"string"
        self.assertEquals(cm.exception.parameter,si.SignalIntegrityExceptionWaveform().parameter)
    def testWaveformExceptionDivIllegal(self):
        """test exception generated by dividing waveform by something illegal"""
        wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.0,5,1e9),[1.,2.,3.,4.,5.])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            wf=wf/"string"
        self.assertEquals(cm.exception.parameter,si.SignalIntegrityExceptionWaveform().parameter)
    def testWaveformExceptionSubIllegal(self):
        """test exception generated by subtracting from waveform something illegal"""
        wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.0,5,1e9),[1.,2.,3.,4.,5.])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            wf=wf-"string"
        self.assertEquals(cm.exception.parameter,si.SignalIntegrityExceptionWaveform().parameter)
    def testWaveformCompareDescriptor(self):
        """test waveform comparison with different descriptor"""
        wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.0,5,1e9),[1.,2.,3.,4.,5.])
        wf2=si.td.wf.Waveform(wf).DelayBy(1e-9)
        self.assertFalse(wf==wf2,'waveform compare with different descriptor failed')
    def testWaveformCompareValuesSame(self):
        """test waveform comparison with same values"""
        wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.0,5,1e9),[1.,2.,3.,4.,5.])
        wf2=si.td.wf.Waveform(wf)/2.
        wf3=wf2*2.
        self.assertTrue(wf==wf3,'waveform compare with same values failed')
    def testWaveformCompareValuesDifferent(self):
        """test waveform comparison with different values"""
        wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.0,5,1e9),[1.,2.,3.,4.,5.])
        wf2=si.td.wf.Waveform(wf)/2.
        self.assertFalse(wf==wf2,'waveform compare with different values failed')
    def testWaveformCompareValuesDifferent2(self):
        """test waveform comparison with different values"""
        wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.0,5,1e9),[1.,2.,3.,4.,5.])
        wf2=si.td.wf.Waveform(wf)/2.
        self.assertTrue(wf!=wf2,'waveform compare with different values failed')
    def testWaveformCompareLengthDifferent(self):
        """test waveform comparison with different length"""
        wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.0,5,1e9),[1.,2.,3.,4.,5.])
        wf2=si.td.wf.Waveform(si.td.wf.TimeDescriptor(wf.td.H,wf.td.K-1,wf.td.Fs),[wf[k] for k in range(len(wf)-1)])
        self.assertFalse(wf==wf2,'waveform compare with different values failed')
    def testWaveformTimeAmplitudeRead(self):
        import os
        wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.0,5,1.),[1.,2.,3.,4.,5.])
        wfName='WaveformTimeAmplitude.txt'
        wfText=str(len(wf))+' '
        for (t,v) in zip(wf.Times(),wf.Values()):
            wfText=wfText+'{:.15g} {:.15g} '.format(t,v)
        with open(wfName,'w') as f:
            f.write(wfText+'\n')
        wf2=si.td.wf.Waveform().ReadFromFile(wfName)
        self.assertTrue(wf==wf2,'waveform compare with same values failed')
        os.remove(wfName)
    def testWaveformImpulseResponseSame(self):
        wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.0,5,1e9),[1.,2.,3.,4.,5.])
        wf2=si.td.wf.ImpulseResponse(wf)
        self.assertTrue(wf==wf2,'waveform compare with same values failed')
    def testWaveformProcessorBase(self):
        wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.0,5,1e9),[1.,2.,3.,4.,5.])
        wf2=si.td.f.WaveformProcessor().ProcessWaveform(wf)
        self.assertTrue(wf==wf2,'waveform compare with same values failed')

if __name__ == '__main__':
    unittest.main()

