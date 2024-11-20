"""
Device.py
"""
# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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
from SignalIntegrity.App.PartProperty import *
from SignalIntegrity.App.PartPicture import *
from SignalIntegrity.App.DeviceNetListLine import DeviceNetListLine
from SignalIntegrity.App.EyeDiagramConfiguration import EyeDiagramConfiguration

class Device(object):
    def __init__(self,netlist,propertiesList,partPicture,configuration=None,variablesList=[]):
        self.netlist=netlist
        if propertiesList==None:
            propertiesList=[]
        self.propertiesList=propertiesList
        self.variablesList=variablesList
        self.partPicture=partPicture
        self.configuration=configuration
        self.selected=False
        self.enabled=True
        if self['defref'] != None:
            self.AddPartProperty(PartPropertyReferenceDesignator(''))
    def DrawDevice(self,canvas,grid,x,y,pinsConnectedList=None):
        self.CreateVisiblePropertiesList()
        unselected_color = 'black'
        if self['element_state'] != None:
            if self['element_state'].GetValue() in ['disabled','thru_wires']:
                unselected_color = 'salmon'
        self.partPicture.current.Selected(self.selected,unselected_color).DrawDevice(self,canvas,grid,(x,y),pinsConnectedList)
    def IsAt(self,coord,augmentor,distance):
        return self.partPicture.current.IsAt(coord,augmentor,distance)
    def IsIn(self,coord0,coord1,coord0Augmentor,coord1Augmentor):
        return self.partPicture.current.IsIn(coord0,coord1,coord0Augmentor,coord1Augmentor)
    def WhereInPart(self,coord):
        return self.partPicture.current.WhereInPart(coord)
    def PartPropertyByName(self,name):
        for partProperty in self.propertiesList:
            if partProperty['PropertyName'] == name:
                return partProperty
        return None
    def PartPropertyByKeyword(self,keyword):
        for partProperty in self.propertiesList:
            if partProperty['Keyword'] == keyword:
                return partProperty
        return None
    def AddPartProperty(self,PartProperty):
        if self[PartProperty['Keyword']] is None:
            self.propertiesList=self.propertiesList+[PartProperty]
    def __getitem__(self,item):
        return self.PartPropertyByKeyword(item)
    def __setitem__(self,item,value):
        for p in range(len(self.propertiesList)):
            if self.propertiesList[p]['Keyword'] == item:
                self.propertiesList[p]=value
                return
        raise ValueError
    def NetListLine(self):
        return self.netlist.NetListLine(self)+self.VariablesNetlistLine()
    def PinCoordinates(self):
        return self.partPicture.current.PinCoordinates()
    def CreateVisiblePropertiesList(self):
        import SignalIntegrity.App.Project
        textLimit = SignalIntegrity.App.Preferences['Appearance.LimitText']
        visiblePartPropertyList=[]
        for partProperty in self.propertiesList:
            propertyString=partProperty.PropertyString(stype='attr')
            if propertyString != '':
                if propertyString != '':
                    if len(propertyString) > textLimit:
                        propertyString = propertyString[:textLimit]+'...'
                visiblePartPropertyList.append(propertyString)
        for variable in self.variablesList:
            displayString=variable.DisplayString(True,True,False)
            if displayString != '':
                if len(displayString) > textLimit:
                    displayString = displayString[:textLimit]+'...'
                visiblePartPropertyList.insert(0,displayString)
        self.partPicture.current.InsertVisiblePartProperties(visiblePartPropertyList)
    def SetWaveform(self,wf):
        self.Wf=wf
    def Waveform(self,callback=None):
        import SignalIntegrity.Lib as si
        wfTypeProperty=self['wftype']
        if wfTypeProperty is None:
            waveform = None
        else:
            if hasattr(self, 'Wf'):
                if self.Wf != None:
                    return self.Wf
            wfType=wfTypeProperty.GetValue()
            if wfType is None:
                waveform = None
            elif wfType=='file':
                fileName = self['wffile'].PropertyString(stype='raw')
                if (len(fileName)>0) and (fileName[0]=='='):
                    import SignalIntegrity.App.Project
                    variables = SignalIntegrity.App.Project['Variables']
                    if fileName[1:] in variables.Names():
                        fileName=variables.VariableByName(fileName[1:]).Value()
                ext=str.lower(fileName).split('.')[-1]
                if ext == 'si':
                    from SignalIntegrity.App.SignalIntegrityAppHeadless import ProjectWaveform
                    import SignalIntegrity.App.Project
                    args=SignalIntegrity.App.Project['Variables'].Dictionary(self.variablesList)
                    if self['calcprop'].GetValue() == 'true':
                        args.update(SignalIntegrity.App.Project['CalculationProperties'].Dictionary())
                    waveform=ProjectWaveform(fileName,self['wfprojname'].GetValue(),callback,**args)
                    if waveform is None:
                        raise si.SignalIntegrityExceptionWaveform('project file: '+fileName+' could not produce waveform: '+self['wfprojname'].GetValue())
                else:
                    waveform = si.td.wf.Waveform().ReadFromFile(fileName)
            elif wfType == 'step':
                amplitude=float(self['a'].GetValue())
                startTime=float(self['t0'].GetValue())
                risetime=float(self['rt'].GetValue())
                waveform = si.td.wf.StepWaveform(self.WaveformTimeDescriptor(),amplitude,startTime,risetime)
            elif wfType == 'pulse':
                amplitude=float(self['a'].GetValue())
                startTime=float(self['t0'].GetValue())
                pulseWidth=float(self['w'].GetValue())
                risetime=float(self['rt'].GetValue())
                waveform = si.td.wf.PulseWaveform(self.WaveformTimeDescriptor(),amplitude,startTime,pulseWidth,risetime)
            elif wfType == 'impulse':
                amplitude=float(self['a'].GetValue())
                waveform = si.td.wf.ImpulseWaveform(self.WaveformTimeDescriptor(),amplitude,0.)
            elif wfType == 'prbs':
                polynomial=int(self['prbs'].GetValue())
                bitrate=float(self['br'].GetValue())
                risetime=float(self['rt'].GetValue())
                amplitude=float(self['a'].GetValue())
                delay=float(self['t0'].GetValue())
                waveform = si.prbs.PseudoRandomWaveform(polynomial,bitrate,amplitude,risetime,delay,self.WaveformTimeDescriptor())
            elif wfType == 'mlw':
                polynomial=int(self['prbs'].GetValue())
                baudrate=float(self['br'].GetValue())
                bitspersymbol=int(self['bps'].GetValue())
                risetime=float(self['rt'].GetValue())
                amplitude=float(self['a'].GetValue())
                delay=float(self['t0'].GetValue())
                waveform = si.prbs.MultiLevelWaveform(polynomial,baudrate,bitspersymbol,amplitude,risetime,delay,self.WaveformTimeDescriptor())
            elif wfType == 'lmlw':
                polynomial=int(self['prbs'].GetValue())
                baudrate=float(self['br'].GetValue())
                levels=int(self['lvl'].GetValue())
                symbols=int(self['sym'].GetValue())
                risetime=float(self['rt'].GetValue())
                amplitude=float(self['a'].GetValue())
                delay=float(self['t0'].GetValue())
                waveform = si.prbs.LevelsMultiLevelWaveform(polynomial,baudrate,levels,symbols,amplitude,risetime,delay,self.WaveformTimeDescriptor())
            elif wfType == 'clock':
                clockrate=float(self['f'].GetValue())
                risetime=float(self['rt'].GetValue())
                amplitude=float(self['a'].GetValue())
                delay=float(self['t0'].GetValue())
                waveform = si.prbs.ClockWaveform(clockrate,amplitude,risetime,delay,self.WaveformTimeDescriptor())
            elif wfType == 'sine':
                amplitude=float(self['a'].GetValue())
                frequency=float(self['f'].GetValue())
                phase=float(self['ph'].GetValue())
                start=float(self['t0'].GetValue())
                stop=float(self['tf'].GetValue())
                waveform = si.td.wf.SineWaveform(self.WaveformTimeDescriptor(),amplitude,frequency,phase,start,stop)
            elif wfType == 'noise':
                sigma=float(self['vrms'].GetValue())
                waveform = si.td.wf.NoiseWaveform(self.WaveformTimeDescriptor(),sigma)
            elif wfType == 'networkanalyzerport':
                td=self.WaveformTimeDescriptor()
                if self['state']['Value'] == 'off':
                    waveform =  si.td.wf.Waveform(td)
                else:
                    if self['st']['Value'] == 'CW':
                        waveform =  si.td.wf.Waveform(td)
                        dbm=float(self['pow']['Value'])
                        waveform[td.IndexOfTime(0.0)]=pow(10.,(float(self['pow']['Value'])-13.010)/20.0)*math.sqrt(td.K)
                    elif self['st']['Value'] == 'TDRImpulse':
                        waveform = si.td.wf.StepWaveform(td,2.*float(self['ia']['Value'])/td.Fs,0.0,float(self['rt']['Value'])).Derivative(removePoint=True,scale=True)
                    elif self['st']['Value'] == 'TDRStep':
                        waveform = si.td.wf.StepWaveform(td,2.*float(self['a']['Value']),0.0,float(self['rt']['Value']))
            elif wfType == 'DC':
                amplitude=float(self['a'].GetValue())
                waveform=si.td.wf.DCWaveform(amplitude)
            # attach any noise specified to the waveform
            if not self['noisefile'] == None:
                noise_file=str(self['noisefile'].GetValue())
                if noise_file not in ['','None']:
                    noise_shape = si.fd.FrequencyResponse()
                    noise_shape.ReadFromFile(noise_file)
                    waveform.noise = noise_shape
        return waveform
    def WaveformTimeDescriptor(self):
        import SignalIntegrity.Lib as si
        Fs=float(self['fs'].GetValue())
        K=int(math.ceil(Fs*float(self['dur'].GetValue())))
        horOffset=float(self['ho'].GetValue())
        return si.td.wf.TimeDescriptor(horOffset,K,Fs)
    def InitializeFromPreferences(self):
        if not self.configuration is None:
            if isinstance(self.configuration,list):
                for config in self.configuration:
                    config.InitializeFromPreferences()
            else:
                self.configuration.InitializeFromPreferences()
        return self
    def VariablesNetlistLine(self):
        variablesLine=''
        for variable in self.variablesList:
            token=''
            value=variable.GetValue('Value')
            if (len(value)>0) and (value[0]=='='):
                value='$'+value[1:]+'$'
                token=variable.GetValue('Name')+' '+value
            elif variable.GetValue('Type') == 'int':
                try:
                    value = str(int(value))
                except ValueError:
                    value = 'Invalid'
                token=variable.GetValue('Name')+' '+value
            elif variable.GetValue('Type') in ['string','enum']:
                value = str(value)
                if value == '': value="''"
                token=variable.GetValue('Name')+' '+value
            elif variable.GetValue('Type')=='float':
                try:
                    value = str(ToSI(float(value),variable.GetValue('Unit'),letterPrefixes=False))
                except ValueError:
                    value = 'Invalid'
                token=variable.GetValue('Name')+' '+value
            elif variable.GetValue('Type')=='file':
                if ' ' in value:
                    value='"'+value+'"'
                token=variable.GetValue('Name')+' '+value
            variablesLine+=(' '+token)
        if not self['calcprop'] == None:
            if self['calcprop']['Value']=='true':
                calculationProperties=SignalIntegrity.App.Project['CalculationProperties']
                for propertyName in calculationProperties.Dictionary().keys():
                    variablesLine+=(' '+propertyName+' '+str(calculationProperties[propertyName]))
        return variablesLine

