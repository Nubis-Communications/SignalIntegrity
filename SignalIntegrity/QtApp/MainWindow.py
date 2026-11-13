"""
MainWindow.py
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

from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QAction, QKeySequence, QActionGroup
from PySide6.QtWidgets import (QMainWindow, QDockWidget, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QWidget, QFormLayout, QLineEdit, QPushButton, QPlainTextEdit, QDialog, QVBoxLayout,
    QProgressDialog, QHeaderView, QAbstractItemView, QMenu, QComboBox, QInputDialog)

from SignalIntegrity.GuiCore.Session import ProjectSession, SessionError
from SignalIntegrity.GuiCore import Themes, Settings
from SignalIntegrity.GuiCore.Menus import MenusFor, TOOLBAR, TOOLBAR_LABELS, TOOLBAR_ICON_SIZE
from SignalIntegrity.QtApp import Theme
from SignalIntegrity.QtApp.SchematicView import SchematicView
from SignalIntegrity.QtApp.PartsDock import PartsDock
from SignalIntegrity.QtApp.SimulatorWindow import SimulatorWindow, SParametersWindow, EyeDiagramWindow, NoiseWindow

CALCULATION_TITLES={'simulate':'Simulate','sparameters':'Calculate S-parameters',
                    'virtualprobe':'Virtual Probe','deembed':'De-embed'}

class CalculationWorker(QThread):
    """runs a ProjectSession calculation off the GUI thread"""
    progress=Signal(int)
    succeeded=Signal(object)
    failed=Signal(str)
    def __init__(self,session,kind,parent=None):
        super().__init__(parent)
        self.session=session
        self.kind=kind
        self.cancelled=False
    def _Callback(self,value):
        try:
            self.progress.emit(int(float(value)))
        except (TypeError,ValueError):
            pass
        return not self.cancelled
    def run(self):
        try:
            self.succeeded.emit(self.session.Calculate(self.kind,self._Callback))
        except Exception as e:
            self.failed.emit('calculation cancelled' if self.cancelled else str(e))

class TextDialog(QDialog):
    def __init__(self,title,text,parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(700,450)
        layout=QVBoxLayout(self)
        editor=QPlainTextEdit(text)
        editor.setReadOnly(True)
        layout.addWidget(editor)

class MainWindow(QMainWindow):
    """PySide6 main window for SignalIntegrity projects, built on GuiCore.ProjectSession"""
    def __init__(self,session=None):
        super().__init__()
        self.session=ProjectSession() if session is None else session
        self.selected=None
        self.worker=None
        self.resultsWindows=[]
        self.simulatorWindows={}
        self.eyeWindows={}
        self.lastCalculation=None
        self._updating=False
        self.resize(1200,800)
        self.view=SchematicView(self)
        self.setCentralWidget(self.view)
        self.view.deviceClicked.connect(self.OnDeviceClicked)
        self.view.backgroundClicked.connect(self.OnBackgroundClicked)
        self.view.deviceDoubleClicked.connect(lambda index: self.propertiesDock.raise_())
        self.view.deviceDragged.connect(self.OnDeviceDragged)
        self.view.deviceContextMenu.connect(self.OnDeviceContextMenu)
        self.view.partDropped.connect(self.OnPartDropped)
        self.view.deleteRequested.connect(self.OnDelete)
        self.view.cancelRequested.connect(self.OnCancel)
        self.view.wireFinished.connect(self.OnWireFinished)
        self.view.vertexDragged.connect(self.OnVertexDragged)
        self.setWindowIcon(Theme.AppIcon())
        self._BuildDocks()
        self._BuildActions()
        self.ApplyTheme(*Theme.Apply(save=False))
        self.UpdateTitle()
        self.UpdateEnables()
        self.statusBar().showMessage('Open a SignalIntegrity project (.si) to begin')
    # ---- construction
    def _Table(self,headers):
        table=QTableWidget(0,len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for c,header in enumerate(headers):
            if header in ('Show','Keyword'):
                table.horizontalHeader().setSectionResizeMode(c,QHeaderView.ResizeToContents)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        return table
    def _BuildDocks(self):
        self.partsDock=PartsDock(self)
        self.partsDock.placeRequested.connect(self.OnPlaceRequested)
        self.addDockWidget(Qt.LeftDockWidgetArea,self.partsDock)

        self.variablesTable=self._Table(['Show','Variable','Value','Units'])
        self.variablesTable.itemChanged.connect(self.OnVariableChanged)
        self.variablesDock=QDockWidget('Variables',self)
        self.variablesDock.setObjectName('variables')
        self.variablesDock.setWidget(self.variablesTable)
        self.addDockWidget(Qt.LeftDockWidgetArea,self.variablesDock)

        self.propertiesTable=self._Table(['Show','Keyword','Property','Value','Unit'])
        self.propertiesTable.itemChanged.connect(self.OnPropertyChanged)
        self.propertiesDock=QDockWidget('Device Properties',self)
        self.propertiesDock.setObjectName('properties')
        self.propertiesDock.setWidget(self.propertiesTable)
        self.addDockWidget(Qt.RightDockWidgetArea,self.propertiesDock)

        form=QWidget()
        layout=QFormLayout(form)
        self.calculationEdits={}
        for name in ProjectSession.CALCULATION_PROPERTIES:
            edit=QLineEdit()
            self.calculationEdits[name]=edit
            layout.addRow(name,edit)
        apply=QPushButton('Apply')
        apply.clicked.connect(self.OnApplyCalculationProperties)
        layout.addRow(apply)
        self.calculationDock=QDockWidget('Calculation Properties',self)
        self.calculationDock.setObjectName('calculation')
        self.calculationDock.setWidget(form)
        self.addDockWidget(Qt.LeftDockWidgetArea,self.calculationDock)
        self.tabifyDockWidget(self.variablesDock,self.calculationDock)
        self.variablesDock.raise_()
        self.resizeDocks([self.partsDock],[260],Qt.Horizontal)
    def _Handlers(self):
        """one handler per GuiCore.Menus command id"""
        handlers={'new':self.OnNew,'open':self.OnOpen,'save':self.OnSave,'saveAs':self.OnSaveAs,
                  'archive':self.OnArchive,'extractArchive':self.OnExtractArchive,
                  'exportNetlist':lambda: self.OnExport('netlist'),'exportTikz':lambda: self.OnExport('tikz'),
                  'exportImage':lambda: self.OnExport('image'),
                  'netlist':self.OnNetList,'exit':self.close,
                  'undo':self.OnUndo,'redo':self.OnRedo,
                  'cut':self.OnCut,'copy':self.OnCopy,'paste':self.OnPaste,'duplicate':self.OnDuplicate,
                  'delete':self.OnDelete,'cancel':self.OnCancel,
                  'rotate':self.OnRotate,'properties':self.OnEditProperties,'deletePart':self.OnDeletePart,
                  'flipHorizontal':lambda: self.OnFlip('horizontal'),'flipVertical':lambda: self.OnFlip('vertical'),
                  'wire':self.OnWireMode,'deleteWire':self.OnDeleteWire,
                  'deleteVertex':self.OnDeleteVertex,'duplicateVertex':self.OnDuplicateVertex,
                  'zoomIn':lambda: self.view.Zoom(1.25),'zoomOut':lambda: self.view.Zoom(0.8),'zoomFit':self.view.ZoomFit,
                  'viewDevice':self.OnViewSelected,'up':self.OnAscend,
                  'postProcessing':self.OnPostProcessing,'equations':self.OnEquations,
                  'help':lambda: self.OnHelp('introduction'),'documentation':lambda: self.OnHelp('documentation'),
                  'preferences':self.OnPreferences,'about':self.OnAbout}
        handlers.update({kind:(lambda k=kind: self.RunCalculation(k)) for kind in CALCULATION_TITLES})
        return handlers
    def _SubmenuBuilders(self):
        return {'recent':self.BuildRecentMenu,'theme':self.BuildThemeMenu,'panels':self.BuildPanelsMenu}
    def _BuildActions(self):
        """menus and toolbar come from GuiCore.Menus, shared with the web GUI"""
        handlers=self._Handlers(); builders=self._SubmenuBuilders()
        self.actions={}; self.submenus={}
        for title,items in MenusFor('qt'):
            menu=self.menuBar().addMenu('&'+title)
            for item in items:
                if item['kind']=='separator':
                    menu.addSeparator()
                elif item['kind']=='submenu':
                    submenu=menu.addMenu(item['label'])
                    submenu.aboutToShow.connect(builders[item['id']])
                    self.submenus[item['id']]=submenu
                else:
                    action=QAction(Theme.CommandIcon(item['id']),item['label'],self)
                    action.setIconText(TOOLBAR_LABELS.get(item['id'],item['label'].rstrip('.')))
                    action.setToolTip(item['label'].rstrip('.')+(' ('+item['shortcut']+')' if item['shortcut'] else ''))
                    action.setCheckable(item['checkable'])
                    if item['shortcut']:
                        action.setShortcut(QKeySequence(item['shortcut']))
                        if len(item['shortcut'])==1 or item['shortcut'] in ('Del','Esc'):
                            # single keys (Del, Esc, W) act on the schematic only, not while typing in a table
                            action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
                            self.view.addAction(action)
                    action.triggered.connect(lambda checked=False,h=handlers[item['id']]: h())
                    menu.addAction(action)
                    self.actions[item['id']]=action
        toolBar=self.addToolBar('Main')
        toolBar.setObjectName('main')
        toolBar.setIconSize(QSize(TOOLBAR_ICON_SIZE,TOOLBAR_ICON_SIZE))
        toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        for commandId in TOOLBAR:
            if commandId is None:
                toolBar.addSeparator()
            else:
                toolBar.addAction(self.actions[commandId])
        a=self.actions
        self.newAction,self.openAction,self.saveAction,self.saveAsAction=a['new'],a['open'],a['save'],a['saveAs']
        self.zoomInAction,self.zoomOutAction,self.zoomFitAction=a['zoomIn'],a['zoomOut'],a['zoomFit']
        self.rotateAction,self.deleteAction,self.wireAction=a['rotate'],a['delete'],a['wire']
        self.viewDeviceAction,self.upAction,self.netListAction=a['viewDevice'],a['up'],a['netlist']
        self.calculationActions={kind:a[kind] for kind in CALCULATION_TITLES}
        self.themeMenu=self.submenus['theme']
        self.BuildRecentMenu()
    def BuildPanelsMenu(self):
        menu=self.submenus['panels']
        menu.clear()
        for dock in (self.partsDock,self.variablesDock,self.calculationDock,self.propertiesDock):
            menu.addAction(dock.toggleViewAction())
    def BuildRecentMenu(self):
        menu=self.submenus['recent']
        menu.clear()
        recent=Settings.RecentProjects()
        for number,filename in enumerate(recent,1):
            action=menu.addAction('&%d  %s'%(number%10,os.path.basename(filename)))
            action.setToolTip(filename); action.setStatusTip(filename)
            action.triggered.connect(lambda checked=False,f=filename: self.OpenProject(f))
        if not recent:
            menu.addAction('(no recent projects)').setEnabled(False)
        menu.addSeparator()
        clear=menu.addAction('Clear Recent Projects')
        clear.setEnabled(bool(recent))
        clear.triggered.connect(lambda: (Settings.ClearRecentProjects(),self.BuildRecentMenu()))
        menu.setToolTipsVisible(True)
    # ---- state
    def ApplyTheme(self,themeId,name):
        """recolors the schematic, the stencil and any open plot windows for the current theme"""
        palette=Theme.Current()
        self.view.ApplyPalette(palette)
        self.partsDock.Populate(self.session.PartCatalog(previews=True),Themes.SchematicColorMap(palette))
        for window in list(self.simulatorWindows.values())+[w for w in self.resultsWindows if hasattr(w,'onSelection')]:
            if window.result is not None:
                window.onSelection()
        self.themeName=name
    def BuildThemeMenu(self):
        menu=self.themeMenu
        menu.clear()
        group=QActionGroup(menu)
        current=Theme.CurrentId()
        themes=Themes.DiscoverThemes()
        def add(target,theme):
            action=target.addAction(theme['label'])
            action.setCheckable(True)
            action.setChecked(theme['id']==current)
            action.triggered.connect(lambda checked=False,t=theme: self.SetTheme(t['id'],t['label']))
            group.addAction(action)
        for theme in themes:
            if theme['extension']=='SignalIntegrity':
                add(menu,theme)
        dark=menu.addMenu('VS Code Dark Themes')
        light=menu.addMenu('VS Code Light Themes')
        for theme in themes:
            if theme['extension']!='SignalIntegrity':
                add(light if theme['uiTheme'] in ('vs','hc-light') else dark,theme)
        dark.setEnabled(not dark.isEmpty()); light.setEnabled(not light.isEmpty())
        menu.addSeparator()
        menu.addAction('Load Theme File...',self.OnLoadThemeFile)
    def SetTheme(self,themeId,name=None):
        try:
            self.ApplyTheme(*Theme.Apply(themeId,name))
            self.statusBar().showMessage('theme: '+str(self.themeName))
        except (Themes.ThemeError,OSError) as e:
            self.Error(e)
    def OnLoadThemeFile(self):
        filename,_=QFileDialog.getOpenFileName(self,'Load Theme','',
            'VS Code color themes (*.json *.vsix);;All files (*)')
        if not filename:
            return
        if filename.lower().endswith('.vsix'):
            try:
                themes=Themes.ThemesInPackage(filename)
            except Exception as e:
                return self.Error(e)
            if not themes:
                return self.Error('no color themes in '+filename)
            labels=[t['label'] for t in themes]
            label,ok=QInputDialog.getItem(self,'Load Theme','Theme:',labels,0,False)
            if not ok:
                return
            theme=themes[labels.index(label)]
            return self.SetTheme(theme['id'],theme['label'])
        self.SetTheme(os.path.realpath(filename))
    def UpdateTitle(self):
        if not self.session.IsOpen():
            self.setWindowTitle('SignalIntegrity (Qt) - untitled')
            return
        drawing=self.drawing if getattr(self,'drawing',None) else self.session.Render()
        self.setWindowTitle('SignalIntegrity (Qt) - '+' > '.join(drawing['path'])+(' (Read Only)' if drawing['readOnly'] else ''))
    def UpdateEnables(self):
        isOpen=self.session.IsOpen()
        busy=self.worker is not None
        writable=isOpen and not self.session.readOnly
        capabilities=self.session.Capabilities() if isOpen else {}
        for kind,action in self.calculationActions.items():
            action.setEnabled(isOpen and not busy and capabilities.get(kind,False))
        for action in (self.saveAction,self.saveAsAction):
            action.setEnabled(writable and not busy)
        self.netListAction.setEnabled(isOpen and not busy)
        self.rotateAction.setEnabled(writable and not busy and self.selected is not None)
        selectedWire=self.SelectedWire()
        self.deleteAction.setEnabled(writable and not busy and (self.selected is not None or selectedWire is not None))
        self.actions['deletePart'].setEnabled(writable and not busy and self.selected is not None)
        self.actions['properties'].setEnabled(isOpen and self.selected is not None)
        self.actions['deleteWire'].setEnabled(writable and not busy and selectedWire is not None)
        drawing=getattr(self,'drawing',None) if isOpen else None
        vertex=drawing.get('selectedVertex') if drawing else None
        for commandId in ('deleteVertex','duplicateVertex'):
            self.actions[commandId].setEnabled(writable and not busy and vertex is not None)
        part=writable and not busy and self.selected is not None
        for commandId in ('cut','duplicate','flipHorizontal','flipVertical'):
            self.actions[commandId].setEnabled(part)
        self.actions['copy'].setEnabled(isOpen and not busy and self.selected is not None)
        self.actions['paste'].setEnabled(writable and not busy and self.session.clipboard is not None)
        self.actions['undo'].setEnabled(writable and not busy and self.session.CanUndo())
        self.actions['redo'].setEnabled(writable and not busy and self.session.CanRedo())
        if drawing:
            self.actions['undo'].setText('Undo '+drawing['undoName'] if drawing.get('undoName') else 'Undo')
            self.actions['redo'].setText('Redo '+drawing['redoName'] if drawing.get('redoName') else 'Redo')
        for commandId in ('archive','equations','postProcessing'):
            self.actions[commandId].setEnabled(writable and not busy)
        for commandId in ('exportNetlist','exportTikz','exportImage'):
            self.actions[commandId].setEnabled(isOpen and not busy)
        self.actions['extractArchive'].setEnabled(not busy)
        self.wireAction.setEnabled(writable and not busy)
        if not self.wireAction.isEnabled() and self.wireAction.isChecked():
            self.wireAction.setChecked(False)
            self.view.StopWiring()
        self.partsDock.widget().setEnabled(writable and not busy)
        self.viewDeviceAction.setEnabled(isOpen and not busy and self.selected is not None
                                         and len(self.session.ViewActions(self.selected))>0)
        self.upAction.setEnabled(isOpen and not busy and len(self.session.stack)>0)
        for edit in self.calculationEdits.values():
            edit.setReadOnly(not writable)
        self.openAction.setEnabled(not busy)
        self.newAction.setEnabled(not busy)
    def Redraw(self,fit=False):
        self.drawing=self.session.Render()
        self.view.SetDrawing(self.drawing,fit)
        self.UpdateTitle()
        self.UpdateEnables()
    def Error(self,message):
        QMessageBox.critical(self,'SignalIntegrity',str(message))
    # ---- file
    def OpenProject(self,filename,new=False):
        try:
            drawing=self.session.New(filename) if new else self.session.Open(filename)
        except (SessionError,OSError) as e:
            self.Error(e)
            return False
        for window in list(self.simulatorWindows.values())+list(self.eyeWindows.values())+self.resultsWindows:
            window.close()
        self.simulatorWindows={}; self.eyeWindows={}; self.resultsWindows=[]
        self.ShowLevel(drawing)
        Settings.AddRecentProject(drawing['filename'])
        self.BuildRecentMenu()
        self.statusBar().showMessage(('created ' if new else 'opened ')+drawing['filename']+
                                     ('  -  drag parts from the Parts stencil onto the schematic' if new else ''))
        return True
    def ShowLevel(self,drawing):
        """shows a project level after opening, descending or ascending"""
        self.drawing=drawing
        selected=[d['index'] for d in drawing['devices'] if d['selected']]
        self.selected=selected[0] if selected else None
        self.view.SetDrawing(drawing,fit=True)
        self.RefreshVariables()
        self.RefreshCalculationProperties()
        self.RefreshProperties()
        self.UpdateTitle()
        self.UpdateEnables()
    def OnNew(self):
        filename,_=QFileDialog.getSaveFileName(self,'New Project File','','SignalIntegrity projects (*.si)')
        if filename:
            self.OpenProject(filename,new=True)
    def OnOpen(self):
        filename,_=QFileDialog.getOpenFileName(self,'Open Project','','SignalIntegrity projects (*.si);;All files (*)')
        if filename:
            self.OpenProject(filename)
    def OnSave(self):
        try:
            self.statusBar().showMessage('saved '+self.session.Save())
        except (SessionError,OSError) as e:
            self.Error(e)
    def OnSaveAs(self):
        filename,_=QFileDialog.getSaveFileName(self,'Save Project As',self.session.filename or '','SignalIntegrity projects (*.si)')
        if filename:
            try:
                saved=self.session.Save(filename)
                Settings.AddRecentProject(saved)
                self.BuildRecentMenu()
                self.statusBar().showMessage('saved '+saved)
            except (SessionError,OSError) as e:
                self.Error(e)
            self.UpdateTitle()
    # ---- tables
    def _CheckItem(self,checked,editable):
        item=QTableWidgetItem()
        flags=Qt.ItemIsEnabled|Qt.ItemIsUserCheckable if editable else Qt.ItemIsEnabled
        item.setFlags(flags)
        item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        return item
    def _FillTable(self,table,rows,valueColumn):
        """rows are (checks,cells,editable,choices): checks are leading checkbox values, choices an enum list"""
        self._updating=True
        table.setRowCount(0)
        table.setRowCount(len(rows))
        for r,(checks,cells,editable,choices) in enumerate(rows):
            for c,checked in enumerate(checks):
                table.setItem(r,c,self._CheckItem(checked,editable))
            for c,text in enumerate(cells,len(checks)):
                hasCombo=c==valueColumn and bool(choices)
                item=QTableWidgetItem('' if text is None or hasCombo else str(text))
                flags=Qt.ItemIsSelectable|Qt.ItemIsEnabled
                if c==valueColumn and editable and not choices:
                    flags|=Qt.ItemIsEditable
                item.setFlags(flags)
                table.setItem(r,c,item)
                if c==valueColumn and choices:
                    combo=QComboBox()
                    combo.addItems(choices)
                    combo.setCurrentText(str(text))
                    combo.setEnabled(editable)
                    combo.currentTextChanged.connect(lambda value,row=r: self.OnEnumChanged(row,value))
                    table.setCellWidget(r,c,combo)
        self._updating=False
    def RefreshVariables(self):
        variables=self.session.Variables() if self.session.IsOpen() else []
        self.variableNames=[v['name'] for v in variables]
        self._FillTable(self.variablesTable,[((v['visible'],),(v['name'],v['value'],v['units']),not v['readOnly'],None)
                                             for v in variables],2)
    def RefreshProperties(self):
        properties=[] if self.selected is None else self.session.DeviceProperties(self.selected)
        self.propertyKeywords=[p['keyword'] for p in properties]
        self._FillTable(self.propertiesTable,[((p['visible'],p['keywordVisible']),(p['description'] or p['name'],p['value'],p['unit']),
                                               not p['readOnly'],p['validEntries']) for p in properties],3)
    def RefreshCalculationProperties(self):
        values=self.session.CalculationProperties()
        for name,edit in self.calculationEdits.items():
            edit.setText(str(values[name]))
    def OnVariableChanged(self,item):
        if self._updating or item.column() not in (0,2):
            return
        name=self.variableNames[item.row()]
        try:
            if item.column()==0:
                self.session.SetVariableVisible(name,item.checkState()==Qt.Checked)
            else:
                self.session.SetVariable(name,item.text())
        except SessionError as e:
            self.Error(e)
        self.RefreshVariables()
        self.RefreshProperties()
        self.Redraw()
    def OnPropertyChanged(self,item):
        if self._updating or self.selected is None or item.column() not in (0,1,3):
            return
        keyword=self.propertyKeywords[item.row()]
        try:
            if item.column()==0:
                self.session.SetDevicePropertyVisibility(self.selected,keyword,visible=item.checkState()==Qt.Checked)
            elif item.column()==1:
                self.session.SetDevicePropertyVisibility(self.selected,keyword,keywordVisible=item.checkState()==Qt.Checked)
            else:
                self.session.SetDeviceProperty(self.selected,keyword,item.text())
        except SessionError as e:
            self.Error(e)
        self.RefreshProperties()
        self.Redraw()
    def OnEnumChanged(self,row,value):
        if self._updating or self.selected is None:
            return
        try:
            self.session.SetDeviceProperty(self.selected,self.propertyKeywords[row],value)
        except SessionError as e:
            self.Error(e)
        self.RefreshProperties()
        self.Redraw()
    def OnApplyCalculationProperties(self):
        try:
            self.session.SetCalculationProperties({name:edit.text() for name,edit in self.calculationEdits.items()})
        except (SessionError,ValueError) as e:
            self.Error(e)
        self.RefreshCalculationProperties()
    # ---- devices
    def SelectedWire(self):
        drawing=getattr(self,'drawing',None)
        if not drawing or not self.session.IsOpen():
            return None
        return next((w['index'] for w in drawing.get('wires',[]) if w['selected']),None)
    def OnDeviceClicked(self,index):
        if not self.session.IsOpen() or (index==self.selected and self.SelectedWire() is None):
            return
        self.selected=self.session.Select(index)
        self.RefreshProperties()
        self.Redraw()
    def OnBackgroundClicked(self,x,y):
        """starts dragging the wire corner under the pointer, selects the wire under it, or deselects everything"""
        if not self.session.IsOpen():
            return
        # within 5 screen pixels at any zoom, but never less than a quarter grid
        tolerance=max(0.25*self.view.grid,5./max(self.view.transform().m11(),1e-6))
        vertex=self.session.VertexAt(x,y,tolerance)
        if vertex is not None:
            self.session.SelectVertex(*vertex)
            self.selected=None
            self.RefreshProperties()
            self.Redraw()
            if not self.session.readOnly:
                self.view.BeginVertexDrag(*vertex)
            self.statusBar().showMessage('wire corner selected: drag it, or use Wires > Delete Vertex / Duplicate Vertex')
            return
        wire=self.session.WireAt(x,y,tolerance)
        if wire is None:
            return self.OnDeviceClicked(None)
        self.session.SelectWire(wire)
        self.selected=None
        self.RefreshProperties()
        self.Redraw()
        self.statusBar().showMessage('wire selected (Del deletes it)')
    def OnVertexDragged(self,wire,vertex,x,y):
        self._Do(lambda: self.session.MoveVertex(wire,vertex,x,y),'wire corner moved')
    def OnDeviceDragged(self,index,dx,dy):
        if self.session.readOnly:
            return
        self.session.MoveDevice(index,dx,dy)
        self.Redraw()
    def OnRotate(self):
        if self.selected is not None and not self.session.readOnly:
            self.session.RotateDevice(self.selected)
            self.Redraw()
    # ---- the parts stencil
    def OnPlaceRequested(self,index):
        if not self.session.IsOpen() or self.session.readOnly:
            return
        if self.wireAction.isChecked():
            self.wireAction.setChecked(False)
            self.view.StopWiring()
        self.view.StartPlacing(index)
        name=self.partsDock.catalog[index]['partname'] if index<len(self.partsDock.catalog) else 'part'
        self.statusBar().showMessage('click on the schematic to place '+name+' (Esc cancels)')
    def OnPartDropped(self,index,x,y):
        if not self.session.IsOpen():
            return self.Error('open or create a project before adding parts')
        try:
            self.selected=self.session.AddPart(index,x,y)
        except SessionError as e:
            return self.Error(e)
        self.RefreshProperties()
        self.Redraw()
        self.propertiesDock.raise_()
        self.statusBar().showMessage('added '+self.session.Render()['devices'][self.selected]['partname'])
    def OnDelete(self):
        """tk Edit > Delete Selected: the selected wire or part"""
        if self.SelectedWire() is not None:
            return self.OnDeleteWire()
        self.OnDeletePart()
    def OnDeletePart(self):
        if self.selected is None or self.session.readOnly or self.worker is not None:
            return
        try:
            self.session.DeleteDevice(self.selected)
        except SessionError as e:
            return self.Error(e)
        self.selected=None
        self.RefreshProperties()
        self.Redraw()
    def OnEditProperties(self):
        self.propertiesDock.show()
        self.propertiesDock.raise_()
        self.propertiesTable.setFocus()
    def OnCancel(self):
        """Esc: drop the wire being drawn, then leave wire mode; or stop placing a part"""
        if self.view.wiring:
            if not self.view.CancelWire():
                self.wireAction.setChecked(False)
                self.view.StopWiring()
                self.statusBar().showMessage('wire mode off')
        elif self.view.placing is not None:
            self.view.StopPlacing()
            self.statusBar().showMessage('placement cancelled')
    # ---- wires
    def OnWireMode(self):
        if self.wireAction.isChecked():
            self.view.StartWiring()
            self.statusBar().showMessage('Add Wire: click each corner, double-click or right-click to finish a wire, Esc to stop')
        else:
            self.view.StopWiring()
            self.statusBar().showMessage('wire mode off')
    def OnWireFinished(self,points):
        try:
            self.session.AddWire(points)
        except SessionError as e:
            return self.Error(e)
        self.selected=None
        self.RefreshProperties()
        self.Redraw()
        self.statusBar().showMessage('wire added - keep clicking to draw another, Esc to stop')
    def OnDeleteWire(self):
        wire=self.SelectedWire()
        if wire is None or self.session.readOnly or self.worker is not None:
            return
        try:
            self.session.DeleteWire(wire)
        except SessionError as e:
            return self.Error(e)
        self.Redraw()
        self.statusBar().showMessage('wire deleted')
    # ---- hierarchy traversal and device views (tk right-click View / Open Project)
    def OnDeviceContextMenu(self,index,globalPos,control):
        if self.worker is not None:
            return
        self.OnDeviceClicked(index)
        actions=self.session.ViewActions(index)
        if control and actions:
            # like the tk app, ctrl-right-click goes straight to the project
            keys=[a['action'] for a in actions]
            self.ViewDevice(index,'openproject' if 'openproject' in keys else keys[0])
            return
        menu=QMenu(self)
        for a in actions:
            menu.addAction(a['label'],lambda action=a['action']: self.ViewDevice(index,action))
        if not self.session.readOnly:
            if actions:
                menu.addSeparator()
            menu.addAction('Edit Properties',self.propertiesDock.raise_)
            menu.addAction('Rotate',self.OnRotate)
        if self.session.stack:
            menu.addSeparator()
            menu.addAction('Up to Parent Project',self.OnAscend)
        if not menu.isEmpty():
            menu.exec(globalPos)
    def OnViewSelected(self):
        if self.selected is None:
            return
        actions=self.session.ViewActions(self.selected)
        if actions:
            keys=[a['action'] for a in actions]
            self.ViewDevice(self.selected,'openproject' if 'openproject' in keys else keys[0])
    def ViewDevice(self,index,action):
        try:
            kind,value=self.session.View(index,action)
        except SessionError as e:
            self.Error(e)
            return
        if kind=='project':
            self.ShowLevel(value)
            self.statusBar().showMessage('opened '+value['filename']+' (read only)')
        elif value.waveforms:
            window=SimulatorWindow(self,recalculatable=False).UpdateResult(value,'Waveform: '+value.title)
            self.resultsWindows.append(window)
            window.show()
        else:
            window=SParametersWindow(value,'S-parameters: '+value.title,self)
            self.resultsWindows.append(window)
            window.show()
    def OnAscend(self):
        try:
            self.ShowLevel(self.session.Ascend())
        except SessionError as e:
            self.Error(e)
    # ---- calculation
    def RunCalculation(self,kind):
        if self.worker is not None:
            return
        self.worker=CalculationWorker(self.session,kind,self)
        self.progressDialog=QProgressDialog(CALCULATION_TITLES[kind]+'...','Cancel',0,100,self)
        self.progressDialog.setWindowModality(Qt.WindowModal)
        self.progressDialog.setMinimumDuration(300)
        self.progressDialog.canceled.connect(self._CancelCalculation)
        self.worker.progress.connect(self.progressDialog.setValue)
        self.worker.succeeded.connect(lambda result,k=kind: self._CalculationSucceeded(k,result))
        self.worker.failed.connect(self._CalculationFailed)
        self.worker.finished.connect(self._CalculationFinished)
        self.UpdateEnables()
        self.worker.start()
    def _CancelCalculation(self):
        if self.worker is not None:
            self.worker.cancelled=True
    def _CalculationSucceeded(self,kind,result):
        self.lastCalculation=kind
        title=os.path.basename(self.session.filename)
        if result.waveforms:
            key=self.session.filename
            window=self.simulatorWindows.get(key)
            if window is None:
                window=SimulatorWindow(self)
                window.recalculate.connect(lambda: self.lastCalculation and self.RunCalculation(self.lastCalculation))
                self.simulatorWindows[key]=window
            window.UpdateResult(result,'Sim: '+title)
            window.show(); window.raise_()
        if result.sparameters:
            window=SParametersWindow(result,CALCULATION_TITLES[kind]+' - '+title,self)
            self.resultsWindows.append(window)
            window.show()
        for name,image in result.eyes:
            if name in self.eyeWindows:
                self.eyeWindows[name].close()
            self.eyeWindows[name]=EyeDiagramWindow(name,image,self)
            self.eyeWindows[name].show()
        if result.noise:
            window=NoiseWindow(result,'Statistical Noise: '+title,self)
            self.resultsWindows.append(window)
            window.show()
    def _CalculationFailed(self,message):
        self.Error(message)
    def _CalculationFinished(self):
        self.progressDialog.reset()
        self.worker=None
        self.Redraw()
    def OnNetList(self):
        try:
            TextDialog('Netlist',self.session.NetList(),self).exec()
        except SessionError as e:
            self.Error(e)
    # ---- edits that go through _Do refresh everything an undo step can change
    def _Do(self,edit,message=None,refreshTables=False):
        try:
            result=edit()
        except SessionError as e:
            self.Error(e)
            return None
        self.drawing=self.session.Render()
        selected=[d['index'] for d in self.drawing['devices'] if d['selected']]
        self.selected=selected[0] if selected else None
        if refreshTables:
            self.RefreshVariables()
            self.RefreshCalculationProperties()
        self.RefreshProperties()
        self.Redraw()
        if message:
            self.statusBar().showMessage(message if not callable(message) else message(result))
        return result
    def OnUndo(self):
        self._Do(self.session.Undo,lambda name: 'undid '+name,refreshTables=True)
    def OnRedo(self):
        self._Do(self.session.Redo,lambda name: 'redid '+name,refreshTables=True)
    def OnCopy(self):
        if self.selected is not None:
            self.session.Copy(self.selected)
            self.UpdateEnables()
            self.statusBar().showMessage('part copied (Ctrl+V pastes it)')
    def OnCut(self):
        if self.selected is not None:
            self._Do(lambda: self.session.Cut(self.selected),'part cut (Ctrl+V pastes it)')
    def OnPaste(self):
        self._Do(self.session.Paste,'part pasted - drag it into place')
    def OnDuplicate(self):
        if self.selected is not None:
            self._Do(lambda: self.session.Duplicate(self.selected),'part duplicated - drag it into place')
    def OnFlip(self,direction):
        if self.selected is not None:
            self._Do(lambda: self.session.FlipDevice(self.selected,direction),'flipped '+direction+'ly')
    def _Vertex(self):
        return (getattr(self,'drawing',None) or {}).get('selectedVertex')
    def OnDeleteVertex(self):
        vertex=self._Vertex()
        if vertex is not None:
            self._Do(lambda: self.session.DeleteVertex(*vertex),'wire corner deleted')
    def OnDuplicateVertex(self):
        vertex=self._Vertex()
        if vertex is not None:
            self._Do(lambda: self.session.DuplicateVertex(*vertex),'wire corner duplicated - drag it to make a bend')
    # ---- equations, post-processing, preferences and help
    def OnEquations(self):
        from SignalIntegrity.QtApp.Dialogs import TextEditorDialog
        dialog=TextEditorDialog('Schematic Equations',self.session.Equations(),self.session.CheckEquations,'equations',self)
        if dialog.exec():
            error=self._Do(lambda: self.session.SetEquations(dialog.Text()),'equations applied',refreshTables=True)
            if error:
                self.statusBar().showMessage('equations stored, but they have an error: '+error)
    def OnPostProcessing(self):
        from SignalIntegrity.QtApp.Dialogs import TextEditorDialog
        dialog=TextEditorDialog('Post-Processing',self.session.PostProcessing(),None,'postprocessing',self)
        if dialog.exec():
            self._Do(lambda: self.session.SetPostProcessing(dialog.Text()),'post-processing applied')
    def OnPreferences(self):
        from SignalIntegrity.QtApp.Dialogs import PreferencesDialog
        PreferencesDialog(self).exec()
    def OnHelp(self,topic):
        from SignalIntegrity.GuiCore import Help
        try:
            self.statusBar().showMessage('opened '+Help.Open(topic))
        except Exception as e:
            self.Error('could not open the help: '+str(e))
    # ---- archives and exports
    def OnArchive(self):
        target=os.path.splitext(self.session.filename)[0]+'.siz'
        if os.path.exists(target) and QMessageBox.question(self,'Archive Project',
                'The archive exists. Overwrite '+target+'?')!=QMessageBox.Yes:
            return
        try:
            self.statusBar().showMessage('archived to '+self.session.Archive())
        except SessionError as e:
            self.Error(e)
    def OnExtractArchive(self):
        filename,_=QFileDialog.getOpenFileName(self,'Extract Archived Project','','SignalIntegrity archives (*.siz)')
        if not filename:
            return
        try:
            drawing=self.session.ExtractArchive(filename)
        except SessionError as e:
            return self.Error(e)
        for window in list(self.simulatorWindows.values())+list(self.eyeWindows.values())+self.resultsWindows:
            window.close()
        self.simulatorWindows={}; self.eyeWindows={}; self.resultsWindows=[]
        self.ShowLevel(drawing)
        Settings.AddRecentProject(drawing['filename'])
        self.BuildRecentMenu()
        self.statusBar().showMessage('extracted and opened '+drawing['filename'])
    EXPORTS={'netlist':('Export NetList','netlist (*.txt);;All files (*)','.txt'),
             'tikz':('Export LaTeX (TikZ)','TpX drawing with TikZ (*.TpX);;TikZ picture (*.tex)','.TpX'),
             'image':('Export Bitmap Image','PNG image (*.png);;JPEG image (*.jpg)','.png')}
    def OnExport(self,kind):
        title,filters,extension=self.EXPORTS[kind]
        start=os.path.splitext(self.session.filename)[0]+extension
        filename,_=QFileDialog.getSaveFileName(self,title,start,filters)
        if not filename:
            return
        try:
            if kind=='netlist':
                written=self.session.ExportNetList(filename)
            elif kind=='tikz':
                written=self.session.ExportTikZ(filename)
            else:
                written=self.session.ExportImage(filename)
            self.statusBar().showMessage('exported '+written)
        except (SessionError,OSError) as e:
            self.Error(e)
    def OnAbout(self):
        from SignalIntegrity.__about__ import __version__
        QMessageBox.about(self,'About SignalIntegrity (Qt)',
            'SignalIntegrity '+__version__+'\nPySide6 user interface\n\n'
            'Projects are fully compatible with the tk application.')
