'''
Created on Oct 15, 2015

@author: peterp
'''
import xml.etree.ElementTree as et
import copy

from PartPin import *

class CoordinateTranslater(object):
    def __init__(self,rotationPoint,rotationAngle):
        self.rotationPoint=rotationPoint
        self.rotationAngle=rotationAngle
    def Translate(self,coord):
        (rcosq,rsinq)=(coord[0]-self.rotationPoint[0],self.rotationPoint[1]-coord[1])
        if self.rotationAngle == '0':
            return (self.rotationPoint[0]+rcosq,self.rotationPoint[1]-rsinq)
        elif self.rotationAngle == '90':
            return (self.rotationPoint[0]-rsinq,self.rotationPoint[1]-rcosq)
        elif self.rotationAngle == '180':
            return (self.rotationPoint[0]-rcosq,self.rotationPoint[1]+rsinq)
        elif self.rotationAngle == '270':
            return (self.rotationPoint[0]+rsinq,self.rotationPoint[1]+rcosq)

class PartPicture(object):
    def __init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation,orientation):
        self.rotationPoint = ((innerBox[0][0]+innerBox[1][0])/2,(innerBox[0][1]+innerBox[1][1])/2)
        self.origin=origin
        self.pinListSupplied = pinList
        self.innerBoxSupplied = innerBox
        self.boundingBoxSupplied = boundingBox
        self.propertiesLocationSupplied = propertiesLocation
        self.ApplyOrientation(orientation)
    def ApplyOrientation(self,orientation):
        self.orientation = orientation
        ct=CoordinateTranslater(self.rotationPoint,self.orientation)
        self.pinList = copy.deepcopy(self.pinListSupplied)
        for pin in self.pinList:
            if pin.pinOrientation=='t':
                if self.orientation=='0':
                    pin.pinOrientation='t'
                elif self.orientation=='90':
                    pin.pinOrientation='l'
                elif self.orientation=='180':
                    pin.pinOrientation='b'
                elif self.orientation=='270':
                    pin.pinOrientation='r'
            elif pin.pinOrientation=='l':
                if self.orientation=='0':
                    pin.pinOrientation='l'
                elif self.orientation=='90':
                    pin.pinOrientation='b'
                elif self.orientation=='180':
                    pin.pinOrientation='r'
                elif self.orientation=='270':
                    pin.pinOrientation='t'
            elif pin.pinOrientation == 'b':
                if self.orientation=='0':
                    pin.pinOrientation='b'
                elif self.orientation=='90':
                    pin.pinOrientation='r'
                elif self.orientation=='180':
                    pin.pinOrientation='t'
                elif self.orientation=='270':
                    pin.pinOrientation='l'
            elif pin.pinOrientation=='r':
                if self.orientation=='0':
                    pin.pinOrientation='r'
                elif self.orientation=='90':
                    pin.pinOrientation='t'
                elif self.orientation=='180':
                    pin.pinOrientation='l'
                elif self.orientation=='270':
                    pin.pinOrientation='b'
            pin.pinConnectionPoint = ct.Translate(pin.pinConnectionPoint)
        self.boundingBox=[ct.Translate(self.boundingBoxSupplied[0]),ct.Translate(self.boundingBoxSupplied[1])]
        self.boundingBox=[(min(self.boundingBox[0][0],self.boundingBox[1][0]),min(self.boundingBox[0][1],self.boundingBox[1][1])),
                     (max(self.boundingBox[0][0],self.boundingBox[1][0]),max(self.boundingBox[0][1],self.boundingBox[1][1]))]
        self.innerBox=[ct.Translate(self.innerBoxSupplied[0]),ct.Translate(self.innerBoxSupplied[1])]
        self.innerBox=[(min(self.innerBox[0][0],self.innerBox[1][0]),min(self.innerBox[0][1],self.innerBox[1][1])),
                     (max(self.innerBox[0][0],self.innerBox[1][0]),max(self.innerBox[0][1],self.innerBox[1][1]))]
        self.propertiesLocation=ct.Translate(self.propertiesLocationSupplied)
    def Rotate(self):
        if self.orientation == '0':
            newOrientation = '90'
        elif self.orientation == '90':
            newOrientation = '180'
        elif self.orientation == '180':
            newOrientation = '270'
        elif self.orientation == '270':
            newOrientation = '0'
        self.ApplyOrientation(newOrientation)
    def CoordinateTranslater(self,grid,drawingOrigin):
        return CoordinateTranslater(((drawingOrigin[0]+self.origin[0]+self.rotationPoint[0])*grid,
                                (drawingOrigin[1]+self.origin[1]+self.rotationPoint[1])*grid),
                                self.orientation)
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
    def DrawDevice(self,canvas,grid,drawingOrigin,drawInnerBox=False):
        if drawInnerBox:
            canvas.create_rectangle((drawingOrigin[0]+self.origin[0]+self.innerBox[0][0])*grid,
            (drawingOrigin[1]+self.origin[1]+self.innerBox[0][1])*grid,
            (drawingOrigin[0]+self.origin[0]+self.innerBox[1][0])*grid,
            (drawingOrigin[1]+self.origin[1]+self.innerBox[1][1])*grid)
        for pin in self.pinList:
            pin.DrawPin(canvas,grid,(self.origin[0]+drawingOrigin[0],self.origin[1]+drawingOrigin[1]))
        for v in range(len(self.visiblePartPropertyList)):
            canvas.create_text((drawingOrigin[0]+self.origin[0]+self.propertiesLocation[0])*grid,(drawingOrigin[1]+self.origin[1]+self.propertiesLocation[1])*grid-10*v-10,text=self.visiblePartPropertyList[v],anchor='nw')
    def PinCoordinates(self):
        return [(pin.pinConnectionPoint[0]+self.origin[0],pin.pinConnectionPoint[1]+self.origin[1]) for pin in self.pinList]

