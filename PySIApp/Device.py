'''
Created on Oct 15, 2015

@author: peterp
'''
import xml.etree.ElementTree as et

from PartProperty import *
from PartPicture import *

import math

class Device(object):
    def __init__(self,propertiesList,partPicture):
        if propertiesList==None:
            propertiesList=[]
        self.propertiesList=propertiesList
        self.partPicture=partPicture
        self.selected=False
    def DrawDevice(self,canvas,grid,x,y,pinsConnectedList=None):
        self.CreateVisiblePropertiesList()
        self.partPicture.current.Selected(self.selected).DrawDevice(canvas,grid,(x,y),pinsConnectedList)
    def IsAt(self,coord):
        return self.partPicture.current.IsAt(coord)
    def IsIn(self,coord0,coord1):
        return self.partPicture.current.IsIn(coord0,coord1)
    def WhereInPart(self,coord):
        return self.partPicture.current.WhereInPart(coord)
    def PartPropertyByName(self,name):
        for partProperty in self.propertiesList:
            if partProperty.propertyName == name:
                return partProperty
        return None
    def AddPartProperty(self,PartProperty):
        self.propertiesList=self.propertiesList+[PartProperty]
    def __getitem__(self,item):
        return self.PartPropertyByName(item)
    def __setitem__(self,item,value):
        for p in range(len(self.propertiesList)):
            if self.propertiesList[p].propertyName == item:
                self.propertiesList[p]=value
                return
        raise ValueError
    def NetListLine(self):
        return 'device '+self[PartPropertyReferenceDesignator().propertyName].PropertyString(stype='raw')+' '+self['ports'].PropertyString(stype='raw')
    def PinCoordinates(self):
        return self.partPicture.current.PinCoordinates()
    def CreateVisiblePropertiesList(self):
        visiblePartPropertyList=[]
        for partProperty in self.propertiesList:
            propertyString=partProperty.PropertyString(stype='attr')
            if propertyString != '':
                visiblePartPropertyList.append(propertyString)
        self.partPicture.current.InsertVisiblePartProperties(visiblePartPropertyList)
    def xml(self):
        dev = et.Element('device')
        classNameElement = et.Element('class_name')
        classNameElement.text = self.__class__.__name__
        pprope = et.Element('part_properties')
        props = [partProperty.xml() for partProperty in self.propertiesList]
        pprope.extend(props)
        dev.extend([classNameElement,pprope,self.partPicture.xml()])
        return dev
    def Waveform(self):
        return None

class DeviceXMLClassFactory(object):
    def __init__(self,xml):
        propertiesList=[]
        partPicture=None
        className='Device'
        for child in xml:
            if child.tag == 'class_name':
                className=child.text
            if child.tag == 'part_properties':
                for partPropertyElement in child:
                    partProperty=PartPropertyXMLClassFactory(partPropertyElement).result
                    propertiesList.append(partProperty)
            elif child.tag == 'part_picture':
                partPicture=PartPictureXMLClassFactory(child).result
        try:
            self.result=eval(className).__new__(eval(className))
            Device.__init__(self.result,propertiesList,partPicture)
        except NameError:
            self.result=None

