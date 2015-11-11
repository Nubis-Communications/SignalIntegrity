'''
Created on Nov 8, 2015

@author: peterp
'''
import xml.etree.ElementTree as et
import copy

class Vertex(object):
    def __init__(self,coord,selected=False):
        self.coord=coord
        self.selected=False
    def __getitem__(self,item):
        return self.coord[item]
    def InitFromXml(self,vertexElement):
        self.selected=False
        self.coord = eval(vertexElement.text)
        return self
    def xml(self):
        vertexElement=et.Element('vertex')
        vertexElement.text=str(self.coord)
        return vertexElement
    def IsAt(self,coord):
        return self.coord == coord
    def IsIn(self,i,f):
        minx=min(i[0],f[0])
        miny=min(i[1],f[1])
        maxx=max(i[0],f[0])
        maxy=max(i[1],f[1])
        if minx > self[0]:
            return False
        if maxx < self[0]:
            return False
        if miny > self[1]:
            return False
        if maxy < self[1]:
            return False
        return True

class Wire(object):
    def __init__(self,vertexList=None):
        if vertexList==None:
            vertexList=[]
        self.vertexList=vertexList
    def __getitem__(self,item):
        return self.vertexList[item]
    def __setitem__(self,item,value):
        if not isinstance(value,Vertex):
            raise ValueError
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
        selected=False
        for vertex in self:
            if vertex.selected:
                selected = True
        if len(self) >= 2:
            segmentCoord=self[0]
            for vertex in self[1:]:
                canvas.create_line((segmentCoord[0]+x)*grid,(segmentCoord[1]+y)*grid,(vertex[0]+x)*grid,(vertex[1]+y)*grid,fill=('blue' if (segmentCoord.selected and vertex.selected) else 'black'))
                segmentCoord=vertex
            if selected:
                for vertex in self:
                    size=max(1,grid/8)
                    canvas.create_line((vertex[0]+x)*grid-size,(vertex[1]+y)*grid-size,
                                        (vertex[0]+x)*grid+size,(vertex[1]+y)*grid+size,
                                        fill=('blue' if vertex.selected else 'black'),
                                        width=(2 if vertex.selected else 1))
                    canvas.create_line((vertex[0]+x)*grid+size,(vertex[1]+y)*grid-size,
                                        (vertex[0]+x)*grid-size,(vertex[1]+y)*grid+size,
                                        fill=('blue' if vertex.selected else 'black'),
                                        width=(2 if vertex.selected else 1))
    def __add__(self,other):
        if isinstance(other, Wire):
            return Wire(self.vertexList+other.vertexList)
        elif isinstance(other,list):
            return Wire(self.vertexList+other)
    def InitFromXml(self,wireElement):
        self.__init__()
        for child in wireElement:
            if child.tag == 'vertex':
                vertex=Vertex((0,0))
                vertex.InitFromXml(child)
                self.append(vertex)
        return self
    def CoordinateList(self):
        return [vertex.coord for vertex in self]
    def xml(self):
        wireElement=et.Element('wire')
        vertexElements=[]
        for vertex in self:
            vertexElement=vertex.xml()
            vertexElements.append(vertexElement)
        wireElement.extend(vertexElements)
        return wireElement

