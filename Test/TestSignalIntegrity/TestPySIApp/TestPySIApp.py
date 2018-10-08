"""
TestPySIApp.py
"""

# Copyright (c) 2018 Teledyne LeCroy, all rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import unittest
from PySIApp import PySIAppHeadless
from PySIApp.TpX import TpX
from PySIApp.TikZ import TikZ
import SignalIntegrity as si
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

class TestPySIAppTest(unittest.TestCase,SParameterCompareHelper,si.test.PySIAppTestHelper):
    relearn=True
    debug=False
    checkPictures=True
    def __init__(self, methodName='runTest'):
        SParameterCompareHelper.__init__(self)
        si.test.PySIAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        os.chdir(self.path)
    def testFourPortTLineTest(self):
        self.SimulationResultsChecker('FourPortTLineTest.xml')
    def testFilterTest(self):
        self.SimulationResultsChecker('FilterTest.xml')
    def testPySIAppExamplesRLCTest2(self):
        self.SimulationResultsChecker('../../../PySIApp/Examples/RLCTest2.xml')
    def testPySIAppDeembedCableFilter(self):
        self.DeembeddingResultsChecker('../../../PySIApp/Examples/DeembedCableFilter.xml')
    def testPySIAppExampleSparameterExampleSParameterGenerationExample(self):
        self.SParameterResultsChecker('../../../PySIApp/Examples/SParameterExample/SParameterGenerationExample.xml')
    def testPySIAppExampleVirtualProbingExampleVirtualProbeExample(self):
        self.VirtualProbeResultsChecker('../../../PySIApp/Examples/VirtualProbingExample/VirtualProbeExample.xml')
    def testOpenStub(self):
        self.SParameterResultsChecker('OpenStub.xml')
    def testPySIAppExampleCascCableFilter(self):
        self.SParameterResultsChecker('../../../PySIApp/Examples/CascCableFilter.xml')
    def testPySIAppExamplesRLCTest(self):
        self.SimulationResultsChecker('../../../PySIApp/Examples/RLCTest.xml')
    def testPySIAppExamplesRC(self):
        self.SimulationResultsChecker('../../../PySIApp/Examples/RC.xml')
    def testPySIAppExampleTelegrapherFourPort(self):
        self.SParameterResultsChecker('../../../PySIApp/Examples/telegrapherFourPort.xml')
    def testPySIAppExampleTelegrapherTestTwoPort(self):
        self.SParameterResultsChecker('../../../PySIApp/Examples/telegrapherTestTwoPort.xml')
    def testPySIAppExamplesSimulationExampleBMYcheby(self):
        self.SimulationResultsChecker('../../../PySIApp/Examples/SimulationExample/BMYcheby.xml')
    def testPySIAppExamplesSimulationExampleBMYchebySParameters(self):
        self.SParameterResultsChecker('../../../PySIApp/Examples/SimulationExample/BMYchebySParameters.xml')
    def testPySIAppExamplesSimulationExampleInvCheby_8(self):
        self.SimulationResultsChecker('../../../PySIApp/Examples/SimulationExample/InvCheby_8.xml')
    def testPySIAppExamplesPulseGeneratorTest(self):
        self.SimulationResultsChecker('../../../PySIApp/Examples/PulseGeneratorTest.xml')
    def testPySIAppExamplesStepGeneratorTest(self):
        self.SimulationResultsChecker('../../../PySIApp/Examples/StepGeneratorTest.xml')
    def testPySIAppPySIBookMeasurementTDRSimulationTest(self):
        self.SimulationResultsChecker('../../../../PySIBook/Measurement/TDRSimulation.xml')
    def testPySIAppPySIBookMeasurementTDRSimulationTest2(self):
        self.SimulationResultsChecker('../../../../PySIBook/Measurement/TDRSimulation2.xml')
    def testPySIAppPySIBookMeasurementTDRSimulationTest3(self):
        self.SimulationResultsChecker('../../../../PySIBook/Measurement/TDRSimulation3.xml')
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
            '../../../PySIApp/PowerIntegrity/TestVRMIstvan2.xml',
            '../../../PySIApp/PowerIntegrity/VP/Measure.xml',
            '../../../PySIApp/PowerIntegrity/VP/Calculate.xml',
            '../../../PySIApp/PowerIntegrity/VP/Compare.xml',
            '../../../PySIApp/PowerIntegrity/TestVRMIstvan.xml',
            '../../../PySIApp/PowerIntegrity/TestVRMEquiv.xml',
            '../../../PySIApp/PowerIntegrity/VRMWaveformCompare.xml',
            '../../../PySIApp/PowerIntegrity/TestCNaturalResponse.xml',
            '../../../PySIApp/PowerIntegrity/TestVRMModel.xml',
            '../../../PySIApp/PowerIntegrity/VPSteady/FeedbackNetwork.xml',
            '../../../PySIApp/PowerIntegrity/VPSteady/Measure5.xml',
            '../../../PySIApp/PowerIntegrity/VPSteady/Measure.xml',
            '../../../PySIApp/PowerIntegrity/VPSteady/Measure2.xml',
            '../../../PySIApp/PowerIntegrity/VPSteady/Measure4.xml',
            '../../../PySIApp/PowerIntegrity/VPSteady/Measure3.xml',
            '../../../PySIApp/PowerIntegrity/VPSteady/Measure6.xml',
            '../../../PySIApp/PowerIntegrity/LoadResistanceBWL.xml',
            '../../../PySIApp/PowerIntegrity/TestVRMEquivAC.xml',
            '../../../PySIApp/PowerIntegrity/TestVRM.xml',
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
            '../../../PySIApp/Examples/RLCTest.xml',
            '../../../PySIApp/Examples/telegrapherFourPort.xml',
            '../../../PySIApp/Examples/SParameterExample.xml',
            '../../../PySIApp/Examples/RC.xml',
            '../../../PySIApp/Examples/telegrapherTestFourPort.xml',
            '../../../PySIApp/Examples/SParameterExample/SParameterGenerationExample.xml',
            '../../../PySIApp/Examples/DeembedCableFilter.xml',
            '../../../PySIApp/Examples/PulseGeneratorTest.xml',
            '../../../PySIApp/Examples/SimulationExample/SimulatorExample.xml',
            '../../../PySIApp/Examples/SimulationExample/InvCheby_8.xml',
            '../../../PySIApp/Examples/SimulationExample/BMYcheby.xml',
            '../../../PySIApp/Examples/SimulationExample/BMYchebySParameters.xml',
            '../../../PySIApp/Examples/telegrapherTestTwoPort.xml',
            '../../../PySIApp/Examples/VirtualProbingExample/VirtualProbeExampleSimulation2.xml',
            '../../../PySIApp/Examples/VirtualProbingExample/VirtualProbeExampleSimulation.xml',
            '../../../PySIApp/Examples/VirtualProbingExample/VirtualProbeExampleCompare.xml',
            '../../../PySIApp/Examples/VirtualProbingExample/VirtualProbeExample.xml',
            '../../../PySIApp/Examples/RLC.xml',
            '../../../PySIApp/Examples/CascCableFilter.xml',
            '../../../PySIApp/Examples/StepGeneratorTest.xml',
            '../../../PySIApp/Examples/RLCTest2.xml',
            'VirtualProbeTests/comparison.xml',
            'VirtualProbeTests/Example2.xml',
            'VirtualProbeTests/SimpleCaseExample1.xml',
            'VirtualProbeTests/Example3DegreeOfFreedom.xml',
            'VirtualProbeTests/SimpleCase.xml',
            '../../../../PySIBook/TransmissionLines/TerminationDifferentialCenterTapUnbalanced.xml',
            '../../../../PySIBook/TransmissionLines/FourPortMixedModeModelCompareTlines.xml',
            '../../../../PySIBook/TransmissionLines/TerminationMixedMode.xml',
            '../../../../PySIBook/TransmissionLines/MixedModeSimulation.xml',
            '../../../../PySIBook/TransmissionLines/MixedModeConverterSymbol.xml',
            '../../../../PySIBook/TransmissionLines/FourPortMixedModeModelCompareTelegrapher.xml',
            '../../../../PySIBook/TransmissionLines/TerminationDifferentialCenterTapACCoupled.xml',
            '../../../../PySIBook/TransmissionLines/TerminationDifferentialTee.xml',
            '../../../../PySIBook/TransmissionLines/TerminationDifferentialCenterTap.xml',
            '../../../../PySIBook/TransmissionLines/SimulationTerminationDifferentialTee.xml',
            '../../../../PySIBook/TransmissionLines/BalancedFourPortTelegrapherMixedMode.xml',
            '../../../../PySIBook/TransmissionLines/TerminationDifferentialOnly.xml',
            '../../../../PySIBook/TransmissionLines/DifferentialTelegrapher.xml',
            '../../../../PySIBook/TransmissionLines/DifferentialTelegrapherBalancede.xml',
            '../../../../PySIBook/TransmissionLines/TerminationDifferentialPi.xml',
            '../../../../PySIBook/TransmissionLines/BalancedFourPortModelMixedMode.xml',
            '../../../../PySIBook/TransmissionLines/MixedModeConverterVoltageSymbol.xml',
            '../../../../PySIBook/TransmissionLines/MixedModeSimulationPi.xml',
            '../../../../PySIBook/TransmissionLines/MixedModeSimulationTee.xml',
            '../../../../PySIBook/SParameters/Mutual.xml',
            '../../../../PySIBook/Simulation/SimulationCircuitSchematic2.xml',
            '../../../../PySIBook/Simulation/SimulationCircuitBlockDiagram.xml',
            '../../../../PySIBook/Simulation/SimulationCircuitSchematic.xml',
            '../../../../PySIBook/WaveformProcessing/TransferMatricesProcessing.xml',
            '../../../../PySIBook/SymbolicDeviceSolutions/FourPortVoltageAmplifierVoltageSeriesFeedbackCircuit.xml',
            '../../../../PySIBook/SymbolicDeviceSolutions/TransistorThreePortCircuit.xml',
            '../../../../PySIBook/VirtualProbing/VirtualProbingSimpleExample.xml',
            '../../../../PySIBook/VirtualProbing/VirtualProbingTwoVoltageExample.xml',
            '../../../../PySIBook/VirtualProbing/VirtualProbingDifferentialExample.xml',
            '../../../../PySIBook/VirtualProbing/VirtualProbingProbeDeembeddingExample.xml',
            '../../../../PySIBook/NetworkParameters/ShuntImpedanceInstrumentedZ.xml',
            '../../../../PySIBook/NetworkParameters/FileDevice.xml',
            '../../../../PySIBook/NetworkParameters/YParametersSchematic.xml',
            '../../../../PySIBook/NetworkParameters/SimpleCircuitAnalysisExampleNetwork.xml',
            '../../../../PySIBook/NetworkParameters/ArbitraryCircuitInstrumentedZ.xml',
            '../../../../PySIBook/NetworkParameters/ClassicNetworkParameterDevice.xml',
            '../../../../PySIBook/NetworkParameters/CascABCD.xml',
            '../../../../PySIBook/NetworkParameters/SeriesImpedanceInstrumentedZ.xml',
            '../../../../PySIBook/NetworkParameters/SeriesImpedanceInstrumentedY.xml',
            '../../../../PySIBook/NetworkParameters/ZParametersSchematic.xml',
            '../../../../PySIBook/NetworkParameters/SimpleCircuitAnalysisExampleCircuit.xml',
            '../../../../PySIBook/Sources/Amplifiers/OperationalAmplifierSymbol.xml',
            '../../../../PySIBook/Sources/Amplifiers/VoltageAmplifierTwoPortSymbol.xml',
            '../../../../PySIBook/Sources/Amplifiers/CurrentAmplifierFourPortCircuit.xml',
            '../../../../PySIBook/Sources/Amplifiers/VoltageAmplifierTwoPortCircuit.xml',
            '../../../../PySIBook/Sources/Amplifiers/OperationalAmplifierCircuit.xml',
            '../../../../PySIBook/Sources/Amplifiers/VoltageAmplifierFourPortSymbol.xml',
            '../../../../PySIBook/Sources/Amplifiers/VoltageAmplifierThreePortCircuit.xml',
            '../../../../PySIBook/Sources/Amplifiers/VoltageAmplifierFourPortCircuit.xml',
            '../../../../PySIBook/Sources/IdealTransformer/testIdealTransformer.xml',
            '../../../../PySIBook/Sources/IdealTransformer/IdealTransformerSP.xml',
            '../../../../PySIBook/Sources/IdealTransformer/IdealTransformerCircuit.xml',
            '../../../../PySIBook/Sources/IdealTransformer/IdealTransformerSymbol.xml',
            '../../../../PySIBook/Sources/DependentSources/DependentSources.xml',
            'SenseResistor/SenseResistorVirtualProbe.xml',
            'SenseResistor/SenseResistorMeasurement.xml',
            'SenseResistor/SenseResistorSimple.xml',
            '../../../../PySIBook/Measurement/TDRSimulation.xml',
            '../../../../PySIBook/Measurement/TDRSimulation2.xml',
        ]
        for filename in filesList:
            self.setUp()
            #print filename
            self.Preliminary(filename)

if __name__ == "__main__":
    unittest.main()
