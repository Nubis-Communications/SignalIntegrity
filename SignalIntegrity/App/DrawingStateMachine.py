"""
DrawingStateMachine.py
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

import tkinter as tk

import copy

from SignalIntegrity.App.MenuSystemHelpers import Doer
from SignalIntegrity.App.Archive import Archive
import SignalIntegrity.App.Project
from SignalIntegrity.App.Wire import Vertex,SegmentList,Wire

class DrawingStateMachine(object):
    def __init__(self,parent,root):
        self.parent=parent
        self.root=root
        self.NoProject()
        self.parent.canvas.bind('<Control-Button-3>',self.onControlMouseButton3TryToViewSomething)
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
    def SelectSomethingAtButton1Coordinate(self):
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
        return selectedSomething

    def SelectedThingIsAtButton2Coordinate(self):
        for device in self.parent.schematic.deviceList:
            if device.selected and device.IsAt(self.parent.Button2Coord,self.parent.Button2Augmentor,0.1):
                return True
        for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
            for vertexProject in wireProject['Vertices']:
                if vertexProject['Selected'] and vertexProject.IsAt(self.parent.Button2Coord,self.parent.Button2Augmentor,0.2):
                    return True
        return False

    def onMouseButton1TryToSelectSomething(self,event):
        self.parent.lift()
        self.Nothing()
        self.SaveButton1Coordinates(event)
        self.SelectSomethingAtButton1Coordinate()
        self.DispatchBasedOnSelections(self.Selecting)

    def onMouseButton3TryToSelectSomething(self,event):
        """right click selects whatever is under the cursor so its menu can be shown"""
        self.parent.lift()
        self.SaveButton1Coordinates(event)
        self.SaveButton2Coordinates(event)
        self.SelectSomethingAtButton1Coordinate()
        self.DispatchBasedOnSelections()

    def onControlMouseButton3TryToViewSomething(self,event):
        if not self.Locked():
            self.parent.lift()
            self.Nothing()
            self.SaveButton1Coordinates(event)
            from SignalIntegrity.App.DeviceProperties import DeviceViewMenuActions,PerformDeviceViewAction
            for device in self.parent.schematic.deviceList:
                if device.IsAt(self.parent.Button1Coord,self.parent.Button1Augmentor,0.1):
                    actions=DeviceViewMenuActions(device)
                    if len(actions) > 0:
                        # ctrl-right-click prefers opening the associated project over other view actions
                        actionsByKey=dict((action,label) for label,action in actions)
                        action='openproject' if 'openproject' in actionsByKey else actions[0][1]
                        # a lightweight select+redraw here (not DispatchBasedOnSelections(), which
                        # transitions to DeviceSelected() and Consolidate()s the whole schematic again)
                        # so launching the viewer isn't delayed by a second redundant redraw pass
                        device.selected=True
                        self.parent.DrawSchematic()
                        self.parent.update_idletasks()
                        PerformDeviceViewAction(self.root,device,action)
                    break
            self.Unlock()
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
            self.parent.canvas.bind('<Shift-Button-1>',self.onShiftMouseButton1_NoProject)
            self.parent.canvas.bind('<Shift-B1-Motion>',self.onShiftMouseButton1Motion_NoProject)
            self.parent.canvas.bind('<Shift-ButtonRelease-1>',self.onShiftMouseButton1Release_NoProject)
            self.parent.canvas.bind('<Control-Button-1>',self.onControlMouseButton1_NoProject)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onControlMouseButton1Motion_NoProject)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onControlMouseButton1Release_NoProject)
            self.parent.canvas.bind('<Button-3>',self.onMouseButton3_NoProject)
            self.parent.canvas.bind('<B1-Motion>',self.onMouseButton1Motion_NoProject)
            self.parent.canvas.bind('<ButtonRelease-1>',self.onMouseButton1Release_NoProject)
            self.parent.canvas.bind('<ButtonRelease-3>',self.onMouseButton3Release_NoProject)
            self.parent.canvas.bind('<Double-Button-1>',self.onMouseButton1Double_NoProject)
            self.parent.canvas.bind('<Motion>',self.onMouseMotion_NoProject)
            self.root.NewProjectDoer.Activate(True)
            self.root.OpenProjectDoer.Activate(True)
            self.root.CloseProjectDoer.Activate(False)
            self.root.SaveProjectDoer.Activate(False)
            self.root.SaveAsProjectDoer.Activate(False)
            self.root.ClearProjectDoer.Activate(False)
            self.root.ExportNetListDoer.Activate(False)
            self.root.ExportTpXDoer.Activate(False)
            self.root.ExportPngDoer.Activate(False)
            self.root.ArchiveDoer.Activate(False)
            self.root.ExtractArchiveDoer.Activate(True)
            self.root.FreshenArchiveDoer.Activate(False)
            self.root.UnExtractArchiveDoer.Activate(False)
            self.root.MakeWritableDoer.Activate(False)
            self.root.MakeReadOnlyDoer.Activate(False)
            self.root.UndoDoer.Activate(False)
            self.root.RedoDoer.Activate(False)
            self.root.DeleteSelectedDoer.Activate(False)
            self.root.DuplicateSelectedDoer.Activate(False)
            self.root.CutSelectedDoer.Activate(False)
            self.root.AddPartDoer.Activate(False)
            self.root.AddNetNameDoer.Activate(False)
            self.root.AddPortDoer.Activate(False)
            self.root.AddMeasureProbeDoer.Activate(False)
            self.root.AddOutputProbeDoer.Activate(False)
            self.root.AddStimDoer.Activate(False)
            self.root.AddUnknownDoer.Activate(False)
            self.root.AddSystemDoer.Activate(False)
            self.root.DeletePartDoer.Activate(False)
            self.root.EditPropertiesDoer.Activate(False)
            self.root.DuplicatePartDoer.Activate(False)
            self.root.RotatePartDoer.Activate(False)
            self.root.FlipPartHorizontallyDoer.Activate(False)
            self.root.FlipPartVerticallyDoer.Activate(False)
            self.root.ConvertPartDoer.Activate(False)
            self.root.AddWireDoer.Activate(False)
            self.root.DeleteVertexDoer.Activate(False)
            self.root.DuplicateVertexDoer.Activate(False)
            self.root.DeleteWireDoer.Activate(False)
            self.root.ZoomInDoer.Activate(False)
            self.root.ZoomOutDoer.Activate(False)
            self.root.PanDoer.Activate(False)
            self.root.ViewPictureDoer.Activate(False)
            self.root.CalculationPropertiesDoer.Activate(False)
            self.root.PostProcessingDoer.Activate(False)
            self.root.SParameterViewerDoer.Activate(True)
            self.root.CalculateDoer.Activate(False)
            self.root.CalculateSParametersDoer.Activate(False)
            self.root.SimulateDoer.Activate(False)
            self.root.TransferParametersDoer.Activate(False)
            self.root.VirtualProbeDoer.Activate(False)
            self.root.DeembedDoer.Activate(False)
            self.root.VariablesDoer.Activate(False)
            self.root.EquationsDoer.Activate(False)
            self.root.ParameterizeDoer.Activate(False)
            self.root.HelpDoer.Activate(True)
            self.root.ControlHelpDoer.Activate(True)
            self.root.EscapeDoer.Activate(True)
            self.root.statusbar.set('No Project')
            self.parent.DrawSchematic()

    def onMouseButton1_NoProject(self,event):
        pass
    def onShiftMouseButton1_NoProject(self,event):
        pass
    def onShiftMouseButton1Motion_NoProject(self,event):
        pass
    def onShiftMouseButton1Release_NoProject(self,event):
        pass
    def onControlMouseButton1_NoProject(self,event):
        pass
    def onControlMouseButton1Motion_NoProject(self,event):
        pass
    def onControlMouseButton1Release_NoProject(self,event):
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
            self.root.config(cursor='left_ptr')
            self.parent.canvas.bind('<Button-1>',self.onMouseButton1_Nothing)
            self.parent.canvas.bind('<Shift-Button-1>',self.onShiftMouseButton1_Nothing)
            self.parent.canvas.bind('<Shift-B1-Motion>',self.onShiftMouseButton1Motion_Nothing)
            self.parent.canvas.bind('<Shift-ButtonRelease-1>',self.onShiftMouseButton1Release_Nothing)
            self.parent.canvas.bind('<Control-Button-1>',self.onControlMouseButton1_Nothing)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onControlMouseButton1Motion_Nothing)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onControlMouseButton1Release_Nothing)
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
            self.root.NewProjectDoer.Activate(True)
            self.root.OpenProjectDoer.Activate(True)
            self.root.CloseProjectDoer.Activate(True)
            self.root.SaveProjectDoer.Activate(True)
            self.root.SaveAsProjectDoer.Activate(True)
            self.root.ClearProjectDoer.Activate(True)
            self.root.ExportNetListDoer.Activate(True)
            self.root.ExportTpXDoer.Activate(True)
            self.root.ExportPngDoer.Activate(True)
            self.root.ArchiveDoer.Activate(True)
            self.root.ExtractArchiveDoer.Activate(True)
            inAnArchive=Archive.InAnArchive(self.root.fileparts.FullFilePathExtension())
            self.root.FreshenArchiveDoer.Activate(inAnArchive)
            self.root.UnExtractArchiveDoer.Activate(inAnArchive)
            self.root.MakeWritableDoer.Activate(False)
            self.root.MakeReadOnlyDoer.Activate(not self.root.ProjectChanged())
            #self.root.UndoDoer.Activate(False)
            #self.root.RedoDoer.Activate(False)
            self.root.DeleteSelectedDoer.Activate(False)
            self.root.DuplicateSelectedDoer.Activate(False)
            self.root.CutSelectedDoer.Activate(False)
            self.root.AddPartDoer.Activate(True)
            self.root.AddNetNameDoer.Activate(True)
            self.root.AddPortDoer.Activate(True)
            self.root.AddMeasureProbeDoer.Activate(True)
            self.root.AddOutputProbeDoer.Activate(True)
            self.root.AddStimDoer.Activate(True)
            self.root.AddUnknownDoer.Activate(True)
            self.root.AddSystemDoer.Activate(True)
            self.root.DeletePartDoer.Activate(False)
            self.root.EditPropertiesDoer.Activate(False)
            self.root.DuplicatePartDoer.Activate(False)
            self.root.RotatePartDoer.Activate(False)
            self.root.FlipPartHorizontallyDoer.Activate(False)
            self.root.FlipPartVerticallyDoer.Activate(False)
            self.root.ConvertPartDoer.Activate(False)
            self.root.AddWireDoer.Activate(True)
            self.root.DeleteVertexDoer.Activate(False)
            self.root.DuplicateVertexDoer.Activate(False)
            self.root.DeleteWireDoer.Activate(False)
            self.root.ZoomInDoer.Activate(True)
            self.root.ZoomOutDoer.Activate(True)
            self.root.PanDoer.Activate(True)
            self.root.ViewPictureDoer.Activate(True)
            self.root.CalculationPropertiesDoer.Activate(True)
            self.root.PostProcessingDoer.Activate(True)
            self.root.SParameterViewerDoer.Activate(True)
            #self.root.CalculateDoer.Activate(False)
            #self.root.CalculateSParametersDoer.Activate(False)
            #self.root.SimulateDoer.Activate(False)
            #self.root.TransferParametersDoer.Activate(False)
            #self.root.VirtualProbeDoer.Activate(False)
            #self.root.DeembedDoer.Activate(False)
            self.root.VariablesDoer.Activate(True)
            self.root.EquationsDoer.Activate(True)
            self.root.ParameterizeDoer.Activate(True)
            self.root.HelpDoer.Activate(True)
            self.root.ControlHelpDoer.Activate(True)
            self.root.EscapeDoer.Activate(False)
            self.root.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.root.statusbar.clear()
            self.parent.DrawSchematic()
    def onMouseButton1_Nothing(self,event):
        if not self.Locked():
            self.onMouseButton1TryToSelectSomething(event)
            self.Unlock()
    def onShiftMouseButton1_Nothing(self,event):
        self.onMouseButton1_Nothing(event)
    def onShiftMouseButton1Motion_Nothing(self,event):
        pass
    def onShiftMouseButton1Release_Nothing(self,event):
        pass
    def onControlMouseButton1_Nothing(self,event):
        if not self.Locked():
            self.onMouseButton1TryToSelectSomething(event)
            self.parent.EditSelectedDevice()
            self.Unlock()
    def onControlMouseButton1Motion_Nothing(self,event):
        pass
    def onControlMouseButton1Release_Nothing(self,event):
        pass
    def onMouseButton3_Nothing(self,event):
        if not self.Locked():
            self.onMouseButton3TryToSelectSomething(event)
            self.Unlock()
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
            self.parent.canvas.bind('<Shift-Button-1>',self.onShiftMouseButton1_DeviceSelected)
            self.parent.canvas.bind('<Shift-B1-Motion>',self.onShiftMouseButton1Motion_DeviceSelected)
            self.parent.canvas.bind('<Shift-ButtonRelease-1>',self.onShiftMouseButton1Release_DeviceSelected)
            self.parent.canvas.bind('<Control-Button-1>',self.onControlMouseButton1_DeviceSelected)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onControlMouseButton1Motion_DeviceSelected)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onControlMouseButton1Release_DeviceSelected)
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
            self.root.RotatePartDoer.Activate(True)
            self.root.FlipPartHorizontallyDoer.Activate(True)
            self.root.FlipPartVerticallyDoer.Activate(True)
            self.root.ConvertPartDoer.Activate(True)
            self.root.DeletePartDoer.Activate(True)
            self.root.DeleteSelectedDoer.Activate(True)
            self.root.EditPropertiesDoer.Activate(True)
            self.root.DuplicatePartDoer.Activate(True)
            self.root.DuplicateSelectedDoer.Activate(True)
            self.root.CutSelectedDoer.Activate(True)
            self.root.DeleteVertexDoer.Activate(False)
            self.root.DuplicateVertexDoer.Activate(False)
            self.root.DeleteWireDoer.Activate(False)
            self.root.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.root.statusbar.set('Part Selected')
            self.parent.DrawSchematic()
    def onMouseButton1_DeviceSelected(self,event):
        if not self.Locked():
            self.onMouseButton1TryToSelectSomething(event)
            self.Unlock()
    def onShiftMouseButton1_DeviceSelected(self,event):
        if not self.Locked():
            self.onMouseButton1TryToToggleSomething(event)
            self.Unlock()
    def onShiftMouseButton1Motion_DeviceSelected(self,event):
        pass
    def onShiftMouseButton1Release_DeviceSelected(self,event):
        if not self.Locked():
            self.parent.schematic.Consolidate()
            self.parent.DrawSchematic()
            self.Unlock()
    def onControlMouseButton1_DeviceSelected(self,event):
        if not self.Locked():
            self.onMouseButton1TryToSelectSomething(event)
            self.parent.EditSelectedDevice()
            self.Unlock()
    def onControlMouseButton1Motion_DeviceSelected(self,event):
        pass
    def onControlMouseButton1Release_DeviceSelected(self,event):
        pass
    def onMouseButton3_DeviceSelected(self,event):
        if not self.Locked():
            self.SaveButton2Coordinates(event)
            if not self.parent.deviceSelected.IsAt(self.parent.Button2Coord,self.parent.Button2Augmentor,0.1):
                self.Nothing()
                self.onMouseButton3TryToSelectSomething(event)
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
            self.root.history.Event('release selected device')
            self.parent.DrawSchematic()
            self.Unlock()
    def onMouseButton3Release_DeviceSelected(self,event):
        if not self.Locked():
            self.parent.deviceTearOffMenu=tk.Menu(self.parent, tearoff=0)
            self.parent.deviceTearOffMenu.add_command(label="Edit Properties",command=self.parent.EditSelectedDevice)
            from SignalIntegrity.App.DeviceProperties import DeviceViewMenuActions
            device=self.parent.deviceSelected
            for label,action in DeviceViewMenuActions(device):
                self.parent.deviceTearOffMenu.add_command(label=label,command=lambda action=action: self.parent.ViewSelectedDevice(action))
            if not self.parent.deviceSelected.configuration is None:
                if isinstance(self.parent.deviceSelected.configuration,list):
                    for config in self.parent.deviceSelected.configuration:
                        self.parent.deviceTearOffMenu.add_command(label=config.name,command=lambda: config.onConfiguration(self.parent))
                else:
                    config=self.parent.deviceSelected.configuration
                    self.parent.deviceTearOffMenu.add_command(label=config.name,command=lambda: config.onConfiguration(self.parent))
            self.parent.deviceTearOffMenu.add_command(label="Duplicate",command=self.parent.DuplicateSelectedDevice)
            self.parent.deviceTearOffMenu.add_command(label="Delete",command=self.parent.DeleteSelectedDevice)
            self.parent.deviceTearOffMenu.add_command(label='Convert',command=self.parent.ConvertSelectedDevice)
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
            self.parent.canvas.bind('<Shift-Button-1>',self.onShiftMouseButton1_WireSelected)
            self.parent.canvas.bind('<Shift-B1-Motion>',self.onShiftMouseButton1Motion_WireSelected)
            self.parent.canvas.bind('<Shift-ButtonRelease-1>',self.onShiftMouseButton1Release_WireSelected)
            self.parent.canvas.bind('<Control-Button-1>',self.onControlMouseButton1_WireSelected)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onControlMouseButton1Motion_WireSelected)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onControlMouseButton1Release_WireSelected)
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
            self.root.RotatePartDoer.Activate(False)
            self.root.FlipPartHorizontallyDoer.Activate(False)
            self.root.FlipPartVerticallyDoer.Activate(False)
            self.root.ConvertPartDoer.Activate(False)
            self.root.DeletePartDoer.Activate(False)
            self.root.DeleteSelectedDoer.Activate(False)
            self.root.EditPropertiesDoer.Activate(False)
            self.root.DuplicatePartDoer.Activate(False)
            self.root.DuplicateSelectedDoer.Activate(False)
            self.root.CutSelectedDoer.Activate(False)
            self.root.DeleteVertexDoer.Activate(True)
            self.root.DuplicateVertexDoer.Activate(True)
            self.root.DeleteWireDoer.Activate(True)
            self.root.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.root.statusbar.set('Wire Selected')
            self.parent.DrawSchematic()
    def onMouseButton1_WireSelected(self,event):
        if not self.Locked():
            self.onMouseButton1TryToSelectSomething(event)
            self.Unlock()
    def onShiftMouseButton1_WireSelected(self,event):
        if not self.Locked():
            self.onMouseButton1TryToToggleSomething(event)
            self.Unlock()
    def onShiftMouseButton1Motion_WireSelected(self,event):
        pass
    def onShiftMouseButton1Release_WireSelected(self,event):
        pass
    def onControlMouseButton1_WireSelected(self,event):
        if not self.Locked():
            self.onMouseButton1TryToSelectSomething(event)
            self.parent.EditSelectedDevice()
            self.Unlock()
    def onControlMouseButton1Motion_WireSelected(self,event):
        pass
    def onControlMouseButton1Release_WireSelected(self,event):
        pass
    def onMouseButton3_WireSelected(self,event):
        if not self.Locked():
            self.Nothing()
            self.onMouseButton3TryToSelectSomething(event)
            self.Unlock()
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
            self.root.history.Event('release selected wire')
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
            self.parent.canvas.bind('<Shift-Button-1>',self.onShiftMouseButton1_PartLoaded)
            self.parent.canvas.bind('<Shift-B1-Motion>',self.onShiftMouseButton1Motion_PartLoaded)
            self.parent.canvas.bind('<Shift-ButtonRelease-1>',self.onShiftMouseButton1Release_PartLoaded)
            self.parent.canvas.bind('<Control-Button-1>',self.onControlMouseButton1_PartLoaded)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onControlMouseButton1Motion_PartLoaded)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onControlMouseButton1Release_PartLoaded)
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
            self.root.RotatePartDoer.Activate(False)
            self.root.FlipPartHorizontallyDoer.Activate(False)
            self.root.FlipPartVerticallyDoer.Activate(False)
            self.root.ConvertPartDoer.Activate(False)
            self.root.DeletePartDoer.Activate(False)
            self.root.DeleteSelectedDoer.Activate(True)
            self.root.EditPropertiesDoer.Activate(False)
            self.root.DuplicatePartDoer.Activate(False)
            self.root.DuplicateSelectedDoer.Activate(False)
            self.root.CutSelectedDoer.Activate(False)
            self.root.DeleteVertexDoer.Activate(False)
            self.root.DuplicateVertexDoer.Activate(False)
            self.root.DeleteWireDoer.Activate(False)
            self.root.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.root.statusbar.set('Part In Clipboard')
            self.parent.DrawSchematic()
    def onMouseButton1_PartLoaded(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.parent.partLoaded.partPicture.current.SetOrigin(self.parent.Button1Coord)
            self.parent.schematic.deviceList.append(self.parent.partLoaded)
            self.parent.schematic.deviceList[-1].selected=True
            self.DeviceSelected()
            self.root.history.Event('part added')
            self.Unlock()
    def onShiftMouseButton1_PartLoaded(self,event):
        pass
    def onShiftMouseButton1Motion_PartLoaded(self,event):
        pass
    def onShiftMouseButton1Release_PartLoaded(self,event):
        pass
    def onControlMouseButton1_PartLoaded(self,event):
        if not self.Locked():
            self.onMouseButton1TryToSelectSomething(event)
            self.parent.EditSelectedDevice()
            self.Unlock()
    def onControlMouseButton1Motion_PartLoaded(self,event):
        pass
    def onControlMouseButton1Release_PartLoaded(self,event):
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
            self.parent.canvas.bind('<Shift-Button-1>',self.onShiftMouseButton1_WireLoaded)
            self.parent.canvas.bind('<Shift-B1-Motion>',self.onShiftMouseButton1Motion_WireLoaded)
            self.parent.canvas.bind('<Shift-ButtonRelease-1>',self.onShiftMouseButton1Release_WireLoaded)
            self.parent.canvas.bind('<Control-Button-1>',self.onControlMouseButton1_WireLoaded)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onControlMouseButton1Motion_WireLoaded)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onControlMouseButton1Release_WireLoaded)
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
            self.root.RotatePartDoer.Activate(False)
            self.root.FlipPartHorizontallyDoer.Activate(False)
            self.root.FlipPartVerticallyDoer.Activate(False)
            self.root.ConvertPartDoer.Activate(False)
            self.root.DeletePartDoer.Activate(False)
            self.root.DeleteSelectedDoer.Activate(False)
            self.root.EditPropertiesDoer.Activate(False)
            self.root.DuplicatePartDoer.Activate(False)
            self.root.DuplicateSelectedDoer.Activate(False)
            self.root.CutSelectedDoer.Activate(False)
            self.root.DeleteVertexDoer.Activate(False)
            self.root.DuplicateVertexDoer.Activate(False)
            self.root.DeleteWireDoer.Activate(False)
            self.root.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.root.statusbar.set('Drawing Wires')
            self.parent.DrawSchematic()
    def onMouseButton1_WireLoaded(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.parent.wireLoaded['Vertices'][-1]['Coord']=self.parent.Button1Coord
            self.parent.DrawSchematic()
            self.Unlock()
    def onShiftMouseButton1_WireLoaded(self,event):
        pass
    def onShiftMouseButton1Motion_WireLoaded(self,event):
        pass
    def onShiftMouseButton1Release_WireLoaded(self,event):
        pass
    def onControlMouseButton1_WireLoaded(self,event):
        if not self.Locked():
            self.onMouseButton1TryToSelectSomething(event)
            self.parent.EditSelectedDevice()
            self.Unlock()
    def onControlMouseButton1Motion_WireLoaded(self,event):
        pass
    def onControlMouseButton1Release_WireLoaded(self,event):
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
                self.root.history.Event('add wire')
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
            self.parent.canvas.bind('<Shift-Button-1>',self.onShiftMouseButton1_Panning)
            self.parent.canvas.bind('<Shift-B1-Motion>',self.onShiftMouseButton1Motion_Panning)
            self.parent.canvas.bind('<Shift-ButtonRelease-1>',self.onShiftMouseButton1Release_Panning)
            self.parent.canvas.bind('<Control-Button-1>',self.onControlMouseButton1_Panning)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onControlMouseButton1Motion_Panning)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onControlMouseButton1Release_Panning)
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
            self.root.RotatePartDoer.Activate(False)
            self.root.FlipPartHorizontallyDoer.Activate(False)
            self.root.FlipPartVerticallyDoer.Activate(False)
            self.root.ConvertPartDoer.Activate(False)
            self.root.DeletePartDoer.Activate(False)
            self.root.DeleteSelectedDoer.Activate(False)
            self.root.EditPropertiesDoer.Activate(False)
            self.root.DuplicatePartDoer.Activate(False)
            self.root.DuplicateSelectedDoer.Activate(False)
            self.root.CutSelectedDoer.Activate(False)
            self.root.DeleteVertexDoer.Activate(False)
            self.root.DuplicateVertexDoer.Activate(False)
            self.root.DeleteWireDoer.Activate(False)
            self.root.PanDoer.toolBarElement.button.config(relief=tk.SUNKEN)
            self.root.statusbar.set('Panning')
            self.parent.DrawSchematic()
    def onMouseButton1_Panning(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.Unlock()
    def onShiftMouseButton1_Panning(self,event):
        pass
    def onShiftMouseButton1Motion_Panning(self,event):
        pass
    def onShiftMouseButton1Release_Panning(self,event):
        pass
    def onControlMouseButton1_Panning(self,event):
        pass
    def onControlMouseButton1Motion_Panning(self,event):
        pass
    def onControlMouseButton1Release_Panning(self,event):
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
            self.root.history.Event('Pan')
            self.Nothing()
            self.Unlock()
    def onMouseButton3Release_Panning(self,event):
        if not self.Locked():
            self.root.history.Event('Pan')
            self.Nothing()
            self.Unlock()
    def onMouseButton1Double_Panning(self,event):
        if not self.Locked():
            self.root.history.Event('Pan')
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
            self.root.history.Event('Pan')
            self.Nothing()
            self.Unlock()

    def Selecting(self,force=False):
        if self.state != 'Selecting' or force:
            self.parent.canvas.config(cursor='left_ptr')
            self.state='Selecting'
            self.UnselectAllDevices()
            self.UnselectAllWires()
            self.parent.canvas.bind('<Button-1>',self.onMouseButton1_Selecting)
            self.parent.canvas.bind('<Shift-Button-1>',self.onShiftMouseButton1_Selecting)
            self.parent.canvas.bind('<Shift-B1-Motion>',self.onShiftMouseButton1Motion_Selecting)
            self.parent.canvas.bind('<Shift-ButtonRelease-1>',self.onShiftMouseButton1Release_Selecting)
            self.parent.canvas.bind('<Control-Button-1>',self.onControlMouseButton1_Selecting)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onControlMouseButton1Motion_Selecting)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onControlMouseButton1Release_Selecting)
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
            self.root.RotatePartDoer.Activate(False)
            self.root.FlipPartHorizontallyDoer.Activate(False)
            self.root.FlipPartVerticallyDoer.Activate(False)
            self.root.ConvertPartDoer.Activate(False)
            self.root.DeletePartDoer.Activate(False)
            self.root.DeleteSelectedDoer.Activate(False)
            self.root.EditPropertiesDoer.Activate(False)
            self.root.DuplicatePartDoer.Activate(False)
            self.root.DuplicateSelectedDoer.Activate(False)
            self.root.CutSelectedDoer.Activate(False)
            self.root.DeleteVertexDoer.Activate(False)
            self.root.DuplicateVertexDoer.Activate(False)
            self.root.DeleteWireDoer.Activate(False)
            self.root.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.root.statusbar.set('Selecting')
            self.parent.DrawSchematic()
    def onMouseButton1_Selecting(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.Unlock()
    def onShiftMouseButton1_Selecting(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.Unlock()
    def onShiftMouseButton1Motion_Selecting(self,event):
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
            grid=self.parent.DisplayGrid()
            originx=drawingPropertiesProject['Originx']
            originy=drawingPropertiesProject['Originy']
            self.parent.canvas.create_rectangle((self.parent.Button1Coord[0]+self.parent.Button1Augmentor[0]+originx)*grid,
                                                (self.parent.Button1Coord[1]+self.parent.Button1Augmentor[1]+originy)*grid,
                                                (coord[0]+coordAugmentor[0]+originx)*grid,
                                                (coord[1]+coordAugmentor[1]+originy)*grid,
                                                dash=(1,5))
            self.Unlock()
    def onShiftMouseButton1Release_Selecting(self,event):
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
    def onControlMouseButton1_Selecting(self,event):
        if not self.Locked():
            self.onMouseButton1TryToSelectSomething(event)
            self.parent.EditSelectedDevice()
            self.Unlock()
    def onControlMouseButton1Motion_Selecting(self,event):
        pass
    def onControlMouseButton1Release_Selecting(self,event):
        pass
    def onMouseButton3_Selecting(self,event):
        if not self.Locked():
            self.Nothing()
            self.onMouseButton3TryToSelectSomething(event)
            self.Unlock()
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
            grid=self.parent.DisplayGrid()
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
            self.parent.canvas.bind('<Shift-Button-1>',self.onShiftMouseButton1_MultipleSelections)
            self.parent.canvas.bind('<Shift-B1-Motion>',self.onShiftMouseButton1Motion_MultipleSelections)
            self.parent.canvas.bind('<Shift-ButtonRelease-1>',self.onShiftMouseButton1Release_MultipleSelections)
            self.parent.canvas.bind('<Control-Button-1>',self.onControlMouseButton1_MultipleSelections)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onControlMouseButton1Motion_MultipleSelections)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onControlMouseButton1Release_MultipleSelections)
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
            self.root.RotatePartDoer.Activate(False)
            self.root.FlipPartHorizontallyDoer.Activate(False)
            self.root.FlipPartVerticallyDoer.Activate(False)
            self.root.ConvertPartDoer.Activate(False)
            self.root.DeletePartDoer.Activate(False)
            self.root.DeleteSelectedDoer.Activate(True)
            self.root.EditPropertiesDoer.Activate(False)
            self.root.DuplicatePartDoer.Activate(False)
            self.root.DuplicateSelectedDoer.Activate(True)
            self.root.CutSelectedDoer.Activate(True)
            self.root.DeleteVertexDoer.Activate(False)
            self.root.DuplicateVertexDoer.Activate(False)
            self.root.DeleteWireDoer.Activate(False)
            self.root.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.root.statusbar.set('Multiple Selections')
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
    def onShiftMouseButton1_MultipleSelections(self,event):
        if not self.Locked():
            self.onMouseButton1TryToToggleSomething(event)
            self.Unlock()
    def onShiftMouseButton1Motion_MultipleSelections(self,event):
        pass
    def onShiftMouseButton1Release_MultipleSelections(self,event):
        if not self.Locked():
            self.MultipleSelections()
            self.Unlock()
    def onControlMouseButton1_MultipleSelections(self,event):
        if not self.Locked():
            self.onMouseButton1TryToSelectSomething(event)
            self.parent.EditSelectedDevice()
            self.Unlock()
    def onControlMouseButton1Motion_MultipleSelections(self,event):
        pass
    def onControlMouseButton1Release_MultipleSelections(self,event):
        pass
    def onMouseButton3_MultipleSelections(self,event):
        if not self.Locked():
            self.SaveButton2Coordinates(event)
            if self.SelectedThingIsAtButton2Coordinate():
                self.parent.tk.call('tk_popup',self.parent.multipleSelectionsTearOffMenu, event.x_root, event.y_root)
            else:
                self.Nothing()
                self.onMouseButton3TryToSelectSomething(event)
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
            self.root.history.Event('release multiple selections')
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
            self.parent.canvas.bind('<Shift-Button-1>',self.onShiftMouseButton1_SelectingMore)
            self.parent.canvas.bind('<Shift-B1-Motion>',self.onShiftMouseButton1Motion_SelectingMore)
            self.parent.canvas.bind('<Shift-ButtonRelease-1>',self.onShiftMouseButton1Release_SelectingMore)
            self.parent.canvas.bind('<Control-Button-1>',self.onControlMouseButton1_SelectingMore)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onControlMouseButton1Motion_SelectingMore)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onControlMouseButton1Release_SelectingMore)
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
            self.root.RotatePartDoer.Activate(False)
            self.root.FlipPartHorizontallyDoer.Activate(False)
            self.root.FlipPartVerticallyDoer.Activate(False)
            self.root.ConvertPartDoer.Activate(False)
            self.root.DeletePartDoer.Activate(False)
            self.root.DeleteSelectedDoer.Activate(False)
            self.root.EditPropertiesDoer.Activate(False)
            self.root.DuplicatePartDoer.Activate(False)
            self.root.DuplicateSelectedDoer.Activate(False)
            self.root.CutSelectedDoer.Activate(False)
            self.root.DeleteVertexDoer.Activate(False)
            self.root.DuplicateVertexDoer.Activate(False)
            self.root.DeleteWireDoer.Activate(False)
            self.root.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.root.statusbar.set('Selecting More')
            self.parent.DrawSchematic()
    def onMouseButton1_SelectingMore(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.Unlock()
    def onShiftMouseButton1_SelectingMore(self,event):
        if not self.Locked():
            self.SaveButton1Coordinates(event)
            self.Unlock()
    def onShiftMouseButton1Motion_SelectingMore(self,event):
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
            grid=self.parent.DisplayGrid()
            originx=drawingPropertiesProject['Originx']
            originy=drawingPropertiesProject['Originy']
            self.parent.canvas.create_rectangle((self.parent.Button1Coord[0]+originx)*grid,
                                                (self.parent.Button1Coord[1]+originy)*grid,
                                                (coord[0]+originx)*grid,
                                                (coord[1]+originy)*grid,
                                                dash=(1,5))
            self.Unlock()
    def onShiftMouseButton1Release_SelectingMore(self,event):
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
    def onControlMouseButton1_SelectingMore(self,event):
        if not self.Locked():
            self.onMouseButton1TryToSelectSomething(event)
            self.parent.EditSelectedDevice()
            self.Unlock()
    def onControlMouseButton1Motion_SelectingMore(self,event):
        pass
    def onControlMouseButton1Release_SelectingMore(self,event):
        pass
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
            self.parent.canvas.bind('<Shift-Button-1>',self.onShiftMouseButton1_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Shift-B1-Motion>',self.onShiftMouseButton1Motion_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Shift-ButtonRelease-1>',self.onShiftMouseButton1Release_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Control-Button-1>',self.onControlMouseButton1_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Control-B1-Motion>',self.onControlMouseButton1Motion_MultipleItemsOnClipboard)
            self.parent.canvas.bind('<Control-ButtonRelease-1>',self.onControlMouseButton1Release_MultipleItemsOnClipboard)
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
            self.root.RotatePartDoer.Activate(False)
            self.root.FlipPartHorizontallyDoer.Activate(False)
            self.root.FlipPartVerticallyDoer.Activate(False)
            self.root.ConvertPartDoer.Activate(False)
            self.root.DeletePartDoer.Activate(False)
            self.root.DeleteSelectedDoer.Activate(False)
            self.root.EditPropertiesDoer.Activate(False)
            self.root.DuplicatePartDoer.Activate(False)
            self.root.DuplicateSelectedDoer.Activate(False)
            self.root.CutSelectedDoer.Activate(False)
            self.root.DeleteVertexDoer.Activate(False)
            self.root.DuplicateVertexDoer.Activate(False)
            self.root.DeleteWireDoer.Activate(False)
            self.root.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.root.statusbar.set('Multiple Items in Clipboard')
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
                elif device['partname'].GetValue() == 'NetworkAnalyzerStimulus':
                    portNumberList=[]
                    for existingDevice in self.parent.schematic.deviceList:
                        if existingDevice['partname'].GetValue() == 'NetworkAnalyzerStimulus':
                            portNumberList.append(int(existingDevice['pn'].GetValue()))
                    if device['pn'].GetValue() in portNumberList:
                        portNumber=1
                        while portNumber in portNumberList:
                            portNumber=portNumber+1
                        device['pn'].SetValueFromString(str(portNumber))
                existingReferenceDesignators=[]
                for existingDevice in self.parent.schematic.deviceList:
                    referenceDesignatorProperty = existingDevice['ref']
                    if referenceDesignatorProperty != None:
                        existingReferenceDesignators.append(referenceDesignatorProperty.GetValue())
                if device['ref'] != None:
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
            self.root.history.Event('add multiple items')
            self.DispatchBasedOnSelections()
            self.Unlock()
    def onShiftMouseButton1_MultipleItemsOnClipboard(self,event):
        pass
    def onShiftMouseButton1Motion_MultipleItemsOnClipboard(self,event):
        pass
    def onShiftMouseButton1Release_MultipleItemsOnClipboard(self,event):
        pass
    def onControlMouseButton1_MultipleItemsOnClipboard(self,event):
        pass
    def onControlMouseButton1Motion_MultipleItemsOnClipboard(self,event):
        pass
    def onControlMouseButton1Release_MultipleItemsOnClipboard(self,event):
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
