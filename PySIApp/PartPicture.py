'''
Created on Oct 15, 2015

@author: peterp
'''
import xml.etree.ElementTree as et

from PartPin import *

class PartPicture(object):
    def __init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation):
        self.origin=origin
        self.pinList=pinList
        self.innerBox=innerBox
        self.boundingBox=boundingBox
        self.visiblePartPropertyList=[]
        self.propertiesLocation = propertiesLocation
    def InsertVisiblePartProperties(self,visiblePartPropertyList):
        self.visiblePartPropertyList=visiblePartPropertyList
    def SetOrigin(self,xy):
        self.origin=tuple(xy)
    def IsAt(self,xy):
        x=xy[0]
        y=xy[1]
        if x < self.innerBox[0][0]+self.origin[0]:
            return False
        if x > self.innerBox[1][0]+self.origin[0]:
            return False
        if y < self.innerBox[0][1]+self.origin[1]:
            return False
        if y > self.innerBox[1][1]+self.origin[1]:
            return False
        return True
    def WhereInPart(self,xy):
        return (xy[0]-self.origin[0],xy[1]-self.origin[1])
    def DrawDevice(self,canvas,grid,drawingOrigin):
        for pin in self.pinList:
            pin.DrawPin(canvas,grid,(self.origin[0]+drawingOrigin[0],self.origin[1]+drawingOrigin[1]))
        for v in range(len(self.visiblePartPropertyList)):
            canvas.create_text((drawingOrigin[0]+self.origin[0]+self.propertiesLocation[0])*grid,(drawingOrigin[1]+self.origin[1]+self.propertiesLocation[1])*grid-10*v-10,text=self.visiblePartPropertyList[v],anchor='nw')
    def PinCoordinates(self):
        return [(pin.pinConnectionPoint[0]+self.origin[0],pin.pinConnectionPoint[1]+self.origin[1]) for pin in self.pinList]


class PartPictureBox(PartPicture):
    def __init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation):
        PartPicture.__init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        canvas.create_rectangle((drawingOrigin[0]+self.origin[0]+self.innerBox[0][0])*grid,
                                (drawingOrigin[1]+self.origin[1]+self.innerBox[0][1])*grid,
                                (drawingOrigin[0]+self.origin[0]+self.innerBox[1][0])*grid,
                                (drawingOrigin[1]+self.origin[1]+self.innerBox[1][1])*grid)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureOnePort(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l')],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1))

class PartPictureOnePortLeft(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l')],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1))

class PartPictureOnePortRight(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(4,1),'r')],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1))

class PartPictureOnePortUp(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(2,-1),'t')],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1))

class PartPictureOnePortDown(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(2,3),'b')],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1))

class PartPictureTwoPortLeft(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(4,1),'r')],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1))

class PartPictureTwoPortRight(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(4,1),'r'),PartPin(2,(0,1),'l')],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1))

class PartPictureTwoPortUp(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(1,0),'t'),PartPin(2,(1,4),'b')],[(0,1),(2,3)],[(0,0),(2,4)],(3,1))

class PartPictureTwoPortDown(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(1,4),'b'),PartPin(2,(1,0),'t')],[(0,1),(2,3)],[(0,0),(2,4)],(3,1))

