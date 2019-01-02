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
    import Tkinter as tk
else:
    import tkinter as tk

import copy

from SignalIntegrity.App.Device import DeviceFromProject
from SignalIntegrity.App.NetList import NetList
from SignalIntegrity.App.Wire import WireList,Vertex,SegmentList,Wire
from SignalIntegrity.App.MenuSystemHelpers import Doer
from SignalIntegrity.App.DeviceProperties import DevicePropertiesDialog
import SignalIntegrity.App.Project

class Schematic(object):
    def __init__(self):
        self.deviceList = []
    def InitFromProject(self):
        self.__init__()
        if SignalIntegrity.App.Project is None:
            return
        deviceListProject=SignalIntegrity.App.Project['Drawing.Schematic.Devices']
        for d in range(len(deviceListProject)):
            try:
                returnedDevice=DeviceFromProject(deviceListProject[d]).result
            except NameError: # part picture doesn't exist
                returnedDevice=None
            if not returnedDevice is None:
                self.deviceList.append(returnedDevice)
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
        if not SignalIntegrity.App.Project is None:
            SignalIntegrity.App.Project['Drawing.Schematic'].dict['Wires']=WireList()
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
        if SignalIntegrity.App.Project is None:
            return devicePinConnectedList
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
                    for wire in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
                        if thisPinConnected:
                            break
                        for vertex in wire['Vertices']:
                            if thisPinCoordinate == vertex['Coord']:
                                thisPinConnected=True
                                break
                thisDeviceConnectedList.append(thisPinConnected)
            devicePinConnectedList.append(thisDeviceConnectedList)
        return devicePinConnectedList
    def Consolidate(self):
        if SignalIntegrity.App.Project is None:
            return
        SignalIntegrity.App.Project['Drawing.Schematic'].dict['Wires'].ConsolidateWires(self)
    def DotList(self):
        dotList=[]
        if SignalIntegrity.App.Project is None:
            return dotList
        # make a list of all coordinates
        coordList=[]
        for device in self.deviceList:
            coordList=coordList+device.PinCoordinates()
        wireListProject = SignalIntegrity.App.Project['Drawing.Schematic.Wires']
        for wireProject in wireListProject:
            vertexCoordinates=[vertexProject['Coord'] for vertexProject in wireProject['Vertices']]
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
        if SignalIntegrity.App.Project is None:
            return
        for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
            for vertexProject in wireProject['Vertices']:
                vertexProject['Selected']=False
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
        for w in range(len(SignalIntegrity.App.Project['Drawing.Schematic.Wires'])):
            for v in range(len(SignalIntegrity.App.Project['Drawing.Schematic.Wires'][w]['Vertices'])):
                if SignalIntegrity.App.Project['Drawing.Schematic.Wires'][w]['Vertices'][v]['Selected']:
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
        for wire in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
            for vertex in wire['Vertices']:
                if vertex.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.2):
                    selectedSomething=True
                    vertex['Selected']=True
        if not selectedSomething:
            for wireIndex in range(len(SignalIntegrity.App.Project['Drawing.Schematic.Wires'])):
                wireProject=SignalIntegrity.App.Project['Drawing.Schematic.Wires'][wireIndex]
                segmentList=SegmentList(wireProject)
                for segment in segmentList:
                    if segment.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.2):
                        segment.selected=True
                        selectedSomething=True
                        break
                if selectedSomething:
                    wire = segmentList.Wire()
                    wireProject['Vertices']=[vertex for vertex in wire]
                    break
        self.DispatchBasedOnSelections(self.Selecting)
    def onMouseButton1TryToToggleSomething(self,event):
        self.SaveButton1Coordinates(event)
        toggledSomething=False
        for device in self.parent.schematic.deviceList:
            if device.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.1):
                device.selected=not device.selected
                toggledSomething=True
        for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
            for vertexProject in wireProject['Vertices']:
                if vertexProject.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.2):
                    vertexProject['Selected']=not vertexProject['Selected']
                    toggledSomething=True
        if not toggledSomething:
            for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
                segmentList=SegmentList(wireProject)
                for segment in segmentList:
                    if segment.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.2):
                        segment.selected=not segment.selected
                        toggledSomething=True
                        break
                if toggledSomething:
                    wire = segmentList.Wire()
                    wireProject['Vertices']=[Vertex() for vertex in wire]
                    for v in range(len(wireProject['Vertices'])):
                        vertexProject=wireProject['Vertices'][v]
                        vertex=wire[v]
                        vertexProject['Coord']=vertex['Coord']
                        vertexProject['Selected']=vertex['Selected']
                    break
        if toggledSomething:
            self.parent.DrawSchematic()
            self.DispatchBasedOnSelections()
            return

        self.selectedDevices = [device.selected for device in self.parent.schematic.deviceList]
        self.SelectingMore()

    def MoveSelectedObjects(self,x,y):
        for d in range(len(self.parent.schematic.deviceList)):
            device=self.parent.schematic.deviceList[d]
            if device.selected:
                device.partPicture.current.origin=(device.partPicture.current.origin[0]+x,device.partPicture.current.origin[1]+y)
        for w in range(len(SignalIntegrity.App.Project['Drawing.Schematic.Wires'])):
            wireProject=SignalIntegrity.App.Project['Drawing.Schematic.Wires'][w]
            for v in range(len(wireProject['Vertices'])):
                vertexProject=wireProject['Vertices'][v]
                if vertexProject['Selected']:
                    vertexProject['Coord']=(vertexProject['Coord'][0]+x,vertexProject['Coord'][1]+y)
        self.parent.DrawSchematic()

    def MoveDrawingOrigin(self,x,y):
        drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        drawingPropertiesProject['Originx']=drawingPropertiesProject['Originx']+x
        drawingPropertiesProject['Originy']=drawingPropertiesProject['Originy']+y
        self.parent.DrawSchematic()

    def Locked(self):
        if not hasattr(self,'locked'):
            locked=False
        else:
            locked=self.locked
        self.locked=True
        return locked

    def Unlock(self):
        self.locked=False

    def NoProject(self,force=False):
        if not hasattr(self,'state'):
            self.state=''
        if self.state != 'NoProject' or force:
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
    def onRightKey_NoProject(self,event):
        pass
    def onLeftKey_NoProject(self,event):
        pass
    def onUpKey_NoProject(self,event):
        pass
    def onDownKey_NoProject(self,event):
        pass
    def onEscapeKey_NoProject(self,event):
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
            self.parent.canvas.bind('<Right>',self.onRightKey_Nothing)
            self.parent.canvas.bind('<Left>',self.onLeftKey_Nothing)
            self.parent.canvas.bind('<Up>',self.onUpKey_Nothing)
            self.parent.canvas.bind('<Down>',self.onDownKey_Nothing)
            self.parent.canvas.bind('<Escape>',self.onEscapeKey_Nothing)
            self.parent.focus_set()
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
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.parent.parent.statusbar.clear()
            self.parent.DrawSchematic()
    def onMouseButton1_Nothing(self,event):
        if not self.Locked():
            self.onMouseButton1TryToSelectSomething(event)
            self.Unlock()
    def onCtrlMouseButton1_Nothing(self,event):
        if not self.Locked():
            self.onMouseButton1_Nothing(event)
            self.Unlock()
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
        if not self.Locked():
            self.parent.tk.call('tk_popup',self.parent.canvasTearOffMenu, event.x_root, event.y_root)
            self.Unlock()
    def onMouseButton1Double_Nothing(self,event):
        pass
    def onMouseMotion_Nothing(self,event):
        pass
    def onRightKey_Nothing(self,event):
        pass
    def onLeftKey_Nothing(self,event):
        pass
    def onUpKey_Nothing(self,event):
        pass
    def onDownKey_Nothing(self,event):
        pass
    def onEscapeKey_Nothing(self,event):
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
            self.parent.canvas.bind('<Right>',self.onRightKey_DeviceSelected)
            self.parent.canvas.bind('<Left>',self.onLeftKey_DeviceSelected)
            self.parent.canvas.bind('<Up>',self.onUpKey_DeviceSelected)
            self.parent.canvas.bind('<Down>',self.onDownKey_DeviceSelected)
            self.parent.canvas.bind('<Escape>',self.onEscapeKey_DeviceSelected)
            self.parent.canvas.focus_set()
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
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.parent.parent.statusbar.set('Part Selected')
            self.parent.DrawSchematic()
    def onMouseButton1_DeviceSelected(self,event):
        if not self.Locked():
            self.onMouseButton1TryToSelectSomething(event)
            self.Unlock()
    def onCtrlMouseButton1_DeviceSelected(self,event):
        if not self.Locked():
            self.onMouseButton1TryToToggleSomething(event)
            self.Unlock()
    def onCtrlMouseButton1Motion_DeviceSelected(self,event):
        pass
    def onCtrlMouseButton1Release_DeviceSelected(self,event):
        if not self.Locked():
            self.parent.schematic.Consolidate()
            self.parent.DrawSchematic()
            self.Unlock()
    def onMouseButton3_DeviceSelected(self,event):
        if not self.Locked():
            self.SaveButton2Coordinates(event)
            if not self.parent.deviceSelected.IsAt(self.parent.Button2Coord,self.parent.Button2Augmentor,0.1):
                self.Nothing()
            self.Unlock()
    def onMouseButton1Motion_DeviceSelected(self,event):
        if not self.Locked():
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            self.parent.deviceSelected.partPicture.current.SetOrigin([coord[0]-self.parent.coordInPart[0],coord[1]-self.parent.coordInPart[1]])
            self.parent.DrawSchematic()
            self.Unlock()
    def onMouseButton1Release_DeviceSelected(self,event):
        if not self.Locked():
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            self.parent.deviceSelected.partPicture.current.SetOrigin([coord[0]-self.parent.coordInPart[0],coord[1]-self.parent.coordInPart[1]])
            self.parent.schematic.Consolidate()
            self.parent.parent.history.Event('release selected device')
            self.parent.DrawSchematic()
            self.Unlock()
    def onMouseButton3Release_DeviceSelected(self,event):
        if not self.Locked():
            self.parent.tk.call("tk_popup", self.parent.deviceTearOffMenu, event.x_root, event.y_root)
            self.Unlock()
    def onMouseButton1Double_DeviceSelected(self,event):
        if not self.Locked():
            self.parent.EditSelectedDevice()
            self.Unlock()
    def onMouseMotion_DeviceSelected(self,event):
        pass
    def onRightKey_DeviceSelected(self,event):
        if not self.Locked():
            self.MoveSelectedObjects(1,0)
            self.Unlock()
    def onLeftKey_DeviceSelected(self,event):
        if not self.Locked():
            self.MoveSelectedObjects(-1,0)
            self.Unlock()
    def onUpKey_DeviceSelected(self,event):
        if not self.Locked():
            self.MoveSelectedObjects(0,-1)
            self.Unlock()
    def onDownKey_DeviceSelected(self,event):
        if not self.Locked():
            self.MoveSelectedObjects(0,1)
            self.Unlock()
    def onEscapeKey_DeviceSelected(self,event):
        if not self.Locked():
            self.Nothing()
            self.Unlock()

    def WireSelected(self,force=False):
        if self.state != 'WireSelected' or force:
            self.state='WireSelected'
            wireListProject=SignalIntegrity.App.Project['Drawing.Schematic.Wires']
            for w in range(len(wireListProject)):
                wireProject=wireListProject[w]
                for v in range(len(wireProject['Vertices'])):
                    vertexProject=wireProject['Vertices'][v]
                    if vertexProject['Selected']:
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
            self.parent.canvas.bind('<Right>',self.onRightKey_WireSelected)
            self.parent.canvas.bind('<Left>',self.onLeftKey_WireSelected)
            self.parent.canvas.bind('<Up>',self.onUpKey_WireSelected)
            self.parent.canvas.bind('<Down>',self.onDownKey_WireSelected)
            self.parent.canvas.bind('<Escape>',self.onEscapeKey_WireSelected)
            self.parent.canvas.focus_set()
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
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.parent.parent.statusbar.set('Wire Selected')
            self.parent.DrawSchematic()
    def onMouseButton1_WireSelected(self,event):
        if not self.Locked():
            self.onMouseButton1TryToSelectSomething(event)
            self.Unlock()
    def onCtrlMouseButton1_WireSelected(self,event):
        if not self.Locked():
            self.onMouseButton1TryToToggleSomething(event)
            self.Unlock()
    def onCtrlMouseButton1Motion_WireSelected(self,event):
        pass
    def onCtrlMouseButton1Release_WireSelected(self,event):
        pass
    def onMouseButton3_WireSelected(self,event):
        pass
    def onMouseButton1Motion_WireSelected(self,event):
        if not self.Locked():
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            SignalIntegrity.App.Project['Drawing.Schematic.Wires'][self.parent.w]['Vertices'][self.parent.v]['Coord']=coord
            self.parent.DrawSchematic()
            self.Unlock()
    def onMouseButton1Release_WireSelected(self,event):
        if not self.Locked():
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            SignalIntegrity.App.Project['Drawing.Schematic.Wires'][self.parent.w]['Vertices'][self.parent.v]['Coord']=coord
            self.parent.schematic.Consolidate()
            self.parent.parent.history.Event('release selected wire')
            self.parent.DrawSchematic()
            self.Unlock()
    def onMouseButton3Release_WireSelected(self,event):
        if not self.Locked():
            self.parent.tk.call('tk_popup',self.parent.wireTearOffMenu, event.x_root, event.y_root)
            self.Unlock()
    def onMouseButton1Double_WireSelected(self,event):
        pass
    def onMouseMotion_WireSelected(self,event):
        pass
    def onRightKey_WireSelected(self,event):
        if not self.Locked():
            self.MoveSelectedObjects(1,0)
            self.Unlock()
    def onLeftKey_WireSelected(self,event):
        if not self.Locked():
            self.MoveSelectedObjects(-1,0)
            self.Unlock()
    def onUpKey_WireSelected(self,event):
        if not self.Locked():
            self.MoveSelectedObjects(0,-1)
            self.Unlock()
    def onDownKey_WireSelected(self,event):
        if not self.Locked():
            self.MoveSelectedObjects(0,1)
            self.Unlock()
    def onEscapeKey_WireSelected(self,event):
        if not self.Locked():
            self.Nothing()
            self.Unlock()

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
            self.parent.canvas.bind('<Right>',self.onRightKey_PartLoaded)
            self.parent.canvas.bind('<Left>',self.onLeftKey_PartLoaded)
            self.parent.canvas.bind('<Up>',self.onUpKey_PartLoaded)
            self.parent.canvas.bind('<Down>',self.onDownKey_PartLoaded)
            self.parent.canvas.bind('<Escape>',self.onEscapeKey_PartLoaded)
            self.parent.focus_set()
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
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.parent.parent.statusbar.set('Part In Clipboard')
            self.parent.DrawSchematic()
    def onMouseButton1_PartLoaded(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.parent.partLoaded.partPicture.current.SetOrigin(self.parent.Button1Coord)
            self.parent.schematic.deviceList.append(self.parent.partLoaded)
            self.parent.schematic.deviceList[-1].selected=True
            self.DeviceSelected()
            self.parent.parent.history.Event('part added')
            self.Unlock()
    def onCtrlMouseButton1_PartLoaded(self,event):
        pass
    def onCtrlMouseButton1Motion_PartLoaded(self,event):
        pass
    def onCtrlMouseButton1Release_PartLoaded(self,event):
        pass
    def onMouseButton3_PartLoaded(self,event):
        if not self.Locked():
            self.Nothing()
            self.Unlock()
    def onMouseButton1Motion_PartLoaded(self,event):
        if not self.Locked():
            self.Nothing()
            self.Unlock()
    def onMouseButton1Release_PartLoaded(self,event):
        if not self.Locked():
            self.Nothing()
            self.Unlock()
    def onMouseButton3Release_PartLoaded(self,event):
        if not self.Locked():
            self.Nothing()
            self.Unlock()
    def onMouseButton1Double_PartLoaded(self,event):
        if not self.Locked():
            self.Nothing()
            self.Unlock()
    def onMouseMotion_PartLoaded(self,event):
        pass
    def onRightKey_PartLoaded(self,event):
        pass
    def onLeftKey_PartLoaded(self,event):
        pass
    def onUpKey_PartLoaded(self,event):
        pass
    def onDownKey_PartLoaded(self,event):
        pass
    def onEscapeKey_PartLoaded(self,event):
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
            self.parent.canvas.bind('<Right>',self.onRightKey_WireLoaded)
            self.parent.canvas.bind('<Left>',self.onLeftKey_WireLoaded)
            self.parent.canvas.bind('<Up>',self.onUpKey_WireLoaded)
            self.parent.canvas.bind('<Down>',self.onDownKey_WireLoaded)
            self.parent.canvas.bind('<Escape>',self.onEscapeKey_WireLoaded)
            self.parent.focus_set()
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
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.parent.parent.statusbar.set('Drawing Wires')
            self.parent.DrawSchematic()
    def onMouseButton1_WireLoaded(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.parent.wireLoaded['Vertices'][-1]['Coord']=self.parent.Button1Coord
            self.parent.DrawSchematic()
            self.Unlock()
    def onCtrlMouseButton1_WireLoaded(self,event):
        pass
    def onCtrlMouseButton1Motion_WireLoaded(self,event):
        pass
    def onCtrlMouseButton1Release_WireLoaded(self,event):
        pass
    def onMouseButton3_WireLoaded(self,event):
        pass
    def onMouseButton1Motion_WireLoaded(self,event):
        if not self.Locked():
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            if len(self.parent.wireLoaded['Vertices']) > 0:
                self.parent.wireLoaded['Vertices'][-1]['Coord']=coord
                self.parent.DrawSchematic()
            self.Unlock()
    def onMouseButton1Release_WireLoaded(self,event):
        if not self.Locked():
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            self.parent.wireLoaded['Vertices'].append(Vertex(coord,False))
            self.parent.DrawSchematic()
            self.Unlock()
    def onMouseButton3Release_WireLoaded(self,event):
        if not self.Locked():
            self.SaveButton2Coordinates(event)
            if len(self.parent.wireLoaded['Vertices']) > 2:
                wireListProject=SignalIntegrity.App.Project['Drawing.Schematic.Wires']
                wireProject=Wire()
                wireProject['Vertices']=self.parent.wireLoaded['Vertices'][:-1]
                wireListProject[-1]=wireProject
                wireProject=Wire()
                wireProject['Vertices']=[Vertex((0,0),False)]
                self.parent.wireLoaded=wireProject
                wireListProject.append(self.parent.wireLoaded)
                self.parent.parent.history.Event('add wire')
                self.parent.DrawSchematic()
            else:
                self.Nothing()
            self.Unlock()
    def onMouseButton1Double_WireLoaded(self,event):
        if not self.Locked():
            self.parent.wireLoaded=None
            self.Nothing()
            self.Unlock()
    def onMouseMotion_WireLoaded(self,event):
        if not self.Locked():
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            self.parent.wireLoaded['Vertices'][-1]['Coord']=coord
            self.parent.DrawSchematic()
            self.Unlock()
    def onRightKey_WireLoaded(self,event):
        pass
    def onLeftKey_WireLoaded(self,event):
        pass
    def onUpKey_WireLoaded(self,event):
        pass
    def onDownKey_WireLoaded(self,event):
        pass
    def onEscapeKey_WireLoaded(self,event):
        pass

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
            self.parent.canvas.bind('<Right>',self.onRightKey_Panning)
            self.parent.canvas.bind('<Left>',self.onLeftKey_Panning)
            self.parent.canvas.bind('<Up>',self.onUpKey_Panning)
            self.parent.canvas.bind('<Down>',self.onDownKey_Panning)
            self.parent.canvas.bind('<Escape>',self.onEscapeKey_Panning)
            self.parent.canvas.focus_set()
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
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=tk.SUNKEN)
            self.parent.parent.statusbar.set('Panning')
            self.parent.DrawSchematic()
    def onMouseButton1_Panning(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.Unlock()
    def onCtrlMouseButton1_Panning(self,event):
        pass
    def onCtrlMouseButton1Motion_Panning(self,event):
        pass
    def onCtrlMouseButton1Release_Panning(self,event):
        pass
    def onMouseButton3_Panning(self,event):
        pass
    def onMouseButton1Motion_Panning(self,event):
        if not self.Locked():
            drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            drawingPropertiesProject['Originx']=drawingPropertiesProject['Originx']+coord[0]-self.parent.Button1Coord[0]
            drawingPropertiesProject['Originy']=drawingPropertiesProject['Originy']+coord[1]-self.parent.Button1Coord[1]
            self.parent.DrawSchematic()
            self.Unlock()
    def onMouseButton1Release_Panning(self,event):
        if not self.Locked():
            self.Nothing()
            self.Unlock()
    def onMouseButton3Release_Panning(self,event):
        if not self.Locked():
            self.Nothing()
            self.Unlock()
    def onMouseButton1Double_Panning(self,event):
        if not self.Locked():
            self.Nothing()
            self.Unlock()
    def onMouseMotion_Panning(self,event):
        pass
    def onRightKey_Panning(self,event):
        if not self.Locked():
            self.MoveDrawingOrigin(1,0)
            self.Unlock()
    def onLeftKey_Panning(self,event):
        if not self.Locked():
            self.MoveDrawingOrigin(-1,0)
            self.Unlock()
    def onUpKey_Panning(self,event):
        if not self.Locked():
            self.MoveDrawingOrigin(0,-1)
            self.Unlock()
    def onDownKey_Panning(self,event):
        if not self.Locked():
            self.MoveDrawingOrigin(0,1)
            self.Unlock()
    def onEscapeKey_Panning(self,event):
        if not self.Locked():
            self.Nothing()
            self.Unlock()

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
            self.parent.canvas.bind('<Right>',self.onRightKey_Selecting)
            self.parent.canvas.bind('<Left>',self.onLeftKey_Selecting)
            self.parent.canvas.bind('<Up>',self.onUpKey_Selecting)
            self.parent.canvas.bind('<Down>',self.onDownKey_Selecting)
            self.parent.canvas.bind('<Escape>',self.onEscapeKey_Selecting)
            self.parent.focus_set()
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
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.parent.parent.statusbar.set('Selecting')
            self.parent.DrawSchematic()
    def onMouseButton1_Selecting(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.Unlock()
    def onCtrlMouseButton1_Selecting(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.Unlock()
    def onCtrlMouseButton1Motion_Selecting(self,event):
        if not self.Locked():
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            coordAugmentor=self.parent.AugmentorToGridCoordinate(event.x,event.y)
            self.UnselectAllDevices()
            self.UnselectAllWires()
            for device in self.parent.schematic.deviceList:
                if device.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                    device.selected=True
            for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
                for vertexProject in wireProject['Vertices']:
                    vertex=Vertex(vertexProject['Coord'],vertexProject['Selected'])
                    if vertex.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                        vertexProject['Selected']=True
            self.parent.DrawSchematic()
            drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
            grid=drawingPropertiesProject['Grid']
            originx=drawingPropertiesProject['Originx']
            originy=drawingPropertiesProject['Originy']
            self.parent.canvas.create_rectangle((self.parent.Button1Coord[0]+self.parent.Button1Augmentor[0]+originx)*grid,
                                                (self.parent.Button1Coord[1]+self.parent.Button1Augmentor[1]+originy)*grid,
                                                (coord[0]+coordAugmentor[0]+originx)*grid,
                                                (coord[1]+coordAugmentor[1]+originy)*grid,
                                                dash=(1,5))
            self.Unlock()
    def onCtrlMouseButton1Release_Selecting(self,event):
        if not self.Locked():
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            coordAugmentor=self.parent.AugmentorToGridCoordinate(event.x,event.y)
            self.UnselectAllDevices()
            self.UnselectAllWires()
            for device in self.parent.schematic.deviceList:
                if device.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                    device.selected=True
            for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
                for vertexProject in wireProject['Vertices']:
                    vertex=Vertex(vertexProject['Coord'],vertexProject['Selected'])
                    if vertex.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                        vertexProject['Selected']=True
            self.DispatchBasedOnSelections()
            self.Unlock()
    def onMouseButton3_Selecting(self,event):
        pass
    def onMouseButton1Motion_Selecting(self,event):
        if not self.Locked():
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            coordAugmentor=self.parent.AugmentorToGridCoordinate(event.x,event.y)
            self.UnselectAllDevices()
            self.UnselectAllWires()
            for device in self.parent.schematic.deviceList:
                if device.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                    device.selected=True
            for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
                for vertexProject in wireProject['Vertices']:
                    if Vertex(vertexProject['Coord'],vertexProject['Selected']).IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                        vertexProject['Selected']=True
            self.parent.DrawSchematic()
            drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
            grid=drawingPropertiesProject['Grid']
            originx=drawingPropertiesProject['Originx']
            originy=drawingPropertiesProject['Originy']
            self.parent.canvas.create_rectangle((self.parent.Button1Coord[0]+self.parent.Button1Augmentor[0]+originx)*grid,
                                                (self.parent.Button1Coord[1]+self.parent.Button1Augmentor[1]+originy)*grid,
                                                (coord[0]+coordAugmentor[0]+originx)*grid,
                                                (coord[1]+coordAugmentor[1]+originy)*grid,
                                                dash=(1,5))
            self.Unlock()
    def onMouseButton1Release_Selecting(self,event):
        if not self.Locked():
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            coordAugmentor=self.parent.AugmentorToGridCoordinate(event.x,event.y)
            self.UnselectAllDevices()
            self.UnselectAllWires()
            for device in self.parent.schematic.deviceList:
                if device.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                    device.selected=True
            for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
                for vertexProject in wireProject['Vertices']:
                    if Vertex(vertexProject['Coord'],vertexProject['Selected']).IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor):
                        vertexProject['Selected']=True
            self.DispatchBasedOnSelections()
            self.Unlock()
    def onMouseButton3Release_Selecting(self,event):
        pass
    def onMouseButton1Double_Selecting(self,event):
        pass
    def onMouseMotion_Selecting(self,event):
        pass
    def onRightKey_Selecting(self,event):
        pass
    def onLeftKey_Selecting(self,event):
        pass
    def onUpKey_Selecting(self,event):
        pass
    def onDownKey_Selecting(self,event):
        pass
    def onEscapeKey_Selecting(self,event):
        pass

    def MultipleSelections(self,force=False):
        if self.state != 'Multiple Selections' or force:
            self.state='Multiple Selections'
            self.parent.canvas.config(cursor='left_ptr')
            self.parent.OriginalDeviceCoordinates = [device.WhereInPart(self.parent.Button1Coord) for device in self.parent.schematic.deviceList]

            self.parent.OriginalWireCoordinates = [[(self.parent.Button1Coord[0]-vertex['Coord'][0],
                                                     self.parent.Button1Coord[1]-vertex['Coord'][1]) for vertex in wire['Vertices']] for wire in SignalIntegrity.App.Project['Drawing.Schematic.Wires']]
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
            self.parent.canvas.bind('<Right>',self.onRightKey_MultipleSelections)
            self.parent.canvas.bind('<Left>',self.onLeftKey_MultipleSelections)
            self.parent.canvas.bind('<Up>',self.onUpKey_MultipleSelections)
            self.parent.canvas.bind('<Down>',self.onDownKey_MultipleSelections)
            self.parent.canvas.bind('<Escape>',self.onEscapeKey_MultipleSelections)
            self.parent.canvas.focus_set()
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
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.parent.parent.statusbar.set('Multiple Selections')
            self.parent.DrawSchematic()
    def onMouseButton1_MultipleSelections(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.parent.OriginalDeviceCoordinates = [device.WhereInPart(self.parent.Button1Coord) for device in self.parent.schematic.deviceList]
            self.parent.OriginalWireCoordinates = [[(self.parent.Button1Coord[0]-vertexProject['Coord'][0],
                                                         self.parent.Button1Coord[1]-vertexProject['Coord'][1]) 
                                                            for vertexProject in wireProject['Vertices']]
                                                                for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']]
            inSelection=False
            for device in self.parent.schematic.deviceList:
                if device.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.1) and device.selected:
                    inSelection=True
                    break
            
            for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
                for vertexProject in wireProject['Vertices']:
                    if vertexProject.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.2) and vertexProject['Selected']:
                        inSelection=True
                        break
            if not inSelection:
                for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
                    segmentList=SegmentList(wireProject)
                    for segment in segmentList:
                        if segment.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.2) and segment.selected:
                            inSelection=True
                            break
                    if inSelection:
                        break
    
            if not inSelection:
                self.onMouseButton1TryToSelectSomething(event)
            self.Unlock()
    def onCtrlMouseButton1_MultipleSelections(self,event):
        if not self.Locked():
            self.onMouseButton1TryToToggleSomething(event)
            self.Unlock()
    def onCtrlMouseButton1Motion_MultipleSelections(self,event):
        pass
    def onCtrlMouseButton1Release_MultipleSelections(self,event):
        if not self.Locked():
            self.MultipleSelections()
            self.Unlock()
    def onMouseButton3_MultipleSelections(self,event):
        if not self.Locked():
            self.parent.tk.call('tk_popup',self.parent.multipleSelectionsTearOffMenu, event.x_root, event.y_root)
            self.Unlock()
    def onMouseButton1Motion_MultipleSelections(self,event):
        if not self.Locked():
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            for d in range(len(self.parent.schematic.deviceList)):
                device=self.parent.schematic.deviceList[d]
                coordInPart = self.parent.OriginalDeviceCoordinates[d]
                if device.selected:
                    device.partPicture.current.SetOrigin([coord[0]-coordInPart[0],coord[1]-coordInPart[1]])
            for w in range(len(SignalIntegrity.App.Project['Drawing.Schematic.Wires'])):
                wireProject=SignalIntegrity.App.Project['Drawing.Schematic.Wires'][w]
                for v in range(len(wireProject['Vertices'])):
                    vertexProject=wireProject['Vertices'][v]
                    if vertexProject['Selected']:
                        vertexProject['Coord']=(coord[0]-self.parent.OriginalWireCoordinates[w][v][0],
                                                              coord[1]-self.parent.OriginalWireCoordinates[w][v][1])
            self.parent.DrawSchematic()
            self.Unlock()
    def onMouseButton1Release_MultipleSelections(self,event):
        if not self.Locked():
            self.parent.schematic.Consolidate()
            self.parent.DrawSchematic()
            self.parent.parent.history.Event('release multiple selections')
            self.Unlock()

    def onMouseButton3Release_MultipleSelections(self,event):
        pass
    def onMouseButton1Double_MultipleSelections(self,event):
        pass
    def onMouseMotion_MultipleSelections(self,event):
        pass
    def onRightKey_MultipleSelections(self,event):
        if not self.Locked():
            self.MoveSelectedObjects(1,0)
            self.Unlock()
    def onLeftKey_MultipleSelections(self,event):
        if not self.Locked():
            self.MoveSelectedObjects(-1,0)
            self.Unlock()
    def onUpKey_MultipleSelections(self,event):
        if not self.Locked():
            self.MoveSelectedObjects(0,-1)
            self.Unlock()
    def onDownKey_MultipleSelections(self,event):
        if not self.Locked():
            self.MoveSelectedObjects(0,1)
            self.Unlock()
    def onEscapeKey_MultipleSelections(self,event):
        if not self.Locked():
            self.Nothing()
            self.Unlock()

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
            self.parent.canvas.bind('<Right>',self.onRightKey_SelectingMore)
            self.parent.canvas.bind('<Left>',self.onLeftKey_SelectingMore)
            self.parent.canvas.bind('<Up>',self.onUpKey_SelectingMore)
            self.parent.canvas.bind('<Down>',self.onDownKey_SelectingMore)
            self.parent.canvas.bind('<Escape>',self.onEscapeKey_SelectingMore)
            self.parent.focus_set()
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
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.parent.parent.statusbar.set('Selecting More')
            self.parent.DrawSchematic()
    def onMouseButton1_SelectingMore(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.Unlock()
    def onCtrlMouseButton1_SelectingMore(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.Unlock()
    def onCtrlMouseButton1Motion_SelectingMore(self,event):
        if not self.Locked():
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            coordAugmentor=self.parent.AugmentorToGridCoordinate(event.x,event.y)
            oldWireListProject=copy.deepcopy(SignalIntegrity.App.Project['Drawing.Schematic.Wires'])
            self.UnselectAllDevices()
            self.UnselectAllWires()
            for d in range(len(self.parent.schematic.deviceList)):
                device=self.parent.schematic.deviceList[d]
                if device.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor) or self.selectedDevices[d]:
                    device.selected=True
            wireListProject=SignalIntegrity.App.Project['Drawing.Schematic.Wires']
            for w in range(len(wireListProject)):
                wireProject=wireListProject[w]['Vertices']
                for v in range(len(wireProject)):
                    vertexProject=wireProject[v]
                    vertex=Vertex(vertexProject['Coord'],vertexProject['Selected'])
                    if vertex.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor) or\
                     oldWireListProject[w]['Vertices'][v]['Selected']:
                        vertexProject['Selected']=True
            self.parent.DrawSchematic()
            drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
            grid=drawingPropertiesProject['Grid']
            originx=drawingPropertiesProject['Originx']
            originy=drawingPropertiesProject['Originy']
            self.parent.canvas.create_rectangle((self.parent.Button1Coord[0]+originx)*grid,
                                                (self.parent.Button1Coord[1]+originy)*grid,
                                                (coord[0]+originx)*grid,
                                                (coord[1]+originy)*grid,
                                                dash=(1,5))
            self.Unlock()
    def onCtrlMouseButton1Release_SelectingMore(self,event):
        if not self.Locked():
            coord=self.parent.NearestGridCoordinate(event.x,event.y)
            coordAugmentor=self.parent.AugmentorToGridCoordinate(event.x,event.y)
            oldWireListProject=copy.deepcopy(SignalIntegrity.App.Project['Drawing.Schematic.Wires'])
            self.UnselectAllDevices()
            self.UnselectAllWires()
            for d in range(len(self.parent.schematic.deviceList)):
                device=self.parent.schematic.deviceList[d]
                if device.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor) or self.selectedDevices[d]:
                    device.selected=True
            wireListProject=SignalIntegrity.App.Project['Drawing.Schematic.Wires']
            for w in range(len(wireListProject)):
                wireProject=wireListProject[w]['Vertices']
                for v in range(len(wireProject)):
                    vertexProject=wireProject[v]
                    vertex=Vertex(vertexProject['Coord'],vertexProject['Selected'])
                    if vertex.IsIn(coord,self.parent.Button1Coord,coordAugmentor,self.parent.Button1Augmentor) or\
                     oldWireListProject[w]['Vertices'][v]['Selected']:
                        vertexProject['Selected']=True
            self.DispatchBasedOnSelections()
            self.Unlock()
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
    def onRightKey_SelectingMore(self,event):
        pass
    def onLeftKey_SelectingMore(self,event):
        pass
    def onUpKey_SelectingMore(self,event):
        pass
    def onDownKey_SelectingMore(self,event):
        pass
    def onEscapeKey_SelectingMore(self,event):
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
            self.parent.canvas.bind('<Right>',self.onRightKey_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Left>',self.onLeftKey_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Up>',self.onUpKey_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Down>',self.onDownKey_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Escape>',self.onEscapeKey_MultipleItemsOnClipboard)
            self.parent.focus_set()
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
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.parent.parent.statusbar.set('Multiple Items in Clipboard')
            self.parent.DrawSchematic()
    def onMouseButton1_MultipleItemsOnClipboard(self,event):
        if not self.Locked():
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
                for vertexProject in wireProject['Vertices']:
                    vertexProject['Selected']=True
                    vertexCoord=vertexProject['Coord']
                    vertexProject['Coord']=(vertexCoord[0]+self.parent.Button1Coord[0],vertexCoord[1]++self.parent.Button1Coord[1])
            schematicProject=SignalIntegrity.App.Project['Drawing.Schematic']
            schematicProject['Wires']=schematicProject['Wires']+self.parent.wiresToDuplicate
            self.parent.parent.history.Event('add multiple items')
            self.DispatchBasedOnSelections()
            self.Unlock()
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
        if not self.Locked():
            self.DispatchBasedOnSelections()
            self.Unlock()
    def onMouseButton3Release_MultipleItemsOnClipboard(self,event):
        if not self.Locked():
            self.DispatchBasedOnSelections()
            self.Unlock()
    def onMouseButton1Double_MultipleItemsOnClipboard(self,event):
        if not self.Locked():
            self.DispatchBasedOnSelections()
            self.Unlock()
    def onMouseMotion_MultipleItemsOnClipboard(self,event):
        pass
    def onRightKey_MultipleItemsOnClipboard(self,event):
        pass
    def onLeftKey_MultipleItemsOnClipboard(self,event):
        pass
    def onUpKey_MultipleItemsOnClipboard(self,event):
        pass
    def onDownKey_MultipleItemsOnClipboard(self,event):
        pass
    def onEscapeKey_MultipleItemsOnClipboard(self,event):
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
            drawingPropertiesProject['Width']=self.Drawing.canvas.winfo_width()
            drawingPropertiesProject['Height']=self.Drawing.canvas.winfo_height()
            drawingPropertiesProject['Geometry']=self.root.geometry()
        grid=drawingPropertiesProject['Grid']
        originx=drawingPropertiesProject['Originx']
        originy=drawingPropertiesProject['Originy']
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
            device.DrawDevice(canvas,grid,originx,originy,devicePinsConnected)
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
            elif device.netlist['DeviceName'] in ['voltagesource','currentsource']:
                foundASource = True
        for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
            foundSomething=True
            wireProject.DrawWire(canvas,grid,originx,originy)
        for dot in self.schematic.DotList():
            size=grid/8
            canvas.create_oval((dot[0]+originx)*grid-size,(dot[1]+originy)*grid-size,
                                    (dot[0]+originx)*grid+size,(dot[1]+originy)*grid+size,
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
        self.canvas.config(width=drawingProperties['Width'],height=drawingProperties['Height'])
        self.parent.root.geometry(drawingProperties['Geometry'].split('+')[0])
        self.schematic = Schematic()
        self.schematic.InitFromProject()
        self.stateMachine = DrawingStateMachine(self)