class DeviceFromProject(object):
    def __init__(self,deviceProject):
        ports=None
        for partPropertyProject in deviceProject['PartProperties']:
            if partPropertyProject['Keyword'] == 'ports':
                ports=int(partPropertyProject['Value'])
                break
        className=deviceProject['ClassName']
        self.result=None
        if className=='DeviceFile':
            self.result=DeviceFile([PartPropertyDescription('Variable Port File'),PartPropertyPorts(ports,False)],PartPictureVariableSpecifiedPorts(ports))
        elif className=='DeviceUnknown':
            self.result=DeviceUnknown([PartPropertyDescription('Variable Port Unknown'),PartPropertyPorts(ports,False)],PartPictureVariableUnknown(ports))
        elif className=='DeviceSystem':
            self.result=DeviceSystem([PartPropertyDescription('Variable Port System'),PartPropertyPorts(ports,False)],PartPictureVariableSystem(ports))
        elif className=='DeviceNetworkAnalyzerModel':
            self.result=DeviceNetworkAnalyzerModel(ports)
        elif className=='DeviceNetworkAnalyzer':
            self.result=DeviceNetworkAnalyzer(ports)
        elif className=='DeviceNetworkAnalyzerDeviceUnderTest':
            self.result=DeviceNetworkAnalyzerDeviceUnderTest(ports)
        elif className=='DeviceWElement':
            self.result=DeviceWElement([PartPropertyPorts(ports,False)],PartPictureVariableWElement(ports))
        elif className=='DeviceRelay':
            self.result=DeviceRelay([PartPropertyPorts(ports,False)],PartPictureVariableRelay(ports))
        elif className=='DeviceSeries':
            self.result=DeviceSeries(ports)
        elif className=='DeviceThru':
            self.result=DeviceThru(ports)
        # elif className=='DeviceVoltageMultiLevelWaveformGenerator':
        #     pass
        else:
            for device in DeviceList+DeviceListSystem+DeviceListUnknown:
                if (str(device.__class__).split('.')[-1].strip('\'>') == className):
                    devicePorts = device['ports']
                    if (devicePorts is None):
                        match=True
                    elif (devicePorts.GetValue() == ports):
                        match=True
                    else:
                        match=False
                    if match:
                        self.result=copy.deepcopy(device)
                        break
        if self.result is None:
            raise
        for partPropertyProject in deviceProject['PartProperties']:
            devicePartProperty=self.result[partPropertyProject['Keyword']]
            if not devicePartProperty is None:
                for propertyItemName in partPropertyProject.dict:
                    if partPropertyProject.dict[propertyItemName].dict['write']:
                        devicePartProperty[propertyItemName]=partPropertyProject.GetValue(propertyItemName)
                if devicePartProperty['Type'] == 'file':
                    if isinstance(devicePartProperty['Value'],str):
                        # keep Linux file system format
                        devicePartProperty['Value']=devicePartProperty['Value'].replace('\\','/')
        self.result.variablesList=deviceProject['Variables']['Items']
        partPictureList=self.result.partPicture.partPictureClassList
        self.result.partPicture=PartPictureFromProject(partPictureList,deviceProject['PartPicture'],ports).result
        if not self.result.configuration is None:
            if isinstance(self.result.configuration,list):
                for c in range(len(self.result.configuration)):
                    if self.result.configuration[c].name in deviceProject.dict.keys():
                        self.result.configuration[c].dict = deviceProject[self.result.configuration[c].name]
            else:
                if self.result.configuration.name in deviceProject.dict.keys():
                    self.result.configuration.dict = deviceProject[self.result.configuration.name].dict
                self.result.configuration.HandleBackwardsCompatibility()

class DeviceFileNetListLine(DeviceNetListLine):
    def __init__(self,devicename=None,partname=None,showReference=True,showports=True,values=None):
        DeviceNetListLine.__init__(self,devicename=devicename,partname=partname,showReference=showReference,showports=showports,values=values)
    def NetListLine(self,device):
        reorder_string=device.PartPropertyByKeyword('reorder').PropertyString(stype='netlist')
        if reorder_string not in ['','None']:
            reorder_string = ' reorder '+reorder_string
        else:
            reorder_string = ''
        returnstring=DeviceNetListLine.NetListLine(self,device)+reorder_string
        return returnstring

class DeviceFile(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceFileNetListLine(values=[('file',True)])
        Device.__init__(self,netlist,[
            PartPropertyCategory('Files'),
            PartPropertyPartName('File'),
            PartPropertyHelp('device:File'),
            PartPropertyCalculationProperties(),
            PartPropertyDefaultReferenceDesignator('D?'),
            PartPropertyFileName(),
            PartPropertyElementState(),
            PartPropertyReorder(),]+propertiesList,partPicture)

class DeviceUnknown(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='unknown')
        Device.__init__(self,netlist,[PartPropertyCategory('Unknowns'),
                                      PartPropertyPartName('Unknown'),
                                      PartPropertyHelp('device:Unknown'),
                                      PartPropertyDefaultReferenceDesignator('U?')]+propertiesList,
                                      partPicture)

class DeviceSystem(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='system',showReference=False,showports=False,values=[('file',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Systems'),
                                      PartPropertyPartName('System'),
                                      PartPropertyHelp('device:System'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyCalculationProperties(),
                                      PartPropertyFileName()]+propertiesList,partPicture)

class DeviceResistor(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='R',values=[('r',False)])
        Device.__init__(self,netlist,[
            PartPropertyCategory('Resistors'),
            PartPropertyPartName('Resistor'),
            PartPropertyHelp('device:Resistor'),
            PartPropertyDefaultReferenceDesignator('R?'),
            PartPropertyResistance()]+propertiesList,partPicture)

class DeviceSkinEffectResistor(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='rse',values=[('rse',False)])
        Device.__init__(self,netlist,[
            PartPropertyCategory('Resistors'),
            PartPropertyPartName('Skin-effect Resistor'),
            PartPropertyHelp('device:Skin-Effect-Resistor'),
            PartPropertyDefaultReferenceDesignator('R?'),
            PartPropertyResistanceSkinEffect()]+propertiesList,partPicture)

class DeviceCapacitor(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='C',values=[('c',False),('esr',True),('df',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Capacitors'),
                                      PartPropertyPartName('Capacitor'),
                                      PartPropertyHelp('device:Capacitor'),
                                      PartPropertyDefaultReferenceDesignator('C?'),
                                      PartPropertyCapacitance(),
                                      PartPropertyDissipationFactor(),
                                      PartPropertyESR()]+propertiesList,
                                      partPicture)

class DeviceInductor(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='L',values=[('l',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Inductors'),
                                      PartPropertyPartName('Inductor'),
                                      PartPropertyHelp('device:Inductor'),
                                      PartPropertyDefaultReferenceDesignator('L?'),
                                      PartPropertyInductance()]+propertiesList,
                                      partPicture)

class DeviceMutual(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='M',values=[('l',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Inductors'),
                                      PartPropertyPartName('Mutual'),
                                      PartPropertyHelp('device:Mutual'),
                                      PartPropertyDefaultReferenceDesignator('M?'),
                                      PartPropertyPorts(4),
                                      PartPropertyInductance(),
                                      PartPropertyDescription('Four Port Mutual Inductance')],
                                      partPicture=PartPictureVariableMutual())

class DeviceIdealTransformer(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='idealtransformer',values=[('tr',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Inductors'),
                                      PartPropertyPartName('IdealTransformer'),
                                      PartPropertyHelp('device:IdealTransformer'),
                                      PartPropertyHelp('device:'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyPorts(4),
                                      PartPropertyTurnsRatio(),
                                      PartPropertyDescription('Four Port IdealTransformer')],
                                      partPicture=PartPictureVariableIdealTransformer())

class PortNetListLine(DeviceNetListLine):
    def NetListLine(self,device):
        line =  DeviceNetListLine.NetListLine(self,device)
        if (len(line) >= 5) and (line[-5:] == ' td 0'):
            line = line.replace(' td 0','')
        return line

class Port(Device):
    def __init__(self,portNumber=1):
        netlist=PortNetListLine(devicename='port',showReference=False,showports=False,values=[('pn',False),('td',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyCategory('Ports and Probes'),
                         PartPropertyPartName('Port'),
                         PartPropertyHelp('device:Port'),
                         PartPropertyDescription('Port'),
                         PartPropertyPorts(1),
                         PartPropertyDelay(0.0),
                         PartPropertyPortNumber(portNumber)],
                        partPicture=PartPictureVariablePort())
        self['td']['Visible']=False

class DeviceGround(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='ground')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Miscellaneous'),
            PartPropertyPartName('Ground'),
            PartPropertyHelp('device:Ground'),
            PartPropertyDefaultReferenceDesignator('G?'),
            PartPropertyDescription('Ground'),
            PartPropertyPorts(1)],partPicture=PartPictureVariableGround())

class DeviceOpen(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='open')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Miscellaneous'),
            PartPropertyPartName('Open'),
            PartPropertyHelp('device:Open'),
            PartPropertyDefaultReferenceDesignator('O?'),
            PartPropertyDescription('Open'),
            PartPropertyPorts(1)],partPicture=PartPictureVariableOpen())

class DeviceDirectionalCoupler(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='directionalcoupler')
        Device.__init__(self,netlist,[PartPropertyCategory('Miscellaneous'),
                                      PartPropertyPartName('Directional Coupler'),
                                      PartPropertyHelp('device:DirectionalCoupler'),
                                      PartPropertyDefaultReferenceDesignator('D?')]+propertiesList,
                                      partPicture)

class DeviceVoltageSource(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Sources'),
            PartPropertyPartName('Voltage Source'),
            PartPropertyHelp('device:Voltage-Source'),
            PartPropertyDefaultReferenceDesignator('VS?'),
            PartPropertyCalculationProperties(),
            PartPropertyWaveformFileName(),
            PartPropertyShow(),
            PartPropertyWaveformType('file'),
            PartPropertyWaveformProjectName(''),
            PartPropertyNoiseFileName()]+propertiesList,partPicture)

class DeviceVoltageStepGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Generators'),
            PartPropertyPartName('Voltage Step Generator'),
            PartPropertyHelp('device:Voltage-Step-Generator'),
            PartPropertyDefaultReferenceDesignator('VG?'),
            PartPropertyShow(),
            PartPropertyHorizontalOffset(),
            PartPropertyDuration(),
            PartPropertyStartTime(),
            PartPropertyRisetime(),
            PartPropertySampleRate(),
            PartPropertyVoltageAmplitude(),
            PartPropertyWaveformType('step'),
            PartPropertyNoiseFileName()]+propertiesList,partPicture)

class DeviceVoltageDCSource(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Sources'),
            PartPropertyPartName('Voltage DC Source'),
            PartPropertyHelp('device:Voltage-DC-Source'),
            PartPropertyDefaultReferenceDesignator('VS?'),
            PartPropertyVoltageAmplitude(),
            PartPropertyWaveformType('DC'),
            PartPropertyShow(),
            PartPropertyNoiseFileName()]+propertiesList,
            partPicture)
        self['a']['KeywordVisible']=False

class DeviceVoltagePulseGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Generators'),
            PartPropertyPartName('Voltage Pulse Generator'),
            PartPropertyHelp('device:Voltage-Pulse-Generator'),
            PartPropertyDefaultReferenceDesignator('VG?'),
            PartPropertyShow(),
            PartPropertyHorizontalOffset(),
            PartPropertyDuration(),
            PartPropertyStartTime(),
            PartPropertyRisetime(),
            PartPropertyPulseWidth(),
            PartPropertySampleRate(),
            PartPropertyVoltageAmplitude(),
            PartPropertyWaveformType('pulse'),
            PartPropertyNoiseFileName()]+propertiesList,
            partPicture)

class DeviceVoltageImpulseGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Generators'),
            PartPropertyPartName('Voltage Impulse Generator'),
            PartPropertyHelp('device:Voltage-Impulse-Generator'),
            PartPropertyDefaultReferenceDesignator('VG?'),
            PartPropertyShow(),
            PartPropertyHorizontalOffset(),
            PartPropertyDuration(),
            PartPropertyStartTime(),
            PartPropertySampleRate(),
            PartPropertyVoltageAmplitude(),
            PartPropertyWaveformType('impulse')]+propertiesList,
            partPicture)

class DeviceVoltagePRBSGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Generators'),
            PartPropertyPartName('Voltage PRBS Generator'),
            PartPropertyHelp('device:Voltage-PRBS-Generator'),
            PartPropertyDefaultReferenceDesignator('VG?'),
            PartPropertyShow(),
            PartPropertyHorizontalOffset(),
            PartPropertyDuration(),
            PartPropertyStartTime(),
            PartPropertyBitRate(),
            PartPropertyRisetime(),
            PartPropertyPRBSPolynomial(),
            PartPropertySampleRate(),
            PartPropertyVoltageAmplitude(),
            PartPropertyWaveformType('prbs'),
            PartPropertyNoiseFileName()]+propertiesList,partPicture)

class DeviceVoltageMultiLevelWaveformGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Generators'),
            PartPropertyPartName('Voltage Multi Level Waveform Generator'),
            PartPropertyHelp('device:Voltage-Multi-Level-Waveform-Generator'),
            PartPropertyDefaultReferenceDesignator('VG?'),
            PartPropertyShow(),
            PartPropertyHorizontalOffset(),
            PartPropertyDuration(),
            PartPropertyStartTime(),
            PartPropertyBaudRate(),
            PartPropertyRisetime(),
            PartPropertyPRBSPolynomial(),
            PartPropertyBitsPerSymbol(),
            PartPropertySampleRate(),
            PartPropertyVoltageAmplitude(),
            PartPropertyWaveformType('mlw'),
            PartPropertyNoiseFileName()]+propertiesList,partPicture)

class DeviceVoltageLevelsMultiLevelWaveformGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Generators'),
            PartPropertyPartName('Voltage Levels Multi Level Waveform Generator'),
            PartPropertyHelp('device:Voltage-Levels-Multi-Level-Waveform-Generator'),
            PartPropertyDefaultReferenceDesignator('VG?'),
            PartPropertyShow(),
            PartPropertyHorizontalOffset(),
            PartPropertyDuration(),
            PartPropertyStartTime(),
            PartPropertyBaudRate(),
            PartPropertyRisetime(),
            PartPropertyPRBSPolynomial(),
            PartPropertyLevels(),
            PartPropertySymbols(),
            PartPropertySampleRate(),
            PartPropertyVoltageAmplitude(),
            PartPropertyWaveformType('lmlw')]+propertiesList,partPicture)

class DeviceVoltageClockGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Generators'),
            PartPropertyPartName('Voltage Clock Generator'),
            PartPropertyHelp('device:Voltage-Clock-Generator'),
            PartPropertyDefaultReferenceDesignator('VG?'),
            PartPropertyShow(),
            PartPropertyHorizontalOffset(),
            PartPropertyDuration(),
            PartPropertyStartTime(),
            PartPropertyFrequency(),
            PartPropertyRisetime(),
            PartPropertySampleRate(),
            PartPropertyVoltageAmplitude(),
            PartPropertyWaveformType('clock'),
            PartPropertyNoiseFileName()]+propertiesList,partPicture)

class DeviceVoltageSineGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Generators'),
            PartPropertyPartName('Voltage Sine Generator'),
            PartPropertyHelp('device:Voltage-Sine-Generator'),
            PartPropertyDefaultReferenceDesignator('VG?'),
            PartPropertyShow(),
            PartPropertyHorizontalOffset(),
            PartPropertyDuration(),
            PartPropertySampleRate(),
            PartPropertyVoltageAmplitude(),
            PartPropertyFrequency(),
            PartPropertyStartTime(-100.),
            PartPropertyStopTime(100.),
            PartPropertyPhase(),
            PartPropertyWaveformType('sine'),
            PartPropertyNoiseFileName()]+propertiesList,partPicture)
        self['t0']['Visible']=False; self['tf']['Visible']=False

class DeviceCurrentSource(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='currentsource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Sources'),
            PartPropertyPartName('Current Source'),
            PartPropertyHelp('device:Current-Source'),
            PartPropertyDefaultReferenceDesignator('CS?'),
            PartPropertyCalculationProperties(),
            PartPropertyWaveformFileName(),
            PartPropertyShow(),
            PartPropertyWaveformType('file'),
            PartPropertyWaveformProjectName('')]+propertiesList,partPicture)

class DeviceCurrentStepGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='currentsource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Generators'),
            PartPropertyPartName('Current Step Generator'),
            PartPropertyHelp('device:Current-Step-Generator'),
            PartPropertyDefaultReferenceDesignator('CG?'),
            PartPropertyShow(),
            PartPropertyHorizontalOffset(),
            PartPropertyDuration(),
            PartPropertyStartTime(),
            PartPropertyRisetime(),
            PartPropertySampleRate(),
            PartPropertyCurrentAmplitude(),PartPropertyWaveformType('step')]+propertiesList,partPicture)

class DeviceCurrentDCSource(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='currentsource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Sources'),
            PartPropertyPartName('Current DC Source'),
            PartPropertyHelp('device:Current-DC-Source'),
            PartPropertyDefaultReferenceDesignator('CS?'),
            PartPropertyCurrentAmplitude(),
            PartPropertyWaveformType('DC'),
            PartPropertyShow()]+propertiesList,
            partPicture)
        self['a']['KeywordVisible']=False

class DeviceCurrentPulseGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='currentsource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Generators'),
            PartPropertyPartName('Current Pulse Generator'),
            PartPropertyHelp('device:Current-Pulse-Generator'),
            PartPropertyDefaultReferenceDesignator('CG?'),
            PartPropertyShow(),
            PartPropertyHorizontalOffset(),
            PartPropertyDuration(),
            PartPropertyStartTime(),
            PartPropertyRisetime(),
            PartPropertyPulseWidth(),
            PartPropertySampleRate(),
            PartPropertyCurrentAmplitude(),
            PartPropertyWaveformType('pulse')]+propertiesList,partPicture)

class DeviceCurrentImpulseGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='currentsource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Generators'),
            PartPropertyPartName('Current Impulse Generator'),
            PartPropertyHelp('device:Current-Impulse-Generator'),
            PartPropertyDefaultReferenceDesignator('CG?'),
            PartPropertyShow(),
            PartPropertyHorizontalOffset(),
            PartPropertyDuration(),
            PartPropertyStartTime(),
            PartPropertySampleRate(),
            PartPropertyCurrentAmplitude(),
            PartPropertyWaveformType('impulse')]+propertiesList,partPicture)

class DeviceCurrentSineGenerator(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='currentsource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Generators'),
            PartPropertyPartName('Current Sine Generator'),
            PartPropertyHelp('device:Current-Sine-Generator'),
            PartPropertyDefaultReferenceDesignator('CG?'),
            PartPropertyShow(),
            PartPropertyHorizontalOffset(),
            PartPropertyDuration(),
            PartPropertySampleRate(),
            PartPropertyCurrentAmplitude(),
            PartPropertyFrequency(),
            PartPropertyStartTime(-100.),
            PartPropertyStopTime(100.),
            PartPropertyPhase(),
            PartPropertyWaveformType('sine')]+propertiesList,partPicture)
        self['t0']['Visible']=False; self['tf']['Visible']=False

class DeviceMeasurement(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='meas',showReference=False,showports=False)
        Device.__init__(self,
                        netlist,
                        [PartPropertyCategory('Virtual Probe'),
                         PartPropertyPartName('Measure'),
                         PartPropertyHelp('device:Measure-Probe'),
                         PartPropertyDefaultReferenceDesignator('VM?'),
                         PartPropertyDescription('Measure'),
                         PartPropertyCalculationProperties(),
                         PartPropertyWaveformFileName(),
                         PartPropertyWaveformType('file'),
                         PartPropertyWaveformProjectName('')],
                        PartPictureVariableMeasureProbe())

class DeviceOutput(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='voltageoutput',showReference=True,showports=False)
        Device.__init__(self,
                        netlist,
                        [PartPropertyCategory('Ports and Probes'),
                         PartPropertyPartName('Output'),
                         PartPropertyHelp('device:Output-Probe'),
                         PartPropertyDefaultReferenceDesignator('VO?'),
                         PartPropertyDescription('Output'),
                         PartPropertyOnOff('on'),
                         PartPropertyACCoupled(),
                         PartPropertyVoltageGain(1.0),
                         PartPropertyVoltageOffset(0.0),
                         PartPropertyDelay(0.0)],
                        PartPictureVariableProbe())
        self['gain']['Visible']=False
        self['offset']['Visible']=False
        self['td']['Visible']=False
        self['ref']['Visible']=True
        self['state']['Visible']=False

class DeviceWaveform(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='waveform',showReference=True,showports=False)
        Device.__init__(self,
                        netlist,
                        [PartPropertyCategory('Waveforms'),
                         PartPropertyPartName('Waveform'),
                         PartPropertyHelp('device:Waveform'),
                         PartPropertyDefaultReferenceDesignator('VO?'),
                         PartPropertyDescription('Waveform'),
                         PartPropertyCalculationProperties(),
                         PartPropertyOnOff('on'),
                         PartPropertyACCoupled(),
                         PartPropertyVoltageGain(1.0),
                         PartPropertyVoltageOffset(0.0),
                         PartPropertyDelay(0.0),
                         PartPropertyWaveformFileName(),
                         PartPropertyWaveformType('file'),
                         PartPropertyWaveformProjectName('')],
                        PartPictureVariableProbeWaveform())
        self['gain']['Visible']=False
        self['offset']['Visible']=False
        self['td']['Visible']=False
        self['wffile']['Visible']=True
        self['wffile']['KeywordVisible']=False
        self['ref']['Visible']=True
        self['state']['Visible']=False

