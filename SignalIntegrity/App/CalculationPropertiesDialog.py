"""
CalculationPropertiesDialog.py
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

from SignalIntegrity.App.CalculationPropertiesProject import PropertiesDialog,CalculationPropertySI,CalculationProperty,CalculationPropertyChoices
from SignalIntegrity.App.ToSI import nextHigher12458
import SignalIntegrity.App.Project
import SignalIntegrity.App.Preferences

import sys
if sys.version_info.major < 3:
    import Tkinter as tk
else:
    import tkinter as tk

class CalculationPropertiesDialog(PropertiesDialog):
    def __init__(self,parent):
        PropertiesDialog.__init__(self,parent,SignalIntegrity.App.Project['CalculationProperties'],parent,'Calculation Properties')
        self.transient(parent)
        self.endFrequency=CalculationPropertySI(self.propertyListFrame,'End Frequency',self.onendFrequencyEntered,None,self.project,'EndFrequency','Hz')
        self.frequencyPoints=CalculationProperty(self.propertyListFrame,'Frequency Points',self.onfrequencyPointsEntered,None,self.project,'FrequencyPoints')
        self.frequencyResolution=CalculationPropertySI(self.propertyListFrame,'Frequency Resolution',self.onfrequencyResolutionEntered,None,self.project,'FrequencyResolution','Hz')
        self.userSampleRate=CalculationPropertySI(self.propertyListFrame,'User Sample Rate',self.onuserSampleRateEntered,None,self.project,'UserSampleRate','S/s')
        self.userSamplePeriod=CalculationPropertySI(self.propertyListFrame,'User Sample Period',self.onuserSamplePeriodEntered,None,self.project,'UserSamplePeriod','s')
        self.baseSampleRate=CalculationPropertySI(self.propertyListFrame,'Base Sample Rate',self.onbaseSampleRateEntered,None,self.project,'BaseSampleRate','S/s')
        self.baseSamplePeriod=CalculationPropertySI(self.propertyListFrame,'Base Sample Period',self.onbaseSamplePeriodEntered,None,self.project,'BaseSamplePeriod','s')
        self.timePoints=CalculationProperty(self.propertyListFrame,'Time Points',self.ontimePointsEntered,None,self.project,'TimePoints')
        self.impulseResponseLength=CalculationPropertySI(self.propertyListFrame,'Impulse Response Length',self.onimpulseLengthEntered,None,self.project,'ImpulseResponseLength','s')
        self.underlyingType=CalculationPropertyChoices(self.propertyListFrame,'Frequency List Type',self.onunderlyingTypeEntered,None,[('Linear','Linear'),('Logarithmic','Logarithmic')],self.project,'UnderlyingType')
        self.logarithmicFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        showLogarithmic = self.project['UnderlyingType'] == 'Logarithmic'
        if showLogarithmic: self.logarithmicFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.logarithmicStartFrequency = CalculationPropertySI(self.logarithmicFrame,'Logarithmic Start Frequency',None,None,self.project,'LogarithmicStartFrequency','Hz')
        self.logarithmicEndFrequency = CalculationPropertySI(self.logarithmicFrame,'Logarithmic End Frequency',None,None,self.project,'LogarithmicEndFrequency','Hz')
        self.logarithmicPointsPerDecade = CalculationProperty(self.logarithmicFrame,'Logarithmic Points Per Decade',None,None,self.project,'LogarithmicPointsPerDecade')
        PropertiesDialog.bind(self,'<Return>',self.ok)
        PropertiesDialog.bind(self,'<Escape>',self.cancel)
        PropertiesDialog.protocol(self,"WM_DELETE_WINDOW", self.onClosing)
        self.attributes('-topmost',True)
        self.Save()
        self.Finish()

    def NextHigher12458(self,x):
        """helper function that allows turning this off, depending on preferences"""
        if SignalIntegrity.App.Preferences['Calculation.Enforce12458']:
            return nextHigher12458(x)
        else:
            return x

    def onendFrequencyEntered(self,event):
        self.project['EndFrequency']=self.NextHigher12458(self.project['EndFrequency'])
        self.project['FrequencyPoints']=int(self.NextHigher12458(self.project['EndFrequency']/self.project['FrequencyResolution']))
        self.project['FrequencyPoints']=max(1,self.project['FrequencyPoints'])
        self.UpdateStrings()

    def onfrequencyPointsEntered(self,event):
        self.project['FrequencyPoints']=max(1,self.project['FrequencyPoints'])
        self.UpdateStrings()

    def onfrequencyResolutionEntered(self,event):
        self.project['FrequencyPoints']=int(self.NextHigher12458(self.project['EndFrequency']/self.project['FrequencyResolution']))
        self.project['FrequencyPoints']=max(1,self.project['FrequencyPoints'])
        self.UpdateStrings()

    def onuserSampleRateEntered(self,event):
        self.project['UserSampleRate']=self.NextHigher12458(self.project['UserSampleRate'])
        self.UpdateStrings()

    def onuserSamplePeriodEntered(self,event):
        self.project['UserSampleRate']=self.NextHigher12458(1./self.project['UserSamplePeriod'])
        self.UpdateStrings()

    def onbaseSampleRateEntered(self,event):
        self.project['EndFrequency']=self.NextHigher12458(self.project['BaseSampleRate'])/2.
        self.project['FrequencyPoints']=int(self.NextHigher12458(self.project['EndFrequency']/self.project['FrequencyResolution']))
        self.project['FrequencyPoints']=max(1,self.project['FrequencyPoints'])
        self.UpdateStrings()

    def onbaseSamplePeriodEntered(self,event):
        self.project['EndFrequency']=self.NextHigher12458(1./self.project['BaseSamplePeriod'])/2.
        self.project['FrequencyPoints']=int(self.NextHigher12458(self.project['EndFrequency']/self.project['FrequencyResolution']))
        self.project['FrequencyPoints']=max(1,self.project['FrequencyPoints'])
        self.UpdateStrings()

    def ontimePointsEntered(self,event):
        self.project['FrequencyPoints']=int(self.NextHigher12458(self.project['TimePoints']/2))
        self.project['FrequencyPoints']=max(1,self.project['FrequencyPoints'])
        self.UpdateStrings()

    def onimpulseLengthEntered(self,event):
        self.project['TimePoints']=int(self.project['ImpulseResponseLength']*self.project['BaseSampleRate']+0.5)
        self.project['FrequencyPoints']=int(self.NextHigher12458(self.project['TimePoints']/2))
        self.project['FrequencyPoints']=max(1,self.project['FrequencyPoints'])
        self.UpdateStrings()

    def onunderlyingTypeEntered(self,event):
        self.UpdateStrings()

    def UpdateStrings(self):
        self.project.CalculateOthersFromBaseInformation()
        self.endFrequency.UpdateStrings()
        self.frequencyPoints.UpdateStrings()
        self.frequencyResolution.UpdateStrings()
        self.userSampleRate.UpdateStrings()
        self.userSamplePeriod.UpdateStrings()
        self.baseSampleRate.UpdateStrings()
        self.baseSamplePeriod.UpdateStrings()
        self.timePoints.UpdateStrings()
        self.impulseResponseLength.UpdateStrings()
        showLogarithmic = self.project['UnderlyingType'] == 'Logarithmic'
        self.logarithmicFrame.pack_forget()
        if showLogarithmic:
            self.logarithmicFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)

    def onClosing(self):
        self.ok(None)

    def ok(self,event):
        self.parent.statusbar.set('Calculation Properties Modified')
        self.parent.history.Event('modify calculation properties')
        PropertiesDialog.destroy(self)

    def cancel(self,event):
        self.Restore()
        PropertiesDialog.destroy(self)

    def Save(self):
        self.saved={'EndFrequency':self.project['EndFrequency'],
                    'FrequencyPoints':self.project['FrequencyPoints'],
                    'UserSampleRate':self.project['UserSampleRate']}

    def Restore(self):
        for key in self.saved:
            self.project[key]=self.saved[key]
        self.project.CalculateOthersFromBaseInformation()

