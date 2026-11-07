"""
TestIXT.py
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

class TestIXTTest(unittest.TestCase,
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
    def IXT_args():
        return {'port_reorder':'1,2,3,4,16,15,14,13','single_ended_ports':'1,2,5,6,3,4,7,8',
                'reference_impedance':'46.25,50','voltage_transfer_function':'True','victim_ports':'1,2','aggressor_ports':'3,2',
                'end_frequency':'55e9','frequency_points':'40','total_aggressor_lanes':'8'}
    def IXT_args_for_calculator(self):
        args=self.IXT_args()
        args['port_reorder']=eval('['+args['port_reorder']+']')
        args['single_ended_ports']=eval('['+args['single_ended_ports']+']')
        args['reference_impedance']=eval('['+args['reference_impedance']+']')
        args['victim_ports']=eval('['+args['victim_ports']+']')
        args['aggressor_ports']=eval('['+args['aggressor_ports']+']')
        args['voltage_transfer_function']=eval(args['voltage_transfer_function'])
        args['end_frequency']=eval(args['end_frequency'])
        args['frequency_points']=eval(args['frequency_points'])
        return args
    def testIXTSubprocess(self):
        import subprocess
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/IXT/IXT.py', os.path.dirname(__file__)))
        file_name='nitro_9-13-24b-tx1_4_HFSS-sig1p0_res.s16p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        cmd_str=self.python+' -u '+script_file+' '+file_name
        ixt_args=self.IXT_args()
        for key in ixt_args:
            cmd_str += ' --'+key+' '+str(ixt_args[key])
        result = subprocess.getoutput(cmd_str)
        result_dB = ToSI(float(result),'dB',round=5)
        # print('result: ',result_dB)
        target = '-41.111 dB'
        self.assertEqual(result_dB, target, 'IXT produced incorrect value')
    def testIXTSubprocessMissingSp(self):
        import subprocess
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/IXT/IXT.py', os.path.dirname(__file__)))
        file_name='missing.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        cmd_str=self.python+' -u '+script_file+' '+file_name
        ixt_args=self.IXT_args()
        for key in ixt_args:
            cmd_str += ' --'+key+' '+ixt_args[key]
        result = subprocess.getoutput(cmd_str)
        self.assertTrue(result=='error','result should be error')
    def formIXTMain_argv(self,missing=[],replace={}):
        import sys
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/IXT/IXT.py', os.path.dirname(__file__)))
        file_name='nitro_9-13-24b-tx1_4_HFSS-sig1p0_res.s16p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        ixt_args=self.IXT_args()
        sys.argv=[script_file,file_name]
        for key in ixt_args:
            value=ixt_args[key]
            if key in replace:
                value=replace[key]
            if key not in missing:
                sys.argv.append('--'+key)
                sys.argv.append(value)
            # sys.argv.append('-d')
    def testIXTMain(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv()
        try:
            IXT_Main()
        except SystemExit as e:
            self.assertEqual(e.code,0,'IXT_Main did not exit properly') # exited correctly
            return
        self.fail('IXT should have exited with SystemExit exception raised')
    def testIXTMainNoFile(self):
        import sys
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv()
        sys.argv[1]='none.s4p'
        try:
            IXT_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'IXT_Main did not exit properly') # should fail
            return
        self.fail('IXT should have exited with SystemExit exception raised')
    def testIXTMainUnknownKeyword(self):
        import sys
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv()
        sys.argv=[sys.argv[0],'-unknown']
        try:
            IXT_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'IXT_Main did not exit properly') # failed
            return
        self.fail('IXT should have exited with SystemExit exception raised')
    def testIXTMainBadPortReorder(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv(['port_reorder'])
        import sys
        sys.argv.append('--port_reorder')
        sys.argv.append(self.IXT_args()['port_reorder']+',100')
        try:
            IXT_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'IXT_Main did not exit properly') # should fail
            return
        self.fail('IXT should have exited with SystemExit exception raised')
    def testIXTMainUnevenSingleEndedPorts(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv(['single_ended_ports'])
        import sys
        sys.argv.append('--single_ended_ports')
        sys.argv.append(self.IXT_args()['single_ended_ports']+',100')
        try:
            IXT_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'IXT_Main did not exit properly') # should fail
            return
        self.fail('IXT should have exited with SystemExit exception raised')
    def testIXTMainBadSingleEndedPorts(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv(['single_ended_ports'])
        import sys
        sys.argv.append('--single_ended_ports')
        sys.argv.append(self.IXT_args()['single_ended_ports']+',100,200')
        try:
            IXT_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'IXT_Main did not exit properly') # should fail
            return
        self.fail('IXT should have exited with SystemExit exception raised')
    def testIXTMainMissingFeN(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv(['end_frequency','frequency_points'])
        try:
            IXT_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'IXT_Main did not exit properly') # should fail
            return
        self.fail('IXT should have exited with SystemExit exception raised')
    def testIXTMainNoZ0(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv(['reference_impedance'])
        try:
            result = IXT_Main()
        except SystemExit as e:
            self.assertEqual(e.code,0,'IXT_Main did not exit properly') # should succeed
            return
        self.fail('IXT should have exited with SystemExit exception raised')
    def testIXTMainSingleZ0(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv(replace={'reference_impedance':'46.25'})
        try:
            result = IXT_Main()
        except SystemExit as e:
            self.assertEqual(e.code,0,'IXT_Main did not exit properly') # should succeed
            return
        self.fail('IXT should have exited with SystemExit exception raised')
    def testIXTMainTooManyZ0(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv(replace={'reference_impedance':'46.25,50,50'})
        try:
            result = IXT_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'IXT_Main did not exit properly') # should fail
            return
        self.fail('IXT should have exited with SystemExit exception raised')
    def testIXTMainaNonNumericZ0(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv(replace={'reference_impedance':'Z0'})
        try:
            result = IXT_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'IXT_Main did not exit properly') # should fail
            return
        self.fail('IXT should have exited with SystemExit exception raised')
    def testIXTMainProfile(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv()
        import sys
        sys.argv.append('-p')
        try:
            IXT_Main()
        except SystemExit as e:
            self.assertEqual(e.code,0,'IXT_Main did not exit properly') # should succeed
            return
        self.fail('IXT should have exited with SystemExit exception raised')
    def testIXTMainProfileFailure(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv(['end_frequency'])
        import sys
        sys.argv.append('-p')
        try:
            IXT_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'IXT_Main did not exit properly') # should fail
            return
        self.fail('IXT should have exited with SystemExit exception raised')
    def testIXTMainMissingN(self):
        import sys
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv(['frequency_points'])
        sys.argv.append('-v')
        try:
            IXT_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'IXT_Main did not exit properly') # should fail
            return
        self.fail('IXT should have exited with SystemExit exception raised')
    def testIXTMainBadN(self):
        import sys
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main
        self.formIXTMain_argv(replace={'frequency_points':'50kHz'})
        #sys.argv.append('-v')
        #sys.argv.append('-p')
        if self.python == 'python3': # linux
            output = '/dev/null'
        else: # windows
            output = 'nul'
        with open(output,'w') as f:
            from contextlib import redirect_stderr
            with redirect_stderr(f):
                try:
                    IXT_Main()
                except SystemExit as e:
                    self.assertEqual(e.code,2,'IXT_Main did not exit properly') # should fail
                    return
                finally:
                    import os
                    try:
                        os.remove('NULL')
                    except FileNotFoundError:
                        pass
        self.fail('IXT should have exited with SystemExit exception raised')

    def testIXTMainBadTotalAggressorLanes(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Main

        for total_aggressor_lanes in ['0', '-1', 'not-a-number', '8,8']:
            self.formIXTMain_argv(replace={'total_aggressor_lanes':total_aggressor_lanes})
            with self.assertRaises(SystemExit) as exception:
                IXT_Main()
            self.assertEqual(exception.exception.code, 1)
    def testIXTPythonScript(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Calculator
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/IXT/IXT.py', os.path.dirname(__file__)))
        file_name='nitro_9-13-24b-tx1_4_HFSS-sig1p0_res.s16p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        ixt_args=self.IXT_args_for_calculator()
        ixt_args['filename']=file_name
        result = IXT_Calculator(**ixt_args)
        result_dB = ToSI(result['ixt'],'dB',round=5)
        # print('result: ',result_dB)
        target = '-41.111 dB'
        self.assertEqual(result_dB, target, 'IXT produced incorrect value')
    def testIXTPythonScriptNoVt(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Calculator
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/IXT/IXT.py', os.path.dirname(__file__)))
        file_name='nitro_9-13-24b-tx1_4_HFSS-sig1p0_res.s16p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        ixt_args=self.IXT_args_for_calculator()
        ixt_args['filename']=file_name
        ixt_args['voltage_transfer_function']=False
        result = IXT_Calculator(**ixt_args)
        result_dB = ToSI(result['ixt'],'dB',round=5)
        # print('result: ',result_dB)
        target = '-41.401 dB'
        self.assertEqual(result_dB, target, 'IXT produced incorrect value')
    def testIXTPythonScriptNoVtError(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Calculator
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/IXT/IXT.py', os.path.dirname(__file__)))
        file_name='nitro_9-13-24b-tx1_4_HFSS-sig1p0_res.s16p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        ixt_args=self.IXT_args_for_calculator()
        ixt_args['filename']=file_name
        ixt_args['voltage_transfer_function']=False
        ixt_args['aggressor_ports']=[9,2]
        #result = IXT_Calculator(**ixt_args)
        with self.assertRaises(Exception) as cme:
            IXT_Calculator(**ixt_args)
    def testIXTPythonScriptVtError(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Calculator
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/IXT/IXT.py', os.path.dirname(__file__)))
        file_name='nitro_9-13-24b-tx1_4_HFSS-sig1p0_res.s16p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        ixt_args=self.IXT_args_for_calculator()
        ixt_args['filename']=file_name
        ixt_args['aggressor_ports']=[9,2]
        #result = IXT_Calculator(**ixt_args)
        with self.assertRaises(Exception) as cme:
            IXT_Calculator(**ixt_args)
    def testIXTPythonScriptMissingSp(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Calculator
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/IXT/IXT.py', os.path.dirname(__file__)))
        file_name='nitro_9-13-24b-tx1_4_HFSS-sig1p0_res.s16p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        ixt_args=self.IXT_args_for_calculator()
        #ixt_args['filename']=file_name
        ixt_args['end_frequency']=float(ixt_args['end_frequency'])
        ixt_args['frequency_points']=int(ixt_args['frequency_points'])
        #result = IXT_Calculator(**ixt_args)
        with self.assertRaises(Exception) as cme:
            IXT_Calculator(**ixt_args)
    def testIXTPythonScriptUnknownKeyword(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Calculator
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/IXT/IXT.py', os.path.dirname(__file__)))
        file_name='nitro_9-13-24b-tx1_4_HFSS-sig1p0_res.s16p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        ixt_args=self.IXT_args_for_calculator()
        ixt_args['filename']=file_name
        ixt_args['gobbledygook']=32.54
        #result = IXT_Calculator(**ixt_args)
        with self.assertRaises(Exception) as cme:
            IXT_Calculator(**ixt_args)

    def testIXTTotalAggressorLaneScaling(self):
        from SignalIntegrity.Utilities.IXT.IXT import IXT_Calculator

        class FakeFrequencyResponse:
            def Frequencies(self):
                return [0., 1.]

            def Values(self, value_type):
                return [1., 1.] if value_type == 'mag' else None

        victim = FakeFrequencyResponse()
        aggressors = [FakeFrequencyResponse(), FakeFrequencyResponse()]
        single_lane_result = IXT_Calculator.IXT(victim, aggressors, 1.)
        total_lane_result = IXT_Calculator.IXT(victim, aggressors, 1., 8)
        fractional_lane_result = IXT_Calculator.IXT(victim, aggressors, 1., 2.5)
        single_value_list_result = IXT_Calculator.IXT(victim, aggressors, 1., [8])
        per_lane_result = IXT_Calculator.IXT(victim, aggressors, 1., [4, 8])

        self.assertAlmostEqual(total_lane_result - single_lane_result, 10. * math.log10(8.))
        self.assertAlmostEqual(fractional_lane_result - single_lane_result, 10. * math.log10(2.5))
        self.assertAlmostEqual(single_value_list_result, total_lane_result)
        self.assertAlmostEqual(per_lane_result - single_lane_result, 10. * math.log10((4. + 8.) / 2.))

        with self.assertRaises(ValueError):
            IXT_Calculator.IXT(victim, aggressors, 1., [8, 8, 8])
        with self.assertRaises(ValueError):
            IXT_Calculator.IXT(victim, aggressors, 1., [0, 8])
        with self.assertRaises(ValueError):
            IXT_Calculator.IXT(victim, aggressors, 1., [-1, 8])
        with self.assertRaises(ValueError):
            IXT_Calculator.IXT(victim, aggressors, 1., ['invalid', 8])

if __name__ == '__main__': # pragma: no cover
    unittest.main()