class DeviceNetName(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='netname',showReference=False,showports=False)
        Device.__init__(self,netlist,[PartPropertyCategory('Miscellaneous'),
                                      PartPropertyPartName('NetName'),
                                      PartPropertyHelp('device:Net-Name'),
                                      PartPropertyNetName('???'),
                                      PartPropertyDescription('Net Name')],
                                      PartPictureVariableNetName())

class DeviceStim(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='stim',showReference=False,showports=False)
        Device.__init__(self,
                        netlist,
                        [PartPropertyCategory('Virtual Probe'),
                         PartPropertyPartName('Stim'),
                         PartPropertyHelp('device:Stim'),
                         PartPropertyDefaultReferenceDesignator('M?'),
                         PartPropertyWeight(1.),
                         PartPropertyDescription('Stim')],
                        PartPictureVariableStim())

class DevicePowerMixedModeConverter(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='mixedmode')
        Device.__init__(self,netlist,[PartPropertyCategory('Miscellaneous'),
                                      PartPropertyPartName('Power Mixed Mode Converter'),
                                      PartPropertyHelp('device:Power-Mixed-Mode-Converter'),
                                      PartPropertyDefaultReferenceDesignator('MM?'),
                                      PartPropertyDescription('Power Mixed Mode Converter'),
                                      PartPropertyPorts(4)],
                                      PartPictureVariablePowerMixedModeConverter())

class DeviceVoltageMixedModeConverter(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='mixedmode voltage')
        Device.__init__(self,netlist,[PartPropertyCategory('Miscellaneous'),
                                      PartPropertyPartName('Voltage Mixed Mode Converter'),
                                      PartPropertyHelp('device:Voltage-Mixed-Mode-Converter'),
                                      PartPropertyDefaultReferenceDesignator('MM?'),
                                      PartPropertyDescription('Voltage Mixed Mode Converter'),
                                      PartPropertyPorts(4)],
                                      PartPictureVariableVoltageMixedModeConverter())

class DeviceVoltageControlledVoltageSourceFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='voltagecontrolledvoltagesource',values=[('gain',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Dependent Sources'),
                                      PartPropertyPartName('VoltageControlledVoltageSource'),
                                      PartPropertyHelp('device:Voltage-Controlled-Voltage-Source'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyVoltageGain(1.0)]+propertiesList,
                                      PartPictureVariableVoltageControlledVoltageSourceFourPort())

class DeviceVoltageAmplifierTwoPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='voltageamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),
                                      PartPropertyPartName('VoltageAmplifier'),
                                      PartPropertyHelp('device:'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyVoltageGain(1.0),
                                      PartPropertyInputImpedance(1e8),
                                      PartPropertyOutputImpedance(0.)]+propertiesList,
                                      PartPictureVariableVoltageAmplifierTwoPort())

class DeviceVoltageAmplifierFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='voltageamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),
                                      PartPropertyPartName('VoltageAmplifier'),
                                      PartPropertyHelp('device:Voltage-Amplifier'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyVoltageGain(1.0),
                                      PartPropertyInputImpedance(1e8),
                                      PartPropertyOutputImpedance(0.)]+propertiesList,
                                      PartPictureVariableVoltageAmplifierFourPort())

class DeviceOperationalAmplifier(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='opamp',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),
                                      PartPropertyPartName('OperationalAmplifier'),
                                      PartPropertyHelp('device:Operational-Amplifier'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyVoltageGain(100e3),
                                      PartPropertyInputImpedance(1e8),
                                      PartPropertyOutputImpedance(0.)]+propertiesList,
                                      PartPictureVariableOperationalAmplifier())

class DeviceCurrentControlledCurrentSourceFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='currentcontrolledcurrentsource',values=[('gain',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Dependent Sources'),
                                      PartPropertyPartName('CurrentControlledCurrentSource'),
                                      PartPropertyHelp('device:Current-Controlled-Current-Source'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyCurrentGain(1.0)]+propertiesList,
                                      PartPictureVariableCurrentControlledCurrentSourceFourPort())

class DeviceCurrentAmplifierTwoPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='currentamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),
                                      PartPropertyPartName('CurrentAmplifier'),
                                      PartPropertyHelp('device:Current-Amplifier'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyCurrentGain(1.0),
                                      PartPropertyInputImpedance(0.),
                                      PartPropertyOutputImpedance(1e8)]+propertiesList,
                                      PartPictureVariableCurrentAmplifierTwoPort())

class DeviceCurrentAmplifierFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='currentamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),
                                      PartPropertyPartName('CurrentAmplifier'),
                                      PartPropertyHelp('device:Current-Amplifier'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyCurrentGain(1.0),
                                      PartPropertyInputImpedance(0.),
                                      PartPropertyOutputImpedance(1e8)]+propertiesList,
                                      PartPictureVariableCurrentAmplifierFourPort())

class DeviceVoltageControlledCurrentSourceFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='voltagecontrolledcurrentsource',values=[('gain',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Dependent Sources'),
                                      PartPropertyPartName('VoltageControlledCurrentSource'),
                                      PartPropertyHelp('device:Voltage-Controlled-Current-Source'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyTransconductance(1.0)]+propertiesList,
                                      PartPictureVariableVoltageControlledCurrentSourceFourPort())

class DeviceTransconductanceAmplifierTwoPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='transconductanceamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),
                                      PartPropertyPartName('TransconductanceAmplifier'),
                                      PartPropertyHelp('device:Transconductance-Amplifier'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyTransconductance(1.0),
                                      PartPropertyInputImpedance(1e8),
                                      PartPropertyOutputImpedance(1e8)]+propertiesList,
                                      PartPictureVariableTransconductanceAmplifierTwoPort())

class DeviceTransconductanceAmplifierFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='transconductanceamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),
                                      PartPropertyPartName('TransconductanceAmplifier'),
                                      PartPropertyHelp('device:Transconductance-Amplifier'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyTransconductance(1.0),
                                      PartPropertyInputImpedance(1e8),
                                      PartPropertyOutputImpedance(1e8)]+propertiesList,
                                      PartPictureVariableTransconductanceAmplifierFourPort())

class DeviceCurrentControlledVoltageSourceFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='currentcontrolledvoltagesource',values=[('gain',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Dependent Sources'),
                                      PartPropertyPartName('CurrentControlledVoltageSource'),
                                      PartPropertyHelp('device:Current-Controlled-Voltage-Source'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyTransresistance(1.0)]+propertiesList,
                                      PartPictureVariableCurrentControlledVoltageSourceFourPort())

class DeviceTransresistanceAmplifierTwoPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='transresistanceamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),
                                      PartPropertyPartName('TransresistanceAmplifier'),
                                      PartPropertyHelp('device:Transresistance-Amplifier'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyTransresistance(1.0),
                                      PartPropertyInputImpedance(0.),
                                      PartPropertyOutputImpedance(0.)]+propertiesList,
                                      PartPictureVariableTransresistanceAmplifierTwoPort())

