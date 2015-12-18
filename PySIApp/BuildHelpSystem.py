'''
Created on Dec 18, 2015

@author: peterp
'''

import xml.etree.ElementTree as et
import os

class HelpSystemKeys(object):
    def __init__(self):
        path=os.getcwd()
        path=path+'/Help/PySIHelp.html.LyXconv'
        self.dict={}
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
                self.dict[child.get('name')]=filename.split('/')[-1]
    def Recurse(self,root,filename):
        for child in root:
            self.CheckAndAdd(child,filename)
            self.Recurse(child,filename)