class PartPictureXMLClassFactory(object):
    def __init__(self,xml):
        partPictureClassList=[]
        partPictureSelected = 0
        origin=(0,0)
        orientation='0'
        for item in xml:
            if item.tag == 'class_names':
                for classNameElement in item:
                    if classNameElement.tag == 'class_name':
                        partPictureClassList.append(classNameElement.text)
            elif item.tag == 'selected':
                partPictureSelected = int(item.text)
            elif item.tag == 'origin':
                origin = eval(item.text)
            elif item.tag == 'orientation':
                orientation = item.text
        self.result=PartPictureVariable(partPictureClassList,partPictureSelected,orientation)
        self.result.current.SetOrigin(origin)

class PartPictureVariable(object):
    def __init__(self,partPictureClassList,partPictureSelected=0,orientation='0'):
        self.partPictureClassList = partPictureClassList
        self.partPictureSelected = partPictureSelected
        self.orientation=orientation
        self.SwitchPartPicture(self.partPictureSelected)
    def PartPicture(self):
        return self.current
    def SwitchPartPicture(self,item):
        self.partPictureSelected = item
        self.current=eval(self.partPictureClassList[self.partPictureSelected])(self.orientation)
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
        orientationElement = et.Element('orientation')
        orientationElement.text=str(self.current.orientation)
        thisElement.extend([classNamesElement,selectedElement,originElement,orientationElement])
        return thisElement

class PartPictureBox(PartPicture):
    def __init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation,orientation):
        PartPicture.__init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation,orientation)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,True)

class PartPictureOnePort(PartPictureBox):
    def __init__(self,orientation):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l')],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1),orientation)

class PartPictureVariableOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureOnePort'])

class PartPictureTwoPort(PartPictureBox):
    def __init__(self,orientation):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(4,1),'r')],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1),orientation)

class PartPictureTwoPortSide(PartPictureBox):
    def __init__(self,orientation):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l')],[(1,0),(3,4)],[(0,0),(4,4)],(1,-1),orientation)    

class PartPictureVariableTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureTwoPort','PartPictureTwoPortSide'])

class PartPictureThreePort(PartPictureBox):
    def __init__(self,orientation):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l'),PartPin(3,(4,2),'r')],[(1,0),(3,4)],[(0,0),(4,4)],(1,-1),orientation)

class PartPictureThreePortSide(PartPictureBox):
    def __init__(self,orientation):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l'),PartPin(3,(0,5),'l')],[(1,0),(3,6)],[(0,0),(4,6)],(1,-1),orientation)    

class PartPictureVariableThreePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureThreePort','PartPictureThreePortSide'])

class PartPictureFourPort(PartPictureBox):
    def __init__(self,orientation):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l'),PartPin(3,(4,1),'r'),PartPin(4,(4,3),'r')],[(1,0),(3,4)],[(0,0),(4,4)],(1,-1),orientation)

class PartPictureFourPortSide(PartPictureBox):
    def __init__(self,orientation):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l'),PartPin(3,(0,5),'l'),PartPin(4,(0,7),'l')],[(1,0),(3,8)],[(0,0),(4,8)],(1,-1),orientation)    

class PartPictureVariableFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureFourPort','PartPictureFourPortSide'])

class PartPicturePort(PartPicture):
    def __init__(self,orientation):
        PartPicture.__init__(self,(0,0),[PartPin(1,(3,1),'r',False)],[(1,1),(3,1)],[(0,0),(3,2)],(1,1),orientation)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid+grid/2
        rx=(drawingOrigin[0]+self.origin[0]+2)*grid
        ty=(drawingOrigin[1]+self.origin[1]+0)*grid+grid/2
        my=(drawingOrigin[1]+self.origin[1]+1)*grid
        by=(drawingOrigin[1]+self.origin[1]+1)*grid+grid/2
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,ty)),ct.Translate((rx,my)),ct.Translate((lx,by))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],p[2][0],p[2][1])
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariablePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPicturePort'])

class PartPictureGround(PartPicture):
    def __init__(self,orientation):
        PartPicture.__init__(self,(0,0),[PartPin(1,(1,0),'t',True)],[(0,1),(3,2)],[(0,0),(3,2)],(3,1),orientation)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        lx=(drawingOrigin[0]+self.origin[0])*grid
        mx=lx+grid
        rx=mx+grid
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid
        by=ty+grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,ty)),ct.Translate((rx,ty)),ct.Translate((mx,by)),ct.Translate((lx,ty))]
        canvas.create_polygon(p[0][0],p[0][1],p[1][0],p[1][1],p[2][0],p[2][1],p[3][0],p[3][1])
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)
        
class PartPictureVariableGround(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureGround'])

class PartPictureResistorTwoPort(PartPicture):
    def __init__(self,orientation):
        PartPicture.__init__(self,(0,0),[PartPin(1,(0,1),'l',False),PartPin(2,(4,1),'r',False)],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1),orientation)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        my=(drawingOrigin[1]+self.origin[1])*grid+grid
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,my)),
           ct.Translate((lx+grid/4,my-grid/2)),
           ct.Translate((lx+grid/2,my+grid/2)),
           ct.Translate((lx+3*grid/4,my-grid/2)),
           ct.Translate((lx+grid,my+grid/2)),
           ct.Translate((rx-3*grid/4,my-grid/2)),
           ct.Translate((rx-grid/2,my+grid/2)),
           ct.Translate((rx-grid/4,my-grid/2)),
           ct.Translate((rx,my))]
        canvas.create_line(p[0][0],p[0][1],
                           p[1][0],p[1][1],
                           p[2][0],p[2][1],
                           p[3][0],p[3][1],
                           p[4][0],p[4][1],
                           p[5][0],p[5][1],
                           p[6][0],p[6][1],
                           p[7][0],p[7][1],
                           p[8][0],p[8][1])
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableResistorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureResistorTwoPort'])

class PartPictureCapacitorTwoPort(PartPicture):
    def __init__(self,orientation):
        PartPicture.__init__(self,(0,0),[PartPin(1,(0,1),'l',False),PartPin(2,(4,1),'r',False)],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1),orientation)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        ty=(drawingOrigin[1]+self.origin[1])*grid
        my=ty+grid
        by=my+grid
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        lpx=lx+2*grid/3
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid
        rpx=rx-2*grid/3
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[[ct.Translate((lx,my)),ct.Translate((lpx,my))],
           [ct.Translate((rx,my)),ct.Translate((rpx,my))],
           [ct.Translate((lpx,ty)),ct.Translate((lpx,by))],
           [ct.Translate((rpx,ty)),ct.Translate((rpx,by))]]
        canvas.create_line(p[0][0][0],p[0][0][1],p[0][1][0],p[0][1][1])
        canvas.create_line(p[1][0][0],p[1][0][1],p[1][1][0],p[1][1][1])
        canvas.create_line(p[2][0][0],p[2][0][1],p[2][1][0],p[2][1][1])
        canvas.create_line(p[3][0][0],p[3][0][1],p[3][1][0],p[3][1][1])
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCapacitorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCapacitorTwoPort'])

