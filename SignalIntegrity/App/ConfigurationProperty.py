"""Metadata, presentation state and typed bindings for device configurations."""

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

import math
import os
import copy
import weakref
import xml.etree.ElementTree as ET

from SignalIntegrity.App.ProjectFileBase import XMLConfiguration, XMLProperty
from SignalIntegrity.Lib.ToSI import FromSI, ToSI


class ConfigurationError(ValueError):
    pass


class ConfigurationFieldState(XMLConfiguration):
    presentationOnly=True

    def __init__(self):
        super().__init__('ConfigurationFields')
        self.entries={}
        self.changed=False

    def InitFromXML(self,element):
        self.entries={}
        self.changed=False
        for field in element.findall('Field'):
            path=field.get('path')
            if not path:
                raise ConfigurationError('configuration field state requires a path')
            visible=field.get('visible','False')
            if visible not in ('True','False'):
                raise ConfigurationError('invalid configuration visibility for '+path)
            self.entries[path]={'visible':visible=='True','reference':field.get('reference','')}
        return self

    def OutputXML(self,indent):
        fields=[]
        for path,state in sorted(self.entries.items()):
            if not state['visible'] and not state['reference']:
                continue
            element=ET.Element('Field',path=path)
            if state['visible']:
                element.set('visible','True')
            if state['reference']:
                element.set('reference',state['reference'])
            fields.append(indent+'\t'+ET.tostring(element,encoding='unicode'))
        return [indent+'<ConfigurationFields>']+fields+[indent+'</ConfigurationFields>'] if fields else []

    def Changed(self,changed):
        return self.changed or changed

    def SetChanged(self,changed=True):
        self.changed=changed
        return self


# label, units, description, accepted stored enum keywords
NOISE_FIELDS={
    'Enable':('Enable noise','','Enable statistical noise generation.',()),
    'Type':('Noise type','','Select the statistical noise model.',()),
    'Lanes':('Lanes','','Number of independent noise lanes; total RMS scales with its square root.',()),
    'WhiteNoise.WhiteNoiseType':('White noise type','','Select the authoritative noise representation.',()),
    'WhiteNoise.NoisedBmPerHz':('Noise density','dBm/Hz','Noise power density using the source reference impedance.',()),
    'WhiteNoise.VPerRootHz':('Voltage noise density','V/sqrt(Hz)','Voltage amplitude spectral density per lane.',()),
    'WhiteNoise.APerRootHz':('Current noise density','A/sqrt(Hz)','Current amplitude spectral density per lane.',()),
    'WhiteNoise.VSquaredPerGHz':('Voltage noise power density','V^2/GHz','Voltage-squared spectral density per GHz per lane.',()),
    'WhiteNoise.ASquaredPerGHz':('Current noise power density','A^2/GHz','Current-squared spectral density per GHz per lane.',()),
    'WhiteNoise.VRms':('RMS voltage noise','Vrms','Integrated voltage noise per lane over the noise bandwidth.',()),
    'WhiteNoise.ARms':('RMS current noise','Arms','Integrated current noise per lane over the noise bandwidth.',()),
    'WhiteNoise.NoiseBandwidth':('Noise bandwidth','Hz','Upper frequency limit for noise support and RMS integration.',()),
    'WhiteNoise.SNR.Vpp':('Signal peak-to-peak voltage','V','Signal swing used by ENOB and COM TX noise models.',()),
    'WhiteNoise.SNR.ENOB.ENOB':('ENOB','','Effective number of bits; SNR = 6.02 * ENOB + 1.76 dB.',()),
    'WhiteNoise.SNR.COM_TX.h0':('COM TX cursor height','','Transmitter FFE main-cursor height used to scale noise.',()),
    'WhiteNoise.SNR.COM_TX.SNRdB':('COM TX SNR','dB','Transmitter signal-to-noise ratio.',()),
    'WhiteNoise.SNR.COM_TX.Risetime':('COM TX 20-80 rise time','s','Gaussian shaping rise time; zero disables shaping.',()),
    'WhiteNoise.Johnson.Temperature_Kelvin':('Johnson temperature','K','Absolute temperature for thermal noise.',()),
    'WhiteNoise.Johnson.Resistance':('Johnson resistance','ohm','Resistance generating thermal voltage noise.',()),
    'SpectralDensityFile.FileName':('Spectral density file','','Spectral-density input file (.txt, .csv or .json).',()),
    'WaveformFile.FileName':('Noise waveform file','','Waveform whose spectrum defines the noise.',()),
    'Crosstalk.ProbeName':('Crosstalk probe','','Output probe supplying the crosstalk waveform.',()),
    'ShotNoise.CurrentSource':('Shot-noise current source','','Use an entered mean current or a current-probe waveform.',('Mean','TimeVarying')),
    'ShotNoise.MeanCurrent':('Shot-noise mean current','A','Input in Mean mode; calculated equivalent current in TimeVarying mode.',()),
    'ShotNoise.ProbeName':('Shot-noise current probe','','Name of the current output probe for time-varying shot noise.',()),
    'ShotNoise.NoiseBandwidth':('Shot-noise bandwidth','Hz','Upper frequency limit for shot-noise integration.',()),
}

