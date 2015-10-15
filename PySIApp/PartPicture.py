'''
Created on Oct 15, 2015

@author: peterp
'''
from PartPin import *

class PartPicture(object):
    def __init__(self,origin,pinList,innerBox,boundingBox):
        self.origin=origin
        self.pinList=pinList
        self.innerBox=innerBox
        self.boundingBox=boundingBox
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

class PartPictureBox(PartPicture):
    def __init__(self,origin,pinList,innerBox,boundingBox):
        PartPicture.__init__(self,origin,pinList,innerBox,boundingBox)
    def DrawDevice(self,canvas,grid,drawingOrigin):
        canvas.create_rectangle((drawingOrigin[0]+self.origin[0]+self.innerBox[0][0])*grid,
                                (drawingOrigin[1]+self.origin[1]+self.innerBox[0][1])*grid,
                                (drawingOrigin[0]+self.origin[0]+self.innerBox[1][0])*grid,
                                (drawingOrigin[1]+self.origin[1]+self.innerBox[1][1])*grid)
        PartPicture.DrawDevice(self,canvas,grid,drawingOrigin)

class PartPictureOnePort(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l')],[(1,0),(3,2)],[(0,0),(4,2)])

class PartPictureTwoPort(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(4,1),'r')],[(1,0),(3,2)],[(0,0),(4,2)])
        
class PartPictureThreePort(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l'),PartPin(3,(4,2),'r')],[(1,0),(3,4)],[(0,0),(4,4)])

class PartPictureFourPort(PartPictureBox):
    def __init__(self):
        PartPictureBox.__init__(self,(0,0),[PartPin(1,(0,1),'l'),PartPin(2,(0,3),'l'),PartPin(3,(4,1),'r'),PartPin(4,(4,3),'r')],[(1,0),(3,4)],[(0,0),(4,4)])

class PartPicturePort(PartPicture):
    def __init__(self,origin,pinNumber):
        PartPicture.__init__(self,origin,[PartPin(pinNumber,(3,1),'r')],[(1,1),(3,1)],[(0,0),(3,2)])
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

class PartPictureCapacitorTwoPort(PartPicture):
    def __init__(self):
        PartPicture.__init__(self,(0,0),[PartPin(1,(1,0),'t'),PartPin(2,(1,4),'b')],[(0,1),(2,3)],[(0,0),(2,4)])
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
