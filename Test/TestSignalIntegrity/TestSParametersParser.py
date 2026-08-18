"""
TestSParametersParser.py
"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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
import SignalIntegrity.Lib as si

class TestSParametersParserTest(unittest.TestCase,si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper):
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
    def setUp(self):
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    def tearDown(self):
        os.chdir(self.cwd)
    def id(self):
        return '_'.join(unittest.TestCase.id(self).split('.')[-2:])
    def testSParameterParserWithFiles(self):
        """
        The object of this test is to test whether known devices installed in the SParameter parser
        get recognized and used properly without error and produce the same result whether the device
        gets read from the disk and resampled at s-parameter generation time.
        """
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1'])
        sp=sspnp.SParameters()

        sspnp2=si.p.SystemSParametersNumericParser(fd)
        sspnp2.AddLines(['device D1 2 cable thing',
                        'device D2 2 dbi filter',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1'])

        deviceList={'2 cable thing':si.sp.SParameterFile('cable.s2p').Resample(fd),
                    '2 dbi filter':si.sp.SParameterFile('filter.s2p').Resample(fd)}
        sspnp2.AddKnownDevices(deviceList)
        sp2=sspnp2.SParameters()

        self.assertTrue(self.SParametersAreEqual(sp,sp2,0.001),self.id()+' result not same')
    def testSParametersPostCausal(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post enforce reciprocity',
                        'post enforce passivity',
                        'post enforce causality',
                        'post limit none none',])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def testSParametersPostBoth(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post enforce both',
                        'post limit none none'])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def testSParametersGarbage(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'garbage'])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def testSParametersPostGarbage(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post garbage'])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sspnp.SParameters()
        self.assertEqual(cm.exception.parameter,si.SignalIntegrityExceptionPostProcessing().parameter)
    def testSParametersPostEnforceGarbage(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post enforce garbage'])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sspnp.SParameters()
        self.assertEqual(cm.exception.parameter,si.SignalIntegrityExceptionPostProcessing().parameter)
    def testSParametersPostReference(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post reference'])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sspnp.SParameters()
        self.assertEqual(cm.exception.parameter,si.SignalIntegrityExceptionPostProcessing().parameter)
    def testSParametersPostReferenceGarbage(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post reference garbage'])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sspnp.SParameters()
        self.assertEqual(cm.exception.parameter,si.SignalIntegrityExceptionPostProcessing().parameter)
    def testSParametersPostReferenceImpedance(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post reference impedance'])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sspnp.SParameters()
        self.assertEqual(cm.exception.parameter,si.SignalIntegrityExceptionPostProcessing().parameter)
    def testSParametersPostReferenceImpedanceGarbage(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post reference impedance garbage'])
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sspnp.SParameters()
        self.assertEqual(cm.exception.parameter,si.SignalIntegrityExceptionPostProcessing().parameter)
    def testSParametersReferenceImpedance30(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post reference impedance 30'])
        sp=sspnp.SParameters().SetReferenceImpedance(50.)
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def testSParametersNewline(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        ''])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def testSParametersPostOffset(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post offset',])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def testSParametersPostOffsetAmount1(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post offset -5e-9',])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def testSParametersPostOffsetAmount2(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post offset -100e-12 500e-12',])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def testSParametersTaper(self):
        fd=si.fd.EvenlySpacedFrequencyList(40e9,800)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post taper 15e9 20e9',])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def testSParametersTaper2(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post taper 10e9',])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def testSParametersTaper3(self):
        fd=si.fd.EvenlySpacedFrequencyList(30e9,600)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post taper 10e9',])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def testSParametersTaper4(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post taper 30e9',])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def testSParametersTaper5(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post taper 30e9 10e9',])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def testSParametersTaper6(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1',
                        'post taper 30e9 40e9',])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    def PostProcessingParser(self,postLines=[],endFrequency=20e9,frequencyPoints=400):
        """builds the standard two device test netlist with optional post-processing lines"""
        fd=si.fd.EvenlySpacedFrequencyList(endFrequency,frequencyPoints)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device D1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 D1 1',
                        'port 2 D2 2',
                        'connect D1 2 D2 1']+postLines)
        return sspnp
    def PostProcessingExceptionChecker(self,postLines):
        """asserts that the post-processing lines supplied generate a post-processing exception"""
        sspnp=self.PostProcessingParser(postLines)
        with self.assertRaises(si.SignalIntegrityException) as cm:
            sspnp.SParameters()
        self.assertEqual(cm.exception.parameter,si.SignalIntegrityExceptionPostProcessing().parameter)
    def testSParametersPostEnforceAll(self):
        sp=self.PostProcessingParser(['post enforce all']).SParameters()
        spExpected=self.PostProcessingParser().SParameters().EnforceAll(causalityThreshold=10e-6,
                                                                       maxIterations=30,
                                                                       maxSingularValue=1.,
                                                                       preserveDC=False)
        self.assertTrue(self.SParametersAreEqual(sp,spExpected,1e-9),self.id()+' result not same')
    def testSParametersPostPreserveDC(self):
        sp=self.PostProcessingParser(['post preserve dc',
                                      'post enforce causality']).SParameters()
        spExpected=self.PostProcessingParser().SParameters().EnforceCausality(preserveDC=True)
        self.assertTrue(self.SParametersAreEqual(sp,spExpected,1e-9),self.id()+' result not same')
        spNotPreserved=self.PostProcessingParser(['post enforce causality']).SParameters()
        self.assertFalse(self.SParametersAreEqual(sp,spNotPreserved,1e-9),self.id()+' DC not preserved')
    def testSParametersPostPreserveDCUpperCase(self):
        sp=self.PostProcessingParser(['post preserve DC',
                                      'post enforce causality']).SParameters()
        spExpected=self.PostProcessingParser().SParameters().EnforceCausality(preserveDC=True)
        self.assertTrue(self.SParametersAreEqual(sp,spExpected,1e-9),self.id()+' result not same')
    def testSParametersPostPreserveGarbage(self):
        self.PostProcessingExceptionChecker(['post preserve garbage'])
    def testSParametersPostLimit(self):
        sp=self.PostProcessingParser(['post limit -100e-12 500e-12']).SParameters()
        spExpected=self.PostProcessingParser().SParameters().LimitImpulseResponseLength((-100e-12,500e-12))
        self.assertTrue(self.SParametersAreEqual(sp,spExpected,1e-9),self.id()+' result not same')
    def testSParametersPostPortReorder(self):
        sp=self.PostProcessingParser(['post port reorder 2,1']).SParameters()
        spExpected=self.PostProcessingParser().SParameters().PortReorder([2,1])
        self.assertTrue(self.SParametersAreEqual(sp,spExpected,1e-9),self.id()+' result not same')
    def testSParametersPostPortReorderNoChange(self):
        sp=self.PostProcessingParser(['post port reorder 1,2']).SParameters()
        spExpected=self.PostProcessingParser().SParameters()
        self.assertTrue(self.SParametersAreEqual(sp,spExpected,1e-9),self.id()+' result not same')
    def testSParametersPostPortGarbage(self):
        self.PostProcessingExceptionChecker(['post port garbage'])
    def testSParametersPostPortReorderGarbage(self):
        self.PostProcessingExceptionChecker(['post port reorder garbage'])
    def testSParametersPostPortReorderMissing(self):
        self.PostProcessingExceptionChecker(['post port reorder'])
    def testSParametersPostScaleRho(self):
        sp=self.PostProcessingParser(['post scale rho 0.5']).SParameters()
        spExpected=self.PostProcessingParser().SParameters().ScaleRho(0.5)
        self.assertTrue(self.SParametersAreEqual(sp,spExpected,1e-9),self.id()+' result not same')
    def testSParametersPostScaleRhoOtherSpellings(self):
        spExpected=self.PostProcessingParser().SParameters().ScaleRho(0.5)
        for rho in ['Rho','RHO']:
            sp=self.PostProcessingParser(['post scale '+rho+' 0.5']).SParameters()
            self.assertTrue(self.SParametersAreEqual(sp,spExpected,1e-9),self.id()+' result not same for '+rho)
    def testSParametersPostScaleGarbage(self):
        self.PostProcessingExceptionChecker(['post scale garbage'])
    def testSParametersPostScaleRhoGarbage(self):
        self.PostProcessingExceptionChecker(['post scale rho garbage'])
    def testSParametersPostScaleRhoMissing(self):
        self.PostProcessingExceptionChecker(['post scale rho'])
    def testSParametersPostScaleRhoVariable(self):
        """post-processing lines must have their variables resolved"""
        sp=self.PostProcessingParser(['var $scale$ 0.5',
                                      'post scale rho $scale$']).SParameters()
        spExpected=self.PostProcessingParser().SParameters().ScaleRho(0.5)
        self.assertTrue(self.SParametersAreEqual(sp,spExpected,1e-9),self.id()+' result not same')
    def testSParametersPostTaperVariable(self):
        """post-processing lines must have their variables resolved"""
        sp=self.PostProcessingParser(['var $ftaper$ 10e9',
                                      'post taper $ftaper$']).SParameters()
        spExpected=self.PostProcessingParser(['post taper 10e9']).SParameters()
        self.assertTrue(self.SParametersAreEqual(sp,spExpected,1e-9),self.id()+' result not same')
    def testSParametersPostWaveletDenoise(self):
        sp=self.PostProcessingParser(['post wavelet denoise 0.001']).SParameters()
        spExpected=self.PostProcessingParser().SParameters().WaveletDenoise(0.001)
        self.assertTrue(self.SParametersAreEqual(sp,spExpected,1e-9),self.id()+' result not same')
    def testSParametersPostWaveletDenoiseGarbage(self):
        self.PostProcessingExceptionChecker(['post wavelet denoise garbage'])
    def testSParametersPostWaveletDenoiseMissing(self):
        self.PostProcessingExceptionChecker(['post wavelet denoise'])
    def testSParametersPostTaperMissing(self):
        self.PostProcessingExceptionChecker(['post taper'])
    def testSParametersPostLimitMissing(self):
        self.PostProcessingExceptionChecker(['post limit'])
    def testSParametersPostComment(self):
        sp=self.PostProcessingParser(['post ! this is a comment']).SParameters()
        header=getattr(sp,'header',[])
        self.assertTrue(any('this is a comment' in line for line in header),
                        self.id()+' comment not in header: '+str(header))
    #@unittest.expectedFailure
    def testSParametersReferenceStartsWithP(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device P1 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 P1 1',
                        'port 2 D2 2',
                        'connect P1 2 D2 1',])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')
    #@unittest.expectedFailure
    def testSParametersReferenceStartsWithPTooShort(self):
        fd=si.fd.EvenlySpacedFrequencyList(20e9,400)
        sspnp=si.p.SystemSParametersNumericParser(fd)
        sspnp.AddLines(['device P 2 file cable.s2p',
                        'device D2 2 file filter.s2p',
                        'port 1 P 1',
                        'port 2 D2 2',
                        'connect P 2 D2 1',])
        sp=sspnp.SParameters()
        self.SParameterRegressionChecker(sp,self.id()+'.s2p')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()