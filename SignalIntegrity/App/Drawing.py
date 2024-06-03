"""
Drawing.py
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
import sys
if sys.version_info.major < 3:
    import Tkinter as tk
else:
    import tkinter as tk

import copy

from SignalIntegrity.App.Schematic import Schematic
from SignalIntegrity.App.DrawingStateMachine import DrawingStateMachine
from SignalIntegrity.App.DeviceProperties import DevicePropertiesDialog
from SignalIntegrity.App.PartPicture import PartPicture
from SignalIntegrity.App.Wire import Wire

import SignalIntegrity.App.Project

class Drawing(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        self.parent=parent
        self.canvas = tk.Canvas(self,relief=tk.SUNKEN,borderwidth=1,width=600,height=600)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        self.schematic = Schematic()
        self.deviceTearOffMenu=tk.Menu(self, tearoff=0)
        self.deviceTearOffMenu.add_command(label="Edit Properties",command=self.EditSelectedDevice)
        self.deviceTearOffMenu.add_command(label="Duplicate",command=self.DuplicateSelectedDevice)
        self.deviceTearOffMenu.add_command(label="Delete",command=self.DeleteSelectedDevice)
        self.deviceTearOffMenu.add_command(label='Convert',command=self.ConvertSelectedDevice)
        self.canvasTearOffMenu=tk.Menu(self, tearoff=0)
        self.canvasTearOffMenu.add_command(label='Add Part',command=self.parent.onAddPart)
        self.canvasTearOffMenu.add_command(label='Add Wire',command=self.parent.onAddWire)
        self.canvasTearOffMenu.add_command(label='Add Port',command=self.parent.onAddPort)
        self.wireTearOffMenu=tk.Menu(self, tearoff=0)
        self.wireTearOffMenu.add_command(label="Delete Vertex",command=self.DeleteSelectedVertex)
        self.wireTearOffMenu.add_command(label="Duplicate Vertex",command=self.DuplicateSelectedVertex)
        self.wireTearOffMenu.add_command(label="Delete Wire",command=self.DeleteSelectedWire)
        self.multipleSelectionsTearOffMenu=tk.Menu(self, tearoff=0)
        self.multipleSelectionsTearOffMenu.add_command(label="Cut Selected",command=self.CutMultipleSelections)
        self.multipleSelectionsTearOffMenu.add_command(label="Delete Selected",command=self.DeleteMultipleSelections)
        self.multipleSelectionsTearOffMenu.add_command(label="Duplicate Selected",command=self.DuplicateMultipleSelections)
        self.stateMachine = DrawingStateMachine(self)
    def NearestGridCoordinate(self,x,y):
        drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        grid=drawingPropertiesProject['Grid']
        originx=drawingPropertiesProject['Originx']
        originy=drawingPropertiesProject['Originy']
        return (int(round(float(x)/grid))-originx,int(round(float(y)/grid))-originy)
    def AugmentorToGridCoordinate(self,x,y):
        drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        grid=drawingPropertiesProject['Grid']
        originx=drawingPropertiesProject['Originx']
        originy=drawingPropertiesProject['Originy']
        (nearestGridx,nearestGridy)=self.NearestGridCoordinate(x,y)
        return (float(x)/grid-originx-nearestGridx,float(y)/grid-originy-nearestGridy)
    def DrawSchematic(self,canvas=None):
        if canvas is None:
            canvas=self.canvas
            canvas.delete(tk.ALL)
        if SignalIntegrity.App.Project is None:
            return canvas
        drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        if not canvas is None and hasattr(self, 'Drawing'):
            drawingPropertiesProject['Geometry']=self.root.geometry()
        grid=drawingPropertiesProject['Grid']
        originx=drawingPropertiesProject['Originx']
        originy=drawingPropertiesProject['Originy']
        SignalIntegrity.App.Project.EvaluateEquations()
        schematicPropertiesList=SignalIntegrity.App.Project['Variables'].DisplayStrings(True,False,False)
        V=len(schematicPropertiesList)
        locations=[(0+7,0+PartPicture.textSpacing*(v+1)+3) for v in range(V)]
        for v in range(V):
            canvas.create_text(locations[v][0],locations[v][1],text=schematicPropertiesList[v],anchor='sw',fill='black')
        devicePinConnectedList=self.schematic.DevicePinConnectedList()
        numPortsFound=0
        foundAPort=False
        foundASource=False
        foundAnOutput=False
        foundSomething=False
        foundAMeasure=False
        foundAStim=False
        foundAnUnknown=False
        foundASystem=False
        foundACalibration=False
        foundANetworkAnalyzerModel=False
        foundAWaveform=False
        for deviceIndex in range(len(self.schematic.deviceList)):
            device = self.schematic.deviceList[deviceIndex]
            foundSomething=True
            devicePinsConnected=devicePinConnectedList[deviceIndex]
            device.DrawDevice(canvas,grid,originx,originy,devicePinsConnected)
            deviceType = device['partname'].GetValue()
            if  deviceType == 'Port':
                foundAPort = True
                numPortsFound=numPortsFound+1
            elif deviceType in ['Output','DifferentialVoltageOutput','CurrentOutput','EyeProbe','DifferentialEyeProbe']:
                foundAnOutput = True
            elif deviceType in ['EyeWaveform','Waveform']:
                foundAWaveform = True
            elif deviceType == 'Stim':
                foundAStim = True
            elif deviceType == 'Measure':
                foundAMeasure = True
            elif deviceType == 'System':
                foundASystem = True
            elif deviceType == 'Unknown':
                foundAnUnknown = True
            elif device.netlist['DeviceName'] in ['voltagesource','currentsource','networkanalyzerport']:
                foundASource = True
            elif device.netlist['DeviceName'] == 'calibration':
                foundACalibration=True
            elif deviceType == 'NetworkAnalyzerModel':
                foundANetworkAnalyzerModel=True
        for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
            foundSomething=True
            wireProject.DrawWire(canvas,grid,originx,originy)
        for dot in self.schematic.DotList():
            size=grid/8
            canvas.create_oval((dot[0]+originx)*grid-size,(dot[1]+originy)*grid-size,
                                    (dot[0]+originx)*grid+size,(dot[1]+originy)*grid+size,
                                    fill='black',outline='black')
        canSimulate = ((foundASource and foundAnOutput) or foundAWaveform) and not foundAPort and not foundAStim and not foundAMeasure and not foundAnUnknown and not foundASystem and not foundACalibration
        canCalculateSParameters = foundAPort and not foundAnOutput and not foundAMeasure and not foundAStim and not foundAnUnknown and not foundASystem and not foundACalibration and not foundAWaveform
        canRLGC=canCalculateSParameters and (numPortsFound == 2)
        canVirtualProbe = foundAStim and foundAnOutput and foundAMeasure and not foundAPort and not foundASource and not foundAnUnknown and not foundASystem and not foundACalibration
        canDeembed = foundAPort and foundAnUnknown and foundASystem and not foundAStim and not foundAMeasure and not foundAnOutput and not foundACalibration and not foundAWaveform
        canCalculateErrorTerms = foundACalibration and not foundASource and not foundAnOutput and not foundAPort and not foundAStim and not foundAMeasure and not foundAnUnknown and not foundASystem and not foundAWaveform
        canSimulateNetworkAnalyzerModel = foundANetworkAnalyzerModel and not foundAPort and not foundAnOutput and not foundAMeasure and not foundAStim and not foundAnUnknown and not foundASystem and not foundACalibration  and not foundAWaveform
        canCalculateSParametersFromNetworkAnalyzerModel = canSimulateNetworkAnalyzerModel
        canCalculate = canSimulate or canCalculateSParameters or canVirtualProbe or canDeembed or canCalculateErrorTerms or canSimulateNetworkAnalyzerModel or canCalculateSParametersFromNetworkAnalyzerModel
        canGenerateTransferMatrices = (canSimulate and foundASource and foundAnOutput) or canVirtualProbe
        self.parent.SimulateDoer.Activate(canSimulate or canSimulateNetworkAnalyzerModel)
        self.parent.TransferParametersDoer.Activate(canGenerateTransferMatrices)
        self.parent.CalculateDoer.Activate(canCalculate)
        self.parent.CalculateSParametersDoer.Activate(canCalculateSParameters or canCalculateSParametersFromNetworkAnalyzerModel)
        self.parent.RLGCDoer.Activate(canRLGC)
        self.parent.VirtualProbeDoer.Activate(canVirtualProbe)
        self.parent.DeembedDoer.Activate(canDeembed)
        self.parent.CalculateErrorTermsDoer.Activate(canCalculateErrorTerms)
        self.parent.CalculateSParametersFromNetworkAnalyzerModelDoer.Activate(canCalculateSParametersFromNetworkAnalyzerModel)
        self.parent.SimulateNetworkAnalyzerModelDoer.Activate(canSimulateNetworkAnalyzerModel)
        self.parent.ClearProjectDoer.Activate(foundSomething)
        self.parent.ExportNetListDoer.Activate(foundSomething)
        self.parent.ExportTpXDoer.Activate(foundSomething)
        self.parent.ExportPngDoer.Activate(foundSomething)
        self.parent.PanDoer.Activate(foundSomething)
        self.parent.ZoomInDoer.Activate(foundSomething)
        self.parent.ZoomOutDoer.Activate(foundSomething)
        return canvas
    def EditSelectedDevice(self):
        if self.stateMachine.state=='DeviceSelected':
            dpe=DevicePropertiesDialog(self.parent,self.deviceSelected)
            if dpe.result != None:
                self.deviceSelected = dpe.result
                self.schematic.deviceList[self.deviceSelectedIndex] = self.deviceSelected
                self.schematic.Consolidate()
                self.DrawSchematic()
                self.parent.history.Event('edit device')
    def DuplicateSelectedDevice(self):
        if self.stateMachine.state=='DeviceSelected':
            self.partLoaded=copy.deepcopy(self.deviceSelected)
            if self.partLoaded['partname'].GetValue() == 'Port':
                portNumberList=[]
                for device in self.schematic.deviceList:
                    if device['partname'].GetValue() == 'Port':
                        portNumberList.append(int(device['pn'].GetValue()))
                portNumber=1
                while portNumber in portNumberList:
                    portNumber=portNumber+1
                self.partLoaded['pn'].SetValueFromString(str(portNumber))
            elif self.partLoaded['partname'].GetValue() == 'NetworkAnalyzerStimulus':
                portNumberList=[]
                for device in self.schematic.deviceList:
                    if device['partname'].GetValue() == 'NetworkAnalyzerStimulus':
                        portNumberList.append(int(device['pn'].GetValue()))
                portNumber=1
                while portNumber in portNumberList:
                    portNumber=portNumber+1
                self.partLoaded['pn'].SetValueFromString(str(portNumber))
            defaultProperty = self.partLoaded['defref']
            if defaultProperty != None:
                defaultPropertyValue = defaultProperty.GetValue()
                uniqueReferenceDesignator = self.schematic.NewUniqueReferenceDesignator(defaultPropertyValue)
                if uniqueReferenceDesignator != None:
                    self.partLoaded['ref'].SetValueFromString(uniqueReferenceDesignator)
            self.stateMachine.PartLoaded()
    def DeleteSelected(self):
        if self.stateMachine.state=='WireSelected':
            self.DeleteSelectedWire()
        elif self.stateMachine.state=='DeviceSelected':
            self.DeleteSelectedDevice()
        elif self.stateMachine.state=='Multiple Selections':
            self.DeleteMultipleSelections()
    def DeleteSelectedDevice(self):
        del self.schematic.deviceList[self.deviceSelectedIndex]
        self.stateMachine.Nothing()
        self.parent.history.Event('delete device')
    def ConvertSelectedDevice(self):
        self.parent.onConvertPart()
    def DeleteSelectedVertex(self):
        del SignalIntegrity.App.Project['Drawing.Schematic.Wires'][self.w]['Vertices'][self.v]
        self.stateMachine.Nothing()
        self.parent.history.Event('delete vertex')
    def DuplicateSelectedVertex(self):
        wireProject=SignalIntegrity.App.Project['Drawing.Schematic.Wires'][self.w]
        vertexProject=copy.deepcopy(wireProject['Vertices'][self.v])
        self.stateMachine.UnselectAllWires()
        wireProject['Vertices']=wireProject['Vertices'][:self.v]+[vertexProject]+wireProject['Vertices'][self.v:]
        self.stateMachine.WireSelected()
    def DeleteSelectedWire(self):
        del SignalIntegrity.App.Project['Drawing.Schematic.Wires'][self.w]
        self.stateMachine.Nothing()
        self.parent.history.Event('delete wire')
    def DeleteMultipleSelections(self,advanceStateMachine=True):
        newDeviceList=[]
        for device in self.schematic.deviceList:
            if not device.selected:
                newDeviceList.append(copy.deepcopy(device))
        newWireListProject=[]
        for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
            newWire= []
            for vertexProject in wireProject['Vertices']:
                if not vertexProject['Selected']:
                    newWire.append(copy.deepcopy(vertexProject))
            if len(newWire) >= 2:
                newWireProject=Wire()
                newWireProject['Vertices']=newWire
                newWireListProject.append(copy.deepcopy(newWireProject))
        SignalIntegrity.App.Project['Drawing.Schematic.Wires']=newWireListProject
        self.schematic.deviceList=newDeviceList
        if advanceStateMachine:
            self.stateMachine.Nothing()
        self.parent.history.Event('delete selections')
    def CutMultipleSelections(self):
        if self.stateMachine.state=='Multiple Selections':
            self.DuplicateMultipleSelections(False)
            self.DeleteMultipleSelections(False)
            self.stateMachine.MultipleItemsOnClipboard()
    def DuplicateSelected(self):
        if self.stateMachine.state=='Multiple Selections':
            self.DuplicateMultipleSelections()
        elif self.stateMachine.state=='DeviceSelected':
            self.DuplicateSelectedDevice()
    def DuplicateMultipleSelections(self,advanceStateMachine=True):
        if self.stateMachine.state=='Multiple Selections':
            self.devicesToDuplicate=[]
            originSet=False
            originx=0
            originy=0
            for device in self.schematic.deviceList:
                if device.selected:
                    self.devicesToDuplicate.append(copy.deepcopy(device))
                    if not originSet:
                        originSet=True
                        originx=device.partPicture.current.origin[0]
                        originy=device.partPicture.current.origin[1]
                    else:
                        originx=min(originx,device.partPicture.current.origin[0])
                        originy=min(originy,device.partPicture.current.origin[1])
            self.wiresToDuplicate=[]
            wireListProject=SignalIntegrity.App.Project['Drawing.Schematic.Wires']
            for wireProject in wireListProject:
                newWireProject = Wire()
                numVerticesSelected = 0
                firstVertexSelected = -1
                lastVertexSelected=-1
                for vertexIndex in range(len(wireProject['Vertices'])):
                    vertexProject=wireProject['Vertices'][vertexIndex]
                    if vertexProject['Selected']:
                        numVerticesSelected=numVerticesSelected+1
                        if firstVertexSelected == -1:
                            firstVertexSelected = vertexIndex
                        lastVertexSelected = vertexIndex
                if numVerticesSelected >= 2:
                    for vertexIndex in range(len(wireProject['Vertices'])):
                        if vertexIndex >= firstVertexSelected and vertexIndex <= lastVertexSelected:
                            vertexProject=wireProject['Vertices'][vertexIndex]
                            newWireProject['Vertices'].append(copy.deepcopy(vertexProject))
                            vertexCoord=vertexProject['Coord']
                            if not originSet:
                                originSet=True
                                originx=vertexCoord[0]
                                originy=vertexCoord[1]
                            else:
                                originx=min(originx,vertexCoord[0])
                                originy=min(originy,vertexCoord[1])
                if len(newWireProject['Vertices']) >= 2:
                    self.wiresToDuplicate.append(newWireProject)
            if not originSet:
                return
            # originx and originy are the upper leftmost coordinates in the selected stuff
            for device in self.devicesToDuplicate:
                device.partPicture.current.SetOrigin((device.partPicture.current.origin[0]-originx,device.partPicture.current.origin[1]-originy))
            for wireProject in self.wiresToDuplicate:
                for vertexProject in wireProject['Vertices']:
                    vertexCoord=vertexProject['Coord']
                    vertexProject['Coord']=(vertexCoord[0]-originx,vertexCoord[1]-originy)
            if advanceStateMachine:
                self.stateMachine.MultipleItemsOnClipboard()
    def InitFromProject(self):
        drawingProperties=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        # the canvas and geometry must be set prior to the remainder of the schematic initialization
        # otherwise it will not be the right size.  In the past, the xml happened to have the drawing
        # properties first, which made it work, but it was an accident.
        #self.canvas.config(width=drawingProperties['Width'],height=drawingProperties['Height'])
        self.parent.root.geometry(drawingProperties['Geometry'].split('+')[0])
        self.schematic = Schematic()
        self.schematic.InitFromProject()
        self.stateMachine = DrawingStateMachine(self)
