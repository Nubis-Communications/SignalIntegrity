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
from SignalIntegrity.App.ProjectFile import PartPinConfiguration
import SignalIntegrity.App.Project

# pinOrientation is 't','b','l','r'
# coordinates are relative to part
class PartPin(PartPinConfiguration):
    def __init__(self,pinNumber,pinConnectPoint,pinOrientation,pinNumberVisible=True,pinVisible=True, pinNumberingMatters=True, numberSide='n'):
        PartPinConfiguration.__init__(self)
        self['Number']=pinNumber
        self['ConnectionPoint']=str(pinConnectPoint)
        self['Orientation']=pinOrientation
        self['NumberVisible']=pinNumberVisible
        self['Visible']=pinVisible
        self['NumberingMatters']=pinNumberingMatters
        self['NumberSide']=numberSide
    def DrawPin(self,canvas,grid,partOrigin,color,connected):
        pinConnectionPoint=self['ConnectionPoint']
        startx=(pinConnectionPoint[0]+partOrigin[0])*grid
        starty=(pinConnectionPoint[1]+partOrigin[1])*grid
        endx=startx
        endy=starty
        textGrid=16
        pinOrientation=self['Orientation']
        numberSide=self['NumberSide']
        if pinOrientation == 't':
            anchorString='s'
            endy=endy+grid
            texty=starty+textGrid
            if numberSide in ['n','br','tl','rt','lb']:
                textx=startx+textGrid/2
            elif numberSide in ['nx']:
                textx=startx+textGrid/2
                texty=starty+textGrid/4
            else:
                textx=startx-textGrid/2
        elif pinOrientation == 'b':
            anchorString='n'
            endy=endy-grid
            texty=starty-textGrid
            if numberSide in ['n','bl','tr','rb','lt']:
                textx=startx+textGrid/2
            elif numberSide in ['nx']:
                textx=startx+textGrid/2
                texty=starty-textGrid/4
            else:
                textx=startx-textGrid/2
        elif pinOrientation == 'l':
            anchorString='e'
            endx=endx+grid
            textx=startx+textGrid*3/4
            if numberSide in ['n','tl','br','rt','lb']:
                texty=starty-textGrid/2
            elif numberSide in ['nx']:
                texty=starty-textGrid/2
                textx=startx-textGrid/4
            else:
                texty=starty+textGrid/2
        elif pinOrientation =='r':
            anchorString='w'
            endx=endx-grid
            textx=startx-textGrid*3/4
            if numberSide in ['n','tr','bl','rb','lt']:
                texty=starty-textGrid/2
            elif numberSide in ['nx']:
                texty=starty-textGrid/2
                textx=startx+textGrid/4
            else:
                texty=starty+textGrid/2
        if self['Visible']:
            canvas.create_line(startx,starty,endx,endy,fill=color)
        if not connected and not SignalIntegrity.App.Preferences['Appearance.AllPinNumbersVisible']:
            size=max(1,grid/8)
            canvas.create_line(startx-size,starty-size,startx+size,starty+size,fill='red',width=2)
            canvas.create_line(startx+size,starty-size,startx-size,starty+size,fill='red',width=2)
        # comment this in for editing book
        #if self.pinNumberingMatters:
        #    self.pinNumberVisible=True
        if self['NumberVisible'] or (self['NumberingMatters'] and SignalIntegrity.App.Preferences['Appearance.AllPinNumbersVisible']):
            canvas.create_text(textx,texty,text=str(self['Number']),anchor=anchorString,fill=color)
