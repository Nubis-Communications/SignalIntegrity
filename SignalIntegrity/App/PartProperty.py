"""
PartProperty.py
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
from SignalIntegrity.App.ToSI import ToSI,FromSI
from SignalIntegrity.App.ProjectFile import PartPropertyConfiguration

class PartProperty(PartPropertyConfiguration):
    def __init__(self,propertyName,type=None,unit=None,keyword=None,description=None,value=None,hidden=False,visible=False,keywordVisible=True,inProjectFile=True):
        PartPropertyConfiguration.__init__(self)
        self['Keyword']=keyword
        self['PropertyName']=propertyName
        self['Description']=description
        self['Value']=value
        self['Hidden']=hidden
        self['Visible']=visible
        self['KeywordVisible']=keywordVisible
        self['Type']=type
        self['Unit']=unit
        self['InProjectFile']=inProjectFile
    def PropertyString(self,stype='raw'):
        if stype=='attr':
            result=''
            if self.GetValue('Visible') and not self.GetValue('Hidden'):
                if self.GetValue('KeywordVisible'):
                    if self.GetValue('Keyword') != None and self.GetValue('Keyword') != 'None':
                        result=result+self.GetValue('Keyword')+' '
                if self.GetValue('Type')=='string':
                    value = self.GetValue('Value')
                elif self.GetValue('Type')=='file':
                    value=('/'.join(str(self.GetValue('Value')).split('\\'))).split('/')[-1]
                elif self.GetValue('Type')=='int':
                    value = self.GetValue('Value')
                elif self.GetValue('Type')=='float':
                    value = str(ToSI(float(self.GetValue('Value')),self.GetValue('Unit')))
                else:
                    value = str(self.GetValue('Value'))
                result=result+value
            return result
        elif stype == 'raw':
            if self.GetValue('Type')=='string':
                value = self.GetValue('Value')
            elif self.GetValue('Type')=='file':
                value = self.GetValue('Value')
            elif self.GetValue('Type')=='int':
                value = self.GetValue('Value')
            elif self.GetValue('Type')=='float':
                value = str(float(self.GetValue('Value')))
            else:
                value = str(self.GetValue('Value'))
            return value
        elif stype == 'entry':
            if self.GetValue('Type')=='string':
                value = str(self.GetValue('Value'))
            elif self.GetValue('Type')=='file':
                value = str(self.GetValue('Value'))
            elif self.GetValue('Type')=='int':
                value = str(self.GetValue('Value'))
            elif self.GetValue('Type')=='float':
                value = str(ToSI(float(self.GetValue('Value')),self.GetValue('Unit')))
            else:
                value = str(self.GetValue('Value'))
            return value
        elif stype == 'netlist':
            if self.GetValue('Type')=='string':
                value = self.GetValue('Value')
            elif self.GetValue('Type')=='file':
                value=self.GetValue('Value')
                if not value is None:
                    if ' ' in value:
                        value = "'"+value+"'"
            elif self.GetValue('Type')=='int':
                value = self.GetValue('Value')
            elif self.GetValue('Type')=='float':
                value = str(float(self.GetValue('Value')))
            else:
                value = str(self.GetValue('Value'))
            return value
        else:
            raise ValueError
            return str(self['Value'])
    def SetValueFromString(self,string):
        if self['Type']=='string':
            self['Value']=str(string)
        elif self.GetValue('Type')=='file':
            self['Value']=str(string)
        elif self.GetValue('Type')=='int':
            try:
                self['Value']=int(string)
            except ValueError:
                self['Value']=0
        elif self['Type']=='float':
            value = FromSI(string,self['Unit'])
            if value is not None:
                self['Value']=value
        else:
            raise ValueError
            self['Value']=str(string)
        return self
    def GetValue(self,name=None):
        if not name is None:
            return PartPropertyConfiguration.GetValue(self,name)

        if self.GetValue('Type')=='int':
            return int(self.GetValue('Value'))
        elif self.GetValue('Type')=='float':
            return float(self.GetValue('Value'))
        else:
            return self.GetValue('Value')

class PartPropertyReadOnly(PartProperty):
    def __init__(self,propertyName,type=None,unit=None,keyword=None,description=None,value=None,hidden=False,visible=False,keywordVisible=True):
        inProjectFile=False
        PartProperty.__init__(self,propertyName,type,unit,keyword,description,value,hidden,visible,keywordVisible,inProjectFile)

class PartPropertyPortNumber(PartProperty):
    def __init__(self,portNumber):
        PartProperty.__init__(self,'portnumber',type='int',unit=None,keyword='pn',description='port number',value=portNumber,visible=True, keywordVisible=False)

class PartPropertyReferenceDesignator(PartProperty):
    def __init__(self,referenceDesignator=''):
        PartProperty.__init__(self,'reference',type='string',unit=None,keyword='ref',description='reference designator',value=referenceDesignator,visible=False,keywordVisible=False)

class PartPropertyDefaultReferenceDesignator(PartPropertyReadOnly):
    def __init__(self,referenceDesignator=''):
        PartPropertyReadOnly.__init__(self,'defaultreference',type='string',unit=None,keyword='defref',description='default reference designator',value=referenceDesignator,hidden=True,visible=False,keywordVisible=False)

class PartPropertyPorts(PartProperty):
    def __init__(self,numPorts=1,hidden=True):
        PartProperty.__init__(self,'ports',type='int',unit=None,description='ports',keyword='ports',value=numPorts,hidden=hidden)

class PartPropertyFileName(PartProperty):
    def __init__(self,fileName=''):
        PartProperty.__init__(self,'filename',type='file',unit=None,keyword='file',description='file name',value=fileName)

class PartPropertyWaveformFileName(PartProperty):
    def __init__(self,fileName=''):
        PartProperty.__init__(self,'waveformfilename',type='file',unit=None,keyword='wffile',description='file name',value=fileName)

class PartPropertyResistance(PartProperty):
    def __init__(self,resistance=50.,keyword='r',descriptionPrefix=''):
        PartProperty.__init__(self,'resistance',type='float',unit='Ohm',keyword=keyword,description=descriptionPrefix+'resistance (Ohms)',value=resistance,visible=True,keywordVisible=False)

class PartPropertyResistanceSkinEffect(PartProperty):
    def __init__(self,resistance=0.,keyword='rse',descriptionPrefix=''):
        PartProperty.__init__(self,'skineffectresistance',type='float',unit='Ohm/sqrt(Hz)',keyword=keyword,description=descriptionPrefix+'skin effect (Ohms/sqrt(Hz)))',value=resistance,visible=False,keywordVisible=False)

class PartPropertyCapacitance(PartProperty):
    def __init__(self,capacitance=1e-12,keyword='c',descriptionPrefix=''):
        PartProperty.__init__(self,'capacitance',type='float',unit='F',keyword=keyword,description=descriptionPrefix+'capacitance (F)',value=capacitance,visible=True,keywordVisible=False)

class PartPropertyDissipationFactor(PartProperty):
    def __init__(self,df=0.,keyword='df',descriptionPrefix=''):
        PartProperty.__init__(self,'dissipationfactor',type='float',unit=' ',keyword=keyword,description=descriptionPrefix+'dissipation factor',value=df,visible=False,keywordVisible=True)

class PartPropertyESR(PartProperty):
    def __init__(self,esr=0.,keyword='esr',descriptionPrefix=''):
        PartProperty.__init__(self,'effectiveseriesresistance',type='float',unit='Ohm',keyword=keyword,description=descriptionPrefix+'ESR (Ohms)',value=esr,visible=False,keywordVisible=True)

class PartPropertyInductance(PartProperty):
    def __init__(self,inductance=1e-9,keyword='l',descriptionPrefix=''):
        PartProperty.__init__(self,'inductance',type='float',unit='H',keyword=keyword,description=descriptionPrefix+'inductance (H)',value=inductance,visible=True,keywordVisible=False)

class PartPropertyConductance(PartProperty):
    def __init__(self,conductance=0.,keyword='g',descriptionPrefix=''):
        PartProperty.__init__(self,'conductance',type='float',unit='S',keyword=keyword,description=descriptionPrefix+'conductance (S)',value=conductance,visible=True,keywordVisible=False)

class PartPropertyPartName(PartPropertyReadOnly):
    def __init__(self,partName=''):
        PartPropertyReadOnly.__init__(self,'type',type='string',unit=None,keyword='partname',description='part type',value=partName,hidden=True)

class PartPropertyCategory(PartPropertyReadOnly):
    def __init__(self,category=''):
        PartPropertyReadOnly.__init__(self,'category',type='string',unit=None,keyword='cat',description='part category',value=category,hidden=True)

class PartPropertyDescription(PartPropertyReadOnly):
    def __init__(self,description=''):
        PartPropertyReadOnly.__init__(self,'description',type='string',unit=None,keyword='desc',description='part description',value=description,hidden=True)

class PartPropertyVoltageGain(PartProperty):
    def __init__(self,voltageGain=1.0):
        PartProperty.__init__(self,'gain',type='float',unit='',keyword='gain',description='voltage gain (V/V)',value=voltageGain,visible=True)

class PartPropertyCurrentGain(PartProperty):
    def __init__(self,currentGain=1.0):
        PartProperty.__init__(self,'gain',type='float',unit='',keyword='gain',description='current gain (A/A)',value=currentGain,visible=True)

class PartPropertyTransconductance(PartProperty):
    def __init__(self,transconductance=1.0):
        PartProperty.__init__(self,'transconductance',type='float',unit='A/V',keyword='gain',description='transconductance (A/V)',value=transconductance,visible=True)

class PartPropertyTransresistance(PartProperty):
    def __init__(self,transresistance=1.0):
        PartProperty.__init__(self,'transresistance',type='float',unit='V/A',keyword='gain',description='transresistance (V/A)',value=transresistance,visible=True)

class PartPropertyInputImpedance(PartProperty):
    def __init__(self,inputImpedance=1e8):
        PartProperty.__init__(self,'inputimpedance',type='float',unit='Ohm',keyword='zi',description='input impedance (Ohms)',value=inputImpedance,visible=True)

class PartPropertyOutputImpedance(PartProperty):
    def __init__(self,outputImpedance=0.):
        PartProperty.__init__(self,'outputimpedance',type='float',unit='Ohm',keyword='zo',description='output impedance (Ohms)',value=outputImpedance,visible=True)

class PartPropertyHorizontalOffset(PartProperty):
    def __init__(self,horizontalOffset=-100e-9):
        PartProperty.__init__(self,'horizontaloffset',type='float',unit='s',keyword='ho',description='horizontal offset (s)',value=horizontalOffset,visible=False)

class PartPropertyDuration(PartProperty):
    def __init__(self,duration=200e-9):
        PartProperty.__init__(self,'duration',type='float',unit='s',keyword='dur',description='duration (s)',value=duration,visible=False)

class PartPropertySampleRate(PartProperty):
    def __init__(self,sampleRate=40e9):
        PartProperty.__init__(self,'sampleRate',type='float',unit='S/s',keyword='fs',description='Sample Rate (S/s)',value=sampleRate,visible=False)

class PartPropertyStartTime(PartProperty):
    def __init__(self,startTime=0.):
        PartProperty.__init__(self,'starttime',type='float',unit='s',keyword='t0',description='start time (s)',value=startTime,visible=True)

class PartPropertyVoltageAmplitude(PartProperty):
    def __init__(self,voltageAmplitude=1.):
        PartProperty.__init__(self,'voltageamplitude',type='float',unit='V',keyword='a',description='voltage amplitude (V)',value=voltageAmplitude,visible=True)

class PartPropertyVoltageRms(PartProperty):
    def __init__(self,voltagerms=0.):
        PartProperty.__init__(self,'voltagerms',type='float',unit='Vrms',keyword='vrms',description='voltage (Vrms)',value=voltagerms,visible=True)

class PartPropertyCurrentAmplitude(PartProperty):
    def __init__(self,currentAmplitude=1.):
        PartProperty.__init__(self,'currentamplitude',type='float',unit='A',keyword='a',description='current amplitude (A)',value=currentAmplitude,visible=True)

class PartPropertyPulseWidth(PartProperty):
    def __init__(self,pulseWidth=1e-9):
        PartProperty.__init__(self,'pulsewidth',type='float',unit='s',keyword='w',description='pulse width (s)',value=pulseWidth,visible=True)

class PartPropertyFrequency(PartProperty):
    def __init__(self,frequency=1e6):
        PartProperty.__init__(self,'frequency',type='float',unit='Hz',keyword='f',description='frequency (Hz)',value=frequency,visible=True)

class PartPropertyPhase(PartProperty):
    def __init__(self,phase=0.):
        PartProperty.__init__(self,'phase',type='float',unit='deg',keyword='ph',description='phase (degrees)',value=phase,visible=True)

class PartPropertyTurnsRatio(PartProperty):
    def __init__(self,ratio=1.):
        PartProperty.__init__(self,'turnsratio',type='float',unit='',keyword='tr',description='turns ratio (S/P)',value=ratio,visible=True,keywordVisible=False)

class PartPropertyVoltageOffset(PartProperty):
    def __init__(self,voltageOffset=0.0):
        PartProperty.__init__(self,'offset',type='float',unit='V',keyword='offset',description='voltage offset (V)',value=voltageOffset,visible=True)

class PartPropertyDelay(PartProperty):
    def __init__(self,delay=0.0):
        PartProperty.__init__(self,'delay',type='float',unit='s',keyword='td',description='delay (s)',value=delay,visible=True)

class PartPropertyCharacteristicImpedance(PartProperty):
    def __init__(self,characteristicImpedance=50.):
        PartProperty.__init__(self,'characteristicimpedance',type='float',unit='Ohm',keyword='zc',description='characteristic impedance (Ohms)',value=characteristicImpedance,visible=True)

class PartPropertySections(PartProperty):
    def __init__(self,sections=1):
        PartProperty.__init__(self,'sections',type='int',unit='',keyword='sect',description='sections',value=sections,visible=True,keywordVisible=False)

class PartPropertyWeight(PartProperty):
    def __init__(self,weight=1.0):
        PartProperty.__init__(self,'weight',type='float',unit='',keyword='weight',description='weight',value=weight,visible=False)

class PartPropertyReferenceImpedance(PartProperty):
    def __init__(self,impedance=50.,keyword='z0',):
        PartProperty.__init__(self,'impedance',type='float',unit='Ohm',keyword=keyword,description='reference impedance (Ohms)',value=impedance,visible=True,keywordVisible=True)

class PartPropertyGm(PartProperty):
    def __init__(self,Gm=1.0):
        PartProperty.__init__(self,'Gm',type='float',unit='A/V',keyword='gm',description='Gm (A/V)',value=Gm,visible=True)

class PartPropertyRpi(PartProperty):
    def __init__(self,rpi=1e8):
        PartProperty.__init__(self,'Rpi',type='float',unit='Ohm',keyword='rpi',description='base/emitter resistance (Ohms)',value=rpi,visible=True)

class PartPropertyOutputResistance(PartProperty):
    def __init__(self,ro=1e8):
        PartProperty.__init__(self,'ro',type='float',unit='Ohm',keyword='ro',description='collector/emitter output resistance (Ohms)',value=ro,visible=True)

class PartPropertyWaveformType(PartProperty):
    def __init__(self,wfType=None):
        PartProperty.__init__(self,'wftype',type='string',unit=None,keyword='wftype',description='waveform type',value=wfType,hidden=True,visible=False)

class PartPropertyWaveformProjectName(PartProperty):
    def __init__(self,wfProjName=None):
        PartProperty.__init__(self,'wfprojname',type='string',unit=None,keyword='wfprojname',keywordVisible=False,description='waveform project name',value=wfProjName,visible=False)

class PartPropertyBitRate(PartProperty):
    def __init__(self,bitRate=1e9):
        PartProperty.__init__(self,'bitRate',type='float',unit='b/s',keyword='br',description='bit rate (b/s)',value=bitRate,visible=True)

class PartPropertyRisetime(PartProperty):
    def __init__(self,risetime=0.0):
        PartProperty.__init__(self,'risetime',type='float',unit='s',keyword='rt',description='risetime (s)',value=risetime,visible=False)

class PartPropertyPRBSPolynomial(PartProperty):
    def __init__(self,poly=7):
        PartProperty.__init__(self,'prbs',type='int',unit='',keyword='prbs',description='prbs polynomial order',value=poly,visible=True,keywordVisible=True)
