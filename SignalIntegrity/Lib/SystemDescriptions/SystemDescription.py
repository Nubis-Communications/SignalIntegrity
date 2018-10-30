"""
SystemDescription.py
"""
from __future__ import print_function
from __future__ import absolute_import

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
from SignalIntegrity.Lib.Devices import Tee
from SignalIntegrity.Lib.Devices import Thru
from .Device import Device
from .UniqueNameFactory import UniqueNameFactory
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionSystemDescription

class SystemDescription(list):
    """Allows the construction of system descriptions for use with all of the
    classes that solve schematics and netlists

    Often, this class will be used to construct the system description and
    then passed to another class for problem solution

    A system description is fundamentally a list of devices, which in turn are lists
    of ports and port connections."""
    def __init__(self,sd=None):
        """Constructor
        @param sd (optional, defaults to None) instance of class SystemDescription
        Initializes a system description
        """
        if not sd is None:
            list.__init__(self,list(sd))
            self.m_UniqueDevice=sd.m_UniqueDevice
            self.m_UniqueNode=sd.m_UniqueNode
        else:
            list.__init__(self,[])
            self.m_UniqueDevice=UniqueNameFactory('#')
            self.m_UniqueNode=UniqueNameFactory('n')
    def AddDevice(self,Name,Ports,SParams=None,Type='device'):
        """Adds a device to the system
        @param Name string name of device to add
        @param Ports integer number of ports in the device
        @param SParams (optional) s-parameter matrix for device
        @param Type type of device defaults to 'device'
        Adds a device to the system with the given name, s-parameters and number of ports
        The type is always 'device' and should not be overridden except for one case where the device
        being added is an 'unknown' to be solved for."""
        # pragma: silent exclude
        if Name in self.DeviceNames():
            raise SignalIntegrityExceptionSystemDescription(
                'duplicate device name: '+str(Name))
        # pragma: include
        self.append(Device(Name,Ports,Type))
        if isinstance(SParams,list):
            self.AssignSParameters(Name,SParams)
    def AssignM(self,DeviceN,DeviceP,MName):
        """Assigns a stimulus to a device port
        @param DeviceN string name of device
        @param DeviceP integer port number of device
        @param MName string name of a stimulus
        Assigns a stimulus in name only as emanating from the device port specified
        """
        di = self.IndexOfDevice(DeviceN)
        self[di][DeviceP-1].M = MName
    def DeviceNames(self):
        """Returns a list of device names in the system
        @return a list of the names of all of the devices in the system
        """
        return [self[d].Name for d in range(len(self))]
    def IndexOfDevice(self,DeviceName):
        """Returns the index of a named device in the system
        @param DeviceName string name of a device
        @return integer index of the named device
        @throw SignalIntegrityExceptionSystemDescription if device not found
        """
        # pragma: silent exclude
        try:
        # pragma: include outdent
            return self.DeviceNames().index(DeviceName)
        # pragma: silent exclude indent
        except ValueError:
            raise SignalIntegrityExceptionSystemDescription(
                'no device named: '+str(DeviceName))
        # pragma: include
    def _InsertNodeName(self,DeviceName,Port,AName,BName):
        di = self.IndexOfDevice(DeviceName)
        self[di][Port-1].A = AName
        self[di][Port-1].B = BName
    def CheckConnections(self):
        """Checks the validity of the connections in the system
        @throw SignalIntegrityExceptionSystemDescription if there are no devices
        @throw SignalIntegrityExceptionSystemDescription if any of the devices have unconnected device ports 
        """
        if len(self)==0:
            raise SignalIntegrityExceptionSystemDescription('no devices')
        if not all([self[d][p].IsConnected()
            for d in range(len(self)) for p in range(len(self[d]))]):
            raise SignalIntegrityExceptionSystemDescription('unconnected device ports')
    def ConnectDevicePort(self,FromN,FromP,ToN,ToP):
        """Connects one device port to another
        @param FromN string name of from device
        @param FromP integer port number of from device
        @param ToN string name of to device
        @param ToP integer port number of to device
        Makes a connection from one device port to another.

        It's okay if devices are already connected and multiple connections are
        allowed and are handled properly.
        """
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
            raise SignalIntegrityExceptionSystemDescription(
                'cannot connect device ports '+str(FromN)+' '+str(FromP)+' to '+
                str(ToN)+' '+str(ToP))
        # pragma: include
    def AddPort(self,DeviceName,DevicePort,SystemPort,AddThru=False):
        """Adds a system port at a specified device port
        @param DeviceName string name of device
        @param DevicePort integer port number of device
        @param SystemPort integer port number
        @param AddThru boolean whether to force a thru between the system port and the device port.
        Adds a system port to a device port for the solutions of s-parameters or for deembedding.

        In the theory, sometimes it's necessary to add a thru between a system port and a device port.
        But it turns out that this is only necessary when connecting a system port directly to a port
        of an unknown device in a deembedding problem.  Although the ability to force the addition of
        a thru is retained, the code actually checks for this situation and adds a thru automatically
        so currently, there are no situations known where AddThru needs to be set True.

        @todo Consider removing the AddThru argument
        """
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
    def AssignSParameters(self,DeviceName,SParameters):
        """Assigns s-parameters to a device
        @param DeviceName string name of a device in the system
        @param SParameters an s-parameter matrix
        """
        self[self.IndexOfDevice(DeviceName)].AssignSParameters(SParameters)
    def Print(self):
        """Prints out an ASCII description of the system"""
        print('\n','Device','Name','Port','Node','Name')
        for d in range(len(self)):
            print(repr(d+1).rjust(6), end=' ')
            self[d].Print(1)
