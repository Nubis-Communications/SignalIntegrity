"""
TpX.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
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

class TpX(object):
    def __init__(self):
        self.lineList=['%<TpX v="5" TeXFormat="tikz" PdfTeXFormat="tikz" ArrowsSize="0.7" StarsSize="1" DefaultFontHeight="5" DefaultSymbolSize="30" ApproximationPrecision="0.01" PicScale="1" Border="2" BitmapRes="20000" HatchingStep="2" DottedSize="0.5" DashSize="1" LineWidth="0.3" TeXFigure="none" FontSizeInTeX="0">\n']
        self.scale=.25
    def Format(self,num):
        return "{0:0.3f}".format(num).rstrip('0').rstrip('.')
    def Finish(self):
        self.lineList=self.lineList+['%</TpX>\n']
        return self
    def WriteToFile(self,fileName):
        with open(fileName,"w") as f:
            for line in self.lineList:
                f.write(line)
        return self
    def create_oval(self, *args, **kw):
        """Create oval with coordinates x1,y1,x2,y2."""
        xi=float(args[0])*self.scale
        yi=-float(args[1])*self.scale
        xf=float(args[2])*self.scale
        yf=-float(args[3])*self.scale
        xm=(xi+xf)/2
        ym=(yi+yf)/2
        dx=xf-xi
        dy=yf-yi
        line='%  <ellipse x="'+self.Format(xm)+'" y="'+self.Format(ym)+'" dx="'+self.Format(dx)+'" dy="'+self.Format(dy)+'"'
        if 'outline' in kw:
            line=line+' lc="'+kw['outline']+'"'
        if 'fill' in kw:
            line=line+' fill="'+kw['fill']+'"'
        line=line+'/>\n'
        self.lineList.append(line)
    def create_line(self, *args, **kw):
        line='%  <polyline'
        if 'arrow' in kw:
            arrowspec=kw['arrow']
            if arrowspec=='first' or arrowspec=='both':
                line=line+' arr1="h44"'
            if arrowspec=='last' or arrowspec=='both':
                line=line+' arr2="h44"'
            line=line+' arrs="0.5"'
        if 'width' in kw:
            line=line+' lw="'+self.Format(kw['width'])+'"'
        if 'fill' in kw:
            line=line+' lc="'+kw['fill']+'"'
        line=line+'>'
        for ci in range(len(args)//2):
            line=line+self.Format(float(args[ci*2])*self.scale)+','+self.Format(-1.*float(args[ci*2+1])*self.scale)+' '
        line=line[:-1]+'</polyline>\n'
        self.lineList.append(line)
    def create_text(self, *args, **kw):
        x=float(args[0])*self.scale
        y=-1.*float(args[1]+4)*self.scale
        if 'anchor' in kw:
            alignString='halign='
            alignment='"c"'
            anchorString=kw['anchor']
            if 'n' in anchorString:
                y=y-2
            elif 's' in anchorString:
                y=y+2
            if anchorString=='n' or anchorString=='s':
                alignment='"c"'
            elif anchorString=='ne' or anchorString=='e' or anchorString=='se':
                alignment='"r"'
            elif anchorString=='sw' or anchorString=='w' or anchorString=='nw':
                alignment='"l"'
            alignString=alignString+alignment
        else:
            alignString='halign="c"'
        #hack to deal with unicode sigma
        if kw['text']==u"\u03C3":
            line='%  <text x="'+self.Format(x)+'" y="'+self.Format(y)+'" t="" tex="$\sigma$" h="3" '+alignString
        else:
            line='%  <text x="'+self.Format(x)+'" y="'+self.Format(y)+'" t="'+kw['text']+'" h="3" '+alignString
        if 'fill' in kw:
            line=line+' lc="'+kw['fill']+'"'
        line=line+'/>\n'
        self.lineList.append(line)
    def create_polygon(self, *args, **kw):
        line='%  <polygon'
        if 'outline' in kw:
            line=line+' lc="'+kw['outline']+'"'
        if 'fill' in kw:
            if kw['fill'] != '':
                line=line+' fill="'+kw['fill']+'"'
        line=line+'>'
        for ci in range(len(args)//2):
            line=line+self.Format(float(args[ci*2])*self.scale)+','+self.Format(-1.*float(args[ci*2+1])*self.scale)+' '
        line=line[:-1]+'</polygon>\n'
        self.lineList.append(line)
    def create_rectangle(self, *args, **kw):
        xi=float(args[0])*self.scale
        yi=-float(args[1])*self.scale
        xf=float(args[2])*self.scale
        yf=-float(args[3])*self.scale
        x=xi
        y=yi
        w=xf-xi
        h=yf-yi
        line='%  <rect x="'+self.Format(x)+'" y="'+self.Format(y)+'" w="'+self.Format(w)+'" h="'+self.Format(h)+'"'
        if 'outline' in kw:
            line=line+' lc="'+kw['outline']+'"'
        if 'fill' in kw:
            line=line+' fill="'+kw['fill']+'"'
        line=line+'/>\n'
        self.lineList.append(line)
    def create_arc(self, *args, **kw):
        xi=float(args[0])
        yi=float(args[1])
        xf=float(args[2])
        yf=float(args[3])
        theta0=float(kw['start'])
        if theta0==90. or theta0==270.:
            theta0=(theta0+180.)%360.
        thetaExtent=-float(kw['extent'])
        color=kw['outline']
        xc=(xi+xf)/2.
        yc=(yi+yf)/2.
        wt=xf-xi
        ht=yf-yi
        w=max(wt,ht)
        h=min(wt,ht)
        w=abs(wt)
        h=abs(ht)
        steps=int(math.ceil(abs(thetaExtent)/2.))
        coord=[]
        for n in range(steps+1):
            theta=(theta0+n*thetaExtent/steps)*math.pi/180.
            c=math.cos(theta)
            s=math.sin(theta)
            r=1./2.*math.sqrt(w*w+c*c*h*h-c*c*w*w)*w*h/(c*c*w*w-w*w-c*c*h*h)
            x=-r*c+xc
            y=-r*s+yc
            coord.append(x)
            coord.append(y)
        self.create_line(*(tuple(coord)),fill=color)