class WireList(object):
    def __init__(self):
        self.wires =[]
    def __getitem__(self,item):
        return self.wires[item]
    def __setitem__(self,item,value):
        if not isinstance(value,Wire):
            raise ValueError
        self.wires[item]=value
    def __delitem__(self,item):
        del self.wires[item]
    def __len__(self):
        return len(self.wires)
    def append(self,item):
        if not isinstance(item,Wire):
            raise ValueError
        self.wires.append(item)
    def UnselectAll(self):
        for wire in self:
            for vertex in wire:
                vertex.selected=False
    def InitFromXml(self,wiresElement):
        self.__init__()
        for child in wiresElement:
            if child.tag == 'wire':
                wire=Wire()
                wire.InitFromXml(child)
                self.wires.append(wire)
    def xml(self):
        wiresElement=et.Element('wires')
        wireElements=[]
        for wire in self:
            wireElement=wire.xml()
            wireElements.append(wireElement)
        wiresElement.extend(wireElements)
        return wiresElement
    def RemoveEmptyWires(self):
        wiresNeedRemoval=False
        for wire in self:
            if len(wire)<2:
                wiresNeedRemoval=True
                break
        if not wiresNeedRemoval:
            return
        newWireList=WireList()
        for wire in self:
            if len(wire)>=2:
                newWireList.append(wire)
        self.wires=newWireList
    def RemoveDuplicateVertices(self):
        hasDuplicateVertices=False
        for wire in self:
            if hasDuplicateVertices:
                break
            if len(wire)<1:
                break
            lastVertexCoordinate=wire[0].coord
            for vertex in wire[1:]:
                thisVertexCoordinate=vertex.coord
                if thisVertexCoordinate==lastVertexCoordinate:
                    hasDuplicateVertices=True
                    break
                lastVertexCoordinate=thisVertexCoordinate
        if not hasDuplicateVertices:
            return
        newWireList=WireList()
        for wire in self:
            if len(wire)<1:
                continue
            newWire=Wire()
            lastVertex=wire[0]
            newWire.append(lastVertex)
            for thisVertex in wire[1:]:
                if thisVertex.coord != lastVertex.coord:
                    newWire.append(thisVertex)
                    lastVertex=thisVertex
            if len(newWire)>=2:
                newWireList.append(newWire)
        self.wires=newWireList
    def Direction(self,startCoord,endCoord):
        vector=(endCoord[0]-startCoord[0],endCoord[1]-startCoord[1])
        if vector[0]==0:
            # this is a north south line
            if vector[1]>0:
                return 's' # this is a south going line
            elif vector[1]<0:
                return 'n' # this is a north going line
            else:
                return '?'
        elif vector[1]==0:
            # this is an east west line
            if vector[0]>0:
                return 'e' # this is an east going line
            elif vector[0]<0:
                return 'w' # this is a west going line
            else:
                return '?'
        else:
            return '?'
    def InsertNeededVertices(self,deviceList):
        # walk along all of the wires and put vertices at any locations where a wire vertex is along a straight line of another wire
        newWireList=WireList()
        for thisWire in self:
            newWire=Wire()
            thisWireSegmentStart=thisWire[0]
            newWire.append(thisWireSegmentStart)
            for vertex in thisWire[1:]:
                thisWireSegmentEnd = vertex
                vector=(thisWireSegmentEnd.coord[0]-thisWireSegmentStart.coord[0],thisWireSegmentEnd.coord[1]-thisWireSegmentStart.coord[1])
                if vector[0]==0:
                    # this is a north south line
                    if vector[1]>0:
                        step=(0,1) # this is a south going line
                    elif vector[1]<0:
                        step=(0,-1) # this is a north going line
                    else:
                        # this should not be possible
                        raise ValueError
                elif vector[1]==0:
                    # this is an east west line
                    if vector[0]>0:
                        step=(1,0) # this is an east going line
                    elif vector[0]<0:
                        step=(-1,0) # this is a west going line
                    else:
                        # this should not be possible
                        raise ValueError
                else:
                    # this is some kind of diagonal line
                    step=(0,0)
                if step != (0,0):
                    # step along this line checking the start and end points of all other lines
                    thisCoordToCheck = (thisWireSegmentStart.coord[0]+step[0],thisWireSegmentStart.coord[1]+step[1])
                    while thisCoordToCheck != thisWireSegmentEnd.coord:
                        vertexAddedAtThisCoordinate=False
                        for otherWire in self:
                            for otherVertex in otherWire:
                                if otherVertex.coord == thisCoordToCheck:
                                    # found one - need to insert a vertex into this wire
                                    newWire.append(Vertex(thisCoordToCheck))
                                    vertexAddedAtThisCoordinate=True
                                    break
                        if not vertexAddedAtThisCoordinate:
                            for device in deviceList:
                                if vertexAddedAtThisCoordinate:
                                    break
                                for pinCoordinate in device.partPicture.current.PinCoordinates():
                                    if pinCoordinate == thisCoordToCheck:
                                        newWire.append(Vertex(thisCoordToCheck))
                                        vertexAddedAtThisCoordinate=True
                                        break
                        thisCoordToCheck = (thisCoordToCheck[0]+step[0],thisCoordToCheck[1]+step[1])
                newWire.append(thisWireSegmentEnd)
                thisWireSegmentStart=thisWireSegmentEnd
            newWireList.append(newWire)
        self.wires=newWireList
    def SplitDottedWires(self,dotList):
        splitAWire=True
        while splitAWire:
            splitAWire=False
            for wireIndex in range(len(self)):
                wire = self[wireIndex]
                if splitAWire:
                    break
                for vertexIndex in range(1,len(wire)-1):
                    if splitAWire:
                        break
                    for dot in dotList:
                        if wire[vertexIndex].coord == dot:
                            newWire=Wire(wire[vertexIndex:])
                            self[wireIndex]=Wire(wire[:vertexIndex+1])
                            self.wires.append(newWire)
                            splitAWire=True
                            break
    def RemoveUnneededVertices(self):
        unneededVertex=False
        for wire in self:
            if unneededVertex:
                break
            for vertexIndex in range(1,len(wire)-1):
                vertexBefore=wire[vertexIndex-1]
                thisVertex=wire[vertexIndex]
                vertexAfter=wire[vertexIndex+1]
                directionSegmentBefore = self.Direction(vertexBefore,thisVertex)
                directionSegmentAfter = self.Direction(thisVertex,vertexAfter)
                if directionSegmentBefore == '?' or directionSegmentAfter == '?':
                    continue
                if directionSegmentBefore == directionSegmentAfter:
                    unneededVertex=True
                    break
        if not unneededVertex:
            return
        newWireList=WireList()
        for wire in self:
            newWire=Wire()
            newWire.append(wire[0])
            for vertexIndex in range(1,len(wire)-1):
                vertexBefore=wire[vertexIndex-1]
                thisVertex=wire[vertexIndex]
                vertexAfter=wire[vertexIndex+1]
                directionSegmentBefore = self.Direction(vertexBefore,thisVertex)
                directionSegmentAfter = self.Direction(thisVertex,vertexAfter)
                if directionSegmentBefore == '?' or directionSegmentAfter == '?':
                    newWire.append(thisVertex)
                    continue
                if directionSegmentBefore != directionSegmentAfter:
                    newWire.append(thisVertex)
            newWire.append(wire[-1])
            newWireList.append(newWire)
        self.wires=newWireList
    def JoinUnDottedWires(self,dotList):
        removeWireIndexList = [False for index in range(len(self))]
        for thisWireIndex in range(len(self)):
            if not removeWireIndexList[thisWireIndex]:
                if len(self[thisWireIndex])<2:
                    removeWireIndexList[thisWireIndex]=True
            if not removeWireIndexList[thisWireIndex]:
                for otherWireIndex in range(thisWireIndex+1,len(self)):
                    thisWireStartPoint=self[thisWireIndex][0].coord
                    thisWireStartPointInDotList = thisWireStartPoint in dotList
                    thisWireEndPoint=self[thisWireIndex][-1].coord
                    thisWireEndPointInDotList = thisWireEndPoint in dotList
                    if not removeWireIndexList[otherWireIndex]:
                        if len(self[otherWireIndex])<2:
                            removeWireIndexList[otherWireIndex]=True
                    if not removeWireIndexList[otherWireIndex]:
                        otherWireStartPoint=self[otherWireIndex][0].coord
                        otherWireStartPointInDotList = otherWireStartPoint in dotList
                        otherWireEndPoint=self[otherWireIndex][-1].coord
                        otherWireEndPointInDotList = otherWireEndPoint in dotList
                        if thisWireEndPoint == otherWireStartPoint and not thisWireEndPointInDotList and not otherWireStartPointInDotList:
                            self[thisWireIndex]=self[thisWireIndex]+self[otherWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
                        elif thisWireStartPoint == otherWireEndPoint and not thisWireStartPointInDotList and not otherWireEndPointInDotList:
                            self[thisWireIndex]=self[otherWireIndex]+self[thisWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
                        elif thisWireStartPoint == otherWireStartPoint and not thisWireStartPointInDotList and not otherWireStartPointInDotList:
                            self[otherWireIndex].reverse()
                            self[thisWireIndex]= self[otherWireIndex]+self[thisWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
                        elif thisWireEndPoint == otherWireEndPoint and not thisWireEndPointInDotList and not otherWireEndPointInDotList:
                            self[otherWireIndex].reverse()
                            self[thisWireIndex]=self[thisWireIndex]+self[otherWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
        if not True in removeWireIndexList:
            return
        # remove all of the wires to be removed
        keepDeletingWires = True
        while keepDeletingWires:
            keepDeletingWires = False
            for wireIndex in range(len(self)):
                if removeWireIndexList[wireIndex]==True:
                    del self[wireIndex]
                    del removeWireIndexList[wireIndex]
                    keepDeletingWires=True
                    break
    def ConsolidateWires(self,schematic):
        deviceList=schematic.deviceList
        self.RemoveEmptyWires()
        self.RemoveDuplicateVertices()
        self.InsertNeededVertices(deviceList)
        dotList=schematic.DotList()
        self.SplitDottedWires(dotList)
        self.JoinUnDottedWires(dotList)
        self.RemoveUnneededVertices()
        return
        keepDeletingWires = True
        while keepDeletingWires:
            keepDeletingWires= False
            for wireIndex in range(len(self)):
                wire = self[wireIndex]
                if len(wire) < 2:
                    del self[wireIndex]
                    keepDeletingWires=True
                    break
                else:
                    keepDeletingVertices = True
                    while keepDeletingVertices:
                        keepDeletingVertices=False
                        for vertexIndex in range(1,len(wire)):
                            thisVertex = wire[vertexIndex].coord
                            lastVertex = wire[vertexIndex-1].coord
                            if thisVertex == lastVertex:
                                del self[wireIndex][vertexIndex]
                                keepDeletingVertices = True
                                break
        # at this point, all wires have at least two coordinates and no adjacent coordinates are the same
        removeWireIndexList = [False for index in range(len(self))]
        for thisWireIndex in range(len(self)):
            if not removeWireIndexList[thisWireIndex]:
                if len(self[thisWireIndex])<2:
                    removeWireIndexList[thisWireIndex]=True
            if not removeWireIndexList[thisWireIndex]:
                for otherWireIndex in range(thisWireIndex+1,len(self)):
                    thisWireStartPoint=self[thisWireIndex][0].coord
                    thisWireEndPoint=self[thisWireIndex][-1].coord
                    if not removeWireIndexList[otherWireIndex]:
                        if len(self[otherWireIndex])<2:
                            removeWireIndexList[otherWireIndex]=True
                    if not removeWireIndexList[otherWireIndex]:
                        otherWireStartPoint=self[otherWireIndex][0].coord
                        otherWireEndPoint=self[otherWireIndex][-1].coord
                        if thisWireEndPoint == otherWireStartPoint:
                            self[thisWireIndex]=self[thisWireIndex]+self[otherWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
                        elif thisWireStartPoint == otherWireEndPoint:
                            self[thisWireIndex]=self[otherWireIndex]+self[thisWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
                        elif thisWireStartPoint == otherWireStartPoint:
                            self[otherWireIndex].reverse()
                            self[thisWireIndex]= self[otherWireIndex]+self[thisWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
                        elif thisWireEndPoint == otherWireEndPoint:
                            self[otherWireIndex].reverse()
                            self[thisWireIndex]=self[thisWireIndex]+self[otherWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
        # remove all of the wires to be removed
        keepDeletingWires = True
        while keepDeletingWires:
            keepDeletingWires = False
            for wireIndex in range(len(self)):
                if removeWireIndexList[wireIndex]==True:
                    del self[wireIndex]
                    del removeWireIndexList[wireIndex]
                    keepDeletingWires=True
                    break
        # now walk along all of the wires and put vertices at any locations where a wire vertex is along a straight line of another wire
        newWireList=WireList()
        for thisWire in self:
            newWire=Wire()
            thisWireSegmentStart=thisWire[0]
            newWire.append(thisWireSegmentStart)
            for vertex in thisWire[1:]:
                thisWireSegmentEnd = vertex
                vector=(thisWireSegmentEnd.coord[0]-thisWireSegmentStart.coord[0],thisWireSegmentEnd.coord[1]-thisWireSegmentStart.coord[1])
                if vector[0]==0:
                    # this is a north south line
                    if vector[1]>0:
                        step=(0,1) # this is a south going line
                    elif vector[1]<0:
                        step=(0,-1) # this is a north going line
                    else:
                        # this should not be possible
                        raise ValueError
                elif vector[1]==0:
                    # this is an east west line
                    if vector[0]>0:
                        step=(1,0) # this is an east going line
                    elif vector[0]<0:
                        step=(-1,0) # this is a west going line
                    else:
                        # this should not be possible
                        raise ValueError
                else:
                    # this is some kind of diagonal line
                    step=(0,0)
                if step != (0,0):
                    # step along this line checking the start and end points of all other lines
                    thisCoordToCheck = (thisWireSegmentStart.coord[0]+step[0],thisWireSegmentStart.coord[1]+step[1])
                    while thisCoordToCheck != thisWireSegmentEnd.coord:
                        vertexAddedAtThisCoordinate=False
                        for otherWire in self:
                            for otherVertex in otherWire:
                                if otherVertex.coord == thisCoordToCheck:
                                    # found one - need to insert a vertex into this wire
                                    newWire.append(Vertex(thisCoordToCheck))
                                    vertexAddedAtThisCoordinate=True
                                    break
                        if not vertexAddedAtThisCoordinate:
                            for device in deviceList:
                                if vertexAddedAtThisCoordinate:
                                    break
                                for pinCoordinate in device.partPicture.current.PinCoordinates():
                                    if pinCoordinate == thisCoordToCheck:
                                        newWire.append(Vertex(thisCoordToCheck))
                                        vertexAddedAtThisCoordinate=True
                                        break
                        thisCoordToCheck = (thisCoordToCheck[0]+step[0],thisCoordToCheck[1]+step[1])
                newWire.append(thisWireSegmentEnd)
                thisWireSegmentStart=thisWireSegmentEnd
            newWireList.append(newWire)
        self.wires=newWireList
    def EquiPotentialWireList(self):
            wireList = copy.deepcopy(self.wires)
            # for the purposes of the netlist, wires are just lists of vertices
            # any vertex shared among wires makes them equipotential, so even though we would not draw the wires
            # as added, their list of vertices can be added to form the equipotential line for purposes of determining
            # device connections
            for wireIndex in range(len(wireList)):
                if len(wireList[wireIndex])>0:
                    for otherWireIndex in range(len(wireList)):
                        if len(wireList[otherWireIndex])>0 and wireIndex != otherWireIndex:
                            if len(set(wireList[wireIndex].CoordinateList()).intersection(set(wireList[otherWireIndex].CoordinateList())))>0:
                                # there is a common vertex among these wires
                                # add the wires
                                wireList[wireIndex]=wireList[wireIndex]+wireList[otherWireIndex]
                                wireList[otherWireIndex]=Wire()
            # now keep only surviving wires
            newWireList=WireList()
            for wire in wireList:
                if len(wire)>0:
                    newWireList.append(wire)
            return newWireList
