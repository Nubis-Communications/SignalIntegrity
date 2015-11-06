'''
Created on Oct 15, 2015

@author: peterp
'''
import xml.etree.ElementTree as et
import copy

from PartPin import *
from matplotlib.pyplot import grid

class CoordinateTranslater(object):
    def __init__(self,rotationPoint,rotationAngle,mirroredHorizontally,mirroredVertically):
        self.rotationPoint=rotationPoint
        self.rotationAngle=rotationAngle
        self.mirroredHorizontally=mirroredHorizontally
        self.mirroredVertically=mirroredVertically
        self.color='black'
    def Translate(self,coord):
        (rcosq,rsinq)=(coord[0]-self.rotationPoint[0],self.rotationPoint[1]-coord[1])
        if self.rotationAngle == '0':
            deltax=rcosq
            deltay=-rsinq
        elif self.rotationAngle == '90':
            deltax=-rsinq
            deltay=-rcosq
        elif self.rotationAngle == '180':
            deltax=-rcosq
            deltay=rsinq
        elif self.rotationAngle == '270':
            deltax=rsinq
            deltay=rcosq
        if self.mirroredHorizontally:
            deltax=-deltax
        if self.mirroredVertically:
            deltay=-deltay
        return (self.rotationPoint[0]+deltax,self.rotationPoint[1]+deltay)

class PartPicture(object):
    def __init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation,orientation,mirroredHorizontally,mirroredVertically,rotationPoint=None):
        if rotationPoint==None:
            self.rotationPoint = ((innerBox[0][0]+innerBox[1][0])/2,(innerBox[0][1]+innerBox[1][1])/2)
        else: self.rotationPoint = rotationPoint
        self.origin=origin
        self.pinListSupplied = pinList
        self.innerBoxSupplied = innerBox
        self.boundingBoxSupplied = boundingBox
        self.propertiesLocationSupplied = propertiesLocation
        self.ApplyOrientation(orientation,mirroredHorizontally,mirroredVertically)
    def ApplyOrientation(self,orientation,mirroredHorizontally,mirroredVertically):
        self.orientation = orientation
        self.mirroredHorizontally=mirroredHorizontally
        self.mirroredVertically=mirroredVertically
        ct=CoordinateTranslater(self.rotationPoint,self.orientation,self.mirroredHorizontally,self.mirroredVertically)
        self.pinList = copy.deepcopy(self.pinListSupplied)
        for pin in self.pinList:
            if pin.pinOrientation=='t':
                if self.orientation=='0':
                    if self.mirroredVertically: pin.pinOrientation = 'b'
                    else: pin.pinOrientation='t'
                elif self.orientation=='90':
                    if self.mirroredHorizontally: pin.pinOrientation='r'
                    else: pin.pinOrientation='l'
                elif self.orientation=='180':
                    if self.mirroredVertically: pin.pinOrientation='t'
                    else: pin.pinOrientation='b'
                elif self.orientation=='270':
                    if self.mirroredHorizontally: pin.pinOrientation='l'
                    else: pin.pinOrientation='r'
            elif pin.pinOrientation=='l':
                if self.orientation=='0':
                    if self.mirroredHorizontally: pin.pinOrientation='r'
                    else: pin.pinOrientation='l'
                elif self.orientation=='90':
                    if self.mirroredVertically: pin.pinOrientation='t'
                    else: pin.pinOrientation='b'
                elif self.orientation=='180':
                    if self.mirroredHorizontally: pin.pinOrientation='l'
                    else: pin.pinOrientation='r'
                elif self.orientation=='270':
                    if self.mirroredVertically: pin.pinOrientation = 'b'
                    else: pin.pinOrientation='t'
            elif pin.pinOrientation == 'b':
                if self.orientation=='0':
                    if self.mirroredVertically: pin.pinOrientation='t'
                    else: pin.pinOrientation='b'
                elif self.orientation=='90':
                    if self.mirroredHorizontally: pin.pinOrientation='l'
                    else: pin.pinOrientation='r'
                elif self.orientation=='180':
                    if self.mirroredVertically: pin.pinOrientation = 'b'
                    else: pin.pinOrientation='t'
                elif self.orientation=='270':
                    if self.mirroredHorizontally: pin.pinOrientation='r'
                    else: pin.pinOrientation='l'
            elif pin.pinOrientation=='r':
                if self.orientation=='0':
                    if self.mirroredHorizontally: pin.pinOrientation='l'
                    else: pin.pinOrientation='r'
                elif self.orientation=='90':
                    if self.mirroredVertically: pin.pinOrientation = 'b'
                    else: pin.pinOrientation='t'
                elif self.orientation=='180':
                    if self.mirroredHorizontally: pin.pinOrientation='r'
                    else: pin.pinOrientation='l'
                elif self.orientation=='270':
                    if self.mirroredVertically: pin.pinOrientation='t'
                    else: pin.pinOrientation='b'
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
        self.ApplyOrientation(newOrientation,self.mirroredHorizontally,self.mirroredVertically)
    def CoordinateTranslater(self,grid,drawingOrigin):
        return CoordinateTranslater(((drawingOrigin[0]+self.origin[0]+self.rotationPoint[0])*grid,
                                (drawingOrigin[1]+self.origin[1]+self.rotationPoint[1])*grid),
                                self.orientation,self.mirroredHorizontally,self.mirroredVertically)
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
    def IsIn(self,i,f):
        minx=min(i[0],f[0])
        miny=min(i[1],f[1])
        maxx=max(i[0],f[0])
        maxy=max(i[1],f[1])
        if minx > self.innerBox[0][0]+self.origin[0]:
            return False
        if maxx < self.innerBox[1][0]+self.origin[0]:
            return False
        if miny > self.innerBox[0][1]+self.origin[1]:
            return False
        if maxy < self.innerBox[1][1]+self.origin[1]:
            return False
        return True
    def WhereInPart(self,xy):
        return (xy[0]-self.origin[0],xy[1]-self.origin[1])
    def DrawDevice(self,canvas,grid,drawingOrigin,drawInnerBox=False):
        if drawInnerBox:
            canvas.create_rectangle((drawingOrigin[0]+self.origin[0]+self.innerBox[0][0])*grid,
            (drawingOrigin[1]+self.origin[1]+self.innerBox[0][1])*grid,
            (drawingOrigin[0]+self.origin[0]+self.innerBox[1][0])*grid,
            (drawingOrigin[1]+self.origin[1]+self.innerBox[1][1])*grid, outline=self.color)
        for pin in self.pinList:
            pin.DrawPin(canvas,grid,(self.origin[0]+drawingOrigin[0],self.origin[1]+drawingOrigin[1]),self.color)

        leftside=min(self.innerBox[0][0],self.innerBox[1][0])
        rightside=max(self.innerBox[0][0],self.innerBox[1][0])
        topside=min(self.innerBox[0][1],self.innerBox[1][1])
        bottomside=max(self.innerBox[0][1],self.innerBox[1][1])
        locationx=self.propertiesLocation[0]
        locationy=self.propertiesLocation[1]
        ToTheLeft = locationx <= leftside
        ToTheRight = locationx >= rightside
        Above = locationy <= topside
        Below = locationy >= bottomside
