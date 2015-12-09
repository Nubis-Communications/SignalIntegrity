from numpy import zeros
import copy

from SignalIntegrity.SParameters import File
from SignalIntegrity.SubCircuits import SubCircuit
from SignalIntegrity.Devices import *
from SignalIntegrity.SParameters.Devices import *
from SignalIntegrity.PySIException import PySIExceptionDeviceParser

class ParserDevice(object):
    def __init__(self,devicename,ports,arginname,defaults,frequencyDependent,func):
        self.devicename=devicename
        self.ports=ports
        self.arginname=arginname
        self.defaults=defaults
        self.frequencyDependent=frequencyDependent
        self.func=func

class DeviceFactory(object):
    def __init__(self):
        self.deviceList=[
        ParserDevice('file',None,True,{'':None},True,"File(arg['']).Resample(f)"),
        ParserDevice('c',1,True,{'':None},True,"TerminationC(f,float(arg['']))"),
        ParserDevice('c',2,True,{'':None},True,"SeriesC(f,float(arg['']))"),
        ParserDevice('l',1,True,{'':None},True,"TerminationL(f,float(arg['']))"),
        ParserDevice('l',2,True,{'':None},True,"SeriesL(f,float(arg['']))"),
        ParserDevice('r',1,True,{'':None},False,"TerminationZ(float(arg['']))"),
        ParserDevice('r',2,True,{'':None},False,"SeriesZ(float(arg['']))"),
        ParserDevice('shunt','2-4',True,{'':None},False,"ShuntZ(ports,float(arg['']))"),
        ParserDevice('m',4,True,{'':None},True,"Mutual(f,float(arg['']))"),
        ParserDevice('ground',1,False,{},False,"Ground()"),
        ParserDevice('open',1,False,{},False,"Open()"),
        ParserDevice('thru',2,False,{},False,"Thru()"),
        ParserDevice('termination',None,False,{},False,"zeros(shape=(ports,ports)).tolist()"),
        ParserDevice('tee',None,False,{},False,"Tee(ports)"),
        ParserDevice('mixedmode',4,True,{'':'power'},False,"(MixedModeConverterVoltage() if arg[''] == 'voltage' else MixedModeConverter())"),
        ParserDevice('idealtransformer',4,True,{'':1.},False,"IdealTransformer(float(arg['']))"),
        ParserDevice('voltagecontrolledvoltagesource',4,True,{'':None},False,"VoltageControlledVoltageSource(float(arg['']))"),
        ParserDevice('currentcontrolledcurrentsource',4,True,{'':None},False,"CurrentControlledCurrentSource(float(arg['']))"),
        ParserDevice('currentcontrolledvoltagesource',4,True,{'':None},False,"CurrentControlledVoltageSource(float(arg['']))"),
        ParserDevice('voltagecontrolledcurrentsource',4,True,{'':None},False,"VoltageControlledCurrentSource(float(arg['']))"),
        ParserDevice('voltageamplifier','2-4',False,{'gain':None,'zo':0,'zi':1e8,'z0':50.},False,"VoltageAmplifier(ports,float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('currentamplifier','2-4',False,{'gain':None,'zo':1e8,'zi':0,'z0':50.},False,"CurrentAmplifier(ports,float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('transresistanceamplifier','2-4',False,{'gain':None,'zo':0.,'zi':0.,'z0':50.},False,"TransresistanceAmplifier(ports,float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('transconductanceamplifier','2-4',False,{'gain':None,'zo':1e8,'zi':1e8,'z0':50.},False,"TransconductanceAmplifier(ports,float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('tline','2,4',False,{'zc':50.,'td':0.},True,"TLine(f,ports,float(arg['zc']),float(arg['td']))"),
        ParserDevice('telegrapher',2,False,{'r':0.,'l':0.,'c':0.,'g':0.,'z0':50.,'sect':1},
                     True,"ApproximateTwoPortTLine(f, float(arg['r']),float(arg['l']),float(arg['g']),float(arg['c']),float(arg['z0']),int(arg['sect']))"),
        ParserDevice('telegrapher',4,False,{'rp':0.,'lp':0.,'cp':0.,'gp':0.,'rn':0.,'ln':0.,'cn':0.,'gn':0.,'lm':0.,'cm':0.,'gm':0.,'z0':50.,'sect':1},
                     True,"ApproximateFourPortTLine(f, float(arg['rp']),float(arg['lp']),float(arg['cp']),float(arg['gp']),float(arg['rn']),float(arg['ln']),float(arg['cn']),float(arg['gn']),float(arg['lm']),float(arg['cm']),float(arg['gm']),float(arg['z0']),int(arg['sect']))")
        ]
    def __getitem__(self,item):
        return self.deviceList[item]
    def __len__(self):
        return len(self.deviceList)
    def MakeDevice(self,ports,argsList,f):
        self.dev=None
        argsList=' '.join(argsList).split()
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
                        if not any(ports == int(acceptablePort) for acceptablePort in acceptablePorts):
                            continue
            if device.devicename != name:
                    continue
            # this is the device, try to make it
            if device.arginname:
                if len(argsList) > 0:
                    argsList=['']+argsList
            if len(argsList)/2*2 != len(argsList): # must be keyword value pairs
                raise PySIExceptionDeviceParser('arguments must come in keyword pairs: '+name+' '+' '.join(argsList))
            argsProvidedDict = {argsList[i].lower():argsList[i+1] for i in range(0,len(argsList),2)}
            if not all(key in device.defaults for key in argsProvidedDict.keys()):
                invalidKeyList=[]
                for key in argsProvidedDict.keys():
                    if key not in device.defaults:
                        invalidKeyList.append(key)
                raise PySIExceptionDeviceParser('argument keyword(s) invalid: '+str(invalidKeyList)+' for '+name)
            arg=copy.copy(device.defaults)
            arg.update(argsProvidedDict)
            if not all(arg[key] != None for key in arg.keys()):
                argNotProvidedList=[]
                for key in arg:
                    if arg[key] == None:
                        argNotProvidedList.append(key)
                raise PySIExceptionDeviceParser('manditory keyword(s) not supplied: '+str(argNotProvidedList)+' for '+name)
            try:
                self.dev=eval(device.func)
                self.frequencyDependent=device.frequencyDependent
            except:
                #print 'device '+name+' could not be instantiated with arguments: '+' '.join(argsList)
                raise PySIExceptionDeviceParser('device '+name+' could not be instantiated with arguments: '+' '.join(argsList))
            return True
        return False

class DeviceParser():
    deviceFactory=DeviceFactory()
    def __init__(self,f,ports,argsList):
        self.m_f=f
        self.m_sp=None
        self.m_spf=None
        if argsList is None:
            return
        if len(argsList) == 0:
            return
        if argsList[0] == 'subcircuit':
            self.m_spf=SubCircuit(self.m_f,argsList[1],
            ' '.join([x if len(x.split())==1 else "\'"+x+"\'" for x in argsList[2:]]))
            return
        if self.deviceFactory.MakeDevice(ports, argsList, f):
            if self.deviceFactory.frequencyDependent:
                self.m_spf=self.deviceFactory.dev
            else:
                self.m_sp=self.deviceFactory.dev
        else:
            #print 'device not found: '+' '.join(argsList)
            raise PySIExceptionDeviceParser('device not found: '+' '.join(argsList))
        return
