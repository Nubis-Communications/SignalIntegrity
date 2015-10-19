'''
Created on Oct 15, 2015

@author: peterp
'''
import xml.etree.ElementTree as et

# pinOrientation is 't','b','l','r'
# coordinates are relative to part
class PartPin(object):
    def __init__(self,pinNumber,pinConnectPoint,pinOrientation,pinVisible=True,pinNumberVisible=True):
        self.pinNumber=pinNumber
        self.pinConnectionPoint=pinConnectPoint
        self.pinOrientation=pinOrientation
        self.pinVisible = pinVisible
        self.pinNumberVisible = pinNumberVisible
    def DrawPin(self,canvas,grid,partOrigin):
        if self.pinVisible:
            startx=(self.pinConnectionPoint[0]+partOrigin[0])*grid
            starty=(self.pinConnectionPoint[1]+partOrigin[1])*grid
            endx=startx
            endy=starty
            if self.pinOrientation == 't':
                endy=endy+grid
                textx=startx+grid/2
                texty=starty+grid/2
            elif self.pinOrientation == 'b':
                endy=endy-grid
                textx=startx+grid/2
                texty=starty-grid/2
            elif self.pinOrientation == 'l':
                endx=endx+grid
                textx=startx+grid/2
                texty=starty-grid/2
            elif self.pinOrientation =='r':
                endx=endx-grid
                textx=startx-grid/2
                texty=starty-grid/2
            canvas.create_line(startx,starty,endx,endy)
            if self.pinNumberVisible:
                canvas.create_text(textx,texty,text=str(self.pinNumber))
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
        p=et.Element('visible')
        p.text=str(self.pinVisible)
        pList.append(p)
        p=et.Element('number_visible')
        p.text=str(self.pinNumberVisible)
        pList.append(p)
        pp.extend(pList)
        return pp

class PartPinXMLClassFactory(PartPin):
    def __init__(self,xml):
        pinNumber=None
        pinConnectionPoint=None
        pinOrientation=None
        pinVisible = True
        pinNumberVisible = True
        for item in xml:
            if item.tag == 'number':
                pinNumber = int(item.text)
            elif item.tag == 'connection_point':
                pinConnectionPoint = eval(item.text)
            elif item.tag == 'orientation':
                pinOrientation = item.text
            elif item.tag == 'visible':
                pinVisible = eval(item.text)
            elif item.tag == 'number_visible':
                pinNumberVisible = eval(item.text)
        self.result=PartPin(pinNumber,pinConnectionPoint,pinOrientation,pinVisible,pinNumberVisible)
        
        
