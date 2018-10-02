'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2017 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from ProjectFileBase import XMLConfiguration,XMLPropertyDefaultString,XMLPropertyDefaultInt,XMLPropertyDefaultBool
from ProjectFileBase import ProjectFileBase,XMLProperty

import os

class ColorConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self)
        self.dict['Background']=XMLPropertyDefaultString('Background')
        self.dict['Foreground']=XMLPropertyDefaultString('Foreground')
        self.dict['ActiveBackground']=XMLPropertyDefaultString('ActiveBackground')
        self.dict['ActiveForeground']=XMLPropertyDefaultString('ActiveForeground')
        self.dict['DisabledForeground']=XMLPropertyDefaultString('DisabledForeground')
        self.dict['Plot']=XMLPropertyDefaultString('Plot')

class AppearanceConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self)
        self.dict['FontSize']=XMLPropertyDefaultInt('FontSize',12)
        self.dict['Color']=ColorConfiguration()

class CacheConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self)
        self.dict['CacheResults']=XMLPropertyDefaultBool('CacheResults',False)

class LastFilesConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self)
        self.dict['Name']=XMLPropertyDefaultString('Name')
        self.dict['Directory']=XMLPropertyDefaultString('Directory')

class ProjectFilesConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self)
        self.dict['OpenLastFile']=XMLPropertyDefaultBool('OpenLastFIle',True)
        self.dict['RetainLastFilesOpened']=XMLPropertyDefaultBool('RetainLastFilesOpened',True)
        self.dict['LastFile']=XMLProperty('LastFile',[LastFilesConfiguration() for _ in range(4)],'array')
        self.dict['AskToSaveCurrentFile']=XMLPropertyDefaultBool('AskToSaveCurrentFile',True)

class OnlineHelpConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self)
        self.dict['UseOnlineHelp']=XMLPropertyDefaultBool('UseOnlineHelp',True)
        self.dict['URL']=XMLPropertyDefaultString('URL','http://teledynelecroy.github.io/PySI/PySIApp')

class PreferencesFile(ProjectFileBase):
    def __init__(self):
        ProjectFileBase.__init__(self,os.path.basename(__file__).split('.')[0])
        self.dict['ProjectFiles']=ProjectFilesConfiguration()
        self.dict['Appearance']=AppearanceConfiguration()
        self.dict['Cache']=CacheConfiguration()
        self.dict['OnlineHelp']=OnlineHelpConfiguration()