##        print 'properties are '+('Above' if Above else '')+('Below' if Below else '')+' and to the '+\
##            ('Right' if ToTheRight else '')+('Left' if ToTheLeft else '')+'\n'

        anchorString=''
        if Above: anchorString=anchorString+'s'
        elif Below: anchorString=anchorString+'n'
        if ToTheLeft: anchorString=anchorString+'e'
        elif ToTheRight: anchorString=anchorString+'w'
        if anchorString == '': anchorString='nw'

        GoingUp=True
        if Above: GoingUp=True
        else: GoingUp=False

        V=len(self.visiblePartPropertyList)
        if GoingUp:
            locations=[((drawingOrigin[0]+self.origin[0]+self.propertiesLocation[0])*grid,
            (drawingOrigin[1]+self.origin[1]+self.propertiesLocation[1])*grid-10*v) for v in range(V)]
        else:
            locations=[((drawingOrigin[0]+self.origin[0]+self.propertiesLocation[0])*grid,
            (drawingOrigin[1]+self.origin[1]+self.propertiesLocation[1])*grid+10*(V-v)-10) for v in range(V)]

        for v in range(V):
            canvas.create_text(locations[v][0],locations[v][1],
                text=self.visiblePartPropertyList[v],anchor=anchorString,fill=self.color)
    def PinCoordinates(self):
        return [(pin.pinConnectionPoint[0]+self.origin[0],pin.pinConnectionPoint[1]+self.origin[1]) for pin in self.pinList]
    def Selected(self,selected):
        if selected:
            self.color='blue'
        else:
            self.color='black'
        return self
    # helpers for commonly drawn things
    def DrawPlusMinus(self,canvas,grid,drawingOrigin,x):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        px=(drawingOrigin[0]+self.origin[0]+x)*grid
        py=(drawingOrigin[1]+self.origin[1]+1)*grid+grid-5*grid/8
        my=(drawingOrigin[1]+self.origin[1]+1)*grid+grid+5*grid/8
        pw=3*grid/16
        p=[[ct.Translate((px-pw,py)),ct.Translate((px+pw,py))],
           [ct.Translate((px,py-pw)),ct.Translate((px,py+pw))],
           [ct.Translate((px-pw,my)),ct.Translate((px+pw,my))]]
        canvas.create_line(p[0][0][0],p[0][0][1],p[0][1][0],p[0][1][1],fill=self.color)
        canvas.create_line(p[1][0][0],p[1][0][1],p[1][1][0],p[1][1][1],fill=self.color)
        canvas.create_line(p[2][0][0],p[2][0][1],p[2][1][0],p[2][1][1],fill=self.color)
    def DrawMinusPlus(self,canvas,grid,drawingOrigin,x):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        px=(drawingOrigin[0]+self.origin[0]+x)*grid
        py=(drawingOrigin[1]+self.origin[1]+1)*grid+grid+5*grid/8
        my=(drawingOrigin[1]+self.origin[1]+1)*grid+grid-5*grid/8
        pw=3*grid/16
        p=[[ct.Translate((px-pw,py)),ct.Translate((px+pw,py))],
           [ct.Translate((px,py-pw)),ct.Translate((px,py+pw))],
           [ct.Translate((px-pw,my)),ct.Translate((px+pw,my))]]
        canvas.create_line(p[0][0][0],p[0][0][1],p[0][1][0],p[0][1][1],fill=self.color)
        canvas.create_line(p[1][0][0],p[1][0][1],p[1][1][0],p[1][1][1],fill=self.color)
        canvas.create_line(p[2][0][0],p[2][0][1],p[2][1][0],p[2][1][1],fill=self.color)
    def DrawArrowUp(self,canvas,grid,drawingOrigin,x):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        px=(drawingOrigin[0]+self.origin[0]+0+x)*grid
        py=(drawingOrigin[1]+self.origin[1]+1+1)*grid-3*grid/4
        my=(drawingOrigin[1]+self.origin[1]+1+1)*grid+3*grid/4
        p=[ct.Translate((px,py)),ct.Translate((px,my))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,arrow='first',arrowshape=((8*grid)/20,(10*grid)/20,(3*grid)/20))
    def DrawArrowDown(self,canvas,grid,drawingOrigin,x):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        px=(drawingOrigin[0]+self.origin[0]+0+x)*grid
        py=(drawingOrigin[1]+self.origin[1]+1+1)*grid-3*grid/4
        my=(drawingOrigin[1]+self.origin[1]+1+1)*grid+3*grid/4
        p=[ct.Translate((px,py)),ct.Translate((px,my))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,arrow='last',arrowshape=((8*grid)/20,(10*grid)/20,(3*grid)/20))
    def DrawDependent(self,canvas,grid,drawingOrigin,x):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        mx=(drawingOrigin[0]+self.origin[0]+x)*grid
        lx=mx-3*grid/4
        rx=mx+3*grid/4
        my=(drawingOrigin[1]+self.origin[1]+2)*grid
        ty=my-grid
        by=my+grid
        p=[ct.Translate((mx,ty)),
            ct.Translate((rx,my)),
            ct.Translate((mx,by)),
            ct.Translate((lx,my)),
            ct.Translate((mx,ty))]
        canvas.create_polygon(p[0][0],p[0][1],
            p[1][0],p[1][1],
            p[2][0],p[2][1],
            p[3][0],p[3][1],
            p[4][0],p[4][1],
            outline=self.color,
            fill='')
    def DrawIndependent(self,canvas,grid,drawingOrigin):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        lx=(drawingOrigin[0]+self.origin[0]+0)*grid
        ly=(drawingOrigin[1]+self.origin[1]+1)*grid
        ux=(drawingOrigin[0]+self.origin[0]+2)*grid
        uy=(drawingOrigin[1]+self.origin[1]+3)*grid
        p=[ct.Translate((lx,ly)),ct.Translate((ux,uy))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1],outline=self.color)
    def DrawGround(self,canvas,grid,drawingOrigin,x,y):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        mx=(drawingOrigin[0]+self.origin[0]+x)*grid
        size=2*grid/3
        lx=mx-size
        rx=mx+size
        ty=(drawingOrigin[1]+self.origin[1]+y)*grid
        by=ty+size
        p=[ct.Translate((lx,ty)),ct.Translate((rx,ty)),ct.Translate((mx,by)),ct.Translate((lx,ty))]
        canvas.create_polygon(p[0][0],p[0][1],p[1][0],p[1][1],p[2][0],p[2][1],p[3][0],p[3][1],fill=self.color)
    def DrawStem(self,canvas,grid,drawingOrigin,x,y):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        gx=(drawingOrigin[0]+self.origin[0]+x)*grid
        gy=(drawingOrigin[1]+self.origin[1]+y)*grid
        p=[ct.Translate((gx,gy)),ct.Translate((gx,gy+grid))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color)
    def DrawStepSymbol(self,canvas,grid,drawingOrigin):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        mx=(drawingOrigin[0]+self.origin[0]+1)*grid
        my=(drawingOrigin[1]+self.origin[1]+2)*grid
        p=[ct.Translate((mx-grid/2,my+3*grid/8)),ct.Translate((mx,my+3*grid/8)),
           ct.Translate((mx,my-3*grid/8)),ct.Translate((mx+grid/2,my-3*grid/8))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],p[2][0],p[2][1],p[3][0],p[3][1],fill=self.color)
    def DrawPulseSymbol(self,canvas,grid,drawingOrigin):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        mx=(drawingOrigin[0]+self.origin[0]+1)*grid
        my=(drawingOrigin[1]+self.origin[1]+2)*grid
        p=[ct.Translate((mx-grid/2,my+3*grid/8)),
            ct.Translate((mx-grid/4,my+3*grid/8)),
            ct.Translate((mx-grid/4,my-3*grid/8)),
            ct.Translate((mx+grid/4,my-3*grid/8)),
            ct.Translate((mx+grid/4,my+3*grid/8)),
            ct.Translate((mx+grid/2,my+3*grid/8))]
        canvas.create_line(p[0][0],p[0][1],
            p[1][0],p[1][1],
            p[2][0],p[2][1],
            p[3][0],p[3][1],
            p[4][0],p[4][1],
            p[5][0],p[5][1],
            fill=self.color)
    def ArcConverter(self,start,extent,rotationAngle,mirroredVertically,mirroredHorizontally):
        start=(start+rotationAngle)%360
        if mirroredVertically:
            extent=-extent
            if start==90 or start==270:
                start=(start+180)%360
        if mirroredHorizontally:
            extent=-extent
            if start==0 or start==180:
                start=(start+180)%360
        return [start,extent]
    def DrawSineSymbol(self,canvas,grid,drawingOrigin):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        mx=(drawingOrigin[0]+self.origin[0]+1)*grid
        my=(drawingOrigin[1]+self.origin[1]+2)*grid
        p=[ct.Translate((mx-grid/2,my-3*grid/8)),ct.Translate((mx,my+3*grid/8)),
            ct.Translate((mx,my-3*grid/8)),ct.Translate((mx+grid/2,my+3*grid/8))]
        r0=self.ArcConverter(0,180,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        r1=self.ArcConverter(0,-180,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r0[0],extent=r0[1],style='arc',outline=self.color)
        canvas.create_arc(p[2][0],p[2][1],p[3][0],p[3][1],start=r1[0],extent=r1[1],style='arc',outline=self.color)

class PartPictureXMLClassFactory(object):
    def __init__(self,xml):
        partPictureClassList=[]
        partPictureSelected = 0
        origin=(0,0)
        orientation='0'
        mirroredVertically=False
        mirroredHorizontally=False
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
            elif item.tag == 'mirrored_vertically':
                mirroredVertically = eval(item.text)
            elif item.tag == 'mirrored_horizontally':
                mirroredHorizontally = eval(item.text)
        self.result=PartPictureVariable(partPictureClassList,partPictureSelected,origin,orientation,mirroredHorizontally,mirroredVertically)

class PartPictureVariable(object):
    def __init__(self,partPictureClassList,partPictureSelected=0,origin=(0,0),orientation='0',mirroredHorizontally=False,mirroredVertically=False):
        self.partPictureClassList = partPictureClassList
        self.partPictureSelected = partPictureSelected
        self.current=eval(self.partPictureClassList[self.partPictureSelected])(origin,orientation,mirroredHorizontally,mirroredVertically)
    def SwitchPartPicture(self,item):
        orientation=self.current.orientation
        mirroredHorizontally=self.current.mirroredHorizontally
        mirroredVertically=self.current.mirroredVertically
        origin=self.current.origin
        self.partPictureSelected = item
        self.current=eval(self.partPictureClassList[self.partPictureSelected])(origin,orientation,mirroredHorizontally,mirroredVertically)
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
        mirroredVerticallyElement = et.Element('mirrored_vertically')
        mirroredVerticallyElement.text=str(self.current.mirroredVertically)
        mirroredHorizontallyElement = et.Element('mirrored_horizontally')
        mirroredHorizontallyElement.text=str(self.current.mirroredHorizontally)
        thisElement.extend([classNamesElement,selectedElement,originElement,orientationElement,mirroredVerticallyElement,mirroredHorizontallyElement])
        return thisElement

class PartPictureBox(PartPicture):
    def __init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,True)