EYE_FIELDS={
    'Color':('Eye color','','Plot color (or background color when not inverted).',()),
    'UI':('Eye UI','','Number of unit intervals displayed.',()),
    'Rows':('Eye rows','','Vertical resolution of the raw eye bitmap.',()),
    'Columns':('Eye columns','','Horizontal bitmap resolution per unit interval.',()),
    'Saturation':('Eye saturation','%','Plot intensity saturation.',()),
    'ScaleX':('Eye X scale','%','Horizontal display scaling.',()),
    'ScaleY':('Eye Y scale','%','Vertical display scaling.',()),
    'Mode':('Eye mode','','Include ISI only, or also statistical jitter and noise.',('ISI','JitterNoise')),
    'Invert':('Invert eye plot','','Invert the plot background and foreground.',()),
    'UpsampleMethod':('Upsample method','','Interpolation used for eye construction.',('SinX','Linear')),
    'ClockRecovery.Recover':('Recover clock','','Enable clock recovery before eye construction.',()),
    'ClockRecovery.TrimLeftRight':('Clock-recovery trim','','Points trimmed from each end during clock recovery.',()),
    'YAxis.Mode':('Eye Y-axis mode','','Automatic or explicitly bounded Y axis.',('Auto','Fixed')),
    'YAxis.Max':('Eye Y maximum','V','Upper bound of the fixed Y axis.',()),
    'YAxis.Min':('Eye Y minimum','V','Lower bound of the fixed Y axis.',()),
    'JitterNoise.JitterS':('Random jitter','s','RMS random timing jitter.',()),
    'JitterNoise.JitterDeterministicPkS':('Deterministic jitter','s','Peak deterministic timing jitter.',()),
    'JitterNoise.Noise':('Inherent noise','Vrms','Fixed inherent receiver noise, combined with external noise.',()),
    'JitterNoise.ExternalNoise':('External noise','Vrms','Calculated noise from statistical noise-source analysis.',()),
    'JitterNoise.TotalNoise':('Total noise','Vrms','Calculated root-sum-square of inherent and external noise.',()),
    'JitterNoise.MaxKernelPixels':('Maximum noise kernel','pixels','Maximum jitter/noise convolution-kernel size.',()),
    'JitterNoise.LogIntensity.LogIntensity':('Log intensity','','Use logarithmic eye intensity.',()),
    'JitterNoise.LogIntensity.MinExponent':('Minimum intensity exponent','','Lower logarithmic intensity exponent.',()),
    'JitterNoise.LogIntensity.MaxExponent':('Maximum intensity exponent','','Upper logarithmic intensity exponent.',()),
    'Alignment.AutoAlign':('Auto-align eye','','Align the eye using its probability contours.',()),
    'Alignment.Levels':('PAM levels','','Number of signal levels per symbol.',()),
    'Alignment.BERForAlignment':('Alignment BER exponent','','Base-10 BER exponent used for eye alignment.',()),
    'Alignment.Mode':('Alignment mode','','Horizontal or vertical alignment.',('Horizontal','Vertical')),
    'Alignment.Horizontal':('Horizontal alignment','','Middle eye or widest eye.',('Middle','Max')),
    'Alignment.Vertical':('Vertical alignment','','Maximize the smallest opening or the maximum opening.',('MaxMin','Max')),
    'EnhancedPrecision.Mode':('Precision mode','','Automatic, fixed, or disabled precision enhancement.',('Auto','Fixed','None')),
    'EnhancedPrecision.FixedEnhancement':('Precision enhancement','','Fixed eye precision-enhancement factor.',()),
    'Measure.Measure':('Measure eye','','Calculate eye measurements.',()),
    'Measure.WaveformType':('Waveform type','','Physical units and optical interpretation of the signal.',('V','A','W','FW','AW','VW')),
    'Measure.RxTx':('Receiver/transmitter','','Optical receiver or transmitter measurement context.',('Rx','Tx','N/A')),
    'Measure.TxInputPowerAvailable':('Input power available','','Whether transmitter optical input power is known.',()),
    'Measure.TxInputPowerW':('Transmitter input power','W','Optical input power in watts.',()),
    'Measure.TxInputPowerdBm':('Transmitter input power','dBm','Calculated dBm representation of optical input power.',()),
    'Measure.BERForMeasure':('Measurement BER exponent','','Base-10 BER exponent used for measurements.',()),
    'Decision.Mode':('Decision level','','Midpoint or best decision threshold.',('Mid','Best')),
    'Bathtub.Measure':('Measure bathtub curves','','Calculate horizontal bathtub curves.',()),
    'Bathtub.DecadesFromJoinForFit':('Bathtub fit decades','','Decades above the join used for tail fitting.',()),
    'Bathtub.MinPointsForFit':('Bathtub fit points','','Minimum points used for tail fitting.',()),
    'Annotation.Annotate':('Annotate eye','','Draw measurement annotations.',()),
    'Annotation.Color':('Annotation color','','Color used for measurement annotations.',()),
    'Annotation.MeanLevels':('Show mean levels','','Draw the mean signal levels.',()),
    'Annotation.LabelMeanLevels':('Label mean levels','','Label the mean signal levels.',()),
    'Annotation.LevelExtents':('Show level extents','','Draw the signal-level extents.',()),
    'Annotation.EyeWidth':('Show eye width','','Draw measured eye widths.',()),
    'Annotation.EyeHeight':('Show eye height','','Draw measured eye heights.',()),
    'Annotation.Contours.Show':('Show contours','','Draw probability contours.',()),
    'Annotation.Contours.Which':('Contours to show','','Only contours inside the eye, or all contours.',('Eye','All')),
}


