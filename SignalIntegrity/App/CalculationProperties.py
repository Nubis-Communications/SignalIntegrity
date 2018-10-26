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
from Tkinter import *
import xml.etree.ElementTree as et
import tkMessageBox

from PlotWindow import *
from ToSI import *
from PartProperty import *

class CalculationProperty(Frame):
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback):
        Frame.__init__(self,parentFrame)
        self.parentFrame=parentFrame
        self.enteredCallback=enteredCallback
        self.updateStringsCallback=updateStringsCallback
        self.pack(side=TOP,fill=X,expand=YES)
        self.string=StringVar()
        self.label = Label(self,width=30,text=textLabel+': ',anchor='e')
        self.label.pack(side=LEFT, expand=NO, fill=X)
        self.entry = Entry(self,textvariable=self.string)
        self.entry.config(width=15)
        self.entry.bind('<Return>',self.onEntered)
        self.entry.bind('<Tab>',self.onEntered)
        self.entry.bind('<Button-1>',self.onTouched)
        self.entry.bind('<Button-1>',self.onTouched)
        self.entry.bind('<Double-Button-1>',self.onCleared)
        self.entry.bind('<Button-3>',self.onUntouchedLoseFocus)
        self.entry.bind('<Escape>',self.onUntouchedLoseFocus)
        self.entry.bind('<FocusOut>',self.onUntouched)
        self.entry.pack(side=LEFT, expand=YES, fill=X)

    def SetString(self,value):
        self.string.set(value)
    def GetString(self):
        return self.string.get()
    def onEntered(self,event):
        self.enteredCallback(event)
        self.onUntouchedLoseFocus(event)
    def onTouched(self,event):
        self.updateStringsCallback()
    def onCleared(self,event):
        self.string.set('')
    def onUntouched(self,event):
        self.updateStringsCallback()
    def onUntouchedLoseFocus(self,event):
        self.parentFrame.focus()