class PartPictureVoltageSourceTwoPort(PartPicture):
    def __init__(self,orientation):
        PartPicture.__init__(self,(0,0),[PartPin(2,(1,0),'t',False),PartPin(1,(1,4),'b',False)],[(0,1),(2,3)],[(0,0),(2,4)],(2,1),orientation)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        lx=(drawingOrigin[0]+self.origin[0]+self.innerBox[0][0])*grid
        ly=(drawingOrigin[1]+self.origin[1]+self.innerBox[0][1])*grid
        ux=(drawingOrigin[0]+self.origin[0]+self.innerBox[1][0])*grid
        uy=(drawingOrigin[1]+self.origin[1]+self.innerBox[1][1])*grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,ly)),ct.Translate((ux,uy))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1])
        px=(drawingOrigin[0]+self.origin[0]+self.innerBox[0][0])*grid+grid
        py=(drawingOrigin[1]+self.origin[1]+self.innerBox[0][1])*grid+grid-grid/2
        my=(drawingOrigin[1]+self.origin[1]+self.innerBox[0][1])*grid+grid+grid/2
        p=[[ct.Translate((px-grid/4,py)),ct.Translate((px+grid/4,py))],
           [ct.Translate((px,py-grid/4)),ct.Translate((px,py+grid/4))],
           [ct.Translate((px-grid/4,my)),ct.Translate((px+grid/4,my))]]
        canvas.create_line(p[0][0][0],p[0][0][1],p[0][1][0],p[0][1][1])
        canvas.create_line(p[1][0][0],p[1][0][1],p[1][1][0],p[1][1][1])
        canvas.create_line(p[2][0][0],p[2][0][1],p[2][1][0],p[2][1][1])        
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableVoltageSourceTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceTwoPort'])

class PartPictureVoltageSourceOnePort(PartPicture):
    def __init__(self,orientation):
        PartPicture.__init__(self,(0,0),[PartPin(1,(1,0),'t',False)],[(0,1),(2,5)],[(0,0),(2,5)],(2,1),orientation)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        lx=(drawingOrigin[0]+self.origin[0]+0)*grid
        ly=(drawingOrigin[1]+self.origin[1]+1)*grid
        ux=(drawingOrigin[0]+self.origin[0]+2)*grid
        uy=(drawingOrigin[1]+self.origin[1]+3)*grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,ly)),ct.Translate((ux,uy))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1])
        px=(drawingOrigin[0]+self.origin[0]+0)*grid+grid
        py=(drawingOrigin[1]+self.origin[1]+1)*grid+grid-grid/2
        my=(drawingOrigin[1]+self.origin[1]+1)*grid+grid+grid/2
        p=[[ct.Translate((px-grid/4,py)),ct.Translate((px+grid/4,py))],
           [ct.Translate((px,py-grid/4)),ct.Translate((px,py+grid/4))],
           [ct.Translate((px-grid/4,my)),ct.Translate((px+grid/4,my))]]
        canvas.create_line(p[0][0][0],p[0][0][1],p[0][1][0],p[0][1][1])
        canvas.create_line(p[1][0][0],p[1][0][1],p[1][1][0],p[1][1][1])
        canvas.create_line(p[2][0][0],p[2][0][1],p[2][1][0],p[2][1][1])
        gmx=(drawingOrigin[0]+self.origin[0]+1)*grid
        glx=gmx-grid
        grx=gmx+grid
        gby=(drawingOrigin[1]+self.origin[1]+5)*grid
        gty=gby-grid
        p=[ct.Translate((gmx,gty-grid)),
           ct.Translate((gmx,gty)),
           ct.Translate((glx,gty)),
           ct.Translate((gmx,gby)),
           ct.Translate((grx,gty)),
           ct.Translate((gmx,gty))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1])
        canvas.create_polygon(p[1][0],p[1][1],
                           p[2][0],p[2][1],
                           p[3][0],p[3][1],
                           p[4][0],p[4][1],
                           p[5][0],p[5][1])
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableVoltageSourceOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceOnePort'])

