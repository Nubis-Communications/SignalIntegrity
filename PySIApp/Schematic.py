'''
Created on Oct 15, 2015

@author: peterp
'''
from Tkinter import *
import xml.etree.ElementTree as et

from DeviceProperties import *

class Schematic(object):
    def __init__(self):
        self.deviceList = []
        self.wireList = []
    def WriteToFile(self,filename):
        sch=et.Element('schematic')
        devices = [device.xml() for device in self.deviceList]
        sch.extend(devices)
        #print et.tostring(sch)
        et.ElementTree(sch).write('output.xml')


class SchematicFrame(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent)
        self.canvas = Canvas(self)
        self.canvas.pack(side=TOP, fill=BOTH, expand=YES)
        self.canvas.create_rectangle(1,1,self.canvas.winfo_reqheight(),self.canvas.winfo_reqwidth())
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind('<Button-1>',self.onMouseButton1)
        self.canvas.bind('<Button-3>',self.onMouseButton2)
        self.canvas.bind('<B1-Motion>',self.onMouseButton1Motion)
        self.canvas.bind('<ButtonRelease-1>',self.onMouseButton1Release)
        self.canvas.bind('<Double-Button-1>',self.onMouseButton1Double)
        self.canvas.bind('<Button-4>',self.onMouseWheel)
        #self.canvas.bind('<MouseWheel>',self.onMouseWheel)
        self.canvas.bind('<Motion>',self.onMouseMotion)
        self.grid=10
        self.originx=0
        self.originy=0
        self.partLoaded = None
        self.deviceSelected = None
        self.coordInPart = (0,0)
        self.wireLoaded = None
        self.schematic = Schematic()
        self.wireSelected = False
    def NearestGridCoordinate(self,x,y):
        return (int(round(float(x)/self.grid))-self.originx,int(round(float(y)/self.grid))-self.originy)
    def on_resize(self,event):
        self.canvas.delete(ALL)
        self.canvas.create_rectangle(1,1,event.width-5,event.height-5)
        self.DrawSchematic()
    def onMouseButton1(self,event):
        print 'clicked at: ',event.x,event.y
        self.Button1Coord=self.NearestGridCoordinate(event.x,event.y)
        if not self.partLoaded == None:
            partToLoad=self.partLoaded
            partToLoad.partPicture.SetOrigin(self.Button1Coord)
            self.schematic.deviceList.append(partToLoad)
            self.partLoaded=None
            self.deviceSelected=self.schematic.deviceList[-1]
            self.deviceSelectedIndex=len(self.schematic.deviceList)-1
            self.coordInPart=self.deviceSelected.WhereInPart(self.Button1Coord)
        elif not self.wireLoaded == None:
            self.wireLoaded[-1]=(self.Button1Coord)
        else: # select a part
            for d in range(len(self.schematic.deviceList)):
                device=self.schematic.deviceList[d]
                if device.IsAt(self.Button1Coord):
                    self.deviceSelected = device
                    self.deviceSelectedIndex = d
                    self.coordInPart = device.WhereInPart(self.Button1Coord)
                    print 'device selected'
                    return
            self.deviceSelected=None
            for w in range(len(self.schematic.wireList)):
                for v in range(len(self.schematic.wireList[w])):
                    if self.Button1Coord == self.schematic.wireList[w][v]:
                        print 'wire vertex selected'
                        self.wireSelected = True
                        self.w = w
                        self.v = v
                        return
            self.wireSelected=False
        self.DrawSchematic()
    def onMouseButton2(self,event):
        print 'right click'
        self.deviceSelected=None
        if self.wireLoaded != None:
            if len(self.wireLoaded) > 2:
                self.schematic.wireList[-1]=self.wireLoaded[:-1]
                self.wireLoaded=[(0,0)]
                self.schematic.wireList.append(self.wireLoaded)
            else:
                self.wireLoaded=None
            #self.schematic.wireList=self.schematic.wireList[:-1]
        self.DrawSchematic()
    def onMouseButton1Motion(self,event):
        coord=self.NearestGridCoordinate(event.x,event.y)
        if not self.deviceSelected == None:
            self.deviceSelected.partPicture.SetOrigin([coord[0]-self.coordInPart[0],coord[1]-self.coordInPart[1]])
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
            self.deviceSelected.partPicture.SetOrigin([coord[0]-self.coordInPart[0],coord[1]-self.coordInPart[1]])
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
        self.deviceSelected=None
        self.wireSelected=False
        if False: #self.wireLoaded != None:
            self.schematic.wireList[-1]=self.schematic.wireList[-1][:-1]
            self.wireLoaded=[[0,0]]
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
            if len(wire) >= 2:
                segmentCoord=wire[0]
                for vertex in wire[1:]:
                    self.canvas.create_line((segmentCoord[0]+self.originx)*self.grid,(segmentCoord[1]+self.originy)*self.grid,(vertex[0]+self.originx)*self.grid,(vertex[1]+self.originy)*self.grid)
                    segmentCoord=vertex