class DeviceFile(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Files'),PartPropertyPartName('File'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyFileName()]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' file '+self[PartPropertyFileName().propertyName].PropertyString(stype='raw')

class DeviceResistor(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Resistors'),PartPropertyPartName('Resistor'),PartPropertyDefaultReferenceDesignator('R?'),PartPropertyResistance()]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' R '+self[PartPropertyResistance().propertyName].PropertyString(stype='raw')

class DeviceCapacitor(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Capacitors'),PartPropertyPartName('Capacitor'),PartPropertyDefaultReferenceDesignator('C?'),PartPropertyCapacitance()]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' C '+self[PartPropertyCapacitance().propertyName].PropertyString(stype='raw')

class DeviceInductor(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Inductors'),PartPropertyPartName('Inductor'),PartPropertyDefaultReferenceDesignator('L?'),PartPropertyInductance()]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' L '+self[PartPropertyInductance().propertyName].PropertyString(stype='raw')

class DeviceMutual(Device):
    def __init__(self):
        Device.__init__(self,[PartPropertyCategory('Inductors'),PartPropertyPartName('Mutual'),PartPropertyDefaultReferenceDesignator('M?'),PartPropertyPorts(4),PartPropertyInductance(),PartPropertyDescription('Four Port Mutual Inductance')],partPicture=PartPictureVariableMutual())
    def NetListLine(self):
        return Device.NetListLine(self)+' M '+self[PartPropertyInductance().propertyName].PropertyString(stype='raw')

class DeviceIdealTransformer(Device):
    def __init__(self):
        Device.__init__(self,[PartPropertyCategory('Inductors'),PartPropertyPartName('IdealTransformer'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyPorts(4),PartPropertyTurnsRatio(),PartPropertyDescription('Four Port IdealTransformer')],partPicture=PartPictureVariableIdealTransformer())
    def NetListLine(self):
        return Device.NetListLine(self)+' idealtransformer '+self[PartPropertyTurnsRatio().propertyName].PropertyString(stype='raw')

class Port(Device):
    def __init__(self,portNumber):
        Device.__init__(self,[PartPropertyPartName('Port'),PartPropertyDescription('Port'),PartPropertyPorts(1),PartPropertyPortNumber(portNumber)],partPicture=PartPictureVariablePort())
    def NetListLine(self):
        return 'port '+str(self['portnumber'].PropertyString(stype='raw'))

class DeviceGround(Device):
    def __init__(self):
        Device.__init__(self,[PartPropertyCategory('Miscellaneous'),PartPropertyPartName('Ground'),PartPropertyDefaultReferenceDesignator('G?'),PartPropertyDescription('Ground'),PartPropertyPorts(1)],partPicture=PartPictureVariableGround())
    def NetListLine(self):
        return Device.NetListLine(self)+' ground'

class DeviceOpen(Device):
    def __init__(self):
        Device.__init__(self,[PartPropertyCategory('Miscellaneous'),PartPropertyPartName('Open'),PartPropertyDefaultReferenceDesignator('O?'),PartPropertyDescription('Open'),PartPropertyPorts(1)],partPicture=PartPictureVariableOpen())
    def NetListLine(self):
        return Device.NetListLine(self)+' open'

class DeviceVoltageSource(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Sources'),PartPropertyPartName('Voltage Source'),PartPropertyDefaultReferenceDesignator('VS?'),PartPropertyWaveformFileName()]+propertiesList,partPicture)
    def NetListLine(self):
        return 'voltagesource '+str(self[PartPropertyReferenceDesignator().propertyName].PropertyString(stype='raw'))+' '+str(self['ports'].PropertyString(stype='raw'))
    def Waveform(self):
        import SignalIntegrity as si
        fileName = self[PartPropertyWaveformFileName().propertyName].PropertyString(stype='raw')
        waveform = si.td.wf.Waveform().ReadFromFile(fileName)
        return waveform

class DeviceVoltageStepGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Generators'),PartPropertyPartName('Voltage Step Generator'),PartPropertyDefaultReferenceDesignator('VG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertyStartTime(),PartPropertySampleRate(),PartPropertyVoltageAmplitude()]+propertiesList,partPicture)
    def NetListLine(self):
        return 'voltagesource '+str(self[PartPropertyReferenceDesignator().propertyName].PropertyString(stype='raw'))+' '+str(self['ports'].PropertyString(stype='raw'))
    def Waveform(self):
        import SignalIntegrity as si
        Fs=float(self[PartPropertySampleRate().propertyName].GetValue())
        K=int(math.ceil(Fs*float(self[PartPropertyDuration().propertyName].GetValue())))
        horOffset=float(self[PartPropertyHorizontalOffset().propertyName].GetValue())
        amplitude=float(self[PartPropertyVoltageAmplitude().propertyName].GetValue())
        startTime=float(self[PartPropertyStartTime().propertyName].GetValue())
        waveform = si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(horOffset,K,Fs),amplitude,startTime)
        return waveform

class DeviceVoltagePulseGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Generators'),PartPropertyPartName('Voltage Pulse Generator'),PartPropertyDefaultReferenceDesignator('VG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertyStartTime(),PartPropertyPulseWidth(),PartPropertySampleRate(),PartPropertyVoltageAmplitude()]+propertiesList,partPicture)
    def NetListLine(self):
        return 'voltagesource '+str(self[PartPropertyReferenceDesignator().propertyName].PropertyString(stype='raw'))+' '+str(self['ports'].PropertyString(stype='raw'))
    def Waveform(self):
        import SignalIntegrity as si
        Fs=float(self[PartPropertySampleRate().propertyName].GetValue())
        K=int(math.ceil(Fs*float(self[PartPropertyDuration().propertyName].GetValue())))
        horOffset=float(self[PartPropertyHorizontalOffset().propertyName].GetValue())
        amplitude=float(self[PartPropertyVoltageAmplitude().propertyName].GetValue())
        startTime=float(self[PartPropertyStartTime().propertyName].GetValue())
        pulseWidth=float(self[PartPropertyPulseWidth().propertyName].GetValue())
        waveform = si.td.wf.PulseWaveform(si.td.wf.TimeDescriptor(horOffset,K,Fs),amplitude,startTime,pulseWidth)
        return waveform

class DeviceVoltageSineGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Generators'),PartPropertyPartName('Voltage Sine Generator'),PartPropertyDefaultReferenceDesignator('VG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertySampleRate(),PartPropertyVoltageAmplitude(),PartPropertyFrequency(),PartPropertyPhase()]+propertiesList,partPicture)
    def NetListLine(self):
        return 'voltagesource '+str(self[PartPropertyReferenceDesignator().propertyName].PropertyString(stype='raw'))+' '+str(self['ports'].PropertyString(stype='raw'))
    def Waveform(self):
        import SignalIntegrity as si
        Fs=float(self[PartPropertySampleRate().propertyName].GetValue())
        K=int(math.ceil(Fs*float(self[PartPropertyDuration().propertyName].GetValue())))
        horOffset=float(self[PartPropertyHorizontalOffset().propertyName].GetValue())
        amplitude=float(self[PartPropertyVoltageAmplitude().propertyName].GetValue())
        frequency=float(self[PartPropertyFrequency().propertyName].GetValue())
        phase=float(self[PartPropertyPhase().propertyName].GetValue())
        waveform = si.td.wf.SineWaveform(si.td.wf.TimeDescriptor(horOffset,K,Fs),amplitude,frequency,phase)
        return waveform

