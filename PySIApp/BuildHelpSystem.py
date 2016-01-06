'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
import xml.etree.ElementTree as et
import os

class HelpSystemKeys(object):
    def __init__(self,path=None):
        if path is None:
            path=os.getcwd()
        path=path+'/Help/PySIHelp.html.LyXconv'
        self.dict={}
        filename=path+'/PySIHelp.html'
        try:
            tree=et.parse(filename)
            r=tree.getroot()
            self.Recurse(r,filename)
        except:
            pass
        for stype in ['Section','Subsection','Subsubsection']:
            secIndex=1
            searchingSections=True
            while searchingSections:
                filename=path+'/PySIHelp-'+stype+'-'+str(secIndex)+'.html'
                try:
                    tree=et.parse(filename)
                except:
                    searchingSections=False
                    break
                r=tree.getroot()
                self.Recurse(r,filename)
                secIndex=secIndex+1
    def CheckAndAdd(self,child,filename):
        if 'class' in child.keys() and 'name' in child.keys():
            if child.get('class')=='Label':
                #print child.get('name')
                self.dict[child.get('name')]=('/'.join(filename.split('\\'))).split('/')[-1]
    def Recurse(self,root,filename):
        for child in root:
            self.CheckAndAdd(child,filename)
            self.Recurse(child,filename)
    def KeyValue(self,key):
        if key in self.dict:
            return self.dict[key]
        else:
            return None
    def __getitem__(self,item):
        return self.KeyValue(item)
