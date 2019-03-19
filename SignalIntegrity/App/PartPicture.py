"""
PartPicture.py
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

from SignalIntegrity.App.PartPin import *

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
    textSpacing=12
    def __init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation,orientation,mirroredHorizontally,mirroredVertically,rotationPoint=None):
        if rotationPoint==None:
            if len(pinList)==1:
                self.rotationPointSupplied=pinList[0]['ConnectionPoint']
            else:
                self.rotationPointSupplied = ((innerBox[0][0]+innerBox[1][0])/2.,(innerBox[0][1]+innerBox[1][1])/2.)
        else:
            self.rotationPointSupplied = rotationPoint
        self.origin=origin
        self.pinListSupplied = pinList
        self.innerBoxSupplied = innerBox
        self.boundingBoxSupplied = boundingBox
        self.propertiesLocationSupplied = propertiesLocation
        self.ApplyOrientation(orientation,mirroredHorizontally,mirroredVertically)
    def ApplyOrientation(self,orientation,mirroredHorizontally,mirroredVertically):
        if orientation in ['0','180']:
            self.rotationPoint=(self.rotationPointSupplied[0],math.floor(self.rotationPointSupplied[1]+0.501))
        else:
            self.rotationPoint=(math.floor(self.rotationPointSupplied[0]+0.501),self.rotationPointSupplied[1])
        self.orientation = orientation
        self.mirroredHorizontally=mirroredHorizontally
        self.mirroredVertically=mirroredVertically
        ct=CoordinateTranslater(self.rotationPoint,self.orientation,self.mirroredHorizontally,self.mirroredVertically)
        self.pinList = copy.deepcopy(self.pinListSupplied)
        pinOrientationList=['t','l','b','r']
        orientationList=['0','90','180','270']
        for pin in self.pinList:
            pinOrientation=pin['Orientation']
            numberSide=pin['NumberSide']
            oi=(pinOrientationList.index(pin['Orientation'])+orientationList.index(self.orientation))%4
            if self.mirroredHorizontally:
                if 'l' in numberSide: numberSide=numberSide.replace('l','r')
                elif 'r' in numberSide: numberSide=numberSide.replace('r','l')
                oi=(oi+(oi%2)*2)%4
            if self.mirroredVertically:
                if 'b' in numberSide: numberSide=numberSide.replace('b','t')
                elif 't' in numberSide: numberSide=numberSide.replace('t','b')
                oi=(oi+((oi+1)%2)*2)%4
            pin['Orientation']=pinOrientationList[oi]
            pin['NumberSide']=numberSide
            pin['ConnectionPoint']=str(ct.Translate(pin['ConnectionPoint']))
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
    def IsAt(self,coord,augmentor,distanceAllowed):
        xc=float(coord[0]+augmentor[0])
        yc=float(coord[1]+augmentor[1])
        xi=self.innerBox[0][0]+self.origin[0]
        yi=self.innerBox[0][1]+self.origin[1]
        xf=self.innerBox[1][0]+self.origin[0]
        yf=self.innerBox[1][1]+self.origin[1]
        if xc < min(xi,xf)-distanceAllowed:
            return False
        if xc > max(xi,xf)+distanceAllowed:
            return False
        if yc < min(yi,yf)-distanceAllowed:
            return False
        if yc > max(yi,yf)+distanceAllowed:
            return False
        return True
    def IsIn(self,i,f,ia,fa):
        minx=min(float(i[0]+ia[0]),float(f[0]+fa[0]))
        miny=min(float(i[1]+ia[1]),float(f[1]+fa[1]))
        maxx=max(float(i[0]+ia[0]),float(f[0]+fa[0]))
        maxy=max(float(i[1]+ia[1]),float(f[1]+fa[1]))
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
    def DrawDevice(self,canvas,grid,drawingOrigin,drawInnerBox=False,pinsConnectedList=None):
        #drawInnerBox=True
        if drawInnerBox:
            canvas.create_rectangle((drawingOrigin[0]+self.origin[0]+self.innerBox[0][0])*grid,
            (drawingOrigin[1]+self.origin[1]+self.innerBox[0][1])*grid,
            (drawingOrigin[0]+self.origin[0]+self.innerBox[1][0])*grid,
            (drawingOrigin[1]+self.origin[1]+self.innerBox[1][1])*grid, outline=self.color)
        for pinIndex in range(len(self.pinList)):
            pin = self.pinList[pinIndex]
            if pinsConnectedList is None:
                pinConnected=True
            else:
                pinConnected=pinsConnectedList[pinIndex]
            pin.DrawPin(canvas,grid,(self.origin[0]+drawingOrigin[0],self.origin[1]+drawingOrigin[1]),self.color,pinConnected)
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
            (drawingOrigin[1]+self.origin[1]+self.propertiesLocation[1])*grid-PartPicture.textSpacing*v) for v in range(V)]
        else:
            locations=[((drawingOrigin[0]+self.origin[0]+self.propertiesLocation[0])*grid,
            (drawingOrigin[1]+self.origin[1]+self.propertiesLocation[1])*grid+PartPicture.textSpacing*(V-v)-PartPicture.textSpacing) for v in range(V)]

        for v in range(V):
            canvas.create_text(locations[v][0],locations[v][1],
                text=self.visiblePartPropertyList[v],anchor=anchorString,fill=self.color)
    def PinCoordinates(self):
        return [(pin['ConnectionPoint'][0]+self.origin[0],pin['ConnectionPoint'][1]+self.origin[1]) for pin in self.pinList]
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
    def DrawPRBSSymbol(self,canvas,grid,drawingOrigin):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        mx=(drawingOrigin[0]+self.origin[0]+1)*grid
        my=(drawingOrigin[1]+self.origin[1]+2)*grid
        p=[ct.Translate((mx-grid/2,my+3*grid/8)),
            ct.Translate((mx-grid/4-grid/8,my+3*grid/8)),
            ct.Translate((mx-grid/4+grid/8,my-3*grid/8)),
            ct.Translate((mx+grid/4-grid/8,my-3*grid/8)),
            ct.Translate((mx+grid/4+grid/8,my+3*grid/8)),
            ct.Translate((mx+grid/2,my+3*grid/8))]
        canvas.create_line(p[0][0],p[0][1],
            p[1][0],p[1][1],
            p[2][0],p[2][1],
            p[3][0],p[3][1],
            p[4][0],p[4][1],
            p[5][0],p[5][1],
            fill=self.color)
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        mx=(drawingOrigin[0]+self.origin[0]+1)*grid
        my=(drawingOrigin[1]+self.origin[1]+2)*grid
        p=[ct.Translate((mx-grid/2,my-3*grid/8)),
            ct.Translate((mx-grid/4-grid/8,my-3*grid/8)),
            ct.Translate((mx-grid/4+grid/8,my+3*grid/8)),
            ct.Translate((mx+grid/4-grid/8,my+3*grid/8)),
            ct.Translate((mx+grid/4+grid/8,my-3*grid/8)),
            ct.Translate((mx+grid/2,my-3*grid/8))]
        canvas.create_line(p[0][0],p[0][1],
            p[1][0],p[1][1],
            p[2][0],p[2][1],
            p[3][0],p[3][1],
            p[4][0],p[4][1],
            p[5][0],p[5][1],
            fill=self.color)
    def DrawClockSymbol(self,canvas,grid,drawingOrigin):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        mx=(drawingOrigin[0]+self.origin[0]+1)*grid
        my=(drawingOrigin[1]+self.origin[1]+2)*grid
        p=[ct.Translate((mx-grid/2,my+3*grid/8)),
           ct.Translate((mx-grid/2,my-3*grid/8)),
           ct.Translate((mx-grid/4,my-3*grid/8)),
           ct.Translate((mx-grid/4,my+3*grid/8)),
           ct.Translate((mx,my+3*grid/8)),
           ct.Translate((mx,my-3*grid/8)),
           ct.Translate((mx+grid/4,my-3*grid/8)),
           ct.Translate((mx+grid/4,my+3*grid/8)),
           ct.Translate((mx+grid/2,my+3*grid/8)),
           ct.Translate((mx+grid/2,my-3*grid/8))]
        canvas.create_line(p[0][0],p[0][1],
            p[1][0],p[1][1],
            p[2][0],p[2][1],
            p[3][0],p[3][1],
            p[4][0],p[4][1],
            p[5][0],p[5][1],
            p[6][0],p[6][1],
            p[7][0],p[7][1],
            p[8][0],p[8][1],
            p[9][0],p[9][1],
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
    def DrawTransmissionLine(self,canvas,grid,drawingOrigin):
        my=(drawingOrigin[1]+self.origin[1])*grid+grid
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        # the oval at the front of the line
        p=[ct.Translate((lx-grid/4,my-grid/2)),ct.Translate((lx+grid/4,my+grid/2))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1],outline=self.color)
        # the arc at the back of the line
        p=[ct.Translate((rx-grid/2,my-grid/2)),ct.Translate((rx,my+grid/2))]
        r=self.ArcConverter(-90, 180, int(ct.rotationAngle), ct.mirroredVertically, ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r[0],extent=r[1],style='arc',outline=self.color)
        # the lines connecting the ovals
        p=[ct.Translate((lx,my-grid/2)),ct.Translate((rx-grid/4,my-grid/2))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color)
        p=[ct.Translate((lx,my+grid/2)),ct.Translate((rx-grid/4,my+grid/2))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color)
    def DrawDifferentialTransmissionLine(self,canvas,grid,drawingOrigin):
        my=(drawingOrigin[1]+self.origin[1])*grid+grid+grid/2
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        # the oval at the front of the line
        p=[ct.Translate((lx-grid/4,my-grid/2-grid/2)),ct.Translate((lx+grid/4,my+grid/2+grid/2))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1],outline=self.color)
        # the arc at the back of the line
        p=[ct.Translate((rx-grid/2,my-grid/2-grid/2)),ct.Translate((rx,my+grid/2+grid/2))]
        r=self.ArcConverter(-90, 180, int(ct.rotationAngle), ct.mirroredVertically, ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r[0],extent=r[1],style='arc',outline=self.color)
        # the lines connecting the ovals
        p=[ct.Translate((lx,my-grid/2-grid/2)),ct.Translate((rx-grid/4,my-grid/2-grid/2))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color)
        p=[ct.Translate((lx,my+grid/2+grid/2)),ct.Translate((rx-grid/4,my+grid/2+grid/2))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color)
    def DrawCharacterInMiddle(self,canvas,grid,drawingOrigin,c):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        lx=(drawingOrigin[0]+self.origin[0]+self.innerBox[0][0])*grid
        rx=(drawingOrigin[0]+self.origin[0]+self.innerBox[1][0])*grid
        ty=(drawingOrigin[1]+self.origin[1]+self.innerBox[0][1])*grid
        by=(drawingOrigin[1]+self.origin[1]+self.innerBox[1][1])*grid
        mx=(lx+rx)/2
        my=(ty+by)/2
        #p=ct.Translate((mx,my))
        p=(mx,my)
        canvas.create_text(p[0],p[1],text=c,fill=self.color)
    def DrawFourPortAmpConnectorLines(self,canvas,grid,drawingOrigin):
        # put the connector lines from the edge of the amp to the pins
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        lx=(drawingOrigin[0]+self.origin[0]+2.5)*grid
        rx=(drawingOrigin[0]+self.origin[0]+4)*grid
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid
        by=(drawingOrigin[1]+self.origin[1]+3)*grid
        p=[ct.Translate((lx,ty)),ct.Translate((rx,ty)),ct.Translate((lx,by)),ct.Translate((rx,by))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color)
        canvas.create_line(p[2][0],p[2][1],p[3][0],p[3][1],fill=self.color)


class PartPictureFromProject(object):
    def __init__(self,partPictureClassList,partPictureProject,ports):
        if partPictureProject['Index'] is None:
            partPictureProject['Index'] = partPictureClassList.index(partPictureProject['ClassName'])
#         if not partPictureProject['ClassName'] in partPictureClassList:
#             # this probably means that I renamed the part picture
#             # This is a really nasty way to mitigate this, and just hope that it works for the user
#             partPictureProject['ClassName']=partPictureClassList[0]
        partPictureSelected = partPictureProject['Index']
        origin=partPictureProject['Origin']
        orientation=str(partPictureProject['Orientation'])
        mirroredVertically=partPictureProject['MirroredVertically']
        mirroredHorizontally=partPictureProject['MirroredHorizontally']
        self.result=PartPictureVariable(partPictureClassList,ports,partPictureSelected,origin,orientation,mirroredHorizontally,mirroredVertically)

class PartPictureVariable(object):
    def __init__(self,partPictureClassList,ports,partPictureSelected=0,origin=(0,0),orientation='0',mirroredHorizontally=False,mirroredVertically=False):
        self.partPictureClassList = partPictureClassList
        self.partPictureSelected = partPictureSelected
        self.ports=ports
        self.current=eval(self.partPictureClassList[self.partPictureSelected])(self.ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def SwitchPartPicture(self,item):
        orientation=self.current.orientation
        mirroredHorizontally=self.current.mirroredHorizontally
        mirroredVertically=self.current.mirroredVertically
        origin=self.current.origin
        self.partPictureSelected = item
        self.current=eval(self.partPictureClassList[self.partPictureSelected])(self.ports,origin,orientation,mirroredHorizontally,mirroredVertically)

class PartPictureBox(PartPicture):
    def __init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,True,connected)

class PartPictureAmp(PartPicture):
    def __init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,pinList,innerBox,boundingBox,propertiesLocation,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        rx=(drawingOrigin[0]+self.origin[0]+4)*grid
        ty=(drawingOrigin[1]+self.origin[1]+0)*grid
        by=(drawingOrigin[1]+self.origin[1]+4)*grid
        mx=(lx+rx)/2
        my=(ty+by)/2
        p=[ct.Translate((lx,ty)),ct.Translate((rx,my)),ct.Translate((lx,by)),ct.Translate((lx,ty))]
        canvas.create_line(p[0][0],p[0][1],
            p[1][0],p[1][1],
            p[2][0],p[2][1],
            p[3][0],p[3][1],fill=self.color)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureAmpTwoPort(PartPictureAmp):
    def __init__(self,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmp.__init__(self,origin,[PartPin(1,(0,2),'l',False,True,True),PartPin(2,(5,2),'r',False,True,True,'n')],[(1,0),(4,4)],[(1,0),(4,4)],(2,0),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPictureAmp.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureAmpFourPort(PartPictureAmp):
    def __init__(self,origin,pinorder,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmp.__init__(self,origin,
                                [PartPin(pinorder[0],(0,1),'l',False,True,True,'tl'),
                                 PartPin(pinorder[1],(0,3),'l',False,True,True,'bl'),
                                 PartPin(pinorder[2],(4,1),'r',False,True,True,'tr'),
                                 PartPin(pinorder[3],(4,3),'r',False,True,True,'br')],
                                [(1,0),(3,4)],[(1,0),(3,4)],(2,0),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # put the connector lines from the edge of the amp to the pins
        self.DrawFourPortAmpConnectorLines(canvas, grid, drawingOrigin)
        # draw remainder of amplifier
        PartPictureAmp.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureDependent(PartPictureBox):
    # normal pin order [1,2,3,4] looks like this:
    #
    #       +------+
    #     2 |      | 4
    #    ---+      +---
    #       |      |
    #     1 |      | 3
    #    ---+      +---
    #       |      |
    #       +------+
    def __init__(self,origin,pinorder,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,
                                [PartPin(pinorder[0],(1,4),'b',False,True,True),
                                 PartPin(pinorder[1],(1,0),'t',False,True,True),
                                 PartPin(pinorder[2],(3,4),'b',False,True,True),
                                 PartPin(pinorder[3],(3,0),'t',False,True,True)],
                                [(0,1),(4,3)],[(0,0),(4,4)],(4.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # the outline around the dependent source
        PartPicture.DrawDependent(self,canvas,grid,drawingOrigin,3)
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin,connected)
    
class PartPictureSpecifiedPorts(PartPictureBox):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        LeftPorts=(ports+1)//2
        RightPorts=ports-LeftPorts
        RightPinOffset = 1 if RightPorts < LeftPorts else 0
        PartPictureBox.__init__(self,origin,
            [PartPin(lp+1,(0,lp*2+1),'l',True,True,True) for lp in range(LeftPorts)]+[PartPin(rp+LeftPorts+1,(4,rp*2+1+RightPinOffset),'r',True,True,True) for rp in range(RightPorts)],
            [(1,0),(3,LeftPorts*2)],[(0,0),(4,LeftPorts*2)],(2,-0.5),orientation,mirroredHorizontally,mirroredVertically)

class PartPictureSpecifiedPortsAcross(PartPictureBox):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        LeftPorts=(ports+1)//2
        RightPorts=ports-LeftPorts
        RightPinOffset = 1 if RightPorts < LeftPorts else 0
        PartPictureBox.__init__(self,origin,
            [PartPin(lp*2+1,(0,lp*2+1),'l',True,True,True) for lp in range(LeftPorts)]+[PartPin(rp*2+2,(4,rp*2+1+RightPinOffset),'r',True,True,True) for rp in range(RightPorts)],
            [(1,0),(3,LeftPorts*2)],[(0,0),(4,LeftPorts*2)],(2,-0.5),orientation,mirroredHorizontally,mirroredVertically)

class PartPictureSpecifiedPortsDownAndUp(PartPictureBox):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        LeftPorts=(ports+1)//2
        RightPorts=ports-LeftPorts
        RightPinOffset = 1 if RightPorts < LeftPorts else 0
        PartPictureBox.__init__(self,origin,
            [PartPin(lp+1,(0,lp*2+1),'l',True,True,True) for lp in range(LeftPorts)]+[PartPin(ports-rp,(4,rp*2+1+RightPinOffset),'r',True,True,True) for rp in range(RightPorts)],
            [(1,0),(3,LeftPorts*2)],[(0,0),(4,LeftPorts*2)],(2,-0.5),orientation,mirroredHorizontally,mirroredVertically)

class PartPictureSpecifiedPortsSide(PartPictureBox):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(p+1,(0,p*2+1),'l',True,True,True) for p in range(ports)],[(1,0),(3,ports*2)],[(0,0),(4,ports*2)],(2,-0.5),orientation,mirroredHorizontally,mirroredVertically)

class PartPictureVariableSpecifiedPorts(PartPictureVariable):
    def __init__(self,ports=4):
        PartPictureVariable.__init__(self,['PartPictureSpecifiedPorts','PartPictureSpecifiedPortsAcross','PartPictureSpecifiedPortsDownAndUp','PartPictureSpecifiedPortsSide'],ports)

class PartPicturePort(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(3,1),'r',False,True,False)],[(1.5,0.5),(2.5,1.5)],[(0,0),(3,2)],(1.5,1),orientation,mirroredHorizontally,mirroredVertically,(3,1))
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid+grid/2
        rx=(drawingOrigin[0]+self.origin[0]+2)*grid
        ty=(drawingOrigin[1]+self.origin[1]+0)*grid+grid/2
        my=(drawingOrigin[1]+self.origin[1]+1)*grid
        by=(drawingOrigin[1]+self.origin[1]+1)*grid+grid/2
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,ty)),ct.Translate((rx,my)),ct.Translate((lx,by))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],p[2][0],p[2][1],fill=self.color)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariablePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPicturePort'],1)

class PartPictureGround(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,
                             [PartPin(1,(1,0),'t',False,True,False)],
                             [(0.25,1.0),(1.75,1.75)],[(0,0),(2,2)],(2,1),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawGround(self,canvas,grid,drawingOrigin,1,1)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableGround(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureGround'],1)

class PartPictureOpen(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(2,1),'r',False,True,False)],[(0.5,0.5),(1.5,1.5)],[(0,0),(2,2)],(0,1),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid-grid/4
        rx=(drawingOrigin[0]+self.origin[0]+1)*grid+grid/4
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid-grid/4
        by=(drawingOrigin[1]+self.origin[1]+1)*grid+grid/4
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,ty)),ct.Translate((rx,by))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color)
        p=[ct.Translate((rx,ty)),ct.Translate((lx,by))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableOpen(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureOpen'],1)

class PartPictureDirectionalCouplerThreePort(PartPictureBox):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(0,1),'l',False,True,True),PartPin(2,(4,1),'r',False,True,True),PartPin(3,(2,3),'b',False,True,True)],[(1,0),(3,2)],[(0,0),(4,3)],(2,-0.5),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sensing port
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid
        y=(drawingOrigin[1]+self.origin[1]+1)*grid
        p=[ct.Translate((lx,y)),ct.Translate((rx,y))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color)
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        sx=(drawingOrigin[0]+self.origin[0]+0)*grid
        sy=(drawingOrigin[1]+self.origin[1]+1)*grid
        ex=(drawingOrigin[0]+self.origin[0]+2)*grid
        ey=(drawingOrigin[1]+self.origin[1]+2.5)*grid
        p=[ct.Translate((sx,sy)),ct.Translate((ex,ey))]
        r0=self.ArcConverter(0,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r0[0],extent=r0[1],style='arc',outline=self.color)
        x=(drawingOrigin[0]+self.origin[0]+2)*grid
        sy=(drawingOrigin[1]+self.origin[1]+1.75)*grid
        ey=(drawingOrigin[1]+self.origin[1]+2)*grid
        p=[ct.Translate((x,sy)),ct.Translate((x,ey))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,arrow='last',arrowshape=((8*grid)/20,(10*grid)/20,(3*grid)/20))        
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableDirectionalCouplerThreePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureDirectionalCouplerThreePort'],3)

class PartPictureDirectionalCouplerFourPort(PartPictureBox):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(0,2),'l',False,True,True),PartPin(2,(4,2),'r',False,True,True),PartPin(3,(2,4),'b',False,True,True),PartPin(4,(2,0),'t',False,True,True)],[(1,1),(3,3)],[(0,0),(4,4)],(1,0.5),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sensing port
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid
        y=(drawingOrigin[1]+self.origin[1]+2)*grid
        p=[ct.Translate((lx,y)),ct.Translate((rx,y))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color)
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        sx=(drawingOrigin[0]+self.origin[0]+0)*grid
        sy=(drawingOrigin[1]+self.origin[1]+2)*grid
        ex=(drawingOrigin[0]+self.origin[0]+2)*grid
        ey=(drawingOrigin[1]+self.origin[1]+3.5)*grid
        p=[ct.Translate((sx,sy)),ct.Translate((ex,ey))]
        r0=self.ArcConverter(0,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r0[0],extent=r0[1],style='arc',outline=self.color)
        x=(drawingOrigin[0]+self.origin[0]+2)*grid
        sy=(drawingOrigin[1]+self.origin[1]+2.75)*grid
        ey=(drawingOrigin[1]+self.origin[1]+3)*grid
        p=[ct.Translate((x,sy)),ct.Translate((x,ey))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,arrow='last',arrowshape=((8*grid)/20,(10*grid)/20,(3*grid)/20))        
        sx=(drawingOrigin[0]+self.origin[0]+2)*grid
        sy=(drawingOrigin[1]+self.origin[1]+0.5)*grid
        ex=(drawingOrigin[0]+self.origin[0]+4)*grid
        ey=(drawingOrigin[1]+self.origin[1]+2)*grid
        p=[ct.Translate((sx,sy)),ct.Translate((ex,ey))]
        r0=self.ArcConverter(180,90,int(ct.rotationAngle),ct.mirroredVertically,ct.mirroredHorizontally)
        canvas.create_arc(p[0][0],p[0][1],p[1][0],p[1][1],start=r0[0],extent=r0[1],style='arc',outline=self.color)
        x=(drawingOrigin[0]+self.origin[0]+2)*grid
        sy=(drawingOrigin[1]+self.origin[1]+1.25)*grid
        ey=(drawingOrigin[1]+self.origin[1]+1)*grid
        p=[ct.Translate((x,sy)),ct.Translate((x,ey))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,arrow='last',arrowshape=((8*grid)/20,(10*grid)/20,(3*grid)/20))        
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableDirectionalCouplerFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureDirectionalCouplerFourPort'],3)

class PartPictureInductorTwoPort(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(0,1),'l',False,True,False),PartPin(2,(4,1),'r',False,True,False)],[(1,0.5),(3,1.5)],[(0,0),(4,2)],(2,0),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
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
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableInductorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureInductorTwoPort'],2)

class PartPictureMutual(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,
                             [PartPin(1,(0,1),'l',False,True,True,'tl'),
                              PartPin(3,(0,3),'l',False,True,True,'tr'),
                              PartPin(2,(4,1),'r',False,True,True,'bl'),
                              PartPin(4,(4,3),'r',False,True,True,'br')],
                             [(1,0.5),(3,3.5)],[(0,0),(4,4)],(2,0),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
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
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableMutual(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureMutual'],4)

class PartPictureIdealTransformerBase(PartPicture):
    def __init__(self,origin,pinorder,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,
                             [PartPin(pinorder[0],(0,1),'l',False,True,True,'tl'),
                              PartPin(pinorder[1],(0,3),'l',False,True,True,'bl'),
                              PartPin(pinorder[2],(4,1),'r',False,True,True,'tr'),
                              PartPin(pinorder[3],(4,3),'r',False,True,True,'br')],
                             [(1,1),(3,3)],[(0,0),(4,4)],(2,0.5),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
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
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureIdealTransformer(PartPictureIdealTransformerBase):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureIdealTransformerBase.__init__(self,origin,[1,2,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
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
        PartPictureIdealTransformerBase.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureIdealTransformerAlt(PartPictureIdealTransformerBase):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureIdealTransformerBase.__init__(self,origin,[1,2,4,3],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        # dot on the primary
        lx=(drawingOrigin[0]+self.origin[0])*grid+3*grid/4
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid+grid/8
        size=grid/8
        p=[ct.Translate((lx,ty)),ct.Translate((lx+size,ty+size))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,outline=self.color)
        # dot on the secondary
        lx=(drawingOrigin[0]+self.origin[0]+3)*grid
        ty=(drawingOrigin[1]+self.origin[1]+3)*grid-grid/4
        size=grid/8
        p=[ct.Translate((lx,ty)),ct.Translate((lx+size,ty+size))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,outline=self.color)
        PartPictureIdealTransformerBase.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureIdealTransformerAlt2(PartPictureIdealTransformerBase):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureIdealTransformerBase.__init__(self,origin,[2,1,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        # dot on the primary
        lx=(drawingOrigin[0]+self.origin[0])*grid+3*grid/4
        ty=(drawingOrigin[1]+self.origin[1]+3)*grid-grid/4
        size=grid/8
        p=[ct.Translate((lx,ty)),ct.Translate((lx+size,ty+size))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,outline=self.color)
        # dot on the secondary
        lx=(drawingOrigin[0]+self.origin[0]+3)*grid
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid+grid/8
        size=grid/8
        p=[ct.Translate((lx,ty)),ct.Translate((lx+size,ty+size))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,outline=self.color)
        PartPictureIdealTransformerBase.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureIdealTransformerAlt3(PartPictureIdealTransformerBase):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureIdealTransformerBase.__init__(self,origin,[2,1,4,3],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        # dot on the primary
        lx=(drawingOrigin[0]+self.origin[0])*grid+3*grid/4
        ty=(drawingOrigin[1]+self.origin[1]+3)*grid-grid/4
        size=grid/8
        p=[ct.Translate((lx,ty)),ct.Translate((lx+size,ty+size))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,outline=self.color)
        # dot on the secondary
        lx=(drawingOrigin[0]+self.origin[0]+3)*grid
        ty=(drawingOrigin[1]+self.origin[1]+3)*grid-grid/4
        size=grid/8
        p=[ct.Translate((lx,ty)),ct.Translate((lx+size,ty+size))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,outline=self.color)
        PartPictureIdealTransformerBase.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableIdealTransformer(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureIdealTransformer','PartPictureIdealTransformerAlt','PartPictureIdealTransformerAlt2','PartPictureIdealTransformerAlt3'],4)

class PartPictureResistorTwoPort(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(0,1),'l',False,True,False),PartPin(2,(4,1),'r',False,True,False)],[(1.0,0.5),(3.0,1.5)],[(0,0),(4,2)],(2,0),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
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
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableResistorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureResistorTwoPort'],2)

class PartPictureResistorOnePort(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(1,0),'t',False,True,False)],[(0.5,1),(1.5,4.75)],[(0,0),(2,5)],(2,2.5),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
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
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableResistorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureResistorOnePort'],1)

class PartPictureCapacitorTwoPort(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(0,1),'l',False,True,False),PartPin(2,(4,1),'r',False,True,False)],[(1.0,0.5),(3.0,1.5)],[(0,0),(4,2)],(2,0),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
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
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableCapacitorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCapacitorTwoPort'],2)

class PartPictureCapacitorOnePort(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(1,0),'t',False,True,False)],[(0.5,1),(1.5,4.75)],[(0,0),(2,5)],(2,2.5),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
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
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableCapacitorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCapacitorOnePort'],1)

class PartPictureVoltageSourceTwoPort(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(2,(1,0),'t',False,True,True),PartPin(1,(1,4),'b',False,True,True)],[(0,1),(2,3)],[(0,0),(2,4)],(2.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawIndependent(self,canvas,grid,drawingOrigin)
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,1)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableVoltageSourceTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceTwoPort'],2)

class PartPictureVoltageSourceStepGeneratorTwoPort(PartPictureVoltageSourceTwoPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceTwoPort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawStepSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageSourceStepGeneratorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceStepGeneratorTwoPort'],2)

class PartPictureVoltageSourceNoiseSourceTwoPort(PartPictureVoltageSourceTwoPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceTwoPort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        self.DrawCharacterInMiddle(canvas,grid,drawingOrigin,u"\u03C3")
        PartPictureVoltageSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageSourceNoiseSourceTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceNoiseSourceTwoPort'],2)

class PartPictureVoltageSourcePulseGeneratorTwoPort(PartPictureVoltageSourceTwoPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceTwoPort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawPulseSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageSourcePulseGeneratorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourcePulseGeneratorTwoPort'],2)

class PartPictureVoltageSourcePRBSGeneratorTwoPort(PartPictureVoltageSourceTwoPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceTwoPort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawPRBSSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageSourcePRBSGeneratorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourcePRBSGeneratorTwoPort'],2)

class PartPictureVoltageSourceClockGeneratorTwoPort(PartPictureVoltageSourceTwoPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceTwoPort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawClockSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageSourceClockGeneratorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceClockGeneratorTwoPort'],2)

class PartPictureVoltageSourceSineGeneratorTwoPort(PartPictureVoltageSourceTwoPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceTwoPort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawSineSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageSourceSineGeneratorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceSineGeneratorTwoPort'],2)

class PartPictureVoltageSourceOnePort(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(1,0),'t',False,True,False)],[(0,1),(2,3)],[(0,0),(2,5)],(2.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawIndependent(self,canvas,grid,drawingOrigin)
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,1)
        PartPicture.DrawStem(self,canvas,grid,drawingOrigin,1,3)
        PartPicture.DrawGround(self,canvas,grid,drawingOrigin,1,4)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableVoltageSourceOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceOnePort'],1)

class PartPictureVoltageSourceStepGeneratorOnePort(PartPictureVoltageSourceOnePort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceOnePort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawStepSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageSourceStepGeneratorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceStepGeneratorOnePort'],1)

class PartPictureVoltageSourceNoiseSourceOnePort(PartPictureVoltageSourceOnePort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceOnePort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        self.DrawCharacterInMiddle(canvas,grid,drawingOrigin,u"\u03C3")
        PartPictureVoltageSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageSourceNoiseSourceOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceNoiseSourceOnePort'],1)

class PartPictureVoltageSourcePulseGeneratorOnePort(PartPictureVoltageSourceOnePort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceOnePort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawPulseSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageSourcePulseGeneratorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourcePulseGeneratorOnePort'],1)

class PartPictureVoltageSourcePRBSGeneratorOnePort(PartPictureVoltageSourceOnePort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceOnePort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawPRBSSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageSourcePRBSGeneratorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourcePRBSGeneratorOnePort'],1)

class PartPictureVoltageSourceClockGeneratorOnePort(PartPictureVoltageSourceOnePort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceOnePort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawClockSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageSourceClockGeneratorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceClockGeneratorOnePort'],1)


class PartPictureVoltageSourceSineGeneratorOnePort(PartPictureVoltageSourceOnePort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureVoltageSourceOnePort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawSineSymbol(self,canvas,grid,drawingOrigin)
        PartPictureVoltageSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageSourceSineGeneratorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageSourceSineGeneratorOnePort'],1)

class PartPictureCurrentSourceTwoPort(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(2,(1,0),'t',False,True,True),PartPin(1,(1,4),'b',False,True,True)],[(0,1),(2,3)],[(0,0),(2,4)],(2.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawIndependent(self,canvas,grid,drawingOrigin)
        # arrow inside the current source
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,1)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableCurrentSourceTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourceTwoPort'],2)

class PartPictureCurrentSourceStepGeneratorTwoPort(PartPictureCurrentSourceTwoPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureCurrentSourceTwoPort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawStepSymbol(self,canvas,grid,drawingOrigin)
        PartPictureCurrentSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableCurrentSourceStepGeneratorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourceStepGeneratorTwoPort'],2)

class PartPictureCurrentSourcePulseGeneratorTwoPort(PartPictureCurrentSourceTwoPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureCurrentSourceTwoPort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawPulseSymbol(self,canvas,grid,drawingOrigin)
        PartPictureCurrentSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableCurrentSourcePulseGeneratorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourcePulseGeneratorTwoPort'],2)

class PartPictureCurrentSourceSineGeneratorTwoPort(PartPictureCurrentSourceTwoPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureCurrentSourceTwoPort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawSineSymbol(self,canvas,grid,drawingOrigin)
        PartPictureCurrentSourceTwoPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableCurrentSourceSineGeneratorTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourceSineGeneratorTwoPort'],2)

class PartPictureCurrentSourceOnePort(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(1,0),'t',False,True,False)],[(0,1),(2,3)],[(0,0),(2,4)],(2.5,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawIndependent(self,canvas,grid,drawingOrigin)
        # arrow inside the current source
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,1)
        PartPicture.DrawStem(self,canvas,grid,drawingOrigin,1,3)
        PartPicture.DrawGround(self,canvas,grid,drawingOrigin,1,4)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableCurrentSourceOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourceOnePort'],1)

class PartPictureCurrentSourceStepGeneratorOnePort(PartPictureCurrentSourceOnePort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureCurrentSourceOnePort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawStepSymbol(self,canvas,grid,drawingOrigin)
        PartPictureCurrentSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableCurrentSourceStepGeneratorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourceStepGeneratorOnePort'],1)

class PartPictureCurrentSourcePulseGeneratorOnePort(PartPictureCurrentSourceOnePort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureCurrentSourceOnePort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawPulseSymbol(self,canvas,grid,drawingOrigin)
        PartPictureCurrentSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableCurrentSourcePulseGeneratorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourcePulseGeneratorOnePort'],1)

class PartPictureCurrentSourceSineGeneratorOnePort(PartPictureCurrentSourceOnePort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureCurrentSourceOnePort.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPicture.DrawSineSymbol(self,canvas,grid,drawingOrigin)
        PartPictureCurrentSourceOnePort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableCurrentSourceSineGeneratorOnePort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentSourceSineGeneratorOnePort'],1)

class PartPictureProbe(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(0,1),'l',False,False,False)],[(0,0),(1,1)],[(0,0),(1,1)],(1,0),orientation,mirroredHorizontally,mirroredVertically,(0,1))
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
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
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableProbe(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureProbe'],1)

class PartPictureMeasureProbe(PartPictureBox):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(0,1),'l',False,False,False)],[(0.5,0),(1,0.5)],[(0,0),(1,1)],(1,0),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
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
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableMeasureProbe(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureMeasureProbe'],1)

class PartPicturePowerMixedModeConverter(PartPictureBox):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(0,1),'l',False,True,True),PartPin(2,(0,3),'l',False,True,True),PartPin(3,(4,1),'r',False,True,True),PartPin(4,(4,3),'r',False,True,True)],[(1,0),(3,4)],[(0,0),(4,4)],(2,-0.5),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
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
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariablePowerMixedModeConverter(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPicturePowerMixedModeConverter'],4)

class PartPictureVoltageMixedModeConverter(PartPictureBox):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(0,1),'l',False,True,True),PartPin(2,(0,3),'l',False,True,True),PartPin(3,(4,1),'r',False,True,True),PartPin(4,(4,3),'r',False,True,True)],[(1,0),(3,4)],[(0,0),(4,4)],(2,-0.5),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid+grid/2
        ty=(drawingOrigin[1]+self.origin[1]+1)*grid
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid-grid/2
        by=(drawingOrigin[1]+self.origin[1]+3)*grid
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        p=[ct.Translate((lx,ty)),
           ct.Translate((lx,by)),
           ct.Translate((rx,ty)),
           ct.Translate((rx,by)),
           ct.Translate(((lx+rx)/2,(ty+by)/2))]
        canvas.create_text(p[0][0],p[0][1],text='+',fill=self.color)
        canvas.create_text(p[1][0],p[1][1],text='-',fill=self.color)
        canvas.create_text(p[2][0],p[2][1],text='D',fill=self.color)
        canvas.create_text(p[3][0],p[3][1],text='C',fill=self.color)
        canvas.create_text(p[4][0],p[4][1],text='V',fill=self.color)
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageMixedModeConverter(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageMixedModeConverter'],4)

class PartPictureVoltageControlledVoltageSourceFourPort(PartPictureDependent):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureDependent.__init__(self,origin,[1,2,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # plus and minus signs on the sensing port
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,1)
        # plus and minus signs inside the voltage source
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,3)
        PartPictureDependent.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVoltageControlledVoltageSourceFourPortAlt(PartPictureDependent):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureDependent.__init__(self,origin,[2,1,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # minus and plus signs on the sensing port
        PartPicture.DrawMinusPlus(self,canvas,grid,drawingOrigin,1)
        # plus and minus signs inside the voltage source
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,3)
        PartPictureDependent.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageControlledVoltageSourceFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageControlledVoltageSourceFourPort','PartPictureVoltageControlledVoltageSourceFourPortAlt'],4)

class PartPictureVoltageAmplifierTwoPort(PartPictureAmpTwoPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpTwoPort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        PartPictureAmpTwoPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageAmplifierTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageAmplifierTwoPort'],2)

class PartPictureVoltageAmplifierFourPort(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[1,2,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # plus and minus signs on the sensing port
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,1.5)
        # plus and minus signs on the output port
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,2.5)
        # draw remainder of amplifier
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVoltageAmplifierFourPortAlt(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[1,2,4,3],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # plus and minus signs on the sensing port
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,1.5)
        # plus and minus signs on the output port
        PartPicture.DrawMinusPlus(self,canvas,grid,drawingOrigin,2.5)
        # draw remainder of amplifier
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVoltageAmplifierFourPortAlt2(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[2,1,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # plus and minus signs on the sensing port
        PartPicture.DrawMinusPlus(self,canvas,grid,drawingOrigin,1.5)
        # plus and minus signs on the output port
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,2.5)
        # draw remainder of amplifier
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVoltageAmplifierFourPortAlt3(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[2,1,4,3],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # plus and minus signs on the sensing port
        PartPicture.DrawMinusPlus(self,canvas,grid,drawingOrigin,1.5)
        # plus and minus signs on the output port
        PartPicture.DrawMinusPlus(self,canvas,grid,drawingOrigin,2.5)
        # draw remainder of amplifier
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageAmplifierFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageAmplifierFourPort','PartPictureVoltageAmplifierFourPortAlt','PartPictureVoltageAmplifierFourPortAlt2','PartPictureVoltageAmplifierFourPortAlt3'],4)

class PartPictureOperationalAmplifier(PartPictureAmp):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmp.__init__(self,origin,[PartPin(1,(0,3),'l',False,True,True),PartPin(2,(0,1),'l',False,True,True),PartPin(3,(5,2),'r',False,True,True)],[(1,0),(4,4)],[(1,0),(4,4)],(2,0),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # minus and plus signs on the sensing port
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,1.5)
        PartPictureAmp.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableOperationalAmplifier(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureOperationalAmplifier'],3)

class PartPictureCurrentControlledCurrentSourceFourPort(PartPictureDependent):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureDependent.__init__(self,origin,[1,2,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sensing port
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,1)
        # arrow inside the current source
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,3)
        PartPictureDependent.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureCurrentControlledCurrentSourceFourPortAlt(PartPictureDependent):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureDependent.__init__(self,origin,[2,1,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sensing port
        PartPicture.DrawArrowDown(self,canvas,grid,drawingOrigin,1)
        # arrow inside the current source
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,3)
        PartPictureDependent.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableCurrentControlledCurrentSourceFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentControlledCurrentSourceFourPort','PartPictureCurrentControlledCurrentSourceFourPortAlt'],4)

class PartPictureCurrentAmplifierTwoPort(PartPictureAmpTwoPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpTwoPort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # draw arrow to the right
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        lx=(drawingOrigin[0]+self.origin[0]+0+1.5)*grid
        rx=(drawingOrigin[0]+self.origin[0]+0+3)*grid
        my=(drawingOrigin[1]+self.origin[1]+0+2)*grid
        p=[ct.Translate((lx,my)),ct.Translate((rx,my))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,arrow='last',arrowshape=((8*grid)/20,(10*grid)/20,(3*grid)/20))
        PartPictureAmpTwoPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableCurrentAmplifierTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentAmplifierTwoPort'],2)

class PartPictureCurrentAmplifierFourPort(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[1,2,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sensing port
        PartPicture.DrawArrowDown(self,canvas,grid,drawingOrigin,1.5)
        # arrow on the output
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,2.5)
        # draw remainder of amplifier
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureCurrentAmplifierFourPortAlt(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[1,2,4,3],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sensing port
        PartPicture.DrawArrowDown(self,canvas,grid,drawingOrigin,1.5)
        # arrow on the output
        PartPicture.DrawArrowDown(self,canvas,grid,drawingOrigin,2.5)
        # draw remainder of amplifier
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureCurrentAmplifierFourPortAlt2(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[2,1,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sensing port
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,1.5)
        # arrow on the output
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,2.5)
        # draw remainder of amplifier
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureCurrentAmplifierFourPortAlt3(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[2,1,4,3],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sensing port
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,1.5)
        # arrow on the output
        PartPicture.DrawArrowDown(self,canvas,grid,drawingOrigin,2.5)
        # draw remainder of amplifier
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableCurrentAmplifierFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentAmplifierFourPort','PartPictureCurrentAmplifierFourPortAlt','PartPictureCurrentAmplifierFourPortAlt2','PartPictureCurrentAmplifierFourPortAlt3'],4)

class PartPictureVoltageControlledCurrentSourceFourPort(PartPictureDependent):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureDependent.__init__(self,origin,[1,2,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # plus and minus signs on the sensing port
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,1)
        # arrow inside the current source
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,3)
        PartPictureDependent.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVoltageControlledCurrentSourceFourPortAlt(PartPictureDependent):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureDependent.__init__(self,origin,[2,1,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # minus and plus signs on the sensing port
        PartPicture.DrawMinusPlus(self,canvas,grid,drawingOrigin,1)
        # arrow inside the current source
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,3)
        PartPictureDependent.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableVoltageControlledCurrentSourceFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageControlledCurrentSourceFourPort','PartPictureVoltageControlledCurrentSourceFourPortAlt'],4)

class PartPictureTransconductanceAmplifierTwoPort(PartPictureAmpTwoPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpTwoPort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # draw a plus sign at the input
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        px=(drawingOrigin[0]+self.origin[0]+1.5)*grid
        py=(drawingOrigin[1]+self.origin[1]+2)*grid
        pw=3*grid/16
        p=[[ct.Translate((px-pw,py)),ct.Translate((px+pw,py))],
           [ct.Translate((px,py-pw)),ct.Translate((px,py+pw))],]
        canvas.create_line(p[0][0][0],p[0][0][1],p[0][1][0],p[0][1][1],fill=self.color)
        canvas.create_line(p[1][0][0],p[1][0][1],p[1][1][0],p[1][1][1],fill=self.color)
        # draw short arrow to the right for the output
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        lx=(drawingOrigin[0]+self.origin[0]+0+2)*grid
        rx=(drawingOrigin[0]+self.origin[0]+0+3.5)*grid
        my=(drawingOrigin[1]+self.origin[1]+0+2)*grid
        p=[ct.Translate((lx,my)),ct.Translate((rx,my))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,arrow='last',arrowshape=((8*grid)/20,(10*grid)/20,(3*grid)/20))
        PartPictureAmpTwoPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableTransconductanceAmplifierTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureTransconductanceAmplifierTwoPort'],2)

class PartPictureTransconductanceAmplifierFourPort(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[1,2,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # plus and minus signs on the sensing port
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,1.5)
        # arrow on the output port
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,2.5)
        # draw remainder of amplifier
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureTransconductanceAmplifierFourPortAlt(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[1,2,4,3],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # plus and minus signs on the sensing port
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,1.5)
        # arrow on the output port
        PartPicture.DrawArrowDown(self,canvas,grid,drawingOrigin,2.5)
        # draw remainder of amplifier
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureTransconductanceAmplifierFourPortAlt2(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[2,1,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # plus and minus signs on the sensing port
        PartPicture.DrawMinusPlus(self,canvas,grid,drawingOrigin,1.5)
        # arrow on the output port
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,2.5)
        # draw remainder of amplifier
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureTransconductanceAmplifierFourPortAlt3(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[2,1,4,3],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # plus and minus signs on the sensing port
        PartPicture.DrawMinusPlus(self,canvas,grid,drawingOrigin,1.5)
        # arrow on the output port
        PartPicture.DrawArrowDown(self,canvas,grid,drawingOrigin,2.5)
        # draw remainder of amplifier
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableTransconductanceAmplifierFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureTransconductanceAmplifierFourPort','PartPictureTransconductanceAmplifierFourPortAlt','PartPictureTransconductanceAmplifierFourPortAlt2','PartPictureTransconductanceAmplifierFourPortAlt3'],4)

class PartPictureCurrentControlledVoltageSourceFourPort(PartPictureDependent):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureDependent.__init__(self,origin,[1,2,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sensing port
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,1)
        # plus and minus signs inside the voltage source
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,3)
        PartPictureDependent.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureCurrentControlledVoltageSourceFourPortAlt(PartPictureDependent):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureDependent.__init__(self,origin,[2,1,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sensing port
        PartPicture.DrawArrowDown(self,canvas,grid,drawingOrigin,1)
        # plus and minus signs inside the voltage source
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,3)
        PartPictureDependent.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableCurrentControlledVoltageSourceFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentControlledVoltageSourceFourPort','PartPictureCurrentControlledVoltageSourceFourPortAlt'],4)

class PartPictureTransresistanceAmplifierTwoPort(PartPictureAmpTwoPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpTwoPort.__init__(self,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # draw short arrow to the right for the input
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        lx=(drawingOrigin[0]+self.origin[0]+0+1.25)*grid
        rx=(drawingOrigin[0]+self.origin[0]+0+2.75)*grid
        my=(drawingOrigin[1]+self.origin[1]+0+2)*grid
        p=[ct.Translate((lx,my)),ct.Translate((rx,my))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,arrow='last',arrowshape=((8*grid)/20,(10*grid)/20,(3*grid)/20))
        # draw a plus sign at the output
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        px=(drawingOrigin[0]+self.origin[0]+3.25)*grid
        py=(drawingOrigin[1]+self.origin[1]+2)*grid
        pw=3*grid/16
        p=[[ct.Translate((px-pw,py)),ct.Translate((px+pw,py))],
           [ct.Translate((px,py-pw)),ct.Translate((px,py+pw))],]
        canvas.create_line(p[0][0][0],p[0][0][1],p[0][1][0],p[0][1][1],fill=self.color)
        canvas.create_line(p[1][0][0],p[1][0][1],p[1][1][0],p[1][1][1],fill=self.color)
        PartPictureAmpTwoPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableTransresistanceAmplifierTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureTransresistanceAmplifierTwoPort'],2)

class PartPictureTransresistanceAmplifierFourPort(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[1,2,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sense port
        PartPicture.DrawArrowDown(self,canvas,grid,drawingOrigin,1.5)
        # plus and minus signs on the output port
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,2.5)
        # draw remainder of amplifier
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureTransresistanceAmplifierFourPortAlt(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[1,2,4,3],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sense port
        PartPicture.DrawArrowDown(self,canvas,grid,drawingOrigin,1.5)
        # plus and minus signs on the output port
        PartPicture.DrawMinusPlus(self,canvas,grid,drawingOrigin,2.5)
        # put the connector lines from the edge of the amp to the pins
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureTransresistanceAmplifierFourPortAlt2(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[2,1,3,4],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sense port
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,1.5)
        # plus and minus signs on the output port
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,2.5)
        # put the connector lines from the edge of the amp to the pins
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureTransresistanceAmplifierFourPortAlt3(PartPictureAmpFourPort):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureAmpFourPort.__init__(self,origin,[2,1,4,3],orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sense port
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,1.5)
        # plus and minus signs on the output port
        PartPicture.DrawMinusPlus(self,canvas,grid,drawingOrigin,2.5)
        # put the connector lines from the edge of the amp to the pins
        PartPictureAmpFourPort.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableTransresistanceAmplifierFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureTransresistanceAmplifierFourPort','PartPictureTransresistanceAmplifierFourPortAlt','PartPictureTransresistanceAmplifierFourPortAlt2','PartPictureTransresistanceAmplifierFourPortAlt3'],4)

class PartPictureTransmissionLineTwoPort(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(0,1),'l',False,True,False),PartPin(2,(4,1),'r',False,True,False)],[(1.0,0.5),(3.0,1.5)],[(0,0),(4,2)],(2,0),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        self.DrawTransmissionLine(canvas,grid,drawingOrigin)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableTransmissionLineTwoPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureTransmissionLineTwoPort'],2)

class PartPictureTransmissionLineFourPort(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(0,1),'l',False,True,True,'tl'),
                                          PartPin(3,(0,2),'l',False,True,True,'bl'),
                                          PartPin(2,(4,1),'r',False,True,True,'tr'),
                                          PartPin(4,(4,2),'r',False,True,True,'br')],
                                          [(1.0,0.5),(3.0,1.5)],[(0,0),(4,3)],(2,0),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        self.DrawTransmissionLine(canvas,grid,drawingOrigin)
        # the lines connecting the bottom pins
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        my=(drawingOrigin[1]+self.origin[1]+1)*grid
        lx=(drawingOrigin[0]+self.origin[0]+1)*grid
        rx=(drawingOrigin[0]+self.origin[0]+3)*grid
        by=(drawingOrigin[1]+self.origin[1]+2)*grid
        p=[ct.Translate((lx,my+grid/2)),ct.Translate((lx,by))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color)
        p=[ct.Translate((rx-grid/4,my+grid/2)),ct.Translate((rx-grid/4,by)),ct.Translate((rx,by))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],p[2][0],p[2][1],fill=self.color)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableTransmissionLineFourPort(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureTransmissionLineFourPort'],4)

class PartPictureTransmissionLineDifferential(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,
                             [PartPin(1,(0,1),'l',False,True,True,'tl'),
                              PartPin(2,(0,2),'l',False,True,True,'bl'),
                              PartPin(3,(4,1),'r',False,True,True,'tr'),
                              PartPin(4,(4,2),'r',False,True,True,'br')],
                             [(1.0,0.5),(3.0,2.5)],[(0,0),(4,3)],(2,0),orientation,mirroredHorizontally,mirroredVertically,(2,1))
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        self.DrawDifferentialTransmissionLine(canvas,grid,drawingOrigin)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableTransmissionLineDifferential(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureTransmissionLineDifferential'],4)

class PartPictureStim(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(2,(0,1),'l',False,True,False),PartPin(1,(2,1),'r',False,True,False)],[(0.25,0.75),(1.75,1.25)],[(0,0),(2,2)],(1,0),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # the arrow
        ct=self.CoordinateTranslater(grid,drawingOrigin)
        lx=(drawingOrigin[0]+self.origin[0]+0)*grid
        rx=(drawingOrigin[0]+self.origin[0]+2)*grid
        my=(drawingOrigin[1]+self.origin[1]+1)*grid
        p=[ct.Translate((lx,my)),ct.Translate((rx,my))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,arrow='last',arrowshape=((8*grid)/10,(10*grid)/10,(3*grid)/10))
        if not connected is None:
            for pinIndex in range(len(self.pinList)):
                pin = self.pinList[pinIndex]
                if pin['Number'] == 2:
                    connected[pinIndex]=True
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)

class PartPictureVariableStim(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureStim'],2)

class PartPictureUnknown(PartPictureSpecifiedPorts):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureSpecifiedPorts.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        self.DrawCharacterInMiddle(canvas,grid,drawingOrigin,'?')
        PartPictureSpecifiedPorts.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureUnknownAcross(PartPictureSpecifiedPortsAcross):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureSpecifiedPortsAcross.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        self.DrawCharacterInMiddle(canvas,grid,drawingOrigin,'?')
        PartPictureSpecifiedPortsAcross.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureUnknownDownAndUp(PartPictureSpecifiedPortsDownAndUp):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureSpecifiedPortsDownAndUp.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        self.DrawCharacterInMiddle(canvas,grid,drawingOrigin,'?')
        PartPictureSpecifiedPortsDownAndUp.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureUnknownSide(PartPictureSpecifiedPortsSide):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureSpecifiedPortsSide.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        self.DrawCharacterInMiddle(canvas,grid,drawingOrigin,'?')
        PartPictureSpecifiedPortsSide.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableUnknown(PartPictureVariable):
    def __init__(self,ports=4):
        PartPictureVariable.__init__(self,['PartPictureUnknown','PartPictureUnknownAcross','PartPictureUnknownDownAndUp','PartPictureUnknownSide'],ports)

class PartPictureSystem(PartPictureSpecifiedPorts):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureSpecifiedPorts.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        self.DrawCharacterInMiddle(canvas,grid,drawingOrigin,'S')
        PartPictureSpecifiedPorts.DrawDevice(self,canvas,grid,drawingOrigin,None if connected is None else [True for ele in connected])

class PartPictureSystemAcross(PartPictureSpecifiedPortsAcross):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureSpecifiedPortsAcross.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        self.DrawCharacterInMiddle(canvas,grid,drawingOrigin,'S')
        PartPictureSpecifiedPortsAcross.DrawDevice(self,canvas,grid,drawingOrigin,None if connected is None else [True for ele in connected])

class PartPictureSystemDownAndUp(PartPictureSpecifiedPortsDownAndUp):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureSpecifiedPortsDownAndUp.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        self.DrawCharacterInMiddle(canvas,grid,drawingOrigin,'S')
        PartPictureSpecifiedPortsDownAndUp.DrawDevice(self,canvas,grid,drawingOrigin,None if connected is None else [True for ele in connected])

class PartPictureSystemSide(PartPictureSpecifiedPortsSide):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureSpecifiedPortsSide.__init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        self.DrawCharacterInMiddle(canvas,grid,drawingOrigin,'S')
        PartPictureSpecifiedPortsSide.DrawDevice(self,canvas,grid,drawingOrigin,None if connected is None else [True for ele in connected])

class PartPictureVoltageProbe(PartPictureBox):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(1,4),'b',False,True,True),PartPin(2,(1,0),'t',False,True,True)],[(0.5,1),(1.5,3)],[(0.5,0),(1.5,4)],(0,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sensing port
        PartPicture.DrawPlusMinus(self,canvas,grid,drawingOrigin,1)
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin,connected)

class PartPictureVariableSystem(PartPictureVariable):
    def __init__(self,ports=4):
        PartPictureVariable.__init__(self,['PartPictureSystem','PartPictureSystemAcross','PartPictureSystemDownAndUp','PartPictureSystemSide'],ports)

class PartPictureVariableVoltageProbe(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureVoltageProbe'],2)

class PartPictureCurrentProbe(PartPictureBox):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPictureBox.__init__(self,origin,[PartPin(1,(1,4),'b',False,True,True),PartPin(2,(1,0),'t',False,True,True)],[(0.5,1),(1.5,3)],[(0.5,0),(1.5,4)],(0,2),orientation,mirroredHorizontally,mirroredVertically)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # arrow on the sensing port
        PartPicture.DrawArrowUp(self,canvas,grid,drawingOrigin,1)
        PartPictureBox.DrawDevice(self,canvas,grid,drawingOrigin,connected)
        
class PartPictureVariableCurrentProbe(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureCurrentProbe'],2)

class PartPictureTransistor(PartPicture):
    def __init__(self,ports,origin,orientation,mirroredHorizontally,mirroredVertically):
        PartPicture.__init__(self,origin,[PartPin(1,(0,2),'l',False,True,True),
                                          PartPin(2,(2,0),'t',False,True,True),
                                          PartPin(3,(2,4),'b',False,True,True)],
            [(1,1),(3,3)],[(0,0),(3,4)],(3.25,2),orientation,mirroredHorizontally,mirroredVertically,(2,2))
    def DrawLine(self,coordinateList,canvas,grid,drawingOrigin):
        ct=self.CoordinateTranslater(grid, drawingOrigin)
        p=[ct.Translate(((drawingOrigin[0]+self.origin[0]+i[0])*grid,(drawingOrigin[1]+self.origin[1]+i[1])*grid))
           for i in coordinateList]
        for k in range(len(p)-1):
            canvas.create_line(p[k][0],p[k][1],p[k+1][0],p[k+1][1],fill=self.color)
    def DrawDevice(self,canvas,grid,drawingOrigin,connected=None):
        # draw the circle
        ct=self.CoordinateTranslater(grid, drawingOrigin)
        xi=(drawingOrigin[0]+self.origin[0]+1)*grid
        xf=(drawingOrigin[0]+self.origin[0]+3)*grid
        yi=(drawingOrigin[1]+self.origin[1]+1)*grid
        yf=(drawingOrigin[1]+self.origin[1]+3)*grid
        p=[ct.Translate((xi,yi)),ct.Translate((xf,yf))]
        canvas.create_oval(p[0][0],p[0][1],p[1][0],p[1][1],outline=self.color)
        # draw the connection to the collector
        self.DrawLine([(2,1),(2,1.25),(1.5,1.75)],canvas,grid,drawingOrigin)
        # draw the connection to the emiiter
        self.DrawLine([(2,3),(2,2.75)],canvas,grid,drawingOrigin)
        # draw emitter arrow
        ct=self.CoordinateTranslater(grid, drawingOrigin)
        p=[ct.Translate(((drawingOrigin[0]+self.origin[0]+1.5)*grid,(drawingOrigin[1]+self.origin[1]+2.25)*grid)),
           ct.Translate(((drawingOrigin[0]+self.origin[0]+2)*grid,(drawingOrigin[1]+self.origin[1]+2.75)*grid))]
        canvas.create_line(p[0][0],p[0][1],p[1][0],p[1][1],fill=self.color,arrow='last',arrowshape=((8*grid)/20,(10*grid)/20,(3*grid)/20))
        # draw the connection to the base
        self.DrawLine([(1,2),(1.5,2)],canvas,grid,drawingOrigin)
        # draw the line through the transistor
        self.DrawLine([(1.5,1.25),(1.5,2.75)],canvas,grid,drawingOrigin)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin,False,connected)
class PartPictureVariableNPNTransister(PartPictureVariable):
    def __init__(self):
        PartPictureVariable.__init__(self,['PartPictureTransistor'],2)


