"""
ProjectFileBase.py
"""

# Copyright (c) 2018 Teledyne LeCroy, all rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import xml.etree.ElementTree as et

class XMLProperty(object):
    def __init__(self,propertyName,propertyValue=None,propertyType=None):
        self.dict={}
        if not propertyValue == None:
            if propertyType == None:
                self.Default(propertyName,propertyValue,'string')
            else:
                self.Default(propertyName,propertyValue,propertyType)
    def Default(self,propertyName,propertyValue,propertyType):
        self.dict['name']=propertyName
        self.dict['type']=propertyType
        self.dict['value']=propertyValue
        self.UpdateValue()

    def OutputXML(self,indent):
        lines=[]
        lines=lines+[indent+'<'+self.dict['name']+'>']
        if 'type' in self.dict:
            elementPropertyType = self.dict['type']
        else:
            elementPropertyType='string'
        if 'value' in self.dict:
            elementPropertyValue = self.dict['value']
        else:
            elementPropertyValue = None
        
        lines=lines+[indent+ProjectFileBase.indent+'<type>'+elementPropertyType+'</type>']
        
        if isinstance(elementPropertyValue,list):
            lines=lines+[indent+ProjectFileBase.indent+'<value>']
            for item in elementPropertyValue:
                lines=lines+item.OutputXML(indent+ProjectFileBase.indent+ProjectFileBase.indent)
            lines=lines+[indent+ProjectFileBase.indent+'</value>']
        else:
            lines=lines+[indent+ProjectFileBase.indent+'<value>'+elementPropertyValue+'</value>']
        lines=lines+[indent+'</'+self.dict['name']+'>']
        return lines

    def InitFromXML(self,element,module):
        self.dict['name']=element.tag
        for elementProperty in element:
            if 'type' in self.dict and elementProperty.tag == 'value' and self.dict['type']=='array':
                self.dict[elementProperty.tag] = []
                for child in elementProperty:
                    name=child.tag
                    if name[len(name)-len('Configuration'):]=='Configuration':
                        temp=__import__(module)
                        self.dict['value'].append(eval('temp.'+name+'().InitFromXML(child,module)'))
                    else:
                        self.dict['value'].append(XMLProperty().InitFromXML(child,module))
            else:
                self.dict[elementProperty.tag] = elementProperty.text
        return self.UpdateValue()
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
            print self.dict[item]
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
            print prefix + ' <' + propertyType + '> = ' + propertyValue

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
    def __init__(self,name,typeString,value=None):
        if value==None:
            strValue='None'
        else:
            strValue = str(value)
        XMLProperty.__init__(self,name,strValue,typeString)

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

class XMLConfiguration(object):
    def __init__(self):
        self.dict={}
    def InterceptProperty(self,element):
        return False
    def OutputXML(self,indent):
        lines=[]
        name=str(self.__class__).split('.')[-1].strip('>\'')
        lines=lines+[indent+'<'+name+'>']
        for item in self.dict:
            lines=lines+self.dict[item].OutputXML(indent+ProjectFileBase.indent)
        lines=lines+[indent+'</'+name+'>']
        return lines
    def InitFromXML(self,element,module):
        for child in element:
            name=child.tag
            if name[len(name)-len('Configuration'):]=='Configuration':
                prefix=name[:-len('Configuration')]
                temp=__import__(module)
                self.dict[prefix]=eval('temp.'+name+'().InitFromXML(child,module)')
            else:
                self.dict[name]=XMLProperty(name).InitFromXML(child,module)
        return self
    def Print(self):
        for item in self.dict:
            print item
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
    def __init__(self,module):
        self.dict={}
        self.module=module

    def OutputXML(self):
        lines=[]
        lines=lines+['<Project>']
        for item in self.dict:
            lines=lines+self.dict[item].OutputXML(self.indent)
        lines=lines+['</Project>']
        for line in lines:
            print line
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
            name=child.tag
            if name[len(name)-len('Configuration'):]=='Configuration':
                prefix=name[:-len('Configuration')]
                temp=__import__(self.module)
                self.dict[prefix]=eval('temp.'+name+'().InitFromXML(child,self.module)')
            else:
                self.dict[name]=XMLProperty(name).InitFromXML(child,self.module)
        return self

    def Print(self):
        for item in self.dict:
            print item
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
