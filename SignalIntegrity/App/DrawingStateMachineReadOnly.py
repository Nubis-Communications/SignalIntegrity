"""
DrawingStateMachineReadOnly.py
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

from SignalIntegrity.App.MenuSystemHelpers import Doer
from SignalIntegrity.App.DrawingStateMachine import DrawingStateMachine
from SignalIntegrity.App.Files import FileParts

class DrawingStateMachineReadOnly(DrawingStateMachine):
    """state machine for a project opened read-only.

    Only the NoProject and Nothing states exist - every other state of the base class
    exists solely to edit, so they all redirect to Nothing.
    """
    def ActivateDoers(self):
        app=self.parent.parent
        app.NewProjectDoer.Activate(True)
        app.OpenProjectDoer.Activate(True)
        app.CloseProjectDoer.Activate(True)
        app.SaveProjectDoer.Activate(False)
        app.SaveAsProjectDoer.Activate(False)
        app.ClearProjectDoer.Activate(False)
        app.ExportNetListDoer.Activate(True)
        app.ExportTpXDoer.Activate(True)
        app.ExportPngDoer.Activate(True)
        app.ArchiveDoer.Activate(True)
        app.ExtractArchiveDoer.Activate(True)
        app.FreshenArchiveDoer.Activate(False)
        app.UnExtractArchiveDoer.Activate(False)
        app.UndoDoer.Activate(False)
        app.RedoDoer.Activate(False)
        app.DeleteSelectedDoer.Activate(False)
        app.DuplicateSelectedDoer.Activate(False)
        app.CutSelectedDoer.Activate(False)
        app.AddPartDoer.Activate(False)
        app.AddNetNameDoer.Activate(False)
        app.AddPortDoer.Activate(False)
        app.AddMeasureProbeDoer.Activate(False)
        app.AddOutputProbeDoer.Activate(False)
        app.AddStimDoer.Activate(False)
        app.AddUnknownDoer.Activate(False)
        app.AddSystemDoer.Activate(False)
        app.DeletePartDoer.Activate(False)
        app.EditPropertiesDoer.Activate(False)
        app.DuplicatePartDoer.Activate(False)
        app.RotatePartDoer.Activate(False)
        app.FlipPartHorizontallyDoer.Activate(False)
        app.FlipPartVerticallyDoer.Activate(False)
        app.ConvertPartDoer.Activate(False)
        app.AddWireDoer.Activate(False)
        app.DeleteVertexDoer.Activate(False)
        app.DuplicateVertexDoer.Activate(False)
        app.DeleteWireDoer.Activate(False)
        # pan and zoom write the grid and origin into the project
        app.ZoomInDoer.Activate(False)
        app.ZoomOutDoer.Activate(False)
        app.PanDoer.Activate(False)
        app.ViewPictureDoer.Activate(False)
        app.CalculationPropertiesDoer.Activate(False)
        app.PostProcessingDoer.Activate(False)
        app.SParameterViewerDoer.Activate(True)
        app.VariablesDoer.Activate(False)
        app.EquationsDoer.Activate(False)
        app.ParameterizeDoer.Activate(False)
        app.HelpDoer.Activate(True)
        app.ControlHelpDoer.Activate(True)
        app.EscapeDoer.Activate(False)
        app.MakeWritableDoer.Activate(True)
        app.MakeReadOnlyDoer.Activate(False)

    def Nothing(self,force=False):
        if not hasattr(self,'state'):
            self.state=''
        if self.state != 'Nothing' or force:
            self.parent.canvas.config(cursor='left_ptr')
            self.state='Nothing'
            self.UnselectAllDevices()
            self.UnselectAllWires()
            Doer.inHelp = False
            self.parent.parent.config(cursor='left_ptr')
            for sequence in ['<Button-1>','<Shift-Button-1>','<Shift-B1-Motion>',
                             '<Shift-ButtonRelease-1>','<Control-Button-1>','<Control-B1-Motion>',
                             '<Control-ButtonRelease-1>','<Button-3>','<Control-Button-3>','<B1-Motion>',
                             '<ButtonRelease-1>','<ButtonRelease-3>','<Double-Button-1>',
                             '<Motion>','<Right>','<Left>','<Up>','<Down>','<Escape>']:
                self.parent.canvas.unbind(sequence)
            self.parent.canvas.bind('<Button-3>',self.onMouseButton3_Nothing)
            self.parent.canvas.bind('<Control-Button-3>',self.onControlMouseButton3_Nothing)
            self.parent.focus_set()
            self.ActivateDoers()
            self.parent.parent.PanDoer.toolBarElement.button.config(relief=tk.RAISED)
            self.parent.parent.statusbar.set('Read Only')
            self.parent.DrawSchematic()

    def onMouseButton3_Nothing(self,event):
        if getattr(event,'state',0) & 0x0004:
            return 'break'
        if not self.Locked():
            self.SaveButton2Coordinates(event)
            for device in self.parent.schematic.deviceList:
                if device.IsAt(self.parent.Button2Coord,self.parent.Button2Augmentor,0.1):
                    if not self.SelectDeviceForView(device) is None:
                        menu=tk.Menu(self.parent,tearoff=0)
                        menu.add_command(label='View',command=lambda: self.ViewDevice(device))
                        self.parent.tk.call('tk_popup',menu,event.x_root,event.y_root)
                    break
            self.Unlock()

    def onControlMouseButton3_Nothing(self,event):
        if not self.Locked():
            self.SaveButton2Coordinates(event)
            for device in self.parent.schematic.deviceList:
                if device.IsAt(self.parent.Button2Coord,self.parent.Button2Augmentor,0.1):
                    if not self.SelectDeviceForView(device) is None:
                        self.ViewDevice(device)
                    break
            self.Unlock()
        return 'break'

    def SelectDeviceForView(self,device):
        from SignalIntegrity.App.DeviceProperties import ViewableFileNameOfDevice
        filename=ViewableFileNameOfDevice(device)
        if filename is None:
            return None
        self.UnselectAllDevices()
        device.selected=True
        self.parent.DrawSchematic()
        self.parent.update_idletasks()
        return filename

    def ViewDevice(self,device):
        from SignalIntegrity.App.DeviceProperties import ViewDeviceFile
        filename=self.SelectDeviceForView(device)
        if filename is None:
            return
        ViewDeviceFile(self.parent.parent,device)
        if FileParts(filename).fileext == '.si':
            self.UnselectAllDevices()
            self.parent.DrawSchematic()

    def DeviceSelected(self,force=False):
        self.Nothing(True)
    def WireSelected(self,force=False):
        self.Nothing(True)
    def PartLoaded(self,force=False):
        self.Nothing(True)
    def WireLoaded(self,force=False):
        self.Nothing(True)
    def Panning(self,force=False):
        self.Nothing(True)
    def Selecting(self,force=False):
        self.Nothing(True)
    def MultipleSelections(self,force=False):
        self.Nothing(True)
    def SelectingMore(self,force=False):
        self.Nothing(True)
    def MultipleItemsOnClipboard(self,force=False):
        self.Nothing(True)

    def DispatchBasedOnSelections(self,nothingSelectedState=None):
        self.Nothing(True)

    def MoveSelectedObjects(self,x,y):
        pass
    def MoveDrawingOrigin(self,x,y):
        pass