class PartPictureCurrentSourceTwoPort(PartPicture):
    def __init__(self,orientation):
        PartPicture.__init__(self,(0,0),[PartPin(2,(1,0),'t',False),PartPin(1,(1,4),'b',False)],[(0,1),(2,3)],[(0,0),(2,4)],(2,1),orientation)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        lx=(drawingOrigin[0]+self.origin[0]+0)*grid
        ly=(drawingOrigin[1]+self.origin[1]+1)*grid
        ux=(drawingOrigin[0]+self.origin[0]+2)*grid
        uy=(drawingOrigin[1]+self.origin[1]+3)*grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,ly)),ct.Translate((ux,uy))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1])
        px=(drawingOrigin[0]+self.origin[0]+0)*grid+grid
        py=(drawingOrigin[1]+self.origin[1]+1)*grid+grid-grid/2
        my=(drawingOrigin[1]+self.origin[1]+1)*grid+grid+grid/2
        p=[[ct.Translate((px-grid/4,py)),ct.Translate((px,py-grid/4))],
           [ct.Translate((px+grid/4,py)),ct.Translate((px,py-grid/4))],
           [ct.Translate((px,my+grid/4)),ct.Translate((px,py-grid/4))]]
        canvas.create_line(p[0][0][0],p[0][0][1],p[0][1][0],p[0][1][1])
        canvas.create_line(p[1][0][0],p[1][0][1],p[1][1][0],p[1][1][1])
        canvas.create_line(p[2][0][0],p[2][0][1],p[2][1][0],p[2][1][1])
       
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCurrentSourceTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourceTwoPort'])

class PartPictureCurrentSourceOnePort(PartPicture):
    def __init__(self,orientation):
        PartPicture.__init__(self,(0,0),[PartPin(1,(1,0),'t',False)],[(0,1),(2,3)],[(0,0),(2,4)],(2,1),orientation)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        lx=(drawingOrigin[0]+self.origin[0]+0)*grid
        ly=(drawingOrigin[1]+self.origin[1]+1)*grid
        ux=(drawingOrigin[0]+self.origin[0]+2)*grid
        uy=(drawingOrigin[1]+self.origin[1]+3)*grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,ly)),ct.Translate((ux,uy))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1])
        px=(drawingOrigin[0]+self.origin[0]+0)*grid+grid
        py=(drawingOrigin[1]+self.origin[1]+1)*grid+grid-grid/2
        my=(drawingOrigin[1]+self.origin[1]+1)*grid+grid+grid/2
        p=[[ct.Translate((px-grid/4,py)),ct.Translate((px,py-grid/4))],
           [ct.Translate((px+grid/4,py)),ct.Translate((px,py-grid/4))],
           [ct.Translate((px,my+grid/4)),ct.Translate((px,py-grid/4))]]
        canvas.create_line(p[0][0][0],p[0][0][1],p[0][1][0],p[0][1][1])
        canvas.create_line(p[1][0][0],p[1][0][1],p[1][1][0],p[1][1][1])
        canvas.create_line(p[2][0][0],p[2][0][1],p[2][1][0],p[2][1][1])
        gmx=(drawingOrigin[0]+self.origin[0]+1)*grid
        glx=gmx-grid
        grx=gmx+grid
        gby=(drawingOrigin[1]+self.origin[1]+5)*grid
        gty=gby-grid
        p=[ct.Translate((gmx,gty-grid)),
           ct.Translate((gmx,gty)),
           ct.Translate((glx,gty)),
           ct.Translate((gmx,gby)),
           ct.Translate((grx,gty)),
           ct.Translate((gmx,gty))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1])
        canvas.create_polygon(p[1][0],p[1][1],
                           p[2][0],p[2][1],
                           p[3][0],p[3][1],
                           p[4][0],p[4][1],
                           p[5][0],p[5][1])       
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCurrentSourceOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourceOnePort'])
        