class PartPictureOnePort(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(0,1),'l')],[(1,0),(3,2)],[(0,0),(4,2)],(1,-0.5),orientation,mirroredHorizontally,mirroredVertically)

class PartPictureVariableOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureOnePort'])

class PartPictureTwoPort(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(0,1),'l'),PartPin(2,(4,1),'r')],[(1,0),(3,2)],[(0,0),(4,2)],(2,-0.5),orientation,mirroredHorizontally,mirroredVertically)

class PartPictureTwoPortSide(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l')],[(1,0),(3,4)],[(0,0),(4,4)],(1,-0.5),orientation,mirroredHorizontally,mirroredVertically)

class PartPictureVariableTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureTwoPort','PartPictureTwoPortSide'])

class PartPictureThreePort(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l'),PartPin(3,(4,2),'r')],[(1,0),(3,4)],[(0,0),(4,4)],(2,-0.5),orientation,mirroredHorizontally,mirroredVertically)

class PartPictureThreePortSide(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l'),PartPin(3,(0,5),'l')],[(1,0),(3,6)],[(0,0),(4,6)],(1,-0.5),orientation,mirroredHorizontally,mirroredVertically)

class PartPictureVariableThreePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureThreePort','PartPictureThreePortSide'])

class PartPictureFourPort(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l'),PartPin(3,(4,1),'r'),PartPin(4,(4,3),'r')],[(1,0),(3,4)],[(0,0),(4,4)],(2,-0.5),orientation,mirroredHorizontally,mirroredVertically)

class PartPictureFourPortSide(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l'),PartPin(3,(0,5),'l'),PartPin(4,(0,7),'l')],[(1,0),(3,8)],[(0,0),(4,8)],(1,-0.5),orientation,mirroredHorizontally,mirroredVertically)

class PartPictureVariableFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureFourPort','PartPictureFourPortSide'])

class PartPicturePort(PartPicture):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(3,1),'r',False)],[(2,0),(3,2)],[(0,0),(3,2)],(1,1),orientation,mirroredHorizontally,mirroredVertically,(3,1))
    def DrawDevice(self,canvas,grid,drawingOrigin):
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid+grid/2
        rx=(drawingOrigin[0]+self.origin[0]+2)*grid
        ty=(drawingOrigin[1]+self.origin[1]+0)*grid+grid/2
        my=(drawingOrigin[1]+self.origin[1]+1)*grid
        by=(drawingOrigin[1]+self.origin[1]+1)*grid+grid/2
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,ty)),ct.Translate((rx,my)),ct.Translate((lx,by))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],p[2][0],p[2][1],fill=self.color)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariablePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPicturePort'])