def _leaves(configuration,prefix=''):
    for name,value in list(configuration.dict.items()):
        if isinstance(value,ConfigurationFieldState):
            continue
        path=prefix+name
        if isinstance(value,XMLProperty):
            yield path,value
        elif isinstance(value,XMLConfiguration):
            if hasattr(value,'parent'):
                value.parent=configuration
            yield from _leaves(value,path+'.')


def InitializeConfiguration(configuration):
    if 'ConfigurationFields' not in configuration.dict:
        configuration.SubDir(ConfigurationFieldState())
    if getattr(configuration,'configurationFieldDictionary',None) is configuration.dict:
        return configuration
    definitions=EYE_FIELDS if configuration.name=='EyeDiagram' else NOISE_FIELDS
    fields={}
    for path,leaf in _leaves(configuration):
        if path not in definitions:
            continue
        field=ConfigurationProperty(configuration,path,definitions[path])
        leaf.configurationField=field
        fields[path]=field
    configuration.configurationFields=fields
    configuration.configurationFieldDictionary=configuration.dict
    return configuration


def BindConfiguration(configuration,variables,reference=''):
    InitializeConfiguration(configuration)
    configuration.configurationVariables=weakref.ref(variables)
    configuration.configurationReference=reference
    return configuration


def DeviceConfigurations(device):
    configurations=device.configuration
    return configurations if isinstance(configurations,list) else ([] if configurations is None else [configurations])


