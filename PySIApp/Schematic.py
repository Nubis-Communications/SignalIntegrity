'''
Created on Oct 15, 2015

@author: peterp
'''
from Tkinter import *
import xml.etree.ElementTree as et

from DeviceProperties import *
from Device import *

class NetList(object):
    def __init__(self,schematic):
        self.textToShow=[]
        self.outputNames=[]
        self.measureNames=[]
        deviceList = schematic.deviceList
        wireList = schematic.wireList
        # put all devices in the net list
        for device in deviceList:
            deviceType = device[PartPropertyPartName().propertyName].GetValue()
            if  not ((deviceType == 'Port') or (deviceType == 'Measure') or (deviceType == 'Output')):
                thisline=device.NetListLine()
                self.textToShow.append(thisline)
        # gather up all device pin coordinates
        devicePinCoordinateList = [device.PinCoordinates() for device in deviceList]
        devicePinNeedToCheckList = [[True for pinIndex in range(len(devicePinCoordinateList[deviceIndex]))] for deviceIndex in range(len(devicePinCoordinateList))]
        deviceConnectionList = []
        for deviceIndex in range(len(devicePinCoordinateList)):
            devicePinConnectionList = []
            for pinIndex in range(len(devicePinCoordinateList[deviceIndex])):
                thisDevicePinCoordinate = devicePinCoordinateList[deviceIndex][pinIndex]
                thisListOfConnectedDevicePins=[]
                if devicePinNeedToCheckList[deviceIndex][pinIndex]:
                    # search all device pins and wire vertices for this coordinate
                    for deviceCheckIndex in range(len(devicePinCoordinateList)):
                        for pinCheckIndex in range(len(devicePinCoordinateList[deviceCheckIndex])):
                            thisDevicePinCheckCoordinate = devicePinCoordinateList[deviceCheckIndex][pinCheckIndex]
                            if thisDevicePinCoordinate == thisDevicePinCheckCoordinate:
                                thisListOfConnectedDevicePins.append((deviceCheckIndex,pinCheckIndex))
                    for wire in wireList:
                        thisWireConnectedToThisDevicePin = False
                        for vertex in wire:
                            if vertex == thisDevicePinCoordinate:
                                thisWireConnectedToThisDevicePin = True
                                break
                        if thisWireConnectedToThisDevicePin:
                            for vertex in wire:
                                for deviceCheckIndex in range(len(devicePinCoordinateList)):
                                    for pinCheckIndex in range(len(devicePinCoordinateList[deviceCheckIndex])):
                                        thisDevicePinCheckCoordinate = devicePinCoordinateList[deviceCheckIndex][pinCheckIndex]
                                        if vertex == thisDevicePinCheckCoordinate:
                                            thisListOfConnectedDevicePins.append((deviceCheckIndex,pinCheckIndex))
                    thisListOfConnectedDevicePins=list(set(thisListOfConnectedDevicePins))
                    for connectedDevicePins in thisListOfConnectedDevicePins:
                        connectedDeviceIndex=connectedDevicePins[0]
                        connectedPinIndex=connectedDevicePins[1]
                        devicePinNeedToCheckList[connectedDeviceIndex][connectedPinIndex]=False
                devicePinConnectionList.append(thisListOfConnectedDevicePins)
            deviceConnectionList.append(devicePinConnectionList)
        netList = []
        for deviceConnection in deviceConnectionList:
            for devicePinConnection in deviceConnection:
                if len(devicePinConnection) > 1:
                    netList.append(devicePinConnection)
        for net in netList:
            measureList=[]
            outputList=[]
            portList=[]
            # gather up list of all measures, outputs, and ports
            for devicePin in net:
                deviceIndex=devicePin[0]
                pinIndex=devicePin[1]
                thisDevice=schematic.deviceList[deviceIndex]
                thisDevicePartName = thisDevice[PartPropertyPartName().propertyName].GetValue()
                if thisDevicePartName == 'Port':
                    portList.append(devicePin)
                elif thisDevicePartName == 'Output':
                    outputList.append(devicePin)
                elif thisDevicePartName == 'Measure':
                    outputList.append(devicePin)
            #remove all of the ports, outputs and measures from the net
            net = list(set(net)-set(measureList)-set(portList)-set(outputList))
            if len(net) > 0:
                # for the measures, outputs and ports, we just need one device/port, so we use the first one
                deviceIndexOfFirstDeviceInNet = net[0][0]
                pinIndexOfFirstDeviceInNet = net[0][1]
                firstDeviceName = schematic.deviceList[deviceIndexOfFirstDeviceInNet][PartPropertyReferenceDesignator().propertyName].GetValue()
                firstDevicePinNumber = schematic.deviceList[deviceIndexOfFirstDeviceInNet].partPicture.current.pinList[pinIndexOfFirstDeviceInNet].pinNumber
                devicePinString = firstDeviceName + ' ' + str(firstDevicePinNumber)
                for measure in measureList:
                    deviceIndex = measure[0]
                    self.textToShow.append(schematic.deviceList[deviceIndex].NetListLine() + ' ' + devicePinString)
                for output in outputList:
                    deviceIndex = output[0]
                    self.textToShow.append(schematic.deviceList[deviceIndex].NetListLine() + ' ' + devicePinString)
                    self.outputNames.append(schematic.deviceList[deviceIndex][PartPropertyReferenceDesignator().propertyName].GetValue())
                for port in portList:
                    deviceIndex = port[0]
                    self.textToShow.append(schematic.deviceList[deviceIndex].NetListLine() + ' ' + devicePinString)
            if len(net) > 1:
                # list the connections
                thisConnectionString = 'connect'
                for devicePortIndex in net:
                    deviceIndex = devicePortIndex[0]
                    pinIndex = devicePortIndex[1]
                    deviceName = schematic.deviceList[deviceIndex][PartPropertyReferenceDesignator().propertyName].GetValue()
                    pinNumber = schematic.deviceList[deviceIndex].partPicture.current.pinList[pinIndex].pinNumber
                    thisConnectionString = thisConnectionString + ' '+ str(deviceName) +' '+str(pinNumber)
                self.textToShow.append(thisConnectionString)
    def Text(self):
        return self.textToShow
    def OutputNames(self):
        return self.outputNames