class CalculationPropertiesDialog(Toplevel):
    def __init__(self, parent,calculationProperties):
        Toplevel.__init__(self, parent)
        self.parent=parent
        self.withdraw()
        self.title('CalculationProperties')
        img = PhotoImage(file=self.parent.installdir+'/icons/png/AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, img)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.calculationProperties=calculationProperties
        propertyListFrame = Frame(self)
        propertyListFrame.pack(side=TOP,fill=X,expand=NO)
        self.endFrequencyFrame=CalculationProperty(propertyListFrame,'end frequency',self.onendFrequencyEntered,self.updateStrings)
        self.frequencyPointsFrame=CalculationProperty(propertyListFrame,'frequency points',self.onfrequencyPointsEntered,self.updateStrings)
        self.frequencyResolutionFrame=CalculationProperty(propertyListFrame,'frequency resolution',self.onfrequencyResolutionEntered,self.updateStrings)
        self.userSampleRateFrame=CalculationProperty(propertyListFrame,'user sample rate',self.onuserSampleRateEntered,self.updateStrings)
        self.baseSampleRateFrame=CalculationProperty(propertyListFrame,'base sample rate',self.onbaseSampleRateEntered,self.updateStrings)
        self.timePointsFrame=CalculationProperty(propertyListFrame,'time points',self.ontimePointsEntered,self.updateStrings)
        self.impulseLengthFrame=CalculationProperty(propertyListFrame,'impulse response length',self.onimpulseLengthEntered,self.updateStrings)
        self.updateStrings()
        self.deiconify()
        (x,y)=(self.parent.root.winfo_x()+self.parent.root.winfo_width()/2-self.winfo_width()/2,
            self.parent.root.winfo_y()+self.parent.root.winfo_height()/2-self.winfo_height()/2)
        self.geometry("%+d%+d" % (x,y))
        
    def onendFrequencyEntered(self,event):
        self.calculationProperties.endFrequency=nextHigherInteger(FromSI(self.endFrequencyFrame.GetString(),'Hz'))
        self.calculationProperties.baseSampleRate=2.*self.calculationProperties.endFrequency
        self.calculationProperties.frequencyPoints=int(nextHigherInteger(self.calculationProperties.endFrequency/self.calculationProperties.frequencyResolution))
        self.calculationProperties.frequencyPoints=max(1,self.calculationProperties.frequencyPoints)
        self.calculationProperties.timePoints=self.calculationProperties.frequencyPoints*2
        self.calculationProperties.frequencyResolution=self.calculationProperties.endFrequency/self.calculationProperties.frequencyPoints
        self.calculationProperties.impulseLength=1./self.calculationProperties.frequencyResolution

    def onfrequencyPointsEntered(self,event):
        self.calculationProperties.frequencyPoints=int(nextHigherInteger(FromSI(self.frequencyPointsFrame.GetString(),'pts')))
        self.calculationProperties.frequencyPoints=max(1,self.calculationProperties.frequencyPoints)
        self.calculationProperties.timePoints=int(self.calculationProperties.frequencyPoints*2)
        self.calculationProperties.frequencyResolution=self.calculationProperties.endFrequency/self.calculationProperties.frequencyPoints
        self.calculationProperties.impulseLength=1./self.calculationProperties.frequencyResolution

    def onfrequencyResolutionEntered(self,event):
        self.calculationProperties.frequencyResolution=FromSI(self.frequencyResolutionFrame.GetString(),'Hz')
        self.calculationProperties.frequencyPoints=int(nextHigherInteger(self.calculationProperties.endFrequency/self.calculationProperties.frequencyResolution))
        self.calculationProperties.frequencyPoints=max(1,self.calculationProperties.frequencyPoints)
        self.calculationProperties.timePoints=self.calculationProperties.frequencyPoints*2
        self.calculationProperties.frequencyResolution=self.calculationProperties.endFrequency/self.calculationProperties.frequencyPoints
        self.calculationProperties.impulseLength=1./self.calculationProperties.frequencyResolution

    def onuserSampleRateEntered(self,event):
        self.calculationProperties.userSampleRate=nextHigherInteger(FromSI(self.userSampleRateFrame.GetString(),'S/s'))

    def onbaseSampleRateEntered(self,event):
        self.calculationProperties.baseSampleRate=FromSI(self.baseSampleRateFrame.GetString(),'S/s')
        self.calculationProperties.endFrequency=nextHigherInteger(self.calculationProperties.baseSampleRate/2.)
        self.calculationProperties.baseSampleRate=self.calculationProperties.endFrequency*2
        self.calculationProperties.frequencyPoints=int(nextHigherInteger(self.calculationProperties.endFrequency/self.calculationProperties.frequencyResolution))
        self.calculationProperties.frequencyPoints=max(1,self.calculationProperties.frequencyPoints)
        self.calculationProperties.timePoints=self.calculationProperties.frequencyPoints*2
        self.calculationProperties.frequencyResolution=self.calculationProperties.endFrequency/self.calculationProperties.frequencyPoints
        self.calculationProperties.impulseLength=1./self.calculationProperties.frequencyResolution

    def ontimePointsEntered(self,event):
        self.calculationProperties.timePoints=int(FromSI(self.timePointsFrame.GetString(),'pts'))
        self.calculationProperties.frequencyPoints=int(nextHigherInteger(self.calculationProperties.timePoints/2))
        self.calculationProperties.frequencyPoints=max(1,self.calculationProperties.frequencyPoints)
        self.calculationProperties.timePoints=self.calculationProperties.frequencyPoints*2
        self.calculationProperties.frequencyResolution=self.calculationProperties.endFrequency/self.calculationProperties.frequencyPoints
        self.calculationProperties.impulseLength=1./self.calculationProperties.frequencyResolution

    def onimpulseLengthEntered(self,event):
        self.calculationProperties.impulseLength=FromSI(self.impulseLengthFrame.GetString(),'s')
        self.calculationProperties.timePoints=self.calculationProperties.impulseLength*self.calculationProperties.baseSampleRate
        self.calculationProperties.frequencyPoints=int(nextHigherInteger(self.calculationProperties.timePoints/2.))
        self.calculationProperties.frequencyPoints=max(1,self.calculationProperties.frequencyPoints)
        self.calculationProperties.timePoints=self.calculationProperties.frequencyPoints*2
        self.calculationProperties.frequencyResolution=self.calculationProperties.endFrequency/self.calculationProperties.frequencyPoints
        self.calculationProperties.impulseLength=1./self.calculationProperties.frequencyResolution

    def onSimulate(self):
        self.calculationProperties.Simulate()

    def updateStrings(self):
        self.endFrequencyFrame.SetString(ToSI(self.calculationProperties.endFrequency,'Hz'))
        self.frequencyPointsFrame.SetString(ToSI(self.calculationProperties.frequencyPoints,'pts'))
        self.userSampleRateFrame.SetString(ToSI(self.calculationProperties.userSampleRate,'S/s'))
        self.baseSampleRateFrame.SetString(ToSI(self.calculationProperties.baseSampleRate,'S/s'))
        self.timePointsFrame.SetString(ToSI(self.calculationProperties.timePoints,'pts'))
        self.frequencyResolutionFrame.SetString(ToSI(self.calculationProperties.frequencyResolution,'Hz/pt'))
        self.impulseLengthFrame.SetString(ToSI(self.calculationProperties.impulseLength,'s'))

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
    def ShowCalculationPropertiesDialog(self):
        self.CalculationPropertiesDialog()
        #self.CalculationPropertiesDialog().state('normal')
        #self.CalculationPropertiesDialog().lift(self.parent)
    def CalculationPropertiesDialog(self):
        if not hasattr(self, 'calculationPropertiesDialog'):
            self.calculationPropertiesDialog = CalculationPropertiesDialog(self.parent,self)
        if self.calculationPropertiesDialog == None:
            self.calculationPropertiesDialog= CalculationPropertiesDialog(self.parent,self)
        else:
            if not self.calculationPropertiesDialog.winfo_exists():
                self.calculationPropertiesDialog=CalculationPropertiesDialog(self.parent,self)
        return self.calculationPropertiesDialog
    def xml(self):
        calculationPropertiesElement=et.Element('calculation_properties')
        calculationPropertiesElementList=[]
        calculationProperty=et.Element('end_frequency')
        calculationProperty.text=str(self.endFrequency)
        calculationPropertiesElementList.append(calculationProperty)
        calculationProperty=et.Element('frequency_points')
        calculationProperty.text=str(self.frequencyPoints)
        calculationPropertiesElementList.append(calculationProperty)
        calculationProperty=et.Element('user_samplerate')
        calculationProperty.text=str(self.userSampleRate)
        calculationPropertiesElementList.append(calculationProperty)
        calculationPropertiesElement.extend(calculationPropertiesElementList)
        return calculationPropertiesElement
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
        #self.PlotDialog().destroy()
    def OpenCalculationProperties(self):
        self.ShowCalculationPropertiesDialog()