class ConfigurationProperty:
    def __init__(self,configuration,path,definition):
        self.configuration=configuration
        self.path=path
        self.label,self._units,self.description,self.choices=definition
        if path=='Type':
            choices=['WhiteNoise','SpectralDensityFile','WaveformFile','Crosstalk']
            choices+=['ShotNoise'] if configuration.name=='CurrentNoise' else ['Johnson']
            self.choices=tuple(choices)
        elif path=='WhiteNoise.WhiteNoiseType':
            self.choices=(('dBm/Hz','A/sqrt(Hz)','A^2/GHz','Arms') if configuration.name=='CurrentNoise'
                          else ('dBm/Hz','V/sqrt(Hz)','V^2/GHz','Vrms','ENOB','COM TX','Johnson'))

    @property
    def leaf(self):
        return self.configuration.GetPropertyValue(self.path)

    @property
    def state(self):
        return self.configuration.dict['ConfigurationFields']

    @property
    def reference(self):
        return self.state.entries.get(self.path,{}).get('reference','')

    @property
    def visible(self):
        return self.state.entries.get(self.path,{}).get('visible',False)

    @visible.setter
    def visible(self,value):
        state=self.state.entries.setdefault(self.path,{'visible':False,'reference':''})
        state['visible']=bool(value)
        self.state.SetChanged()

    @property
    def type(self):
        return self.leaf.dict['type']

    @property
    def units(self):
        if self.configuration.name=='EyeDiagram' and self.path in (
                'JitterNoise.Noise','JitterNoise.ExternalNoise','JitterNoise.TotalNoise'):
            field=self.configuration.configurationFields['Measure.WaveformType']
            value=field.Value()
            value={'Voltage':'V','Current':'A','Power':'W'}.get(value,value)
            return {'V':'Vrms','A':'Arms','W':'Wrms','FW':'','AW':'Arms','VW':'Vrms'}[field.Parse(value)]
        return self._units

    def Computed(self):
        if self.path in ('JitterNoise.ExternalNoise','JitterNoise.TotalNoise','Measure.TxInputPowerdBm'):
            return True
        return (self.path=='ShotNoise.MeanCurrent'
                and self.configuration['ShotNoise.CurrentSource']=='TimeVarying')

    def Active(self):
        c,p=self.configuration,self.path
        if c.name!='EyeDiagram':
            if p=='Enable':
                return True
            if not c['Enable']:
                return False
            if p in ('Type','Lanes'):
                return True
            mode=c['Type']
            if p.startswith('WhiteNoise.'):
                if mode=='Johnson':
                    return p.startswith('WhiteNoise.Johnson.')
                if mode!='WhiteNoise':
                    return False
                kind=c['WhiteNoise.WhiteNoiseType']
                if p in ('WhiteNoise.WhiteNoiseType','WhiteNoise.NoiseBandwidth'):
                    return True
                if p=='WhiteNoise.SNR.Vpp':
                    return kind in ('ENOB','COM TX')
                if p.startswith('WhiteNoise.SNR.ENOB.'):
                    return kind=='ENOB'
                if p.startswith('WhiteNoise.SNR.COM_TX.'):
                    return kind=='COM TX'
                if p.startswith('WhiteNoise.Johnson.'):
                    return kind=='Johnson'
                selected={'dBm/Hz':'NoisedBmPerHz','V/sqrt(Hz)':'VPerRootHz',
                          'V^2/GHz':'VSquaredPerGHz','Vrms':'VRms','A/sqrt(Hz)':'APerRootHz',
                          'A^2/GHz':'ASquaredPerGHz','Arms':'ARms'}
                return p=='WhiteNoise.'+selected.get(kind,'')
            if p.startswith('ShotNoise.'):
                return mode=='ShotNoise' and (p!='ShotNoise.ProbeName'
                       or c['ShotNoise.CurrentSource']=='TimeVarying')
            return p.split('.')[0]==mode
        if p in ('YAxis.Min','YAxis.Max'):
            return c['YAxis.Mode']=='Fixed'
        if p=='EnhancedPrecision.FixedEnhancement':
            return c['EnhancedPrecision.Mode']=='Fixed'
        if p=='ClockRecovery.TrimLeftRight':
            return c['ClockRecovery.Recover']
        if p.startswith('JitterNoise.LogIntensity.'):
            return p.endswith('.LogIntensity') or c['JitterNoise.LogIntensity.LogIntensity']
        if p.startswith('JitterNoise.'):
            return c['Mode']=='JitterNoise'
        if p.startswith('Alignment.') and p not in ('Alignment.Levels','Alignment.AutoAlign'):
            return c['Alignment.AutoAlign'] and (p not in ('Alignment.Horizontal','Alignment.Vertical')
                   or p.split('.')[-1]==c['Alignment.Mode'])
        if p.startswith(('Measure.','Decision.','Bathtub.','Annotation.')):
            if p=='Measure.Measure':
                return True
            if not c['Measure.Measure']:
                return False
            if p in ('Measure.TxInputPowerAvailable','Measure.TxInputPowerW','Measure.TxInputPowerdBm'):
                optical=c['Measure.RxTx']=='Tx' and 'W' in c['Measure.WaveformType']
                return optical and (p=='Measure.TxInputPowerAvailable' or c['Measure.TxInputPowerAvailable'])
            if p.startswith('Bathtub.') and p!='Bathtub.Measure':
                return c['Bathtub.Measure']
            if p.startswith('Annotation.') and p!='Annotation.Annotate':
                return (c['Annotation.Annotate']
                        and (p!='Annotation.LabelMeanLevels' or c['Annotation.MeanLevels'])
                        and (p!='Annotation.Contours.Which' or c['Annotation.Contours.Show']))
        return True

    def Error(self,message):
        device=getattr(self.configuration,'configurationReference','')
        error=ConfigurationError((device+': ' if device else '')+self.configuration.name+'.'+self.path+': '+message)
        error.field=self
        return error

    def Parse(self,value,entry=False):
        try:
            if self.type=='bool':
                if isinstance(value,bool):
                    result=value
                elif str(value).strip().lower() in ('true','false','0','1'):
                    result=str(value).strip().lower() in ('true','1')
                else:
                    raise ValueError('expected True or False (or 0/1)')
            elif self.type in ('float','int'):
                result=FromSI(str(value),self.units) if entry else float(value)
                if result is None or not math.isfinite(result):
                    raise ValueError('expected a finite '+self.type)
                if self.type=='int':
                    if int(result)!=result:
                        raise ValueError('expected an integer')
                    result=int(result)
            else:
                result=str(value)
            if self.choices and result not in self.choices:
                raise ValueError('allowed keywords: '+', '.join(self.choices))
            if self.path in ('Color','Annotation.Color'):
                from PIL import ImageColor
                ImageColor.getrgb(result)
            if self.path in ('UI','Rows','Columns','Alignment.Levels','EnhancedPrecision.FixedEnhancement',
                             'JitterNoise.MaxKernelPixels') and result<=0:
                raise ValueError('must be positive')
            if self.path=='Alignment.Levels' and result<2:
                raise ValueError('must be at least 2')
            if (self.path.endswith(('NoiseBandwidth','Resistance','Temperature_Kelvin','Risetime',
                                    'TrimLeftRight'))
                    or self.path in ('JitterNoise.JitterS','JitterNoise.JitterDeterministicPkS',
                                     'JitterNoise.Noise','Measure.TxInputPowerW','Lanes')) and result<0:
                raise ValueError('must not be negative')
            return result
        except ConfigurationError:
            raise
        except (ValueError,TypeError,OverflowError) as error:
            raise self.Error(str(error)) from error

    def Resolve(self,reference):
        context=getattr(self.configuration,'configurationVariables',None)
        variables=context() if context is not None else None
        if variables is None:
            raise self.Error('cannot resolve ='+reference+' without an owning project')
        visited=set()
        name=reference
        while True:
            if name in visited:
                raise self.Error('cyclic system-variable reference at ='+name)
            visited.add(name)
            if name not in variables.Names():
                raise self.Error('system variable ='+name+' does not exist')
            value=variables.VariableByName(name)['Value']
            if isinstance(value,str) and value.startswith('='):
                name=value[1:]
            else:
                return self.Parse(value)

    def Value(self):
        if self.reference and not self.Computed():
            return self.Resolve(self.reference)
        if self.path=='ShotNoise.MeanCurrent' and self.Computed():
            return getattr(self.leaf,'calculatedValue',self.leaf.value)
        if self.path=='JitterNoise.TotalNoise':
            return math.hypot(self.configuration['JitterNoise.Noise'],self.configuration['JitterNoise.ExternalNoise'])
        if self.path=='Measure.TxInputPowerdBm':
            watts=self.configuration['Measure.TxInputPowerW']
            return 10*math.log10(watts/1.e-3) if watts>0 else -3000.
        return self.leaf.value

    def EntryString(self):
        if self.reference and not self.Computed():
            return '='+self.reference
        value=self.Value() if self.Computed() else self.leaf.value
        if self.type=='float' and value is not None:
            return ToSI(value,self.units,round=12).strip()
        return '' if value is None else str(value)

    def Assign(self,value):
        if self.path=='ShotNoise.MeanCurrent' and self.Computed():
            self.leaf.calculatedValue=self.Parse(value)
            return
        derived=getattr(self.configuration,'configurationUpdating',False) or self.Computed()
        if isinstance(value,str) and value.startswith('=') and not derived:
            name=value[1:].strip()
            if not name or not name.isidentifier():
                raise self.Error('expected =system_variable_name')
            state=self.state.entries.setdefault(self.path,{'visible':False,'reference':''})
            state['reference']=name
            self.state.SetChanged()
            self.leaf.changed=True
            return
        if derived and self.reference:
            if not self.Computed():
                return
        elif self.reference:
            self.state.entries[self.path]['reference']=''
            self.state.SetChanged()
        self.leaf.dict['value']=str(value) if value is not None else None
        self.leaf.UpdateValue()
        self.leaf.changed=True

    def SetEntry(self,string):
        if self.Computed():
            raise self.Error('calculated fields cannot be edited or bound as inputs')
        string=string.strip()
        value=string
        if string.startswith('='):
            self.Resolve(string[1:].strip())
        else:
            value=self.Parse(string,entry=True)
        previous=[(leaf,leaf.dict['value'],leaf.value,getattr(leaf,'changed',False))
                  for _,leaf in _leaves(self.configuration)]
        state=copy.deepcopy(self.state.entries)
        changed=self.state.changed
        dimensions=None
        if self.configuration.name=='EyeDiagram' and self.path in ('UI','Rows','Columns') and not self.reference:
            c=self.configuration
            dimensions=(c['UI']*c['Columns']*c['ScaleX'],c['Rows']*c['ScaleY'])
        try:
            self.Assign(value)
            UpdateConfiguration(self.configuration,self.path)
            if dimensions is not None:
                c=self.configuration
                c.configurationUpdating=True
                try:
                    if self.path=='Rows':
                        c['ScaleY']=dimensions[1]/c['Rows']
                    else:
                        c['ScaleX']=dimensions[0]/(c['UI']*c['Columns'])
                finally:
                    c.configurationUpdating=False
        except (ValueError,TypeError,OverflowError,ZeroDivisionError) as error:
            self.state.entries=state
            self.state.changed=changed
            for leaf,raw,typed,wasChanged in previous:
                leaf.dict['value'],leaf.value,leaf.changed=raw,typed,wasChanged
            if isinstance(error,ConfigurationError):
                raise
            raise self.Error(str(error)) from error

    def Help(self):
        text=self.configuration.name+'.'+self.path+'\n'+self.description
        if self.choices:
            text+='\nAllowed keywords: '+', '.join(self.choices)
        try:
            computed=self.Computed()
        except ConfigurationError as error:
            return text+'\nInvalid: '+str(error)
        if computed:
            text+='\nCalculated result; display only.'
        else:
            text+='\nEnter a literal or =system_variable_name.'
        return text

    def DisplayString(self):
        try:
            value=self.Value()
            formatted=(ToSI(value,self.units).strip() if self.type=='float' and value is not None else str(value))
            if self.type=='file':
                formatted=os.path.basename(str(value).replace('\\','/'))
            return self.label+(' ='+self.reference+' ('+formatted+')' if self.reference and not self.Computed()
                               else ' '+formatted)
        except ConfigurationError as error:
            return self.label+' [Invalid: '+str(error)+']'


