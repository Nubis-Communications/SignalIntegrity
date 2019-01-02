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
import copy
import math

class Segment(object):
    def __init__(self,startVertex,endVertex):
        self.selected=startVertex['Selected'] and endVertex['Selected']
        self.startCoord=startVertex['Coord']
        self.endCoord=endVertex['Coord']
    def __getitem__(self,item):
        if not isinstance(item,int):
            raise ValueError
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
                vertexList[-1]['Selected'] = segment.selected or vertexList[-1]['Selected']
                vertexList.append(Vertex(segment[1],segment.selected))
        return Wire(vertexList)

from SignalIntegrity.App.ProjectFile import VertexConfiguration

class Vertex(VertexConfiguration):
    def __init__(self,coord=(0,0),selected=False):
        VertexConfiguration.__init__(self)
        self['Coord']=coord
        self['Selected']=selected
    def __getitem__(self,item):
        if isinstance(item,(int,slice)):
            return self['Coord'][item]
        else: return VertexConfiguration.__getitem__(self,item)
    def IsAt(self,coord,augmentor,distanceAllowed):
        xc=float(coord[0]+augmentor[0])
        yc=float(coord[1]+augmentor[1])
        x,y=self['Coord']
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
        x,y=self['Coord']
        if minx > x:
            return False
        if maxx < x:
            return False
        if miny > y:
            return False
        if maxy < y:
            return False
        return True

from SignalIntegrity.App.ProjectFileBase import XMLConfiguration

class Wire(XMLConfiguration):
    def __init__(self,vertexList=None):
        if vertexList==None:
            vertexList=[]
        XMLConfiguration.__init__(self,'Wire')
        self.Add(XMLProperty('Vertices',[Vertex(vertex['Coord'],vertex['Selected']) for vertex in vertexList],'array',arrayType=Vertex()))
    def __getitem__(self,item):
        if isinstance(item,(slice,int)):
            return self['Vertices'][item]
        else: return XMLConfiguration.__getitem__(self,item)
    def __setitem__(self,item,value):
        if isinstance(item,int):
            if not isinstance(value,Vertex):
                raise ValueError
            self['Vertices'][item]=value
        else: XMLConfiguration.__setitem__(self,item,value)
    def __delitem__(self,item):
        if isinstance(item,int):
            del self['Vertices'][item]
        else:
            raise ValueError
    def __len__(self):
        return len(self['Vertices'])
    def append(self,item):
        self['Vertices'].append(item)
    def reverse(self):
        self['Vertices'].reverse()
    def DrawWire(self,canvas,grid,x,y):
        selected=False
        verticesProject=self['Vertices']
        for vertex in verticesProject:
            if vertex['Selected']:
                selected = True
        if len(verticesProject) >= 2:
            segmentCoord=verticesProject[0]
            for vertex in verticesProject[1:]:
                canvas.create_line((segmentCoord[0]+x)*grid,
                                    (segmentCoord[1]+y)*grid,
                                    (vertex[0]+x)*grid,
                                    (vertex[1]+y)*grid,
                                    fill=('blue' if (segmentCoord['Selected'] and vertex['Selected']) else 'black'))
                segmentCoord=vertex
            if selected:
                for vertex in verticesProject:
                    size=max(1,grid/8)
                    canvas.create_line((vertex[0]+x)*grid-size,
                                       (vertex[1]+y)*grid-size,
                                       (vertex[0]+x)*grid+size,
                                       (vertex[1]+y)*grid+size,
                                       fill=('blue' if vertex['Selected'] else 'black'),
                                       width=(2 if vertex['Selected'] else 1))
                    canvas.create_line((vertex[0]+x)*grid+size,
                                       (vertex[1]+y)*grid-size,
                                       (vertex[0]+x)*grid-size,
                                       (vertex[1]+y)*grid+size,
                                       fill=('blue' if vertex['Selected'] else 'black'),
                                       width=(2 if vertex['Selected'] else 1))
    def __add__(self,other):
        if isinstance(other, Wire):
            return Wire(self['Vertices']+other['Vertices'])
        elif isinstance(other,list):
            return Wire(self['Vertices']+other)
    def InitFromProject(self,wireProject):
        self.__init__()
        self['Vertices']=[Vertex(vertexProject['Coord'],vertexProject['Selected']) for vertexProject in wireProject['Vertices']]
        return self
    def CoordinateList(self):
        return [vertex['Coord'] for vertex in self]


