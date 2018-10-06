class SystemDescription(list):
...
    def AddDevice(self,Name,Ports,SParams=None,Type='device'):
        self.append(Device(Name,Ports,Type))
        if isinstance(SParams,list):
            self.AssignSParameters(Name,SParams)
...
    def ConnectDevicePort(self,FromN,FromP,ToN,ToP):
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
...