def ValidateConfiguration(configuration):
    for field in configuration.configurationFields.values():
        if not field.Active():
            continue
        if field.reference and field.Computed() and field.path!='ShotNoise.MeanCurrent':
            raise field.Error('calculated fields cannot be bound as inputs')
        if field.reference and not field.Computed():
            field.Parse(field.Value())


def OfferConfigurationVariable(field,entry,parent):
    if not entry.startswith('='):
        return
    name=entry[1:].strip()
    if not name.isidentifier():
        raise field.Error('expected =system_variable_name')
    variables=getattr(field.configuration,'configurationVariables',lambda:None)()
    if variables is None or name in variables.Names():
        return
    from SignalIntegrity.App.ProjectFile import VariableConfiguration
    from SignalIntegrity.App.VariablesDialog import OfferToAddSystemVariable
    variable=VariableConfiguration()
    variable['Name']=field.path.replace('.','_')
    variable['Description']=field.description
    variable['Type']='string' if field.type=='bool' else 'enum' if field.choices else field.type
    variable['Units']=field.units
    variable['Value']='='+name
    OfferToAddSystemVariable(variable,str(field.leaf.value),parent)


def BrowseConfigurationFile(field,entry,defaultFileParts,parent):
    from SignalIntegrity.App.FilePicker import AskOpenFileName
    from SignalIntegrity.App.Files import ConvertFileNameToRelativePath
    current=field.Resolve(entry[1:].strip()) if entry.startswith('=') else entry
    full=os.path.join(defaultFileParts.AbsoluteFilePath(),current) if current else ''
    filetypes=([('spectral density',('.txt','.csv','.json'))] if field.path=='SpectralDensityFile.FileName'
               else [('waveforms',('.txt','.trc'))])
    filename=AskOpenFileName(parent=parent,filetypes=filetypes+[('all','.*')],
                             initialdir=os.path.dirname(full) if full else defaultFileParts.AbsoluteFilePath(),
                             initialfile=os.path.basename(full))
    return ConvertFileNameToRelativePath(filename) if filename and not isinstance(filename,tuple) else ''


