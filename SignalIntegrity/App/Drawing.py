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

import tkinter as tk

import copy
import re
import sys

from SignalIntegrity.App.Schematic import Schematic
from SignalIntegrity.App.DrawingStateMachine import DrawingStateMachine
from SignalIntegrity.App.DrawingStateMachineReadOnly import DrawingStateMachineReadOnly
from SignalIntegrity.App.DeviceProperties import DevicePropertiesDialog
from SignalIntegrity.App.PartPicture import PartPicture
from SignalIntegrity.App.Wire import Wire
from SignalIntegrity.App.Theme import ThemedCanvas

import SignalIntegrity.App.Project

def ScaleWindowGeometry(geometry,scale,extraHeight=0):
    match=re.match(r'^(\d+)x(\d+)',geometry)
    if match is None:
        return geometry
    width=round(int(match.group(1))*scale)
    height=round(int(match.group(2))*scale)+extraHeight
    return str(width)+'x'+str(height)+geometry[match.end():]

class SchematicCanvas(ThemedCanvas):
    strokeItemTypes={'line','rectangle','oval','arc','polygon'}

    def __init__(self,parent,displayScale,**kwargs):
        self.displayScale=displayScale
        ThemedCanvas.__init__(self,parent,**kwargs)

    def _create(self,itemType,args,kwargs):
        if itemType in self.strokeItemTypes:
            kwargs=kwargs.copy()
            kwargs['width']=float(kwargs.get('width',1))*self.displayScale+max(0,self.displayScale-1)
            dash=kwargs.get('dash')
            if isinstance(dash,(tuple,list)):
                kwargs['dash']=tuple(max(1,round(value*self.displayScale)) for value in dash)
        return ThemedCanvas._create(self,itemType,args,kwargs)

