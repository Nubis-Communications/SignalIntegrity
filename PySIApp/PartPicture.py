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

class PartPictureRotatable(PartPicture):
    def __init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation,orientation):
        self.orientation=orientation
        self.rotationPoint = ((innerBox[0][0]+innerBox[1][0])/2,(innerBox[0][1]+innerBox[1][1])/2)
        ct=CoordinateTranslater(self.rotationPoint,self.orientation)
        origin=ct.Translate(origin)
        for pin in pinList:
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
        boundingBox=[ct.Translate(boundingBox[0]),ct.Translate(boundingBox[1])]
        boundingBox=[(min(boundingBox[0][0],boundingBox[1][0]),min(boundingBox[0][1],boundingBox[1][1])),
                     (max(boundingBox[0][0],boundingBox[1][0]),max(boundingBox[0][1],boundingBox[1][1]))]
        innerBox=[ct.Translate(innerBox[0]),ct.Translate(innerBox[1])]
        innerBox=[(min(innerBox[0][0],innerBox[1][0]),min(innerBox[0][1],innerBox[1][1])),
                     (max(innerBox[0][0],innerBox[1][0]),max(innerBox[0][1],innerBox[1][1]))]
        propertiesLocation=ct.Translate(propertiesLocation)
        PartPicture.__init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation)
    def CoordinateTranslater(self,grid,drawingOrigin):
        return CoordinateTranslater(((drawingOrigin[0]+self.origin[0]+self.rotationPoint[0])*grid,
                                (drawingOrigin[1]+self.origin[1]+self.rotationPoint[1])*grid),
                                self.orientation)   

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

class PartPictureBoxRotatable(PartPictureRotatable):
    def __init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation,orientation):
        PartPictureRotatable.__init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation,orientation)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,True)

class PartPictureOnePortRotatable(PartPictureBoxRotatable):
    def __init__(self,orientation):
        PartPictureBoxRotatable.__init__(self,(0,0),[PartPin(1,(0,1),'l')],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1),orientation)

class PartPictureOnePort0(PartPictureOnePortRotatable):
    def __init__(self):
        PartPictureOnePortRotatable.__init__(self,'0')

class PartPictureOnePort90(PartPictureOnePortRotatable):
    def __init__(self):
        PartPictureOnePortRotatable.__init__(self,'90')

class PartPictureOnePort180(PartPictureOnePortRotatable):
    def __init__(self):
        PartPictureOnePortRotatable.__init__(self,'180')

class PartPictureOnePort270(PartPictureOnePortRotatable):
    def __init__(self):
        PartPictureOnePortRotatable.__init__(self,'270')

class PartPictureTwoPortRotatable(PartPictureBoxRotatable):
    def __init__(self,orientation):
        PartPictureBoxRotatable.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(4,1),'r')],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1),orientation)

class PartPictureTwoPort0(PartPictureTwoPortRotatable):
    def __init__(self):
        PartPictureTwoPortRotatable.__init__(self,'0')

class PartPictureTwoPort90(PartPictureTwoPortRotatable):
    def __init__(self):
        PartPictureTwoPortRotatable.__init__(self,'90')

class PartPictureTwoPort180(PartPictureTwoPortRotatable):
    def __init__(self):
        PartPictureTwoPortRotatable.__init__(self,'180')

class PartPictureTwoPort270(PartPictureTwoPortRotatable):
    def __init__(self):
        PartPictureTwoPortRotatable.__init__(self,'270')

class PartPictureThreePortRotatable(PartPictureBoxRotatable):
    def __init__(self,orientation):
        PartPictureBoxRotatable.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l'),PartPin(3,(4,2),'r')],[(1,0),(3,4)],[(0,0),(4,4)],(1,-1),orientation)

class PartPictureThreePort0(PartPictureThreePortRotatable):
    def __init__(self):
        PartPictureThreePortRotatable.__init__(self,'0')

class PartPictureThreePort90(PartPictureThreePortRotatable):
    def __init__(self):
        PartPictureThreePortRotatable.__init__(self,'90')

class PartPictureThreePort180(PartPictureThreePortRotatable):
    def __init__(self):
        PartPictureThreePortRotatable.__init__(self,'180')

class PartPictureThreePort270(PartPictureThreePortRotatable):
    def __init__(self):
        PartPictureThreePortRotatable.__init__(self,'270')

class PartPictureFourPortRotatable(PartPictureBoxRotatable):
    def __init__(self,orientation):
        PartPictureBoxRotatable.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l'),PartPin(3,(4,1),'r'),PartPin(4,(4,3),'r')],[(1,0),(3,4)],[(0,0),(4,4)],(1,-1),orientation)

class PartPictureFourPort0(PartPictureFourPortRotatable):
    def __init__(self):
        PartPictureFourPortRotatable.__init__(self,'0')

class PartPictureFourPort90(PartPictureFourPortRotatable):
    def __init__(self):
        PartPictureFourPortRotatable.__init__(self,'90')

class PartPictureFourPort180(PartPictureFourPortRotatable):
    def __init__(self):
        PartPictureFourPortRotatable.__init__(self,'180')

