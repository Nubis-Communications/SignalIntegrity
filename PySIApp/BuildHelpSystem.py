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
