"""
SchematicView.py
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
import math

from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPath, QPolygonF, QFont, QPainter
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene

TEXT_FONT=QFont('Helvetica')
TEXT_FONT.setPixelSize(11)

def _color(name):
    color=QColor(name) if name else QColor()
    return color if color.isValid() else QColor('black')

def _arrowhead(tip,tail,shape):
    """tk.Canvas arrowshape (d1,d2,d3): d1 tip-to-neck, d2 tip-to-trailing points, d3 half width"""
    d1,d2,d3=shape
    dx,dy=tip[0]-tail[0],tip[1]-tail[1]
    length=math.hypot(dx,dy) or 1.
    ux,uy=dx/length,dy/length
    px,py=-uy,ux
    return QPolygonF([QPointF(*tip),
                      QPointF(tip[0]-ux*d2+px*d3,tip[1]-uy*d2+py*d3),
                      QPointF(tip[0]-ux*d1,tip[1]-uy*d1),
                      QPointF(tip[0]-ux*d2-px*d3,tip[1]-uy*d2-py*d3)])

def AddPrimitives(scene,items):
    """adds RecordingCanvas primitives to a QGraphicsScene"""
    for item in items:
        kind=item['type']
        if kind=='line':
            pts=item['points']
            pen=QPen(_color(item['color']),item.get('width',1.))
            pen.setCapStyle(Qt.RoundCap)
            if 'dash' in item:
                pen.setDashPattern(item['dash'])
            path=QPainterPath(QPointF(pts[0],pts[1]))
            for k in range(2,len(pts)-1,2):
                path.lineTo(pts[k],pts[k+1])
            scene.addPath(path,pen)
            arrow=item.get('arrow')
            if arrow and len(pts)>=4:
                shape=item.get('arrowshape',[8.,10.,3.])
                brush=QBrush(_color(item['color']))
                if arrow in ('last','both'):
                    scene.addPolygon(_arrowhead(pts[-2:],pts[-4:-2],shape),QPen(Qt.NoPen),brush)
                if arrow in ('first','both'):
                    scene.addPolygon(_arrowhead(pts[0:2],pts[2:4],shape),QPen(Qt.NoPen),brush)
        elif kind=='polygon':
            pts=item['points']
            polygon=QPolygonF([QPointF(pts[k],pts[k+1]) for k in range(0,len(pts)-1,2)])
            pen=QPen(_color(item['outline'])) if item.get('outline') else QPen(Qt.NoPen)
            brush=QBrush(_color(item['fill'])) if item.get('fill') else QBrush()
            scene.addPolygon(polygon,pen,brush)
        elif kind in ('rectangle','oval'):
            x0,y0,x1,y1=item['bbox']
            rect=QRectF(QPointF(min(x0,x1),min(y0,y1)),QPointF(max(x0,x1),max(y0,y1)))
            pen=QPen(_color(item['outline'])) if item.get('outline') else QPen(Qt.NoPen)
            brush=QBrush(_color(item['fill'])) if item.get('fill') else QBrush()
            if kind=='rectangle':
                scene.addRect(rect,pen,brush)
            else:
                scene.addEllipse(rect,pen,brush)
        elif kind=='arc':
            x0,y0,x1,y1=item['bbox']
            rect=QRectF(QPointF(min(x0,x1),min(y0,y1)),QPointF(max(x0,x1),max(y0,y1)))
            path=QPainterPath()
            path.arcMoveTo(rect,item['start'])
            path.arcTo(rect,item['start'],item['extent'])
            scene.addPath(path,QPen(_color(item['outline'])))
        elif kind=='text':
            textItem=scene.addSimpleText(item['text'],TEXT_FONT)
            textItem.setBrush(QBrush(_color(item['color'])))
            r=textItem.boundingRect()
            anchor=item.get('anchor') or 'center'
            x=item['x']-(0. if 'w' in anchor else r.width() if 'e' in anchor else r.width()/2.)
            y=item['y']-(0. if 'n' in anchor else r.height() if 's' in anchor else r.height()/2.)
            textItem.setPos(x,y)

class SchematicView(QGraphicsView):
    """read/select/move view of a schematic rendered from GuiCore primitives"""
    deviceClicked=Signal(object)
    deviceDoubleClicked=Signal(int)
    deviceDragged=Signal(int,int,int)
    deviceContextMenu=Signal(int,object,bool)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        self.setBackgroundBrush(QBrush(QColor('white')))
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.devices=[]
        self.grid=16
        self._press=None
        self._pressDevice=None
    def SetDrawing(self,drawing,fit=False):
        scene=self.scene()
        scene.clear()
        AddPrimitives(scene,drawing['items'])
        self.devices=drawing['devices']
        self.grid=drawing['grid']
        bbox=drawing['bbox']
        if bbox is not None:
            margin=2*self.grid
            scene.setSceneRect(QRectF(bbox[0]-margin,bbox[1]-margin,bbox[2]-bbox[0]+2*margin,bbox[3]-bbox[1]+2*margin))
        if fit:
            self.ZoomFit()
    def ZoomFit(self):
        if not self.scene().sceneRect().isEmpty():
            self.fitInView(self.scene().sceneRect(),Qt.KeepAspectRatio)
    def Zoom(self,factor):
        self.scale(factor,factor)
    def DeviceAt(self,scenePoint):
        for device in reversed(self.devices):
            x0,y0,x1,y1=device['bbox']
            tolerance=0.1*self.grid
            if min(x0,x1)-tolerance<=scenePoint.x()<=max(x0,x1)+tolerance and min(y0,y1)-tolerance<=scenePoint.y()<=max(y0,y1)+tolerance:
                return device['index']
        return None
    def wheelEvent(self,event):
        self.Zoom(1.15 if event.angleDelta().y()>0 else 1/1.15)
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            point=self.mapToScene(event.position().toPoint())
            self._pressDevice=self.DeviceAt(point)
            self._press=point
            self.deviceClicked.emit(self._pressDevice)
            if self._pressDevice is not None:
                return
        super().mousePressEvent(event)
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.LeftButton and self._pressDevice is not None and self._press is not None:
            point=self.mapToScene(event.position().toPoint())
            dx=round((point.x()-self._press.x())/self.grid)
            dy=round((point.y()-self._press.y())/self.grid)
            if dx or dy:
                self.deviceDragged.emit(self._pressDevice,dx,dy)
            self._press=None; self._pressDevice=None
            return
        super().mouseReleaseEvent(event)
    def mouseDoubleClickEvent(self,event):
        index=self.DeviceAt(self.mapToScene(event.position().toPoint()))
        if index is not None:
            self.deviceDoubleClicked.emit(index)
            return
        super().mouseDoubleClickEvent(event)
    def contextMenuEvent(self,event):
        index=self.DeviceAt(self.mapToScene(event.pos()))
        if index is None:
            return super().contextMenuEvent(event)
        self.deviceContextMenu.emit(index,event.globalPos(),bool(event.modifiers() & Qt.ControlModifier))
