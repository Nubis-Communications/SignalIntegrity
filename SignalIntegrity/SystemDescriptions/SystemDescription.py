'''
Constructs system descriptions
'''
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.
from SignalIntegrity.Devices import Tee
from SignalIntegrity.Devices import Thru
from Device import Device
from UniqueNameFactory import UniqueNameFactory
from SignalIntegrity.PySIException import PySIExceptionSystemDescription

## SystemDescription
#
# Allows the construction of system descriptions for use with all of the
# classes that solve schematics and netlists
#
# Often, this class will be used to construct the system description and
# then passed to another class for problem solution
#
# A system description is an array of devices, which in turn are an array
# of ports and port connections.
#
class SystemDescription(object):
    ## Constructor
    #
    # @param sd (optional, defaults to None) instance of class SystemDescription
    #
    # Initializes a system description
    def __init__(self,sd=None):
        if not sd is None:
            self.Data = sd.Data
            self.m_UniqueDevice=sd.m_UniqueDevice
            self.m_UniqueNode=sd.m_UniqueNode
        else:
            self.Data = []
            self.m_UniqueDevice=UniqueNameFactory('#')
            self.m_UniqueNode=UniqueNameFactory('n')
    ## overrides [item]
    #
    # @param item integer index of device in system
    # @return a device at the index provided
    def __getitem__(self,item):
        return self.Data[item]
    ## overrides len()
    #
    # returns the number of devices
    def __len__(self):
        return len(self.Data)
    ## Adds a device to the system
    #
    # @param Name string name of device to add
    # @param Ports integer number of ports in the device
    # @param SParams (optional) s-parameter matrix for device
    # @param Type type of device defaults to 'device'
    #
    # Adds a device to the system with the given name, s-parameters and number of ports
    # The type is always 'device' and should not be overridden except for one case where the device
    # being added is an 'unknown' to be solved for.
    def AddDevice(self,Name,Ports,SParams=None,Type='device'):
        # pragma: silent exclude
        if Name in self.DeviceNames():
            raise PySIExceptionSystemDescription(
                'duplicate device name: '+str(Name))
        # pragma: include
        self.Data.append(Device(Name,Ports,Type))
        if isinstance(SParams,list):
            self.AssignSParameters(Name,SParams)
    ## Assigns a stimulus to a device port
    #
    # @param DeviceN string name of device
    # @param DeviceP integer port number of device
    # @param MName string name of a stimulus
    #
    # Assigns a stimulus in name only as emanating from the device port specified
    def AssignM(self,DeviceN,DeviceP,MName):
        di = self.IndexOfDevice(DeviceN)
        self[di][DeviceP-1].M = MName
    ## Returns a list of device names in the system
    #
    # @return a list of the names of all of the devices in the system
    def DeviceNames(self):
        return [self[d].Name for d in range(len(self))]
    ## Returns the index of a named device in the system
    #
    # @param DeviceName string name of a device
    # @return integer index of the named device
    #
    # throws PySIExceptionSystemDescription if device not found
    def IndexOfDevice(self,DeviceName):
        # pragma: silent exclude
        try:
        # pragma: include outdent
            return self.DeviceNames().index(DeviceName)
        # pragma: silent exclude indent
        except ValueError:
            raise PySIExceptionSystemDescription(
                'no device named: '+str(DeviceName))
        # pragma: include
    def _InsertNodeName(self,DeviceName,Port,AName,BName):
        di = self.IndexOfDevice(DeviceName)
        self[di][Port-1].A = AName
        self[di][Port-1].B = BName
    ## Checks the validity of the connections in the system
    #
    # Checks that the system description for devices and connections
    #
    # Throws PySIExceptionSystemDescription if there are no devices or
    # if any of the devices have unconnected device ports 
    def CheckConnections(self):
        if len(self)==0:
            raise PySIExceptionSystemDescription('no devices')
        if not all([self[d][p].IsConnected()
            for d in range(len(self)) for p in range(len(self[d]))]):
            raise PySIExceptionSystemDescription('unconnected device ports')
    ## Connects one device port to another
    #
    # @param FromN string name of from device
    # @param FromP integer port number of from device
    # @param ToN string name of to device
    # @param ToP integer port number of to device
    #
    # Makes a connection from one device port to another.
    # It's okay if devices are already connected and multiple connections are
    # allowed and are handled properly.
    def ConnectDevicePort(self,FromN,FromP,ToN,ToP):
        # pragma: silent exclude
        try:
        # pragma: include outdent
            dfi = self.IndexOfDevice(FromN)
            dti = self.IndexOfDevice(ToN)
            if not self[dfi][FromP-1].IsConnected():
                if not self[dti][ToP-1].IsConnected():
                    uN1,uN2 = (self.m_UniqueNode.Name(),self.m_UniqueNode.Name())
                    self._InsertNodeName(FromN,FromP,uN2,uN1)
                    self._InsertNodeName(ToN,ToP,uN1,uN2)
                else:
                    self.ConnectDevicePort(ToN,ToP,FromN,FromP)
            else:
                TeeN = self.m_UniqueDevice.Name()
                self.AddDevice(TeeN,3)
                self.AssignSParameters(TeeN,Tee())
                self._InsertNodeName(TeeN,1,self[dfi][FromP-1].A,self[dfi][FromP-1].B)
                self._InsertNodeName(FromN,FromP,'','')
                self.ConnectDevicePort(FromN,FromP,TeeN,2)
                self.ConnectDevicePort(TeeN,3,ToN,ToP)
        # pragma: silent exclude indent
        except IndexError:
            raise PySIExceptionSystemDescription(
                'cannot connect device ports '+str(FromN)+' '+str(FromP)+' to '+
                str(ToN)+' '+str(ToP))
        # pragma: include
    ## Adds a system port at a specified device port
    #
    # @param DeviceName string name of device
    # @param DevicePort integer port number of device
    # @param SystemPort integer port number
    # @param AddThru boolean whether to force a thru between the system port and the device port.
    #
    # Adds a system port to a device port for the solutions of s-parameters or for deembedding.
    #
    # In the theory, sometimes it's necessary to add a thru between a system port and a device port.
    # But it turns out that this is only necessary when connecting a system port directly to a port
    # of an unknown device in a deembedding problem.  Although the ability to force the addition of
    # a thru is retained, the code actually checks for this situation and adds a thru automatically
    # so currently, there are no situations known where AddThru needs to be set True.
    #
    # @todo Consider removing the AddThru argument
    def AddPort(self,DeviceName,DevicePort,SystemPort,AddThru=False):
        PortName = 'P'+str(SystemPort)
        self.AddDevice(PortName,1,[[0.0]])
        self.AssignM(PortName,1,'m'+str(SystemPort))
        if not AddThru:
            AddThru = self[self.IndexOfDevice(DeviceName)].Type == 'unknown'
        if AddThru:
            thruName=self.m_UniqueDevice.Name()
            self.AddDevice(thruName,2,Thru())
            self.ConnectDevicePort(PortName,1,thruName,1)
            self.ConnectDevicePort(thruName,2,DeviceName,DevicePort)
        else:
            self.ConnectDevicePort(PortName,1,DeviceName,DevicePort)
    ## Assigns s-parameters to a device
    #
    # @param DeviceName string name of a device in the system
    # @param SParameters an s-parameter matrix
    #
    # Assigns the specified s-parameters to a device
    def AssignSParameters(self,DeviceName,SParameters):
        self[self.IndexOfDevice(DeviceName)].AssignSParameters(SParameters)
    ## Prints the system
    #
    # Prints out an ASCII description of the system
    def Print(self):
        print '\n','Device','Name','Port','Node','Name'
        for d in range(len(self)):
            print repr(d+1).rjust(6),
            self[d].Print(1)