"""
TestERL.py
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
import math

import SignalIntegrity.Lib as si
import SignalIntegrity.App.SignalIntegrityAppHeadless as siapp
import numpy as np
import os

from SignalIntegrity.Lib.ToSI import ToSI,FromSI

class TestERLTest(unittest.TestCase,
        si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    epsilon=50e-12
    def setUp(self):
        unittest.TestCase.setUp(self)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
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
        import platform
        thisOS=platform.system()
        if thisOS == 'Linux':
            self.python = 'python3'
        else:
            self.python = 'python.exe'
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
    @staticmethod
    def ERL_Nitro_args():
        return {'port_reorder':'1,2,3,4','T_r':'10ps','beta_x':'0GHz','rho_x':'0.618','N':'800UI',
                'N_bx':'0','Z0':'100ohm','T_fx':'0s','f_b':'106.25GBaud','DER_0':'1e-6','phi':'10'}
    def testERLComMatlabPDF(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERLComMatlabPDF
        pdf = ERLComMatlabPDF.d_cpdf(0.1, [-0.2, 0.1, 0.2], [1.0, 2.0, 1.0])
        self.assertEqual(pdf['Min'], -2)
        np.testing.assert_allclose(pdf['y'], [0.25, 0.0, 0.0, 0.5, 0.25])
        self.assertAlmostEqual(np.sum(pdf['y']), 1.0)

        zero_mass_pdf = ERLComMatlabPDF.d_cpdf(0.1, [0.1, 0.2], [0.0, 0.0])
        self.assertEqual(np.sum(zero_mass_pdf['y']), 0.0)

        initialized_pdf = ERLComMatlabPDF.init_pdf_fast(pdf, [-0.1, 0.2], [0.25, 0.75])
        np.testing.assert_allclose(initialized_pdf['x'], [-0.1, 0.0, 0.1, 0.2])
        convolved_pdf = ERLComMatlabPDF.conv_fct(pdf, initialized_pdf)
        self.assertEqual(convolved_pdf['Min'], -3)
        self.assertEqual(len(convolved_pdf['x']), len(convolved_pdf['y']))

        with self.assertRaises(ValueError):
            ERLComMatlabPDF.conv_fct(pdf, {'BinSize': 0.2})
        with self.assertRaises(ValueError):
            ERLComMatlabPDF.get_pdf_from_sampled_signal([0.1], 2, 0.1, FAST_NOISE_CONV=1)

        empty_pdf = ERLComMatlabPDF.get_pdf_from_sampled_signal([], 2, 0.1)
        below_threshold_pdf = ERLComMatlabPDF.get_pdf_from_sampled_signal([0.01, -0.02], 2, 0.1)
        np.testing.assert_allclose(empty_pdf['y'], [1.0])
        np.testing.assert_allclose(below_threshold_pdf['y'], [1.0])

        sampled_pdf = ERLComMatlabPDF.get_pdf_from_sampled_signal([-0.2, 0.3], 2, 0.1)
        self.assertAlmostEqual(np.sum(sampled_pdf['y']), 1.0)

    def testERLInternalHelpers(self):
        from SignalIntegrity.Utilities.ERL.ERL import FindWaveformSupport,LinearlyInterpolate

        class Waveform:
            def __init__(self, values):
                self.values = values
                self.td = type('TimeDescriptor', (), {'K': len(values)})()
            def __getitem__(self, index):
                return self.values[index]

        self.assertEqual(FindWaveformSupport(Waveform([0.0, 0.1, 0.0, -0.2, 0.0]), 1e-5), (1, 3))
        self.assertEqual(FindWaveformSupport(Waveform([0.0, 1e-6]), 1e-5), (0, 0))
        self.assertEqual(LinearlyInterpolate(1.0, 1e-310, 2.0, 1e-6, 1e-8), 1.0)
        self.assertAlmostEqual(LinearlyInterpolate(1.0, 1e-2, 3.0, 1.0, 1e-1), 2.0)
    def testERLNitroSubprocess(self):
        import subprocess
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/ERL/ERL.py', os.path.dirname(__file__)))
        file_name='sparam_res.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        cmd_str=self.python+' -u '+script_file+' '+file_name
        nitro_args=self.ERL_Nitro_args()
        for key in nitro_args:
            cmd_str += ' -'+key+' '+nitro_args[key]
        for old_cdf, target in [(False, '9.4347 dB'), (True, '9.4066 dB')]:
            command = cmd_str if not old_cdf else cmd_str+' -ocdf'
            result = subprocess.getoutput(command)
            result_dB = ToSI(float(result),'dB',round=5)
            self.assertEqual(result_dB, target, 'ERL produced incorrect value')
    def testERLNitroSubprocessMissingSp(self):
        import subprocess
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/ERL/ERL.py', os.path.dirname(__file__)))
        file_name='missing.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        cmd_str=self.python+' -u '+script_file+' '+file_name
        nitro_args=self.ERL_Nitro_args()
        for key in nitro_args:
            cmd_str += ' -'+key+' '+nitro_args[key]
        result = subprocess.getoutput(cmd_str)
        self.assertTrue(result=='error','result should be error')
    def formERLMain_argv(self,missing=[],replace={}):
        import sys
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/ERL/ERL.py', os.path.dirname(__file__)))
        file_name='sparam_res.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        nitro_args=self.ERL_Nitro_args()
        sys.argv=[script_file,file_name]
        for key in nitro_args:
            value=nitro_args[key]
            if key in replace:
                value=replace[key]
            if key not in missing:
                sys.argv.append('-'+key)
                sys.argv.append(value)
            # sys.argv.append('-d')
        for key in replace:
            if key not in nitro_args and key not in missing:
                sys.argv.append('-'+key)
                sys.argv.append(replace[key])
    def testERLMain(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv()
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,0,'ERL_Main did not exit properly') # exited correctly
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainNoFile(self):
        import sys
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv()
        sys.argv[1]='none.s4p'
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainNoArgs(self):
        import sys
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv()
        sys.argv=[sys.argv[0]]
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # failed
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainUnknownKeyword(self):
        import sys
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv()
        sys.argv=[sys.argv[0],'-unknown']
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # failed
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainMissingPortReorder(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(['port_reorder'])
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,0,'ERL_Main did not exit properly') # should succeed
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainMissingTr(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(['T_r'])
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainTrUI(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(replace={'T_r':'1.0625UI'})
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,0,'ERL_Main did not exit properly') # should succeed
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainBadTr(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(replace={'T_r':'10Hz'})
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should succeed
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainMissingBetaX(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(['beta_x'])
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainBadBetaX(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(replace={'beta_x':'50lbs'})
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainMissingRhoX(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(['rho_x'])
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainBadRhoX(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(replace={'rho_x':'1UI'})
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainMissingN(self):
        import sys
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(['N'])
        sys.argv.append('-v')
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainBadN(self):
        import sys
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(replace={'N':'50kHz'})
        sys.argv.append('-v')
        sys.argv.append('-p')
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainMissingNBx(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(['N_bx'])
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainBadNBx(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(replace={'N_bx':'20GBaud'})
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainMissingZ0(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(['Z0'])
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,0,'ERL_Main did not exit properly') # should succeed
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainBadZ0(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(replace={'Z0':'20ps'})
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainMissingTFx(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(['T_fx'])
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,0,'ERL_Main did not exit properly') # should succeed
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainBadTFx(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(replace={'T_fx':'30kcycle'})
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainMissingFb(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(['f_b'])
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainBadFb(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(replace={'f_b':'200kbps'})
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainMissingDER0(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(['DER_0'])
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainBadDER0(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv(replace={'DER_0':'50UI'})
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainBadOptionalValues(self):
        from unittest.mock import patch
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        original_from_si = ERL_Main.__globals__['FromSI']
        def from_si(value, units):
            if value == 'invalid':
                return None
            return original_from_si(value, units)
        for argument in ['T_r','bps','phi','f_r']:
            with self.subTest(argument=argument):
                self.formERLMain_argv(replace={argument:'invalid'})
                try:
                    with patch.dict(ERL_Main.__globals__, {'FromSI': from_si}):
                        ERL_Main()
                except SystemExit as e:
                    self.assertEqual(e.code,1,'ERL_Main did not exit properly')
                    continue
                self.fail('ERL should have exited with SystemExit exception raised')
    def testERLPythonScript(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL
        file_name='sparam_res.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        nitro_args=self.ERL_Nitro_args()
        nitro_args['T_r'] = FromSI(nitro_args['T_r'],'s')
        nitro_args['beta_x'] = FromSI(nitro_args['beta_x'],'Hz')
        nitro_args['rho_x'] = FromSI(nitro_args['rho_x'],None)
        nitro_args['N'] = FromSI(nitro_args['N'],'UI')
        nitro_args['N_bx'] = FromSI(nitro_args['N_bx'],'UI')
        nitro_args['Z0'] = FromSI(nitro_args['Z0'],'ohm')
        nitro_args['T_fx'] = FromSI(nitro_args['T_fx'],'s')
        nitro_args['f_b'] = FromSI(nitro_args['f_b'],'Baud')
        nitro_args['DER_0'] = FromSI(nitro_args['DER_0'],None)
        nitro_args['phi'] = FromSI(nitro_args['phi'],None)
        result = ERL(file_name,nitro_args,verbose=True)
        result_dB = ToSI(float(result),'dB',round=5)
        # print('result: ',result_dB)
        target = '9.4347 dB'
        self.assertEqual(result_dB, target, 'ERL produced incorrect value')
        nitro_args['old_cdf'] = True
        old_cdf_result = ERL(file_name,nitro_args,verbose=True)
        old_cdf_result_dB = ToSI(float(old_cdf_result),'dB',round=5)
        self.assertEqual(old_cdf_result_dB, '9.4066 dB', 'ERL old CDF produced incorrect value')
    def testERLPythonScriptMissingSp(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL
        file_name='missing.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        nitro_args=self.ERL_Nitro_args()
        nitro_args['T_r'] = FromSI(nitro_args['T_r'],'s')
        nitro_args['beta_x'] = FromSI(nitro_args['beta_x'],'Hz')
        nitro_args['rho_x'] = FromSI(nitro_args['rho_x'],None)
        nitro_args['N'] = FromSI(nitro_args['N'],'UI')
        nitro_args['N_bx'] = FromSI(nitro_args['N_bx'],'UI')
        nitro_args['Z0'] = FromSI(nitro_args['Z0'],'ohm')
        nitro_args['T_fx'] = FromSI(nitro_args['T_fx'],'s')
        nitro_args['f_b'] = FromSI(nitro_args['f_b'],'Baud')
        nitro_args['DER_0'] = FromSI(nitro_args['DER_0'],None)
        nitro_args['phi'] = FromSI(nitro_args['phi'],None)
        with self.assertRaises(si.SignalIntegrityException) as cme:
            ERL(file_name,nitro_args,verbose=True)
    def testERLPythonScriptMissingKeyword(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL
        file_name='sparam_res.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        nitro_args=self.ERL_Nitro_args()
        nitro_args['T_r'] = FromSI(nitro_args['T_r'],'s')
        nitro_args['beta_x'] = FromSI(nitro_args['beta_x'],'Hz')
        nitro_args['rho_x'] = FromSI(nitro_args['rho_x'],None)
        nitro_args['N'] = FromSI(nitro_args['N'],'UI')
        nitro_args['N_bx'] = FromSI(nitro_args['N_bx'],'UI')
        nitro_args['Z0'] = FromSI(nitro_args['Z0'],'ohm')
        nitro_args['T_fx'] = FromSI(nitro_args['T_fx'],'s')
        nitro_args['f_b'] = FromSI(nitro_args['f_b'],'Baud')
        nitro_args['DER_0'] = FromSI(nitro_args['DER_0'],None)
        nitro_args['phi'] = FromSI(nitro_args['phi'],None)
        del nitro_args['T_r']
        with self.assertRaises(si.SignalIntegrityException) as cme:
            ERL(file_name,nitro_args,verbose=True)
    def testERLPythonScriptBias(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL
        file_name='sparam_res.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        nitro_args=self.ERL_Nitro_args()
        nitro_args['T_r'] = FromSI(nitro_args['T_r'],'s')
        nitro_args['beta_x'] = FromSI(nitro_args['beta_x'],'Hz')
        nitro_args['rho_x'] = FromSI(nitro_args['rho_x'],None)
        nitro_args['N'] = FromSI(nitro_args['N'],'UI')
        nitro_args['N_bx'] = FromSI(nitro_args['N_bx'],'UI')
        nitro_args['Z0'] = FromSI(nitro_args['Z0'],'ohm')
        nitro_args['T_fx'] = FromSI(nitro_args['T_fx'],'s')
        nitro_args['f_b'] = FromSI(nitro_args['f_b'],'Baud')
        nitro_args['DER_0'] = FromSI(nitro_args['DER_0'],None)
        nitro_args['phi'] = FromSI(nitro_args['phi'],None)
        bias = 0.4
        for old_cdf in [False, True]:
            nitro_args['old_cdf'] = old_cdf
            nitro_args.pop('bias', None)
            unbiased = ERL(file_name,nitro_args,verbose=True)
            nitro_args['bias'] = bias
            biased = ERL(file_name,nitro_args,verbose=True)
            # The bias (in dB) is subtracted directly from the selected CDF result.
            self.assertAlmostEqual(biased, unbiased-bias, 5,
                                   'ERL bias not applied correctly for old_cdf=%s' % old_cdf)
    def testERLPythonScriptWorstPhaseTruncation(self):
        from SignalIntegrity.Utilities.ERL.ERL import ERL
        file_name=os.path.join(os.path.dirname(__file__),'sparam_res.s4p')
        nitro_args=self.ERL_Nitro_args()
        for key, units in [('T_r','s'), ('beta_x','Hz'), ('rho_x',None), ('N','UI'),
                           ('N_bx','UI'), ('Z0','ohm'), ('T_fx','s'), ('f_b','Baud'),
                           ('DER_0',None), ('phi',None)]:
            nitro_args[key] = FromSI(nitro_args[key],units)
        nitro_args['old_cdf'] = True
        nitro_args['worst_phase_samples'] = 50
        self.assertTrue(np.isfinite(ERL(file_name,nitro_args,verbose=True)))
    def testERLMainBias(self):
        import sys
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv()
        sys.argv.append('-b')
        sys.argv.append('0.4')
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,0,'ERL_Main did not exit properly') # should succeed
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testERLMainBadBias(self):
        import sys
        from SignalIntegrity.Utilities.ERL.ERL import ERL_Main
        self.formERLMain_argv()
        sys.argv.append('-b')
        sys.argv.append('50UI')
        try:
            ERL_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'ERL_Main did not exit properly') # should fail
            return
        self.fail('ERL should have exited with SystemExit exception raised')
    def testCOMSincPulse(self):
        import shutil
        project_file = 'COM_SincPulse.si'
        project_file_source = os.path.join('../../../SignalIntegrity/Utilities/ERL/Projects/',project_file).replace('\\','/')
        project_file_dest = os.path.join(os.path.dirname(__file__),project_file).replace('\\','/')
        shutil.copy(project_file_source,project_file_dest)
        project_args={'f_b':FromSI('56 GBaud','Baud'),'EndFrequency':FromSI('280 GHz','Hz'),'FrequencyPoints':3357}
        try:
            self.SParameterResultsChecker(project_file,args=project_args)
        finally:
            os.remove(project_file_dest)
    def testCOMHt(self):
        import shutil
        project_file = 'COM_Ht.si'
        project_file_source = os.path.join('../../../SignalIntegrity/Utilities/ERL/Projects/',project_file).replace('\\','/')
        project_file_dest = os.path.join(os.path.dirname(__file__),project_file).replace('\\','/')
        shutil.copy(project_file_source,project_file_dest)
        project_args={'rt_2080':FromSI('10 ps','s'),'EndFrequency':FromSI('100 GHz','Hz'),'FrequencyPoints':100}
        try:
            self.SParameterResultsChecker(project_file,args=project_args)
        finally:
            os.remove(project_file_dest)
    def testCOMHr(self):
        import shutil
        project_file = 'COM_Hr.si'
        project_file_source = os.path.abspath(os.path.join('../../../SignalIntegrity/Utilities/ERL/Projects/',project_file)).replace('\\','/')
        project_file_dest = os.path.join(os.path.dirname(__file__),project_file).replace('\\','/')
        shutil.copy(project_file_source,project_file_dest)
        project_args={'f_r':FromSI('32.48 GHz','Hz'),'EndFrequency':FromSI('280 GHz','Hz'),'FrequencyPoints':3357}
        try:
            self.SParameterResultsChecker(project_file,args=project_args)
        finally:
            os.remove(project_file_dest)
    def testCOMTukey(self):
        import shutil
        project_file = 'COM_Tukey.si'
        project_file_source = os.path.abspath(os.path.join('../../../SignalIntegrity/Utilities/ERL/Projects/',project_file)).replace('\\','/')
        project_file_dest = os.path.join(os.path.dirname(__file__),project_file).replace('\\','/')
        shutil.copy(project_file_source,project_file_dest)
        project_args={'f_b':FromSI('106.25 GBaud','Baud'),'f_r':FromSI('61.625 GHz','Hz'),'EndFrequency':FromSI('280 GHz','Hz'),'FrequencyPoints':3357}
        try:
            self.SParameterResultsChecker(project_file,args=project_args)
        finally:
            os.remove(project_file_dest)
    def testERL_S11(self):
        import shutil
        project_file = 'ERL_S11.si'
        project_file_source = os.path.join('../../../SignalIntegrity/Utilities/ERL/Projects/',project_file).replace('\\','/')
        project_file_dest = os.path.join(os.path.dirname(__file__),project_file).replace('\\','/')
        shutil.copy(project_file_source,project_file_dest)
        file_name='sparam_res.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        project_args={'file_name':file_name,'EndFrequency':FromSI('531.25 GHz','Hz'),'FrequencyPoints':5312,'Zc':FromSI('50 ohm','ohm')}
        try:
            self.SParameterResultsChecker(project_file,args=project_args)
        finally:
            os.remove(project_file_dest)
    def testERL_S11_Impulse(self):
        import shutil
        project_file = 'ERL_S11_Impulse.si'
        project_file_source = os.path.abspath(os.path.join('../../../SignalIntegrity/Utilities/ERL/Projects/',project_file)).replace('\\','/')
        project_file_dest = os.path.abspath(os.path.join(os.path.dirname(__file__),project_file)).replace('\\','/')
        shutil.copy(project_file_source,project_file_dest)
        shutil.copy(os.path.join(os.path.dirname(project_file_source),'COM_Hr.si'),os.path.join(os.path.dirname(project_file_dest),'COM_Hr.si'))
        shutil.copy(os.path.join(os.path.dirname(project_file_source),'COM_Ht.si'),os.path.join(os.path.dirname(project_file_dest),'COM_Ht.si'))
        shutil.copy(os.path.join(os.path.dirname(project_file_source),'COM_SincPulse.si'),os.path.join(os.path.dirname(project_file_dest),'COM_SincPulse.si'))
        shutil.copy(os.path.join(os.path.dirname(project_file_source),'COM_Tukey.si'),os.path.join(os.path.dirname(project_file_dest),'COM_Tukey.si'))
        shutil.copy(os.path.join(os.path.dirname(project_file_source),'ERL_S11.si'),os.path.join(os.path.dirname(project_file_dest),'ERL_S11.si'))
        file_name='sparam_res.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        project_args={'file_name':file_name,'Z0':FromSI('50 ohm','ohm'),'f_b':FromSI('106.25 GBaud','Baud'),'T_r':FromSI('10 ps','s'),
                      'N':FromSI('800 UI','UI'),'phi':'10'}
        # prj=siapp.SignalIntegrityAppHeadless()
        # opened=prj.OpenProjectFile(project_file_dest, args=project_args)
        # self.assertTrue(opened,project_file_dest+' not opened')
        # prj.SaveProject()
        try:
            self.SimulationResultsChecker(project_file,args=project_args)
        finally:
            os.remove(project_file_dest)
            os.remove(os.path.join(os.path.dirname(project_file_dest),'COM_Hr.si'))
            os.remove(os.path.join(os.path.dirname(project_file_dest),'COM_Ht.si'))
            os.remove(os.path.join(os.path.dirname(project_file_dest),'COM_SincPulse.si'))
            os.remove(os.path.join(os.path.dirname(project_file_dest),'COM_Tukey.si'))
            os.remove(os.path.join(os.path.dirname(project_file_dest),'ERL_S11.si'))
    def testERL_S11_Error(self):
        erl_filter=si.td.wf.Waveform(si.td.wf.TimeDescriptor(7.529411764705808e-12,19,106250000000.0),
                                    [-0.03824090205322488,
                                    -0.0017673798447067645,
                                    -0.017308775197736305,
                                    -0.020241791812191216,
                                    0.02217477302791107,
                                    0.02734412559927596,
                                    0.01573951084549432,
                                    0.00956169284179282,
                                    0.0062909651783776815,
                                    0.004425108935951537,
                                    0.0029912201348524705,
                                    0.0019710483038461765,
                                    0.0013003169133326456,
                                    0.0008574162609356506,
                                    0.0005679674487956023,
                                    0.0003765542968370654,
                                    0.0002515539682546589,
                                    0.00017030850639692806,
                                    0.00011770543729302626]).WriteToFile('ERL_Filter.txt')
        import shutil
        project_file = 'ERL_S11_Error.si'
        project_file_source = os.path.abspath(os.path.join('../../../SignalIntegrity/Utilities/ERL/Projects/',project_file))
        project_file_dest = os.path.abspath(os.path.join(os.path.dirname(__file__),project_file))
        shutil.copy(project_file_source,project_file_dest)
        project_args={'Nbits':FromSI('2kbits','bits'),'f_b':FromSI('106.25 GBaud','Baud')}
        # prj=siapp.SignalIntegrityAppHeadless()
        # opened=prj.OpenProjectFile(project_file_dest, args=project_args)
        # self.assertTrue(opened,project_file_dest+' not opened')
        # prj.SaveProject()
        try:
            self.SimulationResultsChecker(project_file,args=project_args)
        finally:
            os.remove(project_file_dest)
            os.remove('ERL_Filter.txt')

if __name__ == '__main__': # pragma: no cover
    unittest.main()
