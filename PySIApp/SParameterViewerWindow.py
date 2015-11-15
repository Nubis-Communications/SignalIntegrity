'''
Created on Oct 22, 2015

@author: peterp
'''

from Tkinter import *
import matplotlib
import math
import SignalIntegrity as si
from numpy import frompyfunc
from PartProperty import PartPropertyDelay

if not 'matplotlib.backends' in sys.modules:
    matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

from matplotlib.figure import Figure

class ViewerProperty(Frame):
    def __init__(self,parentFrame,partProperty,callBack):
        Frame.__init__(self,parentFrame)
        self.pack(side=TOP,fill=X,expand=YES)
        self.parentFrame=parentFrame
        self.partProperty=partProperty
        self.callBack=callBack
        self.pack(side=TOP,fill=X,expand=YES)
        self.propertyString=StringVar(value=str(self.partProperty.PropertyString(stype='entry')))
        propertyLabel = Label(self,width=25,text=self.partProperty.description+': ',anchor='e')
        propertyLabel.pack(side=LEFT, expand=NO, fill=X)
        propertyEntry = Entry(self,textvariable=self.propertyString)
        propertyEntry.config(width=15)
        propertyEntry.bind('<Return>',self.onEntered)
        propertyEntry.bind('<FocusIn>',self.onTouched)
        propertyEntry.bind('<Button-3>',self.onUntouched)
        propertyEntry.bind('<Escape>',self.onUntouched)
        propertyEntry.bind('<FocusOut>',self.onUntouched)
        propertyEntry.pack(side=LEFT, expand=YES, fill=X)
    def onEntered(self,event):
        self.partProperty.SetValueFromString(self.propertyString.get())
        self.onUntouched(event)
    def onTouched(self,event):
        self.propertyString.set('')
    def onUntouched(self,event):
        self.propertyString.set(self.partProperty.PropertyString(stype='entry'))
        self.callBack()
        self.parentFrame.focus()

