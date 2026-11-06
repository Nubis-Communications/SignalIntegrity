"""
TestPoleZeroFitter.py
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

import os
import SignalIntegrity.Lib as si
from SignalIntegrity.Utilities.PZ.PZ import PZ_Fitter

class TestPoleZeroFitterTest(unittest.TestCase,
                             si.test.SignalIntegrityAppTestHelper):
    def __init__(self, methodName='runTest'):
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    def tearDown(self):
        def remove_file(filename):
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass
        remove_file('./PZ.json')
        remove_file('./debug.s4p')
        remove_file('./test_goal.txt')
        remove_file('./test_result.txt')
        unittest.TestCase.tearDown(self)
        os.chdir(self.cwd)
    def FileNameForTest(self):
        return self.id().split('.')[-1]+'.json'
    def Compare(self,result):
        try:
            del result['convergence']['time']
        except KeyError:
            pass
        try:
            del result['convergence']['completed']
        except KeyError:
            pass
        # todo: I should not have to delete these, but they are not deterministic.
        try:
            del result['convergence']['iterations']
        except KeyError:
            pass
        try:
            del result['configuration']['debug']
        except KeyError:
            pass
        try:
            del result['configuration']['profile']
        except KeyError:
            pass
        try:
            del result['configuration']['verbose']
        except KeyError:
            pass
        filename=self.FileNameForTest()
        self.JsonDictRegressionChecker(result,filename)
    def testPZ(self):
        args={'filename': 'MM.s4p',
              'fit_type': 'magnitude',
              'debug': True,
              'profile': False,
              'verbose': False,
              'zero_pairs': 2,
              'pole_pairs': 4,
              'guess_file': None,
              'output_file': 'PZ.json',
              'end_frequency': 100000000000.0,
              'frequency_points': 40,
              'min_delay': 0.0,
              'max_delay': 0.0,
              'max_q': 10.0,
              'initial_delay': 0.0,
              'iterations': 'infinite',
              'precision': 'super',
              'real_zeros': False,
              'lhp_zeros': True,
              'voltage_transfer_function': True,
              'fix_gain': False,
              'fix_delay': True,
              'reference_impedance': 46.0,
              'max_iterations': None,
              'mse_unchanging_threshold': None,
              'initial_lambda': 1000.0,
              'lambda_multiplier': 2.0,
              'tolerance': 1e-07,
              'max_frequency_multiplier': 6}
        result=PZ_Fitter(**args)
        import matplotlib.pyplot as plt
        plt.close()
        self.Compare(result)
    def testPZ1(self):
        args={'filename': 'MM_s21.csv',
              'fit_type': 'complex',
              'debug': False,
              'profile': False,
              'verbose': False,
              'zero_pairs': 2,
              'pole_pairs': 4,
              'guess_file': 'guess.json',
              #'output_file': 'final.json',
              'end_frequency': 85000000000.0,
              'frequency_points': 20,
              'min_delay': 5e-12,
              'max_delay': 2e-11,
              'max_q': 10.0,
              'initial_delay': 1e-11,
              'iterations': 'infinite',
              'precision': 'super',
              'real_zeros': False,
              'lhp_zeros': True,
              'voltage_transfer_function': True,
              'fix_gain': True,
              'fix_delay': False,
              'reference_impedance': 46.0,
              'max_iterations': None,
              'mse_unchanging_threshold': None,
              'initial_lambda': 100000.0,
              'lambda_multiplier': 1.01,
              'tolerance': 1e-06,
              'max_frequency_multiplier': 5}
        result=PZ_Fitter(**args)
        self.Compare(result)
    def testPZ2(self):
        args={'filename': 'MM.s4p',
              'fit_type': 'complex',
              'debug': False,
              'profile': False,
              'verbose': False,
              'zero_pairs': 2,
              'pole_pairs': 4,
              'guess_file': None,
              #'output_file': 'final.json',
              'end_frequency': 85000000000.0,
              'frequency_points': 20,
              'min_delay': 5e-12,
              'max_delay': 2e-11,
              'max_q': 10.0,
              'initial_delay': 1e-11,
              'iterations': 'infinite',
              'precision': 'super',
              'real_zeros': False,
              'lhp_zeros': True,
              'voltage_transfer_function': True,
              'fix_gain': True,
              'fix_delay': False,
              'reference_impedance': 46.0,
              'max_iterations': None,
              'mse_unchanging_threshold': None,
              'initial_lambda': 100000.0,
              'lambda_multiplier': 1.01,
              'tolerance': 1e-06,
              'max_frequency_multiplier': 5}
        result=PZ_Fitter(**args)
        self.Compare(result)
    def testPZvgf(self):
        args={'filename': 'Fitted.s2p',
              'fit_type': 'magnitude',
              'debug': False,
              'profile': True,
              'verbose': True,
              'zero_pairs': 2,
              'pole_pairs': 4,
              'guess_file': None,
              'end_frequency': 100000000000.0,
              'frequency_points': 200,
              'min_delay': 0.0,
              'max_delay': 0.0,
              'max_q': 5.0,
              'initial_delay': 0.0,
              'iterations': 'infinite',
              'precision': 'super',
              'real_zeros': False,
              'lhp_zeros': False,
              'voltage_transfer_function': False,
              'fix_gain': False,
              'fix_delay': False,
              'reference_impedance': None,
              'max_iterations': None,
              'mse_unchanging_threshold': 1e-10,
              'initial_lambda': 100000.0,
              'lambda_multiplier': 1.01,
              'tolerance': 1e-06,
              'max_frequency_multiplier': 10.0}
        result=PZ_Fitter(**args)
        self.Compare(result)
    def baselineArgs(self):
        return {'filename': 'MM.s4p',
              'fit_type': 'magnitude',
              'debug': True,
              'profile': False,
              'verbose': False,
              'zero_pairs': 2,
              'pole_pairs': 4,
              'guess_file': None,
              'output_file': 'PZ.json',
              'end_frequency': 100000000000.0,
              'frequency_points': 40,
              'min_delay': 0.0,
              'max_delay': 0.0,
              'max_q': 10.0,
              'initial_delay': 0.0,
              'iterations': 'infinite',
              'precision': 'super',
              'real_zeros': False,
              'lhp_zeros': True,
              'voltage_transfer_function': True,
              'fix_gain': False,
              'fix_delay': True,
              'reference_impedance': 46.0,
              'max_iterations': None,
              'mse_unchanging_threshold': None,
              'initial_lambda': 1000.0,
              'lambda_multiplier': 2.0,
              'tolerance': 1e-06,
              'max_frequency_multiplier': 5}
    def testAAAWrongIterations(self):
        args=self.baselineArgs()
        args['iterations']='garbage'
        with self.assertRaises(Exception) as cme:
            PZ_Fitter(**args)
            print (cme.message)
    def testAAAWrongPrecision(self):
        args=self.baselineArgs()
        args['precision']='garbage'
        with self.assertRaises(Exception) as cme:
            PZ_Fitter(**args)
            print (cme.message)
    def testAAAExtraKey(self):
        args=self.baselineArgs()
        args['garbage']='garbage'
        with self.assertRaises(Exception) as cme:
            PZ_Fitter(**args)
            print (cme.message)
    def testAAAWrongFilenameCsv(self):
        args=self.baselineArgs()
        args['filename']='garbage.csv'
        with self.assertRaises(Exception) as cme:
            PZ_Fitter(**args)
            print (cme.message)
    def testAAAWrongFilenameS2P(self):
        args=self.baselineArgs()
        args['filename']='garbage.s2p'
        with self.assertRaises(Exception) as cme:
            PZ_Fitter(**args)
            print (cme.message)
    def testAAAWrongFilenameExtension(self):
        args=self.baselineArgs()
        args['filename']='garbage.xxx'
        with self.assertRaises(Exception) as cme:
            PZ_Fitter(**args)
            print (cme.message)
    def testAAANoEndFrequency(self):
        args=self.baselineArgs()
        del args['end_frequency']
        with self.assertRaises(Exception) as cme:
            PZ_Fitter(**args)
            print (cme.message)
    def testAAANoFrequencyPoints(self):
        args=self.baselineArgs()
        del args['frequency_points']
        with self.assertRaises(Exception) as cme:
            PZ_Fitter(**args)
            print (cme.message)
    def testAAAWrongGuessFileJson(self):
        args=self.baselineArgs()
        args['guess_file'] = 'garbage.json'
        with self.assertRaises(Exception) as cme:
            PZ_Fitter(**args)
            print (cme.message)
    def testAAAWrongGuessFileTxt(self):
        args=self.baselineArgs()
        args['guess_file'] = 'garbage.txt'
        with self.assertRaises(Exception) as cme:
            PZ_Fitter(**args)
            print (cme.message)
    def testAAANoZeroPairs(self):
        args=self.baselineArgs()
        del args['zero_pairs']
        with self.assertRaises(Exception) as cme:
            PZ_Fitter(**args)
            print (cme.message)
    def testAAANoPolePairs(self):
        args=self.baselineArgs()
        del args['pole_pairs']
        with self.assertRaises(Exception) as cme:
            PZ_Fitter(**args)
            print (cme.message)
    def testAAAWrongFitType(self):
        args=self.baselineArgs()
        del args['max_delay']
        args['max_iterations'] = 100
        args['real_zeros'] = True
        args['fit_type'] = 'garbage'
        args['guess_file']='result.txt'
        with self.assertRaises(Exception) as cme:
            PZ_Fitter(**args)
            print (cme.message)
    def testAAACommandLine(self):
        import platform
        if platform.system() == 'Windows':
            correct_result = 1
            python = 'python'
        else: # assume Linux
            correct_result = 256
            python = 'python3'
        result = os.system(f'{python} ../../../SignalIntegrity/Utilities/PZ/PZ.py')
        self.assertEqual(result, correct_result, 'incorrect result')
    def testAAACommandLine2(self):
        from SignalIntegrity.Utilities.PZ.PZ import PZ_Main
        with self.assertRaises(SystemExit) as cme:
            import sys
            sys.argv=['PZ.py']
            PZ_Main()
            print (cme.message)