class PartPictureGround(PartPicture):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(1,0),'t',False)],[(0,1),(3,2)],[(0,0),(3,2)],(2,1),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawGround(self,canvas,grid,drawingOrigin,1,1)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableGround(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureGround'])

class PartPictureInductorTwoPort(PartPicture):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(0,1),'l',False),PartPin(2,(4,1),'r',False)],[(1,0),(3,2)],[(0,0),(4,2)],(2,0),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        my=(drawingOrigin[1]+self.origin[1])*grid+grid
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,my+grid/2)),
           ct.Translate((lx+grid/2,my-grid/2)),
           ct.Translate((lx,my+3*grid/2)),
           ct.Translate((lx+grid/2,my-grid/2)),
           ct.Translate((lx+grid/2,my+3*grid/2)),
           ct.Translate((lx+grid,my-grid/2)),
           ct.Translate((rx-grid,my+3*grid/2)),
           ct.Translate((rx-grid/2,my-grid/2)),
           ct.Translate((rx-grid/2,my+3*grid/2)),
           ct.Translate((rx,my-grid/2)),
           ct.Translate((rx-grid/2,my+grid/2)),
           ct.Translate((rx,my-grid/2))]
        r0=self.ArcConverter(90,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        r1=self.ArcConverter(0,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        r2=self.ArcConverter(0,180,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        r3=self.ArcConverter(90,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        r4=self.ArcConverter(0,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r0[0],extent=r0[1],style='arc',outline=self.color)
        canvas.create_arc(p[2][0],p[2][1],p[3][0],p[3][1],start=r1[0],extent=r1[1],style='arc',outline=self.color)
        canvas.create_arc(p[5][0],p[5][1],p[4][0],p[4][1],start=r2[0],extent=r2[1],style='arc',outline=self.color)
        canvas.create_arc(p[6][0],p[6][1],p[7][0],p[7][1],start=r2[0],extent=r2[1],style='arc',outline=self.color)
        canvas.create_arc(p[8][0],p[8][1],p[9][0],p[9][1],start=r3[0],extent=r3[1],style='arc',outline=self.color)
        canvas.create_arc(p[10][0],p[10][1],p[11][0],p[11][1],start=r4[0],extent=r4[1],style='arc',outline=self.color)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableInductorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureInductorTwoPort'])

class PartPictureMutual(PartPicture):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(0,1),'l',False),PartPin(3,(0,3),'l',False),PartPin(2,(4,1),'r',False),PartPin(4,(4,3),'r',False)],[(1,0),(3,4)],[(0,0),(4,4)],(2,0),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        my=(drawingOrigin[1]+self.origin[1])*grid+grid
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,my+grid/2)),
           ct.Translate((lx+grid/2,my-grid/2)),
           ct.Translate((lx,my+3*grid/2)),
           ct.Translate((lx+grid/2,my-grid/2)),
           ct.Translate((lx+grid/2,my+3*grid/2)),
           ct.Translate((lx+grid,my-grid/2)),
           ct.Translate((rx-grid,my+3*grid/2)),
           ct.Translate((rx-grid/2,my-grid/2)),
           ct.Translate((rx-grid/2,my+3*grid/2)),
           ct.Translate((rx,my-grid/2)),
           ct.Translate((rx-grid/2,my+grid/2)),
           ct.Translate((rx,my-grid/2))]
        r0=self.ArcConverter(90,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        r1=self.ArcConverter(0,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        r2=self.ArcConverter(0,180,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        r3=self.ArcConverter(90,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        r4=self.ArcConverter(0,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r0[0],extent=r0[1],style='arc',outline=self.color)
        canvas.create_arc(p[2][0],p[2][1],p[3][0],p[3][1],start=r1[0],extent=r1[1],style='arc',outline=self.color)
        canvas.create_arc(p[5][0],p[5][1],p[4][0],p[4][1],start=r2[0],extent=r2[1],style='arc',outline=self.color)
        canvas.create_arc(p[6][0],p[6][1],p[7][0],p[7][1],start=r2[0],extent=r2[1],style='arc',outline=self.color)
        canvas.create_arc(p[8][0],p[8][1],p[9][0],p[9][1],start=r3[0],extent=r3[1],style='arc',outline=self.color)
        canvas.create_arc(p[10][0],p[10][1],p[11][0],p[11][1],start=r4[0],extent=r4[1],style='arc',outline=self.color)

        my=(drawingOrigin[1]+self.origin[1]+3)*grid
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,my+grid/2)),
           ct.Translate((lx+grid/2,my-grid/2)),
           ct.Translate((lx,my+3*grid/2)),
           ct.Translate((lx+grid/2,my-grid/2)),
           ct.Translate((lx+grid/2,my+3*grid/2)),
           ct.Translate((lx+grid,my-grid/2)),
           ct.Translate((rx-grid,my+3*grid/2)),
           ct.Translate((rx-grid/2,my-grid/2)),
           ct.Translate((rx-grid/2,my+3*grid/2)),
           ct.Translate((rx,my-grid/2)),
           ct.Translate((rx-grid/2,my+grid/2)),
           ct.Translate((rx,my-grid/2))]
        r0=self.ArcConverter(90,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        r1=self.ArcConverter(0,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        r2=self.ArcConverter(0,180,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        r3=self.ArcConverter(90,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        r4=self.ArcConverter(0,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r0[0],extent=r0[1],style='arc',outline=self.color)
        canvas.create_arc(p[2][0],p[2][1],p[3][0],p[3][1],start=r1[0],extent=r1[1],style='arc',outline=self.color)
        canvas.create_arc(p[5][0],p[5][1],p[4][0],p[4][1],start=r2[0],extent=r2[1],style='arc',outline=self.color)
        canvas.create_arc(p[6][0],p[6][1],p[7][0],p[7][1],start=r2[0],extent=r2[1],style='arc',outline=self.color)
        canvas.create_arc(p[8][0],p[8][1],p[9][0],p[9][1],start=r3[0],extent=r3[1],style='arc',outline=self.color)
        canvas.create_arc(p[10][0],p[10][1],p[11][0],p[11][1],start=r4[0],extent=r4[1],style='arc',outline=self.color)

        ax=(drawingOrigin[0]+self.origin[0]+1)*grid-grid/4
        a0y=(drawingOrigin[1]+self.origin[1]+1)*grid+grid/4
        a1y=(drawingOrigin[1]+self.origin[1]+3)*grid-grid/4
        p=[ct.Translate((ax,a0y)),ct.Translate((ax,a1y))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],arrow='both',fill=self.color,arrowshape=((8*grid)/25,(10*grid)/25,(3*grid)/25))
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableMutual(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureMutual'])

class PartPictureIdealTransformer(PartPicture):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(3,(0,1),'l',False),PartPin(4,(0,3),'l',False),PartPin(1,(4,1),'r',False),PartPin(2,(4,3),'r',False)],[(1,1),(3,3)],[(0,0),(4,4)],(2,0.5),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        # left side of the transformer
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid
        p=[ct.Translate((lx-grid/2,ty)),ct.Translate((lx+grid/2,ty+grid/2))]
        r=self.ArcConverter(-90, 180, int(ct.rotationAngle), ct.mirroredVertically, ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r[0],extent=r[1],style='arc',outline=self.color)
        p=[ct.Translate((lx-grid/2,ty+grid/2)),ct.Translate((lx+grid/2,ty+grid))]
        r=self.ArcConverter(-90, 180, int(ct.rotationAngle), ct.mirroredVertically, ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r[0],extent=r[1],style='arc',outline=self.color)
        p=[ct.Translate((lx-grid/2,ty+grid)),ct.Translate((lx+grid/2,ty+3*grid/2))]
        r=self.ArcConverter(-90, 180, int(ct.rotationAngle), ct.mirroredVertically, ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r[0],extent=r[1],style='arc',outline=self.color)
        p=[ct.Translate((lx-grid/2,ty+3*grid/2)),ct.Translate((lx+grid/2,ty+2*grid))]
        r=self.ArcConverter(-90, 180, int(ct.rotationAngle), ct.mirroredVertically, ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r[0],extent=r[1],style='arc',outline=self.color)
        # right side of the transformer
        lx=(drawingOrigin[0]+self.origin[0]+3)*grid
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid
        p=[ct.Translate((lx-grid/2,ty)),ct.Translate((lx+grid/2,ty+grid/2))]
        r=self.ArcConverter(90, 180, int(ct.rotationAngle), ct.mirroredVertically, ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r[0],extent=r[1],style='arc',outline=self.color)
        p=[ct.Translate((lx-grid/2,ty+grid/2)),ct.Translate((lx+grid/2,ty+grid))]
        r=self.ArcConverter(90, 180, int(ct.rotationAngle), ct.mirroredVertically, ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r[0],extent=r[1],style='arc',outline=self.color)
        p=[ct.Translate((lx-grid/2,ty+grid)),ct.Translate((lx+grid/2,ty+3*grid/2))]
        r=self.ArcConverter(90, 180, int(ct.rotationAngle), ct.mirroredVertically, ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r[0],extent=r[1],style='arc',outline=self.color)
        p=[ct.Translate((lx-grid/2,ty+3*grid/2)),ct.Translate((lx+grid/2,ty+2*grid))]
        r=self.ArcConverter(90, 180, int(ct.rotationAngle), ct.mirroredVertically, ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r[0],extent=r[1],style='arc',outline=self.color)
        # the core of the transformer
        mx=(drawingOrigin[0]+self.origin[0]+2)*grid
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid
        by=(drawingOrigin[1]+self.origin[1]+3)*grid
        p=[ct.Translate((mx-grid/4,ty)),ct.Translate((mx-grid/4,by))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color)
        p=[ct.Translate((mx+grid/4,ty)),ct.Translate((mx+grid/4,by))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)
        # dot on the primary
        lx=(drawingOrigin[0]+self.origin[0])*grid+3*grid/4
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid+grid/8
        size=grid/8
        p=[ct.Translate((lx,ty)),ct.Translate((lx+size,ty+size))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,outline=self.color)
        # dot on the secondary
        lx=(drawingOrigin[0]+self.origin[0]+3)*grid
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid+grid/8
        size=grid/8
        p=[ct.Translate((lx,ty)),ct.Translate((lx+size,ty+size))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,outline=self.color)
        # primary label
        x=(drawingOrigin[0]+self.origin[0])*grid+grid/2
        y=(drawingOrigin[1]+self.origin[1]+2)*grid
        p=ct.Translate((x,y))
        canvas.create_text(p[0],p[1],text='P',fill=self.color)
        # secondary label
        x=(drawingOrigin[0]+self.origin[0]+3)*grid+grid/2
        y=(drawingOrigin[1]+self.origin[1]+2)*grid
        p=ct.Translate((x,y))
        canvas.create_text(p[0],p[1],text='S',fill=self.color)

class PartPictureVariableIdealTransformer(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureIdealTransformer'])

class PartPictureResistorTwoPort(PartPicture):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(0,1),'l',False),PartPin(2,(4,1),'r',False)],[(1,0),(3,2)],[(0,0),(4,2)],(2,0),orientation,mirroredHorizontally,mirroredVertically)
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
                           p[8][0],p[8][1],fill=self.color)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableResistorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureResistorTwoPort'])

class PartPictureResistorOnePort(PartPicture):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(1,0),'t',False)],[(0,1),(2,5)],[(0,0),(2,5)],(2,2.5),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        mx=(drawingOrigin[0]+self.origin[0])*grid+grid
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid
        by=(drawingOrigin[1]+self.origin[1]+3)*grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((mx,ty)),
           ct.Translate((mx-grid/2,ty+grid/4)),
           ct.Translate((mx+grid/2,ty+grid/2)),
           ct.Translate((mx-grid/2,ty+3*grid/4)),
           ct.Translate((mx+grid/2,ty+grid)),
           ct.Translate((mx-grid/2,by-3*grid/4)),
           ct.Translate((mx+grid/2,by-grid/2)),
           ct.Translate((mx-grid/2,by-grid/4)),
           ct.Translate((mx,by))]
        canvas.create_line(p[0][0],p[0][1],
                           p[1][0],p[1][1],
                           p[2][0],p[2][1],
                           p[3][0],p[3][1],
                           p[4][0],p[4][1],
                           p[5][0],p[5][1],
                           p[6][0],p[6][1],
                           p[7][0],p[7][1],
                           p[8][0],p[8][1],fill=self.color)
        PartPicture.DrawStem(self,canvas,grid,drawingOrigin,1,3)
        PartPicture.DrawGround(self,canvas,grid,drawingOrigin,1,4)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableResistorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureResistorOnePort'])

