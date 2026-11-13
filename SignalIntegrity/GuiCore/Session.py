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
import copy
import os

from SignalIntegrity.GuiCore.RecordingCanvas import RecordingCanvas
from SignalIntegrity.GuiCore.Results import ResultData

class SessionError(Exception):
    pass

# the three helpers below mirror ViewableFileNameOfDevice, DeviceViewKind and
# WaveformProjectFileNameOfDevice in App/DeviceProperties.py without importing tkinter
def _FileProperty(device,propertyName):
    for partProperty in getattr(device,'propertiesList',[]):
        if partProperty['Type']=='file' and partProperty['PropertyName']==propertyName:
            filename=partProperty.GetValue()
            return None if filename in (None,'') else filename
    return None

def _ViewKind(device):
    if _FileProperty(device,'filename') is not None:
        return 'file'
    try:
        if device.netlist['DeviceName'] in ('voltagesource','currentsource','networkanalyzerport'):
            if device['wftype'].GetValue()!='DC':
                return 'waveform'
    except (AttributeError,TypeError,KeyError):
        pass
    return None

def _WaveformProject(device):
    filename=_FileProperty(device,'waveformfilename')
    if filename is None or os.path.splitext(filename)[1].lower()!='.si':
        return None
    return filename

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
        self.readOnly=False
        self.stack=[]
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
    def _Writable(self):
        self._Project()
        if self.readOnly:
            raise SessionError('this level of the hierarchy is read-only - go up to edit the project')
    def IsOpen(self):
        return self.filename is not None
    def Open(self,filename):
        filename=os.path.realpath(str(filename))
        if not os.path.isfile(filename):
            raise SessionError('file not found: '+filename)
        if not self.app.OpenProjectFile(filename,writable=True):
            raise SessionError('could not open project: '+filename)
        self.filename=filename
        self.readOnly=False
        self.stack=[]
        return self.Render()
    def Save(self,filename=None):
        self._Writable()
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
                'path':[os.path.basename(level['filename']) for level in self.stack]+[os.path.basename(self.filename)],
                'readOnly':self.readOnly,
                'canAscend':len(self.stack)>0,
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
                           'keywordVisible':bool(partProperty['KeywordVisible']),
                           'validEntries':list(getattr(partProperty,'validEntries',[])) if partProperty['Type']=='enum' else [],
                           'readOnly':self.readOnly or isinstance(partProperty,PartPropertyReadOnly)})
        return result
    def _PartProperty(self,index,keyword):
        partProperty=self._Device(index)[keyword]
        if partProperty is None:
            raise SessionError('device has no property '+str(keyword))
        return partProperty
    def SetDevicePropertyVisibility(self,index,keyword,visible=None,keywordVisible=None):
        """chooses whether a property (and its keyword) is shown on the schematic"""
        self._Writable()
        partProperty=self._PartProperty(index,keyword)
        if visible is not None:
            partProperty['Visible']=bool(visible)
        if keywordVisible is not None:
            partProperty['KeywordVisible']=bool(keywordVisible)
        return self.DeviceProperties(index)
    def SetDeviceProperty(self,index,keyword,value):
        from SignalIntegrity.App.PartProperty import PartPropertyReadOnly
        self._Writable()
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
        if partProperty['Type']=='enum' and value not in getattr(partProperty,'validEntries',[value]):
            raise SessionError('invalid value for '+str(keyword)+': '+value)
        partProperty.SetValueFromString(value)
        return self.DeviceProperties(index)
    def MoveDevice(self,index,dx,dy):
        """moves a device by an integer number of grid units"""
        self._Writable()
        picture=self._Device(index).partPicture.current
        picture.SetOrigin((picture.origin[0]+int(dx),picture.origin[1]+int(dy)))
    def RotateDevice(self,index):
        self._Writable()
        self._Device(index).partPicture.current.Rotate()
    def Variables(self):
        return [{'name':v['Name'],'value':v['Value'],'type':v['Type'],'units':v['Units'],
                 'description':v['Description'],'visible':bool(v['Visible']),
                 'readOnly':self.readOnly or bool(v['ReadOnly'])}
                for v in self._Project()['Variables.Items']]
    def SetVariableVisible(self,name,visible):
        """chooses whether a project variable is shown on the schematic"""
        self._Writable()
        project=self._Project()
        if name not in project['Variables'].Names():
            raise SessionError('no variable named '+str(name))
        project['Variables'].VariableByName(name)['Visible']=bool(visible)
        return self.Variables()
    def SetVariable(self,name,value):
        self._Writable()
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
        self._Writable()
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
        @return ResultData holding the waveforms, s-parameters and eye diagrams the tk GUI would show"""
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
            raise SessionError(kind+' failed: '+self._FailureReason(kind))
        data=ResultData.FromHeadless(result,os.path.basename(self.filename),
                                     self._Project()['CalculationProperties.EndFrequency'])
        if kind in ('simulate','virtualprobe'):
            data.eyes=self._EyeDiagrams(kind,result,progress)
        return data
    def _EyeDiagrams(self,kind,result,callback):
        """eye diagrams for the eye probes that are on, computed like SignalIntegrityAppHeadless does
        but on copies, because clock recovery modifies the waveform it is given"""
        import SignalIntegrity.Lib as si
        from SignalIntegrity.App.EyeDiagram import EyeDiagram
        partnames=['EyeProbe','DifferentialEyeProbe']+(['EyeWaveform'] if kind=='simulate' else [])
        noise=result.get('noise') if kind=='simulate' else None
        eyes=[]
        for label,waveform in zip(result['output waveform labels'],result['output waveforms']):
            for device in self.app.Drawing.schematic.deviceList:
                if device['partname'].GetValue() in partnames and device['ref'].GetValue()==label:
                    if noise:
                        device.configuration.SetExternalNoise(noise.Noise(label))
                    if device['eyestate'].GetValue()=='on':
                        eye=EyeDiagram(None,label,headless=True)
                        eye.prbswf=copy.deepcopy(waveform)
                        eye.baudrate=device['br'].GetValue()
                        eye.config=device.configuration
                        try:
                            eye.CalculateEyeDiagram(self.app.fileparts.FileNameTitle(),callback)
                        except si.SignalIntegrityException as e:
                            raise SessionError('eye diagram '+label+': '+str(e.message))
                        if eye.img is not None:
                            eyes.append((label,eye.img))
                    break
        return eyes
    def _FailureReason(self,kind):
        """the headless app only reports failure, so the reason the tk app would show is recovered
        by repeating the netlist parse on a two-point frequency list"""
        import SignalIntegrity.Lib as si
        if not self.app.CheckEquations():
            return 'the equations are not valid'
        frequencies=si.fd.EvenlySpacedFrequencyList(self._Project()['CalculationProperties.EndFrequency'],2)
        try:
            netList=self.app.NetListText()
            if kind=='simulate':
                parser=si.p.SimulatorNumericParser(frequencies); parser.AddLines(netList); parser.TransferMatrices()
                self.app.Drawing.schematic.InputWaveforms()
                self.app.Drawing.schematic.OtherWaveforms()
            elif kind=='virtualprobe':
                parser=si.p.VirtualProbeNumericParser(frequencies); parser.AddLines(netList); parser.TransferMatrices()
                self.app.Drawing.schematic.InputWaveforms()
            elif kind=='sparameters':
                parser=si.p.SystemSParametersNumericParser(frequencies); parser.AddLines(netList); parser.SParameters()
            else:
                parser=si.p.DeembedderNumericParser(frequencies); parser.AddLines(netList); parser.Deembed()
        except si.SignalIntegrityException as e:
            return (str(e.parameter)+': '+str(e.message)).strip(': ')
        except Exception as e:
            return str(e)
        return 'check the schematic, variables and equations'
    # ---- hierarchy traversal, matching the tk View / Open Project actions
    def ViewActions(self,index):
        """@return list of {'label','action'} for the device: 'file' views an s-parameter file or
        descends into a sub-project, 'openproject' descends into a waveform project and
        'waveform' shows the source waveform"""
        device=self._Device(index)
        actions=[]
        kind=_ViewKind(device)
        if kind=='file':
            filename=_FileProperty(device,'filename')
            actions.append({'label':'Open Project' if filename.lower().endswith('.si') else 'View','action':'file'})
        elif kind=='waveform':
            actions.append({'label':'View Waveform','action':'waveform'})
        if _WaveformProject(device) is not None:
            actions.append({'label':'Open Project','action':'openproject'})
        return actions
    def View(self,index,action):
        """performs a ViewActions action
        @return ('project',render dict) after descending, or ('result',ResultData)"""
        import SignalIntegrity.Lib as si
        device=self._Device(index)
        if action not in [a['action'] for a in self.ViewActions(index)]:
            raise SessionError('device cannot perform '+str(action))
        try:
            if action=='openproject':
                return 'project',self.Descend(index,_WaveformProject(device))
            if action=='file':
                filename=_FileProperty(device,'filename')
                if filename.lower().endswith('.si'):
                    return 'project',self.Descend(index,filename)
                data=ResultData('s-parameters',os.path.basename(filename))
                data.sparameters=[(os.path.basename(filename),si.sp.SParameterFile(filename))]
                return 'result',data
            ref=device['ref'].GetValue() if device['ref'] is not None else 'waveform'
            data=ResultData('waveform',ref,self._Project()['CalculationProperties.EndFrequency'])
            data.waveforms=[(ref,device.Waveform())]
            return 'result',data
        except si.SignalIntegrityException as e:
            raise SessionError(str(e.parameter)+': '+str(e.message))
    def Descend(self,index,filename):
        """opens the sub-project of a device read-only, passing the device's variables (and
        calculation properties when calcprop is true) the way the tk app launches it"""
        import SignalIntegrity.App.Project
        device=self._Device(index)
        project=self._Project()
        args=project['Variables'].Dictionary(device.variablesList)
        if device['calcprop'] is not None and device['calcprop'].GetValue()=='true':
            args.update(project['CalculationProperties'].Dictionary())
        child=os.path.realpath(filename)
        if not os.path.isfile(child):
            raise SessionError('file not found: '+child)
        if not self.readOnly:
            # puts unsaved schematic edits into the project so they survive the round trip
            project.Write(self.app)
        level={'project':copy.deepcopy(project),'cwd':os.getcwd(),'filename':self.filename,
               'readOnly':self.readOnly,'fileparts':copy.deepcopy(self.app.fileparts),'selected':index}
        if not self.app.OpenProjectFile(child,args):
            self._Restore(level)
            raise SessionError('could not open project: '+child)
        self.stack.append(level)
        self.filename=child
        self.readOnly=True
        return self.Render()
    def _Restore(self,level):
        import SignalIntegrity.App.Project
        SignalIntegrity.App.Project=level['project']
        os.chdir(level['cwd'])
        self.app.fileparts=level['fileparts']
        self.app.readOnly=level['readOnly']
        self.app.Drawing.InitFromProject()
        self.filename=level['filename']
        self.readOnly=level['readOnly']
    def Ascend(self):
        """returns to the parent project, with its unsaved edits and the traversed device selected"""
        if not self.stack:
            raise SessionError('already at the top of the hierarchy')
        level=self.stack.pop()
        self._Restore(level)
        self.Select(level['selected'])
        return self.Render()