class Wire(object):
    def __init__(self,vertexList=None,selected=False):
        if vertexList==None:
            vertexList=[]
        self.vertexList=vertexList
        self.selected=selected
    def __getitem__(self,item):
        return self.vertexList[item]
    def __setitem__(self,item,value):
        self.vertexList[item]=value
    def __delitem__(self,item):
        del self.vertexList[item]
    def __len__(self):
        return len(self.vertexList)
    def append(self,item):
        self.vertexList.append(item)
    def reverse(self):
        self.vertexList.reverse()
    def DrawWire(self,canvas,grid,x,y):
        if len(self) >= 2:
            segmentCoord=self[0]
            for vertex in self[1:]:
                canvas.create_line((segmentCoord[0]+x)*grid,(segmentCoord[1]+y)*grid,(vertex[0]+x)*grid,(vertex[1]+y)*grid,fill=('blue' if self.selected else 'black'))
                segmentCoord=vertex
            if self.selected:
                for vertex in self:
                    size=max(1,grid/8)
                    canvas.create_line((vertex[0]+x)*grid-size,(vertex[1]+y)*grid-size,(vertex[0]+x)*grid+size,(vertex[1]+y)*grid+size,fill=('blue' if self.selected else 'black'))
                    canvas.create_line((vertex[0]+x)*grid+size,(vertex[1]+y)*grid-size,(vertex[0]+x)*grid-size,(vertex[1]+y)*grid+size,fill=('blue' if self.selected else 'black'))
    def __add__(self,other):
        if isinstance(other, Wire):
            return Wire(self.vertexList+other.vertexList,self.selected)
        elif isinstance(other,list):
            return Wire(self.vertexList+other,self.selected)

