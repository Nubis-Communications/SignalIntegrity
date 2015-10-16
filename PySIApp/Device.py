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
        self.partPicture.DrawDevice(canvas,grid,(x,y))
    def IsAt(self,coord):
        return self.partPicture.IsAt(coord)
    def WhereInPart(self,coord):
        return self.partPicture.WhereInPart(coord)
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
        return self.partPicture.PinCoordinates()
    def CreateVisiblePropertiesList(self):
        visiblePartPropertyList=[]
        for partProperty in self.propertiesList:
            if partProperty.visible:
                visiblePartPropertyList.append(str(partProperty.value))
        self.partPicture.InsertVisiblePartProperties(visiblePartPropertyList)
    def xml(self):
        dev = et.Element('device')
        props = [partProperty.xml() for partProperty in self.propertiesList]
        dev.extend(props)
        #et.SubElement(dev,self.partPicture)
        return dev

class DeviceFile(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Files'),PartPropertyPartName('File'),PartPropertyFileName()]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' file '+self[PartPropertyFileName().propertyName].value

class DeviceResistor(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Resistors'),PartPropertyPartName('Resistor'),PartPropertyResistance()]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' r '+self[PartPropertyResistance().propertyName].value

class DeviceCapacitor(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Capacitors'),PartPropertyPartName('Capacitor'),PartPropertyCapacitance()]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' c '+self[PartPropertyCapacitance().propertyName].value

class DeviceInductor(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Inductors'),PartPropertyPartName('Inductor'),PartPropertyPorts(1)]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' l '+self[PartPropertyInductance().propertyName].value

class DeviceMutual(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,[PartPropertyCategory('Inductors'),PartPropertyPartName('Mutual'),PartPropertyPorts(4),PartPropertyInductance()]+propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' m '+self[PartPropertyInductance().propertyName].value

class Port(Device):
    def __init__(self,portNumber):
        Device.__init__(self,[PartPropertyPartName('Port'),PartPropertyDescription('Port'),PartPropertyPorts(1),PartProperty('portnumber',keyword='',description='Port Number',value=portNumber)],partPicture=PartPicturePort((0,0),portNumber))
    def NetListLine(self):
        return 'port '+str(self['portnumber'].value)+' '

class DeviceGround(Device):
    def __init__(self):
        Device.__init__(self,[PartPropertyCategory('Miscellaneous'),PartPropertyPartName('Ground'),PartPropertyDescription('Ground'),PartPropertyPorts(1)],partPicture=PartPictureGround())
    def NetListLine(self):
        return Device.NetListLine(self)+' ground'

DeviceList = [
              DeviceFile([PartPropertyDescription('One\ Port\ File'),PartPropertyPorts(1)],PartPictureOnePort()),
              DeviceFile([PartPropertyDescription('Two\ Port\ File'),PartPropertyPorts(2)],PartPictureTwoPort()),
              DeviceFile([PartPropertyDescription('Three\ Port\ File'),PartPropertyPorts(3)],PartPictureThreePort()),
              DeviceFile([PartPropertyDescription('Four\ Port\ File'),PartPropertyPorts(4)],PartPictureFourPort()),
              DeviceResistor([PartPropertyDescription('One\ Port\ Resistor\ to\ Ground'),PartPropertyPorts(1)],PartPictureOnePort()),
              DeviceResistor([PartPropertyDescription('Two\ Port\ Resistor'),PartPropertyPorts(2)],PartPictureTwoPort()),
              DeviceCapacitor([PartPropertyDescription('One\ Port\ Capacitor\ to\ Ground'),PartPropertyPorts(1)],PartPictureOnePort()),
              DeviceCapacitor([PartPropertyDescription('Two\ Port\ Capacitor'),PartPropertyPorts(2)],PartPictureCapacitorTwoPort()),
              DeviceInductor([PartPropertyDescription('One\ Port\ Inductor\ to\ Ground'),PartPropertyPorts(1)],PartPictureOnePort()),
              DeviceInductor([PartPropertyDescription('Two\ Port\ Inductor'),PartPropertyPorts(2)],PartPictureTwoPort()),
              DeviceMutual([PartPropertyDescription('Four\ Port\ Mutual\ Inductance')],PartPictureFourPort()),
              DeviceGround()
              ]
