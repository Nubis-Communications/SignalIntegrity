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

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction, QKeySequence, QActionGroup
from PySide6.QtWidgets import (QMainWindow, QDockWidget, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QWidget, QFormLayout, QLineEdit, QPushButton, QPlainTextEdit, QDialog, QVBoxLayout,
    QProgressDialog, QHeaderView, QAbstractItemView, QMenu, QComboBox, QInputDialog)

from SignalIntegrity.GuiCore.Session import ProjectSession, SessionError
from SignalIntegrity.GuiCore import Themes
from SignalIntegrity.QtApp import Theme
from SignalIntegrity.QtApp.SchematicView import SchematicView
from SignalIntegrity.QtApp.PartsDock import PartsDock
from SignalIntegrity.QtApp.SimulatorWindow import SimulatorWindow, SParametersWindow, EyeDiagramWindow

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
        self.view.deviceDoubleClicked.connect(lambda index: self.propertiesDock.raise_())
        self.view.deviceDragged.connect(self.OnDeviceDragged)
        self.view.deviceContextMenu.connect(self.OnDeviceContextMenu)
        self.view.partDropped.connect(self.OnPartDropped)
        self.view.deleteRequested.connect(self.OnDelete)
        self.view.placingCancelled.connect(lambda: self.statusBar().showMessage('placement cancelled'))
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
    def _Action(self,menu,text,slot,shortcut=None):
        action=QAction(text,self)
        if shortcut is not None:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        menu.addAction(action)
        return action
    def _BuildActions(self):
        menuBar=self.menuBar()
        toolBar=self.addToolBar('Main')
        toolBar.setObjectName('main')
        fileMenu=menuBar.addMenu('&File')
        self.newAction=self._Action(fileMenu,'&New Project...',self.OnNew,QKeySequence.New)
        self.openAction=self._Action(fileMenu,'&Open...',self.OnOpen,QKeySequence.Open)
        self.saveAction=self._Action(fileMenu,'&Save',self.OnSave,QKeySequence.Save)
        self.saveAsAction=self._Action(fileMenu,'Save &As...',self.OnSaveAs,QKeySequence.SaveAs)
        fileMenu.addSeparator()
        self._Action(fileMenu,'E&xit',self.close,QKeySequence.Quit)
        viewMenu=menuBar.addMenu('&View')
        self.zoomInAction=self._Action(viewMenu,'Zoom &In',lambda: self.view.Zoom(1.25),QKeySequence.ZoomIn)
        self.zoomOutAction=self._Action(viewMenu,'Zoom &Out',lambda: self.view.Zoom(0.8),QKeySequence.ZoomOut)
        self.zoomFitAction=self._Action(viewMenu,'Zoom to &Fit',self.view.ZoomFit,'Ctrl+0')
        viewMenu.addSeparator()
        for dock in (self.partsDock,self.variablesDock,self.calculationDock,self.propertiesDock):
            viewMenu.addAction(dock.toggleViewAction())
        viewMenu.addSeparator()
        self.themeMenu=viewMenu.addMenu('&Theme')
        self.themeMenu.aboutToShow.connect(self.BuildThemeMenu)
        deviceMenu=menuBar.addMenu('&Device')
        self.rotateAction=self._Action(deviceMenu,'&Rotate',self.OnRotate,'Ctrl+R')
        self.deleteAction=self._Action(deviceMenu,'&Delete',self.OnDelete)
        self.viewDeviceAction=self._Action(deviceMenu,'&View / Open Project',self.OnViewSelected,'Ctrl+E')
        self.upAction=self._Action(deviceMenu,'&Up to Parent Project',self.OnAscend,'Alt+Up')
        calculateMenu=menuBar.addMenu('&Calculate')
        self.calculationActions={kind:self._Action(calculateMenu,title,lambda checked=False,k=kind: self.RunCalculation(k))
                                 for kind,title in CALCULATION_TITLES.items()}
        calculateMenu.addSeparator()
        self.netListAction=self._Action(calculateMenu,'Show &Netlist',self.OnNetList)
        helpMenu=menuBar.addMenu('&Help')
        self._Action(helpMenu,'&About',self.OnAbout)
        for action in [self.newAction,self.openAction,self.saveAction,None,self.zoomInAction,self.zoomOutAction,self.zoomFitAction,None,
                       self.rotateAction,self.viewDeviceAction,self.upAction,None]+list(self.calculationActions.values()):
            if action is None:
                toolBar.addSeparator()
            else:
                toolBar.addAction(action)
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
        self.deleteAction.setEnabled(writable and not busy and self.selected is not None)
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
                self.statusBar().showMessage('saved '+self.session.Save(filename))
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
    def OnDeviceClicked(self,index):
        if not self.session.IsOpen() or index==self.selected:
            return
        self.selected=self.session.Select(index)
        self.RefreshProperties()
        self.Redraw()
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
        if self.selected is None or self.session.readOnly or self.worker is not None:
            return
        try:
            self.session.DeleteDevice(self.selected)
        except SessionError as e:
            return self.Error(e)
        self.selected=None
        self.RefreshProperties()
        self.Redraw()
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
    def OnAbout(self):
        from SignalIntegrity.__about__ import __version__
        QMessageBox.about(self,'About SignalIntegrity (Qt)',
            'SignalIntegrity '+__version__+'\nPySide6 user interface\n\n'
            'Projects are fully compatible with the tk application.')
