"""
PartPin.py
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
import xml.etree.ElementTree as et
from SignalIntegrity.App.ProjectFile import PartPinConfiguration
# pinOrientation is 't','b','l','r'
# coordinates are relative to part
class PartPin(PartPinConfiguration):
    def __init__(self,pinNumber,pinConnectPoint,pinOrientation,pinNumberVisible=True,pinVisible=True, pinNumberingMatters=True):
        PartPinConfiguration.__init__(self)
        self.SetValue('Number', pinNumber)
        self.SetValue('ConnectionPoint', str(pinConnectPoint))
        self.SetValue('Orientation', pinOrientation)
        self.SetValue('NumberVisible', pinNumberVisible)
        self.SetValue('Visible', pinVisible)
        self.SetValue('NumberingMatters', pinNumberingMatters)
    def DrawPin(self,canvas,grid,partOrigin,color,connected):
        pinConnectionPoint=eval(self.GetValue('ConnectionPoint'))
        startx=(pinConnectionPoint[0]+partOrigin[0])*grid
        starty=(pinConnectionPoint[1]+partOrigin[1])*grid
        endx=startx
        endy=starty
        textGrid=16
        pinOrientation=self.GetValue('Orientation')
        if pinOrientation == 't':
            endy=endy+grid
            textx=startx+textGrid/2
            texty=starty+textGrid/2
        elif pinOrientation == 'b':
            endy=endy-grid
            textx=startx+textGrid/2
            texty=starty-textGrid/2
        elif pinOrientation == 'l':
            endx=endx+grid
            textx=startx+textGrid/2
            texty=starty-textGrid/2
        elif pinOrientation =='r':
            endx=endx-grid
            textx=startx-textGrid/2
            texty=starty-textGrid/2
        if self.GetValue('Visible'):
            canvas.create_line(startx,starty,endx,endy,fill=color)
        if not connected:
            size=max(1,grid/8)
            canvas.create_line(startx-size,starty-size,startx+size,starty+size,fill='red',width=2)
            canvas.create_line(startx+size,starty-size,startx-size,starty+size,fill='red',width=2)
        # comment this in for editing book
        #if self.pinNumberingMatters:
        #    self.pinNumberVisible=True
        if self.GetValue('NumberVisible'):
            canvas.create_text(textx,texty,text=str(self.GetValue('Number')),fill=color)