class DeviceTransresistanceAmplifierFourPort(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='transresistanceamplifier',values=[('gain',True),('zi',True),('zo',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),
                                      PartPropertyPartName('TransresistanceAmplifier'),
                                      PartPropertyHelp('device:Transresistance-Amplifier'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyTransresistance(1.0),
                                      PartPropertyInputImpedance(0.),
                                      PartPropertyOutputImpedance(0.)]+propertiesList,
                                      PartPictureVariableTransresistanceAmplifierFourPort())

class DeviceTransmissionLine(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='tline',values=[('zc',True),('td',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Transmission Lines'),
                                      PartPropertyPartName('TransmissionLine'),
                                      PartPropertyHelp('device:Transmission-Line'),
                                      PartPropertyDefaultReferenceDesignator('T?'),
                                      PartPropertyDelay(),
                                      PartPropertyCharacteristicImpedance()]+propertiesList,partPicture)

class DeviceCOMTransmissionLine(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='tlinecom',values=[('gamma0',True),('a1',True),('a2',True),('tau',True),('zc',True),('d',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Transmission Lines'),
                                      PartPropertyPartName('TransmissionLineCOM'),
                                      PartPropertyHelp('device:Transmission-Line-COM'),
                                      PartPropertyDefaultReferenceDesignator('T?'),
                                      PartPropertyCOMgamma0(),PartPropertyCOMa1(),PartPropertyCOMa2(),PartPropertyCOMtau(),PartPropertyCOMd(),
                                      PartPropertyCharacteristicImpedance()]+propertiesList,partPicture)

class DeviceTransmissionLineLossy(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='tlinelossy',values=[('zc',True),('td',True),('ldbperhzpers',True),('ldbperroothzpers',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Transmission Lines'),
                                      PartPropertyPartName('TransmissionLineLossy'),
                                      PartPropertyHelp('device:Transmission-Line-Lossy'),
                                      PartPropertyDefaultReferenceDesignator('T?'),
                                      PartPropertyDelay(),
                                      PartPropertyCharacteristicImpedance(),
                                      PartPropertyLossdBPerHzPers(),
                                      PartPropertyLossdBPerrootHzPers()]+propertiesList,partPicture)

class DeviceTelegrapherTwoPort(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='telegrapher',values=[('r',True),('rse',True),('l',True),('g',True),('c',True),('df',True),('scale',True),('sect',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Transmission Lines'),
                              PartPropertyPartName('Telegrapher'),
                              PartPropertyHelp('device:Telegrapher---Two-Port'),
                              PartPropertyDefaultReferenceDesignator('T?'),
                              PartPropertyResistance(resistance=0.0),
                              PartPropertyResistanceSkinEffect(),
                              PartPropertyInductance(),
                              PartPropertyConductance(),
                              PartPropertyCapacitance(),
                              PartPropertyDissipationFactor(),
                              PartPropertyScale(),
                              PartPropertySections(sections=0)]+propertiesList,partPicture)

class DeviceTelegrapherFourPort(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='telegrapher',
            values=[('rp',True),('rsep',True),('lp',True),('gp',True),('cp',True),('dfp',True),
                    ('rn',True),('rsen',True),('ln',True),('gn',True),('cn',True),('dfn',True),
                    ('lm',True),('gm',True),('cm',True),('dfm',True),('scale',True),('sect',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Transmission Lines'),
                              PartPropertyPartName('Telegrapher'),
                              PartPropertyHelp('device:Telegrapher---Four-Port'),
                              PartPropertyDefaultReferenceDesignator('T?'),
                              PartPropertyResistance(keyword='rp',descriptionPrefix='positive ',resistance=0.0),
                              PartPropertyResistanceSkinEffect(keyword='rsep',descriptionPrefix='positive '),
                              PartPropertyInductance(keyword='lp',descriptionPrefix='positive '),
                              PartPropertyConductance(keyword='gp',descriptionPrefix='positive '),
                              PartPropertyCapacitance(keyword='cp',descriptionPrefix='positive '),
                              PartPropertyDissipationFactor(keyword='dfp',descriptionPrefix='positive '),
                              PartPropertyResistance(keyword='rn',descriptionPrefix='negative ',resistance=0.0),
                              PartPropertyResistanceSkinEffect(keyword='rsen',descriptionPrefix='negative '),
                              PartPropertyInductance(keyword='ln',descriptionPrefix='negative '),
                              PartPropertyConductance(keyword='gn',descriptionPrefix='negative '),
                              PartPropertyCapacitance(keyword='cn',descriptionPrefix='negative '),
                              PartPropertyDissipationFactor(keyword='dfn',descriptionPrefix='negative '),
                              PartPropertyConductance(keyword='gm',descriptionPrefix='mutual '),
                              PartPropertyInductance(keyword='lm',descriptionPrefix='mutual '),
                              PartPropertyCapacitance(keyword='cm',descriptionPrefix='mutual '),
                              PartPropertyDissipationFactor(keyword='dfm',descriptionPrefix='mutual '),
                              PartPropertyScale(),
                              PartPropertySections(sections=0)]+propertiesList,partPicture)

class DeviceVoltageNoiseSource(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(devicename='voltagesource')
        Device.__init__(self,netlist,[
            PartPropertyCategory('Generators'),
            PartPropertyPartName('Voltage Noise Source'),
            PartPropertyHelp('device:Voltage-Noise-Generator'),
            PartPropertyDefaultReferenceDesignator('VG?'),
            PartPropertyShow(),
            PartPropertyHorizontalOffset(),
            PartPropertyDuration(),
            PartPropertySampleRate(),
            PartPropertyVoltageRms(),
            PartPropertyWaveformType('noise'),
            PartPropertyNoiseFileName()]+propertiesList,partPicture)

class DeviceVoltageOutputProbe(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='differentialvoltageoutput')
        Device.__init__(self,
                        netlist,
                        [PartPropertyCategory('Ports and Probes'),
                         PartPropertyPartName('DifferentialVoltageOutput'),
                         PartPropertyHelp('device:Voltage-Diff-Probe'),
                         PartPropertyDefaultReferenceDesignator('VO?'),
                         PartPropertyDescription('Differential Voltage Probe'),
                         PartPropertyOnOff('on'),
                         PartPropertyACCoupled(),
                         PartPropertyPorts(2),
                         PartPropertyVoltageGain(1.0),
                         PartPropertyVoltageOffset(0.0),
                         PartPropertyDelay(0.0)],
                        PartPictureVariableVoltageProbe())
        self['gain']['Visible']=False
        self['offset']['Visible']=False
        self['td']['Visible']=False
        self['state']['Visible']=False

class DeviceCurrentOutputProbe(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='currentoutput')
        Device.__init__(self,
                        netlist,
                        [PartPropertyCategory('Ports and Probes'),
                         PartPropertyPartName('CurrentOutput'),
                         PartPropertyHelp('device:Current-Probe'),
                         PartPropertyDefaultReferenceDesignator('IO?'),
                         PartPropertyDescription('Current Probe'),
                         PartPropertyOnOff('on'),
                         PartPropertyACCoupled(),
                         PartPropertyPorts(2),
                         PartPropertyTransresistance(1.0),
                         PartPropertyVoltageOffset(0.0),
                         PartPropertyDelay(0.0)],
                        PartPictureVariableCurrentProbe())
        self['gain']['Visible']=False
        self['offset']['Visible']=False
        self['td']['Visible']=False
        self['state']['Visible']=False

class DeviceNPNTransistor(Device):
    def __init__(self,propertiesList):
        netlist=DeviceNetListLine(partname='npntransistor',values=[('gm',True),('rpi',True),('ro',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Amplifiers'),
                                      PartPropertyPartName('NPN Transistor'),
                                      PartPropertyHelp('device:NPN-Transistor'),
                                      PartPropertyDefaultReferenceDesignator('Q?'),
                                      PartPropertyGm(200.0),
                                      PartPropertyRpi(200e3),
                                      PartPropertyOutputResistance(200e3),
                                      PartPropertyPorts(3)]+propertiesList,
                                      PartPictureVariableNPNTransister())

class DeviceRLGCFitFromFile(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='rlgcfit',values=[('file',True),('scale',True)])
        Device.__init__(self,netlist,[PartPropertyDescription('Two Port RLGC fitted transmission line'),
                                      PartPropertyPorts(2),
                                      PartPropertyCategory('Transmission Lines'),
                                      PartPropertyPartName('RLGC Fit'),
                                      PartPropertyHelp('device:RLGC-Fit'),
                                      PartPropertyDefaultReferenceDesignator('T?'),
                                      PartPropertyCalculationProperties(),
                                      PartPropertyFileName(),
                                      PartPropertyScale(scale=1)],
                            PartPictureVariableTransmissionLineTwoPort())

class DeviceNetworkAnalyzer(Device):
    def __init__(self,ports=4):
        netlist=DeviceNetListLine(partname='networkanalyzer',values=[('file',True),('et',True),('pl',True),('cd',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Network Analysis'),
                                      PartPropertyPartName('NetworkAnalyzer'),
                                      PartPropertyHelp('device:Network-Analyzer'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyCalculationProperties(),
                                      PartPropertyCalculationDirection(),
                                      PartPropertyFileName(),
                                      PartPropertyErrorTermsFileName(),
                                      PartPropertyPortsList(','.join([str(p+1) for p in range(ports)])),
                                      PartPropertyDescription('Calibrated Port Network Analyzer'),
                                      PartPropertyPorts(ports,False)],
                                PartPictureVariableNetworkAnalyzer())

class DeviceNetworkAnalyzerModel(Device):
    def __init__(self,ports=4):
        netlist=DeviceNetListLine(partname='networkanalyzermodel',values=[('file',True)])
        Device.__init__(self,netlist,[PartPropertyCategory('Network Analysis'),
                                      PartPropertyPartName('NetworkAnalyzerModel'),
                                      PartPropertyHelp('device:Network-Analyzer-Model'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyCalculationProperties(),
                                      PartPropertyFileName(),
                                      PartPropertyDescription('Network Analyzer Model'),
                                      PartPropertyPorts(ports,False)],
                                      PartPictureVariableNetworkAnalyzer())

class DeviceNetworkAnalyzerDeviceUnderTest(Device):
    def __init__(self,ports=4):
        netlist=DeviceNetListLine(partname='dut',values=[('file',False)])
        Device.__init__(self,netlist,[PartPropertyCategory('Network Analysis'),
                                      PartPropertyPartName('DeviceUnderTest'),
                                      PartPropertyHelp('device:Device-Under-Test'),
                                      PartPropertyDefaultReferenceDesignator('D?'),
                                      PartPropertyCalculationProperties(),
                                      PartPropertyFileName(),
                                      PartPropertyDescription('Network Analyzer Device-Under-Test'),
                                      PartPropertyPorts(ports,False)],
                                      PartPictureVariableDeviceUnderTest())

class DeviceShortStandard(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='shortstd',values=[('od',True),('oz0',True),('ol',True),('f0',True),('l0',True),('l1',True),('l2',True),('l3',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Short Standard'),
                         PartPropertyPorts(1),
                         PartPropertyCategory('Network Analysis'),
                         PartPropertyPartName('ShortStandard'),
                         PartPropertyHelp('device:Short-Standard'),
                         PartPropertyDefaultReferenceDesignator('Short?'),
                         PartPropertyOffsetDelay(0.0),
                         PartPropertyOffsetZ0(50.0),
                         PartPropertyOffsetLoss(0.0),
                         PartPropertyF0(1e9),
                         PartPropertyL0(0.0),
                         PartPropertyL1(0.0),
                         PartPropertyL2(0.0),
                         PartPropertyL3(0.0)],
                        PartPictureVariableStandard())

class DeviceOpenStandard(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='openstd',values=[('od',True),('oz0',True),('ol',True),('f0',True),('c0',True),('c1',True),('c2',True),('c3',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Open Standard'),
                         PartPropertyPorts(1),
                         PartPropertyCategory('Network Analysis'),
                         PartPropertyPartName('OpenStandard'),
                         PartPropertyHelp('device:Open-Standard'),
                         PartPropertyDefaultReferenceDesignator('Open?'),
                         PartPropertyOffsetDelay(0.0),
                         PartPropertyOffsetZ0(50.0),
                         PartPropertyOffsetLoss(0.0),
                         PartPropertyF0(1e9),
                         PartPropertyC0(0.0),
                         PartPropertyC1(0.0),
                         PartPropertyC2(0.0),
                         PartPropertyC3(0.0)],
                        PartPictureVariableStandard())

class DeviceLoadStandard(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='loadstd',values=[('od',True),('oz0',True),('ol',True),('f0',True),('tz',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Load Standard'),
                         PartPropertyPorts(1),
                         PartPropertyCategory('Network Analysis'),
                         PartPropertyPartName('LoadStandard'),
                         PartPropertyHelp('device:Load-Standard'),
                         PartPropertyDefaultReferenceDesignator('Load?'),
                         PartPropertyOffsetDelay(0.0),
                         PartPropertyOffsetZ0(50.0),
                         PartPropertyOffsetLoss(0.0),
                         PartPropertyF0(1e9),
                         PartPropertyTerminationZ(50.0)],
                        PartPictureVariableStandard())

class DeviceThruStandard(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='thrustd',values=[('od',True),('oz0',True),('ol',True),('f0',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Thru Standard'),
                         PartPropertyPorts(2),
                         PartPropertyCategory('Network Analysis'),
                         PartPropertyPartName('ThruStandard'),
                         PartPropertyHelp('device:Thru-Standard'),
                         PartPropertyDefaultReferenceDesignator('Thru?'),
                         PartPropertyOffsetDelay(0.0),
                         PartPropertyOffsetZ0(50.0),
                         PartPropertyOffsetLoss(0.0),
                         PartPropertyF0(1e9)],
                        PartPictureVariableTransmissionLineTwoPort())

class DeviceReflectCalibrationMeasurement(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='calibration',partname='reflect',showReference=False,showports=False,values=[('file',True),('std',True),('pn',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Reflect Calibration Measurement'),
                         PartPropertyPorts(1),
                         PartPropertyCategory('Network Analysis'),
                         PartPropertyPartName('ReflectMeasurement'),
                         PartPropertyHelp('device:Reflect-Measurement'),
                         PartPropertyDefaultReferenceDesignator('Meas?'),
                         PartPropertyCalculationProperties(),
                         PartPropertyFileName(),
                         PartPropertyStandardFileName(),
                         PartPropertyPortNumber(1)],
                        PartPictureVariableMeasurementOnePort())

class DeviceThruCalibrationMeasurement(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='calibration',partname='thru',showReference=False,showports=False,values=[('file',True),('std',True),('pn',True),('opn',True),('ct',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Thru Calibration Measurement'),
                         PartPropertyPorts(2),
                         PartPropertyCategory('Network Analysis'),
                         PartPropertyPartName('ThruMeasurement'),
                         PartPropertyHelp('device:Thru-Measurement'),
                         PartPropertyDefaultReferenceDesignator('Meas?'),
                         PartPropertyCalculationProperties(),
                         PartPropertyFileName(),
                         PartPropertyStandardFileName(),
                         PartPropertyPortNumber(1),
                         PartPropertyOtherPortNumber(2),
                         PartPropertyThruCalculationType()],
                        PartPictureVariableMeasurementTwoPort())

class DeviceXtalkCalibrationMeasurement(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='calibration',partname='xtalk',showReference=False,showports=False,values=[('file',True),('pn',True),('opn',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Xtalk Calibration Measurement'),
                         PartPropertyPorts(2),
                         PartPropertyCategory('Network Analysis'),
                         PartPropertyPartName('XtalkMeasurement'),
                         PartPropertyHelp('device:Xtalk-Measurement'),
                         PartPropertyDefaultReferenceDesignator('Meas?'),
                         PartPropertyCalculationProperties(),
                         PartPropertyFileName(),
                         PartPropertyPortNumber(1),
                         PartPropertyOtherPortNumber(2)],
                        PartPictureVariableMeasurementTwoPort())

class DeviceNetworkAnalyzerStimulus(Device):
    def __init__(self,portNumber=1):
        netlist=DeviceNetListLine(devicename='networkanalyzerport',values=[('pn',True),('state',True),('st',True),('pow',True),('rt',True),('a',True),('ia',True)])
        Device.__init__(self,netlist,
                        [PartPropertyDescription('Network Analyzer Stimulus'),
                         PartPropertyPorts(1),
                         PartPropertyCategory('Network Analysis'),
                         PartPropertyPartName('NetworkAnalyzerStimulus'),
                         PartPropertyHelp('device:Network-Analyzer-Stimulus'),
                         PartPropertyPortNumber(portNumber),
                         PartPropertyDefaultReferenceDesignator('D?'),
                         PartPropertyWaveformType('networkanalyzerport'),
                         PartPropertyHorizontalOffset(),
                         PartPropertyDuration(),
                         PartPropertySampleRate(),
                         PartPropertyStimulusType(),
                         PartPropertyPowerLevel(-10),
                         PartPropertyImpulseVoltageAmplitude(0.2),
                         PartPropertyVoltageAmplitude(0.2),
                         PartPropertyRisetime(0.),
                         PartPropertyOnOff()],
                        partPicture=PartPictureVariableNetworkAnalyzerStimulusOnePort())
    def CreateVisiblePropertiesList(self):
        stimulusType = self['st']['Value']
        if self.partPicture.partPictureSelected != self['st'].validEntries.index(stimulusType):
            self.partPicture.SwitchPartPicture(self['st'].validEntries.index(stimulusType))
        self['pow']['Hidden'] = (stimulusType != 'CW')
        self['rt']['Hidden'] = (stimulusType == 'CW')
        self['a']['Hidden'] = (stimulusType != 'TDRStep')
        self['ia']['Hidden']= (stimulusType != 'TDRImpulse')
        Device.CreateVisiblePropertiesList(self)

class DeviceCTLE(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='ctle',values=[('gdc',True),('gdc2',True),('fz',True),('flf',True),('fp1',True),('fp2',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Continuous Time Linear Equalizer'),
                         PartPropertyPorts(2),
                         PartPropertyCategory('Equalizers'),
                         PartPropertyPartName('CTLE'),
                         PartPropertyHelp('device:CTLE'),
                         PartPropertyDefaultReferenceDesignator('F?'),
                         PartPropertyCtleDCGain1(-2.),
                         PartPropertyCtleDCGain2(0.),
                         PartPropertyCtlefz(1e9/2.5),
                         PartPropertyCtleflf(1e9/80),
                         PartPropertyCtlefp1(1e9/2.5),
                         PartPropertyCtlefp2(1e9)],
                         PartPictureVariableCTLE())

class DeviceFFE(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='ffe',values=[('taps',False),('td',True),('pre',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Feed-forward Linear Equalizer'),
                         PartPropertyPorts(2),
                         PartPropertyCategory('Equalizers'),
                         PartPropertyPartName('FFE'),
                         PartPropertyHelp('device:FFE'),
                         PartPropertyDefaultReferenceDesignator('F?'),
                         PartPropertyFfeTaps('[1.0]'),
                         PartPropertyFfePre(0),
                         PartPropertyFfeTd(0.)],
                         PartPictureVariableFFE())

class DeviceRaisedCosineRisetimeFilter(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='raisedcosinerisetimefilter',values=[('rt',False),('rt_type',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Raised-cosine Risetime filter'),
                        PartPropertyPorts(2),
                        PartPropertyCategory('Filters'),
                        PartPropertyPartName('RaisedCosineRisetimeFilter'),
                        PartPropertyHelp('device:RaisedCosineRisetimeFilter'),
                        PartPropertyDefaultReferenceDesignator('F?'),
                        PartPropertyRisetime(),
                        PartPropertyRisetimeType()],
                        PartPictureVariableRisetimeFilter())

class DeviceGaussianRisetimeFilter(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='gaussianrisetimefilter',values=[('rt',False),('rt_type',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Gaussian Risetime filter'),
                        PartPropertyPorts(2),
                        PartPropertyCategory('Filters'),
                        PartPropertyPartName('GaussianRisetimeFilter'),
                        PartPropertyHelp('device:GaussianRisetimeFilter'),
                        PartPropertyDefaultReferenceDesignator('F?'),
                        PartPropertyRisetime(),
                        PartPropertyRisetimeType()],
                        PartPictureVariableRisetimeFilter())

class DeviceBesselLpFilter(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='bessellp',values=[('order',True),('fc',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Bessel low-pass filter'),
                         PartPropertyPorts(2),
                         PartPropertyCategory('Filters'),
                         PartPropertyPartName('BesselLp'),
                         PartPropertyHelp('device:BesselLp'),
                         PartPropertyDefaultReferenceDesignator('F?'),
                         PartPropertyFilterOrder(4),
                         PartPropertyLpFilterCutoff(1e9)],
                         PartPictureVariableLpFilter())

class DeviceButterworthLpFilter(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='butterworthlp',values=[('order',True),('fc',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Butterworth low-pass filter'),
                         PartPropertyPorts(2),
                         PartPropertyCategory('Filters'),
                         PartPropertyPartName('ButterworthLp'),
                         PartPropertyHelp('device:ButterworthLp'),
                         PartPropertyDefaultReferenceDesignator('F?'),
                         PartPropertyFilterOrder(4),
                         PartPropertyLpFilterCutoff(1e9)],
                         PartPictureVariableLpFilter())

class DeviceLaplace(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='laplace',values=[('eq',False)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Laplace domain equation'),
                         PartPropertyPorts(2),
                         PartPropertyCategory('Filters'),
                         PartPropertyPartName('Laplace'),
                         PartPropertyHelp('device:Laplace'),
                         PartPropertyDefaultReferenceDesignator('F?'),
                         PartPropertyLaplaceEquation('')],
                         PartPictureVariableLaplace())

class DeviceImpulseResponseFilter(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='impulseresponsefilter',
                                  values=[('wffile',False),
                                          ('wfprojname',True),
                                          ('dcgain',True),
                                          ('mults',True),
                                          ('derivative',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Impulse Response Filter'),
                         PartPropertyPorts(2),
                         PartPropertyCategory('Filters'),
                         PartPropertyPartName('ImpulseResponseFilter'),
                         PartPropertyHelp('device:ImpulseResponseFilter'),
                         PartPropertyDefaultReferenceDesignator('F?'),
                         PartPropertyCalculationProperties(),
                         PartPropertyWaveformFileName(),
                         PartPropertyWaveformType('file'),
                         PartPropertyDCGain(),
                         PartPropertyMulTs(),
                         PartPropertyDerivative(),
                         PartPropertyWaveformProjectName('')],
                         PartPictureVariableImpulseResponseFilter())
        self['wffile']['Description']='impulse response file name'

class DeviceWElement(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='w',values=[('file',False),('df',True),('scale',True),('sect',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('W Element'),
                         PartPropertyCategory('Transmission Lines'),
                         PartPropertyPartName('WElement'),
                         PartPropertyHelp('device:W-Element'),
                         PartPropertyDefaultReferenceDesignator('W?'),
                         PartPropertyWElementFileName(),
                         PartPropertyDissipationFactor(),
                         PartPropertyScale(),
                         PartPropertySections(sections=0)]+propertiesList,
                         partPicture)
        self['sect']['Visible']=False
        self['scale']['Visible']=True

class DeviceRelay(Device):
    def __init__(self,propertiesList,partPicture):
        netlist=DeviceNetListLine(partname='relay',values=[('pos',False),('term',True)])
        Device.__init__(self,
                        netlist,
                        [PartPropertyDescription('Relay'),
                         PartPropertyCategory('Miscellaneous'),
                         PartPropertyPartName('Relay'),
                         PartPropertyHelp('device:Relay'),
                         PartPropertyDefaultReferenceDesignator('K?'),
                         PartPropertyResistance(1e9,'term','unconn. termination '),
                         PartPropertyPosition(1)]+propertiesList,
                         partPicture)
        self['term']['KeywordVisible']=True
        self['term']['Visible']=False

class DeviceEyeWaveform(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='eyewaveform',showReference=True,showports=False)
        Device.__init__(self,
                        netlist,
                        [PartPropertyCategory('Waveforms'),
                         PartPropertyPartName('EyeWaveform'),
                         PartPropertyHelp('device:Eye-Waveform'),
                         PartPropertyDefaultReferenceDesignator('Wf?'),
                         PartPropertyDescription('Eye Waveform'),
                         PartPropertyCalculationProperties(),
                         PartPropertyOnOff('on'),
                         PartPropertyEyeOnOff('on'),
                         PartPropertyACCoupled(),
                         PartPropertyVoltageGain(1.0),
                         PartPropertyVoltageOffset(0.0),
                         PartPropertyDelay(0.0),
                         PartPropertyBaudRate(),
                         PartPropertyWaveformFileName(),
                         PartPropertyWaveformType('file'),
                         PartPropertyWaveformProjectName('')],
                        PartPictureVariableEyeWaveform(),
                        EyeDiagramConfiguration())
        self['gain']['Visible']=False
        self['offset']['Visible']=False
        self['td']['Visible']=False
        self['br']['Visible']=True
        self['wffile']['Visible']=True
        self['wffile']['KeywordVisible']=False
        self['ref']['Visible']=True
        self['state']['Visible']=False

class DeviceParallel(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='parallel',values=[('file',True),('sect',True)])
        Device.__init__(self,netlist,[
            PartPropertyDescription('Parallel Devices'),
            PartPropertyCategory('Miscellaneous'),
            PartPropertyPorts(2),
            PartPropertyPartName('Parallel'),
            PartPropertyHelp('device:Parallel'),
            PartPropertyDefaultReferenceDesignator('D?'),
            PartPropertyCalculationProperties(),
            PartPropertySections(1),
            PartPropertyFileName()],PartPictureVariableParallel())


class DeviceSeriesNetListLine(DeviceNetListLine):
    def __init__(self,devicename=None,partname=None,showReference=True,showports=True,values=None):
        DeviceNetListLine.__init__(self,devicename=devicename,partname=partname,showReference=showReference,showports=showports,values=values)
    def NetListLine(self,device):
        picture=device.partPicture.partPictureClassList[device.partPicture.partPictureSelected]
        ports=int(device.PartPropertyByKeyword('ports')['Value'])
        if picture=='PartPictureSeries':
            lp=[p+1 for p in range(ports//2)]
            rp=[p+1 for p in range(ports//2,ports)]
        elif picture == 'PartPictureSeriesAcross':
            lp=[p+1 for p in range(0,ports,2)]
            rp=[p+1 for p in range(1,ports,2)]
        elif picture == 'PartPictureSeriesDownAndUp':
            lp=[p+1 for p in range(ports//2)]
            rp=[p+1 for p in range(ports//2,ports)]
            rp.reverse()
        lprpstr=' lp '+str(lp).strip('[] ').replace(' ','')+' rp '+str(rp).strip('[] ').replace(' ','')
        returnstring=DeviceNetListLine.NetListLine(self,device)+lprpstr
        return returnstring

class DeviceSeries(Device):
    def __init__(self,ports=2):
        netlist=DeviceSeriesNetListLine(partname='series',values=[('file',True),('sect',True)])
        Device.__init__(self,netlist,[
            PartPropertyDescription('Series Devices'),
            PartPropertyCategory('Miscellaneous'),
            PartPropertyPorts(ports,False),
            PartPropertyPartName('Series'),
            PartPropertyHelp('device:Series'),
            PartPropertyDefaultReferenceDesignator('D?'),
            PartPropertyCalculationProperties(),
            PartPropertySections(1),
            PartPropertyFileName()],PartPictureVariableSeries())

class DeviceThru(Device):
    def __init__(self,ports=2):
        netlist=DeviceNetListLine(partname='thru',showports=True)
        Device.__init__(self,netlist,[
            PartPropertyDescription('Thru Device'),
            PartPropertyCategory('Miscellaneous'),
            PartPropertyPorts(ports,False),
            PartPropertyPartName('Thru'),
            PartPropertyHelp('device:Thru'),
            PartPropertyDefaultReferenceDesignator('D?')],
            PartPictureVariableThru(ports))
    @staticmethod
    def ConvertDeviceToThru(device):
            from SignalIntegrity.App.Device import DeviceThru
            ports=int(device['ports']['Value'])
            # ports must be even
            if (ports < 2) or (ports//2*2 != ports):
                return device
            # part picture must be one of the first three pictures (thru with different port ordering)
            if device.partPicture.partPictureSelected > 2:
                return device
            thru_device=DeviceThru(int(ports))
            thru_device['ref']['Value']=device['ref']['Value']
            pinList=copy.deepcopy(thru_device.partPicture.current.pinList)
            pinListSupplied=copy.deepcopy(thru_device.partPicture.current.pinListSupplied)
            thru_device.partPicture.current=copy.copy(device.partPicture.current)
            thru_device.partPicture.current.pinList=pinList
            thru_device.partPicture.current.pinListSupplied=pinListSupplied
            thru_device.partPicture.SwitchPartPicture(thru_device.partPicture.partPictureSelected)
            thru_device.selected=device.selected
            return thru_device
    @staticmethod
    def ConvertDeviceToThruWires(device):
            device=DeviceThru.ConvertDeviceToThru(device)
            if device.partPicture.partPictureClassList[device.partPicture.partPictureSelected] != 'PartPictureThru':
                return None
            pinCoordinates=device.PinCoordinates()
            num_wires = len(pinCoordinates)//2
            leftPins=[pinCoordinates[p] for p in range(num_wires)]
            rightPins=[pinCoordinates[p+num_wires] for p in range(num_wires)]
            from SignalIntegrity.App.Wire import Vertex,Wire
            from SignalIntegrity.App.ProjectFile import WireConfiguration
            wire_list=[WireConfiguration() for _ in range(0)]
            for p in range(num_wires):
                left_pin=pinCoordinates[p]
                right_pin=pinCoordinates[p+num_wires]
                wire=Wire()
                wire['Vertices'].append(Vertex(left_pin,False))
                wire['Vertices'].append(Vertex(right_pin,False))
                wire_list.append(wire)
            return wire_list
class DeviceEyeProbe(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='eyeprobe',showReference=True,showports=False)
        Device.__init__(self,
                        netlist,
                        [PartPropertyCategory('Ports and Probes'),
                         PartPropertyPartName('EyeProbe'),
                         PartPropertyHelp('device:Eye-Probe'),
                         PartPropertyDefaultReferenceDesignator('Vo?'),
                         PartPropertyDescription('Eye Probe'),
                         PartPropertyOnOff('on'),
                         PartPropertyEyeOnOff('on'),
                         PartPropertyACCoupled(),
                         PartPropertyVoltageGain(1.0),
                         PartPropertyVoltageOffset(0.0),
                         PartPropertyDelay(0.0),
                         PartPropertyBaudRate(),
                         PartPropertyPorts(1)],
                        PartPictureVariableEyeProbe(),
                        EyeDiagramConfiguration())
        self['gain']['Visible']=False
        self['offset']['Visible']=False
        self['td']['Visible']=True
        self['br']['Visible']=True
        self['ref']['Visible']=True
        self['state']['Visible']=False

class DeviceDifferentialEyeProbe(Device):
    def __init__(self):
        netlist=DeviceNetListLine(devicename='differentialeyeprobe',showReference=True,showports=False)
        Device.__init__(self,
                        netlist,
                        [PartPropertyCategory('Ports and Probes'),
                         PartPropertyPartName('DifferentialEyeProbe'),
                         PartPropertyHelp('device:Differential-Eye-Probe'),
                         PartPropertyDefaultReferenceDesignator('Vo?'),
                         PartPropertyDescription('Differential Eye Probe'),
                         PartPropertyOnOff('on'),
                         PartPropertyEyeOnOff('on'),
                         PartPropertyACCoupled(),
                         PartPropertyVoltageGain(1.0),
                         PartPropertyVoltageOffset(0.0),
                         PartPropertyDelay(0.0),
                         PartPropertyBaudRate(),
                         PartPropertyPorts(2)],
                        PartPictureVariableDifferentialEyeProbe(),
                        EyeDiagramConfiguration())
        self['gain']['Visible']=False
        self['offset']['Visible']=False
        self['td']['Visible']=True
        self['br']['Visible']=True
        self['ref']['Visible']=True
        self['state']['Visible']=False

class DeviceIdealBalun(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='balun')
        Device.__init__(self,
                        netlist,
                        [PartPropertyCategory('Inductors'),
                         PartPropertyPartName('Balun'),
                         PartPropertyHelp('device:Balun'),
                         PartPropertyDefaultReferenceDesignator('B?'),
                         PartPropertyDescription('Ideal Balun'),
                         PartPropertyPorts(3)
                        ],
                        PartPictureVariableBalun()
                        )

class DeviceReference(Device):
    def __init__(self):
        netlist=DeviceNetListLine(partname='reference')
        Device.__init__(self,
                        netlist,
                        [PartPropertyCategory('Inductors'),
                         PartPropertyPartName('Reference'),
                         PartPropertyHelp('device:Reference'),
                         PartPropertyDefaultReferenceDesignator('Ref?'),
                         PartPropertyDescription('Reference'),
                         PartPropertyPorts(3)
                        ],
                        PartPictureVariableReference()
                        )

class Devices(list):
    def __init__(self,devices):
        list.__init__(self,devices)
    def Enable(self,DeviceName,enable):
        for device in self:
            if device['partname']['Value']==DeviceName:
                device.enabled=enable

DeviceList=Devices([
                DeviceFile([PartPropertyDescription('One Port File'),PartPropertyPorts(1)],PartPictureVariableSpecifiedPorts(1)),
                DeviceFile([PartPropertyDescription('Two Port File'),PartPropertyPorts(2)],PartPictureVariableSpecifiedPorts(2)),
                DeviceFile([PartPropertyDescription('Three Port File'),PartPropertyPorts(3)],PartPictureVariableSpecifiedPorts(3)),
                DeviceFile([PartPropertyDescription('Four Port File'),PartPropertyPorts(4)],PartPictureVariableSpecifiedPorts(4)),
                DeviceFile([PartPropertyDescription('Variable Port File'),PartPropertyPorts(4,False)],PartPictureVariableSpecifiedPorts()),
                DeviceResistor([PartPropertyDescription('One Port Resistor to Ground'),PartPropertyPorts(1)],PartPictureVariableResistorOnePort()),
                DeviceResistor([PartPropertyDescription('Two Port Resistor'),PartPropertyPorts(2)],PartPictureVariableResistorTwoPort()),
                DeviceSkinEffectResistor([PartPropertyDescription('Two Port Skin-Effect Resistor'),PartPropertyPorts(2)],PartPictureVariableResistorTwoPort()),
                DeviceCapacitor([PartPropertyDescription('One Port Capacitor to Ground'),PartPropertyPorts(1)],PartPictureVariableCapacitorOnePort()),
                DeviceCapacitor([PartPropertyDescription('Two Port Capacitor'),PartPropertyPorts(2)],PartPictureVariableCapacitorTwoPort()),
                DeviceInductor([PartPropertyDescription('Two Port Inductor'),PartPropertyPorts(2)],PartPictureVariableInductorTwoPort()),
                DeviceMutual(),
                DeviceIdealTransformer(),
                DeviceGround(),
                DeviceOpen(),
                DeviceDirectionalCoupler([PartPropertyDescription('Three Port Directional Coupler'),PartPropertyPorts(3)],PartPictureVariableDirectionalCouplerThreePort()),
                DeviceDirectionalCoupler([PartPropertyDescription('Four Port Directional Coupler'),PartPropertyPorts(4)],PartPictureVariableDirectionalCouplerFourPort()),
                DeviceTransmissionLine([PartPropertyDescription('Two Port Transmission Line'),PartPropertyPorts(2)],PartPictureVariableTransmissionLineTwoPort()),
                DeviceTransmissionLine([PartPropertyDescription('Four Port Transmission Line'),PartPropertyPorts(4)],PartPictureVariableTransmissionLineFourPort()),
                DeviceCOMTransmissionLine([PartPropertyDescription('Two Port COM Transmission Line'),PartPropertyPorts(2)],PartPictureVariableTransmissionLineTwoPort()),
                DeviceTransmissionLineLossy([PartPropertyDescription('Two Port Lossy Transmission Line'),PartPropertyPorts(2)],PartPictureVariableTransmissionLineTwoPort()),
                DeviceTelegrapherTwoPort([PartPropertyDescription('Two Port Telegrapher'),PartPropertyPorts(2)],PartPictureVariableTransmissionLineTwoPort()),
                DeviceTelegrapherFourPort([PartPropertyDescription('Four Port Telegrapher'),PartPropertyPorts(4)],PartPictureVariableTransmissionLineDifferential()),
                DeviceVoltageSource([PartPropertyDescription('One Port Voltage Source'),PartPropertyPorts(1)],PartPictureVariableVoltageSourceOnePort()),
                DeviceVoltageSource([PartPropertyDescription('Two Port Voltage Source'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceTwoPort()),
                DeviceVoltageNoiseSource([PartPropertyDescription('One Port Voltage Noise Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourceNoiseSourceOnePort()),
                DeviceVoltageNoiseSource([PartPropertyDescription('Two Port Voltage Noise Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceNoiseSourceTwoPort()),
                DeviceVoltageStepGenerator([PartPropertyDescription('One Port Voltage Step Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourceStepGeneratorOnePort()),
                DeviceVoltageStepGenerator([PartPropertyDescription('Two Port Voltage Step Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceStepGeneratorTwoPort()),
                DeviceVoltageDCSource([PartPropertyDescription('One Port Voltage DC Generator'),PartPropertyPorts(1)],PartPictureVariableDCVoltageSourceOnePort()),
                DeviceVoltageDCSource([PartPropertyDescription('Two Port Voltage DC Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceTwoPort()),
                DeviceVoltagePulseGenerator([PartPropertyDescription('One Port Voltage Pulse Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourcePulseGeneratorOnePort()),
                DeviceVoltagePulseGenerator([PartPropertyDescription('Two Port Voltage Pulse Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourcePulseGeneratorTwoPort()),
                DeviceVoltageImpulseGenerator([PartPropertyDescription('One Port Voltage Impulse Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourceImpulseGeneratorOnePort()),
                DeviceVoltageImpulseGenerator([PartPropertyDescription('Two Port Voltage Impulse Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceImpulseGeneratorTwoPort()),
                DeviceVoltagePRBSGenerator([PartPropertyDescription('One Port Voltage PRBS Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourcePRBSGeneratorOnePort()),
                DeviceVoltagePRBSGenerator([PartPropertyDescription('Two Port Voltage PRBS Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourcePRBSGeneratorTwoPort()),
                DeviceVoltageMultiLevelWaveformGenerator([PartPropertyDescription('One Port Voltage Multi Level Waveform Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourcePRBSGeneratorOnePort()),
                DeviceVoltageMultiLevelWaveformGenerator([PartPropertyDescription('Two Port Voltage Multi Level Waveform Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourcePRBSGeneratorTwoPort()),
                DeviceVoltageLevelsMultiLevelWaveformGenerator([PartPropertyDescription('One Port Voltage Levels Multi Level Waveform Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourcePRBSGeneratorOnePort()),
                DeviceVoltageLevelsMultiLevelWaveformGenerator([PartPropertyDescription('Two Port Voltage Levels Multi Level Waveform Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourcePRBSGeneratorTwoPort()),
                DeviceVoltageClockGenerator([PartPropertyDescription('One Port Voltage Clock Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourceClockGeneratorOnePort()),
                DeviceVoltageClockGenerator([PartPropertyDescription('Two Port Voltage Clock Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceClockGeneratorTwoPort()),
                DeviceVoltageSineGenerator([PartPropertyDescription('One Port Voltage Sine Generator'),PartPropertyPorts(1)],PartPictureVariableVoltageSourceSineGeneratorOnePort()),
                DeviceVoltageSineGenerator([PartPropertyDescription('Two Port Voltage Sine Generator'),PartPropertyPorts(2)],PartPictureVariableVoltageSourceSineGeneratorTwoPort()),
                DeviceCurrentSource([PartPropertyDescription('One Port Current Source'),PartPropertyPorts(1)],PartPictureVariableCurrentSourceOnePort()),
                DeviceCurrentSource([PartPropertyDescription('Two Port Current Source'),PartPropertyPorts(2)],PartPictureVariableCurrentSourceTwoPort()),
                DeviceCurrentStepGenerator([PartPropertyDescription('One Port Current Step Generator'),PartPropertyPorts(1)],PartPictureVariableCurrentSourceStepGeneratorOnePort()),
                DeviceCurrentStepGenerator([PartPropertyDescription('Two Port Current Step Generator'),PartPropertyPorts(2)],PartPictureVariableCurrentSourceStepGeneratorTwoPort()),
                DeviceCurrentDCSource([PartPropertyDescription('One Port Current DC Generator'),PartPropertyPorts(1)],PartPictureVariableCurrentSourceOnePort()),
                DeviceCurrentDCSource([PartPropertyDescription('Two Port Current DC Generator'),PartPropertyPorts(2)],PartPictureVariableCurrentSourceTwoPort()),
                DeviceCurrentPulseGenerator([PartPropertyDescription('One Port Current Pulse Generator'),PartPropertyPorts(1)],PartPictureVariableCurrentSourcePulseGeneratorOnePort()),
                DeviceCurrentPulseGenerator([PartPropertyDescription('Two Port Current Pulse Generator'),PartPropertyPorts(2)],PartPictureVariableCurrentSourcePulseGeneratorTwoPort()),
                DeviceCurrentImpulseGenerator([PartPropertyDescription('One Port Current Impulse Generator'),PartPropertyPorts(1)],PartPictureVariableCurrentSourceImpulseGeneratorOnePort()),
                DeviceCurrentImpulseGenerator([PartPropertyDescription('Two Port Current Impulse Generator'),PartPropertyPorts(2)],PartPictureVariableCurrentSourceImpulseGeneratorTwoPort()),
                DeviceCurrentSineGenerator([PartPropertyDescription('One Port Current Sine Generator'),PartPropertyPorts(1)],PartPictureVariableCurrentSourceSineGeneratorOnePort()),
                DeviceCurrentSineGenerator([PartPropertyDescription('Two Port Current Sine Generator'),PartPropertyPorts(2)],PartPictureVariableCurrentSourceSineGeneratorTwoPort()),
                Port(),
                DeviceMeasurement(),
                DeviceOutput(),
                DeviceNetName(),
                DeviceStim(),
                DevicePowerMixedModeConverter(),
                DeviceVoltageMixedModeConverter(),
                DeviceVoltageControlledVoltageSourceFourPort([PartPropertyDescription('Four Port Voltage Controlled Voltage Source'),PartPropertyPorts(4)]),
                DeviceVoltageAmplifierTwoPort([PartPropertyDescription('Two Port Voltage Amplifier'),PartPropertyPorts(2)]),
                DeviceVoltageAmplifierFourPort([PartPropertyDescription('Four Port Voltage Amplifier'),PartPropertyPorts(4)]),
                DeviceOperationalAmplifier([PartPropertyDescription('Operational Amplifier'),PartPropertyPorts(3)]),
                DeviceCurrentControlledCurrentSourceFourPort([PartPropertyDescription('Four Port Current Controlled Current Source'),PartPropertyPorts(4)]),
                DeviceCurrentAmplifierTwoPort([PartPropertyDescription('Two Port Current Amplifier'),PartPropertyPorts(2)]),
                DeviceCurrentAmplifierFourPort([PartPropertyDescription('Four Port Current Amplifier'),PartPropertyPorts(4)]),
                DeviceVoltageControlledCurrentSourceFourPort([PartPropertyDescription('Four Port Voltage Controlled Current Source'),PartPropertyPorts(4)]),
                DeviceTransconductanceAmplifierTwoPort([PartPropertyDescription('Two Port Transconductance Amplifier'),PartPropertyPorts(2)]),
                DeviceTransconductanceAmplifierFourPort([PartPropertyDescription('Four Port Transconductance Amplifier'),PartPropertyPorts(4)]),
                DeviceCurrentControlledVoltageSourceFourPort([PartPropertyDescription('Four Port Current Controlled Voltage Source'),PartPropertyPorts(4)]),
                DeviceTransresistanceAmplifierTwoPort([PartPropertyDescription('Two Port Transresistance Amplifier'),PartPropertyPorts(2)]),
                DeviceTransresistanceAmplifierFourPort([PartPropertyDescription('Four Port Transresistance Amplifier'),PartPropertyPorts(4)]),
                DeviceCurrentOutputProbe(),
                DeviceVoltageOutputProbe(),
                #DeviceNPNTransistor([PartPropertyDescription('NPN Transistor')]),
                DeviceRLGCFitFromFile(),
                DeviceNetworkAnalyzer(),
                DeviceNetworkAnalyzerModel(),
                DeviceShortStandard(),
                DeviceOpenStandard(),
                DeviceLoadStandard(),
                DeviceThruStandard(),
                DeviceReflectCalibrationMeasurement(),
                DeviceThruCalibrationMeasurement(),
                DeviceXtalkCalibrationMeasurement(),
                DeviceNetworkAnalyzerStimulus(),
                DeviceNetworkAnalyzerDeviceUnderTest(),
                DeviceCTLE(),
                DeviceFFE(),
                DeviceBesselLpFilter(),
                DeviceButterworthLpFilter(),
                DeviceLaplace(),
                DeviceWElement([PartPropertyPorts(4,False)],PartPictureVariableWElement()),
                DeviceRelay([PartPropertyPorts(3,False)],PartPictureVariableRelay()),
                DeviceImpulseResponseFilter(),
                DeviceEyeProbe(),
                DeviceDifferentialEyeProbe(),
                DeviceEyeWaveform(),
                DeviceWaveform(),
                DeviceParallel(),
                DeviceSeries(),
                DeviceThru(),
                DeviceRaisedCosineRisetimeFilter(),
                DeviceGaussianRisetimeFilter(),
                DeviceIdealBalun(),
                DeviceReference()
                ])


DeviceListUnknown = Devices([
                DeviceUnknown([PartPropertyDescription('One Port Unknown'),PartPropertyPorts(1)],PartPictureVariableUnknown(1)),
                DeviceUnknown([PartPropertyDescription('Two Port Unknown'),PartPropertyPorts(2)],PartPictureVariableUnknown(2)),
                DeviceUnknown([PartPropertyDescription('Three Port Unknown'),PartPropertyPorts(3)],PartPictureVariableUnknown(3)),
                DeviceUnknown([PartPropertyDescription('Four Port Unknown'),PartPropertyPorts(4)],PartPictureVariableUnknown(4)),
                DeviceUnknown([PartPropertyDescription('Variable Port Unknown'),PartPropertyPorts(4,False)],PartPictureVariableUnknown()),
                ])

DeviceListSystem = Devices([
                DeviceSystem([PartPropertyDescription('One Port System'),PartPropertyPorts(1)],PartPictureVariableSystem(1)),
                DeviceSystem([PartPropertyDescription('Two Port System'),PartPropertyPorts(2)],PartPictureVariableSystem(2)),
                DeviceSystem([PartPropertyDescription('Three Port System'),PartPropertyPorts(3)],PartPictureVariableSystem(3)),
                DeviceSystem([PartPropertyDescription('Four Port System'),PartPropertyPorts(4)],PartPictureVariableSystem(4)),
                DeviceSystem([PartPropertyDescription('Variable Port System'),PartPropertyPorts(4,False)],PartPictureVariableSystem()),
                ])