class PartPictureThreePort(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l'),PartPin(3,(4,2),'r')],[(1,0),(3,4)],[(0,0),(4,4)],(1,-1))

class PartPictureFourPort(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l'),PartPin(3,(4,1),'r'),PartPin(4,(4,3),'r')],[(1,0),(3,4)],[(0,0),(4,4)],(1,-1))

class PartPicturePortLeft(PartPicture):
    def __init__(self):
        PartPicture.__init__(self,(0,0),[PartPin(1,(3,1),'r',False)],[(1,1),(3,1)],[(0,0),(3,2)],(1,1))
    def DrawDevice(self,canvas,grid,drawingOrigin):
        canvas.create_line((drawingOrigin[0]+self.origin[0]+1)*grid+grid/2,
                                (drawingOrigin[1]+self.origin[1]+0)*grid+grid/2,
                                (drawingOrigin[0]+self.origin[0]+2)*grid,
                                (drawingOrigin[1]+self.origin[1]+1)*grid)
        canvas.create_line((drawingOrigin[0]+self.origin[0]+1)*grid+grid/2,
                                (drawingOrigin[1]+self.origin[1]+1)*grid+grid/2,
                                (drawingOrigin[0]+self.origin[0]+2)*grid,
                                (drawingOrigin[1]+self.origin[1]+1)*grid)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPicturePortRight(PartPicture):
    def __init__(self):
        PartPicture.__init__(self,(0,0),[PartPin(1,(0,1),'l',False)],[(0,1),(2,1)],[(0,0),(3,2)],(2,1))
    def DrawDevice(self,canvas,grid,drawingOrigin):
        canvas.create_line((drawingOrigin[0]+self.origin[0]+1)*grid+grid/2,
                                (drawingOrigin[1]+self.origin[1]+0)*grid+grid/2,
                                (drawingOrigin[0]+self.origin[0]+1)*grid,
                                (drawingOrigin[1]+self.origin[1]+1)*grid)
        canvas.create_line((drawingOrigin[0]+self.origin[0]+1)*grid+grid/2,
                                (drawingOrigin[1]+self.origin[1]+1)*grid+grid/2,
                                (drawingOrigin[0]+self.origin[0]+1)*grid,
                                (drawingOrigin[1]+self.origin[1]+1)*grid)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPicturePortUp(PartPicture):
    def __init__(self):
        PartPicture.__init__(self,(0,0),[PartPin(1,(1,0),'t',False)],[(1,0),(1,2)],[(0,0),(2,3)],(1,2))
    def DrawDevice(self,canvas,grid,drawingOrigin):
        canvas.create_line((drawingOrigin[0]+self.origin[0]+0)*grid+grid/2,
                                (drawingOrigin[1]+self.origin[1]+1)*grid+grid/2,
                                (drawingOrigin[0]+self.origin[0]+1)*grid,
                                (drawingOrigin[1]+self.origin[1]+1)*grid)
        canvas.create_line((drawingOrigin[0]+self.origin[0]+1)*grid+grid/2,
                                (drawingOrigin[1]+self.origin[1]+1)*grid+grid/2,
                                (drawingOrigin[0]+self.origin[0]+1)*grid,
                                (drawingOrigin[1]+self.origin[1]+1)*grid)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPicturePortDown(PartPicture):
    def __init__(self):
        PartPicture.__init__(self,(0,0),[PartPin(1,(1,3),'b',False)],[(1,1),(1,3)],[(0,0),(2,3)],(1,1))
    def DrawDevice(self,canvas,grid,drawingOrigin):
        canvas.create_line((drawingOrigin[0]+self.origin[0]+0)*grid+grid/2,
                                (drawingOrigin[1]+self.origin[1]+1)*grid+grid/2,
                                (drawingOrigin[0]+self.origin[0]+1)*grid,
                                (drawingOrigin[1]+self.origin[1]+2)*grid)
        canvas.create_line((drawingOrigin[0]+self.origin[0]+1)*grid+grid/2,
                                (drawingOrigin[1]+self.origin[1]+1)*grid+grid/2,
                                (drawingOrigin[0]+self.origin[0]+1)*grid,
                                (drawingOrigin[1]+self.origin[1]+2)*grid)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureCapacitorTwoPortLeft(PartPicture):
    def __init__(self):
        PartPicture.__init__(self,(0,0),[PartPin(1,(0,1),'l',False),PartPin(2,(4,1),'r',False)],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1))
    def DrawDevice(self,canvas,grid,drawingOrigin):
        ty=(drawingOrigin[1]+self.origin[1])*grid
        my=ty+grid
        by=my+grid
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        lpx=lx+2*grid/3
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid
        rpx=rx-2*grid/3
        canvas.create_line(lx,my,lpx,my)
        canvas.create_line(rx,my,rpx,my)
        canvas.create_line(lpx,ty,lpx,by)
        canvas.create_line(rpx,ty,rpx,by)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureCapacitorTwoPortUp(PartPicture):
    def __init__(self):
        PartPicture.__init__(self,(0,0),[PartPin(1,(1,0),'t',False),PartPin(2,(1,4),'b',False)],[(0,1),(2,3)],[(0,0),(2,4)],(3,1))
    def DrawDevice(self,canvas,grid,drawingOrigin):
        lx=(drawingOrigin[0]+self.origin[0])*grid
        mx=lx+grid
        rx=mx+grid
        iy=(drawingOrigin[1]+self.origin[1]+1)*grid
        ty=iy+2*grid/3
        fy=(drawingOrigin[1]+self.origin[1]+3)*grid
        by=fy-2*grid/3
        canvas.create_line(mx,iy,mx,ty)
        canvas.create_line(lx,ty,rx,ty)
        canvas.create_line(lx,by,rx,by)
        canvas.create_line(mx,fy,mx,by)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureResistorTwoPortLeft(PartPicture):
    def __init__(self):
        PartPicture.__init__(self,(0,0),[PartPin(1,(0,1),'l',False),PartPin(2,(4,1),'r',False)],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1))
    def DrawDevice(self,canvas,grid,drawingOrigin):
        my=(drawingOrigin[1]+self.origin[1])*grid+grid
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid
        canvas.create_line(lx,my,
                           lx+grid/4,my-grid/2,
                           lx+grid/2,my+grid/2,
                           lx+3*grid/4,my-grid/2,
                           lx+grid,my+grid/2,
                           rx-3*grid/4,my-grid/2,
                           rx-grid/2,my+grid/2,
                           rx-grid/4,my-grid/2,
                           rx,my)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureResistorTwoPortUp(PartPicture):
    def __init__(self):
        PartPicture.__init__(self,(0,0),[PartPin(1,(1,0),'t',False),PartPin(2,(1,4),'b',False)],[(0,1),(2,3)],[(0,0),(2,4)],(3,1))
    def DrawDevice(self,canvas,grid,drawingOrigin):
        mx=(drawingOrigin[0]+self.origin[0])*grid+grid
        iy=(drawingOrigin[1]+self.origin[1]+1)*grid
        by=(drawingOrigin[1]+self.origin[1]+3)*grid
        canvas.create_line(mx,iy,
                           mx+grid/2,iy+grid/4,
                           mx-grid/2,iy+grid/2,
                           mx+grid/2,iy+3*grid/4,
                           mx-grid/2,iy+grid,
                           mx+grid/2,by-3*grid/4,
                           mx-grid/2,by-grid/2,
                           mx+grid/2,by-grid/4,
                           mx,by)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureGround(PartPicture):
    def __init__(self,origin=(0,0)):
        PartPicture.__init__(self,origin,[PartPin(1,(1,0),'t',False)],[(0,1),(3,2)],[(0,0),(3,2)],(3,1))
    def DrawDevice(self,canvas,grid,drawingOrigin):
        lx=(drawingOrigin[0]+self.origin[0])*grid
        mx=lx+grid
        rx=mx+grid
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid
        by=ty+grid
        canvas.create_polygon(lx,ty,rx,ty,mx,by,lx,ty)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariable(object):
    def __init__(self,partPictureClassList,partPictureSelected=0):
        self.partPictureClassList = partPictureClassList
        self.partPictureSelected = partPictureSelected
        self.SwitchPartPicture(self.partPictureSelected)
    def PartPicture(self):
        return self.current
    def SwitchPartPicture(self,item):
        self.partPictureSelected = item
        self.current=eval(self.partPictureClassList[self.partPictureSelected])()
    def xml(self):
        thisElement=et.Element('part_picture')
        classNamesElement = et.Element('class_names')
        classNamesElementsList = []
        for className in self.partPictureClassList:
            classNameElement=et.Element('class_name')
            classNameElement.text=className
            classNamesElementsList.append(classNameElement)
        classNamesElement.extend(classNamesElementsList)
        selectedElement = et.Element('selected')
        selectedElement.text = str(self.partPictureSelected)
        originElement = et.Element('origin')
        originElement.text=str(self.current.origin)
        thisElement.extend([classNamesElement,selectedElement,originElement])
        return thisElement