class PartPictureCapacitorTwoPort(PartPicture):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(0,1),'l',False),PartPin(2,(4,1),'r',False)],[(1,0),(3,2)],[(0,0),(4,2)],(2,0),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        my=(drawingOrigin[1]+self.origin[1])*grid+grid
        ty=my-2*grid/3
        by=my+2*grid/3
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        lpx=lx+3*grid/4
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid
        rpx=rx-3*grid/4
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[[ct.Translate((lx,my)),ct.Translate((lpx,my))],
           [ct.Translate((rx,my)),ct.Translate((rpx,my))],
           [ct.Translate((lpx,ty)),ct.Translate((lpx,by))],
           [ct.Translate((rpx,ty)),ct.Translate((rpx,by))]]
        canvas.create_line(p[0][0][0],p[0][0][1],p[0][1][0],p[0][1][1],fill=self.color)
        canvas.create_line(p[1][0][0],p[1][0][1],p[1][1][0],p[1][1][1],fill=self.color)
        canvas.create_line(p[2][0][0],p[2][0][1],p[2][1][0],p[2][1][1],fill=self.color)
        canvas.create_line(p[3][0][0],p[3][0][1],p[3][1][0],p[3][1][1],fill=self.color)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCapacitorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCapacitorTwoPort'])

class PartPictureCapacitorOnePort(PartPicture):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(1,0),'t',False)],[(0,1),(2,5)],[(0,0),(2,5)],(2,2.5),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        mx=(drawingOrigin[0]+self.origin[0]+1)*grid
        lx=mx-2*grid/3
        rx=mx+2*grid/3
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid
        by=(drawingOrigin[1]+self.origin[1]+3)*grid
        tpy=ty+3*grid/4
        bpy=by-3*grid/4
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[[ct.Translate((mx,ty)),ct.Translate((mx,tpy))],
           [ct.Translate((lx,tpy)),ct.Translate((rx,tpy))],
           [ct.Translate((lx,bpy)),ct.Translate((rx,bpy))],
           [ct.Translate((mx,bpy)),ct.Translate((mx,by))]]
        canvas.create_line(p[0][0][0],p[0][0][1],p[0][1][0],p[0][1][1],fill=self.color)
        canvas.create_line(p[1][0][0],p[1][0][1],p[1][1][0],p[1][1][1],fill=self.color)
        canvas.create_line(p[2][0][0],p[2][0][1],p[2][1][0],p[2][1][1],fill=self.color)
        canvas.create_line(p[3][0][0],p[3][0][1],p[3][1][0],p[3][1][1],fill=self.color)
        PartPicture.DrawStem(self,canvas,grid,drawingOrigin,1,3)
        PartPicture.DrawGround(self,canvas,grid,drawingOrigin,1,4)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCapacitorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCapacitorOnePort'])

