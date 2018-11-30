"""
TestSignalIntegrityApp.py
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
from SignalIntegrity.App import SignalIntegrityAppHeadless
from SignalIntegrity.App import TpX
from SignalIntegrity.App import TikZ
import SignalIntegrity.Lib as si
import os

class TestSignalIntegrityAppTest(unittest.TestCase,si.test.SParameterCompareHelper,
                                 si.test.SignalIntegrityAppTestHelper):
    relearn=True
    debug=False
    checkPictures=True
    keepNewFormats=False
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        os.chdir(self.path)
        self.book=os.path.exists('../../../../SignalIntegrityBook/')
    def testFourPortTLineTest(self):
        self.SimulationResultsChecker('FourPortTLineTest.si')
    def testFilterTest(self):
        self.SimulationResultsChecker('FilterTest.si')
    def testSignalIntegrityAppExamplesRLCTest2(self):
        self.SimulationResultsChecker('../../../SignalIntegrity/App/Examples/RLCTest2.si')
    def testSignalIntegrityAppDeembedCableFilter(self):
        self.DeembeddingResultsChecker('../../../SignalIntegrity/App/Examples/DeembedCableFilter.si')
    def testSignalIntegrityAppExampleSparameterExampleSParameterGenerationExample(self):
        self.SParameterResultsChecker('../../../SignalIntegrity/App/Examples/SParameterExample/SParameterGenerationExample.si')
    def testSignalIntegrityAppExampleVirtualProbingExampleVirtualProbeExample(self):
        self.VirtualProbeResultsChecker('../../../SignalIntegrity/App/Examples/VirtualProbingExample/VirtualProbeExample.si')
    def testOpenStub(self):
        self.SParameterResultsChecker('OpenStub.si')
    def testSignalIntegrityAppExampleCascCableFilter(self):
        self.SParameterResultsChecker('../../../SignalIntegrity/App/Examples/CascCableFilter.si')
    def testSignalIntegrityAppExamplesRLCTest(self):
        self.SimulationResultsChecker('../../../SignalIntegrity/App/Examples/RLCTest.si')
    def testSignalIntegrityAppExamplesRC(self):
        self.SimulationResultsChecker('../../../SignalIntegrity/App/Examples/RC.si')
    def testSignalIntegrityAppExampleTelegrapherFourPort(self):
        self.SParameterResultsChecker('../../../SignalIntegrity/App/Examples/telegrapherFourPort.si')
    def testSignalIntegrityAppExampleTelegrapherTestTwoPort(self):
        self.SParameterResultsChecker('../../../SignalIntegrity/App/Examples/telegrapherTestTwoPort.si')
    def testSignalIntegrityAppExamplesSimulationExampleBMYcheby(self):
        self.SimulationResultsChecker('../../../SignalIntegrity/App/Examples/SimulationExample/BMYcheby.si')
    def testSignalIntegrityAppExamplesSimulationExampleBMYchebySParameters(self):
        self.SParameterResultsChecker('../../../SignalIntegrity/App/Examples/SimulationExample/BMYchebySParameters.si')
    def testSignalIntegrityAppExamplesSimulationExampleInvCheby_8(self):
        self.SimulationResultsChecker('../../../SignalIntegrity/App/Examples/SimulationExample/InvCheby_8.si')
    def testSignalIntegrityAppExamplesPulseGeneratorTest(self):
        self.SimulationResultsChecker('../../../SignalIntegrity/App/Examples/PulseGeneratorTest.si')
    def testSignalIntegrityAppExamplesStepGeneratorTest(self):
        self.SimulationResultsChecker('../../../SignalIntegrity/App/Examples/StepGeneratorTest.si')
    def testSignalIntegrityAppSignalIntegrityBookMeasurementTDRSimulationTest(self):
        if not self.book: return
        self.SimulationResultsChecker('../../../../SignalIntegrityBook/Measurement/TDRSimulation.si')
    def testSignalIntegrityAppSignalIntegrityBookMeasurementTDRSimulationTest2(self):
        if not self.book: return
        self.SimulationResultsChecker('../../../../SignalIntegrityBook/Measurement/TDRSimulation2.si')
    def testSignalIntegrityAppSignalIntegrityBookMeasurementTDRSimulationTest3(self):
        if not self.book: return
        self.SimulationResultsChecker('../../../../SignalIntegrityBook/Measurement/TDRSimulation3.si')
    def testPicturesNetlists(self):
        filesList=[
            'FilterTest.si',
            'FourPortTLineTest.si',
            'FileDevices.si',
            'ReactiveDevices.si',
            'TransmissionLineDevices.si',
            'GeneratorsDevices.si',
            'UnknownDevices.si',
            'SystemDevices.si',
            'Noise.si',
            'OpenStub.si',
            'Amplifiers.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/TestVRMIstvan2.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VP/Measure.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VP/Calculate.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VP/Compare.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/TestVRMIstvan.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/TestVRMEquiv.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VRMWaveformCompare.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/TestCNaturalResponse.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/TestVRMModel.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VPSteady/FeedbackNetwork.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VPSteady/Measure5.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VPSteady/Measure.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VPSteady/Measure2.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VPSteady/Measure4.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VPSteady/Measure3.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VPSteady/Measure6.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/LoadResistanceBWL.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/TestVRMEquivAC.si',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/TestVRM.si',
            '../../../Test/TestSignalIntegrity/TestCurrentSense.si',
            '../../../Test/TestSignalIntegrity/TestVRMParasitics.si',
            '../../../Test/TestSignalIntegrity/TestVRM.si',
            'FourPortTests/DifferentialTransmissionLineComparesMixedMode.si',
            'FourPortTests/Mutual.si',
            'FourPortTests/telegrapherFourPortTwoElements.si',
            'FourPortTests/telegrapherFourPortCircuitOneSection.si',
            'FourPortTests/DifferentialTransmissionLineCompares.si',
            'FourPortTests/telegrapherFourPortElement.si',
            'FourPortTests/TL_test_Circuit1_Pete.si',
            'FourPortTests/telegrapherFourPort10000Elements.si',
            'FourPortTests/DimaWay.si',
            'FourPortTests/telegrapherFourPortCircuitTwoSections.si',
            '../../../SignalIntegrity/App/Examples/RLCTest.si',
            '../../../SignalIntegrity/App/Examples/telegrapherFourPort.si',
            '../../../SignalIntegrity/App/Examples/SParameterExample.si',
            '../../../SignalIntegrity/App/Examples/RC.si',
            '../../../SignalIntegrity/App/Examples/telegrapherTestFourPort.si',
            '../../../SignalIntegrity/App/Examples/SParameterExample/SParameterGenerationExample.si',
            '../../../SignalIntegrity/App/Examples/DeembedCableFilter.si',
            '../../../SignalIntegrity/App/Examples/PulseGeneratorTest.si',
            '../../../SignalIntegrity/App/Examples/SimulationExample/SimulatorExample.si',
            '../../../SignalIntegrity/App/Examples/SimulationExample/InvCheby_8.si',
            '../../../SignalIntegrity/App/Examples/SimulationExample/BMYcheby.si',
            '../../../SignalIntegrity/App/Examples/SimulationExample/BMYchebySParameters.si',
            '../../../SignalIntegrity/App/Examples/telegrapherTestTwoPort.si',
            '../../../SignalIntegrity/App/Examples/VirtualProbingExample/VirtualProbeExampleSimulation2.si',
            '../../../SignalIntegrity/App/Examples/VirtualProbingExample/VirtualProbeExampleSimulation.si',
            '../../../SignalIntegrity/App/Examples/VirtualProbingExample/VirtualProbeExampleCompare.si',
            '../../../SignalIntegrity/App/Examples/VirtualProbingExample/VirtualProbeExample.si',
            '../../../SignalIntegrity/App/Examples/RLC.si',
            '../../../SignalIntegrity/App/Examples/CascCableFilter.si',
            '../../../SignalIntegrity/App/Examples/StepGeneratorTest.si',
            '../../../SignalIntegrity/App/Examples/RLCTest2.si',
            'VirtualProbeTests/comparison.si',
            'VirtualProbeTests/Example2.si',
            'VirtualProbeTests/SimpleCaseExample1.si',
            'VirtualProbeTests/Example3DegreeOfFreedom.si',
            'VirtualProbeTests/SimpleCase.si',
            '../../../../SignalIntegrityBook/TransmissionLines/TerminationDifferentialCenterTapUnbalanced.si',
            '../../../../SignalIntegrityBook/TransmissionLines/FourPortMixedModeModelCompareTlines.si',
            '../../../../SignalIntegrityBook/TransmissionLines/TerminationMixedMode.si',
            '../../../../SignalIntegrityBook/TransmissionLines/MixedModeSimulation.si',
            '../../../../SignalIntegrityBook/TransmissionLines/MixedModeConverterSymbol.si',
            '../../../../SignalIntegrityBook/TransmissionLines/FourPortMixedModeModelCompareTelegrapher.si',
            '../../../../SignalIntegrityBook/TransmissionLines/TerminationDifferentialCenterTapACCoupled.si',
            '../../../../SignalIntegrityBook/TransmissionLines/TerminationDifferentialTee.si',
            '../../../../SignalIntegrityBook/TransmissionLines/TerminationDifferentialCenterTap.si',
            '../../../../SignalIntegrityBook/TransmissionLines/SimulationTerminationDifferentialTee.si',
            '../../../../SignalIntegrityBook/TransmissionLines/BalancedFourPortTelegrapherMixedMode.si',
            '../../../../SignalIntegrityBook/TransmissionLines/TerminationDifferentialOnly.si',
            '../../../../SignalIntegrityBook/TransmissionLines/DifferentialTelegrapher.si',
            '../../../../SignalIntegrityBook/TransmissionLines/DifferentialTelegrapherBalancede.si',
            '../../../../SignalIntegrityBook/TransmissionLines/TerminationDifferentialPi.si',
            '../../../../SignalIntegrityBook/TransmissionLines/BalancedFourPortModelMixedMode.si',
            '../../../../SignalIntegrityBook/TransmissionLines/MixedModeConverterVoltageSymbol.si',
            '../../../../SignalIntegrityBook/TransmissionLines/MixedModeSimulationPi.si',
            '../../../../SignalIntegrityBook/TransmissionLines/MixedModeSimulationTee.si',
            '../../../../SignalIntegrityBook/SParameters/Mutual.si',
            '../../../../SignalIntegrityBook/Simulation/SimulationCircuitSchematic2.si',
            '../../../../SignalIntegrityBook/Simulation/SimulationCircuitBlockDiagram.si',
            '../../../../SignalIntegrityBook/Simulation/SimulationCircuitSchematic.si',
            '../../../../SignalIntegrityBook/WaveformProcessing/TransferMatricesProcessing.si',
            '../../../../SignalIntegrityBook/SymbolicDeviceSolutions/FourPortVoltageAmplifierVoltageSeriesFeedbackCircuit.si',
            '../../../../SignalIntegrityBook/SymbolicDeviceSolutions/TransistorThreePortCircuit.si',
            '../../../../SignalIntegrityBook/VirtualProbing/VirtualProbingSimpleExample.si',
            '../../../../SignalIntegrityBook/VirtualProbing/VirtualProbingTwoVoltageExample.si',
            '../../../../SignalIntegrityBook/VirtualProbing/VirtualProbingDifferentialExample.si',
            '../../../../SignalIntegrityBook/VirtualProbing/VirtualProbingProbeDeembeddingExample.si',
            '../../../../SignalIntegrityBook/NetworkParameters/ShuntImpedanceInstrumentedZ.si',
            '../../../../SignalIntegrityBook/NetworkParameters/FileDevice.si',
            '../../../../SignalIntegrityBook/NetworkParameters/YParametersSchematic.si',
            '../../../../SignalIntegrityBook/NetworkParameters/SimpleCircuitAnalysisExampleNetwork.si',
            '../../../../SignalIntegrityBook/NetworkParameters/ArbitraryCircuitInstrumentedZ.si',
            '../../../../SignalIntegrityBook/NetworkParameters/ClassicNetworkParameterDevice.si',
            '../../../../SignalIntegrityBook/NetworkParameters/CascABCD.si',
            '../../../../SignalIntegrityBook/NetworkParameters/SeriesImpedanceInstrumentedZ.si',
            '../../../../SignalIntegrityBook/NetworkParameters/SeriesImpedanceInstrumentedY.si',
            '../../../../SignalIntegrityBook/NetworkParameters/ZParametersSchematic.si',
            '../../../../SignalIntegrityBook/NetworkParameters/SimpleCircuitAnalysisExampleCircuit.si',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/OperationalAmplifierSymbol.si',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/VoltageAmplifierTwoPortSymbol.si',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/CurrentAmplifierFourPortCircuit.si',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/VoltageAmplifierTwoPortCircuit.si',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/OperationalAmplifierCircuit.si',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/VoltageAmplifierFourPortSymbol.si',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/VoltageAmplifierThreePortCircuit.si',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/VoltageAmplifierFourPortCircuit.si',
            '../../../../SignalIntegrityBook/Sources/IdealTransformer/testIdealTransformer.si',
            '../../../../SignalIntegrityBook/Sources/IdealTransformer/IdealTransformerSP.si',
            '../../../../SignalIntegrityBook/Sources/IdealTransformer/IdealTransformerCircuit.si',
            '../../../../SignalIntegrityBook/Sources/IdealTransformer/IdealTransformerSymbol.si',
            '../../../../SignalIntegrityBook/Sources/DependentSources/DependentSources.si',
            'SenseResistor/SenseResistorVirtualProbe.si',
            'SenseResistor/SenseResistorMeasurement.si',
            'SenseResistor/SenseResistorSimple.si',
            '../../../../SignalIntegrityBook/Measurement/TDRSimulation.si',
            '../../../../SignalIntegrityBook/Measurement/TDRSimulation2.si',
        ]
        for filename in filesList:
            self.setUp()
            if not 'SignalIntegrityBook' in filename or self.book:
                #print filename
                pysi=self.Preliminary(filename)
#                 pysi.SaveProject()
#                 filename=filename.replace('.si','.si')
#                 pysi=self.Preliminary(filename)
#                 if not self.keepNewFormats:
#                     os.remove(pysi.fileparts.FullFilePathExtension('si'))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
