"""
Device.py
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
from SignalIntegrity.App.PartProperty import *
from SignalIntegrity.App.PartPicture import *
from SignalIntegrity.App.DeviceNetListLine import DeviceNetListLine

import math

class Device(object):
    def __init__(self,netlist,propertiesList,partPicture):
        self.netlist=netlist
        if propertiesList==None:
            propertiesList=[]
        self.propertiesList=propertiesList
        self.partPicture=partPicture
        self.selected=False
        self.AddPartProperty(PartPropertyReferenceDesignator(''))
    def DrawDevice(self,canvas,grid,x,y,pinsConnectedList=None):
        self.CreateVisiblePropertiesList()
        self.partPicture.current.Selected(self.selected).DrawDevice(canvas,grid,(x,y),pinsConnectedList)
    def IsAt(self,coord,augmentor,distance):
        return self.partPicture.current.IsAt(coord,augmentor,distance)
    def IsIn(self,coord0,coord1,coord0Augmentor,coord1Augmentor):
        return self.partPicture.current.IsIn(coord0,coord1,coord0Augmentor,coord1Augmentor)
    def WhereInPart(self,coord):
        return self.partPicture.current.WhereInPart(coord)
    def PartPropertyByName(self,name):
        for partProperty in self.propertiesList:
            if partProperty['PropertyName'] == name:
                return partProperty
        return None
    def PartPropertyByKeyword(self,keyword):
        for partProperty in self.propertiesList:
            if partProperty['Keyword'] == keyword:
                return partProperty
        return None
    def AddPartProperty(self,PartProperty):
        if self[PartProperty['Keyword']] is None:
            self.propertiesList=self.propertiesList+[PartProperty]
    def __getitem__(self,item):
        return self.PartPropertyByKeyword(item)
    def __setitem__(self,item,value):
        for p in range(len(self.propertiesList)):
            if self.propertiesList[p]['Keyword'] == item:
                self.propertiesList[p]=value
                return
        raise ValueError
    def NetListLine(self):
        return self.netlist.NetListLine(self)
    def PinCoordinates(self):
        return self.partPicture.current.PinCoordinates()
    def CreateVisiblePropertiesList(self):
        visiblePartPropertyList=[]
        for partProperty in self.propertiesList:
            propertyString=partProperty.PropertyString(stype='attr')
            if propertyString != '':
                visiblePartPropertyList.append(propertyString)
        self.partPicture.current.InsertVisiblePartProperties(visiblePartPropertyList)
    def Waveform(self):
        import SignalIntegrity.Lib as si
        wfTypeProperty=self['wftype']
        if wfTypeProperty is None:
            waveform = None
        else:
            wfType=wfTypeProperty.GetValue()
            if wfType is None:
                waveform = None
            elif wfType=='file':
                fileName = self['wffile'].PropertyString(stype='raw')
                ext=str.lower(fileName).split('.')[-1]
                if ext == 'si':
                    from SignalIntegrity.App.SignalIntegrityAppHeadless import ProjectWaveform
                    waveform=ProjectWaveform(fileName,self['wfprojname'].GetValue())
                    if waveform is None:
                        raise si.SignalIntegrityExceptionWaveform('project file: '+fileName+' could not produce waveform: '+self['wfprojname'].GetValue())
                else:
                    waveform = si.td.wf.Waveform().ReadFromFile(fileName)
            elif wfType == 'step':
                amplitude=float(self['a'].GetValue())
                startTime=float(self['t0'].GetValue())
                risetime=float(self['rt'].GetValue())
                waveform = si.td.wf.StepWaveform(self.WaveformTimeDescriptor(),amplitude,startTime,risetime)
            elif wfType == 'pulse':
                amplitude=float(self['a'].GetValue())
                startTime=float(self['t0'].GetValue())
                pulseWidth=float(self['w'].GetValue())
                risetime=float(self['rt'].GetValue())
                waveform = si.td.wf.PulseWaveform(self.WaveformTimeDescriptor(),amplitude,startTime,pulseWidth,risetime)
            elif wfType == 'prbs':
                polynomial=int(self['prbs'].GetValue())
                bitrate=float(self['br'].GetValue())
                risetime=float(self['rt'].GetValue())
                amplitude=float(self['a'].GetValue())
                delay=float(self['t0'].GetValue())
                waveform = si.prbs.PseudoRandomWaveform(polynomial,bitrate,amplitude,risetime,delay,self.WaveformTimeDescriptor())
            elif wfType == 'clock':
                clockrate=float(self['f'].GetValue())
                risetime=float(self['rt'].GetValue())
                amplitude=float(self['a'].GetValue())
                delay=float(self['t0'].GetValue())
                waveform = si.prbs.ClockWaveform(clockrate,amplitude,risetime,delay,self.WaveformTimeDescriptor())
            elif wfType == 'sine':
                amplitude=float(self['a'].GetValue())
                frequency=float(self['f'].GetValue())
                phase=float(self['ph'].GetValue())
                waveform = si.td.wf.SineWaveform(self.WaveformTimeDescriptor(),amplitude,frequency,phase)
            elif wfType == 'noise':
                sigma=float(self['vrms'].GetValue())
                waveform = si.td.wf.NoiseWaveform(self.WaveformTimeDescriptor(),sigma)
        return waveform
    def WaveformTimeDescriptor(self):
        import SignalIntegrity as si
        Fs=float(self['fs'].GetValue())
        K=int(math.ceil(Fs*float(self['dur'].GetValue())))
        horOffset=float(self['ho'].GetValue())
        return si.td.wf.TimeDescriptor(horOffset,K,Fs)

class DeviceFromProject(object):
    def __init__(self,deviceProject):
        ports=None
        for partPropertyProject in deviceProject['PartProperties']:
            if partPropertyProject['Keyword'] == 'ports':
                ports=int(partPropertyProject['Value'])
                break
        className=deviceProject['ClassName']
        self.result=None
        if className=='DeviceFile':
            self.result=DeviceFile([PartPropertyDescription('Variable Port File'),PartPropertyPorts(ports,False)],PartPictureVariableSpecifiedPorts(ports))
        elif className=='DeviceUnknown':
            self.result=DeviceUnknown([PartPropertyDescription('Variable Port Unknown'),PartPropertyPorts(ports,False)],PartPictureVariableUnknown(ports))
        elif className=='DeviceSystem':
            self.result=DeviceSystem([PartPropertyDescription('Variable Port System'),PartPropertyPorts(ports,False)],PartPictureVariableSystem(ports))
        else:
            for device in DeviceList+DeviceListSystem+DeviceListUnknown:
                if (str(device.__class__).split('.')[-1].strip('\'>') == className):
                    devicePorts = device['ports']
                    if (devicePorts is None):
                        match=True
                    elif (devicePorts.GetValue() == ports):
                        match=True
                    else:
                        match=False
                    if match:
                        self.result=copy.deepcopy(device)
                        break
        if self.result is None:
            raise
        for partPropertyProject in deviceProject['PartProperties']:
            devicePartProperty=self.result[partPropertyProject['Keyword']]
            for propertyItemName in partPropertyProject.dict:
                if partPropertyProject.dict[propertyItemName].dict['write']:
                    devicePartProperty[propertyItemName]=partPropertyProject.GetValue(propertyItemName)
        partPictureList=self.result.partPicture.partPictureClassList
        self.result.partPicture=PartPictureFromProject(partPictureList,deviceProject['PartPicture'],ports).result

class DeviceFile(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(values=[('file',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Files'),PartPropertyPartName('File'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyFileName()]+propertiesList,partPicture)

class DeviceUnknown(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='unknown')
        Device.__init__(self,netlist,[PartPropertyCategory('Unknowns'),PartPropertyPartName('Unknown'),PartPropertyDefaultReferenceDesignator('U?')]+propertiesList,partPicture)

class DeviceSystem(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='system',showReference=False,showports=False,values=[('file',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Systems'),PartPropertyPartName('System'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyFileName()]+propertiesList,partPicture)

class DeviceResistor(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='R',values=[('r',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Resistors'),PartPropertyPartName('Resistor'),PartPropertyDefaultReferenceDesignator('R?'),PartPropertyResistance()]+propertiesList,partPicture)

class DeviceCapacitor(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='C',values=[('c',False),('esr',True),('df',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Capacitors'),PartPropertyPartName('Capacitor'),PartPropertyDefaultReferenceDesignator('C?'),PartPropertyCapacitance(),PartPropertyDissipationFactor(),PartPropertyESR()]+propertiesList,partPicture)

class DeviceInductor(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='L',values=[('l',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Inductors'),PartPropertyPartName('Inductor'),PartPropertyDefaultReferenceDesignator('L?'),PartPropertyInductance()]+propertiesList,partPicture)

class DeviceMutual(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='M',values=[('l',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Inductors'),PartPropertyPartName('Mutual'),PartPropertyDefaultReferenceDesignator('M?'),PartPropertyPorts(4),PartPropertyInductance(),PartPropertyDescription('Four Port Mutual Inductance')],partPicture=PartPictureVariableMutual())

class DeviceIdealTransformer(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='idealtransformer',values=[('tr',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Inductors'),PartPropertyPartName('IdealTransformer'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyPorts(4),PartPropertyTurnsRatio(),PartPropertyDescription('Four Port IdealTransformer')],partPicture=PartPictureVariableIdealTransformer())

class Port(Device):
    def __init__(self,portNumber=1):
        netlist=DeviceNetListLine(devicename='port',showReference=False,showports=False,values=[('pn',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Special'),PartPropertyPartName('Port'),PartPropertyDescription('Port'),PartPropertyPorts(1),PartPropertyPortNumber(portNumber)],partPicture=PartPictureVariablePort())

class DeviceGround(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='ground')
        Device.__init__(self,netlist,[PartPropertyCategory('Miscellaneous'),PartPropertyPartName('Ground'),PartPropertyDefaultReferenceDesignator('G?'),PartPropertyDescription('Ground'),PartPropertyPorts(1)],partPicture=PartPictureVariableGround())

class DeviceOpen(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='open')
        Device.__init__(self,netlist,[PartPropertyCategory('Miscellaneous'),PartPropertyPartName('Open'),PartPropertyDefaultReferenceDesignator('O?'),PartPropertyDescription('Open'),PartPropertyPorts(1)],partPicture=PartPictureVariableOpen())

class DeviceDirectionalCoupler(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='directionalcoupler')
        Device.__init__(self,netlist,[PartPropertyCategory('Miscellaneous'),PartPropertyPartName('Directional Coupler'),PartPropertyDefaultReferenceDesignator('D?')]+propertiesList,partPicture)    

class DeviceVoltageSource(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[PartPropertyCategory('Sources'),PartPropertyPartName('Voltage Source'),PartPropertyDefaultReferenceDesignator('VS?'),PartPropertyWaveformFileName(),PartPropertyWaveformType('file'),PartPropertyWaveformProjectName('')]+propertiesList,partPicture)

class DeviceVoltageStepGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[PartPropertyCategory('Generators'),PartPropertyPartName('Voltage Step Generator'),PartPropertyDefaultReferenceDesignator('VG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertyStartTime(),PartPropertyRisetime(),PartPropertySampleRate(),PartPropertyVoltageAmplitude(),PartPropertyWaveformType('step')]+propertiesList,partPicture)

class DeviceVoltagePulseGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[PartPropertyCategory('Generators'),PartPropertyPartName('Voltage Pulse Generator'),PartPropertyDefaultReferenceDesignator('VG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertyStartTime(),PartPropertyRisetime(),PartPropertyPulseWidth(),PartPropertySampleRate(),PartPropertyVoltageAmplitude(),PartPropertyWaveformType('pulse')]+propertiesList,partPicture)

class DeviceVoltagePRBSGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[PartPropertyCategory('Generators'),PartPropertyPartName('Voltage PRBS Generator'),PartPropertyDefaultReferenceDesignator('VG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertyStartTime(),PartPropertyBitRate(),PartPropertyRisetime(),PartPropertyPRBSPolynomial(),PartPropertySampleRate(),PartPropertyVoltageAmplitude(),PartPropertyWaveformType('prbs')]+propertiesList,partPicture)

class DeviceVoltageClockGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[PartPropertyCategory('Generators'),PartPropertyPartName('Voltage Clock Generator'),PartPropertyDefaultReferenceDesignator('VG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertyStartTime(),PartPropertyFrequency(),PartPropertyRisetime(),PartPropertySampleRate(),PartPropertyVoltageAmplitude(),PartPropertyWaveformType('clock')]+propertiesList,partPicture)

class DeviceVoltageSineGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[PartPropertyCategory('Generators'),PartPropertyPartName('Voltage Sine Generator'),PartPropertyDefaultReferenceDesignator('VG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertySampleRate(),PartPropertyVoltageAmplitude(),PartPropertyFrequency(),PartPropertyPhase(),PartPropertyWaveformType('sine')]+propertiesList,partPicture)

class DeviceCurrentSource(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='currentsource')
        Device.__init__(self,netlist,[PartPropertyCategory('Sources'),PartPropertyPartName('Current Source'),PartPropertyDefaultReferenceDesignator('CS?'),PartPropertyWaveformFileName(),PartPropertyWaveformType('file'),PartPropertyWaveformProjectName('')]+propertiesList,partPicture)

class DeviceCurrentStepGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='currentsource')
        Device.__init__(self,netlist,[PartPropertyCategory('Generators'),PartPropertyPartName('Current Step Generator'),PartPropertyDefaultReferenceDesignator('CG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertyStartTime(),PartPropertyRisetime(),PartPropertySampleRate(),PartPropertyCurrentAmplitude(),PartPropertyWaveformType('step')]+propertiesList,partPicture)

class DeviceCurrentPulseGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='currentsource')
        Device.__init__(self,netlist,[PartPropertyCategory('Generators'),PartPropertyPartName('Current Pulse Generator'),PartPropertyDefaultReferenceDesignator('CG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertyStartTime(),PartPropertyRisetime(),PartPropertyPulseWidth(),PartPropertySampleRate(),PartPropertyCurrentAmplitude(),PartPropertyWaveformType('pulse')]+propertiesList,partPicture)

class DeviceCurrentSineGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='currentsource')
        Device.__init__(self,netlist,[PartPropertyCategory('Generators'),PartPropertyPartName('Current Sine Generator'),PartPropertyDefaultReferenceDesignator('CG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertySampleRate(),PartPropertyCurrentAmplitude(),PartPropertyFrequency(),PartPropertyPhase(),PartPropertyWaveformType('sine')]+propertiesList,partPicture)

class DeviceMeasurement(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='meas',showReference=False,showports=False)
        Device.__init__(self,netlist,[PartPropertyCategory('Special'),PartPropertyPartName('Measure'),PartPropertyDefaultReferenceDesignator('VM?'),PartPropertyDescription('Measure'),PartPropertyWaveformFileName(),PartPropertyWaveformType('file'),PartPropertyWaveformProjectName('')],PartPictureVariableMeasureProbe())

class DeviceOutput(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='output',showReference=False,showports=False)
        Device.__init__(self,netlist,[PartPropertyCategory('Special'),PartPropertyPartName('Output'),PartPropertyDefaultReferenceDesignator('VO?'),PartPropertyDescription('Output'),
            PartPropertyVoltageGain(1.0),PartPropertyVoltageOffset(0.0),PartPropertyDelay(0.0)],PartPictureVariableProbe())
        self['gain']['Visible']=False
        self['offset']['Visible']=False
        self['td']['Visible']=False

class DeviceStim(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='stim',showReference=False,showports=False)
        Device.__init__(self,netlist,[PartPropertyCategory('Special'),PartPropertyPartName('Stim'),PartPropertyDefaultReferenceDesignator('M?'),PartPropertyWeight(1.),PartPropertyDescription('Stim')],PartPictureVariableStim())

class DevicePowerMixedModeConverter(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='mixedmode')
        Device.__init__(self,netlist,[PartPropertyCategory('Miscellaneous'),PartPropertyPartName('Power Mixed Mode Converter'),PartPropertyDefaultReferenceDesignator('MM?'),PartPropertyDescription('Power Mixed Mode Converter'),PartPropertyPorts(4)],PartPictureVariablePowerMixedModeConverter())

class DeviceVoltageMixedModeConverter(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='mixedmode voltage')
        Device.__init__(self,netlist,[PartPropertyCategory('Miscellaneous'),PartPropertyPartName('Voltage Mixed Mode Converter'),PartPropertyDefaultReferenceDesignator('MM?'),PartPropertyDescription('Voltage Mixed Mode Converter'),PartPropertyPorts(4)],PartPictureVariableVoltageMixedModeConverter())

class DeviceVoltageControlledVoltageSourceFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='voltagecontrolledvoltagesource',values=[('gain',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Dependent Sources'),PartPropertyPartName('VoltageControlledVoltageSource'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyVoltageGain(1.0)]+propertiesList,PartPictureVariableVoltageControlledVoltageSourceFourPort())

class DeviceVoltageAmplifierTwoPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='voltageamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),PartPropertyPartName('VoltageAmplifier'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyVoltageGain(1.0),PartPropertyInputImpedance(1e8),PartPropertyOutputImpedance(0.)]+propertiesList,PartPictureVariableVoltageAmplifierTwoPort())

class DeviceVoltageAmplifierFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='voltageamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),PartPropertyPartName('VoltageAmplifier'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyVoltageGain(1.0),PartPropertyInputImpedance(1e8),PartPropertyOutputImpedance(0.)]+propertiesList,PartPictureVariableVoltageAmplifierFourPort())

class DeviceOperationalAmplifier(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='opamp',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),PartPropertyPartName('OperationalAmplifier'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyVoltageGain(100e3),PartPropertyInputImpedance(1e8),PartPropertyOutputImpedance(0.)]+propertiesList,PartPictureVariableOperationalAmplifier())

class DeviceCurrentControlledCurrentSourceFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='currentcontrolledcurrentsource',values=[('gain',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Dependent Sources'),PartPropertyPartName('CurrentControlledCurrentSource'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyCurrentGain(1.0)]+propertiesList,PartPictureVariableCurrentControlledCurrentSourceFourPort())

class DeviceCurrentAmplifierTwoPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='currentamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),PartPropertyPartName('CurrentAmplifier'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyCurrentGain(1.0),PartPropertyInputImpedance(0.),PartPropertyOutputImpedance(1e8)]+propertiesList,PartPictureVariableCurrentAmplifierTwoPort())

class DeviceCurrentAmplifierFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='currentamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),PartPropertyPartName('CurrentAmplifier'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyCurrentGain(1.0),PartPropertyInputImpedance(0.),PartPropertyOutputImpedance(1e8)]+propertiesList,PartPictureVariableCurrentAmplifierFourPort())

class DeviceVoltageControlledCurrentSourceFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='voltagecontrolledcurrentsource',values=[('gain',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Dependent Sources'),PartPropertyPartName('VoltageControlledCurrentSource'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyTransconductance(1.0)]+propertiesList,PartPictureVariableVoltageControlledCurrentSourceFourPort())

class DeviceTransconductanceAmplifierTwoPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='transconductanceamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),PartPropertyPartName('TransconductanceAmplifier'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyTransconductance(1.0),PartPropertyInputImpedance(1e8),PartPropertyOutputImpedance(1e8)]+propertiesList,PartPictureVariableTransconductanceAmplifierTwoPort())

class DeviceTransconductanceAmplifierFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='transconductanceamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),PartPropertyPartName('TransconductanceAmplifier'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyTransconductance(1.0),PartPropertyInputImpedance(1e8),PartPropertyOutputImpedance(1e8)]+propertiesList,PartPictureVariableTransconductanceAmplifierFourPort())

class DeviceCurrentControlledVoltageSourceFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='currentcontrolledvoltagesource',values=[('gain',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Dependent Sources'),PartPropertyPartName('CurrentControlledVoltageSource'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyTransresistance(1.0)]+propertiesList,PartPictureVariableCurrentControlledVoltageSourceFourPort())

class DeviceTransresistanceAmplifierTwoPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='transresistanceamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),PartPropertyPartName('TransresistanceAmplifier'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyTransresistance(1.0),PartPropertyInputImpedance(0.),PartPropertyOutputImpedance(0.)]+propertiesList,PartPictureVariableTransresistanceAmplifierTwoPort())

class DeviceTransresistanceAmplifierFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='transresistanceamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),PartPropertyPartName('TransresistanceAmplifier'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyTransresistance(1.0),PartPropertyInputImpedance(0.),PartPropertyOutputImpedance(0.)]+propertiesList,PartPictureVariableTransresistanceAmplifierFourPort())

class DeviceTransmissionLine(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='tline',values=[('zc',True),('td',True)])        
        Device.__init__(self,netlist,[PartPropertyCategory('TransmissionLines'),PartPropertyPartName('TransmissionLine'),PartPropertyDefaultReferenceDesignator('T?'),PartPropertyDelay(),PartPropertyCharacteristicImpedance()]+propertiesList,partPicture)

class DeviceTelegrapherTwoPort(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='telegrapher',values=[('r',True),('rse',True),('l',True),('g',True),('c',True),('df',True),('sect',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('TransmissionLines'),
                              PartPropertyPartName('Telegrapher'),
                              PartPropertyDefaultReferenceDesignator('T?'),
                              PartPropertyResistance(resistance=0.0),
                              PartPropertyResistanceSkinEffect(),
                              PartPropertyInductance(),
                              PartPropertyConductance(),
                              PartPropertyCapacitance(),
                              PartPropertyDissipationFactor(),
                              PartPropertySections(sections=0)]+propertiesList,partPicture)

class DeviceTelegrapherFourPort(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='telegrapher',
            values=[('rp',True),('rsep',True),('lp',True),('gp',True),('cp',True),('dfp',True),
                    ('rn',True),('rsen',True),('ln',True),('gn',True),('cn',True),('dfn',True),
                    ('lm',True),('gm',True),('cm',True),('dfm',True),('sect',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('TransmissionLines'),
                              PartPropertyPartName('Telegrapher'),
                              PartPropertyDefaultReferenceDesignator('T?'),
                              PartPropertyResistance(keyword='rp',descriptionPrefix='positive ',resistance=0.0),
                              PartPropertyResistanceSkinEffect(keyword='rsep',descriptionPrefix='positive '),
                              PartPropertyInductance(keyword='lp',descriptionPrefix='positive '),
                              PartPropertyConductance(keyword='gp',descriptionPrefix='positive '),
                              PartPropertyCapacitance(keyword='cp',descriptionPrefix='positive '),
                              PartPropertyDissipationFactor(keyword='dfp',descriptionPrefix='positive '),
                              PartPropertyResistance(keyword='rn',descriptionPrefix='negative ',resistance=0.0),
                              PartPropertyResistanceSkinEffect(keyword='rsen',descriptionPrefix='negative '),
                              PartPropertyInductance(keyword='ln',descriptionPrefix='negative '),
                              PartPropertyConductance(keyword='gn',descriptionPrefix='negative '),
                              PartPropertyCapacitance(keyword='cn',descriptionPrefix='negative '),
                              PartPropertyDissipationFactor(keyword='dfn',descriptionPrefix='negative '),
                              PartPropertyConductance(keyword='gm',descriptionPrefix='mutual '),
                              PartPropertyInductance(keyword='lm',descriptionPrefix='mutual '),
                              PartPropertyCapacitance(keyword='cm',descriptionPrefix='mutual '),
                              PartPropertyDissipationFactor(keyword='dfm',descriptionPrefix='mutual '),
                              PartPropertySections(sections=0)]+propertiesList,partPicture)

class DeviceVoltageNoiseSource(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[PartPropertyCategory('Generators'),PartPropertyPartName('Voltage Noise Source'),PartPropertyDefaultReferenceDesignator('VG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertySampleRate(),PartPropertyVoltageRms(),PartPropertyWaveformType('noise')]+propertiesList,partPicture)

class DeviceVoltageOutputProbe(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='differentialvoltageoutput')
        Device.__init__(self,netlist,[PartPropertyCategory('Special'),PartPropertyPartName('DifferentialVoltageOutput'),PartPropertyDefaultReferenceDesignator('VO?'),PartPropertyDescription('Differential Voltage Probe'),PartPropertyPorts(2),
            PartPropertyVoltageGain(1.0),PartPropertyVoltageOffset(0.0),PartPropertyDelay(0.0)],PartPictureVariableVoltageProbe())
        self['gain']['Visible']=False
        self['offset']['Visible']=False
        self['td']['Visible']=False

class DeviceCurrentOutputProbe(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='currentoutput')
        Device.__init__(self,netlist,[PartPropertyCategory('Special'),PartPropertyPartName('CurrentOutput'),PartPropertyDefaultReferenceDesignator('VO?'),PartPropertyDescription('Current Probe'),PartPropertyPorts(2),
            PartPropertyTransresistance(1.0),PartPropertyVoltageOffset(0.0),PartPropertyDelay(0.0)],PartPictureVariableCurrentProbe())
        self['gain']['Visible']=False
        self['offset']['Visible']=False
        self['td']['Visible']=False

class DeviceNPNTransistor(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='npntransistor',values=[('gm',True),('rpi',True),('ro',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),PartPropertyPartName('NPN Transistor'),PartPropertyDefaultReferenceDesignator('Q?'),PartPropertyGm(200.0),PartPropertyRpi(200e3),PartPropertyOutputResistance(200e3),PartPropertyPorts(3)]+propertiesList,PartPictureVariableNPNTransister())


DeviceList = [
              DeviceFile([PartPropertyDescription('One Port File'),PartPropertyPorts(1)],PartPictureVariableSpecifiedPorts(1)),
              DeviceFile([PartPropertyDescription('Two Port File'),PartPropertyPorts(2)],PartPictureVariableSpecifiedPorts(2)),
              DeviceFile([PartPropertyDescription('Three Port File'),PartPropertyPorts(3)],PartPictureVariableSpecifiedPorts(3)),
              DeviceFile([PartPropertyDescription('Four Port File'),PartPropertyPorts(4)],PartPictureVariableSpecifiedPorts(4)),
              DeviceFile([PartPropertyDescription('Variable Port File'),PartPropertyPorts(4,False)],PartPictureVariableSpecifiedPorts()),
              DeviceResistor([PartPropertyDescription('One Port Resistor to Ground'),PartPropertyPorts(1)],PartPictureVariableResistorOnePort()),
              DeviceResistor([PartPropertyDescription('Two Port Resistor'),PartPropertyPorts(2)],PartPictureVariableResistorTwoPort()),
              DeviceCapacitor([PartPropertyDescription('One Port Capacitor to Ground'),PartPropertyPorts(1)],PartPictureVariableCapacitorOnePort()),
              DeviceCapacitor([PartPropertyDescription('Two Port Capacitor'),PartPropertyPorts(2)],PartPictureVariableCapacitorTwoPort()),
              DeviceInductor([PartPropertyDescription('Two Port Inductor'),PartPropertyPorts(2)],PartPictureVariableInductorTwoPort()),
              DeviceMutual(),
              DeviceIdealTransformer(),
              DeviceGround(),
              DeviceOpen(),
              DeviceDirectionalCoupler([PartPropertyDescription('Three Port Directional Coupler'),PartPropertyPorts(3)],PartPictureVariableDirectionalCouplerThreePort()),
              DeviceDirectionalCoupler([PartPropertyDescription('Four Port Directional Coupler'),PartPropertyPorts(4)],PartPictureVariableDirectionalCouplerFourPort()),
              DeviceTransmissionLine([PartPropertyDescription('Two Port Transmission Line'),PartPropertyPorts(2)],PartPictureVariableTransmissionLineTwoPort()),
              DeviceTransmissionLine([PartPropertyDescription('Four Port Transmission Line'),PartPropertyPorts(4)],PartPictureVariableTransmissionLineFourPort()),
              DeviceTelegrapherTwoPort([PartPropertyDescription('Two Port Telegrapher'),PartPropertyPorts(2)],PartPictureVariableTransmissionLineTwoPort()),
              DeviceTelegrapherFourPort([PartPropertyDescription('Four Port Telegrapher'),PartPropertyPorts(4)],PartPictureVariableTransmissionLineDifferential()),
              DeviceVoltageSource([PartPropertyDescription('One Port Voltage Source'),PartPropertyPorts(1)],PartPictureVariableVoltageSourceOnePort()),
              DeviceVoltageSource([PartPropertyDescription('Two Port Voltage Source'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceTwoPort()),
              DeviceVoltageNoiseSource([PartPropertyDescription('One Port Voltage Noise Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourceNoiseSourceOnePort()),
              DeviceVoltageNoiseSource([PartPropertyDescription('Two Port Voltage Noise Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceNoiseSourceTwoPort()),
              DeviceVoltageStepGenerator([PartPropertyDescription('One Port Voltage Step Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourceStepGeneratorOnePort()),
              DeviceVoltageStepGenerator([PartPropertyDescription('Two Port Voltage Step Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceStepGeneratorTwoPort()),
              DeviceVoltagePulseGenerator([PartPropertyDescription('One Port Voltage Pulse Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourcePulseGeneratorOnePort()),
              DeviceVoltagePulseGenerator([PartPropertyDescription('Two Port Voltage Pulse Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourcePulseGeneratorTwoPort()),
              DeviceVoltagePRBSGenerator([PartPropertyDescription('One Port Voltage PRBS Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourcePRBSGeneratorOnePort()),
              DeviceVoltagePRBSGenerator([PartPropertyDescription('Two Port Voltage PRBS Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourcePRBSGeneratorTwoPort()),
              DeviceVoltageClockGenerator([PartPropertyDescription('One Port Voltage Clock Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourceClockGeneratorOnePort()),
              DeviceVoltageClockGenerator([PartPropertyDescription('Two Port Voltage Clock Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceClockGeneratorTwoPort()),
              DeviceVoltageSineGenerator([PartPropertyDescription('One Port Voltage Sine Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourceSineGeneratorOnePort()),
              DeviceVoltageSineGenerator([PartPropertyDescription('Two Port Voltage Sine Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceSineGeneratorTwoPort()),
              DeviceCurrentSource([PartPropertyDescription('One Port Current Source'),PartPropertyPorts(1)],PartPictureVariableCurrentSourceOnePort()),
              DeviceCurrentSource([PartPropertyDescription('Two Port Current Source'),PartPropertyPorts(2)],PartPictureVariableCurrentSourceTwoPort()),
              DeviceCurrentStepGenerator([PartPropertyDescription('One Port Current Step Generator'),PartPropertyPorts(1)],PartPictureVariableCurrentSourceStepGeneratorOnePort()),
              DeviceCurrentStepGenerator([PartPropertyDescription('Two Port Current Step Generator'),PartPropertyPorts(2)],PartPictureVariableCurrentSourceStepGeneratorTwoPort()),
              DeviceCurrentPulseGenerator([PartPropertyDescription('One Port Current Pulse Generator'),PartPropertyPorts(1)],PartPictureVariableCurrentSourcePulseGeneratorOnePort()),
              DeviceCurrentPulseGenerator([PartPropertyDescription('Two Port Current Pulse Generator'),PartPropertyPorts(2)],PartPictureVariableCurrentSourcePulseGeneratorTwoPort()),
              DeviceCurrentSineGenerator([PartPropertyDescription('One Port Current Sine Generator'),PartPropertyPorts(1)],PartPictureVariableCurrentSourceSineGeneratorOnePort()),
              DeviceCurrentSineGenerator([PartPropertyDescription('Two Port Current Sine Generator'),PartPropertyPorts(2)],PartPictureVariableCurrentSourceSineGeneratorTwoPort()),
              Port(),
              DeviceMeasurement(),
              DeviceOutput(),
              DeviceStim(),
              DevicePowerMixedModeConverter(),
              DeviceVoltageMixedModeConverter(),
              DeviceVoltageControlledVoltageSourceFourPort([PartPropertyDescription('Four Port Voltage Controlled Voltage Source'),PartPropertyPorts(4)]),
              DeviceVoltageAmplifierTwoPort([PartPropertyDescription('Two Port Voltage Amplifier'),PartPropertyPorts(2)]),
              DeviceVoltageAmplifierFourPort([PartPropertyDescription('Four Port Voltage Amplifier'),PartPropertyPorts(4)]),
              DeviceOperationalAmplifier([PartPropertyDescription('Operational Amplifier'),PartPropertyPorts(3)]),
              DeviceCurrentControlledCurrentSourceFourPort([PartPropertyDescription('Four Port Current Controlled Current Source'),PartPropertyPorts(4)]),
              DeviceCurrentAmplifierTwoPort([PartPropertyDescription('Two Port Current Amplifier'),PartPropertyPorts(2)]),
              DeviceCurrentAmplifierFourPort([PartPropertyDescription('Four Port Current Amplifier'),PartPropertyPorts(4)]),
              DeviceVoltageControlledCurrentSourceFourPort([PartPropertyDescription('Four Port Voltage Controlled Current Source'),PartPropertyPorts(4)]),
              DeviceTransconductanceAmplifierTwoPort([PartPropertyDescription('Two Port Transconductance Amplifier'),PartPropertyPorts(2)]),
              DeviceTransconductanceAmplifierFourPort([PartPropertyDescription('Four Port Transconductance Amplifier'),PartPropertyPorts(4)]),
              DeviceCurrentControlledVoltageSourceFourPort([PartPropertyDescription('Four Port Current Controlled Voltage Source'),PartPropertyPorts(4)]),
              DeviceTransresistanceAmplifierTwoPort([PartPropertyDescription('Two Port Transresistance Amplifier'),PartPropertyPorts(2)]),
              DeviceTransresistanceAmplifierFourPort([PartPropertyDescription('Four Port Transresistance Amplifier'),PartPropertyPorts(4)]),
              DeviceCurrentOutputProbe(),
              DeviceVoltageOutputProbe(),
              #DeviceNPNTransistor([PartPropertyDescription('NPN Transistor')])
              ]

DeviceListUnknown = [
              DeviceUnknown([PartPropertyDescription('One Port Unknown'),PartPropertyPorts(1)],PartPictureVariableUnknown(1)),
              DeviceUnknown([PartPropertyDescription('Two Port Unknown'),PartPropertyPorts(2)],PartPictureVariableUnknown(2)),
              DeviceUnknown([PartPropertyDescription('Three Port Unknown'),PartPropertyPorts(3)],PartPictureVariableUnknown(3)),
              DeviceUnknown([PartPropertyDescription('Four Port Unknown'),PartPropertyPorts(4)],PartPictureVariableUnknown(4)),
              DeviceUnknown([PartPropertyDescription('Variable Port Unknown'),PartPropertyPorts(4,False)],PartPictureVariableUnknown()),
              ]

DeviceListSystem = [
              DeviceSystem([PartPropertyDescription('One Port System'),PartPropertyPorts(1)],PartPictureVariableSystem(1)),
              DeviceSystem([PartPropertyDescription('Two Port System'),PartPropertyPorts(2)],PartPictureVariableSystem(2)),
              DeviceSystem([PartPropertyDescription('Three Port System'),PartPropertyPorts(3)],PartPictureVariableSystem(3)),
              DeviceSystem([PartPropertyDescription('Four Port System'),PartPropertyPorts(4)],PartPictureVariableSystem(4)),
              DeviceSystem([PartPropertyDescription('Variable Port System'),PartPropertyPorts(4,False)],PartPictureVariableSystem()),
              ]
