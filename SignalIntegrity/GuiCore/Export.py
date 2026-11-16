"""
Export.py
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

def _Font(size):
    from PIL import ImageFont
    for name in ('arial.ttf','Arial.ttf','DejaVuSans.ttf','LiberationSans-Regular.ttf','Helvetica.ttc'):
        try:
            return ImageFont.truetype(name,size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()

def _Arrowhead(tip,tail,shape):
    d1,d2,d3=shape
    dx,dy=tip[0]-tail[0],tip[1]-tail[1]
    length=math.hypot(dx,dy) or 1.
    ux,uy=dx/length,dy/length
    px,py=-uy,ux
    return [tip,(tip[0]-ux*d2+px*d3,tip[1]-uy*d2+py*d3),(tip[0]-ux*d1,tip[1]-uy*d1),(tip[0]-ux*d2-px*d3,tip[1]-uy*d2-py*d3)]

def PrimitivesImage(items,bbox,colorMap=None,background='white',scale=2.,margin=16.):
    """renders RecordingCanvas primitives (tk canvas semantics) to a PIL image without any GUI toolkit
    @param colorMap optional mapping of tk colour names (black, blue, salmon, white) to theme colours"""
    from PIL import Image, ImageDraw
    if bbox is None:
        bbox=[0.,0.,320.,240.]
    font=_Font(max(8,int(round(11*scale))))
    # the drawing's bbox only holds text anchor points, so grow it by each label's measured size
    bbox=list(bbox)
    for item in items:
        if item['type']=='text' and item['text']:
            w,h=font.getlength(item['text'])/scale,12.
            anchor=item.get('anchor') or 'center'
            left=item['x']-(0 if 'w' in anchor else w if 'e' in anchor else w/2)
            top=item['y']-(0 if 'n' in anchor else h if 's' in anchor else h/2)
            bbox=[min(bbox[0],left),min(bbox[1],top),max(bbox[2],left+w),max(bbox[3],top+h)]
    x0,y0=bbox[0]-margin,bbox[1]-margin
    width=int(math.ceil((bbox[2]-bbox[0]+2*margin)*scale))
    height=int(math.ceil((bbox[3]-bbox[1]+2*margin)*scale))
    colour=lambda name: (colorMap or {}).get(str(name).lower(),name) if name else None
    image=Image.new('RGB',(max(width,1),max(height,1)),colour('white') if background=='white' and colorMap else background)
    draw=ImageDraw.Draw(image)
    P=lambda x,y: ((x-x0)*scale,(y-y0)*scale)
    def box(b):
        (ax,ay),(bx,by)=P(b[0],b[1]),P(b[2],b[3])
        return [min(ax,bx),min(ay,by),max(ax,bx),max(ay,by)]
    for item in items:
        kind=item['type']
        try:
            if kind=='line':
                points=[P(item['points'][k],item['points'][k+1]) for k in range(0,len(item['points'])-1,2)]
                width_=max(1,int(round(item.get('width',1.)*scale)))
                draw.line(points,fill=colour(item['color']),width=width_,joint='curve')
                arrow=item.get('arrow')
                if arrow and len(points)>=2:
                    shape=[s*scale for s in item.get('arrowshape',[8.,10.,3.])]
                    if arrow in ('last','both'):
                        draw.polygon(_Arrowhead(points[-1],points[-2],shape),fill=colour(item['color']))
                    if arrow in ('first','both'):
                        draw.polygon(_Arrowhead(points[0],points[1],shape),fill=colour(item['color']))
            elif kind=='polygon':
                points=[P(item['points'][k],item['points'][k+1]) for k in range(0,len(item['points'])-1,2)]
                if len(points)>=2:
                    draw.polygon(points,fill=colour(item.get('fill')),outline=colour(item.get('outline')))
            elif kind=='rectangle':
                draw.rectangle(box(item['bbox']),fill=colour(item.get('fill')),outline=colour(item.get('outline')))
            elif kind=='oval':
                draw.ellipse(box(item['bbox']),fill=colour(item.get('fill')),outline=colour(item.get('outline')))
            elif kind=='arc':
                # tk measures angles counter-clockwise from 3 o'clock; PIL clockwise
                start,extent=item['start'],item['extent']
                a0,a1=sorted((-start,-(start+extent)))
                draw.arc(box(item['bbox']),a0,a1,fill=colour(item.get('outline')),width=max(1,int(round(scale))))
            elif kind=='text' and item['text']:
                anchor=item.get('anchor') or 'center'
                h='l' if 'w' in anchor else 'r' if 'e' in anchor else 'm'
                v='t' if 'n' in anchor else 'b' if 's' in anchor else 'm'
                draw.text(P(item['x'],item['y']),item['text'],fill=colour(item.get('color')),font=font,anchor=h+v)
        except (ValueError,TypeError):
            continue
    return image