class PartPictureXMLClassFactory(object):
    def __init__(self,xml):
        partPictureClassList=[]
        partPictureSelected = 0
        origin=(0,0)
        for item in xml:
            if item.tag == 'class_names':
                for classNameElement in item:
                    if classNameElement.tag == 'class_name':
                        partPictureClassList.append(classNameElement.text)
            elif item.tag == 'selected':
                partPictureSelected = int(item.text)
            elif item.tag == 'origin':
                origin = eval(item.text)
        self.result=PartPictureVariable(partPictureClassList,partPictureSelected)
        self.result.current.SetOrigin(origin)

class PartPictureVariableOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureOnePortLeft','PartPictureOnePortRight','PartPictureOnePortUp','PartPictureOnePortDown'])

class PartPictureVariableTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureTwoPortLeft','PartPictureTwoPortRight','PartPictureTwoPortUp','PartPictureTwoPortDown'])

class PartPictureVariableThreePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureThreePort'])

class PartPictureVariableFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureFourPort'])

class PartPictureVariableCapacitorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCapacitorTwoPortLeft','PartPictureCapacitorTwoPortUp'])

class PartPictureVariableResistorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureResistorTwoPortLeft','PartPictureResistorTwoPortUp'])

class PartPictureVariableGround(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureGround'])

class PartPictureVariablePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPicturePortLeft','PartPicturePortRight','PartPicturePortUp','PartPicturePortDown'])

