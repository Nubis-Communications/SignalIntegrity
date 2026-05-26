"""
TestTD.py
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

class TestTDTest(unittest.TestCase,
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
    def TD_args():
        return {#'port_reorder':'1,2,3,4,16,15,14,13',
                'lane_number':'4',
                'ic_type':'tia',
                'end_frequency':'65e9',
                'frequency_points':'928',
                'output_file':'testoutput'
        }
    def TD_args_for_calculator(self):
        args=self.TD_args()
        #args['port_reorder']=eval('['+args['port_reorder']+']')
        args['lane_number']=eval(args['lane_number'])
        args['ic_type']=args['ic_type']
        args['output_file']=args['output_file']
        args['end_frequency']=eval(args['end_frequency'])
        args['frequency_points']=eval(args['frequency_points'])
        return args
    def testTDSubprocess(self):
        import subprocess
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/TD/TD.py', os.path.dirname(__file__)))
        file_name='testfile.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        cmd_str=self.python+' -u '+script_file+' '+file_name
        td_args=self.TD_args()
        for key in td_args:
            cmd_str += ' --'+key+' '+str(td_args[key])
        result = subprocess.getoutput(cmd_str)
        self.assertEqual(result, 'success', 'TD failed')
    def testTDSubprocessMissingSp(self):
        import subprocess
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/TD/TD.py', os.path.dirname(__file__)))
        file_name='missing.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        cmd_str=self.python+' -u '+script_file+' '+file_name
        td_args=self.TD_args()
        for key in td_args:
            cmd_str += ' --'+key+' '+td_args[key]
        result = subprocess.getoutput(cmd_str)
        self.assertTrue(result=='error','result should be error')
    def formTDMain_argv(self,missing=[],replace={}):
        import sys
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/TD/TD.py', os.path.dirname(__file__)))
        file_name='testfile.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        td_args=self.TD_args()
        sys.argv=[script_file,file_name]
        for key in td_args:
            value=td_args[key]
            if key in replace:
                value=replace[key]
            if key not in missing:
                sys.argv.append('--'+key)
                sys.argv.append(value)
            # sys.argv.append('-d')
    def testTDMain(self):
        from SignalIntegrity.Utilities.TD.TD import TD_Main
        self.formTDMain_argv()
        try:
            TD_Main()
        except SystemExit as e:
            self.assertEqual(e.code,0,'TD_Main did not exit properly') # exited correctly
            return
        self.fail('TD should have exited with SystemExit exception raised')
    def testTDMainNoFile(self):
        import sys
        from SignalIntegrity.Utilities.TD.TD import TD_Main
        self.formTDMain_argv()
        sys.argv[1]='none.s4p'
        try:
            TD_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'TD_Main did not exit properly') # should fail
            return
        self.fail('TD should have exited with SystemExit exception raised')
    def testTDMainUnknownKeyword(self):
        import sys
        from SignalIntegrity.Utilities.TD.TD import TD_Main
        self.formTDMain_argv()
        sys.argv=[sys.argv[0],'-unknown']
        try:
            TD_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'TD_Main did not exit properly') # failed
            return
        self.fail('TD should have exited with SystemExit exception raised')
    def testTDMainMissingFeN(self):
        from SignalIntegrity.Utilities.TD.TD import TD_Main
        self.formTDMain_argv(['end_frequency','frequency_points'])
        try:
            TD_Main()
        except SystemExit as e:
            self.assertEqual(e.code,0,'TD_Main did not exit properly') # should pass
            return
        self.fail('TD should have exited with SystemExit exception raised')
    def testTDMainMissingICtype(self):
        from SignalIntegrity.Utilities.TD.TD import TD_Main
        self.formTDMain_argv(['ic_type'])
        try:
            TD_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'TD_Main did not exit properly') # should fail
            return
        self.fail('TD should have exited with SystemExit exception raised')
    def testTDMainProfile(self):
        from SignalIntegrity.Utilities.TD.TD import TD_Main
        self.formTDMain_argv()
        import sys
        sys.argv.append('-p')
        try:
            TD_Main()
        except SystemExit as e:
            self.assertEqual(e.code,0,'TD_Main did not exit properly') # should succeed
            return
        self.fail('TD should have exited with SystemExit exception raised')
    def testTDMainProfileFailure(self):
        from SignalIntegrity.Utilities.TD.TD import TD_Main
        self.formTDMain_argv(['lane_number'])
        import sys
        sys.argv.append('-p')
        try:
            TD_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'TD_Main did not exit properly') # should fail
            return
        self.fail('TD should have exited with SystemExit exception raised')
    def testTDMainMissingN(self):
        import sys
        from SignalIntegrity.Utilities.TD.TD import TD_Main
        self.formTDMain_argv(['frequency_points'])
        sys.argv.append('-v')
        try:
            TD_Main()
        except SystemExit as e:
            self.assertEqual(e.code,0,'TD_Main did not exit properly') # should pass
            return
        self.fail('TD should have exited with SystemExit exception raised')
    def testTDMainBadN(self):
        import sys
        from SignalIntegrity.Utilities.TD.TD import TD_Main
        self.formTDMain_argv(replace={'frequency_points':'50kHz'})
        #sys.argv.append('-v')
        #sys.argv.append('-p')
        try:
            TD_Main()
        except SystemExit as e:
            self.assertEqual(e.code,2,'TD_Main did not exit properly') # should fail
            return
        self.fail('TD should have exited with SystemExit exception raised')
    def testTDMainBadICType(self):
        import sys
        from SignalIntegrity.Utilities.TD.TD import TD_Main
        self.formTDMain_argv(replace={'ic_type':'gobbledygook'})
        #sys.argv.append('-v')
        #sys.argv.append('-p')
        try:
            TD_Main()
        except SystemExit as e:
            self.assertEqual(e.code,1,'TD_Main did not exit properly') # should fail
            return
        self.fail('TD should have exited with SystemExit exception raised')
    def testTDPythonScript(self):
        from SignalIntegrity.Utilities.TD.TD import TD_Calculator
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/TD/TD.py', os.path.dirname(__file__)))
        file_name='testfile.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        td_args=self.TD_args_for_calculator()
        td_args['filename']=file_name
        result = TD_Calculator(**td_args)
        self.SParameterRegressionChecker(result.result, 'regression.s2p')
    def testTDPythonScriptMissingSp(self):
        from SignalIntegrity.Utilities.TD.TD import TD_Calculator
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/TD/TD.py', os.path.dirname(__file__)))
        file_name='testfile.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        td_args=self.TD_args_for_calculator()
        #td_args['filename']=file_name
        #result = TD_Calculator(**td_args)
        with self.assertRaises(Exception) as cme:
            TD_Calculator(**td_args)
    def testTDPythonScriptUnknownKeyword(self):
        from SignalIntegrity.Utilities.TD.TD import TD_Calculator
        script_file = os.path.abspath(os.path.relpath('../../../SignalIntegrity/Utilities/TD/TD.py', os.path.dirname(__file__)))
        file_name='testfile.s4p'
        file_name=os.path.join(os.path.dirname(__file__),file_name)
        td_args=self.TD_args_for_calculator()
        td_args['filename']=file_name
        td_args['gobbledygook']=32.54
        #result = TD_Calculator(**td_args)
        with self.assertRaises(Exception) as cme:
            TD_Calculator(**td_args)

if __name__ == '__main__': # pragma: no cover
    unittest.main()
