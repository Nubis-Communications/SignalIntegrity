"""
PartsDock.py
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
from PySide6.QtCore import Qt, QMimeData, QRectF, QSize, Signal
from PySide6.QtGui import QPixmap, QPainter, QIcon, QColor, QDrag
from PySide6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QGraphicsScene, QAbstractItemView, QLabel)

from SignalIntegrity.QtApp.SchematicView import AddPrimitives, PART_MIME

ICON_SIZE=QSize(56,40)

def PreviewPixmap(preview,colorMap,size=ICON_SIZE):
    """renders a part picture's geometry (without its unreadably small labels) into a transparent pixmap"""
    pixmap=QPixmap(size*2)
    pixmap.setDevicePixelRatio(2)
    pixmap.fill(Qt.transparent)
    items=[item for item in preview['items'] if item['type']!='text']
    if not items:
        return pixmap
    from SignalIntegrity.GuiCore.RecordingCanvas import RecordingCanvas
    canvas=RecordingCanvas(); canvas.items=items
    x0,y0,x1,y1=canvas.BoundingBox()
    scene=QGraphicsScene()
    AddPrimitives(scene,items,colorMap)
    painter=QPainter(pixmap)
    painter.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
    scene.render(painter,QRectF(2,2,size.width()-4,size.height()-4),QRectF(x0-2,y0-2,x1-x0+4,y1-y0+4),Qt.KeepAspectRatio)
    painter.end()
    return pixmap

class PartTree(QTreeWidget):
    """category tree whose part items can be dragged onto the schematic"""
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setIconSize(ICON_SIZE)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragOnly)
        self.setAnimated(True)
        self.setIndentation(12)
        self.setUniformRowHeights(False)
    def mimeData(self,items):
        data=QMimeData()
        index=items[0].data(0,Qt.UserRole) if items else None
        if index is not None:
            data.setData(PART_MIME,str(index).encode())
        return data
    def startDrag(self,actions):
        item=self.currentItem()
        if item is None or item.data(0,Qt.UserRole) is None:
            return
        drag=QDrag(self)
        drag.setMimeData(self.mimeData([item]))
        drag.setPixmap(item.icon(0).pixmap(ICON_SIZE))
        drag.exec(Qt.CopyAction)

class PartsDock(QDockWidget):
    """a stencil of every part in the tk Add Part catalog, grouped by function"""
    placeRequested=Signal(int)
    def __init__(self,parent=None):
        super().__init__('Parts',parent)
        self.setObjectName('parts')
        widget=QWidget()
        layout=QVBoxLayout(widget)
        layout.setContentsMargins(4,4,4,4)
        self.search=QLineEdit()
        self.search.setPlaceholderText('Search parts...')
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.Filter)
        layout.addWidget(self.search)
        self.tree=PartTree()
        self.tree.itemDoubleClicked.connect(self._Activated)
        self.tree.itemActivated.connect(self._Activated)
        layout.addWidget(self.tree,1)
        hint=QLabel('Drag a part onto the schematic, or double-click it and click where it goes.')
        hint.setWordWrap(True)
        hint.setEnabled(False)
        layout.addWidget(hint)
        self.setWidget(widget)
        self.catalog=[]
    def Populate(self,catalog,colorMap):
        """fills the tree from ProjectSession.PartCatalog(previews=True)"""
        self.catalog=catalog
        expanded={self.tree.topLevelItem(i).text(0) for i in range(self.tree.topLevelItemCount()) if self.tree.topLevelItem(i).isExpanded()}
        self.tree.clear()
        categories={}
        for part in catalog:
            icon=QIcon(PreviewPixmap(part['preview'],colorMap))
            for category in part['categories'] or ['Miscellaneous']:
                if category not in categories:
                    top=QTreeWidgetItem([category])
                    top.setFlags(Qt.ItemIsEnabled)
                    font=top.font(0); font.setBold(True); top.setFont(0,font)
                    self.tree.addTopLevelItem(top)
                    categories[category]=top
                    top.setExpanded(category in expanded)
                item=QTreeWidgetItem([part['description'] or part['partname']])
                item.setIcon(0,icon)
                item.setToolTip(0,part['partname']+'\n'+part['description'])
                item.setData(0,Qt.UserRole,part['index'])
                item.setData(0,Qt.UserRole+1,(part['partname']+' '+part['description']+' '+' '.join(part['categories'])).lower())
                item.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsDragEnabled)
                categories[category].addChild(item)
        self.Filter(self.search.text())
    def Filter(self,text):
        words=text.lower().split()
        for i in range(self.tree.topLevelItemCount()):
            top=self.tree.topLevelItem(i)
            visible=0
            for k in range(top.childCount()):
                child=top.child(k)
                show=all(w in child.data(0,Qt.UserRole+1) for w in words)
                child.setHidden(not show)
                visible+=show
            top.setHidden(visible==0)
            if words:
                top.setExpanded(visible>0)
    def _Activated(self,item,column=0):
        index=item.data(0,Qt.UserRole)
        if index is not None:
            self.placeRequested.emit(index)
