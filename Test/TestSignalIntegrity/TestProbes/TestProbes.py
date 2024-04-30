"""
TestProbes.py
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
import os

class TestProbesTest(unittest.TestCase,si.test.SParameterCompareHelper,
                                 si.test.SignalIntegrityAppTestHelper,
                                 si.test.SourcesTesterHelper):
    relearn=True
    debug=False
    checkPictures=True
    keepNewFormats=False
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        unittest.TestCase.__init__(self,methodName)

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd=os.getcwd()
        os.chdir(self.path)
        self.book=os.path.exists('../../../../SignalIntegrityBook/')
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        self.UseSinX=SignalIntegrity.App.Preferences['Calculation.UseSinX']
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=False
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

    def testProbes(self):
        self.SimulationResultsChecker('ProbeTestProject.si')

    def testIdealCurrentToVoltageConverterSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D1 4','device G1 1 ground','port 1 td 0 D1 1',
        'port 2 td 0 D1 2','port 3 td 0 D1 3','connect D1 4 G1 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
        ssps.AssignSParameters('D1',si.sy.TransresistanceAmplifier(4,'1','0','0'))
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current To Voltage Symbolic')

    def testIdealVoltageToVoltageConverterSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D1 4','device G1 1 ground','port 1 td 0 D1 2',
        'port 2 td 0 D1 1','port 3 td 0 D1 3','connect D1 4 G1 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
        ssps.AssignSParameters('D1',si.sy.VoltageAmplifier(4,'1','Zi','0'))
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Current To Voltage Symbolic')

    def testIdealCurrentToVoltageConverterSimplificationNumeric(self):
        pass
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()