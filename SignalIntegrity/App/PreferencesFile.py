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

class Color(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Color')
        self.Add(XMLPropertyDefaultString('Background'))
        self.Add(XMLPropertyDefaultString('Foreground'))
        self.Add(XMLPropertyDefaultString('ActiveBackground'))
        self.Add(XMLPropertyDefaultString('ActiveForeground'))
        self.Add(XMLPropertyDefaultString('DisabledForeground'))
        self.Add(XMLPropertyDefaultString('Plot'))

class Appearance(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Appearance')
        self.Add(XMLPropertyDefaultInt('FontSize',12))
        self.Add(XMLPropertyDefaultBool('PlotCursorValues',False))
        self.Add(XMLPropertyDefaultBool('AllPinNumbersVisible',False))
        self.SubDir(Color())

class Calculation(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Calculation')
        self.Add(XMLPropertyDefaultBool('TrySVD',False))
        self.Add(XMLPropertyDefaultBool('UseSinX',False))

class Cache(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Cache')
        self.Add(XMLPropertyDefaultBool('CacheResults',False))

class LastFiles(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'LastFiles')
        self.Add(XMLPropertyDefaultString('Name'))
        self.Add(XMLPropertyDefaultString('Directory'))

class ProjectFiles(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'ProjectFiles')
        self.Add(XMLPropertyDefaultBool('OpenLastFile',True))
        self.Add(XMLPropertyDefaultBool('RetainLastFilesOpened',True))
        self.Add(XMLProperty('LastFile',[LastFiles() for _ in range(4)],'array',arrayType=LastFiles()))
        self.Add(XMLPropertyDefaultBool('AskToSaveCurrentFile',True))

class OnlineHelp(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'OnlineHelp')
        self.Add(XMLPropertyDefaultBool('UseOnlineHelp',True))
        self.Add(XMLPropertyDefaultString('URL','http://teledynelecroy.github.io/SignalIntegrity/SignalIntegrity/App'))

class PreferencesFile(ProjectFileBase):
    def __init__(self):
        ProjectFileBase.__init__(self)
        self.Add(XMLPropertyDefaultString('Version',None))
        self.SubDir(ProjectFiles())
        self.SubDir(Appearance())
        self.SubDir(Cache())
        self.SubDir(OnlineHelp())
        self.SubDir(Calculation())

