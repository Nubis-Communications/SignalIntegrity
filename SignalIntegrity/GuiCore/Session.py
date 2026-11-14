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
import functools
import os

from SignalIntegrity.GuiCore.RecordingCanvas import RecordingCanvas
from SignalIntegrity.GuiCore.Results import ResultData

class SessionError(Exception):
    pass

def _Edit(eventName):
    """marks a ProjectSession method as a project edit: an undo step is recorded after it succeeds"""
    def decorate(method):
        @functools.wraps(method)
        def edit(self,*args,**kwargs):
            result=method(self,*args,**kwargs)
            self._Record(eventName)
            return result
        return edit
    return decorate

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
    MAX_UNDO=100
    def __init__(self):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        self.app=SignalIntegrityAppHeadless()
        self.filename=None
        self.readOnly=False
        self.stack=[]
        self.history=[]
        self.historyIndex=-1
        self.clipboard=None
        self.selectedVertex=None
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
        self._ResetHistory()
        return self.Render()
    def New(self,filename):
        """starts an empty project and saves it to filename, as the tk app's File/New Project does"""
        import SignalIntegrity.App
        from SignalIntegrity.App.ProjectFile import ProjectFile
        from SignalIntegrity.App.Files import FileParts
        filename=os.path.realpath(str(filename))
        if not filename.lower().endswith('.si'):
            filename=filename+'.si'
        if not os.path.isdir(os.path.dirname(filename)):
            raise SessionError('folder not found: '+os.path.dirname(filename))
        SignalIntegrity.App.Project=ProjectFile()
        SignalIntegrity.App.Project['Drawing.DrawingProperties.Grid']=SignalIntegrity.App.Preferences['Appearance.InitialGrid']
        self.app.readOnly=False
        self.app.fileparts=FileParts(filename)
        self.app.Drawing.InitFromProject()
        self.filename=filename
        self.readOnly=False
        self.stack=[]
        self.Save()
        self._ResetHistory()
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
                'wires':self.Wires(),
                'selectedVertex':self._SelectedVertex(),
                'canUndo':self.CanUndo(),'canRedo':self.CanRedo(),
                'undoName':self.history[self.historyIndex][0] if self.CanUndo() else None,
                'redoName':self.history[self.historyIndex+1][0] if self.CanRedo() else None,
                'canPaste':self.clipboard is not None and not self.readOnly,
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
        """selects a single device (or none if index is None) and deselects any wire"""
        for d,device in enumerate(self.app.Drawing.schematic.deviceList):
            device.selected=(d==index)
        for wire in self._WireList():
            for vertex in wire['Vertices']:
                vertex['Selected']=False
        self.selectedVertex=None
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
    @_Edit('change property visibility')
    def SetDevicePropertyVisibility(self,index,keyword,visible=None,keywordVisible=None):
        """chooses whether a property (and its keyword) is shown on the schematic"""
        self._Writable()
        partProperty=self._PartProperty(index,keyword)
        if visible is not None:
            partProperty['Visible']=bool(visible)
        if keywordVisible is not None:
            partProperty['KeywordVisible']=bool(keywordVisible)
        return self.DeviceProperties(index)
    @_Edit('edit property')
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
    @_Edit('move part')
    def MoveDevice(self,index,dx,dy):
        """moves a device by an integer number of grid units"""
        self._Writable()
        picture=self._Device(index).partPicture.current
        picture.SetOrigin((picture.origin[0]+int(dx),picture.origin[1]+int(dy)))
    @_Edit('rotate part')
    def RotateDevice(self,index):
        self._Writable()
        self._Device(index).partPicture.current.Rotate()
    @_Edit('flip part')
    def FlipDevice(self,index,direction='horizontal'):
        """mirrors a device as the tk Flip Horizontally / Flip Vertically commands do"""
        self._Writable()
        if direction not in ('horizontal','vertical'):
            raise SessionError('flip direction must be horizontal or vertical')
        picture=self._Device(index).partPicture.current
        horizontal,vertical=picture.mirroredHorizontally,picture.mirroredVertically
        if direction=='horizontal':
            horizontal=not horizontal
        else:
            vertical=not vertical
        picture.ApplyOrientation(picture.orientation,horizontal,vertical)
    # ---- clipboard (tk Duplicate / Cut, with Copy and Paste)
    def _PlaceCopy(self,device,x=None,y=None):
        """adds a copy of device with the next free reference designator (and port number), at
        pixel x,y or two grid units below and right of the original, selects it and returns its index"""
        schematic=self.app.Drawing.schematic
        device=copy.deepcopy(device)
        device.selected=False
        partname=device['partname'].GetValue()
        if partname in ('Port','NetworkAnalyzerStimulus') and device['pn'] is not None:
            numbers={int(d['pn'].GetValue()) for d in schematic.deviceList if d['partname'].GetValue()==partname}
            number=1
            while number in numbers:
                number+=1
            device['pn'].SetValueFromString(str(number))
        if device['defref'] is not None and device['ref'] is not None:
            reference=schematic.NewUniqueReferenceDesignator(device['defref'].GetValue())
            if reference is not None:
                device['ref'].SetValueFromString(reference)
        picture=device.partPicture.current
        if x is None or y is None:
            picture.SetOrigin((picture.origin[0]+2,picture.origin[1]+2))
        else:
            picture.SetOrigin(self._GridCoordinate(x,y))
        schematic.deviceList.append(device)
        index=len(schematic.deviceList)-1
        self.Select(index)
        return index
    def Copy(self,index):
        self.clipboard=copy.deepcopy(self._Device(index))
    @_Edit('cut part')
    def Cut(self,index):
        self._Writable()
        self.Copy(index)
        del self.app.Drawing.schematic.deviceList[index]
        self.Select(None)
    @_Edit('paste part')
    def Paste(self,x=None,y=None):
        """@return the index of the pasted (and selected) part"""
        self._Writable()
        if self.clipboard is None:
            raise SessionError('nothing to paste')
        return self._PlaceCopy(self.clipboard,x,y)
    @_Edit('duplicate part')
    def Duplicate(self,index,x=None,y=None):
        """@return the index of the new (and selected) copy; the clipboard is unchanged"""
        self._Writable()
        return self._PlaceCopy(self._Device(index),x,y)
    # ---- undo and redo: snapshots of the project text, as the tk History does
    def _Snapshot(self):
        return self._Project().Write(self.app).LinesToWrite()
    def _ResetHistory(self):
        self.history=[('open',self._Snapshot())]
        self.historyIndex=0
        self.selectedVertex=None
    def _Record(self,eventName):
        del self.history[self.historyIndex+1:]
        self.history.append((eventName,self._Snapshot()))
        if len(self.history)>self.MAX_UNDO:
            del self.history[0]
        self.historyIndex=len(self.history)-1
    def _Apply(self,lines):
        # a fresh project, because FromText leaves sections the snapshot doesn't mention (e.g. emptied equations) untouched
        import SignalIntegrity.App
        from SignalIntegrity.App.ProjectFile import ProjectFile
        project=ProjectFile()
        project.FromText(lines)
        SignalIntegrity.App.Project=project
        self.app.Drawing.InitFromProject()
        self.Select(None)
    def CanUndo(self):
        return not self.readOnly and self.historyIndex>0
    def CanRedo(self):
        return not self.readOnly and 0<=self.historyIndex<len(self.history)-1
    def Undo(self):
        """@return the name of the edit that was undone"""
        self._Writable()
        if not self.CanUndo():
            raise SessionError('nothing to undo')
        name=self.history[self.historyIndex][0]
        self.historyIndex-=1
        self._Apply(self.history[self.historyIndex][1])
        return name
    def Redo(self):
        """@return the name of the edit that was redone"""
        self._Writable()
        if not self.CanRedo():
            raise SessionError('nothing to redo')
        self.historyIndex+=1
        self._Apply(self.history[self.historyIndex][1])
        return self.history[self.historyIndex][0]
    # ---- the parts stencil, using the same catalog as the tk Add Part dialog
    @staticmethod
    def _Catalog():
        from SignalIntegrity.App.Device import DeviceList,DeviceListUnknown,DeviceListSystem
        return [d for d in DeviceList+DeviceListUnknown+DeviceListSystem if d.enabled]
    def PartCatalog(self,previews=False):
        """@return [{index,partname,description,categories,preview?}] grouped the way the tk picker groups them"""
        catalog=[]
        for index,device in enumerate(self._Catalog()):
            entry={'index':index,'partname':device['partname'].GetValue(),
                   'description':' '.join(str(device['desc'].GetValue()).split()) if device['desc'] is not None else '',
                   'categories':device.Categories()}
            if previews:
                entry['preview']=self.PartPreview(index)
            catalog.append(entry)
        return catalog
    def PartPreview(self,index):
        """@return {items,bbox} drawing primitives of a catalog part at the origin"""
        catalog=self._Catalog()
        if not isinstance(index,int) or not 0<=index<len(catalog):
            raise SessionError('no part with index '+str(index))
        canvas=RecordingCanvas()
        try:
            device=copy.deepcopy(catalog[index])
            device.DrawDevice(canvas,16,0,0)
        except Exception:
            canvas.items=[]
        return {'items':canvas.items,'bbox':canvas.BoundingBox()}
    @_Edit('add part')
    def AddPart(self,index,x,y):
        """places a catalog part with its origin at the grid point nearest pixel x,y, gives it a
        unique reference designator (and port number) as the tk app does, and selects it
        @return the new device index"""
        from SignalIntegrity.App.PartProperty import PartPropertyReferenceDesignator
        self._Writable()
        catalog=self._Catalog()
        if not isinstance(index,int) or not 0<=index<len(catalog):
            raise SessionError('no part with index '+str(index))
        device=copy.deepcopy(catalog[index]).InitializeFromPreferences()
        schematic=self.app.Drawing.schematic
        if device['defref'] is not None:
            reference=schematic.NewUniqueReferenceDesignator(device['defref'].GetValue())
            if reference is not None:
                device.AddPartProperty(PartPropertyReferenceDesignator(''))
                device['ref'].SetValueFromString(reference)
        if device['partname'].GetValue()=='Port' and device['pn'] is not None:
            numbers=[int(d['pn'].GetValue()) for d in schematic.deviceList if d['partname'].GetValue()=='Port']
            device['pn'].SetValueFromString(str(max(numbers,default=0)+1))
        grid=self.Grid(); ox,oy=self.Origin()
        device.partPicture.current.SetOrigin((int(round(float(x)/grid))-ox,int(round(float(y)/grid))-oy))
        schematic.deviceList.append(device)
        newIndex=len(schematic.deviceList)-1
        self.Select(newIndex)
        return newIndex
    @_Edit('delete part')
    def DeleteDevice(self,index):
        self._Writable()
        self._Device(index)
        del self.app.Drawing.schematic.deviceList[index]
        self.Select(None)
    # ---- wires
    def _WireList(self):
        return self._Project()['Drawing.Schematic.Wires']
    def _GridCoordinate(self,x,y):
        grid=self.Grid(); ox,oy=self.Origin()
        try:
            return (int(round(float(x)/grid))-ox,int(round(float(y)/grid))-oy)
        except (TypeError,ValueError):
            raise SessionError('coordinates must be numbers')
    def Wires(self):
        """@return [{index,points,selected}] each wire's vertices as a flat pixel list [x0,y0,x1,y1,...]"""
        grid=self.Grid(); ox,oy=self.Origin()
        return [{'index':w,
                 'points':[float(c) for v in wire['Vertices'] for c in ((v['Coord'][0]+ox)*grid,(v['Coord'][1]+oy)*grid)],
                 'selected':any(v['Selected'] for v in wire['Vertices'])}
                for w,wire in enumerate(self._WireList())]
    def WireAt(self,x,y,tolerance=None):
        """@return index of the wire passing within tolerance pixels (default a quarter grid) of pixel x,y, or None"""
        from SignalIntegrity.App.Wire import SegmentList
        grid=self.Grid(); ox,oy=self.Origin()
        coord=(float(x)/grid-ox,float(y)/grid-oy)
        distance=0.25 if tolerance is None else float(tolerance)/grid
        for w,wire in enumerate(self._WireList()):
            for segment in SegmentList(wire):
                if segment.IsAt(coord,(0.,0.),distance):
                    return w
        return None
    def SelectWire(self,index):
        """selects one wire (drawn highlighted, with its vertices marked) and deselects devices"""
        wires=self._WireList()
        if not isinstance(index,int) or not 0<=index<len(wires):
            raise SessionError('no wire with index '+str(index))
        self.Select(None)
        for vertex in wires[index]['Vertices']:
            vertex['Selected']=True
        return index
    @_Edit('add wire')
    def AddWire(self,points):
        """adds a wire through pixel points [[x,y],...]; each point snaps to the nearest grid point
        as in the tk app, repeated points are dropped, and the wires are then consolidated (split
        at junctions, joined where only two meet) exactly as the tk app does when it opens a project"""
        from SignalIntegrity.App.Wire import Wire,Vertex
        self._Writable()
        if not isinstance(points,(list,tuple)):
            raise SessionError('wire points must be a list of [x,y] pairs')
        coords=[]
        for point in points:
            if not isinstance(point,(list,tuple)) or len(point)!=2:
                raise SessionError('wire points must be a list of [x,y] pairs')
            coord=self._GridCoordinate(*point)
            if not coords or coords[-1]!=coord:
                coords.append(coord)
        if len(coords)<2:
            raise SessionError('a wire needs at least two different grid points')
        self.Select(None)
        self._WireList().append(Wire([Vertex(coord,False) for coord in coords]))
        self.app.Drawing.schematic.Consolidate()
    @_Edit('delete wire')
    def DeleteWire(self,index):
        self._Writable()
        wires=self._WireList()
        if not isinstance(index,int) or not 0<=index<len(wires):
            raise SessionError('no wire with index '+str(index))
        del wires[index]
        self.app.Drawing.schematic.Consolidate()
        self.Select(None)
    # ---- wire vertices, as the tk Wires menu edits them
    def _Vertex(self,wire,vertex):
        wires=self._WireList()
        if not isinstance(wire,int) or not 0<=wire<len(wires):
            raise SessionError('no wire with index '+str(wire))
        vertices=wires[wire]['Vertices']
        if not isinstance(vertex,int) or not 0<=vertex<len(vertices):
            raise SessionError('no vertex '+str(vertex)+' on wire '+str(wire))
        return vertices
    def _SelectedVertex(self):
        if self.selectedVertex is None:
            return None
        try:
            self._Vertex(*self.selectedVertex)
        except SessionError:
            return None
        return list(self.selectedVertex)
    def VertexAt(self,x,y,tolerance=None):
        """@return [wire,vertex] of the wire corner within tolerance pixels (default a quarter grid) of pixel x,y, or None"""
        grid=self.Grid(); ox,oy=self.Origin()
        coord=(float(x)/grid-ox,float(y)/grid-oy)
        distance=0.25 if tolerance is None else float(tolerance)/grid
        for w,wire in enumerate(self._WireList()):
            for v,vertex in enumerate(wire['Vertices']):
                if vertex.IsAt(coord,(0.,0.),distance):
                    return [w,v]
        return None
    def SelectVertex(self,wire,vertex):
        """selects one wire corner (drawn bold, with the wire's other corners marked)"""
        vertices=self._Vertex(wire,vertex)
        self.Select(None)
        vertices[vertex]['Selected']=True
        self.selectedVertex=(wire,vertex)
        return [wire,vertex]
    @_Edit('move vertex')
    def MoveVertex(self,wire,vertex,x,y):
        """moves a wire corner to the grid point nearest pixel x,y and consolidates the wires"""
        self._Writable()
        vertices=self._Vertex(wire,vertex)
        vertices[vertex]['Coord']=self._GridCoordinate(x,y)
        self.app.Drawing.schematic.Consolidate()
        self.Select(None)
    @_Edit('delete vertex')
    def DeleteVertex(self,wire,vertex):
        self._Writable()
        vertices=self._Vertex(wire,vertex)
        del vertices[vertex]
        if len(vertices)<2:
            del self._WireList()[wire]
        self.app.Drawing.schematic.Consolidate()
        self.Select(None)
    @_Edit('duplicate vertex')
    def DuplicateVertex(self,wire,vertex):
        """inserts a copy of a corner after it and selects the copy, ready to be moved to make a bend
        @return [wire,vertex] of the new corner"""
        self._Writable()
        vertices=self._Vertex(wire,vertex)
        vertices.insert(vertex+1,copy.deepcopy(vertices[vertex]))
        return self.SelectVertex(wire,vertex+1)
    # ---- equations and post-processing (the tk Equations and Post-Processing editors)
    def Equations(self):
        return self._Project()['Equations'].GetTextString()
    def CheckEquations(self,text):
        """@return None if the equations evaluate, otherwise the error message, without changing the project"""
        result=self._Project().EvaluateEquations(str(text),force=True)
        return None if result is None else str(result)
    @_Edit('edit equations')
    def SetEquations(self,text):
        """stores the equations and evaluates them
        @return None if they evaluate, otherwise the error message"""
        self._Writable()
        error=self.CheckEquations(text)
        self._Project()['Equations'].PutTextString(str(text))
        self.app.CheckEquations()
        return error
    def PostProcessing(self):
        return self._Project()['PostProcessing'].GetTextString()
    @_Edit('edit post-processing')
    def SetPostProcessing(self,text):
        self._Writable()
        self._Project()['PostProcessing'].PutTextString(str(text))
    # ---- archives and exports
    def Archive(self):
        """writes the project and every file it uses into <project>.siz next to the project
        @return the archive path"""
        self._Writable()
        self._Project().Write(self.app)
        if not self.app.Archive(overrideExistance=True):
            raise SessionError('nothing to archive, or the archive could not be written')
        return os.path.splitext(self.filename)[0]+'.siz'
    def ExtractArchive(self,filename):
        """extracts a .siz archive next to itself and opens its project"""
        filename=os.path.realpath(str(filename))
        if not filename.lower().endswith('.siz') or not os.path.isfile(filename):
            raise SessionError('not an archive: '+filename)
        if not self.app.ExtractArchive(filename):
            raise SessionError('could not extract '+filename)
        self.filename=os.path.realpath(self.app.fileparts.FullFilePathExtension('.si'))
        self.app.readOnly=False
        self.readOnly=False
        self.stack=[]
        self._ResetHistory()
        return self.Render()
    @staticmethod
    def _ExportName(filename,extension):
        filename=os.path.realpath(str(filename))
        if os.path.splitext(filename)[1]=='':
            filename+=extension
        if not os.path.isdir(os.path.dirname(filename)):
            raise SessionError('folder not found: '+os.path.dirname(filename))
        return filename
    def ExportNetList(self,filename):
        filename=self._ExportName(filename,'.txt')
        with open(filename,'w') as f:
            f.write(self.NetList()+'\n')
        return filename
    def ExportTikZ(self,filename):
        """writes the schematic as LaTeX: a .TpX file (TpX drawing with TikZ, as the tk app writes)
        or, for any other extension, a plain tikzpicture"""
        from SignalIntegrity.App.TikZ import TikZ
        from SignalIntegrity.App.TpX import TpX
        self._Project()
        filename=self._ExportName(filename,'.TpX')
        tikz=self.app.Drawing.DrawSchematic(TikZ()).Finish()
        if filename.lower().endswith('.tpx'):
            tpx=self.app.Drawing.DrawSchematic(TpX()).Finish()
            tpx.lineList=tpx.lineList+tikz.lineList
            tpx.WriteToFile(filename)
        else:
            tikz.WriteToFile(filename)
        return filename
    def ExportImage(self,filename,colorMap=None,background='white',scale=2.):
        """writes the schematic as a PNG (or any image format PIL knows from the extension)"""
        from SignalIntegrity.GuiCore.Export import PrimitivesImage
        filename=self._ExportName(filename,'.png')
        drawing=self.Render()
        PrimitivesImage(drawing['items'],drawing['bbox'],colorMap=colorMap,background=background,
                        scale=scale,margin=drawing['grid']).save(filename)
        return filename
    def Variables(self):
        return [{'name':v['Name'],'value':v['Value'],'type':v['Type'],'units':v['Units'],
                 'description':v['Description'],'visible':bool(v['Visible']),
                 'readOnly':self.readOnly or bool(v['ReadOnly'])}
                for v in self._Project()['Variables.Items']]
    @_Edit('change variable visibility')
    def SetVariableVisible(self,name,visible):
        """chooses whether a project variable is shown on the schematic"""
        self._Writable()
        project=self._Project()
        if name not in project['Variables'].Names():
            raise SessionError('no variable named '+str(name))
        project['Variables'].VariableByName(name)['Visible']=bool(visible)
        return self.Variables()
    @_Edit('edit variable')
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
    @_Edit('edit calculation properties')
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
