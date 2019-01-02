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

import sys
if sys.version_info.major < 3:
    from urllib2 import urlopen
else:
    from urllib.request import urlopen

import SignalIntegrity.App.Project

class HelpSystemKeys(object):
    controlHelpUrlBase=None
    keydict={}
    @staticmethod
    def InstallHelpURLBase(useOnlineHelp,urlBase):
        if useOnlineHelp:
            HelpSystemKeys.controlHelpUrlBase=urlBase+'/'
        else:
            HelpSystemKeys.controlHelpUrlBase='file://'+SignalIntegrity.App.InstallDir
        HelpSystemKeys.keydict={}
    def __init__(self,force=False):
        HelpSystemKeys.controlHelpUrlBase=None
        HelpSystemKeys.keydict={}
    def Read(self,force=False):
        self.keydict={}
        if force:
            raise ValueError
        try:
            lines = urlopen(self.controlHelpUrlBase+'Help/Help.html.LyXconv/helpkeys')
        except:
            return
        for line in lines:
            line=line.decode('ascii')
            tokens=line.strip().split(' >>> ')
            self.keydict[tokens[0]]=tokens[1]
    def SaveToFile(self):
        try:
            with open('helpkeys','w') as f:
                for key in self.keydict:
                    f.write(str(key)+' >>> '+str(self.keydict[key]+'\n'))
        except:
            return
    def Open(self,helpString):
        if helpString is None or self.controlHelpUrlBase is None:
            return
        url=self[helpString]
        if not url is None:
            import webbrowser
            url = self.controlHelpUrlBase+'Help/Help.html.LyXconv/'+url
            url=url.replace('\\','/')
            webbrowser.open(url)
    def Build(self):
        path=self.controlHelpUrlBase
        if path is None:
            path=os.getcwd()
        path=path+'Help/Help.html.LyXconv'
        self.keydict={}
        filename=path+'/Help.html'
        try:
            file=urlopen(filename)
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
                    file=urlopen(filename)
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
                self.keydict[child.get('name')]=('/'.join(filename.split('\\'))).split('/')[-1]
    def Recurse(self,root,filename):
        for child in root:
            self.CheckAndAdd(child,filename)
            self.Recurse(child,filename)
    def KeyValue(self,key):
        if key in self.keydict:
            return self.keydict[key]
        else:
            return None
    def __getitem__(self,item):
        if self.keydict == {}:
            self.Read()
        return self.KeyValue(item)
