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
PART_MIME='application/x-signalintegrity-part'

def _color(name,colorMap=None):
    if colorMap and name:
        name=colorMap.get(str(name).lower(),name)
    color=QColor(name) if name else QColor()
    return color if color.isValid() else QColor(colorMap.get('black','black') if colorMap else 'black')

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

def AddPrimitives(scene,items,colorMap=None):
    """adds RecordingCanvas primitives to a QGraphicsScene, optionally recoloring tk color names"""
    _c=lambda name: _color(name,colorMap)
    for item in items:
        kind=item['type']
        if kind=='line':
            pts=item['points']
            pen=QPen(_c(item['color']),item.get('width',1.))
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
                brush=QBrush(_c(item['color']))
                if arrow in ('last','both'):
                    scene.addPolygon(_arrowhead(pts[-2:],pts[-4:-2],shape),QPen(Qt.NoPen),brush)
                if arrow in ('first','both'):
                    scene.addPolygon(_arrowhead(pts[0:2],pts[2:4],shape),QPen(Qt.NoPen),brush)
        elif kind=='polygon':
            pts=item['points']
            polygon=QPolygonF([QPointF(pts[k],pts[k+1]) for k in range(0,len(pts)-1,2)])
            pen=QPen(_c(item['outline'])) if item.get('outline') else QPen(Qt.NoPen)
            brush=QBrush(_c(item['fill'])) if item.get('fill') else QBrush()
            scene.addPolygon(polygon,pen,brush)
        elif kind in ('rectangle','oval'):
            x0,y0,x1,y1=item['bbox']
            rect=QRectF(QPointF(min(x0,x1),min(y0,y1)),QPointF(max(x0,x1),max(y0,y1)))
            pen=QPen(_c(item['outline'])) if item.get('outline') else QPen(Qt.NoPen)
            brush=QBrush(_c(item['fill'])) if item.get('fill') else QBrush()
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
            scene.addPath(path,QPen(_c(item['outline'])))
        elif kind=='text':
            textItem=scene.addSimpleText(item['text'],TEXT_FONT)
            textItem.setBrush(QBrush(_c(item['color'])))
            r=textItem.boundingRect()
            # tk anchors are compass points; 'center' must not match the 'n' and 'e' tests
            anchor=item.get('anchor') or 'center'
            anchor='' if anchor=='center' else anchor
            x=item['x']-(0. if 'w' in anchor else r.width() if 'e' in anchor else r.width()/2.)
            y=item['y']-(0. if 'n' in anchor else r.height() if 's' in anchor else r.height()/2.)
            textItem.setPos(x,y)
            if item.get('role')=='property':
                # property text sits above its part, often across the wire leaving a top pin
                backing=scene.addRect(QRectF(x-1.,y-2.,r.width()+2.,r.height()+4.),QPen(Qt.NoPen),QBrush(_c('white')))
                backing.setZValue(1)
                textItem.setZValue(2)

