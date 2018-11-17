"""
CalculationProperties.py
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

import sys
if sys.version_info.major < 3:
    from Tkinter import Frame,Label,Entry,StringVar,Toplevel,PhotoImage
    from Tkinter import TOP,YES,NO,X,LEFT
    import xml.etree.ElementTree as et
    import tkMessageBox
else:
    from tkinter import Frame,Label,Entry,StringVar,Toplevel,PhotoImage
    from tkinter import TOP,YES,NO,X,LEFT
    import xml.etree.ElementTree as et
    from tkinter import messagebox

from SignalIntegrity.App.PlotWindow import *
from SignalIntegrity.App.ToSI import *
from SignalIntegrity.App.PartProperty import *

# This is the legacy calculation properties to be removed eventually

class CalculationProperties(object):
    def __init__(self,parent,endFrequency=20e9,frequencyPoints=400,userSampleRate=40e9):
        self.parent=parent
        self.schematic=parent.Drawing.schematic
        self.endFrequency=endFrequency
        self.frequencyPoints=frequencyPoints
        self.userSampleRate=userSampleRate
        self.CalculateOthersFromBaseInformation()
    def CalculateOthersFromBaseInformation(self):
        self.baseSampleRate=self.endFrequency*2
        self.timePoints=self.frequencyPoints*2
        self.frequencyResolution=self.endFrequency/self.frequencyPoints
        self.impulseLength=1./self.frequencyResolution
    def InitFromXml(self,calculationPropertiesElement,parent):
        endFrequency=20e9
        frequencyPoints=400
        userSampleRate=40e9
        for calculationProperty in calculationPropertiesElement:
            if calculationProperty.tag == 'end_frequency':
                endFrequency=float(calculationProperty.text)
            elif calculationProperty.tag == 'frequency_points':
                frequencyPoints=int(calculationProperty.text)
            elif calculationProperty.tag == 'user_samplerate':
                userSampleRate = float(calculationProperty.text)
        self.__init__(parent,endFrequency,frequencyPoints,userSampleRate)
