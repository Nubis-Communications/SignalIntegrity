"""
Wire.py
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
import xml.etree.ElementTree as et
import copy
import math

class Segment(object):
    def __init__(self,startVertex,endVertex):
        self.selected=startVertex.selected and endVertex.selected
        self.startCoord=startVertex.coord
        self.endCoord=endVertex.coord
    def __getitem__(self,item):
        if item==0:
            return self.startCoord
        elif item==1:
            return self.endCoord
    def Direction(self):
        vector=(self.endCoord[0]-self.startCoord[0],self.endCoord[1]-self.startCoord[1])
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
    def IsAt(self,coord,augmentor,distanceAllowed):
        xc=float(coord[0]+augmentor[0])
        yc=float(coord[1]+augmentor[1])
        xi=self.startCoord[0]
        yi=self.startCoord[1]
        xf=self.endCoord[0]
        yf=self.endCoord[1]
        if xc < min(xi,xf)-distanceAllowed:
            return False
        if xc > max(xi,xf)+distanceAllowed:
            return False
        if yc < min(yi,yf)-distanceAllowed:
            return False
        if yc > max(yi,yf)+distanceAllowed:
            return False
        deltax=xf-xi
        deltay=yf-yi
        if deltax == 0:
            R=abs(xc-xi)
        elif deltay == 0:
            R=abs(yc-yi)
        else:
            m=float(deltay)/float(deltax)
            b=yi-xi*m
            # m and b are equation of line forming wire segment
            mp=-1./m
            bp=yc-xc*mp
            # mp and bp are equation of line perpendicular to wire segment passing
            # through coordinate given
            #
            # now to find the intersection of the lines
            # y=m*x+b
            # y=mp*x+bp
            x=(bp-b)/(m-mp)
            y=m*x+b
            R=math.sqrt((xc-x)*(xc-x)+(yc-y)*(yc-y))
        return (R <= distanceAllowed)

class SegmentList(object):
    def __init__(self,wire):
        self.segmentList=[]
        if len(wire)>=2:
            startVertex=wire[0]
            for endVertex in wire[1:]:
                self.segmentList.append(Segment(startVertex,endVertex))
                startVertex=endVertex
    def __getitem__(self,item):
        return self.segmentList[item]
    def __len__(self):
        return len(self.segmentList)
    def Wire(self):
        vertexList=[]
        if len(self)==0:
            return
        for segmentIndex in range(0,len(self)):
            segment=self[segmentIndex]
            if segmentIndex==0:
                vertexList.append(Vertex(segment[0],segment.selected))
                vertexList.append(Vertex(segment[1],segment.selected))
            else:
                vertexList[-1].selected = segment.selected or vertexList[-1].selected
                vertexList.append(Vertex(segment[1],segment.selected))
        return Wire(vertexList)

class Vertex(object):
    def __init__(self,coord,selected=False):
        self.coord=coord
        self.selected=selected
    def __getitem__(self,item):
        return self.coord[item]
    # Legacy File Format
    def InitFromXml(self,vertexElement):
        self.selected=False
        self.coord = eval(vertexElement.text)
        return self
    def IsAt(self,coord,augmentor,distanceAllowed):
        xc=float(coord[0]+augmentor[0])
        yc=float(coord[1]+augmentor[1])
        x=self.coord[0]
        y=self.coord[1]
        if xc < x-distanceAllowed:
            return False
        if xc > x+distanceAllowed:
            return False
        if yc < y-distanceAllowed:
            return False
        if yc > y+distanceAllowed:
            return False
        return True
    def IsIn(self,i,f,ia,fa):
        minx=min(float(i[0]+ia[0]),float(f[0]+fa[0]))
        miny=min(float(i[1]+ia[1]),float(f[1]+fa[1]))
        maxx=max(float(i[0]+ia[0]),float(f[0]+fa[0]))
        maxy=max(float(i[1]+ia[1]),float(f[1]+fa[1]))
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
        self.vertexList=copy.deepcopy(vertexList)
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
                canvas.create_line((segmentCoord[0]+x)*grid,
                                    (segmentCoord[1]+y)*grid,
                                    (vertex[0]+x)*grid,
                                    (vertex[1]+y)*grid,
                                    fill=('blue' if (segmentCoord.selected and vertex.selected) else 'black'))
                segmentCoord=vertex
            if selected:
                for vertex in self:
                    size=max(1,grid/8)
                    canvas.create_line((vertex[0]+x)*grid-size,
                                       (vertex[1]+y)*grid-size,
                                       (vertex[0]+x)*grid+size,
                                       (vertex[1]+y)*grid+size,
                                       fill=('blue' if vertex.selected else 'black'),
                                       width=(2 if vertex.selected else 1))
                    canvas.create_line((vertex[0]+x)*grid+size,
                                       (vertex[1]+y)*grid-size,
                                       (vertex[0]+x)*grid-size,
                                       (vertex[1]+y)*grid+size,
                                       fill=('blue' if vertex.selected else 'black'),
                                       width=(2 if vertex.selected else 1))
    def __add__(self,other):
        if isinstance(other, Wire):
            return Wire(self.vertexList+other.vertexList)
        elif isinstance(other,list):
            return Wire(self.vertexList+other)
    def InitFromProject(self,wireProject):
        self.__init__()
        self.vertexList=[Vertex(eval(vertexProject.GetValue('Coord')),vertexProject.GetValue('Selected')) for vertexProject in wireProject.GetValue('Vertex')]
        return self
    # Legacy File Format
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
    def InitFromProject(self,wiresListProject):
        self.__init__()
        self.wires=[Wire().InitFromProject(wireProject) for wireProject in wiresListProject]
        return self
    # Legacy File Format
    def InitFromXml(self,wiresElement):
        self.__init__()
        for child in wiresElement:
            if child.tag == 'wire':
                wire=Wire()
                wire.InitFromXml(child)
                self.wires.append(wire)
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
    def DotList(self,deviceList):
        dotList=[]
        # make a list of all coordinates
        coordList=[]
        for device in deviceList:
            coordList=coordList+device.PinCoordinates()
        for wire in self:
            vertexCoordinates=[vertex.coord for vertex in wire]
            #vertex coordinates count as two except for the endpoints
            coordList=coordList+vertexCoordinates+vertexCoordinates[1:-1]
        uniqueCoordList=list(set(coordList))
        for coord in uniqueCoordList:
            if coordList.count(coord)>2:
                dotList.append(coord)
        return dotList
    def ConsolidateWires(self,schematic):
        deviceList=schematic.deviceList
        self.RemoveEmptyWires()
        self.RemoveDuplicateVertices()
        self.InsertNeededVertices(deviceList)
        dotList=self.DotList(deviceList)
        self.SplitDottedWires(dotList)
        self.JoinUnDottedWires(dotList)
        self.RemoveUnneededVertices()
    def EquiPotentialWireList(self):
            wireList = copy.deepcopy(self.wires)
            # for the purposes of the netlist, wires are just lists of vertices
            # any vertex shared among wires makes them equipotential, so even though we would not draw the wires
            # as added, their list of vertices can be added to form the equipotential line for purposes of determining
            # device connections
            for wireIndex in range(len(wireList)):
                joinedOne=True
                while joinedOne:
                    joinedOne=False
                    if len(wireList[wireIndex])>0:
                        for otherWireIndex in range(len(wireList)):
                            if len(wireList[otherWireIndex])>0 and wireIndex != otherWireIndex:
                                if len(set(wireList[wireIndex].CoordinateList()).intersection(set(wireList[otherWireIndex].CoordinateList())))>0:
                                    # there is a common vertex among these wires
                                    # add the wires
                                    wireList[wireIndex]=wireList[wireIndex]+wireList[otherWireIndex]
                                    wireList[wireIndex].vertexList=[Vertex(survived) for survived in list(set([vertex.coord for vertex in wireList[wireIndex].vertexList]))]
                                    wireList[otherWireIndex]=Wire()
                                    joinedOne=True
                                    break
            # now keep only surviving wires
            newWireList=WireList()
            for wire in wireList:
                if len(wire)>0:
                    newWireList.append(wire)
            return newWireList
