"""
Help.py
"""
# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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

# The tk help system (App/BuildHelpSystem.HelpSystemKeys) without tkinter: the online or
# local help site chosen by the OnlineHelp preferences, and its help keys.

TOPICS={'introduction':'sec:Introduction',
        'equations':'sec:Equations',
        'postprocessing':'sec:Post-Processing',
        'preferences':'sec:Preferences',
        'documentation':'SoftwareDocumentation'}

_keys={}

def _Base():
    import SignalIntegrity.App
    from SignalIntegrity.GuiCore.Preferences import _Preferences
    from urllib.request import pathname2url
    preferences=_Preferences()
    if preferences['OnlineHelp.UseOnlineHelp']:
        return preferences['OnlineHelp.URL'].rstrip('/')+'/'
    return 'file:'+pathname2url(SignalIntegrity.App.InstallDir)+'/'

def _Keys(base):
    if base not in _keys:
        from SignalIntegrity.App.BuildHelpSystem import HelpSystemKeys
        HelpSystemKeys.controlHelpUrlBase=base
        keys=HelpSystemKeys.__new__(HelpSystemKeys)
        keys.Read()
        _keys[base]=dict(keys.keydict)
    return _keys[base]

def Url(topic='introduction'):
    """@return the help URL for a topic in TOPICS (falling back to the help site's front page)"""
    from SignalIntegrity.App.BuildHelpSystem import HelpSystemKeys
    if topic not in TOPICS:
        raise ValueError('unknown help topic '+str(topic))
    base=_Base()
    page=_Keys(base).get(TOPICS[topic])
    if page is None and topic=='documentation':
        page=HelpSystemKeys.softwareDocumentationRelPath
    return (base+HelpSystemKeys.helpSiteSubPath+(page or 'index.html')).replace('\\','/')

def Open(topic='introduction'):
    """opens the help in the default browser, keeping the #section anchor as the tk app does
    @return the URL"""
    from SignalIntegrity.App.BuildHelpSystem import HelpSystemKeys
    url=Url(topic)
    HelpSystemKeys._OpenUrl(url)
    return url
