'''
Created on Oct 15, 2015

@author: peterp
'''

from PartProperty import *
from PartPicture import *

class Device(object):
    def __init__(self,propertiesList,partPicture):
        if propertiesList==None:
            propertiesList=[]
        self.propertiesList=propertiesList
        self.partPicture=partPicture
    def DrawDevice(self,canvas,grid,x,y):
        self.partPicture.DrawDevice(canvas,grid,(x,y))
    def IsAt(self,coord):
        return self.partPicture.IsAt(coord)
    def WhereInPart(self,coord):
        return self.partPicture.WhereInPart(coord)
    def PartPropertyByName(self,name):
        for partProperty in self.propertiesList:
            if partProperty.description == name:
                return partProperty
        return None
    def AddPartProperty(self,PartProperty):
        self.propertiesList=self.propertiesList+[PartProperty]
    def __getitem__(self,item):
        return self.PartPropertyByName(item)
    def NetListLine(self):
        return 'device '+str(self['name'].value)+' '+str(self['Ports'].value)

class DeviceFile(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' file '+self[PartPropertyFileName().description].value

class DeviceResistor(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' r '+self[PartPropertyResistance().description].value

class DeviceCapacitor(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' c '+self[PartPropertyCapacitance().description].value

class DeviceInductor(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' l '+self[PartPropertyInductance().description].value

class DeviceMutual(Device):
    def __init__(self,propertiesList,partPicture):
        Device.__init__(self,propertiesList,partPicture)
    def NetListLine(self):
        return Device.NetListLine(self)+' m '+self[PartPropertyInductance().description].value

class Port(Device):
    def __init__(self,portNumber):
        Device.__init__(self,[PartPropertyPartName('Port'),PartPropertyDescription('Port'),PartPropertyPorts(1),PartProperty(keyword='',description='Port Number',value=portNumber)],partPicture=PartPicturePort((0,0),portNumber))
    def NetListLine(self):
        return 'port '+str(self['Port Number'].value)+' '

DeviceList = [
              DeviceFile([PartPropertyCategory('Files'),PartPropertyPartName('File'),PartPropertyDescription('One\ Port\ File'),PartPropertyPorts(1),PartPropertyFileName()],PartPictureOnePort()),
              DeviceFile([PartPropertyCategory('Files'),PartPropertyPartName('File'),PartPropertyDescription('Two\ Port\ File'),PartPropertyPorts(2),PartPropertyFileName()],PartPictureTwoPort()),
              DeviceFile([PartPropertyCategory('Files'),PartPropertyPartName('File'),PartPropertyDescription('Three\ Port\ File'),PartPropertyPorts(3),PartPropertyFileName()],PartPictureThreePort()),
              DeviceFile([PartPropertyCategory('Files'),PartPropertyPartName('File'),PartPropertyDescription('Four\ Port\ File'),PartPropertyPorts(4),PartPropertyFileName()],PartPictureFourPort()),
              DeviceResistor([PartPropertyCategory('Resistors'),PartPropertyDescription('One\ Port\ Resistor\ to\ Ground'),PartPropertyPartName('Resistor'),PartPropertyPorts(1),PartPropertyResistance()],PartPictureOnePort()),
              DeviceResistor([PartPropertyCategory('Resistors'),PartPropertyPartName('Resistor'),PartPropertyDescription('Two\ Port\ Resistor'),PartPropertyPorts(2),PartPropertyResistance()],PartPictureTwoPort()),
              DeviceCapacitor([PartPropertyCategory('Capacitors'),PartPropertyPartName('Capacitor'),PartPropertyDescription('One\ Port\ Capacitor\ to\ Ground'),PartPropertyPorts(1),PartPropertyCapacitance()],PartPictureOnePort()),
              DeviceCapacitor([PartPropertyCategory('Capacitors'),PartPropertyPartName('Capacitor'),PartPropertyDescription('Two\ Port\ Capacitor'),PartPropertyPorts(2),PartPropertyCapacitance()],PartPictureCapacitorTwoPort()),
              DeviceInductor([PartPropertyCategory('Inductors'),PartPropertyPartName('Inductor'),PartPropertyDescription('One\ Port\ Inductor\ to\ Ground'),PartPropertyPorts(1),PartPropertyInductance()],PartPictureOnePort()),
              DeviceInductor([PartPropertyCategory('Inductors'),PartPropertyPartName('Inductor'),PartPropertyDescription('Two\ Port\ Inductor'),PartPropertyPorts(2),PartPropertyInductance()],PartPictureTwoPort()),
              Device([PartPropertyCategory('Inductors'),PartPropertyPartName('Mutual'),PartPropertyDescription('Four\ Port\ Mutual\ Inductance'),PartPropertyPorts(1),PartPropertyInductance()],PartPictureFourPort())
              ]