class PartPictureFourPort270(PartPictureFourPortRotatable):
    def __init__(self):
        PartPictureFourPortRotatable.__init__(self,'270')

class PartPictureVariableOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureOnePort0','PartPictureOnePort90','PartPictureOnePort180','PartPictureOnePort270'])

class PartPictureVariableTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureTwoPort0','PartPictureTwoPort90','PartPictureTwoPort180','PartPictureTwoPort270'])

class PartPictureVariableThreePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureThreePort0','PartPictureThreePort90','PartPictureThreePort180','PartPictureThreePort270'])

class PartPictureVariableFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureFourPort0','PartPictureFourPort90','PartPictureFourPort180','PartPictureFourPort270'])

class PartPicturePortRotatable(PartPictureRotatable):
    def __init__(self,orientation):
        PartPictureRotatable.__init__(self,(0,0),[PartPin(1,(3,1),'r',False)],[(1,1),(3,1)],[(0,0),(3,2)],(1,1),orientation)
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

class PartPicturePort0(PartPicturePortRotatable):
    def __init__(self):
        PartPicturePortRotatable.__init__(self,'0')

class PartPicturePort90(PartPicturePortRotatable):
    def __init__(self):
        PartPicturePortRotatable.__init__(self,'90')

class PartPicturePort180(PartPicturePortRotatable):
    def __init__(self):
        PartPicturePortRotatable.__init__(self,'180')

class PartPicturePort270(PartPicturePortRotatable):
    def __init__(self):
        PartPicturePortRotatable.__init__(self,'270')

class PartPictureVariablePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPicturePort0','PartPicturePort90','PartPicturePort180','PartPicturePort270'])

class PartPictureGroundRotatable(PartPictureRotatable):
    def __init__(self,orientation):
        PartPictureRotatable.__init__(self,(0,0),[PartPin(1,(1,0),'t',True)],[(0,1),(3,2)],[(0,0),(3,2)],(3,1),orientation)
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
        
class PartPictureGround0(PartPictureGroundRotatable):
    def __init__(self):
        PartPictureGroundRotatable.__init__(self,'0')

class PartPictureGround180(PartPictureGroundRotatable):
    def __init__(self):
        PartPictureGroundRotatable.__init__(self,'180')

class PartPictureGround90(PartPictureGroundRotatable):
    def __init__(self):
        PartPictureGroundRotatable.__init__(self,'90')

class PartPictureGround270(PartPictureGroundRotatable):
    def __init__(self):
        PartPictureGroundRotatable.__init__(self,'270')        

class PartPictureVariableGround(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureGround0','PartPictureGround90','PartPictureGround180','PartPictureGround270'])

class PartPictureResistorTwoPortRotatable(PartPictureRotatable):
    def __init__(self,orientation):
        PartPictureRotatable.__init__(self,(0,0),[PartPin(1,(0,1),'l',False),PartPin(2,(4,1),'r',False)],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1),orientation)
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

class PartPictureResistorTwoPort0(PartPictureResistorTwoPortRotatable):
    def __init__(self):
        PartPictureResistorTwoPortRotatable.__init__(self,'0')

class PartPictureResistorTwoPort180(PartPictureResistorTwoPortRotatable):
    def __init__(self):
        PartPictureResistorTwoPortRotatable.__init__(self,'180')

class PartPictureResistorTwoPort90(PartPictureResistorTwoPortRotatable):
    def __init__(self):
        PartPictureResistorTwoPortRotatable.__init__(self,'90')

class PartPictureResistorTwoPort270(PartPictureResistorTwoPortRotatable):
    def __init__(self):
        PartPictureResistorTwoPortRotatable.__init__(self,'270')        

class PartPictureVariableResistorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureResistorTwoPort0','PartPictureResistorTwoPort90','PartPictureResistorTwoPort180','PartPictureResistorTwoPort270'])

class PartPictureCapacitorTwoPortRotatable(PartPictureRotatable):
    def __init__(self,orientation):
        PartPictureRotatable.__init__(self,(0,0),[PartPin(1,(0,1),'l',False),PartPin(2,(4,1),'r',False)],[(1,0),(3,2)],[(0,0),(4,2)],(1,-1),orientation)
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

class PartPictureCapacitorTwoPort0(PartPictureCapacitorTwoPortRotatable):
    def __init__(self):
        PartPictureCapacitorTwoPortRotatable.__init__(self,'0')

class PartPictureCapacitorTwoPort180(PartPictureCapacitorTwoPortRotatable):
    def __init__(self):
        PartPictureCapacitorTwoPortRotatable.__init__(self,'180')

class PartPictureCapacitorTwoPort90(PartPictureCapacitorTwoPortRotatable):
    def __init__(self):
        PartPictureCapacitorTwoPortRotatable.__init__(self,'90')

class PartPictureCapacitorTwoPort270(PartPictureCapacitorTwoPortRotatable):
    def __init__(self):
        PartPictureCapacitorTwoPortRotatable.__init__(self,'270')        

class PartPictureVariableCapacitorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCapacitorTwoPort0','PartPictureCapacitorTwoPort90','PartPictureCapacitorTwoPort180','PartPictureCapacitorTwoPort270'])
