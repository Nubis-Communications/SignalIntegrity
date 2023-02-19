"""
ProjectFile.py
"""
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
from SignalIntegrity.App.ProjectFileBase import XMLConfiguration,XMLPropertyDefaultFloat,XMLPropertyDefaultString,XMLPropertyDefaultInt,XMLPropertyDefaultBool,XMLPropertyDefaultCoord
from SignalIntegrity.App.ProjectFileBase import ProjectFileBase,XMLProperty
from SignalIntegrity.App.ToSI import ToSI

import copy
import os

class DeviceNetListKeywordConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'DeviceNetListKeyword',write=False)
        self.Add(XMLPropertyDefaultString('Keyword'))
        self.Add(XMLPropertyDefaultBool('ShowKeyword',True))

class DeviceNetListConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'DeviceNetList',write=False)
        self.Add(XMLPropertyDefaultString('DeviceName'))
        self.Add(XMLPropertyDefaultString('PartName'))
        self.Add(XMLPropertyDefaultBool('ShowReference',True))
        self.Add(XMLPropertyDefaultBool('ShowPorts',True))
        self.Add(XMLProperty('Values',[DeviceNetListKeywordConfiguration() for _ in range(0)],'array',arrayType=DeviceNetListKeywordConfiguration()))

class PartPropertyConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'PartProperty')
        self.Add(XMLPropertyDefaultString('Keyword'))
        self.Add(XMLPropertyDefaultString('PropertyName',write=False))
        self.Add(XMLPropertyDefaultString('Description',write=False))
        self.Add(XMLPropertyDefaultString('Value'))
        self.Add(XMLPropertyDefaultBool('Hidden',write=False))
        self.Add(XMLPropertyDefaultBool('Visible'))
        self.Add(XMLPropertyDefaultBool('KeywordVisible'))
        self.Add(XMLPropertyDefaultString('Type',write=False))
        self.Add(XMLPropertyDefaultString('Unit',write=False))
        self.Add(XMLPropertyDefaultBool('InProjectFile',True,False))
    def OutputXML(self,indent):
        if self['InProjectFile']:
            return XMLConfiguration.OutputXML(self, indent)
        else:
            return []

class PartPinConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'PartPin',write=False)
        self.Add(XMLPropertyDefaultInt('Number'))
        self.Add(XMLPropertyDefaultCoord('ConnectionPoint'))
        self.Add(XMLPropertyDefaultString('Orientation'))
        self.Add(XMLPropertyDefaultBool('NumberVisible'))
        self.Add(XMLPropertyDefaultBool('Visible'))
        self.Add(XMLPropertyDefaultBool('NumberingMatters'))
        self.Add(XMLPropertyDefaultString('NumberSide','n'))

class PartPictureConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'PartPicture')
        self.Add(XMLPropertyDefaultInt('Index',None))
        self.Add(XMLPropertyDefaultString('ClassName',write=False))
        self.Add(XMLPropertyDefaultCoord('Origin'))
        self.Add(XMLPropertyDefaultInt('Orientation'))
        self.Add(XMLPropertyDefaultBool('MirroredVertically',False))
        self.Add(XMLPropertyDefaultBool('MirroredHorizontally',False))

class DeviceConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Device')
        self.Add(XMLPropertyDefaultString('ClassName'))
        self.SubDir(PartPictureConfiguration())
        self.Add(XMLProperty('PartProperties',[PartPropertyConfiguration() for _ in range(0)],'array',arrayType=PartPropertyConfiguration()))
        self.SubDir(VariablesConfiguration())
        self.SubDir(DeviceNetListConfiguration())
        import SignalIntegrity.App.Preferences
        for key in SignalIntegrity.App.Preferences['Devices'].dict.keys():
            self.SubDir(copy.deepcopy(SignalIntegrity.App.Preferences['Devices'][key]),makeOnRead=True)

class VertexConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Vertex')
        self.Add(XMLPropertyDefaultCoord('Coord'))
        self.Add(XMLPropertyDefaultBool('Selected',False,False))