class DeviceCurrentSource(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Sources'),PartPropertyPartName('Current Source'),PartPropertyDefaultReferenceDesignator('CS?'),PartPropertyWaveformFileName()]+propertiesList,partPicture)
    def NetListLine(self):
        return 'currentsource '+str(self[PartPropertyReferenceDesignator().propertyName].PropertyString(stype='raw'))+' '+str(self['ports'].PropertyString(stype='raw'))


class DeviceCurrentStepGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Generators'),PartPropertyPartName('Current Step Generator'),PartPropertyDefaultReferenceDesignator('CG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertyStartTime(),PartPropertySampleRate(),PartPropertyCurrentAmplitude()]+propertiesList,partPicture)
    def NetListLine(self):
        return 'currentsource '+str(self[PartPropertyReferenceDesignator().propertyName].PropertyString(stype='raw'))+' '+str(self['ports'].PropertyString(stype='raw'))
    def Waveform(self):
        import SignalIntegrity as si
        Fs=float(self[PartPropertySampleRate().propertyName].GetValue())
        K=int(math.ceil(Fs*float(self[PartPropertyDuration().propertyName].GetValue())))
        horOffset=float(self[PartPropertyHorizontalOffset().propertyName].GetValue())
        amplitude=float(self[PartPropertyCurrentAmplitude().propertyName].GetValue())
        startTime=float(self[PartPropertyStartTime().propertyName].GetValue())
        waveform = si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(horOffset,K,Fs),amplitude,startTime)
        return waveform

class DeviceCurrentPulseGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Generators'),PartPropertyPartName('Current Pulse Generator'),PartPropertyDefaultReferenceDesignator('CG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertyStartTime(),PartPropertyPulseWidth(),PartPropertySampleRate(),PartPropertyCurrentAmplitude()]+propertiesList,partPicture)
    def NetListLine(self):
        return 'currentsource '+str(self[PartPropertyReferenceDesignator().propertyName].PropertyString(stype='raw'))+' '+str(self['ports'].PropertyString(stype='raw'))
    def Waveform(self):
        import SignalIntegrity as si
        Fs=float(self[PartPropertySampleRate().propertyName].GetValue())
        K=int(math.ceil(Fs*float(self[PartPropertyDuration().propertyName].GetValue())))
        horOffset=float(self[PartPropertyHorizontalOffset().propertyName].GetValue())
        amplitude=float(self[PartPropertyCurrentAmplitude().propertyName].GetValue())
        startTime=float(self[PartPropertyStartTime().propertyName].GetValue())
        pulseWidth=float(self[PartPropertyPulseWidth().propertyName].GetValue())
        waveform = si.td.wf.PulseWaveform(si.td.wf.TimeDescriptor(horOffset,K,Fs),amplitude,startTime,pulseWidth)
        return waveform

class DeviceCurrentSineGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Generators'),PartPropertyPartName('Current Sine Generator'),PartPropertyDefaultReferenceDesignator('CG?'),
        PartPropertyHorizontalOffset(),PartPropertyDuration(),PartPropertySampleRate(),PartPropertyCurrentAmplitude(),PartPropertyFrequency(),PartPropertyPhase()]+propertiesList,partPicture)
    def NetListLine(self):
        return 'currentsource '+str(self[PartPropertyReferenceDesignator().propertyName].PropertyString(stype='raw'))+' '+str(self['ports'].PropertyString(stype='raw'))
    def Waveform(self):
        import SignalIntegrity as si
        Fs=float(self[PartPropertySampleRate().propertyName].GetValue())
        K=int(math.ceil(Fs*float(self[PartPropertyDuration().propertyName].GetValue())))
        horOffset=float(self[PartPropertyHorizontalOffset().propertyName].GetValue())
        amplitude=float(self[PartPropertyCurrentAmplitude().propertyName].GetValue())
        frequency=float(self[PartPropertyFrequency().propertyName].GetValue())
        phase=float(self[PartPropertyPhase().propertyName].GetValue())
        waveform = si.td.wf.SineWaveform(si.td.wf.TimeDescriptor(horOffset,K,Fs),amplitude,frequency,phase)
        return waveform

class DeviceMeasurement(Device):
    def __init__(self):
        Device.__init__(self,[PartPropertyCategory('Probes'),PartPropertyPartName('Measure'),PartPropertyDefaultReferenceDesignator('VM?'),PartPropertyDescription('Measure')],PartPictureVariableProbe())
    def NetListLine(self):
        return 'meas'

class DeviceOutput(Device):
    def __init__(self):
        Device.__init__(self,[PartPropertyCategory('Probes'),PartPropertyPartName('Output'),PartPropertyDefaultReferenceDesignator('VO?'),PartPropertyDescription('Output'),
            PartPropertyVoltageGain(1.0),PartPropertyVoltageOffset(0.0),PartPropertyDelay(0.0)],PartPictureVariableProbe())
        self[PartPropertyVoltageGain().propertyName].visible=False
        self[PartPropertyVoltageOffset().propertyName].visible=False
        self[PartPropertyDelay().propertyName].visible=False
    def NetListLine(self):
        return 'output'

class DevicePowerMixedModeConverter(Device):
    def __init__(self):
        Device.__init__(self,[PartPropertyCategory('Miscellaneous'),PartPropertyPartName('Power Mixed Mode Converter'),PartPropertyDefaultReferenceDesignator('MM?'),PartPropertyDescription('Power Mixed Mode Converter'),PartPropertyPorts(4)],PartPictureVariablePowerMixedModeConverter())
    def NetListLine(self):
        return Device.NetListLine(self)+' mixedmode'

class DeviceVoltageMixedModeConverter(Device):
    def __init__(self):
        Device.__init__(self,[PartPropertyCategory('Miscellaneous'),PartPropertyPartName('Voltage Mixed Mode Converter'),PartPropertyDefaultReferenceDesignator('MM?'),PartPropertyDescription('Voltage Mixed Mode Converter'),PartPropertyPorts(4)],PartPictureVariableVoltageMixedModeConverter())
    def NetListLine(self):
        return Device.NetListLine(self)+' mixedmode voltage'

