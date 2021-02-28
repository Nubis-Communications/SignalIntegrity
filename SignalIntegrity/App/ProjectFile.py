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

import copy

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
        self.SubDir(DeviceNetListConfiguration())

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

class PageConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('Page')
        self.Add(XMLPropertyDefaultString('Name','Page 1'))
        self.SubDir(DrawingConfiguration())
        from SignalIntegrity.App.Wire import WireList
        self['Drawing.Schematic'].dict['Wires']=WireList()

class ProjectConfiguration(XMLConfiguration):
    def __init__(self):
        super().__init__('Project')
        self.Add(XMLPropertyDefaultString('Name','Main'))
        self.SubDir(CalculationProperties())
        self.SubDir(PostProcessingConfiguration())
        self.Add(XMLProperty('Pages',[PageConfiguration() for _ in range(0)],'array',arrayType=PageConfiguration()))
        self.Add(XMLPropertyDefaultInt('Selected',0))

class ProjectFile(ProjectFileBase):
    def __init__(self):
        ProjectFileBase.__init__(self,'si')
        self.SubDir(DrawingConfiguration())
        self.SubDir(CalculationProperties())
        self.SubDir(PostProcessingConfiguration())
        self.Add(XMLProperty('Projects',[ProjectConfiguration() for _ in range(0)],'array',arrayType=ProjectConfiguration()))
        self.Add(XMLPropertyDefaultInt('Selected',0))
        self.Add(XMLPropertyDefaultString('FileName',write=False))
        from SignalIntegrity.App.Wire import WireList
        self['Drawing.Schematic'].dict['Wires']=WireList()
    def New(self):
        self.dict['Projects']=XMLProperty('Projects',[ProjectConfiguration()],'array',arrayType=ProjectConfiguration())
        self['Selected']=0
        selected=self['Projects'][0]
        selected.dict['CalculationProperties']=self['CalculationProperties']
        selected.dict['PostProcessing']=self['PostProcessing']
        selected.dict['Pages']=XMLProperty('Pages',[PageConfiguration()],'array',arrayType=PageConfiguration())
        selected['Selected']=0
        selectedPage=selected['Pages'][0]
        selectedPage['Name']='Page 1'
        selectedPage.dict['Drawing']=self['Drawing']
        return self

    def Read(self,filename=None):
        if not filename is None:
            ProjectFileBase.Read(self, filename)
            self['FileName']=filename
            if self['Projects'] == []:
                # this is legacy format
                self.dict['Projects']=XMLProperty('Projects',[ProjectConfiguration()],'array',arrayType=ProjectConfiguration())
                self['Selected']=0
                selected=self['Projects'][0]
                selected.dict['CalculationProperties']=self['CalculationProperties']
                selected.dict['PostProcessing']=self['PostProcessing']
                selected.dict['Pages']=XMLProperty('Pages',[PageConfiguration()],'array',arrayType=PageConfiguration())
                selected['Selected']=0
                selectedPage=selected['Pages'][0]
                selectedPage['Name']='Page 1'
                for device in self['Drawing.Schematic.Devices']:
                    for prop in device['PartProperties']:
                        if prop['Keyword'] == 'file':
                            from SignalIntegrity.App.PartProperty import PartPropertyFileType,PartPropertySubprojectName
                            if prop['Value'].endswith('.si'):
                                fileTypeProp=PartPropertyFileType('SelectedProjectFile')
                            else:
                                fileTypeProp=PartPropertyFileType('SParameterFile')
                            device['PartProperties'].extend([fileTypeProp,PartPropertySubprojectName()])
                            break
                selectedPage.dict['Drawing']=self['Drawing']
            else:
                selected=self['Selected']
                selectedProject=self['Projects'][selected]
                self.dict['CalculationProperties']=selectedProject['CalculationProperties']
                self.dict['PostProcessing']=selectedProject['PostProcessing']
                selectedPage=selectedProject['Pages'][selectedProject['Selected']]
                self.dict['Drawing']=selectedPage['Drawing']
        return self

    def Select(self,subProjectName):
        if subProjectName in [None,'']:
            return self
        selectIndex=None
        for p in range(len(self['Projects'])):
            if self['Projects'][p]['Name']==subProjectName:
                selectIndex=p
                break
        if selectIndex==None:
            return None
        if selectIndex==self['Selected']:
            return self
        currentlySelectedProject=self['Projects'][self['Selected']]
        currentlySelectedProject.dict['CalculationProperties']=self['CalculationProperties']
        currentlySelectedProject.dict['PostProcessing']=self['PostProcessing']
        currentlySelectedPage=currentlySelectedProject['Pages'][currentlySelectedProject['Selected']]
        currentlySelectedPage.dict['Drawing']=self['Drawing']
        self['Selected']=selectIndex
        newlySelectedProject=self['Projects'][self['Selected']]
        self.dict['CalculationProperties']=newlySelectedProject['CalculationProperties']
        self.dict['PostProcessing']=newlySelectedProject['PostProcessing']
        newlySelectedPage=newlySelectedProject['Pages'][newlySelectedProject['Selected']]
        self.dict['Drawing']=newlySelectedPage['Drawing']
        return self

    def Write(self,app,filename=None):
        self['Drawing.Schematic.Devices']=[DeviceConfiguration() for _ in range(len(app.Drawing.schematic.deviceList))]
        for d in range(len(self['Drawing.Schematic.Devices'])):
            deviceProject=self['Drawing.Schematic.Devices'][d]
            device=app.Drawing.schematic.deviceList[d]
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
            deviceNetListProject=deviceProject['DeviceNetList']
            deviceNetList=device.netlist
            for n in deviceNetList.dict:
                deviceNetListProject[n]=deviceNetList[n]
        selectedProject=self['Projects'][self['Selected']]
        selectedProject.dict['CalculationProperties']=self['CalculationProperties']
        selectedProject.dict['PostProcessing']=self['PostProcessing']
        selectedPage=selectedProject['Pages'][selectedProject['Selected']]
        selectedPage.dict['Drawing']=self['Drawing']
        if not filename is None:
            projectCopy=copy.deepcopy(self)
            del projectCopy.dict['CalculationProperties']
            del projectCopy.dict['PostProcessing']
            del projectCopy.dict['Drawing']
            # Now, after all of this, decide whether we want to save in legacy format
            legacyFormat=True
            if legacyFormat and len(self['Projects']) != 1: legacyFormat = False
            if legacyFormat and self['Projects'][0]['Name'] != 'Main': legacyFormat = False
            if legacyFormat and len(self['Projects'][0]['Pages']) != 1: legacyFormat = False
            if legacyFormat:
                for device in self['Projects'][0]['Pages'][0]['Drawing.Schematic.Devices']:
                    for prop in device['PartProperties']:
                        if prop['Keyword'] == 'filetype':
                            if not prop['Value'] in ['SParameterFile','SelectedProjectFile']:
                                legacyFormat=False
                                break;
            # if there is only one project, the project has the default name, and has only one page,
            # then store it in the legacy format.
            if legacyFormat:
                projectCopy.dict['CalculationProperties']=self['Projects'][0]['CalculationProperties']
                projectCopy.dict['PostProcessing']=self['Projects'][0]['PostProcessing']
                projectCopy.dict['Drawing']=self['Projects'][0]['Pages'][0]['Drawing']
                for device in self['Drawing.Schematic.Devices']:
                    for prop in device['PartProperties']:
                        if prop['Keyword'] in ['filetype','subproject']:
                            prop.write=False
                del(projectCopy.dict['Selected'])
                del(projectCopy.dict['Projects'])
                projectCopy.baseName='Project'
            ProjectFileBase.Write(projectCopy,filename)
        return self
