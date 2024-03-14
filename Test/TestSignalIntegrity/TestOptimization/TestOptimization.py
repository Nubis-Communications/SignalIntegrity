"""
TestOptimization.py
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
import SignalIntegrity.Lib as si
from numpy import linalg, array


class TestOptimizationTest(unittest.TestCase, si.test.SourcesTesterHelper):

    def testOptimizationSymbolic(self):

        sdp = si.p.SystemDescriptionParser()
        sdp.AddLines(['device SL 2', 'device SR 2', 'device SB 2', 'device G1 1 open', 'device G2 1 open',
                      'port 1 SL 1 2 SR 2',
                      'connect SL 2 SR 1', 'connect G1 1 SB 1', 'connect G2 1 SB 2'])
        ssps = si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
                                             docstart='\\documentclass[10pt]{article}\n' + '\\usepackage{amsmath}\n' + \
                                            '\\usepackage{bbold}\n' + '\\usepackage[paperwidth=8.5in,paperheight=11in]{geometry}\n' + '\\begin{document}')
        ssps.DocStart()
        ssps.LaTeXSolution()
        ssps.DocEnd()
        ssps.Emit()
        self.CheckSymbolicResult(self.id(), ssps, 'optimization result')

    def testOptimizationNumeric(self):
        f = si.fd.EvenlySpacedFrequencyList(50e9, 20)
        ssnp = si.p.SystemSParametersNumericParser(f=f)
        ssnp.AddLines(['device T1 2 tline zc 50.0 td 10.0e-12',
                      'device T2 2 tline zc 50.0 td 10.0e-12',
                      'device T3 2 tline zc 50.0 td 10.0e-12',
                      'device G1 1 open',
                      'device O1 1 open',
                      'port 1 td 0 T1 1',
                      'port 2 td 0 T2 2',
                      'connect T1 2 T2 1',
                      'connect T3 1 G1 1',
                      'connect T3 2 O1 1'])
        sp = ssnp.SParameters()
        spCorrect = si.sp.dev.TLineLossless(f, 2, 50, 20e-12)
        difference = linalg.norm(array(spCorrect) - array(sp))
        self.assertTrue(difference < 1e-15, 'Optimization incorrect')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