def UpdateConfiguration(configuration,path=None):
    """Update derived representations without replacing authored bindings."""
    c=configuration
    c.configurationUpdating=True
    try:
        if c.name=='EyeDiagram':
            if c.configurationFields['JitterNoise.TotalNoise'].Active():
                c['JitterNoise.TotalNoise']=math.hypot(c['JitterNoise.Noise'],c['JitterNoise.ExternalNoise'])
            if c.configurationFields['Measure.TxInputPowerdBm'].Active():
                watts=c['Measure.TxInputPowerW']
                c['Measure.TxInputPowerdBm']=10*math.log10(watts/1.e-3) if watts>0 else -3000.
            return
        if not c['Enable'] or c['Type'] not in ('WhiteNoise','Johnson'):
            return
        from SignalIntegrity.Lib.FrequencyDomain.DFTUtilities import DFTUtilities
        kind='Johnson' if c['Type']=='Johnson' else c['WhiteNoise.WhiteNoiseType']
        noise=c['WhiteNoise']
        voltage=c.name!='CurrentNoise'
        modes={'dBm/Hz':'NoisedBmPerHz',
               'V/sqrt(Hz)' if voltage else 'A/sqrt(Hz)':'VPerRootHz' if voltage else 'APerRootHz',
               'V^2/GHz' if voltage else 'A^2/GHz':'VSquaredPerGHz' if voltage else 'ASquaredPerGHz',
               'Vrms' if voltage else 'Arms':'VRms' if voltage else 'ARms'}
        source=next((mode for mode,key in modes.items() if path=='WhiteNoise.'+key),kind)
        bw=noise['NoiseBandwidth']
        if source in modes:
            value=noise[modes[source]]
        elif voltage and source in ('ENOB','COM TX','Johnson'):
            density=noise['Johnson'].NoiseDensity() if source=='Johnson' else noise.NoiseDensity()
            source='V/sqrt(Hz)'
            value=density
        else:
            return
        for target,key in modes.items():
            if target==source or (('rms' in target.lower() or 'rms' in source.lower()) and (bw is None or bw<=0)):
                continue
            c['WhiteNoise.'+key]=DFTUtilities.ConvertSpectralDensity(
                value,source,target,bw=bw,reference='voltage' if voltage else 'current')
        if voltage and bw is not None and bw>0 and noise['SNR.Vpp']>0:
            rms=DFTUtilities.ConvertSpectralDensity(value,source,'Vrms',bw=bw,reference='voltage')
            if rms<=0:
                return
            vpp=noise['SNR.Vpp']
            snr=20*math.log10(vpp/(2*math.sqrt(2)*rms))
            c['WhiteNoise.SNR.ENOB.ENOB']=(snr-1.76)/6.02
            if noise['SNR.COM_TX.h0']>0:
                c['WhiteNoise.SNR.COM_TX.SNRdB']=20*math.log10(noise['SNR.COM_TX.h0']*vpp/(2*rms))
    except ConfigurationError:
        raise
    except (ValueError,TypeError,OverflowError,ZeroDivisionError) as error:
        raise c.configurationFields[path or 'Type'].Error(str(error)) from error
    finally:
        c.configurationUpdating=False
