"""
BuildHelpSystem.py
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
import os

class HelpSystemKeys(object):
    controlHelpUrlBase=None
    def __init__(self,force=False):
        self.dict={}
        self.fileExists=False
        self.helpKeysFileName=os.path.dirname(os.path.realpath(__file__))+'/helpkeys'
        try:
            self.Read(force)
        except:
            try:
                self.Build(self.controlHelpUrlBase)
                if len(self.dict)>0:
                    self.SaveToFile()
            except:
                return
    def Read(self,force=False):
        self.dict={}
        if force:
            raise ValueError
        with open(self.helpKeysFileName,'r') as f:
            lines=f.readlines()
        for line in lines:
            tokens=line.strip().split(' >>> ')
            self.dict[tokens[0]]=tokens[1]
    def SaveToFile(self):
        try:
            with open(self.helpKeysFileName,'w') as f:
                for key in self.dict:
                    f.write(str(key)+' >>> '+str(self.dict[key]+'\n'))
        except:
            return
    def Open(self,helpString):
        if helpString is None or self.controlHelpUrlBase is None:
            return
        url=self[helpString]
        if not url is None:
            import webbrowser
            url = self.controlHelpUrlBase+'/Help/Help.html.LyXconv/'+url
            url=url.replace('\\','/')
            webbrowser.open(url)
    def Build(self,path=None):
        if path is None:
            path=os.getcwd()
        path=path+'/Help/Help.html.LyXconv'
        self.dict={}
        filename=path+'/Help.html'
        try:
            import urllib2
            file=urllib2.urlopen(filename)
            tree=et.parse(file)
            r=tree.getroot()
            self.Recurse(r,filename)
        except:
            pass
        for stype in ['Section','Subsection','Subsubsection']:
            secIndex=1
            searchingSections=True
            while searchingSections:
                filename=path+'/Help-'+stype+'-'+str(secIndex)+'.html'
                try:
                    import urllib2
                    file=urllib2.urlopen(filename)
                    tree=et.parse(file)
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
