'''
Created on Oct 15, 2015

@author: peterp
'''
import xml.etree.ElementTree as et

class PartProperty(object):
    def __init__(self,propertyName,keyword=None,description=None,value=None,hidden=False,visible=False):
        self.keyword=keyword
        self.propertyName=propertyName
        self.description=description
        self.value=value
        self.hidden=hidden
        self.visible=visible

    def xml(self):
        pp = et.Element('part_property')
        pList=[]
        p=et.Element('keyword')
        p.text=str(self.keyword)
        pList.append(p)
        p=et.Element('property_name')
        p.text=str(self.propertyName)
        pList.append(p)
        p=et.Element('description')
        p.text=str(self.description)
        pList.append(p)
        p=et.Element('value')
        p.text=str(self.value)
        pList.append(p)
        p=et.Element('hidden')
        p.text=str(self.hidden)
        pList.append(p)
        p=et.Element('visible')
        p.text=str(self.visible)
        pList.append(p)
        pp.extend(pList)
        return pp

class PartPropertyXMLClassFactory(PartProperty):
    def __init__(self,xml):
        propertyName=''
        keyword=None
        description=None
        value=None
        hidden=False
        visible=False
        for item in xml:
            if item.tag == 'keyword':
                keyword = item.text
            elif item.tag == 'property_name':
                propertyName = item.text
            elif item.tag == 'description':
                description = item.text
            elif item.tag == 'value':
                value = item.text
            elif item.tag == 'hidden':
                hidden = eval(item.text)
            elif item.tag == 'visible':
                visible = eval(item.text)
        self.result=PartProperty(propertyName,keyword,description,value,hidden,visible)

class PartPropertyReferenceDesignator(PartProperty):
    def __init__(self,referenceDesignator=''):
        PartProperty.__init__(self,'reference',description='Reference Designator',value=referenceDesignator,visible=True)

class PartPropertyPorts(PartProperty):
    def __init__(self,numPorts=1):
        PartProperty.__init__(self,'ports',description='Ports',value=numPorts,hidden=True)

class PartPropertyFileName(PartProperty):
    def __init__(self,fileName=''):
        PartProperty.__init__(self,'filename',description='file name',value=fileName)

class PartPropertyWaveformFileName(PartProperty):
    def __init__(self,fileName=''):
        PartProperty.__init__(self,'waveformfilename',description='file name',value=fileName)

class PartPropertyResistance(PartProperty):
    def __init__(self,resistance=50.):
        PartProperty.__init__(self,'resistence',keyword='r',description='resistance (Ohms)',value=resistance,visible=True)

class PartPropertyCapacitance(PartProperty):
    def __init__(self,capacitance=1e-12):
        PartProperty.__init__(self,'capacitance',keyword='c',description='capacitance (F)',value=capacitance,visible=True)

class PartPropertyInductance(PartProperty):
    def __init__(self,inductance=1e-15):
        PartProperty.__init__(self,'inductance',keyword='l',description='inductance (H)',value=inductance,visible=True)

class PartPropertyPartName(PartProperty):
    def __init__(self,partName=''):
        PartProperty.__init__(self,'type',description='part type',value=partName,hidden=True)

class PartPropertyCategory(PartProperty):
    def __init__(self,category=''):
        PartProperty.__init__(self,'category',description='part category',value=category,hidden=True)

class PartPropertyDescription(PartProperty):
    def __init__(self,description=''):
        PartProperty.__init__(self,'description',description='part description',value=description,hidden=True)