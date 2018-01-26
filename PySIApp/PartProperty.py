'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
import xml.etree.ElementTree as et

from ToSI import ToSI,FromSI

class PartProperty(object):
    def __init__(self,propertyName,type=None,unit=None,keyword=None,description=None,value=None,hidden=False,visible=False,keywordVisible=True):
        self.keyword=keyword
        self.propertyName=propertyName
        self.description=description
        self._value=value
        self.hidden=hidden
        self.visible=visible
        self.keywordVisible=keywordVisible
        self.type=type
        self.unit=unit
        if isinstance(value,str):
            self.SetValueFromString(value)
    def NetListProperty(self):
        return self.keyword + ' ' + self.PropertyString(stype='raw')
    def PropertyString(self,stype='raw'):
        if stype=='attr':
            result=''
            if self.visible:
                if self.keywordVisible:
                    if self.keyword != None and self.keyword != 'None':
                        result=result+self.keyword+' '
                if self.type=='string':
                    value = str(self._value)
                elif self.type=='file':
                    value=('/'.join(str(self._value).split('\\'))).split('/')[-1]
                elif self.type=='int':
                    value = str(self._value)
                elif self.type=='float':
                    value = str(ToSI(float(self._value),self.unit))
                else:
                    value = str(self._value)
                result=result+value
            return result
        elif stype == 'raw':
            if self.type=='string':
                value = str(self._value)
            elif self.type=='file':
                value = str(self._value)
            elif self.type=='int':
                value = str(self._value)
            elif self.type=='float':
                value = str(float(self._value))
            else:
                value = str(self._value)
            return value
        elif stype == 'entry':
            if self.type=='string':
                value = str(self._value)
            elif self.type=='file':
                value = str(self._value)
            elif self.type=='int':
                value = str(self._value)
            elif self.type=='float':
                value = str(ToSI(float(self._value),self.unit))
            else:
                value = str(self._value)
            return value
        else:
            raise ValueError
            return str(self._value)
    def SetValueFromString(self,string):
        if self.type=='string':
            self._value = str(string)
        elif self.type=='file':
            self._value = str(string)
        elif self.type=='int':
            try:
                self._value = int(string)
            except ValueError:
                self._value = 0
        elif self.type=='float':
            value = FromSI(string,self.unit)
            if value is not None:
                self._value=value
        else:
            raise ValueError
            self._value = str(string)
        return self
    def GetValue(self):
        return self._value
    def xml(self):
        pp = et.Element('part_property')
        pList=[]
        p=et.Element('keyword')
        p.text=str(self.keyword)
        pList.append(p)
        p=et.Element('property_name')
        p.text=str(self.propertyName)
        pList.append(p)
        p=et.Element('description')
        p.text=str(self.description)
        pList.append(p)
        p=et.Element('value')
        p.text=self.PropertyString(stype='raw')
        pList.append(p)
        p=et.Element('hidden')
        p.text=str(self.hidden)
        pList.append(p)
        p=et.Element('visible')
        p.text=str(self.visible)
        pList.append(p)
        p=et.Element('keyword_visible')
        p.text=str(self.keywordVisible)
        pList.append(p)
        p=et.Element('type')
        p.text=str(self.type)
        pList.append(p)
        p=et.Element('unit')
        p.text=str(self.unit)
        pList.append(p)
        pp.extend(pList)
        return pp

class PartPropertyXMLClassFactory(PartProperty):
    def __init__(self,xml):
        propertyName=''
        keyword=None
        description=None
        value=None
        hidden=False
        visible=False
        ptype='string'
        unit=None
        keywordVisible=False
        for item in xml:
            if item.tag == 'keyword':
                keyword = item.text
            elif item.tag == 'property_name':
                propertyName = item.text
                # this fixes a misspelling I corrected but breaks
                # lots of old projects
                if propertyName == 'resistence':
                    propertyName = 'resistance'
                if propertyName == 'Resistance':
                    propertyName = 'resistance'
            elif item.tag == 'description':
                description = item.text
            elif item.tag == 'value':
                value = item.text
            elif item.tag == 'hidden':
                hidden = eval(item.text)
            elif item.tag == 'visible':
                visible = eval(item.text)
            elif item.tag == 'keyword_visible':
                keywordVisible = eval(item.text)
            elif item.tag == 'type':
                ptype = item.text
            elif item.tag == 'unit':
                unit = item.text
        # hack because stupid xml outputs none for empty string
        if ptype == 'float' and (unit is None or unit == 'None'):
            unit = ''
        self.result=PartProperty(propertyName,ptype,unit,keyword,description,value,hidden,visible,keywordVisible)

class PartPropertyPortNumber(PartProperty):
    def __init__(self,portNumber):
        PartProperty.__init__(self,'portnumber',type='int',unit=None,keyword='',description='port number',value=portNumber,visible=True)

class PartPropertyReferenceDesignator(PartProperty):
    def __init__(self,referenceDesignator=''):
        PartProperty.__init__(self,'reference',type='string',unit=None,description='reference designator',value=referenceDesignator,visible=False,keywordVisible=False)

class PartPropertyDefaultReferenceDesignator(PartProperty):
    def __init__(self,referenceDesignator=''):
        PartProperty.__init__(self,'defaultreference',type='string',unit=None,description='default reference designator',value=referenceDesignator,hidden=True,visible=False,keywordVisible=False)

class PartPropertyPorts(PartProperty):
    def __init__(self,numPorts=1,hidden=True):
        PartProperty.__init__(self,'ports',type='int',unit=None,description='ports',value=numPorts,hidden=hidden)

class PartPropertyFileName(PartProperty):
    def __init__(self,fileName=''):
        PartProperty.__init__(self,'filename',type='file',unit=None,description='file name',value=fileName)

class PartPropertyWaveformFileName(PartProperty):
    def __init__(self,fileName=''):
        PartProperty.__init__(self,'waveformfilename',type='file',unit=None,description='file name',value=fileName)

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

class PartPropertyPartName(PartProperty):
    def __init__(self,partName=''):
        PartProperty.__init__(self,'type',type='string',unit=None,description='part type',value=partName,hidden=True)

class PartPropertyCategory(PartProperty):
    def __init__(self,category=''):
        PartProperty.__init__(self,'category',type='string',unit=None,description='part category',value=category,hidden=True)

class PartPropertyDescription(PartProperty):
    def __init__(self,description=''):
        PartProperty.__init__(self,'description',type='string',unit=None,description='part description',value=description,hidden=True)

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

