"""
Docking.py
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

# VS Code style panes for the Qt GUI, matching the web GUI's dock.js: panes live in the primary
# (left) or secondary (right) side bar or the bottom panel of the main window, or in pane windows
# torn off from it. Drag a pane's header to move it (a highlight shows where it lands; drop it
# outside every window to tear it off into a new window, which accepts other panes), click the
# header to collapse it, and right-click the header to move it or reset the layout.
import json
import os

from PySide6.QtCore import Qt, QPoint, QRect, QSize, QTimer, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QWidget, QFrame, QLabel, QHBoxLayout, QVBoxLayout, QSplitter, QMenu, QRubberBand,
    QApplication)

AREAS=('left','right','bottom')
AREA_NAMES={'left':'Primary Side Bar','right':'Secondary Side Bar','bottom':'Panel'}
DRAG_THRESHOLD=6
WINDOW_SIZE=(320,420)

class PaneHeader(QFrame):
    """the clickable, draggable title bar of a pane"""
    def __init__(self,pane):
        super().__init__(pane)
        self.pane=pane
        self.setObjectName('paneHeader')
        self.setCursor(Qt.OpenHandCursor)
        self.setToolTip('Click to collapse or expand; drag to move or tear off; right-click for more')
        layout=QHBoxLayout(self)
        layout.setContentsMargins(6,3,6,3)
        self.chevron=QLabel('\u25BE')
        self.title=QLabel()
        font=self.title.font(); font.setBold(True); self.title.setFont(font)
        layout.addWidget(self.chevron)
        layout.addWidget(self.title,1)
        self._press=None
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            self._press=event.globalPosition().toPoint()
        event.accept()
    def mouseMoveEvent(self,event):
        if self._press is None:
            return
        if not self.pane.manager.dragging and (event.globalPosition().toPoint()-self._press).manhattanLength()>=DRAG_THRESHOLD:
            self.pane.manager.BeginDrag(self.pane)
        if self.pane.manager.dragging:
            self.pane.manager.DragTo(event.globalPosition().toPoint())
    def mouseReleaseEvent(self,event):
        if event.button()!=Qt.LeftButton or self._press is None:
            return
        self._press=None
        if self.pane.manager.dragging:
            self.pane.manager.EndDrag(event.globalPosition().toPoint())
        else:
            self.pane.manager.ToggleCollapsed(self.pane)
    def contextMenuEvent(self,event):
        self.pane.manager.ShowPaneMenu(self.pane,event.globalPos())

class Pane(QFrame):
    """a movable pane with the parts of the QDockWidget API the main window uses"""
    def __init__(self,title,parent=None):
        super().__init__(parent)
        self.manager=None
        self.collapsed=False
        self.header=PaneHeader(self)
        self._content=None
        self._layout=QVBoxLayout(self)
        self._layout.setContentsMargins(0,0,0,0)
        self._layout.setSpacing(0)
        self._layout.addWidget(self.header)
        self._toggle=QAction(title,self)
        self._toggle.setCheckable(True)
        self._toggle.setChecked(True)
        self._toggle.toggled.connect(lambda shown: self.manager and self.manager.SetPaneShown(self,shown))
        self.setWindowTitle(title)
    def setWindowTitle(self,title):
        super().setWindowTitle(title)
        self.header.title.setText(title)
        self._toggle.setText(title)
    def setWidget(self,widget):
        if self._content is not None:
            self._layout.removeWidget(self._content)
        self._content=widget
        self._layout.addWidget(widget,1)
    def widget(self):
        return self._content
    def toggleViewAction(self):
        return self._toggle
    def raise_(self):
        """shows the pane, expanded, in front"""
        if self.manager is not None:
            self.manager.Reveal(self)
        else:
            super().raise_()
    def SetCollapsed(self,collapsed):
        self.collapsed=collapsed
        if self._content is not None:
            self._content.setVisible(not collapsed)
        self.header.chevron.setText('\u25B8' if collapsed else '\u25BE')
        self.setMaximumHeight(self.header.sizeHint().height() if collapsed else 16777215)

class PaneArea(QSplitter):
    """a side bar, the bottom panel or the inside of a pane window: a splitter of panes"""
    def __init__(self,name,orientation,parent=None):
        super().__init__(orientation,parent)
        self.name=name
        self.setChildrenCollapsible(False)
        self.setHandleWidth(4)
    def Panes(self):
        return [self.widget(i) for i in range(self.count()) if isinstance(self.widget(i),Pane)]
    def VisiblePanes(self):
        return [p for p in self.Panes() if not p.isHidden()]

class PaneWindow(QWidget):
    """a torn-off window holding panes; other panes can be dropped into it"""
    closed=Signal(object)
    def __init__(self,manager,parent):
        super().__init__(parent,Qt.Tool)
        self.manager=manager
        self.setWindowTitle('SignalIntegrity')
        self.area=PaneArea('window',Qt.Vertical,self)
        layout=QVBoxLayout(self)
        layout.setContentsMargins(2,2,2,2)
        layout.addWidget(self.area)
        self.resize(*WINDOW_SIZE)
    def closeEvent(self,event):
        self.manager.WindowClosing(self)
        super().closeEvent(event)

class DockManager(object):
    """owns the panes, the three main-window areas and the torn-off pane windows"""
    def __init__(self,mainWindow,centralWidget,settingsFile):
        self.main=mainWindow
        self.settingsFile=settingsFile
        self.panes={}
        self.windows=[]
        self.dragging=None
        self.target=None
        self.default=None
        self.areas={'left':PaneArea('left',Qt.Vertical),'right':PaneArea('right',Qt.Vertical),
                    'bottom':PaneArea('bottom',Qt.Horizontal)}
        self.center=QSplitter(Qt.Vertical)
        self.center.addWidget(centralWidget)
        self.center.addWidget(self.areas['bottom'])
        self.center.setStretchFactor(0,1)
        self.outer=QSplitter(Qt.Horizontal)
        self.outer.addWidget(self.areas['left'])
        self.outer.addWidget(self.center)
        self.outer.addWidget(self.areas['right'])
        self.outer.setStretchFactor(1,1)
        for splitter in (self.center,self.outer):
            splitter.setChildrenCollapsible(False)
        self.schematic=centralWidget
        self.band=QRubberBand(QRubberBand.Rectangle)
        self.band.setWindowFlags(self.band.windowFlags()|Qt.WindowTransparentForInput|Qt.ToolTip)
        self.saveTimer=QTimer()
        self.saveTimer.setSingleShot(True)
        self.saveTimer.setInterval(300)
        self.saveTimer.timeout.connect(self.Save)
    def Widget(self):
        return self.outer
    # ---- building
    def AddPane(self,paneId,pane,area):
        pane.manager=self
        pane.setObjectName(paneId)
        self.panes[paneId]=pane
        self.areas[area].addWidget(pane)
    def Finish(self,sizes):
        """records the starting arrangement as the default and restores a saved one, if any"""
        self.defaultSizes=sizes
        self.default=self.Layout()
        self._ApplySizes(sizes)
        self._UpdateAreas()
        saved=self.Load()
        if saved is not None:
            self.Apply(saved)
    def _ApplySizes(self,sizes):
        self.outer.setSizes([sizes['left'],max(400,self.main.width()-sizes['left']-sizes['right']),sizes['right']])
        self.center.setSizes([max(200,self.main.height()-sizes['bottom']),sizes['bottom']])
    # ---- queries
    def Containers(self):
        return [self.areas[a] for a in AREAS]+[w.area for w in self.windows]
    def AreaOf(self,pane):
        parent=pane.parentWidget()
        return parent if isinstance(parent,PaneArea) else None
    def _UpdateAreas(self):
        for area in self.areas.values():
            area.setVisible(bool(area.VisiblePanes()))
        for window in list(self.windows):
            if not window.area.Panes():
                self._DropWindow(window)
            elif not window.area.VisiblePanes():
                window.hide()
    def _Changed(self):
        self._UpdateAreas()
        self.saveTimer.start()
    # ---- moving
    def MovePane(self,pane,container,index=None):
        """moves a pane into an area or window container at index (default: the end)"""
        source=self.AreaOf(pane)
        if source is container and index is not None and container.indexOf(pane)<index:
            index-=1
        count=len(container.Panes())
        index=count if index is None else max(0,min(index,count))
        container.insertWidget(index,pane)
        pane.show()
        pane.toggleViewAction().setChecked(True)
        if container.name=='bottom' and pane.collapsed:
            pane.SetCollapsed(False)
        self._Changed()
        window=container.window()
        if window is not self.main:
            window.show()
    def TearOff(self,pane,globalPos=None):
        """moves a pane into a new window at globalPos (default: next to the pane)"""
        window=PaneWindow(self,self.main)
        self.windows.append(window)
        if globalPos is None:
            globalPos=pane.mapToGlobal(QPoint(40,20))
        window.move(globalPos-QPoint(20,12))
        window.resize(max(WINDOW_SIZE[0],pane.width()),max(WINDOW_SIZE[1],pane.height()))
        self.MovePane(pane,window.area)
        window.show()
        window.raise_()
        return window
    def WindowClosing(self,window):
        """panes of a closed window go back to the side bar they started in"""
        if window not in self.windows:
            return
        self.windows.remove(window)
        home=self._HomeAreas()
        for pane in window.area.Panes():
            self.areas[home.get(pane.objectName(),'left')].addWidget(pane)
        self._Changed()
    def _DropWindow(self,window):
        if window in self.windows:
            self.windows.remove(window)
        window.hide()
        window.deleteLater()
    def _HomeAreas(self):
        return {paneId:area for area in AREAS for paneId in self.default['areas'][area]}
    def SetPaneShown(self,pane,shown):
        pane.setVisible(shown)
        if shown:
            window=pane.window()
            if window is not self.main:
                window.show()
        self._Changed()
    def ToggleCollapsed(self,pane):
        area=self.AreaOf(pane)
        if area is None or area.orientation()==Qt.Horizontal:
            return
        pane.SetCollapsed(not pane.collapsed)
        self._Changed()
    def Reveal(self,pane):
        if pane.isHidden():
            pane.toggleViewAction().setChecked(True)
        if pane.collapsed:
            pane.SetCollapsed(False)
            self._Changed()
        window=pane.window()
        window.show()
        if window is not self.main:
            window.raise_()
    def ResetLayout(self):
        for window in list(self.windows):
            self.windows.remove(window)
            for pane in window.area.Panes():
                self.areas['left'].addWidget(pane)
            window.hide()
            window.deleteLater()
        self.Apply(self.default)
        self._ApplySizes(self.defaultSizes)
        self._Changed()
    # ---- dragging a pane by its header
    def BeginDrag(self,pane):
        self.dragging=pane
        QApplication.setOverrideCursor(Qt.ClosedHandCursor)
    def DragTo(self,globalPos):
        self.target=self.DropTarget(globalPos)
        if self.target is None:
            self.band.hide()
            return
        self.band.setGeometry(self.target['rect'])
        self.band.show()
        self.band.raise_()
    def EndDrag(self,globalPos):
        pane,self.dragging=self.dragging,None
        self.band.hide()
        QApplication.restoreOverrideCursor()
        target=self.DropTarget(globalPos)
        self.target=None
        if pane is None or target is None:
            return
        if target['kind']=='window':
            self.TearOff(pane,globalPos)
        else:
            self.MovePane(pane,target['container'],target['index'])
    def _GlobalRect(self,widget):
        return QRect(widget.mapToGlobal(QPoint(0,0)),widget.size())
    def DropTarget(self,globalPos):
        """{'kind','container','index','rect'} for a pane dropped at globalPos (global screen pixels),
        or None where it can't go"""
        dragged=self.dragging
        for container in [w.area for w in self.windows if w.isVisible()]+[self.areas[a] for a in AREAS]:
            if not container.isVisible() or not self._GlobalRect(container).contains(globalPos):
                continue
            panes=container.VisiblePanes()
            for pane in panes:
                rect=self._GlobalRect(pane)
                if pane is dragged or not rect.contains(globalPos):
                    continue
                horizontal=container.orientation()==Qt.Horizontal
                after=globalPos.x()>rect.center().x() if horizontal else globalPos.y()>rect.center().y()
                if horizontal:
                    half=QRect(rect.left()+(rect.width()//2 if after else 0),rect.top(),rect.width()//2,rect.height())
                else:
                    half=QRect(rect.left(),rect.top()+(rect.height()//2 if after else 0),rect.width(),rect.height()//2)
                return {'kind':'area','container':container,'index':container.indexOf(pane)+(1 if after else 0),'rect':half}
            return {'kind':'area','container':container,'index':None,'rect':self._GlobalRect(container)}
        # over the schematic: the nearest edge docks to that side, as dragging a view to an editor edge does
        rect=self._GlobalRect(self.schematic)
        if rect.contains(globalPos):
            edges={'left':(globalPos.x()-rect.left())/rect.width(),'right':(rect.right()-globalPos.x())/rect.width(),
                   'bottom':(rect.bottom()-globalPos.y())/rect.height()}
            area=min(edges,key=edges.get)
            if edges[area]>0.3:
                return None
            width=min(300,rect.width()//2); height=min(220,rect.height()//2)
            highlight={'left':QRect(rect.left(),rect.top(),width,rect.height()),
                       'right':QRect(rect.right()-width,rect.top(),width,rect.height()),
                       'bottom':QRect(rect.left(),rect.bottom()-height,rect.width(),height)}[area]
            return {'kind':'area','container':self.areas[area],'index':None,'rect':highlight}
        if any(self._GlobalRect(w).contains(globalPos) for w in [self.main]+self.windows if w.isVisible()):
            return None
        # outside every window: tear off into a new window here
        return {'kind':'window','container':None,'index':None,'rect':QRect(globalPos-QPoint(20,12),QSize(*WINDOW_SIZE))}
    # ---- header context menu
    def ShowPaneMenu(self,pane,globalPos):
        menu=self.PaneMenu(pane)
        menu.exec(globalPos)
    def PaneMenu(self,pane):
        menu=QMenu(self.main)
        area=self.AreaOf(pane)
        if area is not None and area.orientation()==Qt.Vertical:
            menu.addAction('Expand' if pane.collapsed else 'Collapse',lambda: self.ToggleCollapsed(pane))
        for name in AREAS:
            if area is not self.areas[name]:
                menu.addAction('Move to '+AREA_NAMES[name],lambda n=name: self.MovePane(pane,self.areas[n]))
        menu.addAction('Move to New Window',lambda: self.TearOff(pane))
        for number,window in enumerate(self.windows,1):
            if area is not window.area:
                menu.addAction('Move to Window %d'%number,lambda w=window: self.MovePane(pane,w.area))
        menu.addSeparator()
        menu.addAction('Hide',lambda: pane.toggleViewAction().setChecked(False))
        menu.addAction('Reset Layout',self.ResetLayout)
        return menu
    # ---- the remembered layout
    def Layout(self):
        """the arrangement as plain data: panes per area, pane windows, splitter sizes, collapsed and hidden panes"""
        def geometry(window):
            g=window.geometry()
            return [g.x(),g.y(),g.width(),g.height()]
        return {'areas':{a:[p.objectName() for p in self.areas[a].Panes()] for a in AREAS},
                'areaSizes':{a:self.areas[a].sizes() for a in AREAS},
                'outer':self.outer.sizes(),'center':self.center.sizes(),
                'windows':[{'panes':[p.objectName() for p in w.area.Panes()],'geometry':geometry(w),'sizes':w.area.sizes()}
                           for w in self.windows],
                'collapsed':sorted(i for i,p in self.panes.items() if p.collapsed),
                'hidden':sorted(i for i,p in self.panes.items() if not p.toggleViewAction().isChecked())}
    def Apply(self,layout):
        """rebuilds the arrangement from Layout() data; ignored unless it places every pane exactly once"""
        try:
            placed=[i for a in AREAS for i in layout['areas'][a]]+[i for w in layout.get('windows',[]) for i in w['panes']]
            if sorted(placed)!=sorted(self.panes):
                return False
            for a in AREAS:
                for paneId in layout['areas'][a]:
                    self.areas[a].addWidget(self.panes[paneId])
            for spec in layout.get('windows',[]):
                window=PaneWindow(self,self.main)
                self.windows.append(window)
                for paneId in spec['panes']:
                    window.area.addWidget(self.panes[paneId])
                x,y,w,h=[int(v) for v in spec['geometry']]
                window.setGeometry(x,y,max(160,w),max(120,h))
                if spec.get('sizes'):
                    window.area.setSizes([int(s) for s in spec['sizes']])
            for paneId,pane in self.panes.items():
                pane.SetCollapsed(paneId in layout.get('collapsed',[]) and self.AreaOf(pane).orientation()==Qt.Vertical)
                shown=paneId not in layout.get('hidden',[])
                pane.toggleViewAction().blockSignals(True)
                pane.toggleViewAction().setChecked(shown)
                pane.toggleViewAction().blockSignals(False)
                pane.setVisible(shown)
            for a in AREAS:
                if layout.get('areaSizes',{}).get(a):
                    self.areas[a].setSizes([int(s) for s in layout['areaSizes'][a]])
            if layout.get('outer'):
                self.outer.setSizes([int(s) for s in layout['outer']])
            if layout.get('center'):
                self.center.setSizes([int(s) for s in layout['center']])
            self._UpdateAreas()
            return True
        except (KeyError,TypeError,ValueError,AttributeError):
            return False
    def ShowWindows(self):
        for window in self.windows:
            if window.area.VisiblePanes():
                window.show()
    def Load(self):
        try:
            with open(self.settingsFile) as f:
                layout=json.load(f)
            return layout if isinstance(layout,dict) else None
        except (OSError,ValueError):
            return None
    def Save(self):
        try:
            os.makedirs(os.path.dirname(self.settingsFile),exist_ok=True)
            with open(self.settingsFile,'w') as f:
                json.dump(self.Layout(),f)
        except OSError:
            pass
