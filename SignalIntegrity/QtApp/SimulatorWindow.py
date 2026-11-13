"""
SimulatorWindow.py
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

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QHBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT

from SignalIntegrity.Lib.ToSI import ToSI, FromSI

def _Preference(name,default):
    try:
        import SignalIntegrity.App.Project
        return SignalIntegrity.App.Preferences[name]
    except Exception:
        return default

def _SetPreference(name,value):
    try:
        import SignalIntegrity.App.Project
        SignalIntegrity.App.Preferences[name]=value
        SignalIntegrity.App.Preferences.SaveToFile()
    except Exception:
        pass

def _Colors():
    import matplotlib
    return matplotlib.rcParams['axes.prop_cycle'].by_key()['color']

class PlotPanel(QWidget):
    """matplotlib figure with the navigation toolbar starting in pan mode and an autoscale button,
    which is how the tk simulator and s-parameter windows behave"""
    def __init__(self,parent=None):
        super().__init__(parent)
        layout=QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.label=QLabel()
        layout.addWidget(self.label)
        self.figure=Figure(tight_layout=True)
        self.axes=self.figure.add_subplot(111)
        self.canvas=FigureCanvasQTAgg(self.figure)
        self.toolbar=NavigationToolbar2QT(self.canvas,self)
        self.toolbar.pan()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas,1)
        controls=QHBoxLayout()
        self.autoscaleButton=QPushButton('autoscale')
        controls.addWidget(self.autoscaleButton)
        controls.addStretch(1)
        layout.addLayout(controls)

class SimulatorWindow(QMainWindow):
    """port of the tk SimulatorDialog: the same window is reused for every recalculation so the
    zoom is kept, waveforms can be selected for display, and spectral views are available"""
    recalculate=Signal()
    def __init__(self,parent=None,recalculatable=True):
        super().__init__(parent)
        self.resize(1000,650)
        self.panel=PlotPanel(self)
        self.setCentralWidget(self.panel)
        self.plt=self.panel.axes
        self.panel.autoscaleButton.clicked.connect(self.onAutoscale)
        self.result=None
        self.selections=[]
        self.zoomsInitialized=False
        self.minx=self.maxx=self.miny=self.maxy=None
        self.timeLabelDivisor=1.
        menuBar=self.menuBar()
        fileMenu=menuBar.addMenu('&File')
        self.saveAction=fileMenu.addAction('Save Waveforms',self.onWriteSimulatorToFile)
        self.selectionMenu=menuBar.addMenu('&Selection')
        self.selectionMenu.addAction('Display All',lambda: self._SetAll(lambda s: True))
        self.selectionMenu.addAction('Display None',lambda: self._SetAll(lambda s: False))
        self.selectionMenu.addAction('Toggle All',lambda: self._SetAll(lambda s: not s))
        self.selectionMenu.addSeparator()
        calcMenu=menuBar.addMenu('&Calculate')
        self.recalculateAction=calcMenu.addAction('Recalculate',self.recalculate.emit)
        self.recalculateAction.setEnabled(recalculatable)
        viewMenu=menuBar.addMenu('&View')
        self.showGridsAction=self._Check(viewMenu,'Show Grids',_Preference('Appearance.GridsOnPlots',True),self.onShowGrids)
        group=QActionGroup(self)
        self.timeAction=self._Check(viewMenu,'View Time-domain',True,lambda: self._ChangeView())
        self.contentAction=self._Check(viewMenu,'View Spectral Content',False,lambda: self._ChangeView())
        self.densityAction=self._Check(viewMenu,'View Spectral Density',False,lambda: self._ChangeView())
        for action in (self.timeAction,self.contentAction,self.densityAction):
            group.addAction(action)
        self.logScaleAction=self._Check(viewMenu,'Log Frequency Scale',_Preference('SParameterProperties.Plot.LogScale',False),self.onLogScale)
    def _Check(self,menu,text,checked,slot):
        action=QAction(text,self)
        action.setCheckable(True)
        action.setChecked(bool(checked))
        action.triggered.connect(slot)
        menu.addAction(action)
        return action
    # ---- waveforms
    def UpdateResult(self,result,title=None):
        """shows a GuiCore ResultData, keeping the current zoom like the tk dialog does"""
        if title is not None:
            self.setWindowTitle(title)
        previous={name:action.isChecked() for name,action in zip(self.Names(),self.selections)}
        self.result=result
        for action in self.selections:
            self.selectionMenu.removeAction(action)
        self.selections=[]
        for name in self.Names():
            action=QAction(name,self)
            action.setCheckable(True)
            action.setChecked(previous.get(name,True))
            action.triggered.connect(self.onSelection)
            self.selectionMenu.addAction(action)
            self.selections.append(action)
        self.selectionMenu.setEnabled(len(self.selections)>1)
        self.onSelection()
        return self
    def Names(self):
        return [] if self.result is None else [name for name,_ in self.result.waveforms]
    def SelectedIndices(self):
        return [i for i,action in enumerate(self.selections) if action.isChecked()]
    def _SetAll(self,rule):
        for action in self.selections:
            action.setChecked(rule(action.isChecked()))
        self.onSelection()
    def View(self):
        return 'time' if self.timeAction.isChecked() else 'content' if self.contentAction.isChecked() else 'density'
    def onSelection(self):
        indices=self.SelectedIndices()
        if len(indices)==1:
            wf=self.result.waveforms[indices[0]][1]
            if self.result.IsDC(wf):
                self.statusBar().showMessage('DC waveform  = '+str(wf))
            else:
                self.statusBar().showMessage(ToSI(wf.td.K,'Pts')+' starting at '+ToSI(wf.td.H,'s')+' at '+
                    ToSI(wf.td.Fs,'S/s')+' (T = '+ToSI(1./wf.td.Fs,'s')+')')
        elif len(indices)==0:
            self.statusBar().showMessage('No Waveforms')
        else:
            self.statusBar().showMessage('Multiple Waveforms')
        if self.View()=='time':
            self.PlotTimeDomain()
        else:
            self.PlotFrequencyContent(self.View()=='density')
    def _ChangeView(self):
        self.zoomsInitialized=False
        self.onSelection()
    def onShowGrids(self):
        _SetPreference('Appearance.GridsOnPlots',self.showGridsAction.isChecked())
        self.onSelection()
    def onLogScale(self):
        _SetPreference('SParameterProperties.Plot.LogScale',self.logScaleAction.isChecked())
        self.onSelection()
    def onAutoscale(self):
        self.plt.autoscale(True)
        self.panel.canvas.draw()
    def _TrackLimits(self):
        def onX(ax):
            self.minx,self.maxx=ax.get_xlim()
        def onY(ax):
            self.miny,self.maxy=ax.get_ylim()
        self.limitCallbacks=[self.plt.callbacks.connect('xlim_changed',onX),
                             self.plt.callbacks.connect('ylim_changed',onY)]
    def _Begin(self,label):
        for cid in getattr(self,'limitCallbacks',[]):
            self.plt.callbacks.disconnect(cid)
        self.limitCallbacks=[]
        self.plt.cla()
        self.panel.label.setText(label)
        if not _Preference('Appearance.PlotCursorValues',True):
            self.plt.format_coord=lambda x,y: ''
        self.plt.autoscale(False)
    def _Finish(self,minv,maxv):
        if not self.zoomsInitialized:
            self.miny,self.maxy=minv,maxv
        if self.miny is not None:
            self.plt.set_ylim(bottom=self.miny)
        if self.maxy is not None:
            self.plt.set_ylim(top=self.maxy)
        if self.showGridsAction.isChecked():
            self.plt.grid(True,'both')
        self.zoomsInitialized=True
        self.panel.canvas.draw()
        self._TrackLimits()
    def PlotTimeDomain(self):
        self._Begin('Time-domain View')
        self.plt.set_ylabel('amplitude',fontsize=10)
        indices=self.SelectedIndices()
        colors=_Colors()
        limits=self.result.AutoscaleLimits('time',indices)
        timeLabel,divisor='s',1.
        if limits[0] is not None and limits[1] is not None:
            timeLabel=ToSI(limits[1]-limits[0],'s')[-2:]
            divisor=FromSI('1. '+timeLabel,'s')
        self.timeLabelDivisor=divisor
        if not self.zoomsInitialized:
            self.minx=None if limits[0] is None else limits[0]/divisor
            self.maxx=None if limits[1] is None else limits[1]/divisor
        if self.minx is not None:
            self.plt.set_xlim(left=self.minx)
        if self.maxx is not None:
            self.plt.set_xlim(right=self.maxx)
        for i in indices:
            name,wf=self.result.waveforms[i]
            color=colors[i%len(colors)]
            if self.result.IsDC(wf):
                self.plt.axhline(wf,label=name,c=color)
            else:
                x,y=self.result.Arrays(i,'time')
                self.plt.plot(x/divisor,y,label=name,c=color)
        self.plt.set_xlabel('time ('+timeLabel+')',fontsize=10)
        if indices:
            self.plt.legend(loc='upper right',labelspacing=0.1)
        self._Finish(limits[2],limits[3])
    def PlotFrequencyContent(self,density):
        self._Begin('Spectral Density' if density else 'Spectral Content')
        indices=[i for i in self.SelectedIndices() if not self.result.IsDC(self.result.waveforms[i][1])]
        view='density' if density else 'content'
        colors=_Colors()
        limits=self.result.AutoscaleLimits(view,indices)
        freqLabel,divisor='Hz',1.
        if limits[0] is not None and limits[1] is not None:
            freqLabel=ToSI(limits[1]-limits[0],'Hz')[-3:]
            divisor=FromSI('1. '+freqLabel,'Hz')
        if not self.zoomsInitialized:
            self.minx=None if limits[0] is None else limits[0]/divisor
            self.maxx=None if limits[1] is None else limits[1]/divisor
        log=self.logScaleAction.isChecked()
        if log and self.minx is not None and self.minx<=0.:
            for i in indices:
                x,_=self.result.Arrays(i,view)
                positive=x[x>0.]
                if len(positive):
                    self.minx=positive[0]/divisor
                    break
        if self.minx is not None:
            self.plt.set_xlim(left=self.minx)
        if self.maxx is not None:
            self.plt.set_xlim(right=self.maxx)
        adder=0.
        if density:
            import math
            adder=10.*math.log10(divisor)
            self.plt.set_ylabel('magnitude (dBm/'+freqLabel+')',fontsize=10)
        else:
            self.plt.set_ylabel('magnitude (dBm)',fontsize=10)
        for i in indices:
            name=self.result.waveforms[i][0]
            x,y=self.result.Arrays(i,view)
            (self.plt.semilogx if log else self.plt.plot)(x/divisor,y+adder,label=name,c=colors[i%len(colors)])
        self.plt.set_xlabel('frequency ('+freqLabel+')',fontsize=10)
        if indices:
            self.plt.legend(loc='upper right',labelspacing=0.1)
        self._Finish(None if limits[2] is None else limits[2]+adder,None if limits[3] is None else limits[3]+adder)
    def onWriteSimulatorToFile(self):
        if self.result is None:
            return
        directory=os.getcwd()
        for i in self.SelectedIndices():
            name,wf=self.result.waveforms[i]
            if self.result.IsDC(wf):
                continue
            filename,_=QFileDialog.getSaveFileName(self,'Save Waveform '+name,os.path.join(directory,name+'.txt'),
                'waveform (*.txt);;LeCroy (*.trc);;time/value (*.csv)')
            if not filename:
                continue
            try:
                wf.WriteToFile(filename)
            except Exception as e:
                QMessageBox.critical(self,'Save Waveforms',str(e))

class SParametersWindow(QMainWindow):
    """magnitude and phase of s-parameters with the same pan/zoom/autoscale behaviour"""
    def __init__(self,result,title='S-parameters',parent=None):
        super().__init__(parent)
        from PySide6.QtWidgets import QTabWidget
        self.setWindowTitle(title)
        self.resize(1000,650)
        self.panels=[]
        tabs=QTabWidget()
        self.setCentralWidget(tabs)
        log=_Preference('SParameterProperties.Plot.LogScale',False)
        for name,sp in result.sparameters:
            f=list(sp.f())
            freqLabel=ToSI(f[-1]-f[0],'Hz')[-3:] if len(f)>1 else 'Hz'
            divisor=FromSI('1. '+freqLabel,'Hz') if len(f)>1 else 1.
            colors=_Colors()
            for quantity,ylabel in (('dB','magnitude (dB)'),('deg','phase (degrees)')):
                panel=PlotPanel()
                panel.label.setText(name+(' magnitude' if quantity=='dB' else ' phase'))
                plt=panel.axes
                k=0
                for o in range(1,sp.m_P+1):
                    for i in range(1,sp.m_P+1):
                        fr=sp.FrequencyResponse(o,i)
                        x=[v/divisor for v in fr.Frequencies()]
                        (plt.semilogx if log and x and x[0]>0 else plt.plot)(x,fr.Values(quantity),
                            label='S'+str(o)+str(i),c=colors[k%len(colors)])
                        k+=1
                plt.set_xlabel('frequency ('+freqLabel+')',fontsize=10)
                plt.set_ylabel(ylabel,fontsize=10)
                if _Preference('Appearance.GridsOnPlots',True):
                    plt.grid(True,'both')
                if sp.m_P<=4:
                    plt.legend(loc='upper right',labelspacing=0.1)
                panel.autoscaleButton.clicked.connect(lambda checked=False,p=panel: (p.axes.autoscale(True),p.canvas.draw()))
                self.panels.append(panel)
                tabs.addTab(panel,panel.label.text())

class EyeDiagramWindow(QMainWindow):
    """shows the eye diagram image computed by the headless engine"""
    def __init__(self,name,image,parent=None):
        super().__init__(parent)
        import io
        from PySide6.QtGui import QPixmap
        from PySide6.QtWidgets import QScrollArea
        self.setWindowTitle('Eye Diagram: '+name)
        buffer=io.BytesIO()
        image.save(buffer,format='PNG')
        pixmap=QPixmap()
        pixmap.loadFromData(buffer.getvalue(),'PNG')
        label=QLabel()
        label.setPixmap(pixmap)
        scroll=QScrollArea()
        scroll.setWidget(label)
        self.setCentralWidget(scroll)
        self.resize(min(pixmap.width()+40,1200),min(pixmap.height()+60,900))
