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
        ParserDevice('shunt',2,True,{'':None},False,"ShuntZTwoPort(float(arg['']))"),
        ParserDevice('shunt',3,True,{'':None},False,"ShuntZThreePort(float(arg['']))"),
        ParserDevice('shunt',4,True,{'':None},False,"ShuntZFourPort(float(arg['']))"),
        ParserDevice('m',4,True,{'':None},True,"Mutual(f,float(arg['']))"),
        ParserDevice('ground',1,False,{},False,"Ground()"),
        ParserDevice('open',1,False,{},False,"Open()"),
        ParserDevice('thru',2,False,{},False,"Thru()"),
        ParserDevice('termination',None,False,{},False,"zeros(shape=(ports,ports)).tolist()"),
        ParserDevice('tee',None,False,{},False,"Tee(ports)"),
        ParserDevice('mixedmode',4,True,{'':None},False,"(MixedModeConverterVoltage() if arg[''] == 'voltage' else MixedModeConverter())"),
        ParserDevice('idealtransformer',4,True,{'':1.},False,"IdealTransformer(float(arg['']))"),
        ParserDevice('voltagecontrolledvoltagesource',4,True,{'':None},False,"VoltageControlledVoltageSource(float(arg['']))"),
        ParserDevice('currentcontrolledcurrentsource',4,True,{'':None},False,"CurrentControlledCurrentSource(float(arg['']))"),
        ParserDevice('currentcontrolledvoltagesource',4,True,{'':None},False,"CurrentControlledVoltageSource(float(arg['']))"),
        ParserDevice('voltagecontrolledcurrentsource',4,True,{'':None},False,"VoltageControlledCurrentSource(float(arg['']))"),
        ParserDevice('voltageamplifier',2,False,{'gain':None,'zo':0,'zi':1e8,'z0':50.},False,"VoltageAmplifierTwoPort(float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('voltageamplifier',3,False,{'gain':None,'zo':0,'zi':1e8,'z0':50.},False,"VoltageAmplifierThreePort(float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('voltageamplifier',4,False,{'gain':None,'zo':0,'zi':1e8,'z0':50.},False,"VoltageAmplifierFourPort(float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('currentamplifier',2,False,{'gain':None,'zo':1e8,'zi':0,'z0':50.},False,"CurrentAmplifierTwoPort(float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('currentamplifier',3,False,{'gain':None,'zo':1e8,'zi':0,'z0':50.},False,"CurrentAmplifierThreePort(float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('currentamplifier',4,False,{'gain':None,'zo':1e8,'zi':0,'z0':50.},False,"CurrentAmplifierFourPort(float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('transresistanceamplifier',2,False,{'gain':None,'zo':0.,'zi':0.,'z0':50.},False,"TransresistanceAmplifierTwoPort(float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('transresistanceamplifier',3,False,{'gain':None,'zo':0.,'zi':0.,'z0':50.},False,"TransresistanceAmplifierThreePort(float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('transresistanceamplifier',4,False,{'gain':None,'zo':0.,'zi':0.,'z0':50.},False,"TransresistanceAmplifierFourPort(float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('transconductanceamplifier',2,False,{'gain':None,'zo':1e8,'zi':1e8,'z0':50.},False,"TransconductanceAmplifierTwoPort(float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('transconductanceamplifier',3,False,{'gain':None,'zo':1e8,'zi':1e8,'z0':50.},False,"TransconductanceAmplifierThreePort(float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('transconductanceamplifier',4,False,{'gain':None,'zo':1e8,'zi':1e8,'z0':50.},False,"TransconductanceAmplifierFourPort(float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('tline',2,False,{'zc':50.,'td':0.},True,"TLine(f,ports,float(arg['zc']),float(arg['td']))"),
        ParserDevice('tline',4,False,{'zc':50.,'td':0.},True,"TLine(f,ports,float(arg['zc']),float(arg['td']))")
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
                if device.ports != ports:
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
            # TODO: test for uninitialized required argument
            arg=copy.copy(device.defaults)
            arg.update(argsProvidedDict)
            try:
                self.dev=eval(device.func)
                self.frequencyDependent=device.frequencyDependent
            except:
                print 'device '+name+' could not be instantiated with arguments: '+' '.join(argsList)
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
            print 'device not found: '+' '.join(argsList)
            raise PySIExceptionDeviceParser('device not found: '+' '.join(argsList))
        return
