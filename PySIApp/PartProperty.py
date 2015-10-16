'''
Created on Oct 15, 2015

@author: peterp
'''
class PartProperty(object):
    def __init__(self,propertyName,keyword=None,description=None,value=None,hidden=False):
        self.keyword=keyword
        self.propertyName=propertyName
        self.description=description
        self.value=value
        self.hidden=hidden

class PartPropertyReferenceDesignator(PartProperty):
    def __init__(self,referenceDesignator=''):
        PartProperty.__init__(self,'reference',description='Reference Designator',value=referenceDesignator)

class PartPropertyPorts(PartProperty):
    def __init__(self,numPorts=1):
        PartProperty.__init__(self,'ports',description='Ports',value=numPorts,hidden=True)

class PartPropertyFileName(PartProperty):
    def __init__(self,fileName=''):
        PartProperty.__init__(self,'filename',description='file name',value=fileName)

class PartPropertyResistance(PartProperty):
    def __init__(self,resistance=50.):
        PartProperty.__init__(self,'resistence',keyword='r',description='resistance (Ohms)',value=resistance)

class PartPropertyCapacitance(PartProperty):
    def __init__(self,capacitance=1e-12):
        PartProperty.__init__(self,'capacitance',keyword='c',description='capacitance (F)',value=capacitance)

class PartPropertyInductance(PartProperty):
    def __init__(self,inductance=1e-15):
        PartProperty.__init__(self,'inductance',keyword='l',description='inductance (H)',value=inductance)

class PartPropertyPartName(PartProperty):
    def __init__(self,partName=''):
        PartProperty.__init__(self,'type',description='part type',value=partName,hidden=True)

class PartPropertyCategory(PartProperty):
    def __init__(self,category=''):
        PartProperty.__init__(self,'category',description='part category',value=category,hidden=True)

class PartPropertyDescription(PartProperty):
    def __init__(self,description=''):
        PartProperty.__init__(self,'description',description='part description',value=description,hidden=True)