#     def OutputXML(self,indent):
#         return [indent+'<Vertex>'+str(self.dict['Coord'].dict['value'])+'</Vertex>']

class WireConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Wire')
        self.Add(XMLProperty('Vertices',[VertexConfiguration() for _ in range(0)],'array',arrayType=VertexConfiguration()))

class DrawingPropertiesConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'DrawingProperties')
        self.Add(XMLPropertyDefaultFloat('Grid',16.))
        self.Add(XMLPropertyDefaultInt('Originx',1))
        self.Add(XMLPropertyDefaultInt('Originy',4))
        self.Add(XMLPropertyDefaultString('Geometry','711x363+27+56'))

class SchematicConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Schematic')
        self.Add(XMLProperty('Devices',[DeviceConfiguration() for _ in range(0)],'array',arrayType=DeviceConfiguration()))
        self.Add(XMLProperty('Wires',[WireConfiguration() for _ in range(0)],'array',arrayType=WireConfiguration()))

class DrawingConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Drawing')
        self.SubDir(DrawingPropertiesConfiguration())
        self.SubDir(SchematicConfiguration())

class CalculationPropertiesBase(XMLConfiguration):
    def __init__(self,Name,preferences=False):
        XMLConfiguration.__init__(self,Name)
        if not preferences:
            self.Add(XMLPropertyDefaultFloat('EndFrequency',20e9))
            self.Add(XMLPropertyDefaultInt('FrequencyPoints',2000))
            self.Add(XMLPropertyDefaultFloat('UserSampleRate',40e9))
            self.Add(XMLPropertyDefaultFloat('UserSamplePeriod',write=False))
            self.Add(XMLPropertyDefaultFloat('BaseSampleRate',write=False))
            self.Add(XMLPropertyDefaultFloat('BaseSamplePeriod',write=False))
            self.Add(XMLPropertyDefaultInt('TimePoints',write=False))
            self.Add(XMLPropertyDefaultFloat('FrequencyResolution',write=False))
            self.Add(XMLPropertyDefaultFloat('ImpulseResponseLength',write=False))
            self.CalculateOthersFromBaseInformation()
    def InitFromXML(self,element):
        XMLConfiguration.InitFromXML(self,element)
        self.CalculateOthersFromBaseInformation()
        return self
    def CalculateOthersFromBaseInformation(self):
        self['BaseSampleRate']=self['EndFrequency']*2
        self['BaseSamplePeriod']=1./self['BaseSampleRate']
        self['UserSamplePeriod']=1./self['UserSampleRate']
        self['TimePoints']=self['FrequencyPoints']*2
        self['FrequencyResolution']=self['EndFrequency']/self['FrequencyPoints']
        self['ImpulseResponseLength']=1./self['FrequencyResolution']
    def InitFromXml(self,calculationPropertiesElement):
        endFrequency=20e9
        frequencyPoints=400
        userSampleRate=40e9
        for calculationProperty in calculationPropertiesElement:
            if calculationProperty.tag == 'end_frequency':
                endFrequency=float(calculationProperty.text)
            elif calculationProperty.tag == 'frequency_points':
                frequencyPoints=int(calculationProperty.text)
            elif calculationProperty.tag == 'user_samplerate':
                userSampleRate = float(calculationProperty.text)
        self['EndFrequency']=endFrequency
        self['FrequencyPoints']=frequencyPoints
        self['UserSampleRate']=userSampleRate
        self.CalculateOthersFromBaseInformation()
        return self
    def Dictionary(self):
        return {name:self[name] for name in ['EndFrequency','FrequencyPoints','UserSampleRate']}

class CalculationProperties(CalculationPropertiesBase):
    def __init__(self):
        CalculationPropertiesBase.__init__(self,'CalculationProperties')

class PostProcessingLineConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'PostProcessingLine')
        self.Add(XMLPropertyDefaultString('Line',''))

class PostProcessingConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'PostProcessing')
        self.Add(XMLProperty('Lines',[PostProcessingLineConfiguration() for _ in range(0)],'array',arrayType=PostProcessingLineConfiguration()))
    def GetTextString(self):
        try:
            lines=[ppline['Line'] for ppline in self['Lines']]
            goodlines=[]
            for line in lines:
                if not line is None:
                    goodlines.append(line)
            textstr='\n'.join(goodlines)
        except:
            textstr=''
        return textstr
    def PutTextString(self,textstr):
        lines=textstr.split('\n')
        lines=[str(line) for line in lines]
        goodlines=[]
        for line in lines:
            if line != '':
                goodlines.append(line)
        pplines=[PostProcessingLineConfiguration() for line in goodlines]
        for l in range(len(goodlines)):
            pplines[l]['Line']=lines[l]
        self['Lines']=pplines
    def NetListLines(self):
        try:
            lines=[ppline['Line'] for ppline in self['Lines']]
            goodlines=[]
            for line in lines:
                if not line is None:
                    goodlines.append('post '+line)
        except:
            goodlines=[]
        return goodlines
    def OutputXML(self,indent):
        if len(self['Lines']) > 0:
            return XMLConfiguration.OutputXML(self, indent)
        else:
            return []

class VariableConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Variable')
        self.Add(XMLPropertyDefaultString('Description',''))
        self.Add(XMLPropertyDefaultBool('Visible',True))
        self.Add(XMLPropertyDefaultString('Name',''))
        self.Add(XMLPropertyDefaultString('Type','float'))
        self.Add(XMLPropertyDefaultString('Value','0'))
        self.Add(XMLPropertyDefaultString('Units',''))
        self.Add(XMLPropertyDefaultBool('ReadOnly',False))
    def InitFromPartProperty(self,variableName,partProperty):
        self['Visible']=partProperty['Visible']
        self['Description']=partProperty['Description']
        self['Name']=variableName
        self['Type']=partProperty['Type']
        self['Value']=partProperty['Value']
        self['Units']=partProperty['Unit']
        if self['Units']==None:
            self['Units']=''
        self['ReadOnly']=False
        return self
    def CheckValidity(self):
        if not isinstance(self['Description'],str): return False
        if not isinstance(self['Name'],str): return False
        if len(self['Name']) == 0: return False
        if not isinstance(self['Type'],str): return False
        if not self['Type'] in ['int','float','string','file']: return False
        if not isinstance(self['Value'],str): return False
        if (len(self['Value'])>0) and (self['Value'][0]== '=') and (len(self['Value']) == 1): return False
        if not isinstance(self['Units'],str): return False
        return True
    def Value(self,forDisplay=False,resolveVariable=True):
        value=self.GetValue('Value')
        type=self.GetValue('Type')
        if resolveVariable and (len(value)>0) and (value[0]=='='):
            import SignalIntegrity.App.Project
            if value[1:] in SignalIntegrity.App.Project['Variables'].Names():
                value=SignalIntegrity.App.Project['Variables'].VariableByName(value[1:]).Value(forDisplay,False)
        if type=='file':
            value=('/'.join(str(value).split('\\')))
        if forDisplay and (type=='float'):
            value = str(ToSI(float(value),self.GetValue('Units')))
        return value
    def NetListLine(self):
        value=str(self.GetValue('Value'))
        if (self['Type'] == 'float'):
            try:
                value = str(ToSI(float(value),self.GetValue('Unit'),letterPrefixes=False))
            except:
                value = ''
        elif self['Type'] == 'int':
            value = str(int(value))
        elif self['Type'] == 'file':
            value=('/'.join(str(os.path.abspath(value)).split('\\')))
            if ' ' in value:
                value="'"+value+"'"
        if value != '':
            return '$'+self['Name']+'$ '+ value
        else:
            return value
    def DisplayString(self,displayVariable=True,resolveVariable=True,visible=True):
        result=''
        if visible or self.GetValue('Visible'):
            if displayVariable and (self.GetValue('Name') != None) and (self.GetValue('Name') != 'None'):
                result=result+self.GetValue('Name')
            value=self.GetValue('Value')
            type=self.GetValue('Type')
            prefix,suffix='',''
            if (len(value)>0) and (value[0]=='='):
                if resolveVariable and displayVariable:
                    result=result+value+' '
                    import SignalIntegrity.App.Project
                    if value[1:] in SignalIntegrity.App.Project['Variables'].Names():
                        value = SignalIntegrity.App.Project['Variables'].VariableByName(value[1:]).DisplayString(False,False)
                        if (len(value)>0) and (value[0]=='='):
                            value=value[1:]
                        result=result+'('+value+')'
                        return result
            elif displayVariable:
                result=result+' '
            if (len(value)>0) and (value[0]=='='):
                value=value[1:]
                prefix,suffix='(',')'
                result=result+' ('+value+')'
                return result
            elif type == 'file':
                value=('/'.join(str(self.GetValue('Value')).split('\\'))).split('/')[-1]
            elif type == 'float':
                import SignalIntegrity.App.Project
                value = str(ToSI(float(self.GetValue('Value')),self.GetValue('Units'),round=SignalIntegrity.App.Preferences['Appearance.RoundDisplayedValues']))
            if not value == None:
                result=result+prefix+value+suffix
        return result

class VariablesConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Variables')
        self.Add(XMLProperty('Items',[VariableConfiguration() for _ in range(0)],'array',arrayType=VariableConfiguration()))
    def NetListLines(self):
        return ['var '+variable.NetListLine() for variable in self['Items']]
    def Names(self):
        return [variable['Name'] for variable in self['Items']]
    def VariableByName(self,name):
        return self['Items'][self.Names().index(name)]
    def OutputXML(self,indent):
        if len(self['Items']) > 0:
            return XMLConfiguration.OutputXML(self, indent)
        else:
            return []
    def DisplayStrings(self,displayVariable=True,resolveVariable=True,visible=True):
        import SignalIntegrity.App.Project
        textLimit = SignalIntegrity.App.Preferences['Appearance.LimitText']
        result=[]
        for variable in self['Items']:
            displayString=variable.DisplayString(displayVariable,resolveVariable,visible)
            if displayString != '':
                if len(displayString) > textLimit:
                    displayString = displayString[:textLimit]+'...'
                result.append(displayString)
        return result
    def Dictionary(self,variableList=None):
        if variableList == None:
            variableList=self['Items']
        args={}
        for variable in variableList:
            name=variable['Name']
            value=variable.Value()
            if variable['Type'] == 'file':
                value=os.path.abspath(value)
            args[name]=value
        return args

class EquationLineConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'EquationLine')
        self.Add(XMLPropertyDefaultString('Line',''))

class EquationsConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Equations')
        self.Add(XMLPropertyDefaultBool('AutoDebug',True))
        self.Add(XMLPropertyDefaultBool('Valid',False,write=False))
        self.Add(XMLProperty('Lines',[EquationLineConfiguration() for _ in range(0)],'array',arrayType=EquationLineConfiguration()))
    def GetTextString(self):
        try:
            lines=[ppline['Line'] for ppline in self['Lines']]
            goodlines=[]
            for line in lines:
                if not line is None:
                    goodlines.append(line)
            textstr='\n'.join(goodlines)
        except:
            textstr=''
        return textstr
    def PutTextString(self,textstr):
        lines=textstr.split('\n')
        lines=[str(line) for line in lines]
        goodlines=[]
        for line in lines:
            if line != '':
                goodlines.append(line)
        pplines=[EquationLineConfiguration() for line in goodlines]
        for l in range(len(goodlines)):
            pplines[l]['Line']=lines[l]
        self['Lines']=pplines

