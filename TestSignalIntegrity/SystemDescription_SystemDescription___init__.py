class SystemDescription(object):
    def __init__(self,sd=None):
        if not sd is None:
            self.Data = sd.Data
            self.m_UniqueDevice=sd.m_UniqueDevice
            self.m_UniqueNode=sd.m_UniqueNode
        else:
            self.Data = []
            self.m_UniqueDevice=UniqueNameFactory('#')
            self.m_UniqueNode=UniqueNameFactory('n')
    def __getitem__(self,item):
        return self.Data[item]
    def __len__(self):
        return len(self.Data)
    def AddDevice(self,Name,Ports,SParams=None,Type='device'):
        self.Data.append(Device(Name,Ports,Type))
        if isinstance(SParams,list):
            self.AssignSParameters(Name,SParams)
    def AssignM(self,DeviceN,DeviceP,MName):
        di = self.IndexOfDevice(DeviceN)
        self[di][DeviceP-1].M = MName
    def DeviceNames(self):
        return [self[d].Name for d in range(len(self))]
    def IndexOfDevice(self,DeviceName):
        return self.DeviceNames().index(DeviceName)
    def _InsertNodeName(self,DeviceName,Port,AName,BName):
        di = self.IndexOfDevice(DeviceName)
        self[di][Port-1].A = AName
        self[di][Port-1].B = BName
    def CheckConnections(self):
        if not all([self[d][p].IsConnected()
            for d in range(len(self)) for p in range(len(self[d]))]):
            raise PySIExceptionSystemDescription('unconnected device ports')
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
    def AssignSParameters(self,DeviceName,SParameters):
        di = self.IndexOfDevice(DeviceName)
        self[di].SParameters = SParameters
    def Print(self):
        print '\n','Device','Name','Port','Node','Name'
        for d in range(len(self)):
            print repr(d+1).rjust(6),
            self[d].Print(1)