class PartPictureVoltageSourceTwoPort(PartPicture):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(2,(1,0),'t',False),PartPin(1,(1,4),'b',False)],[(0,1),(2,3)],[(0,0),(2,4)],(2.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawIndependent(self,canvas,grid,drawingOrigin)
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,1)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableVoltageSourceTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceTwoPort'])

class PartPictureVoltageSourceStepGeneratorTwoPort(PartPictureVoltageSourceTwoPort):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceTwoPort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawStepSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableVoltageSourceStepGeneratorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceStepGeneratorTwoPort'])

class PartPictureVoltageSourcePulseGeneratorTwoPort(PartPictureVoltageSourceTwoPort):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceTwoPort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawPulseSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableVoltageSourcePulseGeneratorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourcePulseGeneratorTwoPort'])

class PartPictureVoltageSourceSineGeneratorTwoPort(PartPictureVoltageSourceTwoPort):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceTwoPort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawSineSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableVoltageSourceSineGeneratorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceSineGeneratorTwoPort'])

class PartPictureVoltageSourceOnePort(PartPicture):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(1,0),'t',False)],[(0,1),(2,5)],[(0,0),(2,5)],(2.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawIndependent(self,canvas,grid,drawingOrigin)
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,1)
        PartPicture.DrawStem(self,canvas,grid,drawingOrigin,1,3)
        PartPicture.DrawGround(self,canvas,grid,drawingOrigin,1,4)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableVoltageSourceOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceOnePort'])