class SParametersDialog(Toplevel):
    def __init__(self, parent,sp):
        Toplevel.__init__(self, parent)
        self.parent=parent
        self.title('S-parameters')
        img = PhotoImage(file='./icons/png/AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, img)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        topFrame=Frame(self)
        topFrame.pack(side=TOP,fill=BOTH,expand=YES)
        bottomFrame=Frame(self)
        bottomFrame.pack(side=TOP,fill=BOTH,expand=YES)
        topLeftFrame=Frame(topFrame)
        topLeftFrame.pack(side=LEFT,fill=BOTH,expand=YES)
        topRightFrame=Frame(topFrame)
        topRightFrame.pack(side=LEFT,fill=BOTH,expand=YES)
        bottomLeftFrame=Frame(bottomFrame)
        bottomLeftFrame.pack(side=LEFT,fill=BOTH,expand=YES)
        bottomRightFrame=Frame(bottomFrame)
        bottomRightFrame.pack(side=LEFT,fill=BOTH,expand=YES)
        
        self.topLeftFigure=Figure(figsize=(5,3), dpi=100)
        self.topLeftPlot=self.topLeftFigure.add_subplot(111)
        self.topLeftPlot.set_xlabel('frequency (GHz)')
        self.topLeftPlot.set_ylabel('magnitude (dB)')
        self.topLeftCanvas=FigureCanvasTkAgg(self.topLeftFigure, master=topLeftFrame)
        self.topLeftCanvas.get_tk_widget().pack(side=TOP, fill=X, expand=1)
        self.topLeftToolbar = NavigationToolbar2TkAgg( self.topLeftCanvas, topLeftFrame )
        self.topLeftToolbar.update()
        self.topLeftCanvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        self.topRightFigure=Figure(figsize=(5,3), dpi=100)
        self.topRightPlot=self.topRightFigure.add_subplot(111)
        self.topRightPlot.set_xlabel('frequency (GHz)')
        self.topRightPlot.set_ylabel('phase (deg)')
        self.topRightCanvas=FigureCanvasTkAgg(self.topRightFigure, master=topRightFrame)
        self.topRightCanvas.get_tk_widget().pack(side=TOP, fill=X, expand=1)
        self.topRightToolbar = NavigationToolbar2TkAgg( self.topRightCanvas, topRightFrame )
        self.topRightToolbar.update()
        self.topRightCanvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        self.topRightCanvasControlsFrame=Frame(topRightFrame)
        self.topRightCanvasControlsFrame.pack(side=TOP, fill=X, expand=NO)
        Button(self.topRightCanvasControlsFrame,text='unwrap',command=self.onUnwrap).pack(side=LEFT,expand=NO,fill=NONE)
        self.delay=PartPropertyDelay(0.)
        self.delayViewerProperty=ViewerProperty(self.topRightCanvasControlsFrame,self.delay,self.onDelayEntered)

        self.bottomLeftFigure=Figure(figsize=(5,3), dpi=100)
        self.bottomLeftPlot=self.bottomLeftFigure.add_subplot(111)
        self.bottomLeftPlot.set_xlabel('time (ns)')
        self.bottomLeftPlot.set_ylabel('amplitude')
        self.bottomLeftCanvas=FigureCanvasTkAgg(self.bottomLeftFigure, master=bottomLeftFrame)
        self.bottomLeftCanvas.get_tk_widget().pack(side=TOP, fill=X, expand=1)
        self.bottomLeftToolbar = NavigationToolbar2TkAgg( self.bottomLeftCanvas, bottomLeftFrame )
        self.bottomLeftToolbar.update()
        self.bottomLeftCanvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        self.bottomRightFigure=Figure(figsize=(5,3), dpi=100)
        self.bottomRightPlot=self.bottomRightFigure.add_subplot(111)
        self.bottomRightPlot.set_xlabel('frequency (GHz)')
        self.bottomRightPlot.set_ylabel('phase (deg)')
        self.bottomRightCanvas=FigureCanvasTkAgg(self.bottomRightFigure, master=bottomRightFrame)
        self.bottomRightCanvas.get_tk_widget().pack(side=TOP, fill=X, expand=1)
        self.bottomRightToolbar = NavigationToolbar2TkAgg( self.bottomRightCanvas, bottomRightFrame )
        self.bottomRightToolbar.update()
        self.bottomRightCanvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        self.sp=sp
        
        self.fromPort = 1
        self.toPort = 1
        
        self.PlotSParameter()

        controlsFrame = Frame(self)
        
        sButtonsFrame = Frame(controlsFrame, bd=1, relief=SUNKEN)
        sButtonsFrame.pack(side=LEFT,expand=NO,fill=NONE)
        numPorts=self.sp.m_P
        for toP in range(numPorts):
            rowFrame=Frame(sButtonsFrame)
            rowFrame.pack(side=TOP,expand=NO,fill=NONE)
            for fromP in range(numPorts):
                Button(rowFrame,text='s'+str(toP+1)+str(fromP+1),command=lambda x=toP+1,y=fromP+1: self.onSelectSParameter(x,y)).pack(side=LEFT,fill=NONE,expand=NO)
                       
        #Button(controlsFrame,text='autoscale',command=self.onAutoscale).pack(side=LEFT,expand=NO,fill=X)
        controlsFrame.pack(side=TOP,fill=X,expand=NO)
    
    def PlotSParameter(self):
        self.topLeftPlot.cla()
        self.topRightPlot.cla()
        self.bottomLeftPlot.cla()
        self.bottomRightPlot.cla()

        fr=si.fd.FrequencyResponse(self.sp.f(),self.sp.Response(self.toPort,self.fromPort))
        ir=fr.ImpulseResponse()

        y=fr.Response('dB')
        x=fr.Frequencies('GHz')
        self.topLeftPlot.plot(x,y)
        self.topLeftPlot.set_ylim(ymin=max(min(y),-60.0))
        self.topLeftPlot.set_ylim(ymax=max(y)+1.)

        y=fr.Response('deg')
        x=fr.Frequencies('GHz')
        self.topRightPlot.plot(x,y)
        #self.topRightPlot.canvas.draw()
 
        y=ir.Values()
        x=ir.Times('ns')
        self.bottomLeftPlot.plot(x,y)
        self.bottomLeftPlot.set_ylim(ymin=min(min(y)*1.05,-0.1))
        self.bottomLeftPlot.set_ylim(ymax=max(max(y)*1.05,0.1))

        self.topLeftCanvas.draw()
        self.topRightCanvas.draw()
        self.bottomLeftCanvas.draw()
        self.bottomRightCanvas.draw()
    
    def onSelectSParameter(self,toP,fromP):
        self.toPort = toP
        self.fromPort = fromP
        self.PlotSParameter()

    def onAutoscale(self):
        self.plt.autoscale(True)
        self.f.canvas.draw()

    def UpdateWaveforms(self,waveformList, waveformNamesList):
        self.lift(self.parent)
        self.plt.cla()
        self.plt.set_xlabel('time (ns)',fontsize=10)
        self.plt.set_ylabel('amplitude',fontsize=10)

        if not self.waveformList == None:
            self.plt.autoscale(False)

        self.waveformList=waveformList
        self.waveformNamesList=waveformNamesList

        for wfi in range(len(self.waveformList)):
            self.plt.plot(self.waveformList[wfi].Times('ns'),self.waveformList[wfi].Values(),label=str(self.waveformNamesList[wfi]))

        self.plt.legend(loc='upper right',labelspacing=0.1)
        self.f.canvas.draw()
        return self
    
    def onUnwrap(self):
        fr=si.fd.FrequencyResponse(self.sp.f(),self.sp.Response(self.toPort,self.fromPort))
        ir=fr.ImpulseResponse()
        idx = ir.Values('abs').index(max(ir.Values('abs')))
        TD = ir.Times()[idx] # the time of the main peak
        self.delay.SetValueFromString(str(TD))
        self.delayViewerProperty.onUntouched(None)
        
    def onDelayEntered(self):
        self.topRightPlot.cla()
        fr=si.fd.FrequencyResponse(self.sp.f(),self.sp.Response(self.toPort,self.fromPort))
        TD = self.delay.GetValue()
        fr=fr._DelayBy(-TD)
        y=fr.Response('deg')
        x=fr.Frequencies('GHz')
        self.topRightPlot.plot(x,y)
        self.topRightCanvas.draw()
        





