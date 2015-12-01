#-------------------------------------------------------------------------------
# Name:        TikZ
# Purpose:
#
# Author:      peter.pupalaikis
#
# Created:     01/12/2015
# Copyright:   (c) peter.pupalaikis 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import math

class TikZ(object):
    def __init__(self):
        self.lineList=[]
        self.lineList.append('\\centering\n')
        self.lineList.append('\\begin{tikzpicture}[x=1.00mm, y=1.00mm, inner xsep=0pt, inner ysep=0pt, outer xsep=0pt, outer ysep=0pt]\n')
        self.scale=.25
    def Format(self,num):
        return "{0:0.3f}".format(num).rstrip('0').rstrip('.')
    def Finish(self):
        self.lineList.append('\\end{tikzpicture}%\n')
        return self
    def Document(self):
        self.lineList=['\\documentclass[10pt]{article}\n\\usepackage{tikz}\n\\begin{document}\n']+self.lineList
        self.lineList.append('\\end{document}\n')
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
        line='\\path[line width=0.30mm'
        if 'outline' in kw:
            line=line+', draw='+kw['outline']
        if 'fill' in kw:
            line=line+', fill='+kw['fill']
        line=line+'] ('+self.Format(xm)+','+self.Format(ym)+') ellipse ('+self.Format(dx/2)+'mm and '+self.Format(dy/2)+'mm);\n'
        self.lineList.append(line)
    def create_line(self, *args, **kw):
        line='\\path[line width='
        if 'width' in kw:
            line=line+self.Format(float(kw['width'])*0.3)+'mm'
        else:
            line=line+'0.30mm'
        if 'fill' in kw:
            line=line+', draw='+kw['fill']
        if 'arrow' in kw:
            arrowspec=kw['arrow']
            if arrowspec=='first':
                line=line+', <-'
            elif arrowspec=='both':
                line=line+', <->'
            elif arrowspec=='last':
                line=line+', ->'
        line=line+'] '
        for ci in range(len(args)/2):
            line=line+'('+self.Format(float(args[ci*2])*self.scale)+','+self.Format(-1.*float(args[ci*2+1])*self.scale)+') -- '
        line=line[:-4]+';\n'
        self.lineList.append(line)
    def create_text(self, *args, **kw):
        line='\\draw'
        if 'fill' in kw:
            line=line+'['+kw['fill']+']'
        x=float(args[0])*self.scale
        y=-1.*float(args[1])*self.scale
        line=line+' ('+self.Format(x)+','+self.Format(y)+')'
        if 'anchor' in kw:
            alignString='halign='
            alignment='base'
            anchorString=kw['anchor']
            if 'n' in anchorString:
                alignment='north'
            else:
                alignment='base'
            if 'e' in anchorString:
                alignment=alignment+' east'
            elif 'w' in anchorString:
                alignment=alignment+' west'
            alignString=' node[anchor='+alignment+']'
        else:
            alignString=' node[anchor=base]'
        line=line+alignString
        textToWrite=kw['text']
        textToWrite=textToWrite.replace('_','\\textunderscore ')
        line=line+'{'+textToWrite+'};\n'
        self.lineList.append(line)
    def create_polygon(self, *args, **kw):
        line='\\path[line width=0.30mm'
        if 'outline' in kw:
            line=line+', draw='+kw['outline']
        if 'fill' in kw:
            if kw['fill'] != '':
                line=line+', fill='+kw['fill']
        line=line+'] '
        for ci in range(len(args)/2):
            line=line+'('+self.Format(float(args[ci*2])*self.scale)+','+self.Format(-1.*float(args[ci*2+1])*self.scale)+') -- '
        line=line+'cycle;\n'
        self.lineList.append(line)
    def create_rectangle(self, *args, **kw):
        line='\\path[line width=0.30mm'
        if 'outline' in kw:
            line=line+', draw='+kw['outline']
        if 'fill' in kw:
            if kw['fill'] != '':
                line=line+', fill='+kw['fill']
        line=line+'] '
        xi=float(args[0])*self.scale
        yi=-float(args[1])*self.scale
        xf=float(args[2])*self.scale
        yf=-float(args[3])*self.scale
        (xi,xf)=(min(xi,xf),max(xi,xf))
        (yi,yf)=(min(yi,yf),max(yi,yf))
        x=xi
        y=yi
        w=xf-xi
        h=yf-yi
        line=line+'('+self.Format(x)+','+self.Format(y)+')'
        line=line+' rectangle +('+self.Format(w)+','+self.Format(h)+');\n'
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