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

class Test(unittest.TestCase,SParameterCompareHelper):
    relearn=True
    debug=False
    checkPictures=True
    def TestFileName(self,filename):
        return filename.replace('..', 'Up').replace('/','_').split('.')[0]
    def PictureChecker(self,pysi,filename):
        if not self.checkPictures:
            return
        currentDirectory=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        testFilename=self.TestFileName(filename)+'.TpX'
        try:
            tpx=pysi.Drawing.DrawSchematic(TpX()).Finish()
            tikz=pysi.Drawing.DrawSchematic(TikZ()).Finish()
            tpx.lineList=tpx.lineList+tikz.lineList
        except:
            self.assertTrue(False,filename + ' couldnt be drawn')
        if not os.path.exists(testFilename):
            tpx.WriteToFile(testFilename)
            if not self.relearn:
                self.assertTrue(False, testFilename + ' not found')
        with open(testFilename) as f:
            regression=f.readlines()
        self.assertTrue(tpx.lineList==regression,testFilename + ' incorrect')
        os.chdir(currentDirectory)
    def NetListChecker(self,pysi,filename):
        currentDirectory=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        testFilename=self.TestFileName(filename)+'.net'
        try:
            netlist=pysi.Drawing.schematic.NetList().Text()
        except:
            self.assertTrue(False,filename + ' couldnt produce netlist')
        netlist=[line+'\n' for line in netlist]
        if not os.path.exists(testFilename):
            with open(testFilename,"w") as f:
                for line in netlist:
                    f.write(line)
                if not self.relearn:
                    self.assertTrue(False, testFilename + ' not found')
        with open(testFilename) as f:
            regression=f.readlines()
        self.assertTrue(netlist==regression,testFilename + ' incorrect')
        os.chdir(currentDirectory)
    def SParameterRegressionChecker(self,sp,spfilename):
        currentDirectory=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))        
        if not os.path.exists(spfilename):
            sp.WriteToFile(spfilename)
            if not self.relearn:
                self.assertTrue(False, spfilename + ' not found')
        regression=si.sp.SParameterFile(spfilename)
        self.assertTrue(self.SParametersAreEqual(sp, regression),spfilename + ' incorrect')
        os.chdir(currentDirectory)
    def WaveformRegressionChecker(self,wf,wffilename):
        currentDirectory=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))        
        if not os.path.exists(wffilename):
            wf.WriteToFile(wffilename)
            if not self.relearn:
                self.assertTrue(False, wffilename + ' not found')
        regression=si.td.wf.Waveform().ReadFromFile(wffilename)
        self.assertTrue(wf==regression,wffilename + ' incorrect')
        os.chdir(currentDirectory)
    def Preliminary(self,filename,checkPicture=True,checkNetlist=True):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        pysi=PySIAppHeadless()
        self.assertTrue(pysi.OpenProjectFile(os.path.realpath(filename)),filename + ' couldnt be opened')
        if checkPicture:
            self.PictureChecker(pysi,filename)
        if checkNetlist:
            self.NetListChecker(pysi,filename)
        return pysi
    def SParameterResultsChecker(self,filename,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkPicture, checkNetlist)
        result=pysi.CalculateSParameters()
        self.assertIsNotNone(result, filename+' produced none')
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        spfilename=result[1]
        spfilename=self.TestFileName(filename)+'.'+spfilename.split('.')[-1]
        sp=result[0]
        self.SParameterRegressionChecker(sp, spfilename)
    def SimulationResultsChecker(self,filename,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkPicture, checkNetlist)
        result=pysi.Simulate()
        self.assertIsNotNone(result, filename+' produced none')
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]
        try:
            sp=transferMatrices.SParameters()
            ports=sp.m_P
            if ports == 0:
                raise
        except:
            self.assertTrue(False, filename + 'has no transfer matrices')
        spfilename=self.TestFileName(filename)+'.s'+str(ports)+'p'
        self.SParameterRegressionChecker(sp, spfilename)
        for i in range(len(outputNames)):
            wf=outputWaveforms[i]
            wffilename=self.TestFileName(filename)+'_'+outputNames[i]+'.txt'
            self.WaveformRegressionChecker(wf, wffilename)
    def VirtualProbeResultsChecker(self,filename,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkPicture, checkNetlist)
        result=pysi.VirtualProbe()
        self.assertIsNotNone(result, filename+' produced none')
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        measNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]
        try:
            sp=transferMatrices.SParameters()
            ports=sp.m_P
            if ports == 0:
                raise
        except:
            self.assertTrue(False, filename + 'has no transfer matrices')
        spfilename=self.TestFileName(filename)+'.s'+str(ports)+'p'
        self.SParameterRegressionChecker(sp, spfilename)
        for i in range(len(outputNames)):
            wf=outputWaveforms[i]
            wffilename=self.TestFileName(filename)+'_'+outputNames[i]+'.txt'
            self.WaveformRegressionChecker(wf, wffilename)
    def DeembeddingResultsChecker(self,filename,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkPicture, checkNetlist)
        result=pysi.Deembed()
        self.assertIsNotNone(result, filename+' produced none')
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        spfilenames=result[0]
        spfilenames=[self.TestFileName(filename)+'_'+spf for spf in spfilenames]
        sps=result[1]
        for i in range(len(spfilenames)):
            sp=sps[i]
            spfilename=spfilenames[i]+'.s'+str(sp.m_P)+'p'
            self.SParameterRegressionChecker(sp, spfilename)
    def testFourPortTLineTest(self):
        self.SimulationResultsChecker('FourPortTLineTest.xml')
    def testFilterTest(self):
        self.SimulationResultsChecker('FilterTest.xml')
    def testPySIAppExamplesRLCTest2(self):
        self.SimulationResultsChecker('../../PySIApp/Examples/RLCTest2.xml')
    def testPySIAppDeembedCableFilter(self):
        self.DeembeddingResultsChecker('../../PySIApp/Examples/DeembedCableFilter.xml')
    def testPySIAppExampleSparameterExampleSParameterGenerationExample(self):
        self.SParameterResultsChecker('../../PySIApp/Examples/SParameterExample/SParameterGenerationExample.xml')
    def testPySIAppExampleVirtualProbingExampleVirtualProbeExample(self):
        self.VirtualProbeResultsChecker('../../PySIApp/Examples/VirtualProbingExample/VirtualProbeExample.xml')
    def testOpenStub(self):
        self.SParameterResultsChecker('OpenStub.xml')
    def testPySIAppExampleCascCableFilter(self):
        self.SParameterResultsChecker('../../PySIApp/Examples/CascCableFilter.xml')
    def testPySIAppExamplesRLCTest(self):
        self.SimulationResultsChecker('../../PySIApp/Examples/RLCTest.xml')
    def testPySIAppExamplesRC(self):
        self.SimulationResultsChecker('../../PySIApp/Examples/RC.xml')
    def testPySIAppExampleTelegrapherFourPort(self):
        self.SParameterResultsChecker('../../PySIApp/Examples/telegrapherFourPort.xml')
    def testPySIAppExampleTelegrapherTestTwoPort(self):
        self.SParameterResultsChecker('../../PySIApp/Examples/telegrapherTestTwoPort.xml')
    def testPySIAppExamplesSimulationExampleBMYcheby(self):
        self.SimulationResultsChecker('../../PySIApp/Examples/SimulationExample/BMYcheby.xml')
    def testPySIAppExamplesSimulationExampleBMYchebySParameters(self):
        self.SParameterResultsChecker('../../PySIApp/Examples/SimulationExample/BMYchebySParameters.xml')
    def testPySIAppExamplesSimulationExampleInvCheby_8(self):
        self.SimulationResultsChecker('../../PySIApp/Examples/SimulationExample/InvCheby_8.xml')
    def testPySIAppExamplesPulseGeneratorTest(self):
        self.SimulationResultsChecker('../../PySIApp/Examples/PulseGeneratorTest.xml')
    def testPySIAppExamplesStepGeneratorTest(self):
        self.SimulationResultsChecker('../../PySIApp/Examples/StepGeneratorTest.xml')
    def testPySIAppPySIBookMeasurementTDRSimulationTest(self):
        self.SimulationResultsChecker('../../../PySIBook/Measurement/TDRSimulation.xml')
    def testPySIAppPySIBookMeasurementTDRSimulationTest2(self):
        self.SimulationResultsChecker('../../../PySIBook/Measurement/TDRSimulation2.xml')
    def testPySIAppPySIBookMeasurementTDRSimulationTest3(self):
        self.SimulationResultsChecker('../../../PySIBook/Measurement/TDRSimulation3.xml')
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
            '../../../PySI/PySIApp/PowerIntegrity/TestVRMIstvan2.xml',
            '../../../PySI/PySIApp/PowerIntegrity/VP/Measure.xml',
            '../../../PySI/PySIApp/PowerIntegrity/VP/Calculate.xml',
            '../../../PySI/PySIApp/PowerIntegrity/VP/Compare.xml',
            '../../../PySI/PySIApp/PowerIntegrity/TestVRMIstvan.xml',
            '../../../PySI/PySIApp/PowerIntegrity/TestVRMEquiv.xml',
            '../../../PySI/PySIApp/PowerIntegrity/VRMWaveformCompare.xml',
            '../../../PySI/PySIApp/PowerIntegrity/TestCNaturalResponse.xml',
            '../../../PySI/PySIApp/PowerIntegrity/TestVRMModel.xml',
            '../../../PySI/PySIApp/PowerIntegrity/VPSteady/FeedbackNetwork.xml',
            '../../../PySI/PySIApp/PowerIntegrity/VPSteady/Measure5.xml',
            '../../../PySI/PySIApp/PowerIntegrity/VPSteady/Measure.xml',
            '../../../PySI/PySIApp/PowerIntegrity/VPSteady/Measure2.xml',
            '../../../PySI/PySIApp/PowerIntegrity/VPSteady/Measure4.xml',
            '../../../PySI/PySIApp/PowerIntegrity/VPSteady/Measure3.xml',
            '../../../PySI/PySIApp/PowerIntegrity/VPSteady/Measure6.xml',
            '../../../PySI/PySIApp/PowerIntegrity/LoadResistanceBWL.xml',
            '../../../PySI/PySIApp/PowerIntegrity/TestVRMEquivAC.xml',
            '../../../PySI/PySIApp/PowerIntegrity/TestVRM.xml',
            '../../../PySI/Test/TestSignalIntegrity/TestCurrentSense.xml',
            '../../../PySI/Test/TestSignalIntegrity/TestVRMParasitics.xml',
            '../../../PySI/Test/TestSignalIntegrity/TestVRM.xml',
            '../../../PySI/PySIApp/FourPortTests/DifferentialTransmissionLineComparesMixedMode.xml',
            '../../../PySI/PySIApp/FourPortTests/Mutual.xml',
            '../../../PySI/PySIApp/FourPortTests/telegrapherFourPortTwoElements.xml',
            '../../../PySI/PySIApp/FourPortTests/telegrapherFourPortCircuitOneSection.xml',
            '../../../PySI/PySIApp/FourPortTests/DifferentialTransmissionLineCompares.xml',
            '../../../PySI/PySIApp/FourPortTests/telegrapherFourPortElement.xml',
            '../../../PySI/PySIApp/FourPortTests/TL_test_Circuit1_Pete.xml',
            '../../../PySI/PySIApp/FourPortTests/telegrapherFourPort10000Elements.xml',
            '../../../PySI/PySIApp/FourPortTests/DimaWay.xml',
            '../../../PySI/PySIApp/FourPortTests/telegrapherFourPortCircuitTwoSections.xml',
            '../../../PySI/PySIApp/Examples/RLCTest.xml',
            '../../../PySI/PySIApp/Examples/telegrapherFourPort.xml',
            '../../../PySI/PySIApp/Examples/SParameterExample.xml',
            '../../../PySI/PySIApp/Examples/RC.xml',
            '../../../PySI/PySIApp/Examples/telegrapherTestFourPort.xml',
            '../../../PySI/PySIApp/Examples/SParameterExample/SParameterGenerationExample.xml',
            '../../../PySI/PySIApp/Examples/DeembedCableFilter.xml',
            '../../../PySI/PySIApp/Examples/PulseGeneratorTest.xml',
            '../../../PySI/PySIApp/Examples/SimulationExample/SimulatorExample.xml',
            '../../../PySI/PySIApp/Examples/SimulationExample/InvCheby_8.xml',
            '../../../PySI/PySIApp/Examples/SimulationExample/BMYcheby.xml',
            '../../../PySI/PySIApp/Examples/SimulationExample/BMYchebySParameters.xml',
            '../../../PySI/PySIApp/Examples/telegrapherTestTwoPort.xml',
            '../../../PySI/PySIApp/Examples/VirtualProbingExample/VirtualProbeExampleSimulation2.xml',
            '../../../PySI/PySIApp/Examples/VirtualProbingExample/VirtualProbeExampleSimulation.xml',
            '../../../PySI/PySIApp/Examples/VirtualProbingExample/VirtualProbeExampleCompare.xml',
            '../../../PySI/PySIApp/Examples/VirtualProbingExample/VirtualProbeExample.xml',
            '../../../PySI/PySIApp/Examples/RLC.xml',
            '../../../PySI/PySIApp/Examples/CascCableFilter.xml',
            '../../../PySI/PySIApp/Examples/StepGeneratorTest.xml',
            '../../../PySI/PySIApp/Examples/RLCTest2.xml',
            '../../../PySI/PySIApp/VirtualProbeTests/comparison.xml',
            '../../../PySI/PySIApp/VirtualProbeTests/Example2.xml',
            '../../../PySI/PySIApp/VirtualProbeTests/SimpleCaseExample1.xml',
            '../../../PySI/PySIApp/VirtualProbeTests/Example3DegreeOfFreedom.xml',
            '../../../PySI/PySIApp/VirtualProbeTests/SimpleCase.xml',
