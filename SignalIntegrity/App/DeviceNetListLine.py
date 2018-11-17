"""
DeviceNetListLine.py
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

from ProjectFile import DeviceNetListConfiguration,DeviceNetListKeywordConfiguration

class DeviceNetListLine(DeviceNetListConfiguration):
    def __init__(self,devicename=None,partname=None,showReference=True,showports=True,values=None):
        DeviceNetListConfiguration.__init__(self)
        if devicename is None:
            self.SetValue('DeviceName','device')
        else:
            self.SetValue('DeviceName',devicename)
        self.SetValue('PartName',partname)
        self.SetValue('ShowReference',showReference)
        self.SetValue('ShowPorts',showports)
        if not values is None:
            self.SetValue('Values',[DeviceNetListKeywordConfiguration() for _ in range(len(values))])
            for vi in range(len(values)):
                (kw,show)=values[vi]
                self.GetValue('Values')[vi].SetValue('Keyword',kw)
                self.GetValue('Values')[vi].SetValue('ShowKeyword',show)
    def NetListLine(self,device):
        returnstring=self.GetValue('DeviceName')
        if self.GetValue('ShowReference'):
            if not returnstring=='':
                returnstring=returnstring+' '
            returnstring=returnstring+device['ref'].PropertyString(stype='raw')
        if self.GetValue('ShowPorts'):
            if not returnstring=='':
                returnstring=returnstring+' '
            returnstring=returnstring+device['ports'].PropertyString(stype='raw')
        if not self.GetValue('PartName') is None:
            if not returnstring=='':
                returnstring=returnstring+' '
            returnstring=returnstring+self.GetValue('PartName')
        for kwc in self.GetValue('Values'):
            if not returnstring=='':
                returnstring=returnstring+' '
            if kwc.GetValue('ShowKeyword'):
                returnstring=returnstring+kwc.GetValue('Keyword')+' '
            valueString=device[kwc.GetValue('Keyword')].PropertyString(stype='raw')
            if valueString is None:
                valueString='None'
            returnstring=returnstring+valueString
        return returnstring
