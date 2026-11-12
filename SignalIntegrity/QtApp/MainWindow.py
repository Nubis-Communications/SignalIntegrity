"""
MainWindow.py
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

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QMainWindow, QDockWidget, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QWidget, QFormLayout, QLineEdit, QPushButton, QPlainTextEdit, QDialog, QVBoxLayout,
    QProgressDialog, QHeaderView, QAbstractItemView)

from SignalIntegrity.GuiCore.Session import ProjectSession, SessionError
from SignalIntegrity.QtApp.SchematicView import SchematicView
from SignalIntegrity.QtApp.ResultsWindow import ResultsWindow

CALCULATION_TITLES={'simulate':'Simulate','sparameters':'Calculate S-parameters',
                    'virtualprobe':'Virtual Probe','deembed':'De-embed'}

class CalculationWorker(QThread):
    """runs a ProjectSession calculation off the GUI thread"""
    progress=Signal(int)
    succeeded=Signal(dict)
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
        self._updating=False
        self.resize(1200,800)
        self.view=SchematicView(self)
        self.setCentralWidget(self.view)
        self.view.deviceClicked.connect(self.OnDeviceClicked)
        self.view.deviceDoubleClicked.connect(lambda index: self.propertiesDock.raise_())
        self.view.deviceDragged.connect(self.OnDeviceDragged)
        self._BuildDocks()
        self._BuildActions()
        self.UpdateTitle()
        self.UpdateEnables()
        self.statusBar().showMessage('Open a SignalIntegrity project (.si) to begin')
    # ---- construction
    def _Table(self,headers):
        table=QTableWidget(0,len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        return table
    def _BuildDocks(self):
        self.variablesTable=self._Table(['Variable','Value','Units'])
        self.variablesTable.itemChanged.connect(self.OnVariableChanged)
        self.variablesDock=QDockWidget('Variables',self)
        self.variablesDock.setObjectName('variables')
        self.variablesDock.setWidget(self.variablesTable)
        self.addDockWidget(Qt.LeftDockWidgetArea,self.variablesDock)

        self.propertiesTable=self._Table(['Property','Value','Unit'])
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
        for dock in (self.variablesDock,self.calculationDock,self.propertiesDock):
            viewMenu.addAction(dock.toggleViewAction())
        deviceMenu=menuBar.addMenu('&Device')
        self.rotateAction=self._Action(deviceMenu,'&Rotate',self.OnRotate,'Ctrl+R')
        calculateMenu=menuBar.addMenu('&Calculate')
        self.calculationActions={kind:self._Action(calculateMenu,title,lambda checked=False,k=kind: self.RunCalculation(k))
                                 for kind,title in CALCULATION_TITLES.items()}
        calculateMenu.addSeparator()
        self.netListAction=self._Action(calculateMenu,'Show &Netlist',self.OnNetList)
        helpMenu=menuBar.addMenu('&Help')
        self._Action(helpMenu,'&About',self.OnAbout)
        for action in [self.openAction,self.saveAction,None,self.zoomInAction,self.zoomOutAction,self.zoomFitAction,None,
                       self.rotateAction,None]+list(self.calculationActions.values()):
            if action is None:
                toolBar.addSeparator()
            else:
                toolBar.addAction(action)
    # ---- state
    def UpdateTitle(self):
        name=os.path.basename(self.session.filename) if self.session.IsOpen() else 'untitled'
        self.setWindowTitle('SignalIntegrity (Qt) - '+name)
    def UpdateEnables(self):
        isOpen=self.session.IsOpen()
        busy=self.worker is not None
        capabilities=self.session.Capabilities() if isOpen else {}
        for kind,action in self.calculationActions.items():
            action.setEnabled(isOpen and not busy and capabilities.get(kind,False))
        for action in (self.saveAction,self.saveAsAction,self.netListAction):
            action.setEnabled(isOpen and not busy)
        self.rotateAction.setEnabled(isOpen and not busy and self.selected is not None)
        self.openAction.setEnabled(not busy)
    def Redraw(self,fit=False):
        self.view.SetDrawing(self.session.Render(),fit)
        self.UpdateEnables()
    def Error(self,message):
        QMessageBox.critical(self,'SignalIntegrity',str(message))
    # ---- file
    def OpenProject(self,filename):
        try:
            drawing=self.session.Open(filename)
        except SessionError as e:
            self.Error(e)
            return False
        self.selected=None
        self.view.SetDrawing(drawing,fit=True)
        self.RefreshVariables()
        self.RefreshCalculationProperties()
        self.RefreshProperties()
        self.UpdateTitle()
        self.UpdateEnables()
        self.statusBar().showMessage('opened '+drawing['filename'])
        return True
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
    def _FillTable(self,table,rows):
        self._updating=True
        table.setRowCount(len(rows))
        for r,(cells,editable) in enumerate(rows):
            for c,text in enumerate(cells):
                item=QTableWidgetItem('' if text is None else str(text))
                flags=Qt.ItemIsSelectable|Qt.ItemIsEnabled
                if c==1 and editable:
                    flags|=Qt.ItemIsEditable
                item.setFlags(flags)
                table.setItem(r,c,item)
        self._updating=False
    def RefreshVariables(self):
        variables=self.session.Variables() if self.session.IsOpen() else []
        self._FillTable(self.variablesTable,[((v['name'],v['value'],v['units']),not v['readOnly']) for v in variables])
    def RefreshProperties(self):
        properties=[] if self.selected is None else self.session.DeviceProperties(self.selected)
        self.propertyKeywords=[p['keyword'] for p in properties]
        self._FillTable(self.propertiesTable,[((p['description'] or p['name'],p['value'],p['unit']),not p['readOnly']) for p in properties])
    def RefreshCalculationProperties(self):
        values=self.session.CalculationProperties()
        for name,edit in self.calculationEdits.items():
            edit.setText(str(values[name]))
    def OnVariableChanged(self,item):
        if self._updating or item.column()!=1:
            return
        name=self.variablesTable.item(item.row(),0).text()
        try:
            self.session.SetVariable(name,item.text())
        except SessionError as e:
            self.Error(e)
        self.RefreshVariables()
        self.RefreshProperties()
        self.Redraw()
    def OnPropertyChanged(self,item):
        if self._updating or item.column()!=1 or self.selected is None:
            return
        try:
            self.session.SetDeviceProperty(self.selected,self.propertyKeywords[item.row()],item.text())
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
        self.session.MoveDevice(index,dx,dy)
        self.Redraw()
    def OnRotate(self):
        if self.selected is not None:
            self.session.RotateDevice(self.selected)
            self.Redraw()
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
        window=ResultsWindow(result,CALCULATION_TITLES[kind]+' - '+os.path.basename(self.session.filename),self)
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
    def OnAbout(self):
        from SignalIntegrity.__about__ import __version__
        QMessageBox.about(self,'About SignalIntegrity (Qt)',
            'SignalIntegrity '+__version__+'\nPySide6 user interface\n\n'
            'Projects are fully compatible with the tk application.')
