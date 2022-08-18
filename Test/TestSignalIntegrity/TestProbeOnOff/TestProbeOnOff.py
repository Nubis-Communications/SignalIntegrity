"""
TestProbeOnOff.py
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
import os
import shutil

from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
import SignalIntegrity.Lib as si


class TestProbeOnOffTest(unittest.TestCase,
                         si.test.SParameterCompareHelper,
                         si.test.SignalIntegrityAppTestHelper):
    relearn = True
    debug = False
    checkPictures = True
    keepNewFormats = False
    ProbeNames = ['EyeIn', 'I', 'Vd', 'EyeOut', 'Vin', 'Eye', 'Waveform']

    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        si.test.SignalIntegrityAppTestHelper.__init__(self, os.path.dirname(os.path.realpath(__file__)))
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd = os.getcwd()
        os.chdir(self.path)
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi = SignalIntegrityAppHeadless()
        self.UseSinX = SignalIntegrity.App.Preferences['Calculation.UseSinX']
        SignalIntegrity.App.Preferences['Calculation.UseSinX'] = False
        SignalIntegrity.App.Preferences.SaveToFile()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        os.chdir(self.cwd)
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi = SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation.UseSinX'] = self.UseSinX
        SignalIntegrity.App.Preferences.SaveToFile()

    @staticmethod
    def TestName(testNumber):
        return 'ProbeCircuit' + str(testNumber)

    def ProbeDict(self, testNumber):
        result = {}
        for probeNumber in range(len(self.ProbeNames)):
            probeName = self.ProbeNames[probeNumber]
            probeOn = (testNumber // pow(2, probeNumber) % 2 == 1)
            result[probeName] = probeOn
        return result

    def RunTest(self):
        testNumber = int(self.id().split('_')[-1])
        testname = self.TestName(testNumber)

        app = SignalIntegrityAppHeadless()
        app.OpenProjectFile('ProbeCircuit.si')

        testFileName = testname + '.si'
        probeState = self.ProbeDict(testNumber)

        print('Probe Test: '+str(testNumber)+' '+ str(probeState))

        def copyConditional(probe, ext, test):
            if os.path.exists('ProbeCircuit_' + probe + '.' + ext):
                shutil.copy('ProbeCircuit_' + probe + '.' + ext, testname + '_' + probeName + '.' + ext)

        def cleanupFiles(probe, ext, test):
            if os.path.exists(testname + '_' + probeName + '.' + ext):
                os.remove(testname + '_' + probeName + '.' + ext)

        for probeName in probeState.keys():
            app.Device(probeName)['state']['Value'] = 'on' if probeState[probeName] else 'off'
            if probeState[probeName]:
                copyConditional(probeName, 'json', testname)
                copyConditional(probeName, 'npy', testname)
                copyConditional(probeName, 'png', testname)
                copyConditional(probeName, 'txt', testname)

        app.SaveProjectToFile(testFileName)

        try:
            if not (probeState['EyeIn'] or probeState['I'] or probeState['Vd'] or probeState['EyeOut'] or probeState['Vin']):
                with self.assertRaises(AssertionError) as cme:
                    self.SimulationEyeDiagramResultsChecker(testname)
            else:
                self.SimulationEyeDiagramResultsChecker(testname)
        finally:
            for probeName in probeState.keys():
                cleanupFiles(probeName, 'json', testname)
                cleanupFiles(probeName, 'npy', testname)
                cleanupFiles(probeName, 'png', testname)
                cleanupFiles(probeName, 'txt', testname)

    def testAAAProbe(self):
        app = SignalIntegrityAppHeadless()
        app.OpenProjectFile('ProbeCircuit.si')
        app.Device('Waveform')['state']['Value'] = 'off'
        app.Device('Eye')['state']['Value'] = 'off'
        app.SaveProject()
        self.SimulationEyeDiagramResultsChecker('ProbeCircuit')
        app.Device('Waveform')['state']['Value'] = 'on'
        app.Device('Eye')['state']['Value'] = 'on'
        app.SaveProject()

    def testProbeOnOff_0(self):
        self.RunTest()

    def testProbeOnOff_1(self):
        self.RunTest()

    def testProbeOnOff_2(self):
        self.RunTest()

    def testProbeOnOff_3(self):
        self.RunTest()

    def testProbeOnOff_4(self):
        self.RunTest()

    def testProbeOnOff_5(self):
        self.RunTest()

    def testProbeOnOff_6(self):
        self.RunTest()

    def testProbeOnOff_7(self):
        self.RunTest()

    def testProbeOnOff_8(self):
        self.RunTest()

    def testProbeOnOff_9(self):
        self.RunTest()

    def testProbeOnOff_10(self):
        self.RunTest()

    def testProbeOnOff_11(self):
        self.RunTest()

    def testProbeOnOff_12(self):
        self.RunTest()

    def testProbeOnOff_13(self):
        self.RunTest()

    def testProbeOnOff_14(self):
        self.RunTest()

    def testProbeOnOff_15(self):
        self.RunTest()

    def testProbeOnOff_16(self):
        self.RunTest()

    def testProbeOnOff_17(self):
        self.RunTest()

    def testProbeOnOff_18(self):
        self.RunTest()

    def testProbeOnOff_19(self):
        self.RunTest()

    def testProbeOnOff_20(self):
        self.RunTest()

    def testProbeOnOff_21(self):
        self.RunTest()

    def testProbeOnOff_22(self):
        self.RunTest()

    def testProbeOnOff_23(self):
        self.RunTest()

    def testProbeOnOff_24(self):
        self.RunTest()

    def testProbeOnOff_25(self):
        self.RunTest()

    def testProbeOnOff_26(self):
        self.RunTest()

    def testProbeOnOff_27(self):
        self.RunTest()

    def testProbeOnOff_28(self):
        self.RunTest()

    def testProbeOnOff_29(self):
        self.RunTest()

    def testProbeOnOff_30(self):
        self.RunTest()

    def testProbeOnOff_31(self):
        self.RunTest()

    def testProbeOnOff_32(self):
        self.RunTest()

    def testProbeOnOff_33(self):
        self.RunTest()

    def testProbeOnOff_34(self):
        self.RunTest()

    def testProbeOnOff_35(self):
        self.RunTest()

    def testProbeOnOff_36(self):
        self.RunTest()

    def testProbeOnOff_37(self):
        self.RunTest()

    def testProbeOnOff_38(self):
        self.RunTest()

    def testProbeOnOff_39(self):
        self.RunTest()

    def testProbeOnOff_40(self):
        self.RunTest()

    def testProbeOnOff_41(self):
        self.RunTest()

    def testProbeOnOff_42(self):
        self.RunTest()

    def testProbeOnOff_43(self):
        self.RunTest()

    def testProbeOnOff_44(self):
        self.RunTest()

    def testProbeOnOff_45(self):
        self.RunTest()

    def testProbeOnOff_46(self):
        self.RunTest()

    def testProbeOnOff_47(self):
        self.RunTest()

    def testProbeOnOff_48(self):
        self.RunTest()

    def testProbeOnOff_49(self):
        self.RunTest()

    def testProbeOnOff_50(self):
        self.RunTest()

    def testProbeOnOff_51(self):
        self.RunTest()

    def testProbeOnOff_52(self):
        self.RunTest()

    def testProbeOnOff_53(self):
        self.RunTest()

    def testProbeOnOff_54(self):
        self.RunTest()

    def testProbeOnOff_55(self):
        self.RunTest()

    def testProbeOnOff_56(self):
        self.RunTest()

    def testProbeOnOff_57(self):
        self.RunTest()

    def testProbeOnOff_58(self):
        self.RunTest()

    def testProbeOnOff_59(self):
        self.RunTest()

    def testProbeOnOff_60(self):
        self.RunTest()

    def testProbeOnOff_61(self):
        self.RunTest()

    def testProbeOnOff_62(self):
        self.RunTest()

    def testProbeOnOff_63(self):
        self.RunTest()

    def testProbeOnOff_64(self):
        self.RunTest()

    def testProbeOnOff_65(self):
        self.RunTest()

    def testProbeOnOff_66(self):
        self.RunTest()

    def testProbeOnOff_67(self):
        self.RunTest()

    def testProbeOnOff_68(self):
        self.RunTest()

    def testProbeOnOff_69(self):
        self.RunTest()

    def testProbeOnOff_70(self):
        self.RunTest()

    def testProbeOnOff_71(self):
        self.RunTest()

    def testProbeOnOff_72(self):
        self.RunTest()

    def testProbeOnOff_73(self):
        self.RunTest()

    def testProbeOnOff_74(self):
        self.RunTest()

    def testProbeOnOff_75(self):
        self.RunTest()

    def testProbeOnOff_76(self):
        self.RunTest()

    def testProbeOnOff_77(self):
        self.RunTest()

    def testProbeOnOff_78(self):
        self.RunTest()

    def testProbeOnOff_79(self):
        self.RunTest()

    def testProbeOnOff_80(self):
        self.RunTest()

    def testProbeOnOff_81(self):
        self.RunTest()

    def testProbeOnOff_82(self):
        self.RunTest()

    def testProbeOnOff_83(self):
        self.RunTest()

    def testProbeOnOff_84(self):
        self.RunTest()

    def testProbeOnOff_85(self):
        self.RunTest()

    def testProbeOnOff_86(self):
        self.RunTest()

    def testProbeOnOff_87(self):
        self.RunTest()

    def testProbeOnOff_88(self):
        self.RunTest()

    def testProbeOnOff_89(self):
        self.RunTest()

    def testProbeOnOff_90(self):
        self.RunTest()

    def testProbeOnOff_91(self):
        self.RunTest()

    def testProbeOnOff_92(self):
        self.RunTest()

    def testProbeOnOff_93(self):
        self.RunTest()

    def testProbeOnOff_94(self):
        self.RunTest()

    def testProbeOnOff_95(self):
        self.RunTest()

    def testProbeOnOff_96(self):
        self.RunTest()

    def testProbeOnOff_97(self):
        self.RunTest()

    def testProbeOnOff_98(self):
        self.RunTest()

    def testProbeOnOff_99(self):
        self.RunTest()

    def testProbeOnOff_100(self):
        self.RunTest()

    def testProbeOnOff_101(self):
        self.RunTest()

    def testProbeOnOff_102(self):
        self.RunTest()

    def testProbeOnOff_103(self):
        self.RunTest()

    def testProbeOnOff_104(self):
        self.RunTest()

    def testProbeOnOff_105(self):
        self.RunTest()

    def testProbeOnOff_106(self):
        self.RunTest()

    def testProbeOnOff_107(self):
        self.RunTest()

    def testProbeOnOff_108(self):
        self.RunTest()

    def testProbeOnOff_109(self):
        self.RunTest()

    def testProbeOnOff_110(self):
        self.RunTest()

    def testProbeOnOff_111(self):
        self.RunTest()

    def testProbeOnOff_112(self):
        self.RunTest()

    def testProbeOnOff_113(self):
        self.RunTest()

    def testProbeOnOff_114(self):
        self.RunTest()

    def testProbeOnOff_115(self):
        self.RunTest()

    def testProbeOnOff_116(self):
        self.RunTest()

    def testProbeOnOff_117(self):
        self.RunTest()

    def testProbeOnOff_118(self):
        self.RunTest()

    def testProbeOnOff_119(self):
        self.RunTest()

    def testProbeOnOff_120(self):
        self.RunTest()

    def testProbeOnOff_121(self):
        self.RunTest()

    def testProbeOnOff_122(self):
        self.RunTest()

    def testProbeOnOff_123(self):
        self.RunTest()

    def testProbeOnOff_124(self):
        self.RunTest()

    def testProbeOnOff_125(self):
        self.RunTest()

    def testProbeOnOff_126(self):
        self.RunTest()

    def testProbeOnOff_127(self):
        self.RunTest()

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
