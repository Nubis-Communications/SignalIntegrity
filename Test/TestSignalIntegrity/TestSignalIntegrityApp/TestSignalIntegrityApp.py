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

class SParameterCompareHelper(object):
    def SParametersAreEqual(self,lhs,rhs,epsilon=0.00001):
        if lhs.m_P != rhs.m_P: return False
        if lhs.m_Z0 != rhs.m_Z0: return False
        if len(lhs) != len(rhs): return False
        for n in range(len(lhs)):
            if abs(lhs.m_f[n] - rhs.m_f[n]) > epsilon: return False
            lhsn=lhs[n]
            rhsn=rhs[n]
            for r in range(lhs.m_P):
                for c in range(lhs.m_P):
                    if abs(lhsn[r][c] - rhsn[r][c]) > epsilon:
                        return False
        return True

class TestSignalIntegrityAppTest(unittest.TestCase,SParameterCompareHelper,
                                 si.test.SignalIntegrityAppTestHelper):
    relearn=True
    debug=False
    checkPictures=True
    def __init__(self, methodName='runTest'):
        SParameterCompareHelper.__init__(self)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        os.chdir(self.path)
    def testFourPortTLineTest(self):
        self.SimulationResultsChecker('FourPortTLineTest.xml')
    def testFilterTest(self):
        self.SimulationResultsChecker('FilterTest.xml')
    def testSignalIntegrityAppExamplesRLCTest2(self):
        self.SimulationResultsChecker('../../../SignalIntegrity/App/Examples/RLCTest2.xml')
    def testSignalIntegrityAppDeembedCableFilter(self):
        self.DeembeddingResultsChecker('../../../SignalIntegrity/App/Examples/DeembedCableFilter.xml')
    def testSignalIntegrityAppExampleSparameterExampleSParameterGenerationExample(self):
        self.SParameterResultsChecker('../../../SignalIntegrity/App/Examples/SParameterExample/SParameterGenerationExample.xml')
    def testSignalIntegrityAppExampleVirtualProbingExampleVirtualProbeExample(self):
        self.VirtualProbeResultsChecker('../../../SignalIntegrity/App/Examples/VirtualProbingExample/VirtualProbeExample.xml')
    def testOpenStub(self):
        self.SParameterResultsChecker('OpenStub.xml')
    def testSignalIntegrityAppExampleCascCableFilter(self):
        self.SParameterResultsChecker('../../../SignalIntegrity/App/Examples/CascCableFilter.xml')
    def testSignalIntegrityAppExamplesRLCTest(self):
        self.SimulationResultsChecker('../../../SignalIntegrity/App/Examples/RLCTest.xml')
    def testSignalIntegrityAppExamplesRC(self):
        self.SimulationResultsChecker('../../../SignalIntegrity/App/Examples/RC.xml')
    def testSignalIntegrityAppExampleTelegrapherFourPort(self):
        self.SParameterResultsChecker('../../../SignalIntegrity/App/Examples/telegrapherFourPort.xml')
    def testSignalIntegrityAppExampleTelegrapherTestTwoPort(self):
        self.SParameterResultsChecker('../../../SignalIntegrity/App/Examples/telegrapherTestTwoPort.xml')
    def testSignalIntegrityAppExamplesSimulationExampleBMYcheby(self):
        self.SimulationResultsChecker('../../../SignalIntegrity/App/Examples/SimulationExample/BMYcheby.xml')
    def testSignalIntegrityAppExamplesSimulationExampleBMYchebySParameters(self):
        self.SParameterResultsChecker('../../../SignalIntegrity/App/Examples/SimulationExample/BMYchebySParameters.xml')
    def testSignalIntegrityAppExamplesSimulationExampleInvCheby_8(self):
        self.SimulationResultsChecker('../../../SignalIntegrity/App/Examples/SimulationExample/InvCheby_8.xml')
    def testSignalIntegrityAppExamplesPulseGeneratorTest(self):
        self.SimulationResultsChecker('../../../SignalIntegrity/App/Examples/PulseGeneratorTest.xml')
    def testSignalIntegrityAppExamplesStepGeneratorTest(self):
        self.SimulationResultsChecker('../../../SignalIntegrity/App/Examples/StepGeneratorTest.xml')
    def testSignalIntegrityAppSignalIntegrityBookMeasurementTDRSimulationTest(self):
        self.SimulationResultsChecker('../../../../SignalIntegrityBook/Measurement/TDRSimulation.xml')
    def testSignalIntegrityAppSignalIntegrityBookMeasurementTDRSimulationTest2(self):
        self.SimulationResultsChecker('../../../../SignalIntegrityBook/Measurement/TDRSimulation2.xml')
    def testSignalIntegrityAppSignalIntegrityBookMeasurementTDRSimulationTest3(self):
        self.SimulationResultsChecker('../../../../SignalIntegrityBook/Measurement/TDRSimulation3.xml')
    def testPicturesNetlists(self):
        filesList=[
            'FilterTest.xml',
            'FourPortTLineTest.xml',
            'FileDevices.xml',
            'ReactiveDevices.xml',
            'TransmissionLineDevices.xml',
            'GeneratorsDevices.xml',
            'UnknownDevices.xml',
            'SystemDevices.xml',
            'Noise.xml',
            'OpenStub.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/TestVRMIstvan2.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VP/Measure.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VP/Calculate.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VP/Compare.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/TestVRMIstvan.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/TestVRMEquiv.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VRMWaveformCompare.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/TestCNaturalResponse.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/TestVRMModel.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VPSteady/FeedbackNetwork.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VPSteady/Measure5.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VPSteady/Measure.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VPSteady/Measure2.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VPSteady/Measure4.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VPSteady/Measure3.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/VPSteady/Measure6.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/LoadResistanceBWL.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/TestVRMEquivAC.xml',
            '../../../SignalIntegrity/App/Examples/PowerIntegrity/TestVRM.xml',
            '../../../Test/TestSignalIntegrity/TestCurrentSense.xml',
            '../../../Test/TestSignalIntegrity/TestVRMParasitics.xml',
            '../../../Test/TestSignalIntegrity/TestVRM.xml',
            'FourPortTests/DifferentialTransmissionLineComparesMixedMode.xml',
            'FourPortTests/Mutual.xml',
            'FourPortTests/telegrapherFourPortTwoElements.xml',
            'FourPortTests/telegrapherFourPortCircuitOneSection.xml',
            'FourPortTests/DifferentialTransmissionLineCompares.xml',
            'FourPortTests/telegrapherFourPortElement.xml',
            'FourPortTests/TL_test_Circuit1_Pete.xml',
            'FourPortTests/telegrapherFourPort10000Elements.xml',
            'FourPortTests/DimaWay.xml',
            'FourPortTests/telegrapherFourPortCircuitTwoSections.xml',
            '../../../SignalIntegrity/App/Examples/RLCTest.xml',
            '../../../SignalIntegrity/App/Examples/telegrapherFourPort.xml',
            '../../../SignalIntegrity/App/Examples/SParameterExample.xml',
            '../../../SignalIntegrity/App/Examples/RC.xml',
            '../../../SignalIntegrity/App/Examples/telegrapherTestFourPort.xml',
            '../../../SignalIntegrity/App/Examples/SParameterExample/SParameterGenerationExample.xml',
            '../../../SignalIntegrity/App/Examples/DeembedCableFilter.xml',
            '../../../SignalIntegrity/App/Examples/PulseGeneratorTest.xml',
            '../../../SignalIntegrity/App/Examples/SimulationExample/SimulatorExample.xml',
            '../../../SignalIntegrity/App/Examples/SimulationExample/InvCheby_8.xml',
            '../../../SignalIntegrity/App/Examples/SimulationExample/BMYcheby.xml',
            '../../../SignalIntegrity/App/Examples/SimulationExample/BMYchebySParameters.xml',
            '../../../SignalIntegrity/App/Examples/telegrapherTestTwoPort.xml',
            '../../../SignalIntegrity/App/Examples/VirtualProbingExample/VirtualProbeExampleSimulation2.xml',
            '../../../SignalIntegrity/App/Examples/VirtualProbingExample/VirtualProbeExampleSimulation.xml',
            '../../../SignalIntegrity/App/Examples/VirtualProbingExample/VirtualProbeExampleCompare.xml',
            '../../../SignalIntegrity/App/Examples/VirtualProbingExample/VirtualProbeExample.xml',
            '../../../SignalIntegrity/App/Examples/RLC.xml',
            '../../../SignalIntegrity/App/Examples/CascCableFilter.xml',
            '../../../SignalIntegrity/App/Examples/StepGeneratorTest.xml',
            '../../../SignalIntegrity/App/Examples/RLCTest2.xml',
            'VirtualProbeTests/comparison.xml',
            'VirtualProbeTests/Example2.xml',
            'VirtualProbeTests/SimpleCaseExample1.xml',
            'VirtualProbeTests/Example3DegreeOfFreedom.xml',
            'VirtualProbeTests/SimpleCase.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/TerminationDifferentialCenterTapUnbalanced.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/FourPortMixedModeModelCompareTlines.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/TerminationMixedMode.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/MixedModeSimulation.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/MixedModeConverterSymbol.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/FourPortMixedModeModelCompareTelegrapher.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/TerminationDifferentialCenterTapACCoupled.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/TerminationDifferentialTee.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/TerminationDifferentialCenterTap.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/SimulationTerminationDifferentialTee.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/BalancedFourPortTelegrapherMixedMode.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/TerminationDifferentialOnly.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/DifferentialTelegrapher.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/DifferentialTelegrapherBalancede.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/TerminationDifferentialPi.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/BalancedFourPortModelMixedMode.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/MixedModeConverterVoltageSymbol.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/MixedModeSimulationPi.xml',
            '../../../../SignalIntegrityBook/TransmissionLines/MixedModeSimulationTee.xml',
            '../../../../SignalIntegrityBook/SParameters/Mutual.xml',
            '../../../../SignalIntegrityBook/Simulation/SimulationCircuitSchematic2.xml',
            '../../../../SignalIntegrityBook/Simulation/SimulationCircuitBlockDiagram.xml',
            '../../../../SignalIntegrityBook/Simulation/SimulationCircuitSchematic.xml',
            '../../../../SignalIntegrityBook/WaveformProcessing/TransferMatricesProcessing.xml',
            '../../../../SignalIntegrityBook/SymbolicDeviceSolutions/FourPortVoltageAmplifierVoltageSeriesFeedbackCircuit.xml',
            '../../../../SignalIntegrityBook/SymbolicDeviceSolutions/TransistorThreePortCircuit.xml',
            '../../../../SignalIntegrityBook/VirtualProbing/VirtualProbingSimpleExample.xml',
            '../../../../SignalIntegrityBook/VirtualProbing/VirtualProbingTwoVoltageExample.xml',
            '../../../../SignalIntegrityBook/VirtualProbing/VirtualProbingDifferentialExample.xml',
            '../../../../SignalIntegrityBook/VirtualProbing/VirtualProbingProbeDeembeddingExample.xml',
            '../../../../SignalIntegrityBook/NetworkParameters/ShuntImpedanceInstrumentedZ.xml',
            '../../../../SignalIntegrityBook/NetworkParameters/FileDevice.xml',
            '../../../../SignalIntegrityBook/NetworkParameters/YParametersSchematic.xml',
            '../../../../SignalIntegrityBook/NetworkParameters/SimpleCircuitAnalysisExampleNetwork.xml',
            '../../../../SignalIntegrityBook/NetworkParameters/ArbitraryCircuitInstrumentedZ.xml',
            '../../../../SignalIntegrityBook/NetworkParameters/ClassicNetworkParameterDevice.xml',
            '../../../../SignalIntegrityBook/NetworkParameters/CascABCD.xml',
            '../../../../SignalIntegrityBook/NetworkParameters/SeriesImpedanceInstrumentedZ.xml',
            '../../../../SignalIntegrityBook/NetworkParameters/SeriesImpedanceInstrumentedY.xml',
            '../../../../SignalIntegrityBook/NetworkParameters/ZParametersSchematic.xml',
            '../../../../SignalIntegrityBook/NetworkParameters/SimpleCircuitAnalysisExampleCircuit.xml',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/OperationalAmplifierSymbol.xml',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/VoltageAmplifierTwoPortSymbol.xml',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/CurrentAmplifierFourPortCircuit.xml',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/VoltageAmplifierTwoPortCircuit.xml',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/OperationalAmplifierCircuit.xml',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/VoltageAmplifierFourPortSymbol.xml',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/VoltageAmplifierThreePortCircuit.xml',
            '../../../../SignalIntegrityBook/Sources/Amplifiers/VoltageAmplifierFourPortCircuit.xml',
            '../../../../SignalIntegrityBook/Sources/IdealTransformer/testIdealTransformer.xml',
            '../../../../SignalIntegrityBook/Sources/IdealTransformer/IdealTransformerSP.xml',
            '../../../../SignalIntegrityBook/Sources/IdealTransformer/IdealTransformerCircuit.xml',
            '../../../../SignalIntegrityBook/Sources/IdealTransformer/IdealTransformerSymbol.xml',
            '../../../../SignalIntegrityBook/Sources/DependentSources/DependentSources.xml',
            'SenseResistor/SenseResistorVirtualProbe.xml',
            'SenseResistor/SenseResistorMeasurement.xml',
            'SenseResistor/SenseResistorSimple.xml',
            '../../../../SignalIntegrityBook/Measurement/TDRSimulation.xml',
            '../../../../SignalIntegrityBook/Measurement/TDRSimulation2.xml',
        ]
        for filename in filesList:
            self.setUp()
            #print filename
            self.Preliminary(filename)

if __name__ == "__main__":
    unittest.main()