class Drawing(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        self.parent=parent
        self.canvas = SchematicCanvas(self,parent.displayScale,relief=tk.SUNKEN,borderwidth=1,width=600,height=600)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        self.schematic = Schematic()
        self.pendingPageImport = None
        self.textEditor = None
        self.textEditBrowsing = False
        self.editableTextItems = {}
        self.BuildTearOffMenus()
        self.stateMachine = None
        self.InstallStateMachine()
    def DisplayGrid(self):
        grid=SignalIntegrity.App.Project['Drawing.DrawingProperties']['Grid']
        return grid*self.parent.displayScale
    def ProjectGeometry(self):
        geometry=self.parent.root.geometry()
        if sys.platform.startswith('linux'):
            geometry=ScaleWindowGeometry(geometry,1.0/self.parent.displayScale)
        return geometry
    def BuildTearOffMenus(self):
        self.deviceTearOffMenu=tk.Menu(self, tearoff=0)
        self.canvasTearOffMenu=tk.Menu(self, tearoff=0)
        self.wireTearOffMenu=tk.Menu(self, tearoff=0)
        self.multipleSelectionsTearOffMenu=tk.Menu(self, tearoff=0)
        if self.parent.ReadOnly():
            return
        self.deviceTearOffMenu.add_command(label="Edit Properties",command=self.EditSelectedDevice)
        self.deviceTearOffMenu.add_command(label="Cut",command=self.CutMultipleSelections)
        self.deviceTearOffMenu.add_command(label="Duplicate",command=self.DuplicateSelectedDevice)
        self.deviceTearOffMenu.add_command(label="Delete",command=self.DeleteSelectedDevice)
        self.deviceTearOffMenu.add_command(label='Convert',command=self.ConvertSelectedDevice)
        self.canvasTearOffMenu.add_command(label='Add Part',command=self.parent.onAddPart)
        self.canvasTearOffMenu.add_command(label='Add Wire',command=self.parent.onAddWire)
        self.canvasTearOffMenu.add_command(label='Add Port',command=self.parent.onAddPort)
        self.wireTearOffMenu.add_command(label="Delete Vertex",command=self.DeleteSelectedVertex)
        self.wireTearOffMenu.add_command(label="Duplicate Vertex",command=self.DuplicateSelectedVertex)
        self.wireTearOffMenu.add_command(label="Delete Wire",command=self.DeleteSelectedWire)
        self.multipleSelectionsTearOffMenu.add_command(label="Cut Selected",command=self.CutMultipleSelections)
        self.multipleSelectionsTearOffMenu.add_command(label="Delete Selected",command=self.DeleteMultipleSelections)
        self.multipleSelectionsTearOffMenu.add_command(label="Duplicate Selected",command=self.DuplicateMultipleSelections)
    def InstallStateMachine(self):
        """builds the state machine matching the current read-only mode, preserving the state"""
        state=None if self.stateMachine is None else self.stateMachine.state
        self.BuildTearOffMenus()
        if self.parent.ReadOnly():
            self.stateMachine = DrawingStateMachineReadOnly(self)
        else:
            self.stateMachine = DrawingStateMachine(self)
        if state is not None:
            self.stateMachine.state=state
            self.stateMachine.ForceIntializeState()
    def NearestGridCoordinate(self,x,y):
        drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        grid=self.DisplayGrid()
        originx=drawingPropertiesProject['Originx']
        originy=drawingPropertiesProject['Originy']
        return (int(round(float(x)/grid))-originx,int(round(float(y)/grid))-originy)
    def AugmentorToGridCoordinate(self,x,y):
        drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        grid=self.DisplayGrid()
        originx=drawingPropertiesProject['Originx']
        originy=drawingPropertiesProject['Originy']
        (nearestGridx,nearestGridy)=self.NearestGridCoordinate(x,y)
        return (float(x)/grid-originx-nearestGridx,float(y)/grid-originy-nearestGridy)
    def DrawSchematic(self,canvas=None,evaluateEquations=True):
        if canvas is None:
            canvas=self.canvas
            canvas.delete(tk.ALL)
        onScreen = canvas is getattr(self,'canvas',None)
        if onScreen:
            self.CancelTextEdit()
            self.editableTextItems={}
        if SignalIntegrity.App.Project is None:
            return canvas
        drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        if not canvas is None and hasattr(self, 'Drawing'):
            drawingPropertiesProject['Geometry']=self.ProjectGeometry()
        displayScale=getattr(canvas,'displayScale',1.0)
        grid=drawingPropertiesProject['Grid']*displayScale
        originx=drawingPropertiesProject['Originx']
        originy=drawingPropertiesProject['Originy']
        if evaluateEquations:
            SignalIntegrity.App.Project.EvaluateEquations()
        schematicPropertiesItems=SignalIntegrity.App.Project['Variables'].DisplayItems(True,False,False)
        V=len(schematicPropertiesItems)
        locations=[(7*displayScale,PartPicture.textSpacing*(v+1)*displayScale+3*displayScale) for v in range(V)]
        for v in range(V):
            variable,displayString=schematicPropertiesItems[v]
            item=canvas.create_text(locations[v][0],locations[v][1],text=displayString,anchor='sw',fill='black')
            if onScreen:
                self.editableTextItems[item]=(variable,None)
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
        visible={id(device):connected for device,connected in zip(self.schematic.deviceList,devicePinConnectedList)}
        for device in self.schematic.CircuitDevices():
            visiblePins=visible.get(id(device))
            originalDevice=device
            if device['element_state'] != None:
                if device['element_state'].GetValue() in ['thru','thru_wires']:
                    from SignalIntegrity.App.Device import DeviceThru
                    element_state=device['element_state'].GetValue()
                    device=DeviceThru.ConvertDeviceToThru(device)
                    if element_state == 'thru_wires':
                        from SignalIntegrity.App.PartProperty import PartPropertyElementState
                        device.AddPartProperty(PartPropertyElementState(element_state))
            foundSomething=True
            if visiblePins is not None:
                device.DrawDevice(canvas,grid,originx,originy,visiblePins)
                if onScreen and device is originalDevice:
                    self.RecordEditableDeviceText(device)
            deviceType = device['partname'].GetValue()
            if deviceType == 'WaveformProcessorVariable' and not device.IsProcessingEnabled():
                continue
            if deviceType == 'WaveformProcessorVariable' and device['outputports'].GetValue() == 0:
                foundAnOutput = True
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
            elif device.netlist['DeviceName'] in ['voltagesource','currentsource','networkanalyzerport','voltagenoisesource','currentnoisesource']:
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
        writable = not self.parent.ReadOnly()
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
        self.parent.ClearProjectDoer.Activate(foundSomething and writable)
        self.parent.ExportNetListDoer.Activate(foundSomething)
        self.parent.ExportTpXDoer.Activate(foundSomething)
        self.parent.ExportPngDoer.Activate(foundSomething)
        self.parent.PanDoer.Activate(foundSomething and writable)
        self.parent.ZoomInDoer.Activate(foundSomething and writable)
        self.parent.ZoomOutDoer.Activate(foundSomething and writable)
        return canvas
    def EditSelectedDevice(self):
        if self.parent.ReadOnly():
            return
        if self.stateMachine.state=='DeviceSelected':
            dpe=DevicePropertiesDialog(self.parent,self.deviceSelected)
            if dpe.result != None:
                self.deviceSelected = dpe.result
                self.schematic.deviceList[self.deviceSelectedIndex] = self.deviceSelected
                self.schematic.Consolidate()
                self.DrawSchematic()
                self.parent.history.Event('edit device')
    def RecordEditableDeviceText(self,device):
        picture=device.partPicture.current
        sources=getattr(picture,'visiblePartPropertySources',None)
        items=getattr(picture,'visiblePartPropertyItems',None)
        if sources is None or items is None or len(sources) != len(items):
            return
        for item,source in zip(items,sources):
            if self.IsEditableText(source):
                self.editableTextItems[item]=(source,device)
    @staticmethod
    def IsEditableText(source):
        from SignalIntegrity.App.ProjectFile import VariableConfiguration
        if isinstance(source,VariableConfiguration):
            return True
        return (bool(source['InProjectFile']) and not source['Hidden']
                and source['Keyword'] not in ('ports','inputports','outputports'))
    def EditableTextAt(self,x,y):
        """the (item, source, device) of editable text under canvas window coordinate x,y, if any"""
        x,y=self.canvas.canvasx(x),self.canvas.canvasy(y)
        for item in reversed(self.canvas.find_overlapping(x-1,y-1,x+1,y+1)):
            if item in self.editableTextItems:
                source,device=self.editableTextItems[item]
                return item,source,device
        return None
    def EditTextAt(self,x,y):
        """opens an in-place editor if editable text (and no device body) is at x,y"""
        if self.parent.ReadOnly() or SignalIntegrity.App.Project is None:
            return False
        hit=self.EditableTextAt(x,y)
        if hit is None:
            return False
        coord=self.NearestGridCoordinate(x,y)
        augmentor=self.AugmentorToGridCoordinate(x,y)
        if any(device.IsAt(coord,augmentor,0.1) for device in self.schematic.deviceList):
            return False
        item,source,device=hit
        bbox=self.canvas.bbox(item)
        self.stateMachine.Nothing()
        self.BeginTextEdit(source,device,bbox)
        return True
    def BeginTextEdit(self,source,device,bbox):
        from tkinter import ttk
        import tkinter.font as tkfont
        from SignalIntegrity.App.ProjectFile import VariableConfiguration
        self.CancelTextEdit()
        isVariable=isinstance(source,VariableConfiguration)
        if isVariable:
            name,initial,choices=source['Name'],source.EntryString(),None
        else:
            name,initial=source['Keyword'],source.PropertyString(stype='entry')
            choices=getattr(source,'validEntries',None)
        font=tkfont.nametofont('TkDefaultFont')
        frame=ttk.Frame(self.canvas)
        label=ttk.Label(frame,text=str(name))
        label.pack(side=tk.LEFT,padx=(2,4))
        if choices:
            widget=ttk.Combobox(frame,values=list(choices),state='readonly')
            widget.set(initial)
            widget.bind('<<ComboboxSelected>>',lambda event: self.CommitTextEdit())
            width=max(font.measure(str(choice)) for choice in choices)+font.measure('0')*6
        else:
            widget=tk.Entry(frame,borderwidth=1)
            widget.insert(0,initial)
            widget.select_range(0,tk.END)
            widget.icursor(tk.END)
            width=font.measure(initial)+font.measure('0')*6
        width=max(width,font.measure('0')*12)
        widget.pack(side=tk.LEFT,fill=tk.X,expand=True)
        if not choices and source['Type'] == 'file':
            from SignalIntegrity.App.MenuSystemHelpers import ToolBarElement,ToolTip
            browse=ToolBarElement(frame,iconfile=SignalIntegrity.App.IconsDir+'browse-file.gif',
                                  iconsize=16,padx=1,pady=0,borderwidth=1,highlightthickness=0,
                                  command=self.BrowseTextEditFile).Pack(side=tk.LEFT).button
            ToolTip.createToolTip(browse,'Browse for file')
            width+=browse.winfo_reqwidth()
        width=max(width+font.measure(str(name))+8,bbox[2]-bbox[0])
        # keep the application's root-bound shortcuts (Delete, Ctrl-Z, ...) from acting while typing
        widget.bindtags((str(widget),widget.winfo_class(),'all'))
        for key in ('<Return>','<KP_Enter>','<Tab>'):
            widget.bind(key,lambda event: self.CommitTextEdit())
        widget.bind('<Escape>',lambda event: self.CancelTextEdit())
        widget.bind('<FocusOut>',lambda event: self.after_idle(self.CommitTextEditIfUnfocused))
        window=self.canvas.create_window(bbox[0],bbox[1],anchor='nw',window=frame,width=width)
        self.textEditor=(widget,window,source,device,initial,frame)
        widget.focus_set()
        self.parent.statusbar.set('Editing '+str(name)+': Enter to accept, Escape to cancel')
    def BrowseTextEditFile(self):
        if self.textEditor is None:
            return
        from SignalIntegrity.App.VariablesDialog import AskVariableFileName
        widget=self.textEditor[0]
        # the file dialog takes the focus, which must not commit or close the editor
        self.textEditBrowsing=True
        try:
            filename=AskVariableFileName(widget.get(),self.parent.fileparts,self)
        finally:
            self.textEditBrowsing=False
        if self.textEditor is None or self.textEditor[0] is not widget:
            return
        if filename == '':
            widget.focus_set()
            return
        widget.delete(0,tk.END)
        widget.insert(0,filename)
        self.CommitTextEdit()
    def CommitTextEditIfUnfocused(self):
        if self.textEditor is not None and not self.textEditBrowsing:
            widget=self.textEditor[0]
            focus=self.focus_get()
            # a readonly combobox's dropdown list takes the focus while it is open
            if focus is None or not (str(focus) == str(widget) or str(focus).startswith(str(widget)+'.')
                                     or 'popdown' in str(focus)):
                self.CommitTextEdit()
    def CancelTextEdit(self):
        if self.textEditor is not None:
            frame=self.textEditor[5]
            window=self.textEditor[1]
            self.textEditor=None
            self.canvas.delete(window)
            frame.destroy()
            self.canvas.focus_set()
        return 'break'
    def CommitTextEdit(self):
        if self.textEditor is None:
            return 'break'
        from SignalIntegrity.App.ProjectFile import VariableConfiguration
        widget,window,source,device,initial,frame=self.textEditor
        string=widget.get()
        self.CancelTextEdit()
        if string == initial:
            return 'break'
        previousValue=source['Value']
        if isinstance(source,VariableConfiguration):
            if not source.SetValueFromEntryString(string):
                self.bell()
                return 'break'
            if device is not None:
                from SignalIntegrity.App.VariablesDialog import OfferToAddSystemVariable
                OfferToAddSystemVariable(source,previousValue,self)
        else:
            stripped=string.strip()
            if not stripped.startswith('='):
                valid=True
                if source['Type'] == 'int':
                    try: int(stripped)
                    except ValueError: valid=False
                elif source['Type'] == 'float':
                    from SignalIntegrity.Lib.ToSI import FromSI
                    valid=FromSI(stripped,source['Unit']) is not None
                if not valid:
                    self.bell()
                    return 'break'
            source.SetValueFromString(stripped,True)
            if source['PropertyName'] == 'waveformfilename':
                from SignalIntegrity.App.Files import FileParts
                isProject=FileParts(source.GetValue()).fileext == '.si'
                for prop in device.propertiesList:
                    if prop['PropertyName'] == 'wfprojname':
                        prop['Hidden']=not isProject
        if source['Value'] == previousValue:
            return 'break'
        if device is not None:
            device.Wf=None
            self.schematic.Consolidate()
        self.DrawSchematic()
        self.parent.history.Event('modify system variables' if device is None else 'edit device')
        self.parent.statusbar.set('System Variables Modified' if device is None else 'Part Modified')
        return 'break'
    def ViewSelectedDevice(self,action):
        if self.stateMachine.state=='DeviceSelected':
            from SignalIntegrity.App.DeviceProperties import PerformDeviceViewAction
            PerformDeviceViewAction(self.parent,self.deviceSelected,action)
    def DuplicateSelectedDevice(self):
        if self.stateMachine.state=='DeviceSelected':
            self.partLoaded=copy.deepcopy(self.deviceSelected)
            if self.partLoaded['partname'].GetValue() == 'Port':
                portNumberList=[]
                for device in self.schematic.CircuitDevices():
                    if device['partname'].GetValue() == 'Port':
                        portNumberList.append(int(device['pn'].GetValue()))
                portNumber=1
                while portNumber in portNumberList:
                    portNumber=portNumber+1
                self.partLoaded['pn'].SetValueFromString(str(portNumber))
            elif self.partLoaded['partname'].GetValue() == 'NetworkAnalyzerStimulus':
                portNumberList=[]
                for device in self.schematic.CircuitDevices():
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
        if self.stateMachine.state in ('DeviceSelected','Multiple Selections'):
            self.DuplicateMultipleSelections(False)
            self.DeleteMultipleSelections(False)
            self.stateMachine.MultipleItemsOnClipboard()
    def DuplicateSelected(self):
        if self.stateMachine.state=='Multiple Selections':
            self.DuplicateMultipleSelections()
        elif self.stateMachine.state=='DeviceSelected':
            self.DuplicateSelectedDevice()
    def DuplicateMultipleSelections(self,advanceStateMachine=True):
        if self.stateMachine.state in ('DeviceSelected','Multiple Selections'):
            self.pendingPageImport=None
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
    def InitFromProject(self,resize=True,addTabHeight=False):
        drawingProperties=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        # the canvas and geometry must be set prior to the remainder of the schematic initialization
        # otherwise it will not be the right size.  In the past, the xml happened to have the drawing
        # properties first, which made it work, but it was an accident.
        #self.canvas.config(width=drawingProperties['Width'],height=drawingProperties['Height'])
        geometry=drawingProperties['Geometry'].split('+')[0]
        if resize:
            scale=self.parent.displayScale if sys.platform.startswith('linux') else 1.0
            extraHeight=0
            if addTabHeight:
                # Measure the actual themed strip in screen pixels, after Tk has laid it out.
                self.parent.root.update_idletasks()
                extraHeight=self.parent.pageBar.winfo_reqheight()
            geometry=ScaleWindowGeometry(geometry,scale,extraHeight)
            if addTabHeight:
                # The initial history entry may be captured before the resize event arrives.
                drawingProperties['Geometry']=ScaleWindowGeometry(geometry,1.0/scale)
            self.parent.root.geometry(geometry)
        self.schematic = Schematic()
        self.schematic.InitFromProject()
        self.stateMachine = None
        self.InstallStateMachine()
        self.parent.RefreshSchematicPages()