class PartPictureVoltageSourceStepGeneratorOnePort(PartPictureVoltageSourceOnePort):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceOnePort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawStepSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableVoltageSourceStepGeneratorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceStepGeneratorOnePort'])

class PartPictureVoltageSourcePulseGeneratorOnePort(PartPictureVoltageSourceOnePort):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceOnePort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawPulseSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableVoltageSourcePulseGeneratorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourcePulseGeneratorOnePort'])

class PartPictureVoltageSourceSineGeneratorOnePort(PartPictureVoltageSourceOnePort):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceOnePort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawSineSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableVoltageSourceSineGeneratorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceSineGeneratorOnePort'])

class PartPictureCurrentSourceTwoPort(PartPicture):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(2,(1,0),'t',False),PartPin(1,(1,4),'b',False)],[(0,1),(2,3)],[(0,0),(2,4)],(2.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawIndependent(self,canvas,grid,drawingOrigin)
        # arrow inside the current source
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,1)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCurrentSourceTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourceTwoPort'])

class PartPictureCurrentSourceStepGeneratorTwoPort(PartPictureCurrentSourceTwoPort):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureCurrentSourceTwoPort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawStepSymbol(self,canvas,grid,drawingOrigin)
        PartPictureCurrentSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCurrentSourceStepGeneratorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourceStepGeneratorTwoPort'])

class PartPictureCurrentSourcePulseGeneratorTwoPort(PartPictureCurrentSourceTwoPort):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureCurrentSourceTwoPort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawPulseSymbol(self,canvas,grid,drawingOrigin)
        PartPictureCurrentSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCurrentSourcePulseGeneratorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourcePulseGeneratorTwoPort'])

class PartPictureCurrentSourceSineGeneratorTwoPort(PartPictureCurrentSourceTwoPort):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureCurrentSourceTwoPort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawSineSymbol(self,canvas,grid,drawingOrigin)
        PartPictureCurrentSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCurrentSourceSineGeneratorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourceSineGeneratorTwoPort'])

class PartPictureCurrentSourceOnePort(PartPicture):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(1,0),'t',False)],[(0,1),(2,3)],[(0,0),(2,4)],(2.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawIndependent(self,canvas,grid,drawingOrigin)
        # arrow inside the current source
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,1)
        PartPicture.DrawStem(self,canvas,grid,drawingOrigin,1,3)
        PartPicture.DrawGround(self,canvas,grid,drawingOrigin,1,4)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCurrentSourceOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourceOnePort'])

class PartPictureCurrentSourceStepGeneratorOnePort(PartPictureCurrentSourceOnePort):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureCurrentSourceOnePort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawStepSymbol(self,canvas,grid,drawingOrigin)
        PartPictureCurrentSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCurrentSourceStepGeneratorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourceStepGeneratorOnePort'])

class PartPictureCurrentSourcePulseGeneratorOnePort(PartPictureCurrentSourceOnePort):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureCurrentSourceOnePort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawPulseSymbol(self,canvas,grid,drawingOrigin)
        PartPictureCurrentSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCurrentSourcePulseGeneratorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourcePulseGeneratorOnePort'])

class PartPictureCurrentSourceSineGeneratorOnePort(PartPictureCurrentSourceOnePort):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureCurrentSourceOnePort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        PartPicture.DrawSineSymbol(self,canvas,grid,drawingOrigin)
        PartPictureCurrentSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCurrentSourceSineGeneratorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourceSineGeneratorOnePort'])

