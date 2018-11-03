"""
ProjectFileBase.py
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
import xml.etree.ElementTree as et

class XMLProperty(object):
    def __init__(self,propertyName,propertyValue=None,propertyType=None,arrayType=None):
        self.dict={}
        if not propertyValue == None:
            if propertyType == None:
                self.Default(propertyName,propertyValue,'string',arrayType)
            else:
                self.Default(propertyName,propertyValue,propertyType,arrayType)
    def Default(self,propertyName,propertyValue,propertyType,arrayType):
        self.dict['name']=propertyName
        self.dict['type']=propertyType
        self.dict['value']=propertyValue
        self.dict['arrayType']=arrayType
        self.UpdateValue()

    def OutputXML(self,indent):
        lines=[]
        if 'value' in self.dict:
            elementPropertyValue = self.dict['value']
        else:
            elementPropertyValue = None
        if isinstance(elementPropertyValue,list):
            lines=lines+[indent+'<'+self.dict['name']+'>']
            for item in elementPropertyValue:
                lines=lines+item.OutputXML(indent+ProjectFileBase.indent)
            lines=lines+[indent+'</'+self.dict['name']+'>']
        else:
            lines=lines+[indent+'<'+self.dict['name']+'>'+elementPropertyValue+'</'+self.dict['name']+'>']
        return lines

    def InitFromXML(self,element):
        try:
            if 'type' in self.dict and self.dict['type']=='array':
                self.dict['value']=[]
                for child in element:
                    import copy
                    self.dict['value'].append(copy.deepcopy(self.dict['arrayType']).InitFromXML(child))
            else:
                self.dict['value'] = element.text
            return self.UpdateValue()
        except:
            return self
    def UpdateValue(self):
        if not 'value' in self.dict:
            self.value = None
        elif 'type' in self.dict:
            elementPropertyValue = self.dict['value']
            if elementPropertyValue=='None':
                self.value = None
                return self
            elementPropertyType = self.dict['type']
            if elementPropertyType == 'int':
                self.value = int(elementPropertyValue)
            elif elementPropertyType == 'float':
                self.value = float(elementPropertyValue)
            elif elementPropertyType == 'string':
                self.value = str(elementPropertyValue)
            elif elementPropertyType == 'bool':
                if isinstance(elementPropertyValue,str):
                    elementPropertyValue = elementPropertyValue == 'True'
                self.value = bool(elementPropertyValue)
            else:
                self.value = elementPropertyValue
        return self
    def Print(self):
        for item in self.dict:
            print(self.dict[item])
    def PrintFullInformation(self,prefix):
        if 'type' in self.dict:
            propertyType=self.dict['type']
        else:
            propertyType='string'
        if 'value' in self.dict:
            propertyValue=self.dict['value']
        else:
            propertyValue='None'
        if isinstance(propertyValue,list):
            for i in range(len(propertyValue)):
                propertyValue[i].PrintFullInformation(prefix+'['+str(i)+']')
        else:
            print(prefix + ' <' + propertyType + '> = ' + propertyValue)

    def GetPropertyValue(self,path):
        if path in self.dict:
            return self.dict[path]
        else:
            return None
    def GetValue(self,path):
        return self.value

    def SetValue(self,path,value):
        self.dict['value']=str(value)
        self.UpdateValue()

class XMLPropertyDefault(XMLProperty):
    def __init__(self,name,typeString,value=None,arrayType=None):
        if value==None:
            strValue='None'
        else:
            strValue = str(value)
        XMLProperty.__init__(self,name,strValue,typeString,arrayType)

class XMLPropertyDefaultFloat(XMLPropertyDefault):
    def __init__(self,name,value=None):
        XMLPropertyDefault.__init__(self,name,'float',value)

class XMLPropertyDefaultInt(XMLPropertyDefault):
    def __init__(self,name,value=None):
        XMLPropertyDefault.__init__(self,name,'int',value)

class XMLPropertyDefaultString(XMLPropertyDefault):
    def __init__(self,name,value=None):
        XMLPropertyDefault.__init__(self,name,'string',value)

class XMLPropertyDefaultBool(XMLPropertyDefault):
    def __init__(self,name,value=None):
        XMLPropertyDefault.__init__(self,name,'bool',value)

class XMLPropertyDefaultArray(XMLPropertyDefault):
    def __init__(self,name,value=None,arrayType=None):
        XMLPropertyDefault.__init__(self,name,'array',value,arrayType)

class XMLConfiguration(object):
    def __init__(self,name):
        self.name=name
        self.dict={}
    def Add(self,property):
        self.dict[property.dict['name']]=property
        return self
    def SubDir(self,config):
        self.dict[str(config.__class__).split('.')[-1].strip('>\'')]=config
    def InterceptProperty(self,element):
        return False
    def OutputXML(self,indent):
        lines=[]
        lines=lines+[indent+'<'+self.name+'>']
        for item in self.dict:
            lines=lines+self.dict[item].OutputXML(indent+ProjectFileBase.indent)
        lines=lines+[indent+'</'+self.name+'>']
        return lines
    def InitFromXML(self,element):
        for child in element:
            try:
                name=child.tag
                if name[len(name)-len('Configuration'):]=='Configuration':
                    name=name[:-len('Configuration')]
                self.dict[name].InitFromXML(child)
            except:
                pass
        return self
    def Print(self):
        for item in self.dict:
            print (item)
            self.dict[item].Print()

    def PrintFullInformation(self,prefix):
        for item in self.dict:
            self.dict[item].PrintFullInformation(prefix+'.'+item)

    def GetPropertyValue(self,path):
        if path == '':
            return self
        pathList=path.split('.')
        if pathList[0] in self.dict:
            return self.dict[pathList[0]].GetPropertyValue('.'.join(pathList[1:]))
        else:
            return None

    def GetValue(self,path):
        if path == '':
            return self
        pathList=path.split('.')
        if pathList[0] in self.dict:
            return self.dict[pathList[0]].GetValue('.'.join(pathList[1:]))
        else:
            return None

    def SetValue(self,path,value):
        if path == '':
            return self
        pathList=path.split('.')
        if pathList[0] in self.dict:
            return self.dict[pathList[0]].SetValue('.'.join(pathList[1:]),value)
        else:
            return None

class ProjectFileBase(object):
    indent='    '
    def __init__(self):
        self.dict={}

    def Add(self,property):
        self.dict[property.dict['name']]=property
        return self

    def SubDir(self,config):
        self.dict[str(config.__class__).split('.')[-1].strip('>\'')]=config

    def OutputXML(self):
        lines=[]
        lines=lines+['<Project>']
        for item in self.dict:
            lines=lines+self.dict[item].OutputXML(self.indent)
        lines=lines+['</Project>']
        for line in lines:
            print(line)
        return self

    def Write(self,filename):
        if not filename.split('.')[-1] == 'xml':
            filename=filename+'.xml'
        lines=[]
        lines=lines+['<Project>']
        for item in self.dict:
            lines=lines+self.dict[item].OutputXML(self.indent)
        lines=lines+['</Project>']
        with open(filename,'w') as f:
            f.writelines("%s\n" % l for l in lines)
        return self

    def Read(self,filename):
        if not filename.split('.')[-1] == 'xml':
            filename=filename+'.xml'
        tree=et.parse(filename)
        root=tree.getroot()
        self.Parse(root)
        return self

    def Parse(self,element):
        for child in element:
            try:
                name=child.tag
                if name[len(name)-len('Configuration'):]=='Configuration':
                    name=name[:-len('Configuration')]
                self.dict[name].InitFromXML(child)
            except:
                pass
        return self

    def Print(self):
        for item in self.dict:
            print(item)
            self.dict[item].Print()

    def PrintFullInformation(self):
        for item in self.dict:
            self.dict[item].PrintFullInformation(item)

    def GetPropertyValue(self,path):
        if path == '':
            return self
        pathList=path.split('.')
        if pathList[0] in self.dict:
            return self.dict[pathList[0]].GetPropertyValue('.'.join(pathList[1:])) 
        else:
            return None

    def GetValue(self,path):
        if path == '':
            return self
        pathList=path.split('.')
        if pathList[0] in self.dict:
            return self.dict[pathList[0]].GetValue('.'.join(pathList[1:]))
        else:
            return None

    def SetValue(self,path,value):
        if path == '':
            return self
        pathList=path.split('.')
        if pathList[0] in self.dict:
            return self.dict[pathList[0]].SetValue('.'.join(pathList[1:]),value)
        else:
            return None
