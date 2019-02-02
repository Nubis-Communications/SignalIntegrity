"""
TestPRBS.py
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
import sys
import unittest
import SignalIntegrity.Lib as si

class TestPRBSTest(unittest.TestCase):
    def testPRBS7(self):
        prbs7Calc=si.prbs.PseudoRandomBitPattern(si.prbs.PseudoRandomBitPattern.Prbs7Polynomial()).Pattern()
        with open('prbs7.txt','rU' if sys.version_info.major < 3 else 'r') as f:
            prbs7Regression=[int(e) for e in f.readline().split()]
        self.assertEqual(prbs7Calc, prbs7Regression, 'prbs 7 failed')
