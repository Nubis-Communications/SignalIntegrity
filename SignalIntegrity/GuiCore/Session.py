"""
Session.py
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

from SignalIntegrity.GuiCore.RecordingCanvas import RecordingCanvas

class SessionError(Exception):
    pass

class ProjectSession(object):
    """toolkit-neutral façade over SignalIntegrityAppHeadless used by the alternative GUIs.

    It exposes the project as plain Python data (lists, dicts, strings and floats) so a GUI
    never touches the tk application, and every calculation goes through the same headless
    code path that scripted clients and the regression tests already use."""
    CALCULATIONS={'simulate':'canSimulate',
                  'sparameters':'canCalculateSParameters',
                  'virtualprobe':'canVirtualProbe',
                  'deembed':'canDeembed'}
    CALCULATION_PROPERTIES=['EndFrequency','FrequencyPoints','UserSampleRate','ReferenceImpedance']
    def __init__(self):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        self.app=SignalIntegrityAppHeadless()
        self.filename=None
    def _Project(self):
        import SignalIntegrity.App.Project
        if SignalIntegrity.App.Project is None or self.filename is None:
            raise SessionError('no project is open')
        return SignalIntegrity.App.Project
    def _Device(self,index):
        deviceList=self.app.Drawing.schematic.deviceList
        if not isinstance(index,int) or not 0 <= index < len(deviceList):
            raise SessionError('no device with index '+str(index))
        return deviceList[index]
    def IsOpen(self):
        return self.filename is not None
    def Open(self,filename):
        filename=os.path.realpath(str(filename))
        if not os.path.isfile(filename):
            raise SessionError('file not found: '+filename)
        if not self.app.OpenProjectFile(filename,writable=True):
            raise SessionError('could not open project: '+filename)
        self.filename=filename
        return self.Render()
    def Save(self,filename=None):
        self._Project()
        filename=self.filename if filename is None else os.path.realpath(str(filename))
        if not filename.lower().endswith('.si'):
            filename=filename+'.si'
        self.app.SaveProjectToFile(filename)
        self.filename=filename
        return filename
    def Grid(self):
        return self._Project()['Drawing.DrawingProperties']['Grid']
    def Origin(self):
        drawingProperties=self._Project()['Drawing.DrawingProperties']
        return (drawingProperties['Originx'],drawingProperties['Originy'])
    def Capabilities(self):
        drawing=self.app.Drawing
        return {key:bool(getattr(drawing,attr,False)) for key,attr in self.CALCULATIONS.items()}
    def Render(self):
        """@return dict with the drawing primitives, per-device boxes and calculation capabilities"""
        self._Project()
        canvas=RecordingCanvas()
        self.app.Drawing.DrawSchematic(canvas)
        grid=self.Grid(); ox,oy=self.Origin()
        devices=[]
        for d,device in enumerate(self.app.Drawing.schematic.deviceList):
            picture=device.partPicture.current
            box=picture.innerBox
            devices.append({'index':d,
                            'partname':device['partname'].GetValue(),
                            'ref':device['ref'].GetValue() if device['ref'] is not None else '',
                            'selected':bool(device.selected),
                            'bbox':[(ox+picture.origin[0]+box[0][0])*grid,(oy+picture.origin[1]+box[0][1])*grid,
                                    (ox+picture.origin[0]+box[1][0])*grid,(oy+picture.origin[1]+box[1][1])*grid]})
        return {'filename':self.filename,
                'title':os.path.basename(self.filename),
                'grid':grid,
                'items':canvas.items,
                'bbox':canvas.BoundingBox(),
                'devices':devices,
                'capabilities':self.Capabilities(),
                'equationsValid':bool(self._Project()['Equations.Valid']) if self._Project()['Equations.Lines'] else True}
    def DeviceAt(self,x,y):
        """@return index of the device under pixel coordinate x,y or None"""
        grid=self.Grid(); ox,oy=self.Origin()
        coord=(float(x)/grid-ox,float(y)/grid-oy)
        for d,device in enumerate(self.app.Drawing.schematic.deviceList):
            if device.IsAt(coord,(0.,0.),0.1):
                return d
        return None
    def Select(self,index):
        """selects a single device (or none if index is None)"""
        for d,device in enumerate(self.app.Drawing.schematic.deviceList):
            device.selected=(d==index)
        return index
    def DeviceProperties(self,index):
        from SignalIntegrity.App.PartProperty import PartPropertyReadOnly
        device=self._Device(index)
        result=[]
        for partProperty in device.propertiesList:
            if partProperty['Hidden']:
                continue
            try:
                value=partProperty.PropertyString(stype='entry')
            except (TypeError,ValueError):
                value=str(partProperty['Value'])
            result.append({'keyword':partProperty['Keyword'],
                           'name':partProperty['PropertyName'],
                           'description':partProperty['Description'],
                           'type':partProperty['Type'],
                           'unit':'' if partProperty['Unit'] in (None,'None') else partProperty['Unit'],
                           'value':value,
                           'visible':bool(partProperty['Visible']),
                           'readOnly':isinstance(partProperty,PartPropertyReadOnly)})
        return result
    def SetDeviceProperty(self,index,keyword,value):
        from SignalIntegrity.App.PartProperty import PartPropertyReadOnly
        partProperty=self._Device(index)[keyword]
        if partProperty is None:
            raise SessionError('device has no property '+str(keyword))
        if isinstance(partProperty,PartPropertyReadOnly):
            raise SessionError('property '+str(keyword)+' is read-only')
        value=str(value)
        if partProperty['Type']=='float' and not value.startswith('='):
            from SignalIntegrity.Lib.ToSI import FromSI
            if FromSI(value,partProperty['Unit']) is None:
                raise SessionError('invalid value for '+str(keyword)+': '+value)
        partProperty.SetValueFromString(value)
        return self.DeviceProperties(index)
    def MoveDevice(self,index,dx,dy):
        """moves a device by an integer number of grid units"""
        picture=self._Device(index).partPicture.current
        picture.SetOrigin((picture.origin[0]+int(dx),picture.origin[1]+int(dy)))
    def RotateDevice(self,index):
        self._Device(index).partPicture.current.Rotate()
    def Variables(self):
        return [{'name':v['Name'],'value':v['Value'],'type':v['Type'],'units':v['Units'],
                 'description':v['Description'],'readOnly':bool(v['ReadOnly'])}
                for v in self._Project()['Variables.Items']]
    def SetVariable(self,name,value):
        project=self._Project()
        if name not in project['Variables'].Names():
            raise SessionError('no variable named '+str(name))
        variable=project['Variables'].VariableByName(name)
        if variable['ReadOnly']:
            raise SessionError('variable '+str(name)+' is read-only')
        self.app.SetVariables({name:str(value)})
        return self.Variables()
    def CalculationProperties(self):
        calculationProperties=self._Project()['CalculationProperties']
        return {name:calculationProperties[name] for name in self.CALCULATION_PROPERTIES}
    def SetCalculationProperties(self,values):
        calculationProperties=self._Project()['CalculationProperties']
        for name,value in values.items():
            if name not in self.CALCULATION_PROPERTIES:
                raise SessionError('unknown calculation property '+str(name))
            calculationProperties[name]=int(value) if name=='FrequencyPoints' else float(value)
        calculationProperties.CalculateOthersFromBaseInformation()
        return self.CalculationProperties()
    def NetList(self):
        self._Project()
        return '\n'.join(self.app.NetListText())
    def Calculate(self,kind,callback=None):
        """runs a calculation through the headless application
        @param kind one of 'simulate','sparameters','virtualprobe','deembed'
        @param callback (optional) progress callback; returning False aborts
        @return JSON-serializable dict with 'waveforms' and/or 's-parameters'"""
        self._Project()
        if kind not in self.CALCULATIONS:
            raise SessionError('unknown calculation '+str(kind))
        self.Render()
        if not self.Capabilities()[kind]:
            raise SessionError('the schematic does not support '+kind)
        cancelled=[]
        def progress(value,message=None):
            if callback is None or callback(value) is not False:
                return True
            cancelled.append(True)
            return False
        if kind=='simulate':
            result=self.app.Simulate(progress)
        elif kind=='virtualprobe':
            result=self.app.VirtualProbe(progress)
        elif kind=='sparameters':
            result=self.app.CalculateSParameters(progress)
        else:
            result=self.app.Deembed(progress)
        # some calculations run to completion even after the callback asks to abort
        if cancelled:
            raise SessionError(kind+' cancelled')
        if not result:
            raise SessionError(kind+' failed - check the schematic, variables and equations')
        return self.SerializeResult(result)
    @staticmethod
    def _Waveform(name,wf):
        return {'name':name,'x':[float(t) for t in wf.Times()],'y':[float(v) for v in wf.Values()],
                'xunit':'s','yunit':'A' if name[:2]=='i/' or name[:3]=='di/' else 'V'}
    @staticmethod
    def _SParameters(name,sp):
        P=sp.m_P
        traces=[]
        for o in range(1,P+1):
            for i in range(1,P+1):
                fr=sp.FrequencyResponse(o,i)
                traces.append({'name':'S'+str(o)+str(i),'to':o,'from':i,
                               'dB':[float(v) for v in fr.Values('dB')],
                               'deg':[float(v) for v in fr.Values('deg')]})
        return {'name':name,'ports':P,'frequencies':[float(f) for f in sp.f()],'traces':traces}
    def SerializeResult(self,result):
        serialized={'type':result['type'],'waveforms':[],'sparameters':[]}
        if result['type'] in ('simulation','virtual probe'):
            labels=list(result.get('output waveform labels',[]))+list(result.get('other waveform labels',[]))
            waveforms=list(result.get('output waveforms',[]))+list(result.get('other waveforms',[]))
            serialized['waveforms']=[self._Waveform(n,wf) for n,wf in zip(labels,waveforms) if wf is not None]
        elif result['type']=='s-parameters':
            name=os.path.basename(result['file names'])
            serialized['sparameters']=[self._SParameters(name,result['s-parameters'])]
        elif result['type']=='de-embed':
            serialized['sparameters']=[self._SParameters(n,sp)
                for n,sp in zip(result['unknown names'],result['s-parameters'])]
        return serialized
