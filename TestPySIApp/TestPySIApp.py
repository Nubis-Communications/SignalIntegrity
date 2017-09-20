'''
Created on Sep 7, 2017

@author: pete
'''
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
    def TestFileName(self,filename):
        return filename.replace('..', 'Up').replace('/','_').split('.')[0]
    def PictureChecker(self,pysi,filename):
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
        self.SimulationResultsChecker('../PySIApp/Examples/RLCTest2.xml')
    def testPySIAppDeembedCableFilter(self):
        self.DeembeddingResultsChecker('../PySIApp/Examples/DeembedCableFilter.xml')
    def testPySIAppExampleSparameterExampleSParameterGenerationExample(self):
        self.SParameterResultsChecker('../PySIApp/Examples/SParameterExample/SParameterGenerationExample.xml')
    def testPySIAppExampleVirtualProbingExampleVirtualProbeExample(self):
        self.VirtualProbeResultsChecker('../PySIApp/Examples/VirtualProbingExample/VirtualProbeExample.xml')
    def testOpenStub(self):
        self.SParameterResultsChecker('OpenStub.xml')
    def testPySIAppExamplesPulseGeneratorTest(self):
        self.SimulationResultsChecker('../PySIApp/Examples/PulseGeneratorTest.xml')
    def testPySIAppExamplesStepGeneratorTest(self):
        self.SimulationResultsChecker('../PySIApp/Examples/StepGeneratorTest.xml')
    def testPicturesNetlists(self):
        filesList=[
            '/home/peterp/Work/PySI/TestPySIApp/FilterTest.xml',
            '/home/peterp/Work/PySI/TestPySIApp/FourPortTLineTest.xml',
            '/home/peterp/Work/PySI/TestPySIApp/Devices.xml',
            '/home/peterp/Work/PySI/TestPySIApp/Noise.xml',
            '/home/peterp/Work/PySI/TestPySIApp/OpenStub.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/TestVRMIstvan2.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/VP/Measure.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/VP/Calculate.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/VP/Compare.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/TestVRMIstvan.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/TestVRMEquiv.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/VRMWaveformCompare.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/TestCNaturalResponse.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/TestVRMModel.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/VPSteady/FeedbackNetwork.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/VPSteady/Measure5.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/VPSteady/Measure.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/VPSteady/Measure2.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/VPSteady/Measure4.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/VPSteady/Measure3.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/VPSteady/Measure6.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/LoadResistanceBWL.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/TestVRMEquivAC.xml',
            '/home/peterp/Work/PySI/PowerIntegrity/TestVRM.xml',
            '/home/peterp/Work/PySI/TestSignalIntegrity/TestCurrentSense.xml',
            '/home/peterp/Work/PySI/TestSignalIntegrity/TestVRMParasitics.xml',
            '/home/peterp/Work/PySI/TestSignalIntegrity/TestVRM.xml',
            '/home/peterp/Work/PySI/PySIApp/FourPortTests/DifferentialTransmissionLineComparesMixedMode.xml',
            '/home/peterp/Work/PySI/PySIApp/FourPortTests/Mutual.xml',
            '/home/peterp/Work/PySI/PySIApp/FourPortTests/telegrapherFourPortTwoElements.xml',
            '/home/peterp/Work/PySI/PySIApp/FourPortTests/telegrapherFourPortCircuitOneSection.xml',
            '/home/peterp/Work/PySI/PySIApp/FourPortTests/DifferentialTransmissionLineCompares.xml',
            '/home/peterp/Work/PySI/PySIApp/FourPortTests/telegrapherFourPortElement.xml',
            '/home/peterp/Work/PySI/PySIApp/FourPortTests/TL_test_Circuit1_Pete.xml',
            '/home/peterp/Work/PySI/PySIApp/FourPortTests/telegrapherFourPort10000Elements.xml',
            '/home/peterp/Work/PySI/PySIApp/FourPortTests/DimaWay.xml',
            '/home/peterp/Work/PySI/PySIApp/FourPortTests/telegrapherFourPortCircuitTwoSections.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/RLCTest.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/telegrapherFourPort.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/SParameterExample.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/RC.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/telegrapherTestFourPort.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/SParameterExample/SParameterGenerationExample.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/DeembedCableFilter.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/PulseGeneratorTest.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/SimulationExample/SimulatorExample.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/SimulationExample/InvCheby_8.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/SimulationExample/BMYcheby.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/SimulationExample/BMYchebySParameters.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/telegrapherTestTwoPort.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/VirtualProbingExample/VirtualProbeExampleSimulation2.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/VirtualProbingExample/VirtualProbeExampleSimulation.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/VirtualProbingExample/VirtualProbeExampleCompare.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/VirtualProbingExample/VirtualProbeExample.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/RLC.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/CascCableFilter.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/StepGeneratorTest.xml',
            '/home/peterp/Work/PySI/PySIApp/Examples/RLCTest2.xml',
            '/home/peterp/Work/PySI/PySIApp/VirtualProbeTests/comparison.xml',
            '/home/peterp/Work/PySI/PySIApp/VirtualProbeTests/Example2.xml',
            '/home/peterp/Work/PySI/PySIApp/VirtualProbeTests/SimpleCaseExample1.xml',
            '/home/peterp/Work/PySI/PySIApp/VirtualProbeTests/Example3DegreeOfFreedom.xml',
            '/home/peterp/Work/PySI/PySIApp/VirtualProbeTests/SimpleCase.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/TerminationDifferentialCenterTapUnbalanced.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/FourPortMixedModeModelCompareTlines.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/TerminationMixedMode.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/MixedModeSimulation.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/MixedModeConverterSymbol.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/FourPortMixedModeModelCompareTelegrapher.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/TerminationDifferentialCenterTapACCoupled.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/TerminationDifferentialTee.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/TerminationDifferentialCenterTap.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/SimulationTerminationDifferentialTee.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/BalancedFourPortTelegrapherMixedMode.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/TerminationDifferentialOnly.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/DifferentialTelegrapher.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/DifferentialTelegrapherBalancede.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/TerminationDifferentialPi.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/BalancedFourPortModelMixedMode.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/MixedModeConverterVoltageSymbol.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/MixedModeSimulationPi.xml',
            '/home/peterp/Work/PySIBook/TransmissionLines/MixedModeSimulationTee.xml',
            '/home/peterp/Work/PySIBook/SParameters/Mutual.xml',
            '/home/peterp/Work/PySIBook/Simulation/SimulationCircuitSchematic2.xml',
            '/home/peterp/Work/PySIBook/Simulation/SimulationCircuitBlockDiagram.xml',
            '/home/peterp/Work/PySIBook/Simulation/SimulationCircuitSchematic.xml',
            '/home/peterp/Work/PySIBook/WaveformProcessing/TransferMatricesProcessing.xml',
            '/home/peterp/Work/PySIBook/SymbolicDeviceSolutions/FourPortVoltageAmplifierVoltageSeriesFeedbackCircuit.xml',
            '/home/peterp/Work/PySIBook/SymbolicDeviceSolutions/TransistorThreePortCircuit.xml',
            '/home/peterp/Work/PySIBook/VirtualProbing/VirtualProbingSimpleExample.xml',
            '/home/peterp/Work/PySIBook/VirtualProbing/VirtualProbingTwoVoltageExample.xml',
            '/home/peterp/Work/PySIBook/VirtualProbing/VirtualProbingDifferentialExample.xml',
            '/home/peterp/Work/PySIBook/VirtualProbing/VirtualProbingProbeDeembeddingExample.xml',
            '/home/peterp/Work/PySIBook/NetworkParameters/ShuntImpedanceInstrumentedZ.xml',
            '/home/peterp/Work/PySIBook/NetworkParameters/FileDevice.xml',
            '/home/peterp/Work/PySIBook/NetworkParameters/YParametersSchematic.xml',
            '/home/peterp/Work/PySIBook/NetworkParameters/SimpleCircuitAnalysisExampleNetwork.xml',
            '/home/peterp/Work/PySIBook/NetworkParameters/ArbitraryCircuitInstrumentedZ.xml',
            '/home/peterp/Work/PySIBook/NetworkParameters/ClassicNetworkParameterDevice.xml',
            '/home/peterp/Work/PySIBook/NetworkParameters/CascABCD.xml',
            '/home/peterp/Work/PySIBook/NetworkParameters/SeriesImpedanceInstrumentedZ.xml',
            '/home/peterp/Work/PySIBook/NetworkParameters/SeriesImpedanceInstrumentedY.xml',
            '/home/peterp/Work/PySIBook/NetworkParameters/ZParametersSchematic.xml',
            '/home/peterp/Work/PySIBook/NetworkParameters/SimpleCircuitAnalysisExampleCircuit.xml',
            '/home/peterp/Work/PySIBook/Sources/Amplifiers/OperationalAmplifierSymbol.xml',
            '/home/peterp/Work/PySIBook/Sources/Amplifiers/VoltageAmplifierTwoPortSymbol.xml',
            '/home/peterp/Work/PySIBook/Sources/Amplifiers/CurrentAmplifierFourPortCircuit.xml',
            '/home/peterp/Work/PySIBook/Sources/Amplifiers/VoltageAmplifierTwoPortCircuit.xml',
            '/home/peterp/Work/PySIBook/Sources/Amplifiers/OperationalAmplifierCircuit.xml',
            '/home/peterp/Work/PySIBook/Sources/Amplifiers/VoltageAmplifierFourPortSymbol.xml',
            '/home/peterp/Work/PySIBook/Sources/Amplifiers/VoltageAmplifierThreePortCircuit.xml',
            '/home/peterp/Work/PySIBook/Sources/Amplifiers/VoltageAmplifierFourPortCircuit.xml',
            '/home/peterp/Work/PySIBook/Sources/IdealTransformer/testIdealTransformer.xml',
            '/home/peterp/Work/PySIBook/Sources/IdealTransformer/IdealTransformerSP.xml',
            '/home/peterp/Work/PySIBook/Sources/IdealTransformer/IdealTransformerCircuit.xml',
            '/home/peterp/Work/PySIBook/Sources/IdealTransformer/IdealTransformerSymbol.xml',
            '/home/peterp/Work/PySIBook/Sources/DependentSources/DependentSources.xml',
            '/home/peterp/Work/TempProject/SenseResistorVirtualProbe.xml',
            '/home/peterp/Work/TempProject/SenseResistorMeasurement.xml',
            '/home/peterp/Work/TempProject/SenseResistorSimple.xml'
        ]
        for filename in filesList:
            filename=filename.replace('/home/peterp/Work','../..')
            self.Preliminary(filename)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()