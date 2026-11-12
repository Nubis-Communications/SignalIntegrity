"""
RecordingCanvas.py
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

class RecordingCanvas(object):
    """toolkit-neutral canvas that records the tk.Canvas drawing calls made by the existing
    part pictures, wires and schematic code as a list of JSON-serializable primitives.

    Each primitive is a dict with a 'type' of 'line', 'polygon', 'rectangle', 'oval', 'arc'
    or 'text'.  Coordinates are in the same pixel units the tk application uses."""
    def __init__(self):
        self.items=[]
    @staticmethod
    def _coords(args):
        if len(args)==1 and isinstance(args[0],(list,tuple)):
            args=args[0]
        return [float(a) for a in args]
    @staticmethod
    def _color(value,default=None):
        if value is None or value=='':
            return default
        return str(value)
    def create_line(self,*args,**kw):
        item={'type':'line','points':self._coords(args),
              'color':self._color(kw.get('fill'),'black'),
              'width':float(kw.get('width',1))}
        if kw.get('arrow') in ('first','last','both'):
            item['arrow']=kw['arrow']
            if 'arrowshape' in kw:
                item['arrowshape']=[float(a) for a in kw['arrowshape']]
        if kw.get('dash'):
            item['dash']=[float(d) for d in kw['dash']]
        self.items.append(item)
    def create_polygon(self,*args,**kw):
        self.items.append({'type':'polygon','points':self._coords(args),
                           'outline':self._color(kw.get('outline')),
                           'fill':self._color(kw.get('fill'),'black')})
    def create_rectangle(self,*args,**kw):
        self.items.append({'type':'rectangle','bbox':self._coords(args)[:4],
                           'outline':self._color(kw.get('outline'),'black'),
                           'fill':self._color(kw.get('fill'))})
    def create_oval(self,*args,**kw):
        self.items.append({'type':'oval','bbox':self._coords(args)[:4],
                           'outline':self._color(kw.get('outline'),'black'),
                           'fill':self._color(kw.get('fill'))})
    def create_arc(self,*args,**kw):
        self.items.append({'type':'arc','bbox':self._coords(args)[:4],
                           'start':float(kw.get('start',0.)),
                           'extent':float(kw.get('extent',90.)),
                           'outline':self._color(kw.get('outline'),'black')})
    def create_text(self,*args,**kw):
        x,y=self._coords(args)[:2]
        self.items.append({'type':'text','x':x,'y':y,'text':str(kw.get('text','')),
                           'anchor':kw.get('anchor','center'),
                           'color':self._color(kw.get('fill'),'black')})
    def delete(self,*args):
        self.items=[]
    def BoundingBox(self):
        """@return [xmin,ymin,xmax,ymax] of all geometry or None if empty"""
        xs=[];ys=[]
        for item in self.items:
            if item['type'] in ('line','polygon'):
                xs.extend(item['points'][0::2]); ys.extend(item['points'][1::2])
            elif item['type']=='text':
                xs.append(item['x']); ys.append(item['y'])
            else:
                xs.extend(item['bbox'][0::2]); ys.extend(item['bbox'][1::2])
        if not xs:
            return None
        return [min(xs),min(ys),max(xs),max(ys)]
