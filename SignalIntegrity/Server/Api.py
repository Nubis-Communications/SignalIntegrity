"""
Api.py
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
import os
import json
import threading
import itertools
from collections import OrderedDict

from SignalIntegrity.GuiCore.Session import ProjectSession, SessionError
from SignalIntegrity.GuiCore.Results import VIEWS
from SignalIntegrity.GuiCore import Settings

class ApiError(Exception):
    def __init__(self,message,status=400):
        super().__init__(message)
        self.status=status

class CalculationJob(object):
    def __init__(self,jobId,kind):
        self.id=jobId
        self.kind=kind
        self.progress=0.
        self.state='running'
        self.result=None
        self.error=None
        self.cancelled=False
    def Status(self,includeResult=True):
        status={'id':self.id,'kind':self.kind,'state':self.state,'progress':self.progress,'error':self.error}
        if includeResult and self.state=='done':
            status['result']=self.result
        return status

class Api(object):
    """JSON method dispatcher over GuiCore.ProjectSession.

    Every public method takes a params dict and returns JSON-serializable data.  Calculations
    run as background jobs because the engine uses a process-global project; while a job runs,
    every call that touches the project is rejected with status 409."""
    METHODS=['open','new','save','render','deviceAt','select','deviceProperties','setDeviceProperty',
             'setPropertyVisibility','moveDevice','rotateDevice','variables','setVariable','setVariableVisible',
             'calculationProperties','setCalculationProperties','netlist','calculate','job','cancel',
             'plotData','viewActions','view','ascend','listDirectory','version',
             'partCatalog','addPart','deleteDevice','themes','theme','setTheme','themesInPackage',
             'addWire','selectWire','deleteWire','menus','recentProjects','clearRecentProjects',
             'undo','redo','cut','copy','paste','duplicate','flipDevice',
             'selectVertex','moveVertex','deleteVertex','duplicateVertex',
             'equations','checkEquations','setEquations','postProcessing','setPostProcessing',
             'archive','extractArchive','exportNetlist','exportTikz','exportImage',
             'preferences','setPreference','help','sparameterTime','noiseSeries','layout','setLayout']
    # these never touch the project, so they neither wait for nor are blocked by a running calculation
    UNLOCKED=('job','cancel','plotData','listDirectory','version','themes','theme','setTheme','themesInPackage',
              'menus','recentProjects','clearRecentProjects','help','sparameterTime','noiseSeries','layout','setLayout')
    LISTABLE=('.si','.json','.vsix','.siz','.txt','.tpx','.tex','.png','.jpg')
    MAX_RESULTS=8
    LAYOUT_FILE='web-layout.json'
    MAX_LAYOUT=16384
    def __init__(self,session=None):
        self.session=ProjectSession() if session is None else session
        self.lock=threading.Lock()
        self.jobs={}
        self.activeJob=None
        self.results=OrderedDict()
        self._ids=itertools.count(1)
        self._resultIds=itertools.count(1)
        self.catalog=None
    def Dispatch(self,method,params):
        if method not in self.METHODS:
            raise ApiError('unknown method '+str(method),404)
        if not isinstance(params,dict):
            raise ApiError('params must be an object')
        try:
            if method in self.UNLOCKED:
                return getattr(self,'_'+method)(params)
            if self.activeJob is not None:
                raise ApiError('a calculation is running',409)
            with self.lock:
                return getattr(self,'_'+method)(params)
        except SessionError as e:
            raise ApiError(str(e))
    def _StoreResult(self,data):
        resultId=next(self._resultIds)
        self.results[resultId]=data
        while len(self.results)>self.MAX_RESULTS:
            self.results.popitem(last=False)
        summary=data.Summary()
        summary['resultId']=resultId
        return summary
    @staticmethod
    def _Get(params,name,kind,optional=False):
        if params.get(name) is None:
            if optional:
                return None
            raise ApiError('missing parameter '+name)
        value=params[name]
        if kind is float and isinstance(value,int) and not isinstance(value,bool):
            value=float(value)
        if not isinstance(value,kind) or isinstance(value,bool) and kind is not bool:
            raise ApiError('parameter '+name+' has the wrong type')
        return value
    def _version(self,params):
        from SignalIntegrity.__about__ import __version__
        return {'version':__version__}
    def _open(self,params):
        drawing=self.session.Open(self._Get(params,'filename',str))
        Settings.AddRecentProject(drawing['filename'])
        return drawing
    def _new(self,params):
        drawing=self.session.New(self._Get(params,'filename',str))
        Settings.AddRecentProject(drawing['filename'])
        return drawing
    # ---- menus (GuiCore.Menus, shared with the Qt GUI) and recent projects
    def _menus(self,params):
        from SignalIntegrity.GuiCore.Menus import MenusFor, TOOLBAR, TOOLBAR_LABELS, TOOLBAR_ICON_SIZE, CommandIds
        from SignalIntegrity.GuiCore.Icons import AllSvgs
        return {'menus':[{'title':title,'items':items} for title,items in MenusFor('web')],'toolbar':TOOLBAR,
                'toolbarLabels':TOOLBAR_LABELS,'iconSize':TOOLBAR_ICON_SIZE,'icons':AllSvgs(CommandIds('web'))}
    def _recentProjects(self,params):
        return Settings.RecentProjects()
    def _clearRecentProjects(self,params):
        return Settings.ClearRecentProjects()
    # ---- wires
    def _addWire(self,params):
        self.session.AddWire(self._Get(params,'points',list))
        return self.session.Render()
    def _selectWire(self,params):
        self.session.SelectWire(self._Get(params,'index',int))
        return self.session.Render()
    def _deleteWire(self,params):
        self.session.DeleteWire(self._Get(params,'index',int))
        return self.session.Render()
    # ---- editing: undo/redo, clipboard, flip, wire corners (all return the render)
    def _undo(self,params):
        self.session.Undo()
        return self.session.Render()
    def _redo(self,params):
        self.session.Redo()
        return self.session.Render()
    def _cut(self,params):
        self.session.Cut(self._Get(params,'index',int))
        return self.session.Render()
    def _copy(self,params):
        self.session.Copy(self._Get(params,'index',int))
        return self.session.Render()
    def _paste(self,params):
        self.session.Paste(self._Get(params,'x',float,True),self._Get(params,'y',float,True))
        return self.session.Render()
    def _duplicate(self,params):
        self.session.Duplicate(self._Get(params,'index',int),self._Get(params,'x',float,True),self._Get(params,'y',float,True))
        return self.session.Render()
    def _flipDevice(self,params):
        self.session.FlipDevice(self._Get(params,'index',int),self._Get(params,'direction',str))
        return self.session.Render()
    def _selectVertex(self,params):
        self.session.SelectVertex(self._Get(params,'wire',int),self._Get(params,'vertex',int))
        return self.session.Render()
    def _moveVertex(self,params):
        self.session.MoveVertex(self._Get(params,'wire',int),self._Get(params,'vertex',int),
                                self._Get(params,'x',float),self._Get(params,'y',float))
        return self.session.Render()
    def _deleteVertex(self,params):
        self.session.DeleteVertex(self._Get(params,'wire',int),self._Get(params,'vertex',int))
        return self.session.Render()
    def _duplicateVertex(self,params):
        self.session.DuplicateVertex(self._Get(params,'wire',int),self._Get(params,'vertex',int))
        return self.session.Render()
    # ---- equations and post-processing
    def _equations(self,params):
        return {'text':self.session.Equations()}
    def _checkEquations(self,params):
        return {'error':self.session.CheckEquations(self._Get(params,'text',str))}
    def _setEquations(self,params):
        error=self.session.SetEquations(self._Get(params,'text',str))
        return {'error':error,'drawing':self.session.Render()}
    def _postProcessing(self,params):
        return {'text':self.session.PostProcessing()}
    def _setPostProcessing(self,params):
        self.session.SetPostProcessing(self._Get(params,'text',str))
        return self.session.Render()
    # ---- archives and exports
    def _archive(self,params):
        return {'filename':self.session.Archive()}
    def _extractArchive(self,params):
        drawing=self.session.ExtractArchive(self._Get(params,'filename',str))
        Settings.AddRecentProject(drawing['filename'])
        return drawing
    def _exportNetlist(self,params):
        return {'filename':self.session.ExportNetList(self._Get(params,'filename',str))}
    def _exportTikz(self,params):
        return {'filename':self.session.ExportTikZ(self._Get(params,'filename',str))}
    def _exportImage(self,params):
        filename=self._Get(params,'filename',str)
        if os.path.splitext(filename)[1].lower() not in ('','.png','.jpg','.jpeg'):
            raise ApiError('images are written as .png or .jpg')
        return {'filename':self.session.ExportImage(filename)}
    # ---- preferences (shared with the tk app) and help
    def _preferences(self,params):
        from SignalIntegrity.GuiCore import Preferences
        return {'file':Preferences.FileName(),'sections':Preferences.Items()}
    def _setPreference(self,params):
        from SignalIntegrity.GuiCore import Preferences
        value=params.get('value')
        if not isinstance(value,(str,int,float,bool)):
            raise ApiError('parameter value has the wrong type')
        try:
            return {'value':Preferences.Set(self._Get(params,'path',str),value)}
        except Preferences.PreferencesError as e:
            raise ApiError(str(e))
    def _help(self,params):
        from SignalIntegrity.GuiCore import Help
        topic=self._Get(params,'topic',str)
        if topic not in Help.TOPICS:
            raise ApiError('unknown help topic '+topic)
        return {'url':Help.Open(topic)}
    # ---- result views
    def _Result(self,params):
        data=self.results.get(self._Get(params,'resultId',int))
        if data is None:
            raise ApiError('no such result',404)
        return data
    def _Points(self,params,default=4000):
        points=self._Get(params,'points',int,True)
        return default if points is None else max(16,min(points,20000))
    def _sparameterTime(self,params):
        from SignalIntegrity.GuiCore.Results import SPARAMETER_TIME_VIEWS
        data=self._Result(params)
        index=self._Get(params,'index',int)
        view=self._Get(params,'view',str)
        if not 0<=index<len(data.sparameters) or view not in SPARAMETER_TIME_VIEWS:
            raise ApiError('no such s-parameter view')
        try:
            return data.SParameterTime(index,view,self._Points(params))
        except ValueError as e:
            raise ApiError(str(e))
    def _noiseSeries(self,params):
        data=self._Result(params)
        if not data.noise:
            raise ApiError('this result has no statistical noise')
        indices=self._Get(params,'indices',list,True)
        count=len(data.NoiseInfo())
        if indices is not None and not all(isinstance(i,int) and not isinstance(i,bool) and 0<=i<count for i in indices):
            raise ApiError('invalid noise indices')
        return data.NoiseSeries(indices,self._Points(params))
    # ---- parts stencil
    def _partCatalog(self,params):
        if self.catalog is None:
            self.catalog=self.session.PartCatalog(previews=True)
        return self.catalog
    def _addPart(self,params):
        index=self.session.AddPart(self._Get(params,'part',int),self._Get(params,'x',float),self._Get(params,'y',float))
        drawing=self.session.Render()
        drawing['added']=index
        return drawing
    def _deleteDevice(self,params):
        self.session.DeleteDevice(self._Get(params,'index',int))
        return self.session.Render()
    # ---- themes
    def _ThemeResult(self,themeId,name,palette):
        from SignalIntegrity.GuiCore import Themes
        return {'id':themeId,'name':name,'palette':palette,'colorMap':Themes.SchematicColorMap(palette)}
    def _themes(self,params):
        from SignalIntegrity.GuiCore import Themes
        return Themes.DiscoverThemes()
    def _theme(self,params):
        from SignalIntegrity.GuiCore import Themes
        return self._ThemeResult(*Themes.CurrentTheme())
    def _setTheme(self,params):
        from SignalIntegrity.GuiCore import Themes
        themeId=self._Get(params,'id',str)
        try:
            name,palette=Themes.LoadTheme(themeId)
        except (Themes.ThemeError,OSError) as e:
            raise ApiError(str(e))
        Themes.SaveThemeId(themeId)
        return self._ThemeResult(themeId,self._Get(params,'name',str,True) or name,palette)
    def _themesInPackage(self,params):
        from SignalIntegrity.GuiCore import Themes
        path=self._Get(params,'path',str)
        try:
            return Themes.ThemesInPackage(path)
        except Exception as e:
            raise ApiError('could not read '+path+': '+str(e))
    # ---- dock layout of the web UI (in the settings folder, since the desktop app's port changes per run)
    def _LayoutFile(self):
        return os.path.join(Settings.SettingsDirectory(),self.LAYOUT_FILE)
    def _layout(self,params):
        try:
            with open(self._LayoutFile()) as f:
                layout=json.load(f)
        except (OSError,ValueError):
            return None
        return layout if isinstance(layout,dict) else None
    def _setLayout(self,params):
        layout=self._Get(params,'layout',dict)
        text=json.dumps(layout)
        if len(text)>self.MAX_LAYOUT:
            raise ApiError('layout is too large')
        try:
            os.makedirs(Settings.SettingsDirectory(),exist_ok=True)
            with open(self._LayoutFile(),'w') as f:
                f.write(text)
        except OSError as e:
            raise ApiError('could not save the layout: '+str(e))
        return layout
    def _save(self,params):
        filename=self._Get(params,'filename',str,True)
        saved=self.session.Save(filename)
        if filename is not None:
            Settings.AddRecentProject(saved)
        return {'filename':saved}
    def _render(self,params):
        return self.session.Render()
    def _deviceAt(self,params):
        return {'index':self.session.DeviceAt(self._Get(params,'x',float),self._Get(params,'y',float))}
    def _select(self,params):
        index=params.get('index')
        if index is not None and not isinstance(index,int):
            raise ApiError('parameter index has the wrong type')
        self.session.Select(index)
        return self.session.Render()
    def _deviceProperties(self,params):
        return self.session.DeviceProperties(self._Get(params,'index',int))
    def _setDeviceProperty(self,params):
        return self.session.SetDeviceProperty(self._Get(params,'index',int),self._Get(params,'keyword',str),
                                              self._Get(params,'value',str))
    def _setPropertyVisibility(self,params):
        return self.session.SetDevicePropertyVisibility(self._Get(params,'index',int),self._Get(params,'keyword',str),
            self._Get(params,'visible',bool,True),self._Get(params,'keywordVisible',bool,True))
    def _moveDevice(self,params):
        self.session.MoveDevice(self._Get(params,'index',int),self._Get(params,'dx',int),self._Get(params,'dy',int))
        return self.session.Render()
    def _rotateDevice(self,params):
        self.session.RotateDevice(self._Get(params,'index',int))
        return self.session.Render()
    def _variables(self,params):
        return self.session.Variables()
    def _setVariable(self,params):
        return self.session.SetVariable(self._Get(params,'name',str),self._Get(params,'value',str))
    def _setVariableVisible(self,params):
        return self.session.SetVariableVisible(self._Get(params,'name',str),self._Get(params,'visible',bool))
    def _viewActions(self,params):
        return self.session.ViewActions(self._Get(params,'index',int))
    def _view(self,params):
        kind,value=self.session.View(self._Get(params,'index',int),self._Get(params,'action',str))
        if kind=='project':
            return {'kind':'project','drawing':value}
        return {'kind':'result','result':self._StoreResult(value)}
    def _ascend(self,params):
        return self.session.Ascend()
    def _plotData(self,params):
        data=self.results.get(self._Get(params,'resultId',int))
        if data is None:
            raise ApiError('no such result',404)
        view=self._Get(params,'view',str)
        if view not in VIEWS:
            raise ApiError('unknown view '+view)
        indices=self._Get(params,'indices',list,True)
        if indices is not None and not all(isinstance(i,int) and not isinstance(i,bool) and 0<=i<len(data.waveforms) for i in indices):
            raise ApiError('invalid waveform indices')
        points=self._Get(params,'points',int,True)
        points=4000 if points is None else max(16,min(points,20000))
        return data.Series(view,indices,self._Get(params,'xmin',float,True),self._Get(params,'xmax',float,True),points)
    def _calculationProperties(self,params):
        return self.session.CalculationProperties()
    def _setCalculationProperties(self,params):
        values=self._Get(params,'values',dict)
        try:
            return self.session.SetCalculationProperties(values)
        except (TypeError,ValueError):
            raise ApiError('calculation properties must be numbers')
    def _netlist(self,params):
        return {'netlist':self.session.NetList()}
    def _calculate(self,params):
        kind=self._Get(params,'kind',str)
        if kind not in ProjectSession.CALCULATIONS:
            raise ApiError('unknown calculation '+kind)
        if not self.session.IsOpen():
            raise ApiError('no project is open')
        job=CalculationJob(next(self._ids),kind)
        self.jobs={job.id:job}
        self.activeJob=job
        threading.Thread(target=self._RunJob,args=(job,),daemon=True).start()
        return job.Status()
    def _RunJob(self,job):
        def callback(progress):
            try:
                job.progress=float(progress)
            except (TypeError,ValueError):
                pass
            return not job.cancelled
        try:
            with self.lock:
                data=self.session.Calculate(job.kind,callback)
            job.result=self._StoreResult(data)
            job.state='done'
        except Exception as e:
            job.error='calculation cancelled' if job.cancelled else str(e)
            job.state='failed'
        finally:
            self.activeJob=None
    def _JobFor(self,params):
        job=self.jobs.get(self._Get(params,'id',int))
        if job is None:
            raise ApiError('no such job',404)
        return job
    def _job(self,params):
        return self._JobFor(params).Status()
    def _cancel(self,params):
        job=self._JobFor(params)
        job.cancelled=True
        return job.Status(includeResult=False)
    def _listDirectory(self,params):
        path=self._Get(params,'path',str,True)
        extensions=self._Get(params,'extensions',list,True) or ['.si']
        if not all(isinstance(e,str) and e.lower() in self.LISTABLE for e in extensions):
            raise ApiError('extensions must be among '+', '.join(self.LISTABLE))
        extensions=tuple(e.lower() for e in extensions)
        if not path:
            path=os.path.dirname(self.session.filename) if self.session.IsOpen() else os.path.expanduser('~')
        path=os.path.realpath(path)
        if not os.path.isdir(path):
            raise ApiError('not a directory: '+path)
        entries=[]
        try:
            names=sorted(os.listdir(path),key=str.lower)
        except OSError as e:
            raise ApiError(str(e))
        for name in names:
            if name.startswith('.'):
                continue
            full=os.path.join(path,name)
            if os.path.isdir(full):
                entries.append({'name':name,'path':full,'directory':True})
            elif name.lower().endswith(extensions):
                entries.append({'name':name,'path':full,'directory':False})
        parent=os.path.dirname(path)
        return {'path':path,'parent':parent if parent!=path else None,'entries':entries}