class DeviceVoltageControlledVoltageSourceFourPort(Device):
    def __init__(self,propertiesList):
        Device.__init__(self,[PartPropertyCategory('Dependent Sources'),PartPropertyPartName('VoltageControlledVoltageSource'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyVoltageGain(1.0)]+propertiesList,PartPictureVariableVoltageControlledVoltageSourceFourPort())
    def NetListLine(self):
        return Device.NetListLine(self)+' voltagecontrolledvoltagesource '+str(self[PartPropertyVoltageGain().propertyName].PropertyString(stype='raw'))

class DeviceVoltageAmplifierFourPort(Device):
    def __init__(self,propertiesList):
        Device.__init__(self,[PartPropertyCategory('Amplifiers'),PartPropertyPartName('VoltageAmplifier'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyVoltageGain(1.0),PartPropertyInputImpedance(1e8),PartPropertyOutputImpedance(0.)]+propertiesList,PartPictureVariableVoltageControlledVoltageSourceFourPort())
    def NetListLine(self):
        return Device.NetListLine(self)+' voltageamplifier '+self[PartPropertyVoltageGain().propertyName].NetListProperty()+' '+self[PartPropertyInputImpedance().propertyName].NetListProperty()+' '+self[PartPropertyOutputImpedance().propertyName].NetListProperty()

class DeviceCurrentControlledCurrentSourceFourPort(Device):
    def __init__(self,propertiesList):
        Device.__init__(self,[PartPropertyCategory('Dependent Sources'),PartPropertyPartName('CurrentControlledCurrentSource'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyCurrentGain(1.0)]+propertiesList,PartPictureVariableCurrentControlledCurrentSourceFourPort())
    def NetListLine(self):
        return Device.NetListLine(self)+' currentcontrolledcurrentsource '+str(self[PartPropertyCurrentGain().propertyName].PropertyString(stype='raw'))

class DeviceCurrentAmplifierFourPort(Device):
    def __init__(self,propertiesList):
        Device.__init__(self,[PartPropertyCategory('Amplifiers'),PartPropertyPartName('CurrentAmplifier'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyCurrentGain(1.0),PartPropertyInputImpedance(0.),PartPropertyOutputImpedance(1e8)]+propertiesList,PartPictureVariableCurrentControlledCurrentSourceFourPort())
    def NetListLine(self):
        return Device.NetListLine(self)+' currentamplifier '+self[PartPropertyCurrentGain().propertyName].NetListProperty()+' '+self[PartPropertyInputImpedance().propertyName].NetListProperty()+' '+self[PartPropertyOutputImpedance().propertyName].NetListProperty()

class DeviceVoltageControlledCurrentSourceFourPort(Device):
    def __init__(self,propertiesList):
        Device.__init__(self,[PartPropertyCategory('Dependent Sources'),PartPropertyPartName('VoltageControlledCurrentSource'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyTransconductance(1.0)]+propertiesList,PartPictureVariableVoltageControlledCurrentSourceFourPort())
    def NetListLine(self):
        return Device.NetListLine(self)+' voltagecontrolledcurrentsource '+str(self[PartPropertyTransconductance().propertyName].PropertyString(stype='raw'))

class DeviceTransconductanceAmplifierFourPort(Device):
    def __init__(self,propertiesList):
        Device.__init__(self,[PartPropertyCategory('Amplifiers'),PartPropertyPartName('TransconductanceAmplifier'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyTransconductance(1.0),PartPropertyInputImpedance(1e8),PartPropertyOutputImpedance(1e8)]+propertiesList,PartPictureVariableVoltageControlledCurrentSourceFourPort())
    def NetListLine(self):
        return Device.NetListLine(self)+' transconductanceamplifier '+self[PartPropertyTransconductance().propertyName].NetListProperty()+' '+self[PartPropertyInputImpedance().propertyName].NetListProperty()+' '+self[PartPropertyOutputImpedance().propertyName].NetListProperty()

class DeviceCurrentControlledVoltageSourceFourPort(Device):
    def __init__(self,propertiesList):
        Device.__init__(self,[PartPropertyCategory('Dependent Sources'),PartPropertyPartName('CurrentControlledVoltageSource'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyTransresistance(1.0)]+propertiesList,PartPictureVariableCurrentControlledVoltageSourceFourPort())
    def NetListLine(self):
        return Device.NetListLine(self)+' currentcontrolledvoltagesource '+str(self[PartPropertyTransresistance().propertyName].PropertyString(stype='raw'))

class DeviceTransresistanceAmplifierFourPort(Device):
    def __init__(self,propertiesList):
        Device.__init__(self,[PartPropertyCategory('Amplifiers'),PartPropertyPartName('TransresistanceAmplifier'),PartPropertyDefaultReferenceDesignator('D?'),PartPropertyTransresistance(1.0),PartPropertyInputImpedance(0.),PartPropertyOutputImpedance(0.)]+propertiesList,PartPictureVariableCurrentControlledVoltageSourceFourPort())
    def NetListLine(self):
        return Device.NetListLine(self)+' transresistanceamplifier '+self[PartPropertyTransresistance().propertyName].NetListProperty()+' '+self[PartPropertyInputImpedance().propertyName].NetListProperty()+' '+self[PartPropertyOutputImpedance().propertyName].NetListProperty()

class DeviceTransmissionLine(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('TransmissionLines'),PartPropertyPartName('TransmissionLine'),PartPropertyDefaultReferenceDesignator('T?'),PartPropertyDelay(),PartPropertyCharacteristicImpedance()]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' tline '+self[PartPropertyCharacteristicImpedance().propertyName].NetListProperty()+' '+self[PartPropertyDelay().propertyName].NetListProperty()

DeviceList = [
              DeviceFile([PartPropertyDescription('One Port File'),PartPropertyPorts(1)],PartPictureVariableOnePort()),
              DeviceFile([PartPropertyDescription('Two Port File'),PartPropertyPorts(2)],PartPictureVariableTwoPort()),
              DeviceFile([PartPropertyDescription('Three Port File'),PartPropertyPorts(3)],PartPictureVariableThreePort()),
              DeviceFile([PartPropertyDescription('Four Port File'),PartPropertyPorts(4)],PartPictureVariableFourPort()),
              DeviceResistor([PartPropertyDescription('One Port Resistor to Ground'),PartPropertyPorts(1)],PartPictureVariableResistorOnePort()),
              DeviceResistor([PartPropertyDescription('Two Port Resistor'),PartPropertyPorts(2)],PartPictureVariableResistorTwoPort()),
              DeviceCapacitor([PartPropertyDescription('One Port Capacitor to Ground'),PartPropertyPorts(1)],PartPictureVariableCapacitorOnePort()),
              DeviceCapacitor([PartPropertyDescription('Two Port Capacitor'),PartPropertyPorts(2)],PartPictureVariableCapacitorTwoPort()),
              DeviceInductor([PartPropertyDescription('Two Port Inductor'),PartPropertyPorts(2)],PartPictureVariableInductorTwoPort()),
              DeviceMutual(),
              DeviceIdealTransformer(),
              DeviceGround(),
              DeviceOpen(),
              DeviceTransmissionLine([PartPropertyDescription('Two Port Transmission Line'),PartPropertyPorts(2)],PartPictureVariableTransmissionLineTwoPort()),
              DeviceTransmissionLine([PartPropertyDescription('Four Port Transmission Line'),PartPropertyPorts(4)],PartPictureVariableTransmissionLineFourPort()),
              DeviceVoltageSource([PartPropertyDescription('One Port Voltage Source'),PartPropertyPorts(1)],PartPictureVariableVoltageSourceOnePort()),
              DeviceVoltageSource([PartPropertyDescription('Two Port Voltage Source'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceTwoPort()),
              DeviceVoltageStepGenerator([PartPropertyDescription('One Port Voltage Step Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourceStepGeneratorOnePort()),
              DeviceVoltageStepGenerator([PartPropertyDescription('Two Port Voltage Step Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceStepGeneratorTwoPort()),
              DeviceVoltagePulseGenerator([PartPropertyDescription('One Port Voltage Pulse Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourcePulseGeneratorOnePort()),
              DeviceVoltagePulseGenerator([PartPropertyDescription('Two Port Voltage Pulse Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourcePulseGeneratorTwoPort()),
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
              DeviceMeasurement(),
              DeviceOutput(),
              DevicePowerMixedModeConverter(),
              DeviceVoltageMixedModeConverter(),
              DeviceVoltageControlledVoltageSourceFourPort([PartPropertyDescription('Four Port Voltage Controlled Voltage Source'),PartPropertyPorts(4)]),
              DeviceVoltageAmplifierFourPort([PartPropertyDescription('Four Port Voltage Amplifier'),PartPropertyPorts(4)]),
              DeviceCurrentControlledCurrentSourceFourPort([PartPropertyDescription('Four Port Current Controlled Current Source'),PartPropertyPorts(4)]),
              DeviceCurrentAmplifierFourPort([PartPropertyDescription('Four Port Current Amplifier'),PartPropertyPorts(4)]),
              DeviceVoltageControlledCurrentSourceFourPort([PartPropertyDescription('Four Port Voltage Controlled Current Source'),PartPropertyPorts(4)]),
              DeviceTransconductanceAmplifierFourPort([PartPropertyDescription('Four Port Transconductance Amplifier'),PartPropertyPorts(4)]),
              DeviceCurrentControlledVoltageSourceFourPort([PartPropertyDescription('Four Port Current Controlled Voltage Source'),PartPropertyPorts(4)]),
              DeviceTransresistanceAmplifierFourPort([PartPropertyDescription('Four Port Transresistance Amplifier'),PartPropertyPorts(4)])
              ]
