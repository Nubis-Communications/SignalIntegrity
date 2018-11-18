"""
ProjectFile.py
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
from SignalIntegrity.App.ProjectFileBase import XMLConfiguration,XMLPropertyDefaultFloat,XMLPropertyDefaultString,XMLPropertyDefaultInt,XMLPropertyDefaultBool,XMLPropertyDefaultCoord
from SignalIntegrity.App.ProjectFileBase import ProjectFileBase,XMLProperty

import os
import sys

class DeviceNetListKeywordConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'DeviceNetListKeyword',write=False)
        self.Add(XMLPropertyDefaultString('Keyword'))
        self.Add(XMLPropertyDefaultBool('ShowKeyword',True))

class DeviceNetListConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'DeviceNetList',write=False)
        self.Add(XMLPropertyDefaultString('DeviceName'))
        self.Add(XMLPropertyDefaultString('PartName'))
        self.Add(XMLPropertyDefaultBool('ShowReference',True))
        self.Add(XMLPropertyDefaultBool('ShowPorts',True))
        self.Add(XMLProperty('Values',[DeviceNetListKeywordConfiguration() for _ in range(0)],'array',arrayType=DeviceNetListKeywordConfiguration()))

class PartPropertyConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'PartProperty')
        self.Add(XMLPropertyDefaultString('Keyword'))
        self.Add(XMLPropertyDefaultString('PropertyName',write=False))
        self.Add(XMLPropertyDefaultString('Description',write=False))
        self.Add(XMLPropertyDefaultString('Value'))
        self.Add(XMLPropertyDefaultBool('Hidden',write=False))
        self.Add(XMLPropertyDefaultBool('Visible'))
        self.Add(XMLPropertyDefaultBool('KeywordVisible'))
        self.Add(XMLPropertyDefaultString('Type',write=False))
        self.Add(XMLPropertyDefaultString('Unit',write=False))
        self.Add(XMLPropertyDefaultBool('InProjectFile',True,False))
    def OutputXML(self,indent):
        if self.GetValue('InProjectFile'):
            return XMLConfiguration.OutputXML(self, indent)
        else:
            return []

class PartPinConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'PartPin',write=False)
        self.Add(XMLPropertyDefaultInt('Number'))
        self.Add(XMLPropertyDefaultCoord('ConnectionPoint'))
        self.Add(XMLPropertyDefaultString('Orientation'))
        self.Add(XMLPropertyDefaultBool('NumberVisible'))
        self.Add(XMLPropertyDefaultBool('Visible'))
        self.Add(XMLPropertyDefaultBool('NumberingMatters'))

class PartPictureConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'PartPicture')
        self.Add(XMLPropertyDefaultString('ClassName'))
        self.Add(XMLPropertyDefaultCoord('Origin'))
        self.Add(XMLPropertyDefaultInt('Orientation'))
        self.Add(XMLPropertyDefaultBool('MirroredVertically',False))
        self.Add(XMLPropertyDefaultBool('MirroredHorizontally',False))

class DeviceConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Device')
        self.Add(XMLPropertyDefaultString('ClassName'))
        self.SubDir(PartPictureConfiguration())
        self.Add(XMLProperty('PartProperties',[PartPropertyConfiguration() for _ in range(0)],'array',arrayType=PartPropertyConfiguration()))
        self.SubDir(DeviceNetListConfiguration())

class VertexConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Vertex')
        self.Add(XMLPropertyDefaultCoord('Coord'))
        self.Add(XMLPropertyDefaultBool('Selected',False,False))
#     def OutputXML(self,indent):
#         return [indent+'<Vertex>'+str(self.dict['Coord'].dict['value'])+'</Vertex>']

class WireConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Wire')
        self.Add(XMLProperty('Vertices',[VertexConfiguration() for _ in range(0)],'array',arrayType=VertexConfiguration()))

class DrawingPropertiesConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'DrawingProperties')
        self.Add(XMLPropertyDefaultFloat('Grid',32.))
        self.Add(XMLPropertyDefaultInt('Originx',1))
        self.Add(XMLPropertyDefaultInt('Originy',4))
        self.Add(XMLPropertyDefaultInt('Width',711))
        self.Add(XMLPropertyDefaultInt('Height',318))
        self.Add(XMLPropertyDefaultString('Geometry','711x363+27+56'))

class SchematicConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Schematic')
        self.Add(XMLProperty('Devices',[DeviceConfiguration() for _ in range(0)],'array',arrayType=DeviceConfiguration()))
        self.Add(XMLProperty('Wires',[WireConfiguration() for _ in range(0)],'array',arrayType=WireConfiguration()))

class DrawingConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Drawing')
        self.SubDir(DrawingPropertiesConfiguration())
        self.dict['Schematic']=SchematicConfiguration()

class CalculationPropertiesConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'CalculationProperties')
        self.Add(XMLPropertyDefaultFloat('EndFrequency',20e9))
        self.Add(XMLPropertyDefaultInt('FrequencyPoints',2000))
        self.Add(XMLPropertyDefaultFloat('UserSampleRate',40e9))
        self.Add(XMLPropertyDefaultFloat('BaseSampleRate'))
        self.Add(XMLPropertyDefaultInt('TimePoints'))
        self.Add(XMLPropertyDefaultFloat('FrequencyResolution'))
        self.Add(XMLPropertyDefaultFloat('ImpulseResponseLength'))

class ProjectFile(ProjectFileBase):
    def __init__(self):
        ProjectFileBase.__init__(self,'si')
        self.SubDir(DrawingConfiguration())
        self.SubDir(CalculationPropertiesConfiguration())

    def Read(self, filename,drawing):
        ProjectFileBase.Read(self, filename)
        # calculate certain calculation properties
        self.SetValue('CalculationProperties.BaseSampleRate', self.GetValue('CalculationProperties.EndFrequency')*2)
        self.SetValue('CalculationProperties.TimePoints',self.GetValue('CalculationProperties.FrequencyPoints')*2)
        self.SetValue('CalculationProperties.FrequencyResolution', self.GetValue('CalculationProperties.EndFrequency')/self.GetValue('CalculationProperties.FrequencyPoints'))
        self.SetValue('CalculationProperties.ImpulseResponseLength',1./self.GetValue('CalculationProperties.FrequencyResolution'))
        drawing.InitFromProject(self)
        return self

    def Write(self,filename,app):
        self.SetValue('Drawing.DrawingProperties.Grid',app.Drawing.grid)
        self.SetValue('Drawing.DrawingProperties.Originx',app.Drawing.originx)
        self.SetValue('Drawing.DrawingProperties.Originy',app.Drawing.originy)
        if not app.Drawing.canvas is None:
            self.SetValue('Drawing.DrawingProperties.Width',app.Drawing.canvas.winfo_width())
            self.SetValue('Drawing.DrawingProperties.Height',app.Drawing.canvas.winfo_height())
            self.SetValue('Drawing.DrawingProperties.Geometry',app.root.geometry())
        self.SetValue('Drawing.Schematic.Devices',[DeviceConfiguration() for _ in range(len(app.Drawing.schematic.deviceList))])
        for d in range(len(self.GetValue('Drawing.Schematic.Devices'))):
            deviceProject=self.GetValue('Drawing.Schematic.Devices')[d]
            device=app.Drawing.schematic.deviceList[d]
            deviceProject.SetValue('ClassName',device.__class__.__name__)
            partPictureProject=deviceProject.GetValue('PartPicture')
            partPicture=device.partPicture
            partPictureProject.SetValue('ClassName',partPicture.partPictureClassList[partPicture.partPictureSelected])
            partPictureProject.SetValue('Origin',partPicture.current.origin)
            partPictureProject.SetValue('Orientation',partPicture.current.orientation)
            partPictureProject.SetValue('MirroredVertically',partPicture.current.mirroredVertically)
            partPictureProject.SetValue('MirroredHorizontally',partPicture.current.mirroredHorizontally)
            deviceProject.SetValue('PartProperties',device.propertiesList)
            deviceNetListProject=deviceProject.GetValue('DeviceNetList')
            deviceNetList=device.netlist
            for n in deviceNetList.dict:
                deviceNetListProject.SetValue(n,deviceNetList.GetValue(n))
        ProjectFileBase.Write(self,filename)
        return self

# Legacy File Format
if __name__ == '__main__':

    from SignalIntegrity.App.SignalIntegrityApp import TheApp

    class App(TheApp):
        def __init__(self):
            TheApp.__init__(self,False)
        def ConvertOldProjectToNew(self,oldfilename,newfilename):
            import xml.etree.ElementTree as et
            tree=et.parse(oldfilename)
            root=tree.getroot()
            for child in root:
                if child.tag == 'drawing':
                    self.Drawing.InitFromXml(child)
                elif child.tag == 'calculation_properties':
                    from CalculationProperties import CalculationProperties
                    self.calculationProperties=CalculationProperties(self)
                    self.calculationProperties.InitFromXml(child, self)
            project=ProjectFile()
            project.SetValue('Drawing.DrawingProperties.Grid',self.Drawing.grid)
            project.SetValue('Drawing.DrawingProperties.Originx',self.Drawing.originx)
            project.SetValue('Drawing.DrawingProperties.Originy',self.Drawing.originy)
            project.SetValue('Drawing.DrawingProperties.Width',self.Drawing.canvas.winfo_width())
            project.SetValue('Drawing.DrawingProperties.Height',self.Drawing.canvas.winfo_height())
            project.SetValue('Drawing.DrawingProperties.Geometry',self.root.geometry())
            project.SetValue('Drawing.Schematic.Devices',[DeviceConfiguration() for _ in range(len(self.Drawing.schematic.deviceList))])
            for d in range(len(project.GetValue('Drawing.Schematic.Devices'))):
                deviceProject=project.GetValue('Drawing.Schematic.Devices')[d]
                device=self.Drawing.schematic.deviceList[d]
                deviceProject.SetValue('ClassName',device.__class__.__name__)
                partPictureProject=deviceProject.GetValue('PartPicture')
                partPicture=device.partPicture
                partPictureProject.SetValue('ClassNames',[XMLPropertyDefaultString('ClassName',name) for name in partPicture.partPictureClassList])
                partPictureProject.SetValue('Selected',partPicture.partPictureSelected)
                partPictureProject.SetValue('Origin',partPicture.current.origin)
                partPictureProject.SetValue('Orientation',partPicture.current.orientation)
                partPictureProject.SetValue('MirroredVertically',partPicture.current.mirroredVertically)
                partPictureProject.SetValue('MirroredHorizontally',partPicture.current.mirroredHorizontally)
                deviceProject.SetValue('PartProperties',device.propertiesList)
            project.SetValue('Drawing.Schematic.Wires',[WireConfiguration() for _ in range(len(self.Drawing.schematic.wireList))])
            for w in range(len(project.GetValue('Drawing.Schematic.Wires'))):
                wireProject=project.GetValue('Drawing.Schematic.Wires')[w]
                wire=self.Drawing.schematic.wireList[w]
                wireProject.SetValue('Vertices',[VertexConfiguration() for vertex in wire])
                for v in range(len(wireProject.GetValue('Vertices'))):
                    vertexProject=wireProject.GetValue('Vertices')[v]
                    vertex=wire[v]
                    vertexProject.SetValue('Coord',vertex.coord)
            project.SetValue('CalculationProperties.EndFrequency',self.calculationProperties.endFrequency)
            project.SetValue('CalculationProperties.FrequencyPoints',self.calculationProperties.frequencyPoints)
            project.SetValue('CalculationProperties.UserSampleRate',self.calculationProperties.userSampleRate)
            project.Write(newfilename,self)
            project.Read(newfilename,self.Drawing)
            project.Write(newfilename,self)
            #project.PrintFullInformation()


    filesList=[
        '/home/peterp/Work/PySI/TestPySIApp/FilterTest.xml',
        '/home/peterp/Work/PySI/TestPySIApp/FourPortTLineTest.xml',
        '/home/peterp/Work/PySI/TestPySIApp/Devices.xml',
        '/home/peterp/Work/PySI/TestPySIApp/TestVRM.xml',
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
        '/home/peterp/Work/PySI/PySIApp/Examples/XRAYTest.xml',
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
        '/home/peterp/Work/PySI/PySIApp/Examples/XRAYTest2.xml',
        '/home/peterp/Work/PySI/PySIApp/Examples/telegrapherTestTwoPort.xml',
        '/home/peterp/Work/PySI/PySIApp/Examples/VirtualProbingExample/VirtualProbeExampleSimulation2.xml',
        '/home/peterp/Work/PySI/PySIApp/Examples/VirtualProbingExample/VirtualProbeExampleSimulation.xml',
        '/home/peterp/Work/PySI/PySIApp/Examples/VirtualProbingExample/VirtualProbeExampleCompare.xml',
        '/home/peterp/Work/PySI/PySIApp/Examples/VirtualProbingExample/VirtualProbeExample.xml',
        '/home/peterp/Work/PySI/PySIApp/Examples/RLC.xml',
        '/home/peterp/Work/PySI/PySIApp/Examples/CascCableFilter.xml',
        #'/home/peterp/Work/PySI/PySIApp/Examples/RCNetwork.xml',
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

    app=App()
    for file in filesList:
        oldfile=file
        newfile=file.split('.')[0]+'.si'
        
        print 'oldfile: '+oldfile+' -> newfile: '+newfile
        app.ConvertOldProjectToNew(oldfile,newfile)
