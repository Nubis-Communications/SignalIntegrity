"""
TestVNACalibrationObject.py
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
import SignalIntegrity.App as siapp

import os

from numpy import matrix,identity
import math

class TestVNACalibrationObjectTest(unittest.TestCase,
        si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper):
    resDict=None
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    def testSIUnits(self):
        unit='e-27 F/Hz'
        number=-310.13
        print(siapp.ToSI.ToSI(number,unit))
        print(siapp.ToSI.FromSI(str(number)),unit)