class PartPictureProbe(PartPicture):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(0,1),'l',False,False)],[(0,0),(1,1)],[(0,0),(1,1)],(1,0),orientation,mirroredHorizontally,mirroredVertically,(0,1))
    def DrawDevice(self,canvas,grid,drawingOrigin):
        ix=(drawingOrigin[0]+self.origin[0]+1)*grid
        iy=(drawingOrigin[1]+self.origin[1]+0)*grid
        mx=ix-grid/2
        my=iy+grid/2
        fx=(drawingOrigin[0]+self.origin[0]+0)*grid
        fy=(drawingOrigin[1]+self.origin[1]+1)*grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((ix,iy)),ct.Translate((mx,my)),ct.Translate((fx,fy))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,width=3)
        canvas.create_line(p[1][0],p[1][1],p[2][0],p[2][1],fill=self.color)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableProbe(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureProbe'])

class PartPictureMixedModeConverter(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(0,1),'l',False),PartPin(2,(0,3),'l',False),PartPin(3,(4,1),'r',False),PartPin(4,(4,3),'r',False)],[(1,0),(3,4)],[(0,0),(4,4)],(2,-0.5),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid+grid/2
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid-grid/2
        by=(drawingOrigin[1]+self.origin[1]+3)*grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,ty)),
           ct.Translate((lx,by)),
           ct.Translate((rx,ty)),
           ct.Translate((rx,by))]
        canvas.create_text(p[0][0],p[0][1],text='+',fill=self.color)
        canvas.create_text(p[1][0],p[1][1],text='-',fill=self.color)
        canvas.create_text(p[2][0],p[2][1],text='D',fill=self.color)
        canvas.create_text(p[3][0],p[3][1],text='C',fill=self.color)
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableMixedModeConverter(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureMixedModeConverter'])

class PartPictureVoltageControlledVoltageSourceFourPort(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(1,4),'b',False),PartPin(2,(1,0),'t',False),PartPin(3,(3,4),'b',False),PartPin(4,(3,0),'t',False)],[(0,1),(4,3)],[(0,0),(4,4)],(4.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        # the outline around the dependent source
        PartPicture.DrawDependent(self,canvas,grid,drawingOrigin,3)
        # plus and minus signs on the sensing port
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,1)
        # plus and minus signs inside the voltage source
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,3)
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVoltageControlledVoltageSourceFourPortAlt(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(2,(1,4),'b',False),PartPin(1,(1,0),'t',False),PartPin(3,(3,4),'b',False),PartPin(4,(3,0),'t',False)],[(0,1),(4,3)],[(0,0),(4,4)],(4.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        # the outline around the dependent source
        PartPicture.DrawDependent(self,canvas,grid,drawingOrigin,3)
        # minus and plus signs on the sensing port
        PartPicture.DrawMinusPlus(self,canvas,grid,drawingOrigin,1)
        # plus and minus signs inside the voltage source
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,3)
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableVoltageControlledVoltageSourceFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageControlledVoltageSourceFourPort','PartPictureVoltageControlledVoltageSourceFourPortAlt'])

class PartPictureCurrentControlledCurrentSourceFourPort(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(1,4),'b',False),PartPin(2,(1,0),'t',False),PartPin(3,(3,4),'b',False),PartPin(4,(3,0),'t',False)],[(0,1),(4,3)],[(0,0),(4,4)],(4.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        # the outline around the dependent source
        PartPicture.DrawDependent(self,canvas,grid,drawingOrigin,3)
        # arrow on the sensing port
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,1)
        # arrow inside the current source
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,3)
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureCurrentControlledCurrentSourceFourPortAlt(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(2,(1,4),'b',False),PartPin(1,(1,0),'t',False),PartPin(3,(3,4),'b',False),PartPin(4,(3,0),'t',False)],[(0,1),(4,3)],[(0,0),(4,4)],(4.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        # the outline around the dependent source
        PartPicture.DrawDependent(self,canvas,grid,drawingOrigin,3)
        # arrow on the sensing port
        PartPicture.DrawArrowDown(self,canvas,grid,drawingOrigin,1)
        # arrow inside the current source
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,3)
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCurrentControlledCurrentSourceFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentControlledCurrentSourceFourPort','PartPictureCurrentControlledCurrentSourceFourPortAlt'])

class PartPictureVoltageControlledCurrentSourceFourPort(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(1,4),'b',False),PartPin(2,(1,0),'t',False),PartPin(3,(3,4),'b',False),PartPin(4,(3,0),'t',False)],[(0,1),(4,3)],[(0,0),(4,4)],(4.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        # the outline around the dependent source
        PartPicture.DrawDependent(self,canvas,grid,drawingOrigin,3)
        # plus and minus signs on the sensing port
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,1)
        # arrow inside the current source
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,3)
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVoltageControlledCurrentSourceFourPortAlt(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(2,(1,4),'b',False),PartPin(1,(1,0),'t',False),PartPin(3,(3,4),'b',False),PartPin(4,(3,0),'t',False)],[(0,1),(4,3)],[(0,0),(4,4)],(4.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        # the outline around the dependent source
        PartPicture.DrawDependent(self,canvas,grid,drawingOrigin,3)
        # minus and plus signs on the sensing port
        PartPicture.DrawMinusPlus(self,canvas,grid,drawingOrigin,1)
        # arrow inside the current source
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,3)
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableVoltageControlledCurrentSourceFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageControlledCurrentSourceFourPort','PartPictureVoltageControlledCurrentSourceFourPortAlt'])

class PartPictureCurrentControlledVoltageSourceFourPort(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(1,4),'b',False),PartPin(2,(1,0),'t',False),PartPin(3,(3,4),'b',False),PartPin(4,(3,0),'t',False)],[(0,1),(4,3)],[(0,0),(4,4)],(4.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        # the outline around the dependent source
        PartPicture.DrawDependent(self,canvas,grid,drawingOrigin,3)
        # arrow on the sensing port
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,1)
        # plus and minus signs inside the voltage source
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,3)
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureCurrentControlledVoltageSourceFourPortAlt(PartPictureBox):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(2,(1,4),'b',False),PartPin(1,(1,0),'t',False),PartPin(3,(3,4),'b',False),PartPin(4,(3,0),'t',False)],[(0,1),(4,3)],[(0,0),(4,4)],(4.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        # the outline around the dependent source
        PartPicture.DrawDependent(self,canvas,grid,drawingOrigin,3)
        # arrow on the sensing port
        PartPicture.DrawArrowDown(self,canvas,grid,drawingOrigin,1)
        # plus and minus signs inside the voltage source
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,3)
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureVariableCurrentControlledVoltageSourceFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentControlledVoltageSourceFourPort','PartPictureCurrentControlledVoltageSourceFourPortAlt'])
