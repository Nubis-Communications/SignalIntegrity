'''
Created on Oct 15, 2015

@author: peterp
'''
# pinOrientation is 't','b','l','r'
# coordinates are relative to part
class PartPin(object):
    def __init__(self,pinNumber,pinConnectPoint,pinOrientation):
        self.pinNumber=pinNumber
        self.pinConnectionPoint=pinConnectPoint
        self.pinOrientation=pinOrientation
        self.pinVisible = True
        self.pinNumberVisible = True
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
