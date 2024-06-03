"""
CalculationPropertiesDialog.py
"""
# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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
from SignalIntegrity.Lib.ToSI import nextHigher12458
import SignalIntegrity.App.Project
import SignalIntegrity.App.Preferences

import tkinter as tk

class CalculationPropertiesDialog(PropertiesDialog):
    def __init__(self,parent):
        PropertiesDialog.__init__(self,parent,SignalIntegrity.App.Project['CalculationProperties'],parent,'Calculation Properties')
        self.transient(parent)
        self.TimeAndFrequencyFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.TimeAndFrequencyFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.endFrequency=CalculationPropertySI(self.TimeAndFrequencyFrame,'End Frequency',self.onendFrequencyEntered,None,self.project,'EndFrequency','Hz')
        self.frequencyPoints=CalculationProperty(self.TimeAndFrequencyFrame,'Frequency Points',self.onfrequencyPointsEntered,None,self.project,'FrequencyPoints')
        self.frequencyResolution=CalculationPropertySI(self.TimeAndFrequencyFrame,'Frequency Resolution',self.onfrequencyResolutionEntered,None,self.project,'FrequencyResolution','Hz')
        self.userSampleRate=CalculationPropertySI(self.TimeAndFrequencyFrame,'User Sample Rate',self.onuserSampleRateEntered,None,self.project,'UserSampleRate','S/s')
        self.userSamplePeriod=CalculationPropertySI(self.TimeAndFrequencyFrame,'User Sample Period',self.onuserSamplePeriodEntered,None,self.project,'UserSamplePeriod','s')
        self.baseSampleRate=CalculationPropertySI(self.TimeAndFrequencyFrame,'Base Sample Rate',self.onbaseSampleRateEntered,None,self.project,'BaseSampleRate','S/s')
        self.baseSamplePeriod=CalculationPropertySI(self.TimeAndFrequencyFrame,'Base Sample Period',self.onbaseSamplePeriodEntered,None,self.project,'BaseSamplePeriod','s')
        self.timePoints=CalculationProperty(self.TimeAndFrequencyFrame,'Time Points',self.ontimePointsEntered,None,self.project,'TimePoints')
        self.impulseResponseLength=CalculationPropertySI(self.TimeAndFrequencyFrame,'Impulse Response Length',self.onimpulseLengthEntered,None,self.project,'ImpulseResponseLength','s')
        if (self.parent.Drawing.schematic.HasDependentSource()):
            self.ProcessingIterations = CalculationProperty(self.TimeAndFrequencyFrame, 'Number of Processing Iterations', self.onProcessingIterationsEntered, None, self.project,'ProcessingIterations')
        self.logarithmicFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.logarithmicFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        if SignalIntegrity.App.Preferences['Calculation.LogarithmicSolutions'] or self.project['UnderlyingType'] != 'Linear':
            self.underlyingType=CalculationPropertyChoices(self.logarithmicFrame,'Frequency List Type',self.onunderlyingTypeEntered,None,[('Linear','Linear'),('Logarithmic','Logarithmic')],self.project,'UnderlyingType')
        self.logarithmicInformationFrame=tk.Frame(self.logarithmicFrame)
        showLogarithmic = self.project['UnderlyingType'] == 'Logarithmic'
        if showLogarithmic: self.logarithmicInformationFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.logarithmicStartFrequency = CalculationPropertySI(self.logarithmicInformationFrame,'Logarithmic Start Frequency',None,None,self.project,'LogarithmicStartFrequency','Hz')
        self.logarithmicEndFrequency = CalculationPropertySI(self.logarithmicInformationFrame,'Logarithmic End Frequency',None,None,self.project,'LogarithmicEndFrequency','Hz')
        self.logarithmicPointsPerDecade = CalculationProperty(self.logarithmicInformationFrame,'Logarithmic Points Per Decade',None,None,self.project,'LogarithmicPointsPerDecade')
        self.ReferenceImpedanceFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.ReferenceImpedanceFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        if SignalIntegrity.App.Preferences['Calculation.Non50OhmSolutions'] or self.project['ReferenceImpedance'] != 50.:
            self.referenceImpedance=CalculationPropertySI(self.ReferenceImpedanceFrame,'Reference Impedance',None,None,self.project,'ReferenceImpedance','ohm')
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

    def onProcessingIterationsEntered(self, event):
        self.project['ProcessingIterations'] = int(self.project['ProcessingIterations'])
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
        if (self.parent.Drawing.schematic.HasDependentSource()):
            self.ProcessingIterations.UpdateStrings()
        showLogarithmic = self.project['UnderlyingType'] == 'Logarithmic'
        self.logarithmicInformationFrame.pack_forget()
        if showLogarithmic:
            self.logarithmicInformationFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        showReferenceImpedance = SignalIntegrity.App.Preferences['Calculation.Non50OhmSolutions'] or self.project['ReferenceImpedance'] != 50.
        self.ReferenceImpedanceFrame.pack_forget()
        if showReferenceImpedance:
            self.ReferenceImpedanceFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)

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
                    'UserSampleRate':self.project['UserSampleRate'],
                    'ProcessingIterations':self.project['ProcessingIterations']}

    def Restore(self):
        for key in self.saved:
            self.project[key]=self.saved[key]
        self.project.CalculateOthersFromBaseInformation()