class SchematicView(QGraphicsView):
    """schematic rendered from GuiCore primitives: left-drag on the background selects with a rubber
    band (Ctrl/Shift adds), left-drag on a part moves it or the whole selection, the middle button
    pans and the wheel zooms; it also accepts parts from the stencil and draws wires"""
    deviceClicked=Signal(object)
    deviceToggled=Signal(int)
    backgroundClicked=Signal(float,float)
    regionSelected=Signal(float,float,float,float,bool)
    deviceDoubleClicked=Signal(int)
    deviceDragged=Signal(int,int,int)
    selectionDragged=Signal(int,int)
    deviceContextMenu=Signal(int,object,bool)
    partDropped=Signal(int,float,float)
    deleteRequested=Signal()
    cancelRequested=Signal()
    wireFinished=Signal(list)
    vertexDragged=Signal(int,int,float,float)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        self.setBackgroundBrush(QBrush(QColor('white')))
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setAcceptDrops(True)
        self.viewport().setMouseTracking(True)
        self.devices=[]
        self.grid=16
        self.colorMap=None
        self.drawing=None
        self.fitRect=QRectF()
        self.placing=None
        self.wiring=False
        self.wirePoints=[]
        self.wireCursor=None
        self.wirePreview=None
        self._vertexDrag=None
        self._press=None
        self._pressDevice=None
        self._groupDrag=False
        self._ghosts=[]
        self._band=None
        self._pan=None
    def ApplyPalette(self,palette):
        from SignalIntegrity.GuiCore.Themes import SchematicColorMap
        self.colorMap=SchematicColorMap(palette)
        self.setBackgroundBrush(QBrush(QColor(palette['schematicBackground'])))
        if self.drawing is not None:
            self.SetDrawing(self.drawing)
    def SetDrawing(self,drawing,fit=False):
        self.drawing=drawing
        scene=self.scene()
        scene.clear()
        self.wirePreview=None
        self._ghosts=[]
        if self._band is not None:
            self._band['item']=None
        AddPrimitives(scene,drawing['items'],self.colorMap)
        self.devices=drawing['devices']
        self.grid=drawing['grid']
        bbox=drawing['bbox'] or [0,0,40*self.grid,30*self.grid]
        margin=2*self.grid
        self.fitRect=QRectF(bbox[0]-margin,bbox[1]-margin,bbox[2]-bbox[0]+2*margin,bbox[3]-bbox[1]+2*margin)
        # leave room around the drawing to drop new parts
        room=40*self.grid
        scene.setSceneRect(self.fitRect.adjusted(-room,-room,room,room))
        self._UpdateWirePreview()
        if fit:
            self.ZoomFit()
    def ZoomFit(self):
        if not self.fitRect.isEmpty():
            self.fitInView(self.fitRect,Qt.KeepAspectRatio)
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
    def SelectionSize(self):
        """number of selected parts plus selected wires in the last drawing"""
        if not self.drawing:
            return 0
        return sum(1 for d in self.devices if d['selected'])+sum(1 for w in self.drawing.get('wires',[]) if w['selected'])
    def _ScreenTolerance(self):
        return max(0.25*self.grid,5./max(self.transform().m11(),1e-6))
    def WireHit(self,point):
        """True if a wire passes within a few screen pixels of the scene point"""
        tolerance=self._ScreenTolerance()
        for wire in (self.drawing or {}).get('wires',[]):
            q=wire['points']
            for k in range(0,len(q)-3,2):
                x0,y0,x1,y1=q[k:k+4]
                length=(x1-x0)**2+(y1-y0)**2
                t=0. if not length else max(0.,min(1.,((point.x()-x0)*(x1-x0)+(point.y()-y0)*(y1-y0))/length))
                if math.hypot(point.x()-(x0+t*(x1-x0)),point.y()-(y0+t*(y1-y0)))<=tolerance:
                    return True
        return False
    def _ClearGhosts(self):
        for item in self._ghosts:
            self.scene().removeItem(item)
        self._ghosts=[]
    def _ShowGhosts(self,dx,dy):
        """dashed outlines where the dragged part (or the whole selection) will land"""
        self._ClearGhosts()
        if not (dx or dy):
            return
        moving=[d for d in self.devices if d['selected']] if self._groupDrag else [d for d in self.devices if d['index']==self._pressDevice]
        pen=QPen(_color('blue',self.colorMap),1.,Qt.DashLine)
        for d in moving:
            x0,y0,x1,y1=d['bbox']
            rect=QRectF(QPointF(min(x0,x1),min(y0,y1)),QPointF(max(x0,x1),max(y0,y1))).translated(dx*self.grid,dy*self.grid)
            self._ghosts.append(self.scene().addRect(rect,pen))
    def _Modifiers(self,event):
        return bool(event.modifiers() & (Qt.ControlModifier|Qt.ShiftModifier))
    def mousePressEvent(self,event):
        if self.wiring:
            point=self.Snap(self.mapToScene(event.position().toPoint()))
            if event.button()==Qt.LeftButton:
                if not self.wirePoints or self.wirePoints[-1]!=point:
                    self.wirePoints.append(point)
                self._UpdateWirePreview()
            elif event.button()==Qt.RightButton:
                self.FinishWire()
            return
        if event.button()==Qt.MiddleButton:
            self._pan=event.position()
            self.viewport().setCursor(Qt.ClosedHandCursor)
            return
        if event.button()==Qt.LeftButton and self.placing is not None:
            point=self.mapToScene(event.position().toPoint())
            index=self.placing
            self.StopPlacing()
            self.partDropped.emit(index,point.x(),point.y())
            return
        if event.button()==Qt.LeftButton:
            point=self.mapToScene(event.position().toPoint())
            add=self._Modifiers(event)
            device=self.DeviceAt(point)
            if device is not None:
                if add:
                    self.deviceToggled.emit(device)
                    return
                selected=any(d['index']==device and d['selected'] for d in self.devices)
                self._groupDrag=selected and self.SelectionSize()>1
                self._pressDevice=device
                self._press=point
                if not self._groupDrag:
                    self.deviceClicked.emit(device)
                return
            if not add:
                self.backgroundClicked.emit(point.x(),point.y())
                if self._vertexDrag is not None or self.WireHit(point):
                    return
            self._band={'start':point,'item':None,'add':add,'screen':event.position()}
            return
        super().mousePressEvent(event)
    def mouseMoveEvent(self,event):
        if self.wiring:
            self.wireCursor=self.Snap(self.mapToScene(event.position().toPoint()))
            self._UpdateWirePreview()
            return
        if self._vertexDrag is not None:
            self._vertexDrag['to']=self.Snap(self.mapToScene(event.position().toPoint()))
            self._UpdateWirePreview()
            return
        if self._pan is not None:
            delta=event.position()-self._pan
            self._pan=event.position()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-round(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value()-round(delta.y()))
            return
        if self._band is not None:
            point=self.mapToScene(event.position().toPoint())
            rect=QRectF(self._band['start'],point).normalized()
            if self._band['item'] is None:
                color=_color('blue',self.colorMap)
                fill=QColor(color); fill.setAlpha(28)
                pen=QPen(color,0.,Qt.DashLine); pen.setCosmetic(True)
                self._band['item']=self.scene().addRect(rect,pen,QBrush(fill))
            else:
                self._band['item'].setRect(rect)
            return
        if self._pressDevice is not None and self._press is not None and event.buttons() & Qt.LeftButton:
            point=self.mapToScene(event.position().toPoint())
            self._ShowGhosts(round((point.x()-self._press.x())/self.grid),round((point.y()-self._press.y())/self.grid))
            return
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.MiddleButton and self._pan is not None:
            self._pan=None
            self.viewport().setCursor(Qt.CrossCursor if self.wiring or self.placing is not None else Qt.ArrowCursor)
            return
        if event.button()==Qt.LeftButton and self._band is not None:
            band,self._band=self._band,None
            if band['item'] is not None:
                self.scene().removeItem(band['item'])
            moved=event.position()-band['screen']
            if abs(moved.x())+abs(moved.y())>=4:
                end=self.mapToScene(event.position().toPoint())
                start=band['start']
                self.regionSelected.emit(start.x(),start.y(),end.x(),end.y(),band['add'])
            return
        if event.button()==Qt.LeftButton and self._vertexDrag is not None:
            drag,self._vertexDrag=self._vertexDrag,None
            self._UpdateWirePreview()
            if drag['to'] is not None and drag['to']!=drag['from']:
                self.vertexDragged.emit(drag['wire'],drag['vertex'],float(drag['to'][0]),float(drag['to'][1]))
            return
        if event.button()==Qt.LeftButton and self._pressDevice is not None and self._press is not None:
            point=self.mapToScene(event.position().toPoint())
            dx=round((point.x()-self._press.x())/self.grid)
            dy=round((point.y()-self._press.y())/self.grid)
            self._ClearGhosts()
            device,group=self._pressDevice,self._groupDrag
            self._press=None; self._pressDevice=None; self._groupDrag=False
            if group:
                if dx or dy:
                    self.selectionDragged.emit(dx,dy)
                else:
                    # a click (no drag) on a part of a multiple selection selects just that part
                    self.deviceClicked.emit(device)
            elif dx or dy:
                self.deviceDragged.emit(device,dx,dy)
            return
        super().mouseReleaseEvent(event)
    def mouseDoubleClickEvent(self,event):
        if self.wiring:
            point=self.Snap(self.mapToScene(event.position().toPoint()))
            if not self.wirePoints or self.wirePoints[-1]!=point:
                self.wirePoints.append(point)
            self.FinishWire()
            return
        index=self.DeviceAt(self.mapToScene(event.position().toPoint()))
        if index is not None:
            self.deviceDoubleClicked.emit(index)
            return
        super().mouseDoubleClickEvent(event)
    def contextMenuEvent(self,event):
        if self.wiring:
            return
        index=self.DeviceAt(self.mapToScene(event.pos()))
        if index is None:
            return super().contextMenuEvent(event)
        self.deviceContextMenu.emit(index,event.globalPos(),bool(event.modifiers() & Qt.ControlModifier))
    # ---- placing parts from the stencil
    def StartPlacing(self,index):
        self.placing=index
        self.setDragMode(QGraphicsView.NoDrag)
        self.viewport().setCursor(Qt.CrossCursor)
        self.setFocus()
    def StopPlacing(self):
        self.placing=None
        if not self.wiring:
            self.viewport().unsetCursor()
    # ---- drawing wires: click each vertex, double-click or right-click to finish
    def Snap(self,point):
        return (round(point.x()/self.grid)*self.grid,round(point.y()/self.grid)*self.grid)
    def StartWiring(self):
        if self.placing is not None:
            self.StopPlacing()
        self.wiring=True
        self.wirePoints=[]
        self.setDragMode(QGraphicsView.NoDrag)
        self.viewport().setCursor(Qt.CrossCursor)
        self.setFocus()
    def StopWiring(self):
        self.wiring=False
        self.wirePoints=[]
        self.wireCursor=None
        self._UpdateWirePreview()
        self.viewport().unsetCursor()
    def FinishWire(self):
        """emits the wire drawn so far (two or more points) and starts the next one"""
        points=[list(p) for p in self.wirePoints]
        self.wirePoints=[]
        self._UpdateWirePreview()
        if len(points)>=2:
            self.wireFinished.emit(points)
    def CancelWire(self):
        """drops the wire being drawn; @return False if there was none"""
        if not self.wirePoints:
            return False
        self.wirePoints=[]
        self._UpdateWirePreview()
        return True
    def BeginVertexDrag(self,wire,vertex):
        """starts dragging a wire corner; called while handling backgroundClicked so the press doesn't pan"""
        points=self.drawing['wires'][wire]['points']
        corners=[(points[k],points[k+1]) for k in range(0,len(points)-1,2)]
        self._vertexDrag={'wire':wire,'vertex':vertex,'from':corners[vertex],'to':None,
                          'neighbours':[corners[k] for k in (vertex-1,vertex+1) if 0<=k<len(corners)]}
    def _UpdateWirePreview(self):
        if self.wirePreview is not None:
            self.scene().removeItem(self.wirePreview)
            self.wirePreview=None
        path=None
        drag=self._vertexDrag
        if drag is not None and drag['to'] is not None:
            path=QPainterPath()
            for n in drag['neighbours'] or [drag['to']]:
                path.moveTo(*n); path.lineTo(*drag['to'])
        else:
            points=self.wirePoints+([self.wireCursor] if self.wiring and self.wirePoints and self.wireCursor else [])
            if len(points)>=2:
                path=QPainterPath(QPointF(*points[0]))
                for p in points[1:]:
                    path.lineTo(*p)
        if path is None:
            return
        pen=QPen(_color('blue',self.colorMap),1.5,Qt.DashLine)
        self.wirePreview=self.scene().addPath(path,pen)
    def keyPressEvent(self,event):
        # normally the window's Esc/Del shortcuts get these first
        if event.key()==Qt.Key_Escape:
            self.cancelRequested.emit()
            return
        if event.key() in (Qt.Key_Delete,Qt.Key_Backspace):
            self.deleteRequested.emit()
            return
        if event.key() in (Qt.Key_Return,Qt.Key_Enter) and self.wiring:
            self.FinishWire()
            return
        super().keyPressEvent(event)
    def dragEnterEvent(self,event):
        if event.mimeData().hasFormat(PART_MIME):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)
    def dragMoveEvent(self,event):
        if event.mimeData().hasFormat(PART_MIME):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)
    def dropEvent(self,event):
        if not event.mimeData().hasFormat(PART_MIME):
            return super().dropEvent(event)
        index=int(bytes(event.mimeData().data(PART_MIME)).decode())
        point=self.mapToScene(event.position().toPoint())
        event.acceptProposedAction()
        self.partDropped.emit(index,point.x(),point.y())