class Schematic(object):
    def __init__(self):
        self.deviceList = []
        self.wireList = []
    def xml(self):
        schematicElement=et.Element('schematic')
        deviceElement=et.Element('devices')
        deviceElementList = [device.xml() for device in self.deviceList]
        deviceElement.extend(deviceElementList)
        wiresElement=et.Element('wires')
        wireElements=[]
        for wire in self.wireList:
            wireElement=et.Element('wire')
            vertexElements=[]
            for vertex in wire:
                vertexElement=et.Element('vertex')
                vertexElement.text=str(vertex)
                vertexElements.append(vertexElement)
            wireElement.extend(vertexElements)
            wireElements.append(wireElement)
        wiresElement.extend(wireElements)
        schematicElement.extend([deviceElement,wiresElement])
        return schematicElement
    def InitFromXml(self,schematicElement):
        for child in schematicElement:
            if child.tag == 'devices':
                for deviceElement in child:
                    returnedDevice=DeviceXMLClassFactory(deviceElement).result
                    if not returnedDevice is None:
                        self.deviceList.append(returnedDevice)
            elif child.tag == 'wires':
                for wireElement in child:
                    wire=Wire()
                    for vertexElement in wireElement:
                        wire.append(eval(vertexElement.text))
                    self.wireList.append(wire)
    def NetList(self):
        self.ConsolidateWires()
        return NetList(self)
        textToShow=[]
        deviceList = self.deviceList
        wireList = self.wireList
        # put all devices in the net list
        for device in deviceList:
            deviceType = device[PartPropertyPartName().propertyName].GetValue()
            if  not ((deviceType == 'Port') or (deviceType == 'Measure') or (deviceType == 'Output')):
                thisline=device.NetListLine()
                textToShow.append(thisline)
        # gather up all device pin coordinates
        devicePinCoordinateList = [device.PinCoordinates() for device in deviceList]
        devicePinNeedToCheckList = [[True for pinIndex in range(len(devicePinCoordinateList[deviceIndex]))] for deviceIndex in range(len(devicePinCoordinateList))]
        deviceConnectionList = []
        for deviceIndex in range(len(devicePinCoordinateList)):
            devicePinConnectionList = []
            for pinIndex in range(len(devicePinCoordinateList[deviceIndex])):
                thisDevicePinCoordinate = devicePinCoordinateList[deviceIndex][pinIndex]
                thisListOfConnectedDevicePins=[]
                if devicePinNeedToCheckList[deviceIndex][pinIndex]:
                    # search all device pins and wire vertices for this coordinate
                    for deviceCheckIndex in range(len(devicePinCoordinateList)):
                        for pinCheckIndex in range(len(devicePinCoordinateList[deviceCheckIndex])):
                            thisDevicePinCheckCoordinate = devicePinCoordinateList[deviceCheckIndex][pinCheckIndex]
                            if thisDevicePinCoordinate == thisDevicePinCheckCoordinate:
                                thisListOfConnectedDevicePins.append((deviceCheckIndex,pinCheckIndex))
                    for wire in wireList:
                        thisWireConnectedToThisDevicePin = False
                        for vertex in wire:
                            if vertex == thisDevicePinCoordinate:
                                thisWireConnectedToThisDevicePin = True
                                break
                        if thisWireConnectedToThisDevicePin:
                            for vertex in wire:
                                for deviceCheckIndex in range(len(devicePinCoordinateList)):
                                    for pinCheckIndex in range(len(devicePinCoordinateList[deviceCheckIndex])):
                                        thisDevicePinCheckCoordinate = devicePinCoordinateList[deviceCheckIndex][pinCheckIndex]
                                        if vertex == thisDevicePinCheckCoordinate:
                                            thisListOfConnectedDevicePins.append((deviceCheckIndex,pinCheckIndex))
                    thisListOfConnectedDevicePins=list(set(thisListOfConnectedDevicePins))
                    for connectedDevicePins in thisListOfConnectedDevicePins:
                        connectedDeviceIndex=connectedDevicePins[0]
                        connectedPinIndex=connectedDevicePins[1]
                        devicePinNeedToCheckList[connectedDeviceIndex][connectedPinIndex]=False
                devicePinConnectionList.append(thisListOfConnectedDevicePins)
            deviceConnectionList.append(devicePinConnectionList)
        netList = []
        for deviceConnection in deviceConnectionList:
            for devicePinConnection in deviceConnection:
                if len(devicePinConnection) > 1:
                    netList.append(devicePinConnection)
        for net in netList:
            measureList=[]
            outputList=[]
            portList=[]
            # gather up list of all measures, outputs, and ports
            for devicePin in net:
                deviceIndex=devicePin[0]
                pinIndex=devicePin[1]
                thisDevice=self.deviceList[deviceIndex]
                thisDevicePartName = thisDevice[PartPropertyPartName().propertyName].GetValue()
                if thisDevicePartName == 'Port':
                    portList.append(devicePin)
                elif thisDevicePartName == 'Output':
                    outputList.append(devicePin)
                elif thisDevicePartName == 'Measure':
                    outputList.append(devicePin)
            #remove all of the ports, outputs and measures from the net
            net = list(set(net)-set(measureList)-set(portList)-set(outputList))
            if len(net) > 0:
                # for the measures, outputs and ports, we just need one device/port, so we use the first one
                deviceIndexOfFirstDeviceInNet = net[0][0]
                pinIndexOfFirstDeviceInNet = net[0][1]
                firstDeviceName = self.deviceList[deviceIndexOfFirstDeviceInNet][PartPropertyReferenceDesignator().propertyName].value
                firstDevicePinNumber = self.deviceList[deviceIndexOfFirstDeviceInNet].partPicture.current.pinList[pinIndexOfFirstDeviceInNet].pinNumber
                devicePinString = firstDeviceName + ' ' + str(firstDevicePinNumber)
                for measure in measureList:
                    deviceIndex = measure[0]
                    textToShow.append(self.deviceList[deviceIndex].NetListLine() + ' ' + devicePinString)
                for output in outputList:
                    deviceIndex = output[0]
                    textToShow.append(self.deviceList[deviceIndex].NetListLine() + ' ' + devicePinString)
                for port in portList:
                    deviceIndex = port[0]
                    textToShow.append(self.deviceList[deviceIndex].NetListLine() + ' ' + devicePinString)
            if len(net) > 1:
                # list the connections
                thisConnectionString = 'connect'
                for devicePortIndex in net:
                    deviceIndex = devicePortIndex[0]
                    pinIndex = devicePortIndex[1]
                    deviceName = self.deviceList[deviceIndex][PartPropertyReferenceDesignator().propertyName].GetValue()
                    pinNumber = self.deviceList[deviceIndex].partPicture.current.pinList[pinIndex].pinNumber
                    thisConnectionString = thisConnectionString + ' '+ str(deviceName) +' '+str(pinNumber)
                textToShow.append(thisConnectionString)
        return textToShow
    def InputWaveforms(self):
        inputWaveformList=[]
        for device in self.deviceList:
            wf = device.Waveform()
            if not wf is None:
                inputWaveformList.append(wf)
        return inputWaveformList
    def Clear(self):
        self.deviceList = []
        self.wireList = []
    def ConsolidateWires(self):
        keepDeletingWires = True
        while keepDeletingWires:
            keepDeletingWires= False
            for wireIndex in range(len(self.wireList)):
                wire = self.wireList[wireIndex]
                if len(wire) < 2:
                    del self.wireList[wireIndex]
                    keepDeletingWires=True
                    break
                else:
                    keepDeletingVertices = True
                    while keepDeletingVertices:
                        keepDeletingVertices=False
                        for vertexIndex in range(1,len(wire)):
                            thisVertex = wire[vertexIndex]
                            lastVertex = wire[vertexIndex-1]
                            if thisVertex == lastVertex:
                                del self.wireList[wireIndex][vertexIndex]
                                keepDeletingVertices = True
                                break
        # at this point, all wires have at least two coordinates and no adjacent coordinates are the same
        removeWireIndexList = [False for index in range(len(self.wireList))]
        for thisWireIndex in range(len(self.wireList)):
            if not removeWireIndexList[thisWireIndex]:
                if len(self.wireList[thisWireIndex])<2:
                    removeWireIndexList[thisWireIndex]=True
            if not removeWireIndexList[thisWireIndex]:
                for otherWireIndex in range(thisWireIndex+1,len(self.wireList)):
                    thisWireStartPoint=self.wireList[thisWireIndex][0]
                    thisWireEndPoint=self.wireList[thisWireIndex][-1]
                    if not removeWireIndexList[otherWireIndex]:
                        if len(self.wireList[otherWireIndex])<2:
                            removeWireIndexList[otherWireIndex]=True
                    if not removeWireIndexList[otherWireIndex]:
                        otherWireStartPoint=self.wireList[otherWireIndex][0]
                        otherWireEndPoint=self.wireList[otherWireIndex][-1]
                        if thisWireEndPoint == otherWireStartPoint:
                            self.wireList[thisWireIndex]=self.wireList[thisWireIndex]+self.wireList[otherWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
                        elif thisWireStartPoint == otherWireEndPoint:
                            self.wireList[thisWireIndex]=self.wireList[otherWireIndex]+self.wireList[thisWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
                        elif thisWireStartPoint == otherWireStartPoint:
                            self.wireList[otherWireIndex].reverse()
                            self.wireList[thisWireIndex]= self.wireList[otherWireIndex]+self.wireList[thisWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
                        elif thisWireEndPoint == otherWireEndPoint:
                            self.wireList[otherWireIndex].reverse()
                            self.wireList[thisWireIndex]=self.wireList[thisWireIndex]+self.wireList[otherWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True

        # remove all of the wires to be removed
        keepDeletingWires = True
        while keepDeletingWires:
            keepDeletingWires = False
            for wireIndex in range(len(self.wireList)):
                if removeWireIndexList[wireIndex]==True:
                    del self.wireList[wireIndex]
                    del removeWireIndexList[wireIndex]
                    keepDeletingWires=True
                    break
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

class DrawingStateMachine(object):
    def __init__(self,parent):
        self.parent=parent
        self.Nothing()

    def UnselectAllDevices(self):
        for device in self.parent.schematic.deviceList:
            device.selected=False
    def UnselectAllWires(self):
        for wire in self.parent.schematic.wireList:
            wire.selected=False

    def Nothing(self):
        self.parent.canvas.config(cursor='left_ptr')
        self.state='Nothing'
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
        self.parent.Button1Coord=self.parent.NearestGridCoordinate(event.x,event.y)
        for d in range(len(self.parent.schematic.deviceList)):
            device=self.parent.schematic.deviceList[d]
            if device.IsAt(self.parent.Button1Coord):
                self.parent.deviceSelected = device
                self.parent.deviceSelectedIndex = d
                self.parent.coordInPart = device.WhereInPart(self.parent.Button1Coord)
                self.DeviceSelected()
                return
        for w in range(len(self.parent.schematic.wireList)):
            for v in range(len(self.parent.schematic.wireList[w])):
                if self.parent.Button1Coord == self.parent.schematic.wireList[w][v]:
                    self.parent.w = w
                    self.parent.v = v
                    self.WireSelected()
                    return
        self.Selecting()
    def onCtrlMouseButton1_Nothing(self,event):
        pass
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

    def DeviceSelected(self):
        self.parent.canvas.config(cursor='left_ptr')
        self.UnselectAllDevices()
        self.parent.deviceSelected.selected=True
        self.UnselectAllWires()
        self.state='DeviceSelected'
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
        self.parent.Button1Coord=self.parent.NearestGridCoordinate(event.x,event.y)
        for d in range(len(self.parent.schematic.deviceList)):
            device=self.parent.schematic.deviceList[d]
            if device.IsAt(self.parent.Button1Coord):
                self.parent.deviceSelected = device
                self.parent.deviceSelectedIndex = d
                self.parent.coordInPart = device.WhereInPart(self.parent.Button1Coord)
                self.DeviceSelected()
                return
        for w in range(len(self.parent.schematic.wireList)):
            for v in range(len(self.parent.schematic.wireList[w])):
                if self.parent.Button1Coord == self.parent.schematic.wireList[w][v]:
                    self.parent.w = w
                    self.parent.v = v
                    self.WireSelected()
                    return
        self.Nothing()
    def onCtrlMouseButton1_DeviceSelected(self,event):
        pass
    def onCtrlMouseButton1Motion_DeviceSelected(self,event):
        pass
    def onCtrlMouseButton1Release_DeviceSelected(self,event):
        pass
    def onMouseButton3_DeviceSelected(self,event):
        self.parent.Button2Coord=self.parent.NearestGridCoordinate(event.x,event.y)
        if not self.parent.deviceSelected.IsAt(self.parent.Button2Coord):
            self.Nothing()
    def onMouseButton1Motion_DeviceSelected(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.deviceSelected.partPicture.current.SetOrigin([coord[0]-self.parent.coordInPart[0],coord[1]-self.parent.coordInPart[1]])
        self.parent.DrawSchematic()
    def onMouseButton1Release_DeviceSelected(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.deviceSelected.partPicture.current.SetOrigin([coord[0]-self.parent.coordInPart[0],coord[1]-self.parent.coordInPart[1]])
        self.parent.DrawSchematic()
    def onMouseButton3Release_DeviceSelected(self,event):
        self.parent.tk.call("tk_popup", self.parent.deviceTearOffMenu, event.x_root, event.y_root)
    def onMouseButton1Double_DeviceSelected(self,event):
        dpe=DevicePropertiesDialog(self.parent,self.parent.deviceSelected)
        if dpe.result != None:
            self.parent.schematic.deviceList[self.parent.deviceSelectedIndex] = dpe.result
            self.parent.DrawSchematic()
    def onMouseMotion_DeviceSelected(self,event):
        pass

    def WireSelected(self):
        self.parent.canvas.config(cursor='left_ptr')
        self.UnselectAllDevices()
        self.UnselectAllWires()
        self.parent.schematic.wireList[self.parent.w].selected=True
        self.state='WireSelected'
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
        self.parent.Button1Coord=self.parent.NearestGridCoordinate(event.x,event.y)
        for d in range(len(self.parent.schematic.deviceList)):
            device=self.parent.schematic.deviceList[d]
            if device.IsAt(self.parent.Button1Coord):
                self.parent.deviceSelected = device
                self.parent.deviceSelectedIndex = d
                self.parent.coordInPart = device.WhereInPart(self.parent.Button1Coord)
                self.DeviceSelected()
                return
        for w in range(len(self.parent.schematic.wireList)):
            for v in range(len(self.parent.schematic.wireList[w])):
                if self.parent.Button1Coord == self.parent.schematic.wireList[w][v]:
                    self.parent.w = w
                    self.parent.v = v
                    self.WireSelected()
                    return
        self.Nothing()
    def onCtrlMouseButton1_WireSelected(self,event):
        pass
    def onCtrlMouseButton1Motion_WireSelected(self,event):
        pass
    def onCtrlMouseButton1Release_WireSelected(self,event):
        pass
    def onMouseButton3_WireSelected(self,event):
        pass
    def onMouseButton1Motion_WireSelected(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.schematic.wireList[self.parent.w][self.parent.v] = coord
        self.parent.DrawSchematic()
    def onMouseButton1Release_WireSelected(self,event):
        pass
    def onMouseButton3Release_WireSelected(self,event):
        self.parent.tk.call('tk_popup',self.parent.wireTearOffMenu, event.x_root, event.y_root)
    def onMouseButton1Double_WireSelected(self,event):
        pass
    def onMouseMotion_WireSelected(self,event):
        pass

    def PartLoaded(self):
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
        self.parent.Button1Coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.partLoaded.partPicture.current.SetOrigin(self.parent.Button1Coord)
        self.parent.schematic.deviceList.append(self.parent.partLoaded)
        self.parent.deviceSelected=self.parent.schematic.deviceList[-1]
        self.parent.deviceSelectedIndex=len(self.parent.schematic.deviceList)-1
        self.parent.coordInPart=self.parent.deviceSelected.WhereInPart(self.parent.Button1Coord)
        self.DeviceSelected()
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

    def WireLoaded(self):
        self.parent.canvas.config(cursor='pencil')
        self.UnselectAllDevices()
        self.UnselectAllWires()
        self.state='WireLoaded'
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
        self.parent.Button1Coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.wireLoaded[-1]=(self.parent.Button1Coord)
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
            self.parent.wireLoaded[-1] = coord
            self.parent.DrawSchematic()
    def onMouseButton1Release_WireLoaded(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.parent.wireLoaded.append(coord)
        self.parent.DrawSchematic()
    def onMouseButton3Release_WireLoaded(self,event):
        self.parent.Button2Coord=self.parent.NearestGridCoordinate(event.x,event.y)
        if len(self.parent.wireLoaded) > 2:
            self.parent.schematic.wireList[-1]=Wire(self.parent.wireLoaded[:-1])
            self.parent.wireLoaded=Wire([(0,0)])
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
            self.parent.wireLoaded[-1]=coord
        else:
            if len(self.parent.wireLoaded) == 1:
                self.parent.wireLoaded[-1] = coord
            else:
                if abs(coord[0]-self.parent.wireLoaded[-2][0]) > abs(coord[1]-self.parent.wireLoaded[-2][1]):
                    self.parent.wireLoaded[-1] = (coord[0],self.parent.wireLoaded[-2][1])
                else:
                    self.parent.wireLoaded[-1] = (self.parent.wireLoaded[-2][0],coord[1])
        self.parent.DrawSchematic()

    def Panning(self):
        self.UnselectAllDevices()
        self.UnselectAllWires()
        self.parent.canvas.config(cursor='fleur')
        self.state='Panning'
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
        self.parent.Button1Coord=self.parent.NearestGridCoordinate(event.x,event.y)
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

    def Selecting(self):
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
        self.parent.Button1Coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.Selecting()
    def onCtrlMouseButton1_Selecting(self,event):
        pass
    def onCtrlMouseButton1Motion_Selecting(self,event):
        pass
    def onCtrlMouseButton1Release_Selecting(self,event):
        pass
    def onMouseButton3_Selecting(self,event):
        pass
    def onMouseButton1Motion_Selecting(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.UnselectAllDevices()
        self.UnselectAllWires()
        minx=min(coord[0],self.parent.Button1Coord[0])
        miny=min(coord[1],self.parent.Button1Coord[1])
        maxx=max(coord[0],self.parent.Button1Coord[0])
        maxy=max(coord[1],self.parent.Button1Coord[1])
        for d in range(len(self.parent.schematic.deviceList)):
            device=self.parent.schematic.deviceList[d]
            if device.IsIn(coord,self.parent.Button1Coord):
                device.selected=True
        for w in range(len(self.parent.schematic.wireList)):
            for v in range(len(self.parent.schematic.wireList[w])):
                if (minx <= self.parent.schematic.wireList[w][v][0]) and\
                    (maxx >= self.parent.schematic.wireList[w][v][0]) and\
                    (miny <= self.parent.schematic.wireList[w][v][1]) and\
                    (maxy >= self.parent.schematic.wireList[w][v][1]):
                    self.parent.schematic.wireList[w].selected=True
        self.parent.DrawSchematic()
        self.parent.canvas.create_rectangle((self.parent.Button1Coord[0]+self.parent.originx)*self.parent.grid,
                                            (self.parent.Button1Coord[1]+self.parent.originy)*self.parent.grid,
                                            (coord[0]+self.parent.originx)*self.parent.grid,
                                            (coord[1]+self.parent.originy)*self.parent.grid,
                                            dash=(1,5))
    def onMouseButton1Release_Selecting(self,event):
        AtLeastOneDeviceSelected=False
        AtLeastOneWireSelected=False
        MultipleThingsSelected=False
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        self.UnselectAllDevices()
        self.UnselectAllWires()
        minx=min(coord[0],self.parent.Button1Coord[0])
        miny=min(coord[1],self.parent.Button1Coord[1])
        maxx=max(coord[0],self.parent.Button1Coord[0])
        maxy=max(coord[1],self.parent.Button1Coord[1])
        for d in range(len(self.parent.schematic.deviceList)):
            device=self.parent.schematic.deviceList[d]
            if device.IsIn(coord,self.parent.Button1Coord):
                device.selected=True
                if AtLeastOneDeviceSelected:
                    MultipleThingsSelected = True
                else:
                    AtLeastOneDeviceSelected=True
                    self.parent.deviceSelected = device
                    self.parent.deviceSelectedIndex = d
                    self.parent.coordInPart = device.WhereInPart(self.parent.Button1Coord)
        for w in range(len(self.parent.schematic.wireList)):
            for v in range(len(self.parent.schematic.wireList[w])):
                if (minx <= self.parent.schematic.wireList[w][v][0]) and\
                    (maxx >= self.parent.schematic.wireList[w][v][0]) and\
                    (miny <= self.parent.schematic.wireList[w][v][1]) and\
                    (maxy >= self.parent.schematic.wireList[w][v][1]):
                    self.parent.schematic.wireList[w].selected=True
                    if AtLeastOneWireSelected:
                        MultipleThingsSelected=True
                    else:
                        AtLeastOneWireSelected=True
                        self.parent.w = w
                        self.parent.v = v
        if AtLeastOneDeviceSelected and AtLeastOneWireSelected:
            MultipleThingsSelected=True
        if MultipleThingsSelected:
            self.MultipleSelections()
        elif AtLeastOneDeviceSelected:
            self.DeviceSelected()
        elif AtLeastOneWireSelected:
            self.WireSelected()
        else:  
            self.Nothing()
    def onMouseButton3Release_Selecting(self,event):
        pass
    def onMouseButton1Double_Selecting(self,event):
        pass
    def onMouseMotion_Selecting(self,event):
        pass

    def MultipleSelections(self):
        self.parent.canvas.config(cursor='left_ptr')
        self.state='Multiple Selections'
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
        self.parent.parent.toolbar.deletePartButton.config(state="disabled")
        self.parent.parent.menu.PartsMenu.entryconfigure('Delete Part',state='disabled')
        self.parent.parent.menu.PartsMenu.entryconfigure('Edit Properties',state='disabled')
        self.parent.parent.toolbar.duplicatePartButton.config(state="disabled")
        self.parent.parent.menu.PartsMenu.entryconfigure('Duplicate Part',state='disabled')
        self.parent.parent.menu.WireMenu.entryconfigure('Delete Vertex',state='disabled')
        self.parent.parent.menu.WireMenu.entryconfigure('Duplicate Vertex',state='disabled')
        self.parent.parent.menu.WireMenu.entryconfigure('Delete Wire',state='disabled')
        self.parent.parent.toolbar.panButton.config(relief=RAISED)
        self.parent.parent.statusbar.set('Multiple Selections')
        self.parent.DrawSchematic()
    def onMouseButton1_MultipleSelections(self,event):
        self.parent.Button1Coord=self.parent.NearestGridCoordinate(event.x,event.y)
        inSelection=False
        for d in range(len(self.parent.schematic.deviceList)):
            device=self.parent.schematic.deviceList[d]
            if device.IsAt(self.parent.Button1Coord):
                inSelection=True
                break
        for w in range(len(self.parent.schematic.wireList)):
            for v in range(len(self.parent.schematic.wireList[w])):
                if self.parent.Button1Coord == self.parent.schematic.wireList[w][v]:
                    inSelection=True
                    break
        if inSelection:
            self.parent.OriginalDeviceCoordinates = [device.WhereInPart(self.parent.Button1Coord) for device in self.parent.schematic.deviceList]
            self.parent.OriginalWireCoordinates = [[(self.parent.Button1Coord[0]-vertex[0],
                                                     self.parent.Button1Coord[1]-vertex[1]) for vertex in wire] for wire in self.parent.schematic.wireList]
            self.MultipleSelections()
        else:
            self.Selecting()
    def onCtrlMouseButton1_MultipleSelections(self,event):
        pass
    def onCtrlMouseButton1Motion_MultipleSelections(self,event):
        pass
    def onCtrlMouseButton1Release_MultipleSelections(self,event):
        self.MultipleSelections()
    def onMouseButton3_MultipleSelections(self,event):
        pass
    def onMouseButton1Motion_MultipleSelections(self,event):
        coord=self.parent.NearestGridCoordinate(event.x,event.y)
        for d in range(len(self.parent.schematic.deviceList)):
            device=self.parent.schematic.deviceList[d]
            coordInPart = self.parent.OriginalDeviceCoordinates[d]
            if device.selected:
                device.partPicture.current.SetOrigin([coord[0]-coordInPart[0],coord[1]-coordInPart[1]])
            for w in range(len(self.parent.schematic.wireList)):
                for v in range(len(self.parent.schematic.wireList[w])):
                    if self.parent.schematic.wireList[w].selected:
                        self.parent.schematic.wireList[w][v]=(coord[0]-self.parent.OriginalWireCoordinates[w][v][0],
                                                              coord[1]-self.parent.OriginalWireCoordinates[w][v][1])
        self.parent.DrawSchematic()
    def onMouseButton1Release_MultipleSelections(self,event):
        pass
    def onMouseButton3Release_MultipleSelections(self,event):
        self.Nothing()
    def onMouseButton1Double_MultipleSelections(self,event):
        pass
    def onMouseMotion_MultipleSelections(self,event):
        pass

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

        self.stateMachine = DrawingStateMachine(self)
    def NearestGridCoordinate(self,x,y):
        return (int(round(float(x)/self.grid))-self.originx,int(round(float(y)/self.grid))-self.originy)
    def DrawSchematic(self):
        self.canvas.delete(ALL)
        foundAPort=False
        foundASource=False
        for device in self.schematic.deviceList:
            device.DrawDevice(self.canvas,self.grid,self.originx,self.originy)
            deviceType = device['type'].GetValue()
            if  deviceType == 'Port':
                foundAPort = True
            else:
                netListLine = device.NetListLine()
                if not netListLine is None:
                    firstToken=netListLine.strip().split(' ')[0]
                    if firstToken == 'voltagesource':
                        foundASource = True
                    elif firstToken == 'currentsource':
                        foundASource = True
        for wire in self.schematic.wireList:
            wire.DrawWire(self.canvas,self.grid,self.originx,self.originy)
        self.parent.menu.CalcMenu.entryconfigure('Simulate',state='normal' if foundASource else 'disabled')
        self.parent.menu.CalcMenu.entryconfigure('Calculate S-parameters',state='normal' if foundAPort else 'disabled')
    def EditSelectedDevice(self):
        if self.stateMachine.state=='DeviceSelected':
            dpe=DevicePropertiesDialog(self,self.deviceSelected)
            if dpe.result != None:
                self.schematic.deviceList[self.deviceSelectedIndex] = dpe.result
                self.DrawSchematic()
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
    def DeleteSelectedDevice(self):
        del self.schematic.deviceList[self.deviceSelectedIndex]
        self.stateMachine.Nothing()
    def DeleteSelectedVertex(self):
        del self.schematic.wireList[self.w][self.v]
        self.stateMachine.Nothing()
    def DuplicateSelectedVertex(self):
        self.schematic.wireList[self.w]=Wire(self.schematic.wireList[self.w][:self.v]+\
        [self.schematic.wireList[self.w][self.v]]+\
        self.schematic.wireList[self.w][self.v:],True)
        self.stateMachine.WireSelected()
    def DeleteSelectedWire(self):
        del self.schematic.wireList[self.w]
        self.stateMachine.Nothing()
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
