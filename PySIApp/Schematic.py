'''
Created on Oct 15, 2015

@author: peterp
'''
from Tkinter import *
import xml.etree.ElementTree as et

from DeviceProperties import *
from Device import *
from NetList import NetList
from Wire import *

class Schematic(object):
    def __init__(self):
        self.deviceList = []
        self.wireList = WireList()
    def xml(self):
        schematicElement=et.Element('schematic')
        deviceElement=et.Element('devices')
        deviceElementList = [device.xml() for device in self.deviceList]
        deviceElement.extend(deviceElementList)
        wiresElement=self.wireList.xml()
        schematicElement.extend([deviceElement,wiresElement])
        return schematicElement
    def InitFromXml(self,schematicElement):
        self.__init__()
        for child in schematicElement:
            if child.tag == 'devices':
                for deviceElement in child:
                    try:
                        returnedDevice=DeviceXMLClassFactory(deviceElement).result
                    except NameError: # part picture doesn't exist
                        returnedDevice=None
                    if not returnedDevice is None:
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
        self.wireList = WireList()
    def NewUniqueReferenceDesignator(self,defaultDesignator):
        if defaultDesignator != None and '?' in defaultDesignator:
            referenceDesignatorList=[]
            for device in self.deviceList:
                deviceReferenceDesignatorProperty = device[PartPropertyReferenceDesignator().propertyName]
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
                    for wire in self.wireList:
                        if thisPinConnected:
                            break
                        for vertex in wire:
                            if thisPinCoordinate == vertex.coord:
                                thisPinConnected=True
                                break
                thisDeviceConnectedList.append(thisPinConnected)
            devicePinConnectedList.append(thisDeviceConnectedList)
        return devicePinConnectedList
    def Consolidate(self):
        deviceList=self.deviceList
        self.wireList.RemoveEmptyWires()
        self.wireList.RemoveDuplicateVertices()
        self.wireList.InsertNeededVertices(deviceList)
        dotList=self.DotList()
        self.wireList.SplitDottedWires(dotList)
        self.wireList.JoinUnDottedWires(dotList)
        self.wireList.RemoveUnneededVertices()
    def DotList(self):
        dotList=[]
        # make a list of all coordinates
        coordList=[]
        for device in self.deviceList:
            coordList=coordList+device.PinCoordinates()
        for wire in self.wireList:
            vertexCoordinates=[vertex.coord for vertex in wire]
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
        self.Nothing()
    def UnselectAllDevices(self):
        for device in self.parent.schematic.deviceList:
            device.selected=False
    def UnselectAllWires(self):
        self.parent.schematic.wireList.UnselectAll()
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
        for w in range(len(self.parent.schematic.wireList)):
            for v in range(len(self.parent.schematic.wireList[w])):
                if self.parent.schematic.wireList[w][v].selected:
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
            if device.IsAt(self.parent.Button1Coord):
                selectedSomething=True
                device.selected=True
        for wire in self.parent.schematic.wireList:
            for vertex in wire:
                if vertex.IsAt(self.parent.Button1Coord):
                    selectedSomething=True
                    vertex.selected=True
        if not selectedSomething:
            for wireIndex in range(len(self.parent.schematic.wireList)):
                wire=self.parent.schematic.wireList[wireIndex]
                segmentList = SegmentList(wire)
                for segment in segmentList:
                    usingAdvancedSegmentDetection=True
                    if usingAdvancedSegmentDetection:
                        if segment.IsAtAdvanced(self.parent.Button1Coord,self.parent.Button1Augmentor,0.5):
                            segment.selected=True
                            selectedSomething=True
                            break
                    else:
                        if segment.IsAt(self.parent.Button1Coord):
                            segment.selected=True
                            selectedSomething=True
                            break
                if selectedSomething:
                    wire = segmentList.Wire()
                    self.parent.schematic.wireList[wireIndex]=wire
                    break
        self.DispatchBasedOnSelections(self.Selecting)

    def onMouseButton1TryToToggleSomething(self,event):
        self.SaveButton1Coordinates(event)
        toggledSomething=False
        for device in self.parent.schematic.deviceList:
            if device.IsAt(self.parent.Button1Coord):
                device.selected=not device.selected
                toggledSomething=True
        for wire in self.parent.schematic.wireList:
            for vertex in wire:
                if vertex.IsAt(self.parent.Button1Coord):
                    vertex.selected=not vertex.selected
                    toggledSomething=True
        if not toggledSomething:
            for wireIndex in range(len(self.parent.schematic.wireList)):
                wire=self.parent.schematic.wireList[wireIndex]
                segmentList = SegmentList(wire)
                for segment in segmentList:
                    usingAdvancedSegmentDetection=True
                    if usingAdvancedSegmentDetection:
                        if segment.IsAtAdvanced(self.parent.Button1Coord,self.parent.Button1Augmentor,0.5):
                            segment.selected=not segment.selected
                            toggledSomething=True
                            break
                    else:
                        if segment.IsAt(self.parent.Button1Coord):
                            segment.selected=not segment.selected
                            toggledSomething=True
                            break
                if toggledSomething:
                    wire = segmentList.Wire()
                    self.parent.schematic.wireList[wireIndex]=wire
                    break
        if toggledSomething:
            self.parent.DrawSchematic()
            self.DispatchBasedOnSelections()
            return

        self.selectedDevices = [device.selected for device in self.parent.schematic.deviceList]
        self.selectedWireVertex = [[vertex.selected for vertex in wire] for wire in self.parent.schematic.wireList]
        self.SelectingMore()

    def Nothing(self,force=False):
        if not hasattr(self,'state'):
            self.state=''
        if self.state != 'Nothing' or force:
            self.parent.canvas.config(cursor='left_ptr')
            self.state='Nothing'
            self.parent.schematic.Consolidate()
            self.UnselectAllDevices()
            self.UnselectAllWires()
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
            self.parent.parent.toolbar.rotatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Rotate Part',state='disabled')
            self.parent.parent.toolbar.flipPartHorizontallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Horizontally',state='disabled')
            self.parent.parent.toolbar.flipPartVerticallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Vertically',state='disabled')
            self.parent.parent.toolbar.deletePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Delete Part',state='disabled')
            self.parent.parent.menu.PartsMenu.entryconfigure('Edit Properties',state='disabled')
            self.parent.parent.toolbar.duplicatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Duplicate Part',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Duplicate Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Wire',state='disabled')
            self.parent.parent.toolbar.panButton.config(relief=RAISED)
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
            self.parent.parent.toolbar.rotatePartButton.config(state="normal")
            self.parent.parent.menu.PartsMenu.entryconfigure('Rotate Part',state='normal')
            self.parent.parent.toolbar.flipPartHorizontallyButton.config(state="normal")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Horizontally',state='normal')
            self.parent.parent.toolbar.flipPartVerticallyButton.config(state="normal")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Vertically',state='normal')
            self.parent.parent.toolbar.deletePartButton.config(state="normal")
            self.parent.parent.menu.PartsMenu.entryconfigure('Delete Part',state='normal')
            self.parent.parent.menu.PartsMenu.entryconfigure('Edit Properties',state='normal')
            self.parent.parent.toolbar.duplicatePartButton.config(state="normal")
            self.parent.parent.menu.PartsMenu.entryconfigure('Duplicate Part',state='normal')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Duplicate Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Wire',state='disabled')
            self.parent.parent.toolbar.panButton.config(relief=RAISED)
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
        if not self.parent.deviceSelected.IsAt(self.parent.Button2Coord):
            self.Nothing()
    def onMouseButton1Motion_DeviceSelected(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.deviceSelected.partPicture.current.SetOrigin([coord[0]-self.parent.coordInPart[0],coord[1]-self.parent.coordInPart[1]])
        self.parent.DrawSchematic()
    def onMouseButton1Release_DeviceSelected(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.deviceSelected.partPicture.current.SetOrigin([coord[0]-self.parent.coordInPart[0],coord[1]-self.parent.coordInPart[1]])
        self.parent.schematic.Consolidate()
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
            for w in range(len(self.parent.schematic.wireList)):
                for v in range(len(self.parent.schematic.wireList[w])):
                    if self.parent.schematic.wireList[w][v].selected:
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
            self.parent.parent.toolbar.rotatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Rotate Part',state='disabled')
            self.parent.parent.toolbar.flipPartHorizontallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Horizontally',state='disabled')
            self.parent.parent.toolbar.flipPartVerticallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Vertically',state='disabled')
            self.parent.parent.toolbar.deletePartButton.config(state="normal")
            self.parent.parent.menu.PartsMenu.entryconfigure('Delete Part',state='disabled')
            self.parent.parent.menu.PartsMenu.entryconfigure('Edit Properties',state='disabled')
            self.parent.parent.toolbar.duplicatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Duplicate Part',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Vertex',state='normal')
            self.parent.parent.menu.WireMenu.entryconfigure('Duplicate Vertex',state='normal')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Wire',state='normal')
            self.parent.parent.toolbar.panButton.config(relief=RAISED)
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
        self.parent.schematic.wireList[self.parent.w][self.parent.v].coord = coord
        self.parent.DrawSchematic()
    def onMouseButton1Release_WireSelected(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.schematic.wireList[self.parent.w][self.parent.v].coord = coord
        self.parent.schematic.Consolidate()
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
            self.parent.parent.toolbar.rotatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Rotate Part',state='disabled')
            self.parent.parent.toolbar.flipPartHorizontallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Horizontally',state='disabled')
            self.parent.parent.toolbar.flipPartVerticallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Vertically',state='disabled')
            self.parent.parent.toolbar.deletePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Delete Part',state='disabled')
            self.parent.parent.menu.PartsMenu.entryconfigure('Edit Properties',state='disabled')
            self.parent.parent.toolbar.duplicatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Duplicate Part',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Duplicate Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Wire',state='disabled')
            self.parent.parent.toolbar.panButton.config(relief=RAISED)
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
            self.parent.parent.toolbar.rotatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Rotate Part',state='disabled')
            self.parent.parent.toolbar.flipPartHorizontallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Horizontally',state='disabled')
            self.parent.parent.toolbar.flipPartVerticallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Vertically',state='disabled')
            self.parent.parent.toolbar.deletePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Delete Part',state='disabled')
            self.parent.parent.menu.PartsMenu.entryconfigure('Edit Properties',state='disabled')
            self.parent.parent.toolbar.duplicatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Duplicate Part',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Duplicate Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Wire',state='disabled')
            self.parent.parent.toolbar.panButton.config(relief=RAISED)
            self.parent.parent.statusbar.set('Drawing Wires')
            self.parent.DrawSchematic()
    def onMouseButton1_WireLoaded(self,event):
        self.SaveButton1Coordinates(event)
        self.parent.wireLoaded[-1]=Vertex(self.parent.Button1Coord)
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
        if len(self.parent.wireLoaded) > 0:
            self.parent.wireLoaded[-1] = Vertex(coord)
            self.parent.DrawSchematic()
    def onMouseButton1Release_WireLoaded(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.wireLoaded.append(Vertex(coord))
        self.parent.DrawSchematic()
    def onMouseButton3Release_WireLoaded(self,event):
        self.SaveButton2Coordinates(event)
        if len(self.parent.wireLoaded) > 2:
            self.parent.schematic.wireList[-1]=Wire(self.parent.wireLoaded[:-1])
            self.parent.wireLoaded=Wire([Vertex((0,0))])
            self.parent.schematic.wireList.append(self.parent.wireLoaded)
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
            self.parent.wireLoaded[-1]=Vertex(coord)
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
            self.parent.parent.toolbar.rotatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Rotate Part',state='disabled')
            self.parent.parent.toolbar.flipPartHorizontallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Horizontally',state='disabled')
            self.parent.parent.toolbar.flipPartVerticallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Vertically',state='disabled')
            self.parent.parent.toolbar.deletePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Delete Part',state='disabled')
            self.parent.parent.menu.PartsMenu.entryconfigure('Edit Properties',state='disabled')
            self.parent.parent.toolbar.duplicatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Duplicate Part',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Duplicate Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Wire',state='disabled')
            self.parent.parent.toolbar.panButton.config(relief=SUNKEN)
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
            self.parent.parent.toolbar.rotatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Rotate Part',state='disabled')
            self.parent.parent.toolbar.flipPartHorizontallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Horizontally',state='disabled')
            self.parent.parent.toolbar.flipPartVerticallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Vertically',state='disabled')
            self.parent.parent.toolbar.deletePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Delete Part',state='disabled')
            self.parent.parent.menu.PartsMenu.entryconfigure('Edit Properties',state='disabled')
            self.parent.parent.toolbar.duplicatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Duplicate Part',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Duplicate Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Wire',state='disabled')
            self.parent.parent.toolbar.panButton.config(relief=RAISED)
            self.parent.parent.statusbar.set('Selecting')
            self.parent.DrawSchematic()
    def onMouseButton1_Selecting(self,event):
        self.SaveButton1Coordinates(event)
    def onCtrlMouseButton1_Selecting(self,event):
        self.SaveButton1Coordinates(event)
    def onCtrlMouseButton1Motion_Selecting(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.UnselectAllDevices()
        self.UnselectAllWires()
        for device in self.parent.schematic.deviceList:
            if device.IsIn(coord,self.parent.Button1Coord):
                device.selected=True
        for wire in self.parent.schematic.wireList:
            for vertex in wire:
                if vertex.IsIn(coord,self.parent.Button1Coord):
                    vertex.selected=True
        self.parent.DrawSchematic()
        self.parent.canvas.create_rectangle((self.parent.Button1Coord[0]+self.parent.originx)*self.parent.grid,
                                            (self.parent.Button1Coord[1]+self.parent.originy)*self.parent.grid,
                                            (coord[0]+self.parent.originx)*self.parent.grid,
                                            (coord[1]+self.parent.originy)*self.parent.grid,
                                            dash=(1,5))
    def onCtrlMouseButton1Release_Selecting(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.UnselectAllDevices()
        self.UnselectAllWires()
        for device in self.parent.schematic.deviceList:
            if device.IsIn(coord,self.parent.Button1Coord):
                device.selected=True
        for wire in self.parent.schematic.wireList:
            for vertex in wire:
                if vertex.IsIn(coord,self.parent.Button1Coord):
                    vertex.selected=True
        self.DispatchBasedOnSelections()
    def onMouseButton3_Selecting(self,event):
        pass
    def onMouseButton1Motion_Selecting(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.UnselectAllDevices()
        self.UnselectAllWires()
        for device in self.parent.schematic.deviceList:
            if device.IsIn(coord,self.parent.Button1Coord):
                device.selected=True
        for wire in self.parent.schematic.wireList:
            for vertex in wire:
                if vertex.IsIn(coord,self.parent.Button1Coord):
                    vertex.selected=True
        self.parent.DrawSchematic()
        self.parent.canvas.create_rectangle((self.parent.Button1Coord[0]+self.parent.originx)*self.parent.grid,
                                            (self.parent.Button1Coord[1]+self.parent.originy)*self.parent.grid,
                                            (coord[0]+self.parent.originx)*self.parent.grid,
                                            (coord[1]+self.parent.originy)*self.parent.grid,
                                            dash=(1,5))
    def onMouseButton1Release_Selecting(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.UnselectAllDevices()
        self.UnselectAllWires()
        for device in self.parent.schematic.deviceList:
            if device.IsIn(coord,self.parent.Button1Coord):
                device.selected=True
        for wire in self.parent.schematic.wireList:
            for vertex in wire:
                if vertex.IsIn(coord,self.parent.Button1Coord):
                    vertex.selected=True
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
            self.parent.OriginalWireCoordinates = [[(self.parent.Button1Coord[0]-vertex[0],
                                                     self.parent.Button1Coord[1]-vertex[1]) for vertex in wire] for wire in self.parent.schematic.wireList]
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
            self.parent.parent.toolbar.rotatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Rotate Part',state='disabled')
            self.parent.parent.toolbar.flipPartHorizontallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Horizontally',state='disabled')
            self.parent.parent.toolbar.flipPartVerticallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Vertically',state='disabled')
            self.parent.parent.toolbar.deletePartButton.config(state="normal")
            self.parent.parent.menu.PartsMenu.entryconfigure('Delete Part',state='disabled')
            self.parent.parent.menu.PartsMenu.entryconfigure('Edit Properties',state='disabled')
            self.parent.parent.toolbar.duplicatePartButton.config(state="normal")
            self.parent.parent.menu.PartsMenu.entryconfigure('Duplicate Part',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Duplicate Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Wire',state='disabled')
            self.parent.parent.toolbar.panButton.config(relief=RAISED)
            self.parent.parent.statusbar.set('Multiple Selections')
            self.parent.DrawSchematic()
    def onMouseButton1_MultipleSelections(self,event):
        self.SaveButton1Coordinates(event)
        self.parent.OriginalDeviceCoordinates = [device.WhereInPart(self.parent.Button1Coord) for device in self.parent.schematic.deviceList]
        self.parent.OriginalWireCoordinates = [[(self.parent.Button1Coord[0]-vertex[0],
                                                 self.parent.Button1Coord[1]-vertex[1]) for vertex in wire] for wire in self.parent.schematic.wireList]
        inSelection=False
        for device in self.parent.schematic.deviceList:
            if device.IsAt(self.parent.Button1Coord) and device.selected:
                inSelection=True
                break
        for wire in self.parent.schematic.wireList:
            for vertex in wire:
                if vertex.IsAt(self.parent.Button1Coord) and vertex.selected:
                    inSelection=True
                    break
        if not inSelection:
            for wireIndex in range(len(self.parent.schematic.wireList)):
                wire=self.parent.schematic.wireList[wireIndex]
                segmentList = SegmentList(wire)
                for segment in segmentList:
                    usingAdvancedSegmentDetection=True
                    if usingAdvancedSegmentDetection:
                        if segment.IsAtAdvanced(self.parent.Button1Coord,self.parent.Button1Augmentor,0.5) and segment.selected:
                            inSelection=True
                            break
                    else:
                        if segment.IsAt(self.parent.Button1Coord) and segment.selected:
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
        for w in range(len(self.parent.schematic.wireList)):
            for v in range(len(self.parent.schematic.wireList[w])):
                if self.parent.schematic.wireList[w][v].selected:
                    self.parent.schematic.wireList[w][v].coord=(coord[0]-self.parent.OriginalWireCoordinates[w][v][0],
                                                          coord[1]-self.parent.OriginalWireCoordinates[w][v][1])
        self.parent.DrawSchematic()
    def onMouseButton1Release_MultipleSelections(self,event):
        self.parent.schematic.Consolidate()
        self.parent.DrawSchematic()
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
            self.parent.parent.toolbar.rotatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Rotate Part',state='disabled')
            self.parent.parent.toolbar.flipPartHorizontallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Horizontally',state='disabled')
            self.parent.parent.toolbar.flipPartVerticallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Vertically',state='disabled')
            self.parent.parent.toolbar.deletePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Delete Part',state='disabled')
            self.parent.parent.menu.PartsMenu.entryconfigure('Edit Properties',state='disabled')
            self.parent.parent.toolbar.duplicatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Duplicate Part',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Duplicate Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Wire',state='disabled')
            self.parent.parent.toolbar.panButton.config(relief=RAISED)
            self.parent.parent.statusbar.set('Selecting More')
            self.parent.DrawSchematic()
    def onMouseButton1_SelectingMore(self,event):
        self.SaveButton1Coordinates(event)
    def onCtrlMouseButton1_SelectingMore(self,event):
        self.SaveButton1Coordinates(event)
    def onCtrlMouseButton1Motion_SelectingMore(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.UnselectAllDevices()
        self.UnselectAllWires()
        for d in range(len(self.parent.schematic.deviceList)):
            device=self.parent.schematic.deviceList[d]
            if device.IsIn(coord,self.parent.Button1Coord) or self.selectedDevices[d]:
                device.selected=True
        for w in range(len(self.parent.schematic.wireList)):
            for v in range(len(self.parent.schematic.wireList[w])):
                if self.parent.schematic.wireList[w][v].IsIn(coord,self.parent.Button1Coord) or self.selectedWireVertex[w][v]:
                    self.parent.schematic.wireList[w][v].selected=True
        self.parent.DrawSchematic()
        self.parent.canvas.create_rectangle((self.parent.Button1Coord[0]+self.parent.originx)*self.parent.grid,
                                            (self.parent.Button1Coord[1]+self.parent.originy)*self.parent.grid,
                                            (coord[0]+self.parent.originx)*self.parent.grid,
                                            (coord[1]+self.parent.originy)*self.parent.grid,
                                            dash=(1,5))
    def onCtrlMouseButton1Release_SelectingMore(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.UnselectAllDevices()
        self.UnselectAllWires()
        for d in range(len(self.parent.schematic.deviceList)):
            device=self.parent.schematic.deviceList[d]
            if device.IsIn(coord,self.parent.Button1Coord) or self.selectedDevices[d]:
                device.selected=True
        for w in range(len(self.parent.schematic.wireList)):
            for v in range(len(self.parent.schematic.wireList[w])):
                vertex = self.parent.schematic.wireList[w][v]
                if vertex.IsIn(coord,self.parent.Button1Coord) or self.selectedWireVertex[w][v]:
                    vertex.selected=True
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
            self.parent.parent.toolbar.rotatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Rotate Part',state='disabled')
            self.parent.parent.toolbar.flipPartHorizontallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Horizontally',state='disabled')
            self.parent.parent.toolbar.flipPartVerticallyButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Flip Vertically',state='disabled')
            self.parent.parent.toolbar.deletePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Delete Part',state='disabled')
            self.parent.parent.menu.PartsMenu.entryconfigure('Edit Properties',state='disabled')
            self.parent.parent.toolbar.duplicatePartButton.config(state="disabled")
            self.parent.parent.menu.PartsMenu.entryconfigure('Duplicate Part',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Duplicate Vertex',state='disabled')
            self.parent.parent.menu.WireMenu.entryconfigure('Delete Wire',state='disabled')
            self.parent.parent.toolbar.panButton.config(relief=RAISED)
            self.parent.parent.statusbar.set('Multiple Items in Clipboard')
            self.parent.DrawSchematic()
    def onMouseButton1_MultipleItemsOnClipboard(self,event):
        self.UnselectAllDevices()
        self.UnselectAllWires()
        self.SaveButton1Coordinates(event)
        for device in self.parent.devicesToDuplicate:
            if device['type'].GetValue() == 'Port':
                portNumberList=[]
                for existingDevice in self.parent.schematic.deviceList:
                    if existingDevice['type'].GetValue() == 'Port':
                        portNumberList.append(int(existingDevice['portnumber'].GetValue()))
                if device['portnumber'].GetValue() in portNumberList:
                    portNumber=1
                    while portNumber in portNumberList:
                        portNumber=portNumber+1
                    device['portnumber'].SetValueFromString(str(portNumber))
            else:
                existingReferenceDesignators=[]
                for existingDevice in self.parent.schematic.deviceList:
                    referenceDesignatorProperty = existingDevice[PartPropertyReferenceDesignator().propertyName]
                    if referenceDesignatorProperty != None:
                        existingReferenceDesignators.append(referenceDesignatorProperty.GetValue())
                if device[PartPropertyReferenceDesignator().propertyName].GetValue() in existingReferenceDesignators:
                    defaultProperty = device[PartPropertyDefaultReferenceDesignator().propertyName]
                    if defaultProperty != None:
                        defaultPropertyValue = defaultProperty.GetValue()
                        uniqueReferenceDesignator = self.parent.schematic.NewUniqueReferenceDesignator(defaultPropertyValue)
                        if uniqueReferenceDesignator != None:
                            device[PartPropertyReferenceDesignator().propertyName].SetValueFromString(uniqueReferenceDesignator)
            device.partPicture.current.SetOrigin((device.partPicture.current.origin[0]+self.parent.Button1Coord[0],device.partPicture.current.origin[1]+self.parent.Button1Coord[1]))
            device.selected=True
            self.parent.schematic.deviceList.append(device)
        for wire in self.parent.wiresToDuplicate:
            for vertex in wire:
                vertex.selected=True
                vertex.coord=(vertex.coord[0]+self.parent.Button1Coord[0],vertex.coord[1]++self.parent.Button1Coord[1])
            self.parent.schematic.wireList.append(wire)

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
        for deviceIndex in range(len(self.schematic.deviceList)):
            device = self.schematic.deviceList[deviceIndex]
            foundSomething=True
            devicePinsConnected=devicePinConnectedList[deviceIndex]
            device.DrawDevice(canvas,self.grid,self.originx,self.originy,devicePinsConnected)
            deviceType = device['type'].GetValue()
            if  deviceType == 'Port':
                foundAPort = True
            elif deviceType == 'Output':
                foundAnOutput = True
            else:
                netListLine = device.NetListLine()
                if not netListLine is None:
                    firstToken=netListLine.strip().split(' ')[0]
                    if firstToken == 'voltagesource':
                        foundASource = True
                    elif firstToken == 'currentsource':
                        foundASource = True
        for wire in self.schematic.wireList:
            foundSomething=True
            wire.DrawWire(canvas,self.grid,self.originx,self.originy)
        for dot in self.schematic.DotList():
            size=self.grid/8
            canvas.create_oval((dot[0]+self.originx)*self.grid-size,(dot[1]+self.originy)*self.grid-size,
                                    (dot[0]+self.originx)*self.grid+size,(dot[1]+self.originy)*self.grid+size,
                                    fill='black',outline='black')
        canSimulate = foundASource and foundAnOutput and not foundAPort
        canCalculateSParameters = foundAPort and not foundAnOutput
        canCalculate = canSimulate or canCalculateSParameters
        self.parent.menu.CalcMenu.entryconfigure('Simulate',state='normal' if canSimulate else 'disabled')
        self.parent.toolbar.calculateButton.config(state='normal' if canCalculate else 'disabled')
        self.parent.menu.CalcMenu.entryconfigure('Calculate S-parameters',state='normal' if canCalculateSParameters else 'disabled')
        self.parent.menu.FileMenu.entryconfigure('Save Project',state='normal' if foundSomething else 'disabled')
        self.parent.menu.FileMenu.entryconfigure('Clear Schematic',state='normal' if foundSomething else 'disabled')
        self.parent.menu.FileMenu.entryconfigure('Export NetList',state='normal' if foundSomething else 'disabled')
        self.parent.menu.FileMenu.entryconfigure('Export LaTeX (TikZ)',state='normal' if foundSomething else 'disabled')
        return canvas
    def EditSelectedDevice(self):
        if self.stateMachine.state=='DeviceSelected':
            dpe=DevicePropertiesDialog(self,self.deviceSelected)
            if dpe.result != None:
                self.deviceSelected = dpe.result
                self.schematic.deviceList[self.deviceSelectedIndex] = self.deviceSelected
                self.schematic.Consolidate()
                self.DrawSchematic()
                self.parent.history.Event('edit device')
    def DuplicateSelectedDevice(self):
        if self.stateMachine.state=='DeviceSelected':
            self.partLoaded=copy.deepcopy(self.deviceSelected)
            if self.partLoaded['type'].GetValue() == 'Port':
                portNumberList=[]
                for device in self.schematic.deviceList:
                    if device['type'].GetValue() == 'Port':
                        portNumberList.append(int(device['portnumber'].GetValue()))
                portNumber=1
                while portNumber in portNumberList:
                    portNumber=portNumber+1
                self.partLoaded['portnumber'].SetValueFromString(str(portNumber))
            else:
                defaultProperty = self.partLoaded[PartPropertyDefaultReferenceDesignator().propertyName]
                if defaultProperty != None:
                    defaultPropertyValue = defaultProperty.GetValue()
                    uniqueReferenceDesignator = self.schematic.NewUniqueReferenceDesignator(defaultPropertyValue)
                    if uniqueReferenceDesignator != None:
                        self.partLoaded[PartPropertyReferenceDesignator().propertyName].SetValueFromString(uniqueReferenceDesignator)
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
        del self.schematic.wireList[self.w][self.v]
        self.stateMachine.Nothing()
        self.parent.history.Event('delete vertex')
    def DuplicateSelectedVertex(self):
        vertex=copy.deepcopy(self.schematic.wireList[self.w][self.v])
        self.schematic.wireList.UnselectAll()
        self.schematic.wireList[self.w]=Wire(self.schematic.wireList[self.w][:self.v]+\
        [vertex]+\
        self.schematic.wireList[self.w][self.v:])
        self.stateMachine.WireSelected()
    def DeleteSelectedWire(self):
        del self.schematic.wireList[self.w]
        self.stateMachine.Nothing()
        self.parent.history.Event('delete wire')
    def DeleteMultipleSelections(self,advanceStateMachine=True):
        newDeviceList=[]
        newWireList=WireList()
        for device in self.schematic.deviceList:
            if not device.selected:
                newDeviceList.append(copy.deepcopy(device))
        for wire in self.schematic.wireList:
            newWire=Wire()
            for vertex in wire:
                if not vertex.selected:
                    newWire.append(copy.deepcopy(vertex))
            if len(newWire) >= 2:
                newWireList.append(copy.deepcopy(newWire))
        self.schematic.deviceList=newDeviceList
        self.schematic.wireList=newWireList
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
            self.wiresToDuplicate=WireList()
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
            for wire in self.schematic.wireList:
                newWire=Wire()
                numVerticesSelected = 0
                firstVertexSelected = -1
                lastVertexSelected=-1
                for vertexIndex in range(len(wire)):
                    if wire[vertexIndex].selected:
                        numVerticesSelected=numVerticesSelected+1
                        if firstVertexSelected == -1:
                            firstVertexSelected = vertexIndex
                        lastVertexSelected = vertexIndex
                if numVerticesSelected >= 2:
                    for vertexIndex in range(len(wire)):
                        if vertexIndex >= firstVertexSelected and vertexIndex <= lastVertexSelected:
                            vertex=wire[vertexIndex]
                            newWire.append(copy.deepcopy(vertex))
                            if not originSet:
                                originSet=True
                                originx=vertex.coord[0]
                                originy=vertex.coord[1]
                            else:
                                originx=min(originx,vertex.coord[0])
                                originy=min(originy,vertex.coord[1])
                if len(newWire) >= 2:
                    self.wiresToDuplicate.append(newWire)
            if not originSet:
                return
            # originx and originy are the upper leftmost coordinates in the selected stuff
            for device in self.devicesToDuplicate:
                device.partPicture.current.SetOrigin((device.partPicture.current.origin[0]-originx,device.partPicture.current.origin[1]-originy))
            for wire in self.wiresToDuplicate:
                for vertex in wire:
                    vertex.coord=((vertex.coord[0]-originx,vertex.coord[1]-originy))
            if advanceStateMachine:
                self.stateMachine.MultipleItemsOnClipboard()
    def xml(self):
        drawingElement=et.Element('drawing')
        drawingPropertiesElement=et.Element('drawing_properties')
        drawingPropertiesElementList=[]
        drawingProperty=et.Element('grid')
        drawingProperty.text=str(self.grid)
        drawingPropertiesElementList.append(drawingProperty)
        drawingProperty=et.Element('originx')
        drawingProperty.text=str(self.originx)
        drawingPropertiesElementList.append(drawingProperty)
        drawingProperty=et.Element('originy')
        drawingProperty.text=str(self.originy)
        drawingPropertiesElementList.append(drawingProperty)
        drawingProperty=et.Element('width')
        drawingProperty.text=str(self.canvas.winfo_width())
        drawingPropertiesElementList.append(drawingProperty)
        drawingProperty=et.Element('height')
        drawingProperty.text=str(self.canvas.winfo_height())
        drawingPropertiesElementList.append(drawingProperty)
        drawingProperty=et.Element('geometry')
        drawingProperty.text=self.parent.root.geometry()
        drawingPropertiesElementList.append(drawingProperty)
        drawingPropertiesElement.extend(drawingPropertiesElementList)
        schematicPropertiesElement=self.schematic.xml()
        drawingElement.extend([drawingPropertiesElement,schematicPropertiesElement])
        return drawingElement
    def InitFromXml(self,drawingElement):
        self.grid=32
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
                        self.grid = int(drawingPropertyElement.text)
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