"""
Api.py
"""
# Copyright (c) 2026 Nubis Communications, Inc.
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
import threading
import itertools

from SignalIntegrity.GuiCore.Session import ProjectSession, SessionError

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
    METHODS=['open','save','render','deviceAt','select','deviceProperties','setDeviceProperty',
             'moveDevice','rotateDevice','variables','setVariable','calculationProperties',
             'setCalculationProperties','netlist','calculate','job','cancel','listDirectory','version']
    READ_ONLY_WHILE_BUSY=('job','cancel','listDirectory','version')
    def __init__(self,session=None):
        self.session=ProjectSession() if session is None else session
        self.lock=threading.Lock()
        self.jobs={}
        self.activeJob=None
        self._ids=itertools.count(1)
    def Dispatch(self,method,params):
        if method not in self.METHODS:
            raise ApiError('unknown method '+str(method),404)
        if not isinstance(params,dict):
            raise ApiError('params must be an object')
        if self.activeJob is not None and method not in self.READ_ONLY_WHILE_BUSY:
            raise ApiError('a calculation is running',409)
        try:
            with self.lock:
                return getattr(self,'_'+method)(params)
        except SessionError as e:
            raise ApiError(str(e))
    @staticmethod
    def _Get(params,name,kind,optional=False):
        if name not in params:
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
        return self.session.Open(self._Get(params,'filename',str))
    def _save(self,params):
        return {'filename':self.session.Save(self._Get(params,'filename',str,True))}
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
                job.result=self.session.Calculate(job.kind,callback)
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
            elif name.lower().endswith('.si'):
                entries.append({'name':name,'path':full,'directory':False})
        parent=os.path.dirname(path)
        return {'path':path,'parent':parent if parent!=path else None,'entries':entries}
