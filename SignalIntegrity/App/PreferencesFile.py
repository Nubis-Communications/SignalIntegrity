"""
PreferencesFile.py
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
from SignalIntegrity.App.ProjectFileBase import XMLConfiguration,XMLPropertyDefaultString,XMLPropertyDefaultInt,XMLPropertyDefaultBool
from SignalIntegrity.App.ProjectFileBase import ProjectFileBase,XMLProperty

import os

class ColorConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'ColorConfiguration')
        self.dict['Background']=XMLPropertyDefaultString('Background')
        self.dict['Foreground']=XMLPropertyDefaultString('Foreground')
        self.dict['ActiveBackground']=XMLPropertyDefaultString('ActiveBackground')
        self.dict['ActiveForeground']=XMLPropertyDefaultString('ActiveForeground')
        self.dict['DisabledForeground']=XMLPropertyDefaultString('DisabledForeground')
        self.dict['Plot']=XMLPropertyDefaultString('Plot')

class AppearanceConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'AppearanceConfiguration')
        self.dict['FontSize']=XMLPropertyDefaultInt('FontSize',12)
        self.dict['Color']=ColorConfiguration()

class LastFilesConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'LastFilesConfiguration')
        self.dict['Name']=XMLPropertyDefaultString('Name')
        self.dict['Directory']=XMLPropertyDefaultString('Directory')
        
class ProjectFilesConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'ProjectFilesConfiguration')
        self.dict['OpenLastFile']=XMLPropertyDefaultBool('OpenLastFile',True)
        self.dict['RetainLastFilesOpened']=XMLPropertyDefaultBool('RetainLastFilesOpened',True)
        self.dict['LastFile']=XMLProperty('LastFile',[LastFilesConfiguration() for _ in range(4)])
        self.dict['AskToSaveCurrentFile']=XMLPropertyDefaultBool('AskToSaveCurrentFile',True)

class PreferencesFile(ProjectFileBase):
    def __init__(self):
        ProjectFileBase.__init__(self,os.path.basename(__file__).split('.')[0])
        self.dict['ProjectFiles']=ProjectFilesConfiguration()
        self.dict['Appearance']=AppearanceConfiguration()