from SignalIntegrity.App.ProjectFileBase import XMLProperty

class WireList(XMLProperty):
    def __init__(self):
        XMLProperty.__init__(self,'Wires',[Wire() for _ in range(0)],'array',arrayType=Wire())
    def InitFromProject(self,wiresListProject):
        self.__init__()
        self.SetValue(None,[Wire().InitFromProject(wireProject) for wireProject in wiresListProject])
        return self
    def RemoveEmptyWires(self):
        wiresNeedRemoval=False
        wl=self.GetValue()
        for wire in wl:
            if len(wire)<2:
                wiresNeedRemoval=True
                break
        if not wiresNeedRemoval:
            return
        nwl=WireList().GetValue()
        for wire in wl:
            if len(wire)>=2:
                nwl.append(wire)
        self.SetValue(None,nwl)
    def RemoveDuplicateVertices(self):
        hasDuplicateVertices=False
        wl=self.GetValue()
        for wire in wl:
            if hasDuplicateVertices:
                break
            if len(wire)<1:
                break
            lastVertexCoordinate=wire[0]['Coord']
            for vertex in wire[1:]:
                thisVertexCoordinate=vertex['Coord']
                if thisVertexCoordinate==lastVertexCoordinate:
                    hasDuplicateVertices=True
                    break
                lastVertexCoordinate=thisVertexCoordinate
        if not hasDuplicateVertices:
            return
        nwl=WireList().GetValue()
        for wire in wl:
            if len(wire)<1:
                continue
            newWire=Wire()
            lastVertex=wire[0]
            newWire.append(lastVertex)
            for thisVertex in wire[1:]:
                if thisVertex['Coord'] != lastVertex['Coord']:
                    newWire.append(thisVertex)
                    lastVertex=thisVertex
            if len(newWire)>=2:
                nwl.append(newWire)
        self.SetValue(None,nwl)
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
        newWireList=WireList().GetValue()
        wl=self.GetValue()
        for thisWire in wl:
            newWire=Wire()
            thisWireSegmentStart=thisWire[0]
            newWire.append(thisWireSegmentStart)
            for vertex in thisWire[1:]:
                thisWireSegmentEnd = vertex
                vector=(thisWireSegmentEnd['Coord'][0]-thisWireSegmentStart['Coord'][0],thisWireSegmentEnd['Coord'][1]-thisWireSegmentStart['Coord'][1])
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
                    thisCoordToCheck = (thisWireSegmentStart['Coord'][0]+step[0],thisWireSegmentStart['Coord'][1]+step[1])
                    while thisCoordToCheck != thisWireSegmentEnd['Coord']:
                        vertexAddedAtThisCoordinate=False
                        for otherWire in wl:
                            for otherVertex in otherWire:
                                if otherVertex['Coord'] == thisCoordToCheck:
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
        self.SetValue(None,newWireList)
    def SplitDottedWires(self,dotList):
        wl=self.GetValue()
        splitAWire=True
        while splitAWire:
            splitAWire=False
            for wireIndex in range(len(wl)):
                wire = wl[wireIndex]
                if splitAWire:
                    break
                for vertexIndex in range(1,len(wire)-1):
                    if splitAWire:
                        break
                    for dot in dotList:
                        if wire[vertexIndex]['Coord'] == dot:
                            newWire=Wire(wire[vertexIndex:])
                            wl[wireIndex]=Wire(wire[:vertexIndex+1])
                            wl.append(newWire)
                            splitAWire=True
                            break
    def RemoveUnneededVertices(self):
        unneededVertex=False
        wl=self.GetValue()
        for wire in wl:
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
        nwl=WireList().GetValue()
        for wire in wl:
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
            nwl.append(newWire)
        self.SetValue(None,nwl)
    def JoinUnDottedWires(self,dotList):
        wl=self.GetValue()
        removeWireIndexList = [False for index in range(len(wl))]
        for thisWireIndex in range(len(wl)):
            if not removeWireIndexList[thisWireIndex]:
                if len(wl[thisWireIndex])<2:
                    removeWireIndexList[thisWireIndex]=True
            if not removeWireIndexList[thisWireIndex]:
                for otherWireIndex in range(thisWireIndex+1,len(wl)):
                    thisWireStartPoint=wl[thisWireIndex][0]['Coord']
                    thisWireStartPointInDotList = thisWireStartPoint in dotList
                    thisWireEndPoint=wl[thisWireIndex][-1]['Coord']
                    thisWireEndPointInDotList = thisWireEndPoint in dotList
                    if not removeWireIndexList[otherWireIndex]:
                        if len(wl[otherWireIndex])<2:
                            removeWireIndexList[otherWireIndex]=True
                    if not removeWireIndexList[otherWireIndex]:
                        otherWireStartPoint=wl[otherWireIndex][0]['Coord']
                        otherWireStartPointInDotList = otherWireStartPoint in dotList
                        otherWireEndPoint=wl[otherWireIndex][-1]['Coord']
                        otherWireEndPointInDotList = otherWireEndPoint in dotList
                        if thisWireEndPoint == otherWireStartPoint and not thisWireEndPointInDotList and not otherWireStartPointInDotList:
                            wl[thisWireIndex]=wl[thisWireIndex]+wl[otherWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
                        elif thisWireStartPoint == otherWireEndPoint and not thisWireStartPointInDotList and not otherWireEndPointInDotList:
                            wl[thisWireIndex]=wl[otherWireIndex]+wl[thisWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
                        elif thisWireStartPoint == otherWireStartPoint and not thisWireStartPointInDotList and not otherWireStartPointInDotList:
                            wl[otherWireIndex].reverse()
                            wl[thisWireIndex]= wl[otherWireIndex]+wl[thisWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
                        elif thisWireEndPoint == otherWireEndPoint and not thisWireEndPointInDotList and not otherWireEndPointInDotList:
                            wl[otherWireIndex].reverse()
                            wl[thisWireIndex]=wl[thisWireIndex]+wl[otherWireIndex][1:]
                            removeWireIndexList[otherWireIndex]=True
        if not True in removeWireIndexList:
            return
        # remove all of the wires to be removed
        keepDeletingWires = True
        while keepDeletingWires:
            keepDeletingWires = False
            for wireIndex in range(len(wl)):
                if removeWireIndexList[wireIndex]==True:
                    del wl[wireIndex]
                    del removeWireIndexList[wireIndex]
                    keepDeletingWires=True
                    break
        pass
    def DotList(self,deviceList):
        dotList=[]
        wl=self.GetValue()
        # make a list of all coordinates
        coordList=[]
        for device in deviceList:
            coordList=coordList+device.PinCoordinates()
        for wire in wl:
            vertexCoordinates=[vertex['Coord'] for vertex in wire]
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
            wireList = copy.deepcopy(self.GetValue())
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
                                    wireList[wireIndex]['Vertices']=wireList[wireIndex]['Vertices']+wireList[otherWireIndex]['Vertices']
                                    wireList[wireIndex]['Vertices']=[Vertex(survived) for survived in list(set([vertex['Coord'] for vertex in wireList[wireIndex]['Vertices']]))]
                                    wireList[otherWireIndex]=Wire()
                                    joinedOne=True
                                    break
            # now keep only surviving wires
            newWireList=WireList().GetValue()
            for wire in wireList:
                if len(wire)>0:
                    newWireList.append(wire)
            return newWireList
