"""
Schematic.py
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
import sys
if sys.version_info.major < 3:
    from Tkinter import Menu,Frame,Canvas
    from Tkinter import RAISED,SUNKEN,BOTH,YES,TOP,ALL
else:
    from tkinter import Menu,Frame,Canvas
    from tkinter import RAISED,SUNKEN,BOTH,YES,TOP,ALL

import xml.etree.ElementTree as et
import copy

from SignalIntegrity.App.PartProperty import PartPropertyReferenceDesignator,PartPropertyDefaultReferenceDesignator
from SignalIntegrity.App.Device import DeviceXMLClassFactory,DeviceFromProject
from SignalIntegrity.App.NetList import NetList
from SignalIntegrity.App.Wire import WireList,Vertex,SegmentList,Wire
from SignalIntegrity.App.MenuSystemHelpers import Doer
from SignalIntegrity.App.DeviceProperties import DevicePropertiesDialog

class Schematic(object):
    def __init__(self):
        self.deviceList = []
        self.project=None
    def InitFromProject(self,project):
        self.__init__()
        self.project=project
        deviceListProject=project.GetValue('Drawing.Schematic.Devices')
        for d in range(len(deviceListProject)):
            try:
                returnedDevice=DeviceFromProject(deviceListProject[d]).result
            except NameError: # part picture doesn't exist
                returnedDevice=None
            if not returnedDevice is None:
                self.deviceList.append(returnedDevice)
    # Legacy File Format
    def InitFromXml(self,schematicElement):
        self.__init__()
        self.wireList = WireList()
        for child in schematicElement:
            if child.tag == 'devices':
                for deviceElement in child:
                    try:
                        returnedDevice=DeviceXMLClassFactory(deviceElement).result
                    except NameError: # part picture doesn't exist
                        returnedDevice=None
                    if not returnedDevice is None:
                        # hack to fix port numbering of old four port transmission lines
                        from Device import DeviceTelegrapherFourPort
                        if isinstance(returnedDevice,DeviceTelegrapherFourPort):
                            if returnedDevice.partPicture.current.pinList[1].GetValue('Number')==3:
                                returnedDevice.partPicture.current.pinList[1].SetValue('Number',2)
                                returnedDevice.partPicture.current.pinList[2].SetValue('Number',3)
                        self.deviceList.append(returnedDevice)
            elif child.tag == 'wires':
                self.wireList.InitFromXml(child)
    def NetList(self):
        self.Consolidate()
        return NetList(self)
    def InputWaveforms(self):
        inputWaveformList=[]
        for device in self.deviceList:
            wf = device.Waveform()
            if not wf is None:
                inputWaveformList.append(wf)
        return inputWaveformList
    def Clear(self):
        self.deviceList = []
        if not self.project is None:
            from ProjectFile import XMLProperty
            self.project.SetValue('Drawing.Schematic.Wires',XMLProperty('Wires',[]))
    def NewUniqueReferenceDesignator(self,defaultDesignator):
        if defaultDesignator != None and '?' in defaultDesignator:
            referenceDesignatorList=[]
            for device in self.deviceList:
                deviceReferenceDesignatorProperty = device['ref']
                if deviceReferenceDesignatorProperty != None:
                    deviceReferenceDesignator = deviceReferenceDesignatorProperty.GetValue()
                    if deviceReferenceDesignator != None:
                        referenceDesignatorList.append(deviceReferenceDesignator)
            num = 1
            while defaultDesignator.replace('?',str(num)) in referenceDesignatorList:
                num=num+1
            return defaultDesignator.replace('?',str(num))
        else:
            return None
    def DevicePinConnectedList(self):
        devicePinConnectedList=[]
        for thisDeviceIndex in range(len(self.deviceList)):
            thisDeviceConnectedList=[]
            for thisPinCoordinate in self.deviceList[thisDeviceIndex].partPicture.current.PinCoordinates():
                thisPinConnected=False
                for otherDeviceIndex in range(len(self.deviceList)):
                    if thisPinConnected:
                        break
                    if thisDeviceIndex != otherDeviceIndex:
                        if thisPinConnected:
                            break
                        for otherPinCoordinate in self.deviceList[otherDeviceIndex].partPicture.current.PinCoordinates():
                            if thisPinCoordinate == otherPinCoordinate:
                                thisPinConnected=True
                                break
                if not thisPinConnected:
                    for wire in self.project.GetValue('Drawing.Schematic.Wires'):
                        if thisPinConnected:
                            break
                        for vertex in wire.GetValue('Vertex'):
                            if thisPinCoordinate == eval(vertex.GetValue('Coord')):
                                thisPinConnected=True
                                break
                thisDeviceConnectedList.append(thisPinConnected)
            devicePinConnectedList.append(thisDeviceConnectedList)
        return devicePinConnectedList
    def Consolidate(self):
        from ProjectFile import WireConfiguration,XMLPropertyDefaultString
        if self.project is None:
            return
        wireList = WireList().InitFromProject(self.project.GetValue('Drawing.Schematic.Wires'))
        wireList.ConsolidateWires(self)
        self.project.SetValue('Drawing.Schematic.Wires',[WireConfiguration() for _ in range(len(wireList))])
        from ProjectFile import VertexConfiguration
        for w in range(len(self.project.GetValue('Drawing.Schematic.Wires'))):
            wireProject=self.project.GetValue('Drawing.Schematic.Wires')[w]
            wire=wireList[w]
            wireProject.SetValue('Vertex',[VertexConfiguration() for vertex in wire])
            for v in range(len(wireProject.GetValue('Vertex'))):
                vertexProject=wireProject.GetValue('Vertex')[v]
                vertex=wire[v]
                vertexProject.SetValue('Coord',vertex.coord)
                vertexProject.SetValue('Selected',vertex.selected)

    def DotList(self):
        dotList=[]
        if self.project is None:
            return dotList
        # make a list of all coordinates
        coordList=[]
        for device in self.deviceList:
            coordList=coordList+device.PinCoordinates()
        wireListProject = self.project.GetValue('Drawing.Schematic.Wires')
        for wireProject in wireListProject:
            vertexCoordinates=[eval(vertexProject.GetValue('Coord')) for vertexProject in wireProject.GetValue('Vertex')]
            #vertex coordinates count as two except for the endpoints
            coordList=coordList+vertexCoordinates+vertexCoordinates[1:-1]
        uniqueCoordList=list(set(coordList))
        for coord in uniqueCoordList:
            if coordList.count(coord)>2:
                dotList.append(coord)
        return dotList

class DrawingStateMachine(object):
    def __init__(self,parent):
        self.parent=parent
        self.NoProject()
    def UnselectAllDevices(self):
        for device in self.parent.schematic.deviceList:
            device.selected=False
    def UnselectAllWires(self):
        if self.parent.schematic.project is None:
            return
        for wireProject in self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'):
            for vertexProject in wireProject.GetValue('Vertex'):
                vertexProject.SetValue('Selected',False)
    def SaveButton1Coordinates(self,event):
        self.parent.Button1Coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.Button1Augmentor=self.parent.AugmentorToGridCoordinate(event.x,event.y)
    def SaveButton2Coordinates(self,event):
        self.parent.Button2Coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.Button2Augmentor=self.parent.AugmentorToGridCoordinate(event.x,event.y)
    def DispatchBasedOnSelections(self,nothingSelectedState=None):
        AtLeastOneDeviceSelected=False
        AtLeastOneVertexSelected=False
        MultipleThingsSelected=False
        for d in range(len(self.parent.schematic.deviceList)):
            device=self.parent.schematic.deviceList[d]
            if device.selected:
                if AtLeastOneDeviceSelected:
                    MultipleThingsSelected = True
                else:
                    AtLeastOneDeviceSelected=True
                    self.parent.deviceSelected = device
                    self.parent.deviceSelectedIndex = d
                    self.parent.coordInPart = device.WhereInPart(self.parent.Button1Coord)
        for w in range(len(self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'))):
            for v in range(len(self.parent.schematic.project.GetValue('Drawing.Schematic.Wires')[w].GetValue('Vertex'))):
                if self.parent.schematic.project.GetValue('Drawing.Schematic.Wires')[w].GetValue('Vertex')[v].GetValue('Selected'):
                    if AtLeastOneVertexSelected:
                        MultipleThingsSelected=True
                    else:
                        AtLeastOneVertexSelected=True
                        self.parent.w = w
                        self.parent.v = v

        if AtLeastOneDeviceSelected and AtLeastOneVertexSelected:
            MultipleThingsSelected=True
        if MultipleThingsSelected:
            self.MultipleSelections()
        elif AtLeastOneDeviceSelected:
            self.DeviceSelected()
        elif AtLeastOneVertexSelected:
            self.WireSelected()
        else:
            if nothingSelectedState == None:
                self.Nothing()
            else:
                nothingSelectedState()
    def onMouseButton1TryToSelectSomething(self,event):
        self.Nothing()
        self.SaveButton1Coordinates(event)
        selectedSomething=False
        for device in self.parent.schematic.deviceList:
            if device.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.1):
                selectedSomething=True
                device.selected=True
        for wire in self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'):
            for vertex in wire.GetValue('Vertex'):
                if Vertex(eval(vertex.GetValue('Coord')),vertex.GetValue('Selected')).IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.2):
                    selectedSomething=True
                    vertex.SetValue('Selected',True)
        if not selectedSomething:
            for wireIndex in range(len(self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'))):
                wireProject=self.parent.schematic.project.GetValue('Drawing.Schematic.Wires')[wireIndex]
                segmentList=SegmentList(Wire().InitFromProject(wireProject))
                for segment in segmentList:
                    if segment.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.2):
                        segment.selected=True
                        selectedSomething=True
                        break
                if selectedSomething:
                    wire = segmentList.Wire()
                    from ProjectFile import VertexConfiguration
                    wireProject.SetValue('Vertex',[VertexConfiguration() for vertex in wire])
                    for v in range(len(wireProject.GetValue('Vertex'))):
                        vertexProject=wireProject.GetValue('Vertex')[v]
                        vertex=wire[v]
                        vertexProject.SetValue('Coord',vertex.coord)
                        vertexProject.SetValue('Selected',vertex.selected)
                    break
        self.DispatchBasedOnSelections(self.Selecting)
    def onMouseButton1TryToToggleSomething(self,event):
        self.SaveButton1Coordinates(event)
        toggledSomething=False
        for device in self.parent.schematic.deviceList:
            if device.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.1):
                device.selected=not device.selected
                toggledSomething=True
        for wireProject in self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'):
            for vertexProject in wireProject.GetValue('Vertex'):
                if Vertex(eval(vertexProject.GetValue('Coord')),vertexProject.GetValue('Selected')).IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.2):
                    vertexProject.SetValue('Selected',not vertexProject.GetValue('Selected'))
                    toggledSomething=True
        if not toggledSomething:
            for wireProject in self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'):
                segmentList=SegmentList(Wire().InitFromProject(wireProject))
                for segment in segmentList:
                    if segment.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.2):
                        segment.selected=not segment.selected
                        toggledSomething=True
                        break
                if toggledSomething:
                    wire = segmentList.Wire()
                    from ProjectFile import VertexConfiguration
                    wireProject.SetValue('Vertex',[VertexConfiguration() for vertex in wire])
                    for v in range(len(wireProject.GetValue('Vertex'))):
                        vertexProject=wireProject.GetValue('Vertex')[v]
                        vertex=wire[v]
                        vertexProject.SetValue('Coord',vertex.coord)
                        vertexProject.SetValue('Selected',vertex.selected)
                    break
        if toggledSomething:
            self.parent.DrawSchematic()
            self.DispatchBasedOnSelections()
            return

        self.selectedDevices = [device.selected for device in self.parent.schematic.deviceList]
        self.SelectingMore()

    def NoProject(self,force=False):
        if not hasattr(self,'state'):
            self.state=''
        if self.state != 'NoProject' or force:
            self.parent.schematic.project=None
            self.parent.canvas.config(cursor='left_ptr')
            self.state='NoProject'
            self.parent.schematic.Consolidate()
            self.UnselectAllDevices()
            self.UnselectAllWires()
            Doer.inHelp = False
            self.parent.canvas.bind('<Button-1>',self.onMouseButton1_NoProject)
            self.parent.canvas.bind('<Control-Button-1>',self.onCtrlMouseButton1_NoProject)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onCtrlMouseButton1Motion_NoProject)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onCtrlMouseButton1Release_NoProject)
            self.parent.canvas.bind('<Button-3>',self.onMouseButton3_NoProject)
            self.parent.canvas.bind('<B1-Motion>',self.onMouseButton1Motion_NoProject)
            self.parent.canvas.bind('<ButtonRelease-1>',self.onMouseButton1Release_NoProject)
            self.parent.canvas.bind('<ButtonRelease-3>',self.onMouseButton3Release_NoProject)
            self.parent.canvas.bind('<Double-Button-1>',self.onMouseButton1Double_NoProject)
            self.parent.canvas.bind('<Motion>',self.onMouseMotion_NoProject)
            self.parent.parent.NewProjectDoer.Activate(True)
            self.parent.parent.OpenProjectDoer.Activate(True)
            self.parent.parent.SaveProjectDoer.Activate(False)
            self.parent.parent.SaveAsProjectDoer.Activate(False)
            self.parent.parent.ClearProjectDoer.Activate(False)
            self.parent.parent.ExportNetListDoer.Activate(False)
            self.parent.parent.ExportTpXDoer.Activate(False)
            self.parent.parent.UndoDoer.Activate(False)
            self.parent.parent.RedoDoer.Activate(False)
            self.parent.parent.DeleteSelectedDoer.Activate(False)
            self.parent.parent.DuplicateSelectedDoer.Activate(False)
            self.parent.parent.CutSelectedDoer.Activate(False)
            self.parent.parent.AddPartDoer.Activate(False)
            self.parent.parent.AddPortDoer.Activate(False)
            self.parent.parent.AddMeasureProbeDoer.Activate(False)
            self.parent.parent.AddOutputProbeDoer.Activate(False)
            self.parent.parent.AddStimDoer.Activate(False)
            self.parent.parent.AddUnknownDoer.Activate(False)
            self.parent.parent.AddSystemDoer.Activate(False)
            self.parent.parent.DeletePartDoer.Activate(False)
            self.parent.parent.EditPropertiesDoer.Activate(False)
            self.parent.parent.DuplicatePartDoer.Activate(False)
            self.parent.parent.RotatePartDoer.Activate(False)
            self.parent.parent.FlipPartHorizontallyDoer.Activate(False)
            self.parent.parent.FlipPartVerticallyDoer.Activate(False)
            self.parent.parent.AddWireDoer.Activate(False)
            self.parent.parent.DeleteVertexDoer.Activate(False)
            self.parent.parent.DuplicateVertexDoer.Activate(False)
            self.parent.parent.DeleteWireDoer.Activate(False)
            self.parent.parent.ZoomInDoer.Activate(False)
            self.parent.parent.ZoomOutDoer.Activate(False)
            self.parent.parent.PanDoer.Activate(False)
            self.parent.parent.CalculationPropertiesDoer.Activate(False)
            self.parent.parent.SParameterViewerDoer.Activate(True)
            self.parent.parent.CalculateDoer.Activate(False)
            self.parent.parent.CalculateSParametersDoer.Activate(False)
            self.parent.parent.SimulateDoer.Activate(False)
            self.parent.parent.VirtualProbeDoer.Activate(False)
            self.parent.parent.DeembedDoer.Activate(False)
            self.parent.parent.HelpDoer.Activate(True)
            self.parent.parent.ControlHelpDoer.Activate(True)
            self.parent.parent.EscapeDoer.Activate(True)
            self.parent.parent.statusbar.set('No Project')
            self.parent.DrawSchematic()

    def onMouseButton1_NoProject(self,event):
        pass
    def onCtrlMouseButton1_NoProject(self,event):
        pass
    def onCtrlMouseButton1Motion_NoProject(self,event):
        pass
    def onCtrlMouseButton1Release_NoProject(self,event):
        pass
    def onMouseButton3_NoProject(self,event):
        pass
    def onMouseButton1Motion_NoProject(self,event):
        pass
    def onMouseButton1Release_NoProject(self,event):
        pass
    def onMouseButton3Release_NoProject(self,event):
        self.parent.tk.call('tk_popup',self.parent.canvasTearOffMenu, event.x_root, event.y_root)
    def onMouseButton1Double_NoProject(self,event):
        pass
    def onMouseMotion_NoProject(self,event):
        pass

    def Nothing(self,force=False):
        if not hasattr(self,'state'):
            self.state=''
        if self.state != 'Nothing' or force:
            self.parent.canvas.config(cursor='left_ptr')
            self.state='Nothing'
            self.parent.schematic.Consolidate()
            self.UnselectAllDevices()
            self.UnselectAllWires()
            Doer.inHelp = False
            self.parent.parent.config(cursor='left_ptr')
            self.parent.canvas.bind('<Button-1>',self.onMouseButton1_Nothing)
            self.parent.canvas.bind('<Control-Button-1>',self.onCtrlMouseButton1_Nothing)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onCtrlMouseButton1Motion_Nothing)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onCtrlMouseButton1Release_Nothing)
            self.parent.canvas.bind('<Button-3>',self.onMouseButton3_Nothing)
            self.parent.canvas.bind('<B1-Motion>',self.onMouseButton1Motion_Nothing)
            self.parent.canvas.bind('<ButtonRelease-1>',self.onMouseButton1Release_Nothing)
            self.parent.canvas.bind('<ButtonRelease-3>',self.onMouseButton3Release_Nothing)
            self.parent.canvas.bind('<Double-Button-1>',self.onMouseButton1Double_Nothing)
            self.parent.canvas.bind('<Motion>',self.onMouseMotion_Nothing)
            self.parent.parent.NewProjectDoer.Activate(True)
            self.parent.parent.OpenProjectDoer.Activate(True)
            self.parent.parent.SaveProjectDoer.Activate(True)
            self.parent.parent.SaveAsProjectDoer.Activate(True)
            self.parent.parent.ClearProjectDoer.Activate(True)
            self.parent.parent.ExportNetListDoer.Activate(True)
            self.parent.parent.ExportTpXDoer.Activate(True)
            #self.parent.parent.UndoDoer.Activate(False)
            #self.parent.parent.RedoDoer.Activate(False)
            self.parent.parent.DeleteSelectedDoer.Activate(False)
            self.parent.parent.DuplicateSelectedDoer.Activate(False)
            self.parent.parent.CutSelectedDoer.Activate(False)
            self.parent.parent.AddPartDoer.Activate(True)
            self.parent.parent.AddPortDoer.Activate(True)
            self.parent.parent.AddMeasureProbeDoer.Activate(True)
            self.parent.parent.AddOutputProbeDoer.Activate(True)
            self.parent.parent.AddStimDoer.Activate(True)
            self.parent.parent.AddUnknownDoer.Activate(True)
            self.parent.parent.AddSystemDoer.Activate(True)
            self.parent.parent.DeletePartDoer.Activate(False)
            self.parent.parent.EditPropertiesDoer.Activate(False)
            self.parent.parent.DuplicatePartDoer.Activate(False)
            self.parent.parent.RotatePartDoer.Activate(False)
            self.parent.parent.FlipPartHorizontallyDoer.Activate(False)
            self.parent.parent.FlipPartVerticallyDoer.Activate(False)
            self.parent.parent.AddWireDoer.Activate(True)
            self.parent.parent.DeleteVertexDoer.Activate(False)
            self.parent.parent.DuplicateVertexDoer.Activate(False)
            self.parent.parent.DeleteWireDoer.Activate(False)
            self.parent.parent.ZoomInDoer.Activate(True)
            self.parent.parent.ZoomOutDoer.Activate(True)
            self.parent.parent.PanDoer.Activate(True)
            self.parent.parent.CalculationPropertiesDoer.Activate(True)
            self.parent.parent.SParameterViewerDoer.Activate(True)
            #self.parent.parent.CalculateDoer.Activate(False)
            #self.parent.parent.CalculateSParametersDoer.Activate(False)
            #self.parent.parent.SimulateDoer.Activate(False)
            #self.parent.parent.VirtualProbeDoer.Activate(False)
            #self.parent.parent.DeembedDoer.Activate(False)
            self.parent.parent.HelpDoer.Activate(True)
            self.parent.parent.ControlHelpDoer.Activate(True)
            self.parent.parent.EscapeDoer.Activate(False)
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=RAISED)
            self.parent.parent.statusbar.clear()
            self.parent.DrawSchematic()
    def onMouseButton1_Nothing(self,event):
        self.onMouseButton1TryToSelectSomething(event)
    def onCtrlMouseButton1_Nothing(self,event):
        self.onMouseButton1_Nothing(event)
    def onCtrlMouseButton1Motion_Nothing(self,event):
        pass
    def onCtrlMouseButton1Release_Nothing(self,event):
        pass
    def onMouseButton3_Nothing(self,event):
        pass
    def onMouseButton1Motion_Nothing(self,event):
        pass
    def onMouseButton1Release_Nothing(self,event):
        pass
    def onMouseButton3Release_Nothing(self,event):
        self.parent.tk.call('tk_popup',self.parent.canvasTearOffMenu, event.x_root, event.y_root)
    def onMouseButton1Double_Nothing(self,event):
        pass
    def onMouseMotion_Nothing(self,event):
        pass

    def DeviceSelected(self,force=False):
        if self.state != 'DeviceSelected' or force:
            self.state='DeviceSelected'
            for d in range(len(self.parent.schematic.deviceList)):
                device=self.parent.schematic.deviceList[d]
                if device.selected:
                    self.parent.deviceSelected = device
                    self.parent.deviceSelectedIndex = d
                    self.parent.coordInPart = device.WhereInPart(self.parent.Button1Coord)
            self.parent.canvas.config(cursor='left_ptr')
            self.parent.canvas.bind('<Button-1>',self.onMouseButton1_DeviceSelected)
            self.parent.canvas.bind('<Control-Button-1>',self.onCtrlMouseButton1_DeviceSelected)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onCtrlMouseButton1Motion_DeviceSelected)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onCtrlMouseButton1Release_DeviceSelected)
            self.parent.canvas.bind('<Button-3>',self.onMouseButton3_DeviceSelected)
            self.parent.canvas.bind('<B1-Motion>',self.onMouseButton1Motion_DeviceSelected)
            self.parent.canvas.bind('<ButtonRelease-1>',self.onMouseButton1Release_DeviceSelected)
            self.parent.canvas.bind('<ButtonRelease-3>',self.onMouseButton3Release_DeviceSelected)
            self.parent.canvas.bind('<Double-Button-1>',self.onMouseButton1Double_DeviceSelected)
            self.parent.canvas.bind('<Motion>',self.onMouseMotion_DeviceSelected)
            self.parent.parent.RotatePartDoer.Activate(True)
            self.parent.parent.FlipPartHorizontallyDoer.Activate(True)
            self.parent.parent.FlipPartVerticallyDoer.Activate(True)
            self.parent.parent.DeletePartDoer.Activate(True)
            self.parent.parent.DeleteSelectedDoer.Activate(True)
            self.parent.parent.EditPropertiesDoer.Activate(True)
            self.parent.parent.DuplicatePartDoer.Activate(True)
            self.parent.parent.DuplicateSelectedDoer.Activate(True)
            self.parent.parent.CutSelectedDoer.Activate(True)
            self.parent.parent.DeleteVertexDoer.Activate(False)
            self.parent.parent.DuplicateVertexDoer.Activate(False)
            self.parent.parent.DeleteWireDoer.Activate(False)
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=RAISED)
            self.parent.parent.statusbar.set('Part Selected')
            self.parent.DrawSchematic()
    def onMouseButton1_DeviceSelected(self,event):
        self.onMouseButton1TryToSelectSomething(event)
    def onCtrlMouseButton1_DeviceSelected(self,event):
        self.onMouseButton1TryToToggleSomething(event)
    def onCtrlMouseButton1Motion_DeviceSelected(self,event):
        pass
    def onCtrlMouseButton1Release_DeviceSelected(self,event):
        self.parent.schematic.Consolidate()
        self.parent.DrawSchematic()
    def onMouseButton3_DeviceSelected(self,event):
        self.SaveButton2Coordinates(event)
        if not self.parent.deviceSelected.IsAt(self.parent.Button2Coord,self.parent.Button2Augmentor,0.1):
            self.Nothing()
    def onMouseButton1Motion_DeviceSelected(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.deviceSelected.partPicture.current.SetOrigin([coord[0]-self.parent.coordInPart[0],coord[1]-self.parent.coordInPart[1]])
        self.parent.DrawSchematic()
    def onMouseButton1Release_DeviceSelected(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.deviceSelected.partPicture.current.SetOrigin([coord[0]-self.parent.coordInPart[0],coord[1]-self.parent.coordInPart[1]])
        self.parent.schematic.Consolidate()
        self.parent.parent.history.Event('release selected device')
        self.parent.DrawSchematic()
    def onMouseButton3Release_DeviceSelected(self,event):
        self.parent.tk.call("tk_popup", self.parent.deviceTearOffMenu, event.x_root, event.y_root)
    def onMouseButton1Double_DeviceSelected(self,event):
        self.parent.EditSelectedDevice()
    def onMouseMotion_DeviceSelected(self,event):
        pass

    def WireSelected(self,force=False):
        if self.state != 'WireSelected' or force:
            self.state='WireSelected'
            wireListProject=self.parent.schematic.project.GetValue('Drawing.Schematic.Wires')
            for w in range(len(wireListProject)):
                wireProject=wireListProject[w]
                for v in range(len(wireProject.GetValue('Vertex'))):
                    vertexProject=wireProject.GetValue('Vertex')[v]
                    if vertexProject.GetValue('Selected'):
                        self.parent.w = w
                        self.parent.v = v
            self.parent.canvas.config(cursor='left_ptr')
            self.parent.canvas.bind('<Button-1>',self.onMouseButton1_WireSelected)
            self.parent.canvas.bind('<Control-Button-1>',self.onCtrlMouseButton1_WireSelected)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onCtrlMouseButton1Motion_WireSelected)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onCtrlMouseButton1Release_WireSelected)
            self.parent.canvas.bind('<Button-3>',self.onMouseButton3_WireSelected)
            self.parent.canvas.bind('<B1-Motion>',self.onMouseButton1Motion_WireSelected)
            self.parent.canvas.bind('<ButtonRelease-1>',self.onMouseButton1Release_WireSelected)
            self.parent.canvas.bind('<ButtonRelease-3>',self.onMouseButton3Release_WireSelected)
            self.parent.canvas.bind('<Double-Button-1>',self.onMouseButton1Double_WireSelected)
            self.parent.canvas.bind('<Motion>',self.onMouseMotion_WireSelected)
            self.parent.parent.RotatePartDoer.Activate(False)
            self.parent.parent.FlipPartHorizontallyDoer.Activate(False)
            self.parent.parent.FlipPartVerticallyDoer.Activate(False)
            self.parent.parent.DeletePartDoer.Activate(False)
            self.parent.parent.DeleteSelectedDoer.Activate(False)
            self.parent.parent.EditPropertiesDoer.Activate(False)
            self.parent.parent.DuplicatePartDoer.Activate(False)
            self.parent.parent.DuplicateSelectedDoer.Activate(False)
            self.parent.parent.CutSelectedDoer.Activate(False)
            self.parent.parent.DeleteVertexDoer.Activate(True)
            self.parent.parent.DuplicateVertexDoer.Activate(True)
            self.parent.parent.DeleteWireDoer.Activate(True)
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=RAISED)
            self.parent.parent.statusbar.set('Wire Selected')
            self.parent.DrawSchematic()
    def onMouseButton1_WireSelected(self,event):
        self.onMouseButton1TryToSelectSomething(event)
    def onCtrlMouseButton1_WireSelected(self,event):
        self.onMouseButton1TryToToggleSomething(event)
    def onCtrlMouseButton1Motion_WireSelected(self,event):
        pass
    def onCtrlMouseButton1Release_WireSelected(self,event):
        pass
    def onMouseButton3_WireSelected(self,event):
        pass
    def onMouseButton1Motion_WireSelected(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.schematic.project.GetValue('Drawing.Schematic.Wires')[self.parent.w].GetValue('Vertex')[self.parent.v].SetValue('Coord',coord)
        self.parent.DrawSchematic()
    def onMouseButton1Release_WireSelected(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.schematic.project.GetValue('Drawing.Schematic.Wires')[self.parent.w].GetValue('Vertex')[self.parent.v].SetValue('Coord',coord)
        self.parent.schematic.Consolidate()
        self.parent.parent.history.Event('release selected wire')
        self.parent.DrawSchematic()
    def onMouseButton3Release_WireSelected(self,event):
        self.parent.tk.call('tk_popup',self.parent.wireTearOffMenu, event.x_root, event.y_root)
    def onMouseButton1Double_WireSelected(self,event):
        pass
    def onMouseMotion_WireSelected(self,event):
        pass

    def PartLoaded(self,force=False):
        if self.state!='PartLoaded' or force:
            self.parent.canvas.config(cursor='hand2')
            self.UnselectAllDevices()
            self.UnselectAllWires()
            self.state='PartLoaded'
            self.parent.canvas.bind('<Button-1>',self.onMouseButton1_PartLoaded)
            self.parent.canvas.bind('<Control-Button-1>',self.onCtrlMouseButton1_PartLoaded)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onCtrlMouseButton1Motion_PartLoaded)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onCtrlMouseButton1Release_PartLoaded)
            self.parent.canvas.bind('<Button-3>',self.onMouseButton3_PartLoaded)
            self.parent.canvas.bind('<B1-Motion>',self.onMouseButton1Motion_PartLoaded)
            self.parent.canvas.bind('<ButtonRelease-1>',self.onMouseButton1Release_PartLoaded)
            self.parent.canvas.bind('<ButtonRelease-3>',self.onMouseButton3Release_PartLoaded)
            self.parent.canvas.bind('<Double-Button-1>',self.onMouseButton1Double_PartLoaded)
            self.parent.canvas.bind('<Motion>',self.onMouseMotion_PartLoaded)
            self.parent.parent.RotatePartDoer.Activate(False)
            self.parent.parent.FlipPartHorizontallyDoer.Activate(False)
            self.parent.parent.FlipPartVerticallyDoer.Activate(False)
            self.parent.parent.DeletePartDoer.Activate(False)
            self.parent.parent.DeleteSelectedDoer.Activate(True)
            self.parent.parent.EditPropertiesDoer.Activate(False)
            self.parent.parent.DuplicatePartDoer.Activate(False)
            self.parent.parent.DuplicateSelectedDoer.Activate(False)
            self.parent.parent.CutSelectedDoer.Activate(False)
            self.parent.parent.DeleteVertexDoer.Activate(False)
            self.parent.parent.DuplicateVertexDoer.Activate(False)
            self.parent.parent.DeleteWireDoer.Activate(False)
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=RAISED)
            self.parent.parent.statusbar.set('Part In Clipboard')
            self.parent.DrawSchematic()
    def onMouseButton1_PartLoaded(self,event):
        self.SaveButton1Coordinates(event)
        self.parent.partLoaded.partPicture.current.SetOrigin(self.parent.Button1Coord)
        self.parent.schematic.deviceList.append(self.parent.partLoaded)
        self.parent.schematic.deviceList[-1].selected=True
        self.DeviceSelected()
        self.parent.parent.history.Event('part added')
    def onCtrlMouseButton1_PartLoaded(self,event):
        pass
    def onCtrlMouseButton1Motion_PartLoaded(self,event):
        pass
    def onCtrlMouseButton1Release_PartLoaded(self,event):
        pass
    def onMouseButton3_PartLoaded(self,event):
        self.Nothing()
    def onMouseButton1Motion_PartLoaded(self,event):
        self.Nothing()
    def onMouseButton1Release_PartLoaded(self,event):
        self.Nothing()
    def onMouseButton3Release_PartLoaded(self,event):
        self.Nothing()
    def onMouseButton1Double_PartLoaded(self,event):
        self.Nothing()
    def onMouseMotion_PartLoaded(self,event):
        pass

    def WireLoaded(self,force=False):
        if self.state != 'WireLoaded' or force:
            self.state='WireLoaded'
            self.parent.canvas.config(cursor='pencil')
            self.UnselectAllDevices()
            self.UnselectAllWires()
            self.parent.canvas.bind('<Button-1>',self.onMouseButton1_WireLoaded)
            self.parent.canvas.bind('<Control-Button-1>',self.onCtrlMouseButton1_WireLoaded)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onCtrlMouseButton1Motion_WireLoaded)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onCtrlMouseButton1Release_WireLoaded)
            self.parent.canvas.bind('<Button-3>',self.onMouseButton3_WireLoaded)
            self.parent.canvas.bind('<B1-Motion>',self.onMouseButton1Motion_WireLoaded)
            self.parent.canvas.bind('<ButtonRelease-1>',self.onMouseButton1Release_WireLoaded)
            self.parent.canvas.bind('<ButtonRelease-3>',self.onMouseButton3Release_WireLoaded)
            self.parent.canvas.bind('<Double-Button-1>',self.onMouseButton1Double_WireLoaded)
            self.parent.canvas.bind('<Motion>',self.onMouseMotion_WireLoaded)
            self.parent.parent.RotatePartDoer.Activate(False)
            self.parent.parent.FlipPartHorizontallyDoer.Activate(False)
            self.parent.parent.FlipPartVerticallyDoer.Activate(False)
            self.parent.parent.DeletePartDoer.Activate(False)
            self.parent.parent.DeleteSelectedDoer.Activate(False)
            self.parent.parent.EditPropertiesDoer.Activate(False)
            self.parent.parent.DuplicatePartDoer.Activate(False)
            self.parent.parent.DuplicateSelectedDoer.Activate(False)
            self.parent.parent.CutSelectedDoer.Activate(False)
            self.parent.parent.DeleteVertexDoer.Activate(False)
            self.parent.parent.DuplicateVertexDoer.Activate(False)
            self.parent.parent.DeleteWireDoer.Activate(False)
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=RAISED)
            self.parent.parent.statusbar.set('Drawing Wires')
            self.parent.DrawSchematic()
    def onMouseButton1_WireLoaded(self,event):
        self.SaveButton1Coordinates(event)
        self.parent.wireLoaded.GetValue('Vertex')[-1].SetValue('Coord',self.parent.Button1Coord)
        self.parent.DrawSchematic()
    def onCtrlMouseButton1_WireLoaded(self,event):
        pass
    def onCtrlMouseButton1Motion_WireLoaded(self,event):
        pass
    def onCtrlMouseButton1Release_WireLoaded(self,event):
        pass
    def onMouseButton3_WireLoaded(self,event):
        pass
    def onMouseButton1Motion_WireLoaded(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        if len(self.parent.wireLoaded.GetValue('Vertex')) > 0:
            self.parent.wireLoaded.GetValue('Vertex')[-1].SetValue('Coord',coord)
            self.parent.DrawSchematic()
    def onMouseButton1Release_WireLoaded(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        from ProjectFile import VertexConfiguration
        vertexProject=VertexConfiguration()
        vertexProject.SetValue('Coord', coord)
        vertexProject.SetValue('Selected',False)
        self.parent.wireLoaded.GetValue('Vertex').append(vertexProject)
        self.parent.DrawSchematic()
    def onMouseButton3Release_WireLoaded(self,event):
        self.SaveButton2Coordinates(event)
        if len(self.parent.wireLoaded.GetValue('Vertex')) > 2:
            from ProjectFile import VertexConfiguration,WireConfiguration
            wireListProject=self.parent.schematic.project.GetValue('Drawing.Schematic.Wires')
            wireProject=WireConfiguration()
            wireProject.SetValue('Vertex',self.parent.wireLoaded.GetValue('Vertex')[:-1])
            wireListProject[-1]=wireProject
            vertexProject=VertexConfiguration()
            vertexProject.SetValue('Coord', (0,0))
            vertexProject.SetValue('Selected',False)
            wireProject=WireConfiguration()
            wireProject.SetValue('Vertex', [vertexProject])
            self.parent.wireLoaded=wireProject
            wireListProject.append(self.parent.wireLoaded)
            self.parent.parent.history.Event('add wire')
            self.parent.DrawSchematic()
        else:
            self.Nothing()
    def onMouseButton1Double_WireLoaded(self,event):
        self.parent.wireLoaded=None
        self.Nothing()
    def onMouseMotion_WireLoaded(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        freeFormWire=True
        if freeFormWire:
            self.parent.wireLoaded.GetValue('Vertex')[-1].SetValue('Coord',coord)
        else:
            if len(self.parent.wireLoaded) == 1:
                self.parent.wireLoaded[-1] = Vertex(coord)
            else:
                if abs(coord[0]-self.parent.wireLoaded[-2][0]) > abs(coord[1]-self.parent.wireLoaded[-2][1]):
                    self.parent.wireLoaded[-1] = Vertex((coord[0],self.parent.wireLoaded[-2][1]))
                else:
                    self.parent.wireLoaded[-1] = Vertex((self.parent.wireLoaded[-2][0],coord[1]))
        self.parent.DrawSchematic()

    def Panning(self,force=False):
        if self.state != 'Panning' or force:
            self.state='Panning'
            self.UnselectAllDevices()
            self.UnselectAllWires()
            self.parent.canvas.config(cursor='fleur')
            self.parent.canvas.bind('<Button-1>',self.onMouseButton1_Panning)
            self.parent.canvas.bind('<Control-Button-1>',self.onCtrlMouseButton1_Panning)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onCtrlMouseButton1Motion_Panning)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onCtrlMouseButton1Release_Panning)
            self.parent.canvas.bind('<Button-3>',self.onMouseButton3_Panning)
            self.parent.canvas.bind('<B1-Motion>',self.onMouseButton1Motion_Panning)
            self.parent.canvas.bind('<ButtonRelease-1>',self.onMouseButton1Release_Panning)
            self.parent.canvas.bind('<ButtonRelease-3>',self.onMouseButton3Release_Panning)
            self.parent.canvas.bind('<Double-Button-1>',self.onMouseButton1Double_Panning)
            self.parent.canvas.bind('<Motion>',self.onMouseMotion_Panning)
            self.parent.parent.RotatePartDoer.Activate(False)
            self.parent.parent.FlipPartHorizontallyDoer.Activate(False)
            self.parent.parent.FlipPartVerticallyDoer.Activate(False)
            self.parent.parent.DeletePartDoer.Activate(False)
            self.parent.parent.DeleteSelectedDoer.Activate(False)
            self.parent.parent.EditPropertiesDoer.Activate(False)
            self.parent.parent.DuplicatePartDoer.Activate(False)
            self.parent.parent.DuplicateSelectedDoer.Activate(False)
            self.parent.parent.CutSelectedDoer.Activate(False)
            self.parent.parent.DeleteVertexDoer.Activate(False)
            self.parent.parent.DuplicateVertexDoer.Activate(False)
            self.parent.parent.DeleteWireDoer.Activate(False)
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=SUNKEN)
            self.parent.parent.statusbar.set('Panning')
            self.parent.DrawSchematic()
    def onMouseButton1_Panning(self,event):
        self.SaveButton1Coordinates(event)
    def onCtrlMouseButton1_Panning(self,event):
        pass
    def onCtrlMouseButton1Motion_Panning(self,event):
        pass
    def onCtrlMouseButton1Release_Panning(self,event):
        pass
    def onMouseButton3_Panning(self,event):
        pass
    def onMouseButton1Motion_Panning(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.originx=self.parent.originx+coord[0]-self.parent.Button1Coord[0]
        self.parent.originy=self.parent.originy+coord[1]-self.parent.Button1Coord[1]
        self.parent.schematic.project.SetValue('Drawing.Originx',self.parent.originx)
        self.parent.schematic.project.SetValue('Drawing.Originy',self.parent.originy)
        self.parent.DrawSchematic()
    def onMouseButton1Release_Panning(self,event):
        self.Nothing()
    def onMouseButton3Release_Panning(self,event):
        self.Nothing()
    def onMouseButton1Double_Panning(self,event):
        self.Nothing()
    def onMouseMotion_Panning(self,event):
        pass

    def Selecting(self,force=False):
        if self.state != 'Selecting' or force:
            self.parent.canvas.config(cursor='left_ptr')
            self.state='Selecting'
            self.UnselectAllDevices()
            self.UnselectAllWires()
            self.parent.canvas.bind('<Button-1>',self.onMouseButton1_Selecting)
            self.parent.canvas.bind('<Control-Button-1>',self.onCtrlMouseButton1_Selecting)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onCtrlMouseButton1Motion_Selecting)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onCtrlMouseButton1Release_Selecting)
            self.parent.canvas.bind('<Button-3>',self.onMouseButton3_Selecting)
            self.parent.canvas.bind('<B1-Motion>',self.onMouseButton1Motion_Selecting)
            self.parent.canvas.bind('<ButtonRelease-1>',self.onMouseButton1Release_Selecting)
            self.parent.canvas.bind('<ButtonRelease-3>',self.onMouseButton3Release_Selecting)
            self.parent.canvas.bind('<Double-Button-1>',self.onMouseButton1Double_Selecting)
            self.parent.canvas.bind('<Motion>',self.onMouseMotion_Selecting)
            self.parent.parent.RotatePartDoer.Activate(False)
            self.parent.parent.FlipPartHorizontallyDoer.Activate(False)
            self.parent.parent.FlipPartVerticallyDoer.Activate(False)
            self.parent.parent.DeletePartDoer.Activate(False)
            self.parent.parent.DeleteSelectedDoer.Activate(False)
            self.parent.parent.EditPropertiesDoer.Activate(False)
            self.parent.parent.DuplicatePartDoer.Activate(False)
            self.parent.parent.DuplicateSelectedDoer.Activate(False)
            self.parent.parent.CutSelectedDoer.Activate(False)
            self.parent.parent.DeleteVertexDoer.Activate(False)
            self.parent.parent.DuplicateVertexDoer.Activate(False)
            self.parent.parent.DeleteWireDoer.Activate(False)
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=RAISED)
            self.parent.parent.statusbar.set('Selecting')
            self.parent.DrawSchematic()
    def onMouseButton1_Selecting(self,event):
        self.SaveButton1Coordinates(event)
    def onCtrlMouseButton1_Selecting(self,event):
        self.SaveButton1Coordinates(event)
    def onCtrlMouseButton1Motion_Selecting(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        coordAugmentor=self.parent.AugmentorToGridCoordinate(event.x,event.y)
        self.UnselectAllDevices()
        self.UnselectAllWires()
        for device in self.parent.schematic.deviceList:
            if device.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                device.selected=True
        for wireProject in self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'):
            for vertexProject in wireProject.GetValue('Vertex'):
                vertex=Vertex(eval(vertexProject.GetValue('Coord')),vertexProject.GetValue('Selected'))
                if vertex.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                    vertexProject.SetValue('Selected',True)
        self.parent.DrawSchematic()
        self.parent.canvas.create_rectangle((self.parent.Button1Coord[0]+self.parent.Button1Augmentor[0]+self.parent.originx)*self.parent.grid,
                                            (self.parent.Button1Coord[1]+self.parent.Button1Augmentor[1]+self.parent.originy)*self.parent.grid,
                                            (coord[0]+coordAugmentor[0]+self.parent.originx)*self.parent.grid,
                                            (coord[1]+coordAugmentor[1]+self.parent.originy)*self.parent.grid,
                                            dash=(1,5))
    def onCtrlMouseButton1Release_Selecting(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        coordAugmentor=self.parent.AugmentorToGridCoordinate(event.x,event.y)
        self.UnselectAllDevices()
        self.UnselectAllWires()
        for device in self.parent.schematic.deviceList:
            if device.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                device.selected=True
        for wireProject in self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'):
            for vertexProject in wireProject.GetValue('Vertex'):
                vertex=Vertex(eval(vertexProject.GetValue('Coord')),vertexProject.GetValue('Selected'))
                if vertex.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                    vertexProject.SetValue('Selected',True)
        self.DispatchBasedOnSelections()
    def onMouseButton3_Selecting(self,event):
        pass
    def onMouseButton1Motion_Selecting(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        coordAugmentor=self.parent.AugmentorToGridCoordinate(event.x,event.y)
        self.UnselectAllDevices()
        self.UnselectAllWires()
        for device in self.parent.schematic.deviceList:
            if device.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                device.selected=True
        for wireProject in self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'):
            for vertexProject in wireProject.GetValue('Vertex'):
                if Vertex(eval(vertexProject.GetValue('Coord')),vertexProject.GetValue('Selected')).IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                    vertexProject.SetValue('Selected',True)
        self.parent.DrawSchematic()
        self.parent.canvas.create_rectangle((self.parent.Button1Coord[0]+self.parent.Button1Augmentor[0]+self.parent.originx)*self.parent.grid,
                                            (self.parent.Button1Coord[1]+self.parent.Button1Augmentor[1]+self.parent.originy)*self.parent.grid,
                                            (coord[0]+coordAugmentor[0]+self.parent.originx)*self.parent.grid,
                                            (coord[1]+coordAugmentor[1]+self.parent.originy)*self.parent.grid,
                                            dash=(1,5))
    def onMouseButton1Release_Selecting(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        coordAugmentor=self.parent.AugmentorToGridCoordinate(event.x,event.y)
        self.UnselectAllDevices()
        self.UnselectAllWires()
        for device in self.parent.schematic.deviceList:
            if device.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                device.selected=True
        for wireProject in self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'):
            for vertexProject in wireProject.GetValue('Vertex'):
                if Vertex(eval(vertexProject.GetValue('Coord')),vertexProject.GetValue('Selected')).IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                    vertexProject.SetValue('Selected',True)
        self.DispatchBasedOnSelections()
    def onMouseButton3Release_Selecting(self,event):
        pass
    def onMouseButton1Double_Selecting(self,event):
        pass
    def onMouseMotion_Selecting(self,event):
        pass

    def MultipleSelections(self,force=False):
        if self.state != 'Multiple Selections' or force:
            self.state='Multiple Selections'
            self.parent.canvas.config(cursor='left_ptr')
            self.parent.OriginalDeviceCoordinates = [device.WhereInPart(self.parent.Button1Coord) for device in self.parent.schematic.deviceList]
            
            self.parent.OriginalWireCoordinates = [[(self.parent.Button1Coord[0]-eval(vertex.GetValue('Coord'))[0],
                                                     self.parent.Button1Coord[1]-eval(vertex.GetValue('Coord'))[1]) for vertex in wire.GetValue('Vertex')] for wire in self.parent.schematic.project.GetValue('Drawing.Schematic.Wires')]
            self.parent.canvas.bind('<Button-1>',self.onMouseButton1_MultipleSelections)
            self.parent.canvas.bind('<Control-Button-1>',self.onCtrlMouseButton1_MultipleSelections)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onCtrlMouseButton1Motion_MultipleSelections)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onCtrlMouseButton1Release_MultipleSelections)
            self.parent.canvas.bind('<Button-3>',self.onMouseButton3_MultipleSelections)
            self.parent.canvas.bind('<B1-Motion>',self.onMouseButton1Motion_MultipleSelections)
            self.parent.canvas.bind('<ButtonRelease-1>',self.onMouseButton1Release_MultipleSelections)
            self.parent.canvas.bind('<ButtonRelease-3>',self.onMouseButton3Release_MultipleSelections)
            self.parent.canvas.bind('<Double-Button-1>',self.onMouseButton1Double_MultipleSelections)
            self.parent.canvas.bind('<Motion>',self.onMouseMotion_MultipleSelections)
            self.parent.parent.RotatePartDoer.Activate(False)
            self.parent.parent.FlipPartHorizontallyDoer.Activate(False)
            self.parent.parent.FlipPartVerticallyDoer.Activate(False)
            self.parent.parent.DeletePartDoer.Activate(False)
            self.parent.parent.DeleteSelectedDoer.Activate(True)
            self.parent.parent.EditPropertiesDoer.Activate(False)
            self.parent.parent.DuplicatePartDoer.Activate(False)
            self.parent.parent.DuplicateSelectedDoer.Activate(True)
            self.parent.parent.CutSelectedDoer.Activate(True)
            self.parent.parent.DeleteVertexDoer.Activate(False)
            self.parent.parent.DuplicateVertexDoer.Activate(False)
            self.parent.parent.DeleteWireDoer.Activate(False)
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=RAISED)
            self.parent.parent.statusbar.set('Multiple Selections')
            self.parent.DrawSchematic()
    def onMouseButton1_MultipleSelections(self,event):
        self.SaveButton1Coordinates(event)
        self.parent.OriginalDeviceCoordinates = [device.WhereInPart(self.parent.Button1Coord) for device in self.parent.schematic.deviceList]
        self.parent.OriginalWireCoordinates = [[(self.parent.Button1Coord[0]-eval(vertexProject.GetValue('Coord'))[0],
                                                     self.parent.Button1Coord[1]-eval(vertexProject.GetValue('Coord'))[1]) 
                                                        for vertexProject in wireProject.GetValue('Vertex')]
                                                            for wireProject in self.parent.schematic.project.GetValue('Drawing.Schematic.Wires')]
        inSelection=False
        for device in self.parent.schematic.deviceList:
            if device.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.1) and device.selected:
                inSelection=True
                break
        
        for wireProject in self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'):
            for vertexProject in wireProject.GetValue('Vertex'):
                if Vertex(eval(vertexProject.GetValue('Coord')),vertexProject.GetValue('Selected')).IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.2) and vertexProject.GetValue('Selected'):
                    inSelection=True
                    break
        if not inSelection:
            for wireProject in self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'):
                wire=Wire().InitFromProject(wireProject)
                segmentList=SegmentList(wire)
                for segment in segmentList:
                    if segment.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.2) and segment.selected:
                        inSelection=True
                        break
                if inSelection:
                    break

        if not inSelection:
            self.onMouseButton1TryToSelectSomething(event)
    def onCtrlMouseButton1_MultipleSelections(self,event):
        self.onMouseButton1TryToToggleSomething(event)
    def onCtrlMouseButton1Motion_MultipleSelections(self,event):
        pass
    def onCtrlMouseButton1Release_MultipleSelections(self,event):
        self.MultipleSelections()
    def onMouseButton3_MultipleSelections(self,event):
        self.parent.tk.call('tk_popup',self.parent.multipleSelectionsTearOffMenu, event.x_root, event.y_root)
    def onMouseButton1Motion_MultipleSelections(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        for d in range(len(self.parent.schematic.deviceList)):
            device=self.parent.schematic.deviceList[d]
            coordInPart = self.parent.OriginalDeviceCoordinates[d]
            if device.selected:
                device.partPicture.current.SetOrigin([coord[0]-coordInPart[0],coord[1]-coordInPart[1]])
        for w in range(len(self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'))):
            wireProject=self.parent.schematic.project.GetValue('Drawing.Schematic.Wires')[w]
            for v in range(len(wireProject.GetValue('Vertex'))):
                vertexProject=wireProject.GetValue('Vertex')[v]
                if vertexProject.GetValue('Selected'):
                    vertexProject.SetValue('Coord',(coord[0]-self.parent.OriginalWireCoordinates[w][v][0],
                                                          coord[1]-self.parent.OriginalWireCoordinates[w][v][1]))
        self.parent.DrawSchematic()
    def onMouseButton1Release_MultipleSelections(self,event):
        self.parent.schematic.Consolidate()
        self.parent.DrawSchematic()
        self.parent.parent.history.Event('release multiple selections')

    def onMouseButton3Release_MultipleSelections(self,event):
        pass
    def onMouseButton1Double_MultipleSelections(self,event):
        pass
    def onMouseMotion_MultipleSelections(self,event):
        pass

    def SelectingMore(self,force=False):
        if self.state != 'Selecting More' or force:
            self.state='Selecting More'
            self.parent.canvas.config(cursor='left_ptr')
            self.parent.canvas.bind('<Button-1>',self.onMouseButton1_SelectingMore)
            self.parent.canvas.bind('<Control-Button-1>',self.onCtrlMouseButton1_SelectingMore)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onCtrlMouseButton1Motion_SelectingMore)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onCtrlMouseButton1Release_SelectingMore)
            self.parent.canvas.bind('<Button-3>',self.onMouseButton3_SelectingMore)
            self.parent.canvas.bind('<B1-Motion>',self.onMouseButton1Motion_SelectingMore)
            self.parent.canvas.bind('<ButtonRelease-1>',self.onMouseButton1Release_SelectingMore)
            self.parent.canvas.bind('<ButtonRelease-3>',self.onMouseButton3Release_SelectingMore)
            self.parent.canvas.bind('<Double-Button-1>',self.onMouseButton1Double_SelectingMore)
            self.parent.canvas.bind('<Motion>',self.onMouseMotion_SelectingMore)
            self.parent.parent.RotatePartDoer.Activate(False)
            self.parent.parent.FlipPartHorizontallyDoer.Activate(False)
            self.parent.parent.FlipPartVerticallyDoer.Activate(False)
            self.parent.parent.DeletePartDoer.Activate(False)
            self.parent.parent.DeleteSelectedDoer.Activate(False)
            self.parent.parent.EditPropertiesDoer.Activate(False)
            self.parent.parent.DuplicatePartDoer.Activate(False)
            self.parent.parent.DuplicateSelectedDoer.Activate(False)
            self.parent.parent.CutSelectedDoer.Activate(False)
            self.parent.parent.DeleteVertexDoer.Activate(False)
            self.parent.parent.DuplicateVertexDoer.Activate(False)
            self.parent.parent.DeleteWireDoer.Activate(False)
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=RAISED)
            self.parent.parent.statusbar.set('Selecting More')
            self.parent.DrawSchematic()
    def onMouseButton1_SelectingMore(self,event):
        self.SaveButton1Coordinates(event)
    def onCtrlMouseButton1_SelectingMore(self,event):
        self.SaveButton1Coordinates(event)
    def onCtrlMouseButton1Motion_SelectingMore(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        coordAugmentor=self.parent.AugmentorToGridCoordinate(event.x,event.y)
        oldWireListProject=copy.deepcopy(self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'))
        self.UnselectAllDevices()
        self.UnselectAllWires()
        for d in range(len(self.parent.schematic.deviceList)):
            device=self.parent.schematic.deviceList[d]
            if device.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor) or self.selectedDevices[d]:
                device.selected=True
        wireListProject=self.parent.schematic.project.GetValue('Drawing.Schematic.Wires')
        for w in range(len(wireListProject)):
            wireProject=wireListProject[w].GetValue('Vertex')
            for v in range(len(wireProject)):
                vertexProject=wireProject[v]
                vertex=Vertex(eval(vertexProject.GetValue('Coord')),vertexProject.GetValue('Selected'))
                if vertex.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor) or\
                 oldWireListProject[w].GetValue('Vertex')[v].GetValue('Selected'):
                    vertexProject.SetValue('Selected',True)
        self.parent.DrawSchematic()
        self.parent.canvas.create_rectangle((self.parent.Button1Coord[0]+self.parent.originx)*self.parent.grid,
                                            (self.parent.Button1Coord[1]+self.parent.originy)*self.parent.grid,
                                            (coord[0]+self.parent.originx)*self.parent.grid,
                                            (coord[1]+self.parent.originy)*self.parent.grid,
                                            dash=(1,5))
    def onCtrlMouseButton1Release_SelectingMore(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        coordAugmentor=self.parent.AugmentorToGridCoordinate(event.x,event.y)
        oldWireListProject=copy.deepcopy(self.parent.schematic.project.GetValue('Drawing.Schematic.Wires'))
        self.UnselectAllDevices()
        self.UnselectAllWires()
        for d in range(len(self.parent.schematic.deviceList)):
            device=self.parent.schematic.deviceList[d]
            if device.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor) or self.selectedDevices[d]:
                device.selected=True
        wireListProject=self.parent.schematic.project.GetValue('Drawing.Schematic.Wires')
        for w in range(len(wireListProject)):
            wireProject=wireListProject[w].GetValue('Vertex')
            for v in range(len(wireProject)):
                vertexProject=wireProject[v]
                vertex=Vertex(eval(vertexProject.GetValue('Coord')),vertexProject.GetValue('Selected'))
                if vertex.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor) or\
                 oldWireListProject[w].GetValue('Vertex')[v].GetValue('Selected'):
                    vertexProject.SetValue('Selected',True)
        self.DispatchBasedOnSelections()
    def onMouseButton3_SelectingMore(self,event):
        pass
    def onMouseButton1Motion_SelectingMore(self,event):
        pass
    def onMouseButton1Release_SelectingMore(self,event):
        pass
    def onMouseButton3Release_SelectingMore(self,event):
        pass
    def onMouseButton1Double_SelectingMore(self,event):
        pass
    def onMouseMotion_SelectingMore(self,event):
        pass

    def MultipleItemsOnClipboard(self,force=False):
        if self.state != 'MultipleItemsOnClipboard' or force:
            self.state='MultipleItemsOnClipboard'
            self.parent.canvas.config(cursor='hand2')
            self.parent.canvas.bind('<Button-1>',self.onMouseButton1_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Control-Button-1>',self.onCtrlMouseButton1_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onCtrlMouseButton1Motion_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onCtrlMouseButton1Release_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Button-3>',self.onMouseButton3_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<B1-Motion>',self.onMouseButton1Motion_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<ButtonRelease-1>',self.onMouseButton1Release_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<ButtonRelease-3>',self.onMouseButton3Release_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Double-Button-1>',self.onMouseButton1Double_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Motion>',self.onMouseMotion_MultipleItemsOnClipboard)
            self.parent.parent.RotatePartDoer.Activate(False)
            self.parent.parent.FlipPartHorizontallyDoer.Activate(False)
            self.parent.parent.FlipPartVerticallyDoer.Activate(False)
            self.parent.parent.DeletePartDoer.Activate(False)
            self.parent.parent.DeleteSelectedDoer.Activate(False)
            self.parent.parent.EditPropertiesDoer.Activate(False)
            self.parent.parent.DuplicatePartDoer.Activate(False)
            self.parent.parent.DuplicateSelectedDoer.Activate(False)
            self.parent.parent.CutSelectedDoer.Activate(False)
            self.parent.parent.DeleteVertexDoer.Activate(False)
            self.parent.parent.DuplicateVertexDoer.Activate(False)
            self.parent.parent.DeleteWireDoer.Activate(False)
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=RAISED)
            self.parent.parent.statusbar.set('Multiple Items in Clipboard')
            self.parent.DrawSchematic()
    def onMouseButton1_MultipleItemsOnClipboard(self,event):
        self.UnselectAllDevices()
        self.UnselectAllWires()
        self.SaveButton1Coordinates(event)
        for device in self.parent.devicesToDuplicate:
            if device['partname'].GetValue() == 'Port':
                portNumberList=[]
                for existingDevice in self.parent.schematic.deviceList:
                    if existingDevice['partname'].GetValue() == 'Port':
                        portNumberList.append(int(existingDevice['pn'].GetValue()))
                if device['pn'].GetValue() in portNumberList:
                    portNumber=1
                    while portNumber in portNumberList:
                        portNumber=portNumber+1
                    device['pn'].SetValueFromString(str(portNumber))
            else:
                existingReferenceDesignators=[]
                for existingDevice in self.parent.schematic.deviceList:
                    referenceDesignatorProperty = existingDevice['ref']
                    if referenceDesignatorProperty != None:
                        existingReferenceDesignators.append(referenceDesignatorProperty.GetValue())
                if device['ref'].GetValue() in existingReferenceDesignators:
                    defaultProperty = device['defref']
                    if defaultProperty != None:
                        defaultPropertyValue = defaultProperty.GetValue()
                        uniqueReferenceDesignator = self.parent.schematic.NewUniqueReferenceDesignator(defaultPropertyValue)
                        if uniqueReferenceDesignator != None:
                            device['ref'].SetValueFromString(uniqueReferenceDesignator)
            device.partPicture.current.SetOrigin((device.partPicture.current.origin[0]+self.parent.Button1Coord[0],device.partPicture.current.origin[1]+self.parent.Button1Coord[1]))
            device.selected=True
            self.parent.schematic.deviceList.append(device)
        for wireProject in self.parent.wiresToDuplicate:
            for vertexProject in wireProject.GetValue('Vertex'):
                vertexProject.SetValue('Selected',True)
                vertexCoord=eval(vertexProject.GetValue('Coord'))
                vertexProject.SetValue('Coord',(vertexCoord[0]+self.parent.Button1Coord[0],vertexCoord[1]++self.parent.Button1Coord[1]))
        schematicProject=self.parent.schematic.project.GetValue('Drawing.Schematic')
        schematicProject.SetValue('Wires',schematicProject.GetValue('Wires')+self.parent.wiresToDuplicate)
        self.parent.parent.history.Event('add multiple items')
        self.DispatchBasedOnSelections()
    def onCtrlMouseButton1_MultipleItemsOnClipboard(self,event):
        pass
    def onCtrlMouseButton1Motion_MultipleItemsOnClipboard(self,event):
        pass
    def onCtrlMouseButton1Release_MultipleItemsOnClipboard(self,event):
        pass
    def onMouseButton3_MultipleItemsOnClipboard(self,event):
        self.DispatchBasedOnSelections()
    def onMouseButton1Motion_MultipleItemsOnClipboard(self,event):
        pass
    def onMouseButton1Release_MultipleItemsOnClipboard(self,event):
        self.DispatchBasedOnSelections()
    def onMouseButton3Release_MultipleItemsOnClipboard(self,event):
        self.DispatchBasedOnSelections()
    def onMouseButton1Double_MultipleItemsOnClipboard(self,event):
        self.DispatchBasedOnSelections()
    def onMouseMotion_MultipleItemsOnClipboard(self,event):
        pass

    def ForceIntializeState(self):
        if self.state == 'Nothing':
            self.Nothing(True)
        elif self.state == 'DeviceSelected':
            self.DeviceSelected(True)
        elif self.state == 'WireSelected':
            self.WireSelected(True)
        elif self.state=='PartLoaded':
            self.PartLoaded(True)
        elif self.state == 'WireLoaded':
            self.WireLoaded(True)
        elif self.state == 'Panning':
            self.Panning(True)
        elif self.state == 'Selecting':
            self.Selecting(True)
        elif self.state == 'Multiple Selections':
            self.MultipleSelections(True)
        elif self.state == 'Selecting More':
            self.SelectingMore(True)
        elif self.state == 'MultipleItemsOnClipboard':
            self.MultipleItemsOnClipboard(True)
        else:
            self.Nothing(True)

class Drawing(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent)
        self.parent=parent
        self.canvas = Canvas(self,relief=SUNKEN,borderwidth=1,width=600,height=600)
        self.canvas.pack(side=TOP, fill=BOTH, expand=YES)
        self.grid=32
        self.originx=0
        self.originy=0
        self.schematic = Schematic()
        self.deviceTearOffMenu=Menu(self, tearoff=0)
        self.deviceTearOffMenu.add_command(label="Edit Properties",command=self.EditSelectedDevice)
        self.deviceTearOffMenu.add_command(label="Duplicate",command=self.DuplicateSelectedDevice)
        self.deviceTearOffMenu.add_command(label="Delete",command=self.DeleteSelectedDevice)
        self.canvasTearOffMenu=Menu(self, tearoff=0)
        self.canvasTearOffMenu.add_command(label='Add Part',command=self.parent.onAddPart)
        self.canvasTearOffMenu.add_command(label='Add Wire',command=self.parent.onAddWire)
        self.canvasTearOffMenu.add_command(label='Add Port',command=self.parent.onAddPort)
        self.wireTearOffMenu=Menu(self, tearoff=0)
        self.wireTearOffMenu.add_command(label="Delete Vertex",command=self.DeleteSelectedVertex)
        self.wireTearOffMenu.add_command(label="Duplicate Vertex",command=self.DuplicateSelectedVertex)
        self.wireTearOffMenu.add_command(label="Delete Wire",command=self.DeleteSelectedWire)
        self.multipleSelectionsTearOffMenu=Menu(self, tearoff=0)
        self.multipleSelectionsTearOffMenu.add_command(label="Cut Selected",command=self.CutMultipleSelections)
        self.multipleSelectionsTearOffMenu.add_command(label="Delete Selected",command=self.DeleteMultipleSelections)
        self.multipleSelectionsTearOffMenu.add_command(label="Duplicate Selected",command=self.DuplicateMultipleSelections)
        self.stateMachine = DrawingStateMachine(self)
    def NearestGridCoordinate(self,x,y):
        return (int(round(float(x)/self.grid))-self.originx,int(round(float(y)/self.grid))-self.originy)
    def AugmentorToGridCoordinate(self,x,y):
        (nearestGridx,nearestGridy)=self.NearestGridCoordinate(x,y)
        return (float(x)/self.grid-self.originx-nearestGridx,float(y)/self.grid-self.originy-nearestGridy)
    def DrawSchematic(self,canvas=None):
        if canvas==None:
            canvas=self.canvas
            canvas.delete(ALL)
        devicePinConnectedList=self.schematic.DevicePinConnectedList()
        foundAPort=False
        foundASource=False
        foundAnOutput=False
        foundSomething=False
        foundAMeasure=False
        foundAStim=False
        foundAnUnknown=False
        foundASystem=False
        for deviceIndex in range(len(self.schematic.deviceList)):
            device = self.schematic.deviceList[deviceIndex]
            foundSomething=True
            devicePinsConnected=devicePinConnectedList[deviceIndex]
            device.DrawDevice(canvas,self.grid,self.originx,self.originy,devicePinsConnected)
            deviceType = device['partname'].GetValue()
            if  deviceType == 'Port':
                foundAPort = True
            elif deviceType in ['Output','DifferentialVoltageOutput','CurrentOutput']:
                foundAnOutput = True
            elif deviceType == 'Stim':
                foundAStim = True
            elif deviceType == 'Measure':
                foundAMeasure = True
            elif deviceType == 'System':
                foundASystem = True
            elif deviceType == 'Unknown':
                foundAnUnknown = True
            elif device.netlist.GetValue('DeviceName') in ['voltagesource','currentsource']:
                foundASource = True
        if not hasattr(self.parent,'project'):
            return
        if self.parent.project is None:
            return
        for wireProject in self.parent.project.GetValue('Drawing.Schematic.Wires'):
            foundSomething=True
            Wire().InitFromProject(wireProject).DrawWire(canvas,self.grid,self.originx,self.originy)
        for dot in self.schematic.DotList():
            size=self.grid/8
            canvas.create_oval((dot[0]+self.originx)*self.grid-size,(dot[1]+self.originy)*self.grid-size,
                                    (dot[0]+self.originx)*self.grid+size,(dot[1]+self.originy)*self.grid+size,
                                    fill='black',outline='black')
        canSimulate = foundASource and foundAnOutput and not foundAPort and not foundAStim and not foundAMeasure and not foundAnUnknown and not foundASystem
        canCalculateSParameters = foundAPort and not foundAnOutput and not foundAMeasure and not foundAStim and not foundAnUnknown and not foundASystem
        canVirtualProbe = foundAStim and foundAnOutput and foundAMeasure and not foundAPort and not foundASource and not foundAnUnknown and not foundASystem
        canDeembed = foundAPort and foundAnUnknown and foundASystem and not foundAStim and not foundAMeasure and not foundAnOutput
        canCalculate = canSimulate or canCalculateSParameters or canVirtualProbe or canDeembed
        self.parent.SimulateDoer.Activate(canSimulate)
        self.parent.CalculateDoer.Activate(canCalculate)
        self.parent.CalculateSParametersDoer.Activate(canCalculateSParameters)
        self.parent.VirtualProbeDoer.Activate(canVirtualProbe)
        self.parent.DeembedDoer.Activate(canDeembed)
        self.parent.ClearProjectDoer.Activate(foundSomething)
        self.parent.ExportNetListDoer.Activate(foundSomething)
        self.parent.ExportTpXDoer.Activate(foundSomething)
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
            else:
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
    def DeleteSelectedVertex(self):
        del self.schematic.project.GetValue('Drawing.Schematic.Wires')[self.w].GetValue('Vertex')[self.v]
        self.stateMachine.Nothing()
        self.parent.history.Event('delete vertex')
    def DuplicateSelectedVertex(self):
        wireProject=self.schematic.project.GetValue('Drawing.Schematic.Wires')[self.w]
        vertexProject=copy.deepcopy(wireProject.GetValue('Vertex')[self.v])
        self.stateMachine.UnselectAllWires()
        wireProject.SetValue('Vertex',wireProject.GetValue('Vertex')[:self.v]+[vertexProject]+wireProject.GetValue('Vertex')[self.v:])       
        self.stateMachine.WireSelected()
    def DeleteSelectedWire(self):
        del self.schematic.project.GetValue('Drawing.Schematic.Wires')[self.w]
        self.stateMachine.Nothing()
        self.parent.history.Event('delete wire')
    def DeleteMultipleSelections(self,advanceStateMachine=True):
        newDeviceList=[]
        for device in self.schematic.deviceList:
            if not device.selected:
                newDeviceList.append(copy.deepcopy(device))
        newWireListProject=[]
        for wireProject in self.schematic.project.GetValue('Drawing.Schematic.Wires'):
            newWire= []
            for vertexProject in wireProject.GetValue('Vertex'):
                if not vertexProject.GetValue('Selected'):
                    newWire.append(copy.deepcopy(vertexProject))
            if len(newWire) >= 2:
                from ProjectFile import WireConfiguration
                newWireProject=WireConfiguration()
                newWireProject.SetValue('Vertex',newWire)
                newWireListProject.append(copy.deepcopy(newWireProject))
        self.schematic.project.SetValue('Drawing.Schematic.Wires',newWireListProject)
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
        from ProjectFile import WireConfiguration
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
            wireListProject=self.schematic.project.GetValue('Drawing.Schematic.Wires')
            for wireProject in wireListProject:
                newWireProject = WireConfiguration()
                numVerticesSelected = 0
                firstVertexSelected = -1
                lastVertexSelected=-1
                for vertexIndex in range(len(wireProject.GetValue('Vertex'))):
                    vertexProject=wireProject.GetValue('Vertex')[vertexIndex]
                    if vertexProject.GetValue('Selected'):
                        numVerticesSelected=numVerticesSelected+1
                        if firstVertexSelected == -1:
                            firstVertexSelected = vertexIndex
                        lastVertexSelected = vertexIndex
                if numVerticesSelected >= 2:
                    for vertexIndex in range(len(wireProject.GetValue('Vertex'))):
                        if vertexIndex >= firstVertexSelected and vertexIndex <= lastVertexSelected:
                            vertexProject=wireProject.GetValue('Vertex')[vertexIndex]
                            newWireProject.GetValue('Vertex').append(copy.deepcopy(vertexProject))
                            vertexCoord=eval(vertexProject.GetValue('Coord'))
                            if not originSet:
                                originSet=True
                                originx=vertexCoord[0]
                                originy=vertexCoord[1]
                            else:
                                originx=min(originx,vertexCoord[0])
                                originy=min(originy,vertexCoord[1])
                if len(newWireProject.GetValue('Vertex')) >= 2:
                    self.wiresToDuplicate.append(newWireProject)
            if not originSet:
                return
            # originx and originy are the upper leftmost coordinates in the selected stuff
            for device in self.devicesToDuplicate:
                device.partPicture.current.SetOrigin((device.partPicture.current.origin[0]-originx,device.partPicture.current.origin[1]-originy))
            for wireProject in self.wiresToDuplicate:
                for vertexProject in wireProject.GetValue('Vertex'):
                    vertexCoord=eval(vertexProject.GetValue('Coord'))
                    vertexProject.SetValue('Coord',(vertexCoord[0]-originx,vertexCoord[1]-originy))
            if advanceStateMachine:
                self.stateMachine.MultipleItemsOnClipboard()
    def InitFromProject(self,project):
        drawingProperties=project.GetValue('Drawing.DrawingProperties')
        # the canvas and geometry must be set prior to the remainder of the schematic initialization
        # otherwise it will not be the right size.  In the past, the xml happened to have the drawing
        # properties first, which made it work, but it was an accident.
        self.canvas.config(width=drawingProperties.GetValue('Width'),height=drawingProperties.GetValue('Height'))
        self.parent.root.geometry(drawingProperties.GetValue('Geometry').split('+')[0])
        self.grid=drawingProperties.GetValue('Grid')
        self.originx=drawingProperties.GetValue('Originx')
        self.originy=drawingProperties.GetValue('Originy')
        self.schematic = Schematic()
        self.stateMachine = DrawingStateMachine(self)
        self.schematic.InitFromProject(project)
    # Legacy File Format
    def InitFromXml(self,drawingElement):
        self.grid=32.
        self.originx=0
        self.originy=0
        self.schematic = Schematic()
        self.stateMachine = DrawingStateMachine(self)
        canvasWidth=600
        canvasHeight=600
        geometry='600x600'
        for child in drawingElement:
            if child.tag == 'schematic':
                self.schematic.InitFromXml(child)
            elif child.tag == 'drawing_properties':
                for drawingPropertyElement in child:
                    if drawingPropertyElement.tag == 'grid':
                        self.grid = float(drawingPropertyElement.text)
                    elif drawingPropertyElement.tag == 'originx':
                        self.originx = int(drawingPropertyElement.text)
                    elif drawingPropertyElement.tag == 'originy':
                        self.originy = int(drawingPropertyElement.text)
                    elif drawingPropertyElement.tag == 'width':
                        canvasWidth = int(drawingPropertyElement.text)
                    elif drawingPropertyElement.tag == 'height':
                        canvasHeight = int(drawingPropertyElement.text)
                    elif drawingPropertyElement.tag == 'geometry':
                        geometry = drawingPropertyElement.text
                self.canvas.config(width=canvasWidth,height=canvasHeight)
                self.parent.root.geometry(geometry.split('+')[0])
