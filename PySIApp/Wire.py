'''
Created on Nov 8, 2015

@author: peterp
'''
import xml.etree.ElementTree as et

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
    def __init__(self,vertexList=None,selected=False):
        if vertexList==None:
            vertexList=[]
        self.vertexList=vertexList
        self.selected=selected
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
    def InitFromXml(self,wireElement):
        self.__init__()
        for child in wireElement:
            if child.tag == 'vertex':
                vertex=Vertex((0,0))
                vertex.InitFromXml(child)
                self.append(vertex)
        return self
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
    def ConsolidateWires(self):
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
                            thisVertex = wire[vertexIndex]
                            lastVertex = wire[vertexIndex-1]
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
                    thisWireStartPoint=self[thisWireIndex][0]
                    thisWireEndPoint=self[thisWireIndex][-1]
                    if not removeWireIndexList[otherWireIndex]:
                        if len(self[otherWireIndex])<2:
                            removeWireIndexList[otherWireIndex]=True
                    if not removeWireIndexList[otherWireIndex]:
                        otherWireStartPoint=self[otherWireIndex][0]
                        otherWireEndPoint=self[otherWireIndex][-1]
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

        