class ProjectFile(ProjectFileBase):
    def __init__(self):
        ProjectFileBase.__init__(self,'si')
        self.SubDir(DrawingConfiguration())
        self.SubDir(CalculationProperties())
        self.SubDir(PostProcessingConfiguration())
        self.SubDir(VariablesConfiguration())
        self.SubDir(EquationsConfiguration())
        # for backwards compatibility with projects with global eye diagram configurations, allow for these projects to be
        # read properly - the eye diagram configuration will then be assigned to each device, and when the project file is
        # saved, the global eye diagram configuration will be removed
        import SignalIntegrity.App.Preferences
        self.SubDir(copy.deepcopy(SignalIntegrity.App.Preferences['Devices']['EyeDiagram']),makeOnRead=True)
        # end of backward compatibility to be removed some day
        from SignalIntegrity.App.Wire import WireList
        self['Drawing.Schematic'].dict['Wires']=WireList()

    def Read(self,filename=None):
        if not filename is None:
            ProjectFileBase.Read(self, filename)
        return self

    def Write(self,app,filename=None):
        self['Drawing.Schematic.Devices']=[DeviceConfiguration() for _ in range(len(app.Drawing.schematic.deviceList))]
        for d in range(len(self['Drawing.Schematic.Devices'])):
            deviceProject=self['Drawing.Schematic.Devices'][d]
            device=app.Drawing.schematic.deviceList[d]
            if not device.configuration is None:
                if isinstance(device.configuration,list):
                    for config in device.configuration:
                        deviceProject.SubDir(config)
                else:
                    deviceProject.SubDir(device.configuration)
            deviceProject['ClassName']=device.__class__.__name__
            partPictureProject=deviceProject['PartPicture']
            partPicture=device.partPicture
            partPictureProject['Index']=partPicture.partPictureSelected
            partPictureProject['ClassName']=partPicture.partPictureClassList[partPicture.partPictureSelected]
            partPictureProject['Origin']=partPicture.current.origin
            partPictureProject['Orientation']=partPicture.current.orientation
            partPictureProject['MirroredVertically']=partPicture.current.mirroredVertically
            partPictureProject['MirroredHorizontally']=partPicture.current.mirroredHorizontally
            deviceProject['PartProperties']=device.propertiesList
            deviceProject['Variables']['Items']=device.variablesList
            deviceNetListProject=deviceProject['DeviceNetList']
            deviceNetList=device.netlist
            for n in deviceNetList.dict:
                deviceNetListProject[n]=deviceNetList[n]
        if not filename is None:
            ProjectFileBase.Write(self,filename)
        return self

    @staticmethod
    def EvaluateSafely(equations,sendargs,returnargs):
        for argkey in sendargs.keys():
            arg=sendargs[argkey]
            if isinstance(arg,str):
                exec(argkey+' = "'+arg+'"')
            else:
                exec(argkey+' = '+str(arg))
        exec(equations)
        for argkey in returnargs.keys():
            try:
                exec(str("returnargs[argkey] = eval(argkey)"))
            except NameError:
                pass
        return returnargs

    def EvaluateEquations(self,equations=None):
        if (equations != None) or (self['Equations.Lines'] != []):
            variablesDefinition=[(variable['Name'],variable['Value']) for variable in self['Variables.Items']]
            equationsDefinition=self['Equations'].GetTextString() if equations == None else equations
            try:
                calculate = (variablesDefinition != self.variablesDefinition) or (equationsDefinition != self.equationsDefinition)
            except:
                calculate=True
            if calculate:
                self['Equations.Valid']=True
                self.variablesDefinition = variablesDefinition
                self.equationsDefinition = equationsDefinition
                self['Equations.Valid']=False
                sendargs={}; returnargs={}
                for variable in self['Variables.Items']:
                    if variable['ReadOnly']:
                        returnargs[variable['Name']]=None
                    if not variable['ReadOnly']:
                        if variable['Type'] in ['file','string']:
                            sendargs[variable['Name']]=str(variable['Value'])
                        elif variable['Type'] == 'float':
                            sendargs[variable['Name']]=float(variable['Value'])
                        elif variable['Type'] == 'int':
                            sendargs[variable['Name']]=int(variable['Value'])
                try:
                    if equations == None:
                        equations=self['Equations'].GetTextString()
                    returnargs=self.EvaluateSafely(equations,sendargs,returnargs)
                except Exception as e:
                    print(e)
                    return e
                for variable in self['Variables.Items']:
                    if variable['ReadOnly'] and returnargs[variable['Name']] != None:
                        variable['Value']=returnargs[variable['Name']]
                self['Equations.Valid']=True
        else:
            self['Equations.Valid']=True
        return None
