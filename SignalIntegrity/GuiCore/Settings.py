"""
Settings.py
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
import json
import os
import sys

ENVIRONMENT_VARIABLE='SIGNALINTEGRITY_GUI_SETTINGS'
MAX_RECENT_PROJECTS=10

def SettingsDirectory():
    """folder for the settings both alternative GUIs share (theme, recent projects);
    the SIGNALINTEGRITY_GUI_SETTINGS environment variable overrides it"""
    if os.environ.get(ENVIRONMENT_VARIABLE):
        return os.environ[ENVIRONMENT_VARIABLE]
    if sys.platform.startswith('win'):
        base=os.environ.get('APPDATA') or os.path.expanduser('~')
    elif sys.platform=='darwin':
        base=os.path.expanduser('~/Library/Application Support')
    else:
        base=os.environ.get('XDG_CONFIG_HOME') or os.path.expanduser('~/.config')
    return os.path.join(base,'SignalIntegrity')

def _RecentFile():
    return os.path.join(SettingsDirectory(),'gui-recent-projects.json')

def _WriteRecent(files):
    try:
        os.makedirs(SettingsDirectory(),exist_ok=True)
        with open(_RecentFile(),'w') as f:
            json.dump({'projects':files},f,indent=1)
    except OSError:
        pass
    return files

def RecentProjects():
    """@return the most recently opened projects, newest first, skipping files that no longer exist"""
    try:
        with open(_RecentFile()) as f:
            files=json.load(f).get('projects')
    except (OSError,ValueError,AttributeError):
        return []
    if not isinstance(files,list):
        return []
    return [f for f in files if isinstance(f,str) and os.path.isfile(f)][:MAX_RECENT_PROJECTS]

def AddRecentProject(filename):
    """moves filename to the top of the recent projects
    @return the new list"""
    filename=os.path.realpath(filename)
    key=os.path.normcase(filename)
    files=[filename]+[f for f in RecentProjects() if os.path.normcase(f)!=key]
    return _WriteRecent(files[:MAX_RECENT_PROJECTS])

def ClearRecentProjects():
    return _WriteRecent([])
