class DeviceFactory(list):
...
    def MakeDevice(self,ports,argsList,f):
        self.dev=None
        if len(argsList) == 0:
            return False
        name=argsList[0].lower()
        argsList=argsList[1:]
        for device in self:
            if device.ports is not None:
                if isinstance(device.ports,int):
                    if device.ports != ports:
                        continue
                elif isinstance(device.ports,str):
                    if '-' in device.ports:
                        (minPort,maxPort) = device.ports.split('-')
                        if ports < int(minPort):
                            continue
                        if ports > int(maxPort):
                            continue
                    else:
                        acceptablePorts = device.ports.split(',')
                        if not any(ports == int(acceptablePort)
                                   for acceptablePort in acceptablePorts):
                            continue
            if device.devicename != name: continue
            # this is the device, try to make it
            if device.arginname:
                if len(argsList) > 0:
                    argsList=['']+argsList
            argsProvidedDict = {argsList[i].lower():argsList[i+1]
                                for i in range(0,len(argsList),2)}
            arg=copy.copy(device.defaults)
            arg.update(argsProvidedDict)
            self.dev=eval(device.func)
            self.frequencyDependent=device.frequencyDependent
            return True
        return False

