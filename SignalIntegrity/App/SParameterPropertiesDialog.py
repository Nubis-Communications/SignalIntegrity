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
import sys
if sys.version_info.major < 3:
    import Tkinter as tk
else:
    import tkinter as tk

from SignalIntegrity.App.CalculationPropertiesProject import PropertiesDialog,CalculationPropertySI,CalculationProperty
from SignalIntegrity.App.ToSI import nextHigher12458
import SignalIntegrity.App.Project

class SParameterPropertiesDialog(PropertiesDialog):
    def __init__(self,parent,project):
        PropertiesDialog.__init__(self,parent,project,parent,'S-parameter Properties')
        self.inheritButton=tk.Button(self.propertyListFrame,text='Inherit Properties from Calculation Properties',command=self.onInherit)
        self.inheritButton.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.endFrequencyFrame=CalculationPropertySI(self.propertyListFrame,'End Frequency',self.onendFrequencyEntered,None,self.project,'EndFrequency','Hz')
        self.frequencyPointsFrame=CalculationProperty(self.propertyListFrame,'Frequency Points',self.onfrequencyPointsEntered,None,self.project,'FrequencyPoints')
        self.frequencyResolutionFrame=CalculationPropertySI(self.propertyListFrame,'Frequency Resolution',self.onfrequencyResolutionEntered,None,self.project,'FrequencyResolution','Hz')
        self.baseSampleRateFrame=CalculationPropertySI(self.propertyListFrame,'Base Sample Rate',self.onbaseSampleRateEntered,None,self.project,'BaseSampleRate','S/s')
        self.baseSamplePeriodFrame=CalculationPropertySI(self.propertyListFrame,'Base Sample Period',self.onbaseSamplePeriodEntered,None,self.project,'BaseSamplePeriod','s')
        self.timePointsFrame=CalculationProperty(self.propertyListFrame,'Time Points',self.ontimePointsEntered,None,self.project,'TimePoints')
        self.impulseResponseLengthFrame=CalculationPropertySI(self.propertyListFrame,'Impulse Response Length',self.onimpulseLengthEntered,None,self.project,'ImpulseResponseLength','s')  
        self.referenceImpedanceEntryFrame = tk.Frame(self,relief=tk.RIDGE, borderwidth=5)
        self.referenceImpedanceEntryFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.referenceImpedanceFrame=CalculationPropertySI(self.referenceImpedanceEntryFrame,'Reference Impedance',self.onReferenceImpedanceEntered,None,self.project,'ReferenceImpedance','Ohm')
        self.timeLimitsFrame = tk.Frame(self,relief=tk.RIDGE, borderwidth=5)
        self.timeLimitsFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.negativeTimeFrame=CalculationPropertySI(self.timeLimitsFrame,'Negative Time Limit',self.onNegativeTimeLimitEntered,None,self.project,'TimeLimitNegative','s')
        self.positiveTimeFrame=CalculationPropertySI(self.timeLimitsFrame,'Positive Time Limit',self.onPositiveTimeLimitEntered,None,self.project,'TimeLimitPositive','s')
        PropertiesDialog.bind(self,'<Return>',self.ok)
        PropertiesDialog.bind(self,'<Escape>',self.cancel)
        PropertiesDialog.protocol(self,"WM_DELETE_WINDOW", self.onClosing)
        self.Save()
        self.Finish()

    def onInherit(self):
        self.project['EndFrequency']=SignalIntegrity.App.Project['CalculationProperties.EndFrequency']
        self.project['FrequencyPoints']=SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints']
        self.project.CalculateOthersFromBaseInformation()
        self.UpdateStrings()

    def onendFrequencyEntered(self,event):
        self.project['EndFrequency']=nextHigher12458(self.project['EndFrequency'])
        self.project['FrequencyPoints']=int(nextHigher12458(self.project['EndFrequency']/self.project['FrequencyResolution']))
        self.project['FrequencyPoints']=max(1,self.project['FrequencyPoints'])
        self.UpdateStrings()

    def onfrequencyPointsEntered(self,event):
        self.project['FrequencyPoints']=max(1,self.project['FrequencyPoints'])
        self.UpdateStrings()

    def onfrequencyResolutionEntered(self,event):
        self.project['FrequencyPoints']=int(nextHigher12458(self.project['EndFrequency']/self.project['FrequencyResolution']))
        self.project['FrequencyPoints']=max(1,self.project['FrequencyPoints'])
        self.UpdateStrings()

    def onbaseSampleRateEntered(self,event):
        self.project['EndFrequency']=nextHigher12458(self.project['BaseSampleRate'])/2.
        self.project['FrequencyPoints']=int(nextHigher12458(self.project['EndFrequency']/self.project['FrequencyResolution']))
        self.project['FrequencyPoints']=max(1,self.project['FrequencyPoints'])
        self.UpdateStrings()

    def onbaseSamplePeriodEntered(self,event):
        self.project['EndFrequency']=nextHigher12458(1./self.project['BaseSamplePeriod'])/2.
        self.project['FrequencyPoints']=int(nextHigher12458(self.project['EndFrequency']/self.project['FrequencyResolution']))
        self.project['FrequencyPoints']=max(1,self.project['FrequencyPoints'])
        self.UpdateStrings()

    def ontimePointsEntered(self,event):
        self.project['FrequencyPoints']=int(nextHigher12458(self.project['TimePoints']/2))
        self.project['FrequencyPoints']=max(1,self.project['FrequencyPoints'])
        self.UpdateStrings()

    def onimpulseLengthEntered(self,event):
        self.project['TimePoints']=int(self.project['ImpulseResponseLength']*self.project['BaseSampleRate']+0.5)
        self.project['FrequencyPoints']=int(nextHigher12458(self.project['TimePoints']/2))
        self.project['FrequencyPoints']=max(1,self.project['FrequencyPoints'])
        self.UpdateStrings()

    def onNegativeTimeLimitEntered(self,event):
        if self.project['TimeLimitNegative']>0.:
            self.project['TimeLimitNegative']=0.0
            self.negativeTimeFrame.UpdateStrings()

    def onPositiveTimeLimitEntered(self,event):
        if self.project['TimeLimitPositive']<0.:
            self.project['TimeLimitPositive']=0.
            self.positiveTimeFrame.UpdateStrings()
    
    def onReferenceImpedanceEntered(self,event):
        self.UpdateStrings()

    def UpdateStrings(self):
        self.project.CalculateOthersFromBaseInformation()
        self.endFrequencyFrame.UpdateStrings()
        self.frequencyPointsFrame.UpdateStrings()
        self.frequencyResolutionFrame.UpdateStrings()
        self.baseSampleRateFrame.UpdateStrings()
        self.baseSamplePeriodFrame.UpdateStrings()
        self.timePointsFrame.UpdateStrings()
        self.impulseResponseLengthFrame.UpdateStrings()
        self.referenceImpedanceFrame.UpdateStrings()

    def destroy(self):
        PropertiesDialog.destroy(self)

    def onClosing(self):
        self.ok(None)

    def ok(self,event):
        self.destroy()
        self.parent.UpdateSParametersFromProperties()
        
    def cancel(self,event):
        self.Restore()
        self.destroy()

    def Save(self):
        self.saved={'EndFrequency':self.project['EndFrequency'],
                    'FrequencyPoints':self.project['FrequencyPoints'],
                    'UserSampleRate':self.project['UserSampleRate'],
                    'ReferenceImpedance':self.project['ReferenceImpedance'],
                    'TimeLimitNegative':self.project['TimeLimitNegative'],
                    'TimeLimitPositive':self.project['TimeLimitPositive']}
    
    def Restore(self):
        for key in self.saved:
            self.project[key]=self.saved[key]
        self.project.CalculateOthersFromBaseInformation()