#             '../../../PySIBook/TransmissionLines/TerminationDifferentialCenterTapUnbalanced.xml',
#             '../../../PySIBook/TransmissionLines/FourPortMixedModeModelCompareTlines.xml',
#             '../../../PySIBook/TransmissionLines/TerminationMixedMode.xml',
#             '../../../PySIBook/TransmissionLines/MixedModeSimulation.xml',
#             '../../../PySIBook/TransmissionLines/MixedModeConverterSymbol.xml',
#             '../../../PySIBook/TransmissionLines/FourPortMixedModeModelCompareTelegrapher.xml',
#             '../../../PySIBook/TransmissionLines/TerminationDifferentialCenterTapACCoupled.xml',
#             '../../../PySIBook/TransmissionLines/TerminationDifferentialTee.xml',
#             '../../../PySIBook/TransmissionLines/TerminationDifferentialCenterTap.xml',
#             '../../../PySIBook/TransmissionLines/SimulationTerminationDifferentialTee.xml',
#             '../../../PySIBook/TransmissionLines/BalancedFourPortTelegrapherMixedMode.xml',
#             '../../../PySIBook/TransmissionLines/TerminationDifferentialOnly.xml',
#             '../../../PySIBook/TransmissionLines/DifferentialTelegrapher.xml',
#             '../../../PySIBook/TransmissionLines/DifferentialTelegrapherBalancede.xml',
#             '../../../PySIBook/TransmissionLines/TerminationDifferentialPi.xml',
#             '../../../PySIBook/TransmissionLines/BalancedFourPortModelMixedMode.xml',
#             '../../../PySIBook/TransmissionLines/MixedModeConverterVoltageSymbol.xml',
#             '../../../PySIBook/TransmissionLines/MixedModeSimulationPi.xml',
#             '../../../PySIBook/TransmissionLines/MixedModeSimulationTee.xml',
#             '../../../PySIBook/SParameters/Mutual.xml',
#             '../../../PySIBook/Simulation/SimulationCircuitSchematic2.xml',
#             '../../../PySIBook/Simulation/SimulationCircuitBlockDiagram.xml',
#             '../../../PySIBook/Simulation/SimulationCircuitSchematic.xml',
#             '../../../PySIBook/WaveformProcessing/TransferMatricesProcessing.xml',
#             '../../../PySIBook/SymbolicDeviceSolutions/FourPortVoltageAmplifierVoltageSeriesFeedbackCircuit.xml',
#             '../../../PySIBook/SymbolicDeviceSolutions/TransistorThreePortCircuit.xml',
#             '../../../PySIBook/VirtualProbing/VirtualProbingSimpleExample.xml',
#             '../../../PySIBook/VirtualProbing/VirtualProbingTwoVoltageExample.xml',
#             '../../../PySIBook/VirtualProbing/VirtualProbingDifferentialExample.xml',
#             '../../../PySIBook/VirtualProbing/VirtualProbingProbeDeembeddingExample.xml',
#             '../../../PySIBook/NetworkParameters/ShuntImpedanceInstrumentedZ.xml',
#             '../../../PySIBook/NetworkParameters/FileDevice.xml',
#             '../../../PySIBook/NetworkParameters/YParametersSchematic.xml',
#             '../../../PySIBook/NetworkParameters/SimpleCircuitAnalysisExampleNetwork.xml',
#             '../../../PySIBook/NetworkParameters/ArbitraryCircuitInstrumentedZ.xml',
#             '../../../PySIBook/NetworkParameters/ClassicNetworkParameterDevice.xml',
#             '../../../PySIBook/NetworkParameters/CascABCD.xml',
#             '../../../PySIBook/NetworkParameters/SeriesImpedanceInstrumentedZ.xml',
#             '../../../PySIBook/NetworkParameters/SeriesImpedanceInstrumentedY.xml',
#             '../../../PySIBook/NetworkParameters/ZParametersSchematic.xml',
#             '../../../PySIBook/NetworkParameters/SimpleCircuitAnalysisExampleCircuit.xml',
#             '../../../PySIBook/Sources/Amplifiers/OperationalAmplifierSymbol.xml',
#             '../../../PySIBook/Sources/Amplifiers/VoltageAmplifierTwoPortSymbol.xml',
#             '../../../PySIBook/Sources/Amplifiers/CurrentAmplifierFourPortCircuit.xml',
#             '../../../PySIBook/Sources/Amplifiers/VoltageAmplifierTwoPortCircuit.xml',
#             '../../../PySIBook/Sources/Amplifiers/OperationalAmplifierCircuit.xml',
#             '../../../PySIBook/Sources/Amplifiers/VoltageAmplifierFourPortSymbol.xml',
#             '../../../PySIBook/Sources/Amplifiers/VoltageAmplifierThreePortCircuit.xml',
#             '../../../PySIBook/Sources/Amplifiers/VoltageAmplifierFourPortCircuit.xml',
#             '../../../PySIBook/Sources/IdealTransformer/testIdealTransformer.xml',
#             '../../../PySIBook/Sources/IdealTransformer/IdealTransformerSP.xml',
#             '../../../PySIBook/Sources/IdealTransformer/IdealTransformerCircuit.xml',
#             '../../../PySIBook/Sources/IdealTransformer/IdealTransformerSymbol.xml',
#             '../../../PySIBook/Sources/DependentSources/DependentSources.xml',
#             '../../../TempProject/SenseResistorVirtualProbe.xml',
#             '../../../TempProject/SenseResistorMeasurement.xml',
#             '../../../TempProject/SenseResistorSimple.xml',
#             '../../../PySIBook/Measurement/TDRSimulation.xml',
#             '../../../PySIBook/Measurement/TDRSimulation2.xml',
        ]
        for filename in filesList:
            self.Preliminary(filename)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
