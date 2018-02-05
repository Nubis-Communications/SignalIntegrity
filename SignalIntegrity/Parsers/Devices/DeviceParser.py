'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import zeros
import copy

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
        ParserDevice('file',None,True,{'':None},True,
            "SParameterFile(arg[''],50.).Resample(f)"),
        ParserDevice('c',1,True,{'':None,'df':0.,'esr':0.,'z0':50.},True,
            "TerminationC(f,float(arg['']),float(arg['z0']),\
            float(arg['df']),float(arg['esr']))"),
        ParserDevice('c',2,True,{'':None,'df':0.,'esr':0.,'z0':50.},True,
            "SeriesC(f,float(arg['']),float(arg['z0']),float(arg['df']),\
            float(arg['esr']))"),
        ParserDevice('l',1,True,{'':None},True,"TerminationL(f,float(arg['']))"),
        ParserDevice('l',2,True,{'':None},True,"SeriesL(f,float(arg['']))"),
        ParserDevice('r',1,True,{'':None},False,"TerminationZ(float(arg['']))"),
        ParserDevice('r',2,True,{'':None},False,"SeriesZ(float(arg['']))"),
        ParserDevice('shunt','2-4',True,{'':None},False,
            "ShuntZ(ports,float(arg['']))"),
        ParserDevice('m',4,True,{'':None},True,"Mutual(f,float(arg['']))"),
        ParserDevice('ground',1,False,{},False,"Ground()"),
        ParserDevice('open',1,False,{},False,"Open()"),
        ParserDevice('thru',2,False,{},False,"Thru()"),
        ParserDevice('directionalcoupler','3-4',False,{},False,
            "DirectionalCoupler(ports)"),
        ParserDevice('termination',None,False,{},False,
            "zeros(shape=(ports,ports)).tolist()"),
        ParserDevice('tee',None,False,{},False,"Tee(ports)"),
        ParserDevice('mixedmode',4,True,{'':'power'},False,
            "(MixedModeConverterVoltage() if arg[''] == 'voltage'\
            else MixedModeConverter())"),
        ParserDevice('idealtransformer',4,True,{'':1.},False,
            "IdealTransformer(float(arg['']))"),
        ParserDevice('voltagecontrolledvoltagesource',4,True,{'':None},False,
            "VoltageControlledVoltageSource(float(arg['']))"),
        ParserDevice('currentcontrolledcurrentsource',4,True,{'':None},False,
            "CurrentControlledCurrentSource(float(arg['']))"),
        ParserDevice('currentcontrolledvoltagesource',4,True,{'':None},False,
            "CurrentControlledVoltageSource(float(arg['']))"),
        ParserDevice('voltagecontrolledcurrentsource',4,True,{'':None},False,
            "VoltageControlledCurrentSource(float(arg['']))"),
        ParserDevice('voltageamplifier','2-4',False,{'gain':None,'zo':0,'zi':1e8,
            'z0':50.},False,"VoltageAmplifier(ports,float(arg['gain']),\
            float(arg['zi']),float(arg['zo']))"),
        ParserDevice('currentamplifier','2-4',False,{'gain':None,'zo':1e8,'zi':0,
            'z0':50.},False,"CurrentAmplifier(ports,float(arg['gain']),\
            float(arg['zi']),float(arg['zo']))"),
        ParserDevice('transresistanceamplifier','2-4',False,{'gain':None,'zo':0.,
            'zi':0.,'z0':50.},False,"TransresistanceAmplifier(ports,\
            float(arg['gain']),float(arg['zi']),float(arg['zo']))"),
        ParserDevice('transconductanceamplifier','2-4',False,{'gain':None,'zo':1e8,
            'zi':1e8,'z0':50.},False,"TransconductanceAmplifier(ports,\
            float(arg['gain']),float(arg['zi']),float(arg['zo']))")]
        ParserDevice('opamp',3,False,{'zi':1e8,'zd':1e8,'zo':0.,'gain':1e8,'z0':50.},
            False,"OperationalAmplifier(float(arg['zi']),float(arg['zd']),\
            float(arg['zo']),float(arg['gain']),float(arg['z0']))"),
        # pragma: silent exclude
        self.__init__Contd()
        # pragma: include
    def __init__Contd(self):
        self.deviceList=self.deviceList+[
        ParserDevice('tline','2,4',False,{'zc':50.,'td':0.},True,
            "TLineLossless(f,ports,float(arg['zc']),float(arg['td']))"),
        ParserDevice('telegrapher',2,False,{'r':0.,'rse':0.,'l':0.,'c':0.,'df':0.,
            'g':0.,'z0':50.,'sect':0},True,"TLineTwoPortRLGC(f,\
            float(arg['r']),float(arg['rse']),float(arg['l']),float(arg['g']),\
            float(arg['c']),float(arg['df']),float(arg['z0']),int(arg['sect']))"),
        ParserDevice('telegrapher',4,False,{'rp':0.,'rsep':0.,'lp':0.,'cp':0.,'dfp':0.,
            'gp':0.,'rn':0.,'rsen':0.,'ln':0.,'cn':0.,'dfn':0.,'gn':0.,'lm':0.,
            'cm':0.,'dfm':0.,'gm':0.,'z0':50.,'sect':1},
            True,"TLineFourPortRLGC(f, float(arg['rp']),float(arg['rsep']),\
            float(arg['lp']),float(arg['gp']),float(arg['cp']),float(arg['dfp']),\
            float(arg['rn']),float(arg['rsen']),float(arg['ln']),float(arg['gn']),\
            float(arg['cn']),float(arg['dfn']),float(arg['cm']),float(arg['dfm']),\
            float(arg['gm']),float(arg['lm']),float(arg['z0']),int(arg['sect']))"),
        ParserDevice('shortstd',1,False,{'od':0.,'oz0':50.,'ol':0.0,
            'l0':0.0,'l1':0.0,'l2':0.0,'l3':0.0},True,
            "ShortStandard(f,float(arg['od']),float(arg['oz0']),float(arg['ol']),\
            float(arg['l0']),float(arg['l1']),float(arg['l2']),float(arg['l3']))"),
        ParserDevice('openstd',1,False,{'od':0.,'oz0':50.,'ol':0.0,
            'c0':0.0,'c1':0.0,'c2':0.0,'c3':0.0},True,
            "OpenStandard(f,float(arg['od']),float(arg['oz0']),float(arg['ol']),\
            float(arg['c0']),float(arg['c1']),float(arg['c2']),float(arg['c3']))"),
        ParserDevice('loadstd',1,False,{'od':0.,'oz0':50.,'ol':0.0,'tz0':50.0},
            True,"LoadStandard(f,float(arg['od']),float(arg['oz0']),float(arg['ol']),\
            float(arg['tz0']))"),
        ParserDevice('thrustd',2,False,{'od':0.,'oz0':50.,'ol':0.0},
            True,"ThruStandard(f,float(arg['od']),float(arg['oz0']),float(arg['ol']))")
        ]
    def __getitem__(self,item):
        return self.deviceList[item]
    def __len__(self):
        return len(self.deviceList)
    def MakeDevice(self,ports,argsList,f):
        # pragma: silent exclude
        from SignalIntegrity.SParameters import SParameterFile
        from SignalIntegrity.Devices.CurrentAmplifier import CurrentAmplifier
        from SignalIntegrity.Devices.CurrentControlledCurrentSource import CurrentControlledCurrentSource
        from SignalIntegrity.Devices.CurrentControlledVoltageSource import CurrentControlledVoltageSource
        from SignalIntegrity.Devices.DirectionalCoupler import DirectionalCoupler
        from SignalIntegrity.Devices.Ground import Ground
        from SignalIntegrity.Devices.IdealTransformer import IdealTransformer
        from SignalIntegrity.Devices.MixedModeConverter import MixedModeConverter
        from SignalIntegrity.Devices.Open import Open
        from SignalIntegrity.Devices.OperationalAmplifier import OperationalAmplifier
        from SignalIntegrity.Devices.SeriesZ import SeriesZ
        from SignalIntegrity.Devices.TerminationZ import TerminationZ
        from SignalIntegrity.Devices.MixedModeConverter import MixedModeConverterVoltage
        from SignalIntegrity.Devices.Thru import Thru
        from SignalIntegrity.Devices.VoltageAmplifier import VoltageAmplifier
        from SignalIntegrity.Devices.ShuntZ import ShuntZ
        from SignalIntegrity.Devices.Tee import Tee
        from SignalIntegrity.Devices.TransconductanceAmplifier import TransconductanceAmplifier
        from SignalIntegrity.Devices.TransresistanceAmplifier import TransresistanceAmplifier
        from SignalIntegrity.Devices.VoltageControlledVoltageSource import VoltageControlledVoltageSource
        from SignalIntegrity.Devices.VoltageControlledCurrentSource import VoltageControlledCurrentSource
        from SignalIntegrity.SParameters.Devices.Mutual import Mutual
        from SignalIntegrity.SParameters.Devices.SeriesC import SeriesC
        from SignalIntegrity.SParameters.Devices.SeriesL import SeriesL
        from SignalIntegrity.SParameters.Devices.TerminationC import TerminationC
        from SignalIntegrity.SParameters.Devices.TerminationL import TerminationL
        from SignalIntegrity.SParameters.Devices.TLineLossless import TLineLossless
        from SignalIntegrity.SParameters.Devices.TLineTwoPortRLGC import TLineTwoPortRLGC
        from SignalIntegrity.PySIException import PySIExceptionDeviceParser
        from SignalIntegrity.Measurement.CalKit.Standards.ShortStandard import ShortStandard
        from SignalIntegrity.Measurement.CalKit.Standards.OpenStandard import OpenStandard
        from SignalIntegrity.Measurement.CalKit.Standards.LoadStandard import LoadStandard
        from SignalIntegrity.Measurement.CalKit.Standards.ThruStandard import ThruStandard
        from SignalIntegrity.Measurement.CalKit.Standards.Offset import Offset
        from SignalIntegrity.SParameters.Devices.TLineFourPortRLGC import TLineFourPortRLGC
        # pragma: include
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
                        if not any(ports == int(acceptablePort)
                                   for acceptablePort in acceptablePorts):
                            continue
            if device.devicename != name:
                    continue
            # this is the device, try to make it
            if device.arginname:
                if len(argsList) > 0:
                    argsList=['']+argsList
            # pragma: silent exclude
            if len(argsList)/2*2 != len(argsList): # must be keyword value pairs
                raise PySIExceptionDeviceParser('arguments must come in keyword pairs: '+name+' '+' '.join(argsList))
            # pragma: include
            argsProvidedDict = {argsList[i].lower():argsList[i+1]
                                for i in range(0,len(argsList),2)}
            # pragma: silent exclude
            if not all(key in device.defaults for key in argsProvidedDict.keys()):
                invalidKeyList=[]
                for key in argsProvidedDict.keys():
                    if key not in device.defaults:
                        invalidKeyList.append(key)
                raise PySIExceptionDeviceParser('argument keyword(s) invalid: '+str(invalidKeyList)+' for '+name)
            # pragma: include
            arg=copy.copy(device.defaults)
            arg.update(argsProvidedDict)
            # pragma: silent exclude
            if not all(arg[key] != None for key in arg.keys()):
                argNotProvidedList=[]
                for key in arg:
                    if arg[key] == None:
                        argNotProvidedList.append(key)
                raise PySIExceptionDeviceParser('mandatory keyword(s) not supplied: '+str(argNotProvidedList)+' for '+name)
            # pragma: include
            # pragma: silent exclude
            try:
            # pragma: include outdent
                self.dev=eval(device.func)
                self.frequencyDependent=device.frequencyDependent
            # pragma: silent exclude indent
            except:
                try:
                    f=[0]
                    eval(device.func)
                except:
                    raise PySIExceptionDeviceParser('device '+name+' could not be instantiated with arguments: '+' '.join(argsList))
                raise PySIExceptionDeviceParser('frequency dependent device '+name+' could not be instantiated because no frequencies provided')
            # pragma: include
            return True
        return False

class DeviceParser():
    deviceFactory=DeviceFactory()
    def __init__(self,f,ports,argsList):
        # pragma: silent exclude
        from SignalIntegrity.PySIException import PySIExceptionDeviceParser
        from SignalIntegrity.SubCircuits.SubCircuit import SubCircuit
        # pragma: include
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
