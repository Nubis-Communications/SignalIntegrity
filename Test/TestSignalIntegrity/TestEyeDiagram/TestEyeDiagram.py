"""
TestEyeDiagram.py
"""

# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# Copyright (c) 2021-2025 Nubis Communications, Inc.
# Copyright (c) 2026 Ciena, Inc.
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
import math
import SignalIntegrity.Lib as si
import numpy as np
import os

class TestEyeDiagramTest(unittest.TestCase,
        si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    epsilon=50e-12
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        #si.test.SignalIntegrityAppTestHelper.forceWritePictures=True
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        self.UseSinX=SignalIntegrity.App.Preferences['Calculation.UseSinX']
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=True
        self.TextLimit=SignalIntegrity.App.Preferences['Appearance.LimitText']
        SignalIntegrity.App.Preferences['Appearance.LimitText']=60
        self.RoundDisplayedValues=SignalIntegrity.App.Preferences['Appearance.RoundDisplayedValues']
        SignalIntegrity.App.Preferences['Appearance.RoundDisplayedValues']=4
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        os.chdir(self.cwd)
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=self.UseSinX
        SignalIntegrity.App.Preferences['Appearance.LimitText']=self.TextLimit
        SignalIntegrity.App.Preferences['Appearance.RoundDisplayedValues']=self.RoundDisplayedValues
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
    def testEyeUpsampleMethodControlsInterpolation(self):
        from unittest.mock import patch
        from SignalIntegrity.Lib.Eye.EyeDiagramBitmap import EyeDiagramBitmap
        from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionEyeDiagram

        waveform=si.td.wf.Waveform(si.td.wf.TimeDescriptor(-.13e-9,1024,4.e9),
                                 np.repeat(np.random.default_rng(42).choice([-1.,1.],256),4).tolist())
        waveform.adaptionStrategy='Linear'
        original=si.td.wf.Waveform(waveform)
        def makeEye(method):
            return EyeDiagramBitmap(Rows=64,Cols=30,BaudRate=1.e9,prbswf=waveform,
                                    YAxisMode='Fixed',YMin=-1.5,YMax=1.5,
                                    EnhancementMode='None',UpsampleMethod=method)

        bitmaps={}
        for globalMethod in ['SinX','Linear']:
            with self.subTest(globalMethod=globalMethod), \
                 patch.object(si.td.wf.Waveform,'adaptionStrategy',globalMethod):
                default=EyeDiagramBitmap(Rows=64,Cols=30,BaudRate=1.e9,prbswf=waveform,
                                         YAxisMode='Fixed',YMin=-1.5,YMax=1.5,EnhancementMode='None')
                sinx=makeEye('SinX')
                linear=makeEye('Linear')
                np.testing.assert_array_equal(default.Bitmap(),sinx.Bitmap())
                self.assertGreater(max(abs(value) for value in sinx.aprbswf),1.05)
                self.assertLessEqual(max(abs(value) for value in linear.aprbswf),1.+1.e-14)
                expected=np.interp(np.asarray(linear.aprbswf.Times())+.5e-9,
                                   waveform.Times(),waveform)
                np.testing.assert_allclose(linear.aprbswf,expected,rtol=0.,atol=2.e-12)
                self.assertGreater(np.max(np.abs(sinx.Bitmap()-linear.Bitmap())),.01)
                if bitmaps:
                    np.testing.assert_array_equal(sinx.Bitmap(),bitmaps['SinX'])
                    np.testing.assert_array_equal(linear.Bitmap(),bitmaps['Linear'])
                bitmaps={'SinX':sinx.Bitmap(),'Linear':linear.Bitmap()}
                self.assertEqual(si.td.wf.Waveform.adaptionStrategy,globalMethod)
                self.assertEqual(waveform.adaptionStrategy,'Linear')
                self.assertEqual(waveform.td,original.td)
                self.assertEqual(waveform,original)
        with self.assertRaises(SignalIntegrityExceptionEyeDiagram):
            makeEye('invalid')

    def testEyeUpsampleMethodInvalidatesCache(self):
        import tempfile
        from unittest.mock import patch
        from SignalIntegrity.Lib.Eye.EyeDiagramBitmap import EyeDiagramBitmap
        from SignalIntegrity.Lib.ResultsCache import ResultsCache

        waveform=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,512,4.e9),
                                 np.tile([-1.,-1.,1.,1.],128).tolist())
        with tempfile.TemporaryDirectory() as directory,patch.object(ResultsCache,'enabled',True):
            def makeEye(method):
                return EyeDiagramBitmap(cacheFileName=os.path.join(directory,'eye'),Rows=32,Cols=16,
                                        BaudRate=1.e9,prbswf=waveform,EnhancementMode='None',
                                        UpsampleMethod=method)

            sinx=makeEye('SinX')
            linear=makeEye('Linear')
            self.assertNotEqual(sinx.hash,linear.hash)
            with patch.object(si.td.wf.Waveform,'Adapt',
                              side_effect=AssertionError('unchanged eye should use cached bitmap')):
                cached=makeEye('Linear')
            np.testing.assert_array_equal(cached.Bitmap(),linear.Bitmap())
            self.assertEqual(cached.aprbswf,linear.aprbswf)

    def testEyeUpsampleMethodConfigurationAndGeneration(self):
        import xml.etree.ElementTree as ET
        from unittest.mock import patch
        from SignalIntegrity.App.EyeDiagramConfiguration import EyeDiagramConfiguration
        from SignalIntegrity.App.EyeDiagram import EyeDiagram
        from SignalIntegrity.Lib.Eye.EyeDiagramBitmap import EyeDiagramBitmap
        import SignalIntegrity.App as siapp

        config=EyeDiagramConfiguration().InitFromXML(ET.fromstring(
            '<EyeDiagram><Rows>32</Rows><Columns>16</Columns></EyeDiagram>'))
        waveform=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,512,4.e9),
                                 np.tile([-1.,-1.,1.,1.],128).tolist())
        for method in ['SinX','Linear']:
            with self.subTest(method=method):
                if method == 'Linear':
                    config['UpsampleMethod']=method
                    config=EyeDiagramConfiguration().InitFromXML(
                        ET.fromstring('\n'.join(config.OutputXML(''))))
                eye=EyeDiagram(None,'eye',headless=True)
                eye.config=config
                eye.prbswf=waveform
                eye.baudrate=1.e9
                with patch('SignalIntegrity.App.EyeDiagram.EyeDiagramBitmap',
                           wraps=EyeDiagramBitmap) as bitmap:
                    cacheEnabled=siapp.Preferences['Cache.CacheResults']
                    try:
                        siapp.Preferences['Cache.CacheResults']=False
                        eye.CalculateEyeDiagram('eye')
                    finally:
                        siapp.Preferences['Cache.CacheResults']=cacheEnabled
                self.assertEqual(bitmap.call_args.kwargs['UpsampleMethod'],method)
                self.assertEqual(eye.BitMap().shape,(32,16))

    def testEyeDiagram(self):
        self.SimulationEyeDiagramResultsChecker('EyeDiagramTest.si')
    def testEyeDiagramTransferMatrices(self):
        self.SimulationTransferMatricesResultsChecker('EyeDiagramTest.si')
    def testEyeDiagramJitterNoise(self):
        self.SimulationEyeDiagramResultsChecker('EyeDiagramTestJitterNoise.si')
    def testEyeDiagramJitterNoiseTransferMatrices(self):
        self.SimulationTransferMatricesResultsChecker('EyeDiagramTestJitterNoise.si')
    def testEyeDiagramJitterNoiseLog(self):
        self.SimulationEyeDiagramResultsChecker('EyeDiagramTestJitterNoiseLog.si')
    def testEyeDiagramJitterNoiseLogTransferMatrices(self):
        self.SimulationTransferMatricesResultsChecker('EyeDiagramTestJitterNoiseLog.si')
    def testMatPlotLib(self):
        result=self.SimulationEyeDiagramResultsChecker('EyeDiagramTest.si')
        eyeDiagrams=result['eye diagrams']
        eyeDiagramImages=[ed.Image() for ed in eyeDiagrams]
        eyeDiagramBitmaps=[ed.BitMap() for ed in eyeDiagrams]
    def testEyeDiagramNonlinear(self):
        self.SimulationEyeDiagramResultsChecker('EyeDiagramNonLinear.si')
    def testPRBSTest(self):
        self.SimulationEyeDiagramResultsChecker('../../../SignalIntegrity/App/Examples/HDMICable/PRBSTest.si')

if __name__ == "__main__": # pragma: no cover
    runProfiler=False

    if runProfiler:
        import cProfile
        cProfile.run('unittest.main()','stats')

        import pstats
        p = pstats.Stats('stats')
        p.strip_dirs().sort_stats('cumulative').print_stats(30)
    else:
        unittest.main()
