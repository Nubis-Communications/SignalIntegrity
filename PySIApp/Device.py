'''
Created on Oct 15, 2015

@author: peterp
'''
import xml.etree.ElementTree as et

from PartProperty import *
from PartPicture import *

class Device(object):
    def __init__(self,propertiesList,partPicture):
        if propertiesList==None:
            propertiesList=[]
        self.propertiesList=propertiesList
        self.partPicture=partPicture
    def DrawDevice(self,canvas,grid,x,y):
        self.CreateVisiblePropertiesList()
        self.partPicture.current.DrawDevice(canvas,grid,(x,y))
    def IsAt(self,coord):
        return self.partPicture.current.IsAt(coord)
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
    def NetListLine(self):
        return 'device '+str(self[PartPropertyReferenceDesignator().propertyName].value)+' '+str(self['ports'].value)
    def PinCoordinates(self):
        return self.partPicture.current.PinCoordinates()
    def CreateVisiblePropertiesList(self):
        visiblePartPropertyList=[]
        for partProperty in self.propertiesList:
            if partProperty.visible:
                value = str(partProperty.value)
                if partProperty.propertyName == 'filename' or partProperty.propertyName == 'waveformfilename':
                    value = value.split('/')[-1]
                visiblePartPropertyList.append(value)
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
        self.result=eval(className).__new__(eval(className))
        Device.__init__(self.result,propertiesList,partPicture)

class DeviceFile(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Files'),PartPropertyPartName('File'),PartPropertyFileName()]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' file '+self[PartPropertyFileName().propertyName].value

class DeviceResistor(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Resistors'),PartPropertyPartName('Resistor'),PartPropertyResistance()]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' R '+self[PartPropertyResistance().propertyName].value

class DeviceCapacitor(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Capacitors'),PartPropertyPartName('Capacitor'),PartPropertyCapacitance()]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' C '+self[PartPropertyCapacitance().propertyName].value

class DeviceInductor(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Inductors'),PartPropertyPartName('Inductor'),PartPropertyPorts(1)]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' L '+self[PartPropertyInductance().propertyName].value

class DeviceMutual(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Inductors'),PartPropertyPartName('Mutual'),PartPropertyPorts(4),PartPropertyInductance()]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' M '+self[PartPropertyInductance().propertyName].value

class Port(Device):
    def __init__(self,portNumber):
        Device.__init__(self,[PartPropertyPartName('Port'),PartPropertyDescription('Port'),PartPropertyPorts(1),PartProperty('portnumber',keyword='',description='Port Number',value=portNumber,visible=True)],partPicture=PartPictureVariablePort())
    def NetListLine(self):
        return 'port '+str(self['portnumber'].value)

class DeviceGround(Device):
    def __init__(self):
        Device.__init__(self,[PartPropertyCategory('Miscellaneous'),PartPropertyPartName('Ground'),PartPropertyDescription('Ground'),PartPropertyPorts(1)],partPicture=PartPictureVariableGround())
    def NetListLine(self):
        return Device.NetListLine(self)+' ground'

class DeviceVoltageSource(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Miscellaneous'),PartPropertyPartName('Voltage Source'),PartPropertyWaveformFileName()]+propertiesList,partPicture)
    def NetListLine(self):
        return 'voltagesource '+str(self[PartPropertyReferenceDesignator().propertyName].value)+' '+str(self['ports'].value)

class DeviceCurrentSource(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Miscellaneous'),PartPropertyPartName('Current Source'),PartPropertyWaveformFileName()]+propertiesList,partPicture)
    def NetListLine(self):
        return 'currentsource '+str(self[PartPropertyReferenceDesignator().propertyName].value)+' '+str(self['ports'].value)

class DeviceMeasurement(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,propertiesList,partPicture)
    def NetListLine(self):
        return 'meas'

class DeviceOutput(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,propertiesList,partPicture)
    def NetListLine(self):
        return 'output'

class DeviceMixedModeConverter(Device):
    def __init__(self):
        Device.__init__(self,[PartPropertyCategory('Miscellaneous'),PartPropertyPartName('Mixed Mode Converter'),PartPropertyDescription('Mixed\ Mode\ Converter'),PartPropertyPorts(4)],PartPictureVariableMixedModeConverter())
    def NetListLine(self):
        return Device.NetListLine(self)+' mixedmode'

DeviceList = [
              DeviceFile([PartPropertyDescription('One\ Port\ File'),PartPropertyPorts(1)],PartPictureVariableOnePort()),
              DeviceFile([PartPropertyDescription('Two\ Port\ File'),PartPropertyPorts(2)],PartPictureVariableTwoPort()),
              DeviceFile([PartPropertyDescription('Three\ Port\ File'),PartPropertyPorts(3)],PartPictureVariableThreePort()),
              DeviceFile([PartPropertyDescription('Four\ Port\ File'),PartPropertyPorts(4)],PartPictureVariableFourPort()),
              DeviceResistor([PartPropertyDescription('One\ Port\ Resistor\ to\ Ground'),PartPropertyPorts(1)],PartPictureVariableResistorOnePort()),
              DeviceResistor([PartPropertyDescription('Two\ Port\ Resistor'),PartPropertyPorts(2)],PartPictureVariableResistorTwoPort()),
              DeviceCapacitor([PartPropertyDescription('One\ Port\ Capacitor\ to\ Ground'),PartPropertyPorts(1)],PartPictureVariableOnePort()),
              DeviceCapacitor([PartPropertyDescription('Two\ Port\ Capacitor'),PartPropertyPorts(2)],PartPictureVariableCapacitorTwoPort()),
              DeviceInductor([PartPropertyDescription('One\ Port\ Inductor\ to\ Ground'),PartPropertyPorts(1)],PartPictureVariableOnePort()),
              DeviceInductor([PartPropertyDescription('Two\ Port\ Inductor'),PartPropertyPorts(2)],PartPictureVariableTwoPort()),
              DeviceMutual([PartPropertyDescription('Four\ Port\ Mutual\ Inductance')],PartPictureVariableFourPort()),
              DeviceGround(),
              DeviceVoltageSource([PartPropertyDescription('One\ Port\ Voltage\ Source'),PartPropertyPorts(1)],PartPictureVariableVoltageSourceOnePort()),
              DeviceVoltageSource([PartPropertyDescription('Two\ Port\ Voltage\ Source'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceTwoPort()),
              DeviceCurrentSource([PartPropertyDescription('One\ Port\ Current\ Source'),PartPropertyPorts(1)],PartPictureVariableCurrentSourceOnePort()),
              DeviceCurrentSource([PartPropertyDescription('Two\ Port\ Current\ Source'),PartPropertyPorts(2)],PartPictureVariableCurrentSourceTwoPort()),
              DeviceMeasurement([PartPropertyCategory('Probes'),PartPropertyPartName('Measure'),PartPropertyDescription('Measure')],PartPictureVariableProbe()),
              DeviceOutput([PartPropertyCategory('Probes'),PartPropertyPartName('Output'),PartPropertyDescription('Output')],PartPictureVariableProbe()),
              DeviceMixedModeConverter()
              ]
