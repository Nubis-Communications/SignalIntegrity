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

from SignalIntegrity.App.CalculationPropertiesProject import PropertiesDialog,CalculationPropertySI,CalculationProperty
from SignalIntegrity.App.ToSI import nextHigher12458
import SignalIntegrity.App.Project

class CalculationPropertiesDialog(PropertiesDialog):
    def __init__(self,parent):
        PropertiesDialog.__init__(self,parent,SignalIntegrity.App.Project['CalculationProperties'],parent,'Calculation Properties')
        self.endFrequencyFrame=CalculationPropertySI(self.propertyListFrame,'End Frequency',self.onendFrequencyEntered,None,self.project,'EndFrequency','Hz')
        self.frequencyPointsFrame=CalculationProperty(self.propertyListFrame,'Frequency Points',self.onfrequencyPointsEntered,None,self.project,'FrequencyPoints')
        self.frequencyResolutionFrame=CalculationPropertySI(self.propertyListFrame,'Frequency Resolution',self.onfrequencyResolutionEntered,None,self.project,'FrequencyResolution','Hz')
        self.userSampleRateFrame=CalculationPropertySI(self.propertyListFrame,'User Sample Rate',self.onuserSampleRateEntered,None,self.project,'UserSampleRate','S/s')
        self.userSamplePeriodFrame=CalculationPropertySI(self.propertyListFrame,'User Sample Period',self.onuserSamplePeriodEntered,None,self.project,'UserSamplePeriod','s')
        self.baseSampleRateFrame=CalculationPropertySI(self.propertyListFrame,'Base Sample Rate',self.onbaseSampleRateEntered,None,self.project,'BaseSampleRate','S/s')
        self.baseSamplePeriodFrame=CalculationPropertySI(self.propertyListFrame,'Base Sample Period',self.onbaseSamplePeriodEntered,None,self.project,'BaseSamplePeriod','s')
        self.timePointsFrame=CalculationProperty(self.propertyListFrame,'Time Points',self.ontimePointsEntered,None,self.project,'TimePoints')
        self.impulseResponseLengthFrame=CalculationPropertySI(self.propertyListFrame,'Impulse Response Length',self.onimpulseLengthEntered,None,self.project,'ImpulseResponseLength','s')  
        PropertiesDialog.bind(self,'<Return>',self.ok)
        PropertiesDialog.bind(self,'<Escape>',self.cancel)
        PropertiesDialog.protocol(self,"WM_DELETE_WINDOW", self.onClosing)
        self.Save()
        self.Finish()

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

    def onuserSampleRateEntered(self,event):
        self.project['UserSampleRate']=nextHigher12458(self.project['UserSampleRate'])
        self.UpdateStrings()

    def onuserSamplePeriodEntered(self,event):
        self.project['UserSampleRate']=nextHigher12458(1./self.project['UserSamplePeriod'])
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

    def UpdateStrings(self):
        self.project.CalculateOthersFromBaseInformation()
        self.endFrequencyFrame.UpdateStrings()
        self.frequencyPointsFrame.UpdateStrings()
        self.frequencyResolutionFrame.UpdateStrings()
        self.userSampleRateFrame.UpdateStrings()
        self.userSamplePeriodFrame.UpdateStrings()
        self.baseSampleRateFrame.UpdateStrings()
        self.baseSamplePeriodFrame.UpdateStrings()
        self.timePointsFrame.UpdateStrings()
        self.impulseResponseLengthFrame.UpdateStrings()

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

