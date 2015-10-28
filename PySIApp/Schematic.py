'''
Created on Oct 15, 2015

@author: peterp
'''
from Tkinter import *
import xml.etree.ElementTree as et

from DeviceProperties import *
from Device import *

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
                    self.deviceList.append(returnedDevice)
                    pass
            elif child.tag == 'wires':
                for wireElement in child:
                    wire=Wire()
                    for vertexElement in wireElement:
                        wire.append(eval(vertexElement.text))
                    self.wireList.append(wire)
    def NetList(self):
        self.ConsolidateWires()
        textToShow=[]
        deviceList = self.deviceList
        wireList = self.wireList
        # put all devices in the net list
        for device in deviceList:
            deviceType = device[PartPropertyPartName().propertyName].value
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
                thisDevicePartName = thisDevice[PartPropertyPartName().propertyName].value
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
                    deviceName = self.deviceList[deviceIndex][PartPropertyReferenceDesignator().propertyName].value
                    pinNumber = self.deviceList[deviceIndex].partPicture.current.pinList[pinIndex].pinNumber
                    thisConnectionString = thisConnectionString + ' '+ str(deviceName) +' '+str(pinNumber)
                textToShow.append(thisConnectionString)
        return textToShow
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

class Drawing(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent)
        self.parent=parent
        self.canvas = Canvas(self,relief=SUNKEN,borderwidth=1,width=600,height=600)
        self.canvas.pack(side=TOP, fill=BOTH, expand=YES)
        #self.canvas.create_rectangle(1,1,self.canvas.winfo_reqheight(),self.canvas.winfo_reqwidth())
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind('<Button-1>',self.onMouseButton1)
        self.canvas.bind('<Button-3>',self.onMouseButton2)
        self.canvas.bind('<B1-Motion>',self.onMouseButton1Motion)
        self.canvas.bind('<ButtonRelease-1>',self.onMouseButton1Release)
        self.canvas.bind('<ButtonRelease-3>',self.onMouseButton3Release)
        self.canvas.bind('<Double-Button-1>',self.onMouseButton1Double)
        self.canvas.bind('<Button-4>',self.onMouseWheel)
        self.canvas.bind('<MouseWheel>',self.onMouseWheel)
        self.canvas.bind('<Motion>',self.onMouseMotion)
        self.grid=32
        self.originx=0
        self.originy=0
        self.partLoaded = None
        self.deviceSelected = None
        self.coordInPart = (0,0)
        self.wireLoaded = None
        self.schematic = Schematic()
        self.wireSelected = False
        self.deviceTearOffMenu=Menu(self, tearoff=0)
        self.deviceTearOffMenu.add_command(label="Edit Properties",command=self.EditSelectedDevice)
        self.deviceTearOffMenu.add_command(label="Duplicate",command=self.DuplicateSelectedDevice)
        self.deviceTearOffMenu.add_command(label="Delete",command=self.DeleteSelectedDevice)
        self.canvasTearOffMenu=Menu(self, tearoff=0)
        self.canvasTearOffMenu.add_command(label='Add Part',command=self.parent.onAddPart)
        self.canvasTearOffMenu.add_command(label='Add Wire',command=self.parent.onAddWire)
        self.canvasTearOffMenu.add_command(label='Add Port',command=self.parent.onAddPort)
    def NearestGridCoordinate(self,x,y):
        return (int(round(float(x)/self.grid))-self.originx,int(round(float(y)/self.grid))-self.originy)
    def on_resize(self,event):
        return
        self.canvas.delete(ALL)
        self.canvas.create_rectangle(1,1,event.width-5,event.height-5)
        self.DrawSchematic()
    def onMouseButton1(self,event):
        print 'clicked at: ',event.x,event.y
        self.Button1Coord=self.NearestGridCoordinate(event.x,event.y)
        if self.wireSelected:
            self.wireSelected = False
            self.schematic.wireList[self.w].selected=False
        if not self.partLoaded == None:
            partToLoad=self.partLoaded
            partToLoad.partPicture.current.SetOrigin(self.Button1Coord)
            self.schematic.deviceList.append(partToLoad)
            self.partLoaded=None
            if not self.deviceSelected == None:
                self.deviceSelected.selected=False
                self.deviceSelected=None
            self.deviceSelected=self.schematic.deviceList[-1]
            self.deviceSelected.selected=True
            self.deviceSelectedIndex=len(self.schematic.deviceList)-1
            self.coordInPart=self.deviceSelected.WhereInPart(self.Button1Coord)
        elif not self.wireLoaded == None:
            self.wireLoaded[-1]=(self.Button1Coord)
        else: # select a part
            for d in range(len(self.schematic.deviceList)):
                device=self.schematic.deviceList[d]
                if device.IsAt(self.Button1Coord):
                    if not self.deviceSelected == None:
                        self.deviceSelected.selected=False
                        self.deviceSelected=None
                    self.deviceSelected = device
                    self.deviceSelected.selected=True
                    self.deviceSelectedIndex = d
                    self.coordInPart = device.WhereInPart(self.Button1Coord)
                    print 'device selected'
                    return
            if not self.deviceSelected == None:
                self.deviceSelected.selected=False
                self.deviceSelected=None
            for w in range(len(self.schematic.wireList)):
                for v in range(len(self.schematic.wireList[w])):
                    if self.Button1Coord == self.schematic.wireList[w][v]:
                        if self.wireSelected:
                            self.wireSelected = False
                            self.schematic.wireList[self.w].selected=False
                        print 'wire vertex selected'
                        self.wireSelected = True
                        self.schematic.wireList[w].selected=True
                        self.w = w
                        self.v = v
                        return
            if self.wireSelected:
                self.schematic.wireList[self.w].selected=False
                self.wireSelected=False
        self.DrawSchematic()
    def onMouseButton2(self,event):
        self.Button2Coord=self.NearestGridCoordinate(event.x,event.y)
        print 'right click'
        if not self.deviceSelected == None:
            if self.deviceSelected.IsAt(self.Button2Coord):
                pass
            else:
                self.deviceSelected.selected=False
                self.deviceSelected=None
        if self.wireLoaded != None:
            if len(self.wireLoaded) > 2:
                self.schematic.wireList[-1]=Wire(self.wireLoaded[:-1])
                self.wireLoaded=Wire([(0,0)])
                self.schematic.wireList.append(self.wireLoaded)
            else:
                self.wireLoaded=None
            #self.schematic.wireList=self.schematic.wireList[:-1]
        self.DrawSchematic()
    def onMouseButton3Release(self,event):
        if self.deviceSelected != None:
            self.tk.call("tk_popup", self.deviceTearOffMenu, event.x_root, event.y_root)
        elif self.wireLoaded != None:
            pass
        else:
            self.tk.call('tk_popup',self.canvasTearOffMenu, event.x_root, event.y_root)

    def onMouseButton1Motion(self,event):
        coord=self.NearestGridCoordinate(event.x,event.y)
        if not self.deviceSelected == None:
            self.deviceSelected.partPicture.current.SetOrigin([coord[0]-self.coordInPart[0],coord[1]-self.coordInPart[1]])
        elif not self.wireLoaded == None:
            if len(self.wireLoaded) > 0:
                self.wireLoaded[-1] = coord
        elif self.wireSelected == True:
            self.schematic.wireList[self.w][self.v] = coord
        else:
            self.originx=self.originx+coord[0]-self.Button1Coord[0]
            self.originy=self.originy+coord[1]-self.Button1Coord[1]
        self.DrawSchematic()
    def onMouseMotion(self,event):
        coord=self.NearestGridCoordinate(event.x,event.y)
        if not self.wireLoaded == None:
            freeFormWire=True
            if freeFormWire:
                self.wireLoaded[-1]=coord
            else:
                if len(self.wireLoaded) == 1:
                    self.wireLoaded[-1] = coord
                else:
                    if abs(coord[0]-self.wireLoaded[-2][0]) > abs(coord[1]-self.wireLoaded[-2][1]):
                        self.wireLoaded[-1] = (coord[0],self.wireLoaded[-2][1])
                    else:
                        self.wireLoaded[-1] = (self.wireLoaded[-2][0],coord[1])
        self.DrawSchematic()

    def onMouseButton1Release(self,event):
        coord=self.NearestGridCoordinate(event.x,event.y)
        if not self.deviceSelected == None:
            self.deviceSelected.partPicture.current.SetOrigin([coord[0]-self.coordInPart[0],coord[1]-self.coordInPart[1]])
            #self.deviceSelected = None
        elif self.wireLoaded != None:
            self.wireLoaded.append(coord)
        #self.wireSelected = False
        self.DrawSchematic()
    def onMouseWheel(self,event):
        print 'wheel',event.delta
    def onMouseButton1Double(self,event):
        print 'double click'
        self.wireLoaded=None
        if not self.deviceSelected == None:
            self.deviceSelected.selected=False
            self.deviceSelected=None
            if self.wireSelected:
                self.schematic.wireList[self.w].selected=False
                self.wireSelected=False
        if False: #self.wireLoaded != None:
            self.schematic.wireList[-1]=self.schematic.wireList[-1][:-1]
            self.wireLoaded=Wire([(0,0)])
            self.schematic.wireList.append(self.wireLoaded)
        else:
            for d in range(len(self.schematic.deviceList)):
                if self.schematic.deviceList[d].IsAt(self.NearestGridCoordinate(event.x,event.y)):
                    dpe=DevicePropertiesDialog(self,self.schematic.deviceList[d])
                    if dpe.result != None:
                        self.schematic.deviceList[d] = dpe.result
                        self.DrawSchematic()
                    return
    def DrawSchematic(self):
        self.canvas.delete(ALL)
        for device in self.schematic.deviceList:
            device.DrawDevice(self.canvas,self.grid,self.originx,self.originy)
        for wire in self.schematic.wireList:
            wire.DrawWire(self.canvas,self.grid,self.originx,self.originy)
    def EditSelectedDevice(self):
        if self.deviceSelected != None:
            dpe=DevicePropertiesDialog(self,self.deviceSelected)
            if dpe.result != None:
                self.schematic.deviceList[self.deviceSelectedIndex] = dpe.result
                self.DrawSchematic()
    def DuplicateSelectedDevice(self):
        if not self.deviceSelected == None:
            self.partLoaded=copy.deepcopy(self.deviceSelected)
        if not self.deviceSelected == None:
            self.deviceSelected.selected=False
            self.deviceSelected=None
        if self.wireSelected:
            self.schematic.wireList[self.w].selected=False
            self.wireSelected = False
    def DeleteSelectedDevice(self):
        if self.wireSelected:
            self.schematic.wireList[self.w].selected=False
            self.wireSelected=False
            del self.schematic.wireList[self.w]
            self.DrawSchematic()
        elif self.deviceSelected != None:
            self.deviceSelected.selected=False
            self.deviceSelected = None
            del self.schematic.deviceList[self.deviceSelectedIndex]
            self.DrawSchematic()
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
        self.partLoaded = None
        self.deviceSelected = None
        self.coordInPart = (0,0)
        self.wireLoaded = None
        self.schematic = Schematic()
        self.wireSelected = False
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
