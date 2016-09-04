'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
import xml.etree.ElementTree as et

# pinOrientation is 't','b','l','r'
# coordinates are relative to part
class PartPin(object):
    def __init__(self,pinNumber,pinConnectPoint,pinOrientation,pinNumberVisible=True,pinVisible=True, pinNumberingMatters=True):
        self.pinNumber=pinNumber
        self.pinConnectionPoint=pinConnectPoint
        self.pinOrientation=pinOrientation
        self.pinNumberVisible = pinNumberVisible
        self.pinVisible = pinVisible
        self.pinNumberingMatters = pinNumberingMatters
    def DrawPin(self,canvas,grid,partOrigin,color,connected):
        startx=(self.pinConnectionPoint[0]+partOrigin[0])*grid
        starty=(self.pinConnectionPoint[1]+partOrigin[1])*grid
        endx=startx
        endy=starty
        textGrid=16
        if self.pinOrientation == 't':
            endy=endy+grid
            textx=startx+textGrid/2
            texty=starty+textGrid/2
        elif self.pinOrientation == 'b':
            endy=endy-grid
            textx=startx+textGrid/2
            texty=starty-textGrid/2
        elif self.pinOrientation == 'l':
            endx=endx+grid
            textx=startx+textGrid/2
            texty=starty-textGrid/2
        elif self.pinOrientation =='r':
            endx=endx-grid
            textx=startx-textGrid/2
            texty=starty-textGrid/2
        if self.pinVisible:
            canvas.create_line(startx,starty,endx,endy,fill=color)
        if not connected:
            size=max(1,grid/8)
            canvas.create_line(startx-size,starty-size,startx+size,starty+size,fill='red',width=2)
            canvas.create_line(startx+size,starty-size,startx-size,starty+size,fill='red',width=2)
        # comment this in for editing book
        #if self.pinNumberingMatters:
        #    self.pinNumberVisible=True
        if self.pinNumberVisible:
            canvas.create_text(textx,texty,text=str(self.pinNumber),fill=color)
    def xml(self):
        pp = et.Element('pin')
        pList=[]
        p=et.Element('number')
        p.text=str(self.pinNumber)
        pList.append(p)
        p=et.Element('connection_point')
        p.text=str(self.pinConnectionPoint)
        pList.append(p)
        p=et.Element('orientation')
        p.text=str(self.pinOrientation)
        pList.append(p)
        p=et.Element('number_visible')
        p.text=str(self.pinNumberVisible)
        pList.append(p)
        p=et.Element('pin_visible')
        p.text=str(self.pinVisible)
        pList.append(p)
        pp.extend(pList)
        return pp

class PartPinXMLClassFactory(PartPin):
    def __init__(self,xml):
        pinNumber=None
        pinConnectionPoint=None
        pinOrientation=None
        pinNumberVisible = True
        for item in xml:
            if item.tag == 'number':
                pinNumber = int(item.text)
            elif item.tag == 'connection_point':
                pinConnectionPoint = eval(item.text)
            elif item.tag == 'orientation':
                pinOrientation = item.text
            elif item.tag == 'number_visible':
                pinNumberVisible = eval(item.text)
            elif item.tag == 'pin_visible':
                pinVisible = eval(item.text)
        self.result=PartPin(pinNumber,pinConnectionPoint,pinOrientation,pinNumberVisible,pinVisible)