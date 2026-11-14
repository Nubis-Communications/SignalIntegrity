"""
Preferences.py
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

# Editing the SignalIntegrity preferences shared with the tk app (preferences.xml; the
# SIGNALINTEGRITY_PREFERENCES environment variable chooses the file).  The settings are listed
# generically from the preferences file definition, so new tk preferences appear automatically.

class PreferencesError(Exception):
    pass

# sections the tk Preferences dialog shows, in its order; others follow alphabetically
SECTION_ORDER=['Appearance','ProjectFiles','Calculation','SParameterProperties','Cache','OnlineHelp','Features','Regression']
# never sent to a GUI: the encryption password and bookkeeping the tk app manages itself
HIDDEN=('Version','Encryption','ProjectFiles.LastFile','Devices')
EDITABLE_TYPES=('int','float','string','bool','file')

def _Preferences():
    import SignalIntegrity.App
    preferences=getattr(SignalIntegrity.App,'Preferences',None)
    if preferences is None:
        from SignalIntegrity.App.Preferences import Preferences
        preferences=SignalIntegrity.App.Preferences=Preferences()
    return preferences

def _Hidden(path):
    return any(path==h or path.startswith(h+'.') for h in HIDDEN)

def _Walk(configuration,prefix=''):
    from SignalIntegrity.App.ProjectFileBase import XMLConfiguration
    for name in sorted(configuration.dict):
        item=configuration.dict[name]
        path=prefix+name
        if _Hidden(path):
            continue
        if isinstance(item,XMLConfiguration):
            yield from _Walk(item,path+'.')
        elif item.dict.get('type') in EDITABLE_TYPES:
            yield path,item

def _Label(name):
    out=''
    for k,c in enumerate(name):
        if c.isupper() and k>0 and (not name[k-1].isupper() or (k+1<len(name) and name[k+1].islower())):
            out+=' '
        out+=c
    return out

def Items():
    """@return [{section,items:[{path,label,type,value}]}] every editable preference, grouped by section"""
    sections={}
    for path,item in _Walk(_Preferences()):
        parts=path.split('.')
        section=parts[0] if len(parts)>1 else 'General'
        value=item.GetValue()
        sections.setdefault(section,[]).append({'path':path,'label':' / '.join(_Label(p) for p in parts[1:] or parts),
                                                'type':item.dict['type'],'value':value})
    order=[s for s in SECTION_ORDER if s in sections]+sorted(s for s in sections if s not in SECTION_ORDER)
    return [{'section':s,'label':_Label(s),'items':sections[s]} for s in order]

def Set(path,value):
    """sets one preference, converting value to its type, and saves the preferences file
    @return the stored value"""
    items=dict(_Walk(_Preferences()))
    if path not in items:
        raise PreferencesError('no editable preference '+str(path))
    kind=items[path].dict['type']
    try:
        if kind=='bool':
            if isinstance(value,str):
                if value.lower() not in ('true','false'):
                    raise ValueError
                value=value.lower()=='true'
            value=bool(value)
        elif kind=='int':
            if isinstance(value,bool) or float(value)!=int(float(value)):
                raise ValueError
            value=int(float(value))
        elif kind=='float':
            if isinstance(value,bool):
                raise ValueError
            value=float(value)
        else:
            value=None if value is None else str(value)
    except (TypeError,ValueError):
        raise PreferencesError('invalid '+kind+' value for '+path+': '+str(value))
    preferences=_Preferences()
    preferences[path]=value
    preferences.SaveToFile()
    return preferences[path]

def FileName():
    return _Preferences().preferencesFileName
