'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from Tkinter import Frame,Entry,Label,StringVar,Toplevel,PhotoImage,BooleanVar,Menu,Button
from Tkinter import TOP,X,YES,LEFT,NO,SUNKEN,RAISED,NONE,BOTH
import matplotlib
import math
import sys
import os
import tkMessageBox


from PartProperty import PartPropertyDelay,PartPropertyReferenceImpedance
from Files import FileParts
from MenuSystemHelpers import Doer

from FilePicker import AskOpenFileName,AskSaveAsFilename

from ToSI import ToSI,FromSI

if not 'matplotlib.backends' in sys.modules:
    matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

from matplotlib.figure import Figure
from matplotlib.collections import LineCollection

from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

class ViewerProperty(Frame):
    def __init__(self,parentFrame,partProperty,callBack):
        Frame.__init__(self,parentFrame)
        self.pack(side=TOP,fill=X,expand=YES)
        self.parentFrame=parentFrame
        self.partProperty=partProperty
        self.callBack=callBack
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
        propertyEntry.pack(side=LEFT, expand=NO, fill=X)
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
    def __init__(self, parent,sp,filename=None,title=None,buttonLabels=None):
        Toplevel.__init__(self, parent)
        self.parent=parent
        self.withdraw()
        self.fileparts=FileParts(filename)
        if title is None:
            if self.fileparts.filename =='':
                self.title('S-parameters')
            else:
                self.title('S-parameters: '+self.fileparts.FileNameTitle())
        else:
            if filename is None:
                self.title(title)
            else:
                self.title(title+': '+self.fileparts.FileNameTitle())

        img = PhotoImage(file=self.parent.installdir+'/icons/png/AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, img)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.variableLineWidth = BooleanVar()
        self.showPassivityViolations = BooleanVar()
        self.showCausalityViolations = BooleanVar()
        self.showImpedance = BooleanVar()
        self.logScale =  BooleanVar()

        # the Doers - the holder of the commands, menu elements, toolbar elements, and key bindings
        self.ReadSParametersFromFileDoer = Doer(self.onReadSParametersFromFile).AddKeyBindElement(self,'<Control-o>').AddHelpElement(self.parent.helpSystemKeys['Control-Help:Open-S-parameter-File'])
        self.WriteSParametersToFileDoer = Doer(self.onWriteSParametersToFile).AddKeyBindElement(self,'<Control-s>').AddHelpElement(self.parent.helpSystemKeys['Control-Help:Save-S-parameter-File'])
        # ------
        self.CalculationPropertiesDoer = Doer(self.onCalculationProperties).AddHelpElement(self.parent.helpSystemKeys['Control-Help:Calculation-Properties'])
        self.ResampleDoer = Doer(self.onResample).AddHelpElement(self.parent.helpSystemKeys['Control-Help:Resample'])
        self.EnforcePassivityDoer = Doer(self.onEnforcePassivity).AddHelpElement(self.parent.helpSystemKeys['Control-Help:Enforce-Passivity'])
        self.EnforceCausalityDoer = Doer(self.onEnforceCausality).AddHelpElement(self.parent.helpSystemKeys['Control-Help:Enforce-Causality'])
        self.WaveletDenoiseDoer = Doer(self.onWaveletDenoise).AddHelpElement(self.parent.helpSystemKeys['Control-Help:Wavelet-Denoise'])
        # ------
        self.HelpDoer = Doer(self.onHelp).AddHelpElement(self.parent.helpSystemKeys['Control-Help:Open-Help-File'])
        self.ControlHelpDoer = Doer(self.onControlHelp).AddHelpElement(self.parent.helpSystemKeys['Control-Help:Control-Help'])
        # ------
        self.VariableLineWidthDoer = Doer(self.PlotSParameter).AddHelpElement(self.parent.helpSystemKeys['Control-Help:Variable-Line-Width'])
        self.ShowPassivityViolationsDoer = Doer(self.PlotSParameter).AddHelpElement(self.parent.helpSystemKeys['Control-Help:Show-Passivity-Violations'])
        self.ShowCausalityViolationsDoer = Doer(self.PlotSParameter).AddHelpElement(self.parent.helpSystemKeys['Control-Help:Show-Causality-Violations'])
        self.ShowImpedanceDoer = Doer(self.PlotSParameter).AddHelpElement(self.parent.helpSystemKeys['Control-Help:Show-Impedance'])
        self.LogScaleDoer = Doer(self.PlotSParameter)
        # ------
        self.EscapeDoer = Doer(self.onEscape).AddKeyBindElement(self,'<Escape>').DisableHelp()

        # The menu system
        TheMenu=Menu(self)
        self.config(menu=TheMenu)
        # ------
        FileMenu=Menu(self)
        TheMenu.add_cascade(label='File',menu=FileMenu,underline=0)
        self.WriteSParametersToFileDoer.AddMenuElement(FileMenu,label="Save",accelerator='Ctrl+S',underline=0)
        self.ReadSParametersFromFileDoer.AddMenuElement(FileMenu,label="Open File",accelerator='Ctrl+O',underline=0)
        # ------
        CalcMenu=Menu(self)
        TheMenu.add_cascade(label='Calculate',menu=CalcMenu,underline=0)
        self.CalculationPropertiesDoer.AddMenuElement(CalcMenu,label='Calculation Properties',underline=0)
        #CalcMenu.add_separator()
        self.ResampleDoer.AddMenuElement(CalcMenu,label='Resample',underline=0)
        #CalcMenu.add_separator()
        self.EnforcePassivityDoer.AddMenuElement(CalcMenu,label='Enforce Passivity',underline=8)
        self.EnforceCausalityDoer.AddMenuElement(CalcMenu,label='Enforce Causality',underline=9)
        self.WaveletDenoiseDoer.AddMenuElement(CalcMenu,label='Wavelet Denoise',underline=0)
        # ------
        ViewMenu=Menu(self)
        TheMenu.add_cascade(label='View',menu=ViewMenu,underline=0)
        self.VariableLineWidthDoer.AddCheckButtonMenuElement(ViewMenu,label='Variable Line Width',underline=9,onvalue=True,offvalue=False,variable=self.variableLineWidth)
        self.ShowPassivityViolationsDoer.AddCheckButtonMenuElement(ViewMenu,label='Show Passivity Violations',underline=5,onvalue=True,offvalue=False,variable=self.showPassivityViolations)
        self.ShowCausalityViolationsDoer.AddCheckButtonMenuElement(ViewMenu,label='Show Causality Violations',underline=6,onvalue=True,offvalue=False,variable=self.showCausalityViolations)
        self.ShowImpedanceDoer.AddCheckButtonMenuElement(ViewMenu,label='Show Impedance',underline=5,onvalue=True,offvalue=False,variable=self.showImpedance)
        self.LogScaleDoer.AddCheckButtonMenuElement(ViewMenu,label='Log Scale',underline=4,onvalue=True,offvalue=False,variable=self.logScale)
        # ------
        HelpMenu=Menu(self)
        TheMenu.add_cascade(label='Help',menu=HelpMenu,underline=0)
        self.HelpDoer.AddMenuElement(HelpMenu,label='Open Help File',underline=0)
        self.ControlHelpDoer.AddMenuElement(HelpMenu,label='Control Help',underline=0)

        # The Toolbar
        ToolBarFrame = Frame(self)
        ToolBarFrame.pack(side=TOP,fill=X,expand=NO)
        self.ReadSParametersFromFileDoer.AddToolBarElement(ToolBarFrame,iconfile=self.parent.installdir+'/icons/png/16x16/actions/document-open-2.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.WriteSParametersToFileDoer.AddToolBarElement(ToolBarFrame,iconfile=self.parent.installdir+'/icons/png/16x16/actions/document-save-2.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        Frame(self,bd=2,relief=SUNKEN).pack(side=LEFT,fill=X,padx=5,pady=5)
        self.CalculationPropertiesDoer.AddToolBarElement(ToolBarFrame,iconfile=self.parent.installdir+'/icons/png/16x16/actions/tooloptions.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        Frame(ToolBarFrame,height=2,bd=2,relief=RAISED).pack(side=LEFT,fill=X,padx=5,pady=5)
        self.HelpDoer.AddToolBarElement(ToolBarFrame,iconfile=self.parent.installdir+'/icons/png/16x16/actions/help-contents-5.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.ControlHelpDoer.AddToolBarElement(ToolBarFrame,iconfile=self.parent.installdir+'/icons/png/16x16/actions/help-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)

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

        self.topLeftFigure=Figure(figsize=(5,2), dpi=100)
        self.topLeftPlot=self.topLeftFigure.add_subplot(111)
        self.topLeftCanvas=FigureCanvasTkAgg(self.topLeftFigure, master=topLeftFrame)
        self.topLeftCanvas.get_tk_widget().pack(side=TOP, fill=X, expand=1)
        self.topLeftToolbar = NavigationToolbar2TkAgg( self.topLeftCanvas, topLeftFrame )
        self.topLeftToolbar.update()
        self.topLeftCanvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        self.topRightFigure=Figure(figsize=(5,2), dpi=100)
        self.topRightPlot=self.topRightFigure.add_subplot(111)
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

        self.bottomLeftFigure=Figure(figsize=(5,2), dpi=100)
        self.bottomLeftPlot=self.bottomLeftFigure.add_subplot(111)
        self.bottomLeftCanvas=FigureCanvasTkAgg(self.bottomLeftFigure, master=bottomLeftFrame)
        self.bottomLeftCanvas.get_tk_widget().pack(side=TOP, fill=X, expand=1)
        self.bottomLeftToolbar = NavigationToolbar2TkAgg( self.bottomLeftCanvas, bottomLeftFrame )
        self.bottomLeftToolbar.update()
        self.bottomLeftCanvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        self.bottomRightFigure=Figure(figsize=(5,2), dpi=100)
        self.bottomRightPlot=self.bottomRightFigure.add_subplot(111)
        self.bottomRightCanvas=FigureCanvasTkAgg(self.bottomRightFigure, master=bottomRightFrame)
        self.bottomRightCanvas.get_tk_widget().pack(side=TOP, fill=X, expand=1)
        self.bottomRightToolbar = NavigationToolbar2TkAgg( self.bottomRightCanvas, bottomRightFrame )
        self.bottomRightToolbar.update()
        self.bottomRightCanvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        controlsFrame = Frame(self)
        controlsFrame.pack(side=TOP,fill=X,expand=NO)
        self.sButtonsFrame = Frame(controlsFrame, bd=1, relief=SUNKEN)
        self.sButtonsFrame.pack(side=LEFT,expand=NO,fill=NONE)
        self.resampleButton=Button(controlsFrame,text='resample',command=self.onResample)
        self.resampleButton.pack(side=LEFT,expand=NO,fill=NONE)

        self.sp=sp

        if buttonLabels is None:
            numPorts=self.sp.m_P
            buttonLabels=[['s'+str(toP+1)+str(fromP+1) for fromP in range(numPorts)] for toP in range(numPorts)]
            self.referenceImpedance=PartPropertyReferenceImpedance(self.sp.m_Z0)
            self.referenceImpedanceProperty=ViewerProperty(controlsFrame,self.referenceImpedance,self.onReferenceImpedanceEntered)
        else:
            # button labels are a proxy for transfer parameters (until I do something better)
            self.showPassivityViolations.set(False)
            self.ShowPassivityViolationsDoer.Activate(False)
            self.ShowCausalityViolationsDoer.Activate(False)
            self.ShowImpedanceDoer.Activate(False)
            self.LogScaleDoer.Activate(False)
            self.EnforcePassivityDoer.Activate(False)
            self.EnforceCausalityDoer.Activate(False)
            self.WaveletDenoiseDoer.Activate(False)
            self.ReadSParametersFromFileDoer.Activate(False)

        self.buttonLabels=buttonLabels

        self.buttons=[]
        for toP in range(len(buttonLabels)):
            buttonrow=[]
            rowFrame=Frame(self.sButtonsFrame)
            rowFrame.pack(side=TOP,expand=NO,fill=NONE)
            for fromP in range(len(buttonLabels[0])):
                thisButton=Button(rowFrame,text=buttonLabels[toP][fromP],width=len(buttonLabels[toP][fromP]),command=lambda x=toP+1,y=fromP+1: self.onSelectSParameter(x,y))
                thisButton.pack(side=LEFT,fill=NONE,expand=NO)
                buttonrow.append(thisButton)
            self.buttons.append(buttonrow)

        self.fromPort = 1
        self.toPort = 1

        self.buttons[self.toPort-1][self.fromPort-1].config(relief=SUNKEN)
        self.PlotSParameter()
        self.deiconify()
        self.geometry("%+d%+d" % (self.parent.root.winfo_x()+self.parent.root.winfo_width()/2-self.winfo_width()/2,
            self.parent.root.winfo_y()+self.parent.root.winfo_height()/2-self.winfo_height()/2))


    def PlotSParameter(self):
        import SignalIntegrity as si
        self.topLeftPlot.cla()
        self.topRightPlot.cla()
        self.bottomLeftPlot.cla()
        self.bottomRightPlot.cla()

        fr=self.sp.FrequencyResponse(self.toPort,self.fromPort)
        ir=fr.ImpulseResponse()

        y=fr.Response('dB')

        freqLabel=ToSI(fr.Frequencies()[-1],'Hz')[-3:]
        freqLabelDivisor=FromSI('1. '+freqLabel,'Hz')

        x=fr.Frequencies(freqLabelDivisor)

        if self.showPassivityViolations.get():
            self.passivityViolations=[]
            s=self.sp._LargestSingularValues()
            for n in range(len(s)):
                if s[n]-1 > 1e-15:
                    dotsize=max(min(20.,math.log10(s[0])/math.log10(1.01)*20.),1e-15)
                    self.passivityViolations.append([x[n],y[n],dotsize])

        lw=[min(1.,math.sqrt(w))*1.5 for w in fr.Response('mag')]

        fastway=True

# this works - properly displays on log plot, only it is just too slow!
#         if self.logScale.get():
#             fastway=False

        if self.variableLineWidth.get():
            if fastway:
                segments = [[[x[i],y[i]],[x[i+1],y[i+1]]] for i in range(len(x)-1)]
                slw=lw[:-1]
                lc = LineCollection(segments, linewidths=slw,color='blue')
                self.topLeftPlot.add_collection(lc)
            else:
                for i in range(len(x)-1):
                    if self.logScale.get():
                        self.topLeftPlot.semilogx(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
                    else:
                        self.topLeftPlot.plot(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
        else:
            if self.logScale.get():
                self.topLeftPlot.semilogx(x,y)
            else:
                self.topLeftPlot.plot(x,y)

        if self.showPassivityViolations.get():
            self.topLeftPlot.scatter(
                [c[0] for c in self.passivityViolations],
                [c[1] for c in self.passivityViolations],
                s=[c[2] for c in self.passivityViolations],
                color='red')

        self.topLeftPlot.set_xlim(xmin=min(x))
        self.topLeftPlot.set_xlim(xmax=max(x))
        self.topLeftPlot.set_ylim(ymin=max(min(y)-1.,-60.0))
        self.topLeftPlot.set_ylim(ymax=max(y)+1.)
        self.topLeftPlot.set_ylabel('magnitude (dB)',fontsize=10)
        self.topLeftPlot.set_xlabel('frequency ('+freqLabel+')',fontsize=10)

        y=fr.Response('deg')
        x=fr.Frequencies(freqLabelDivisor)

        if self.variableLineWidth.get():
            if fastway:
                segments = [[[x[i],y[i]],[x[i+1],y[i+1]]] for i in range(len(x)-1)]
                slw=lw[:-1]
                lc = LineCollection(segments, linewidths=slw,color='blue')
                self.topRightPlot.add_collection(lc)
            else:
                for i in range(len(x)-1):
                    if self.logScale.get():
                        self.topRightPlot.semilogx(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
                    else:
                        self.topRightPlot.plot(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
        else:
            if self.logScale.get():
                self.topRightPlot.semilogx(x,y)
            else:
                self.topRightPlot.plot(x,y)

        self.topRightPlot.set_xlim(xmin=min(x))
        self.topRightPlot.set_xlim(xmax=max(x))
        self.topRightPlot.set_ylim(ymin=min(y)-1)
        self.topRightPlot.set_ylim(ymax=max(y)+1)
        self.topRightPlot.set_ylabel('phase (degrees)',fontsize=10)
        self.topRightPlot.set_xlabel('frequency ('+freqLabel+')',fontsize=10)

        if ir is not None:
            if self.buttonLabels[self.toPort-1][self.fromPort-1][:2]=='i/' or self.buttonLabels[self.toPort-1][self.fromPort-1][:3]=='di/':
                print 'Integrate'
                ir=si.td.wf.ImpulseResponse(ir.Integral(addPoint=False))
            if self.buttonLabels[self.toPort-1][self.fromPort-1][:3]=='di/':
                print 'Integrate'
                ir=si.td.wf.ImpulseResponse(ir.Integral(addPoint=False)*ir.TimeDescriptor().Fs)

            y=ir.Values()

            timeLabel=ToSI(ir.Times()[-1],'s')[-2:]
            timeLabelDivisor=FromSI('1. '+timeLabel,'s')

            x=ir.Times(timeLabelDivisor)

            self.bottomLeftPlot.plot(x,y)

            if self.showCausalityViolations.get():
                self.causalityViolations=[]
                Ts=1./ir.TimeDescriptor().Fs/1e-9
                for k in range(len(x)):
                    if x[k]<=-Ts and abs(y[k])>0:
                        dotsize=max(min(20.,abs(y[k])/0.1*20.),1e-15)
                        self.causalityViolations.append([x[k],y[k],dotsize])
                self.bottomLeftPlot.scatter(
                    [c[0] for c in self.causalityViolations],
                    [c[1] for c in self.causalityViolations],
                    s=[c[2] for c in self.causalityViolations],
                    color='red')

            self.bottomLeftPlot.set_ylim(ymin=min(min(y)*1.05,-0.1))
            self.bottomLeftPlot.set_ylim(ymax=max(max(y)*1.05,0.1))
            self.bottomLeftPlot.set_xlim(xmin=min(x))
            self.bottomLeftPlot.set_xlim(xmax=max(x))
            self.bottomLeftPlot.set_ylabel('amplitude',fontsize=10)
            self.bottomLeftPlot.set_xlabel('time ('+timeLabel+')',fontsize=10)

            firFilter=ir.FirFilter()
            stepWaveformTimeDescriptor=ir.TimeDescriptor()/firFilter.FilterDescriptor()
            stepWaveform=si.td.wf.StepWaveform(stepWaveformTimeDescriptor)
            stepResponse=stepWaveform*firFilter
            y=stepResponse.Values()
            x=stepResponse.Times(timeLabelDivisor)

            if self.showImpedance.get() and (self.fromPort == self.toPort):
                Z0=self.referenceImpedance.GetValue()
                y=[3000. if (1-yv)<=.000001 else min(Z0*(1+yv)/(1-yv),3000) for yv in y]
                x=[xv/2 for xv in x]
                self.bottomRightPlot.set_ylabel('impedance (Ohms)',fontsize=10)
                self.bottomRightPlot.set_xlabel('length ('+timeLabel+')',fontsize=10)
                self.bottomRightPlot.set_ylim(ymin=min(min(y)*1.05,Z0-1))
            else:
                self.bottomRightPlot.set_ylabel('amplitude',fontsize=10)
                self.bottomRightPlot.set_xlabel('time ('+timeLabel+')',fontsize=10)
                self.bottomRightPlot.set_ylim(ymin=min(min(y)*1.05,-0.1))

            self.bottomRightPlot.plot(x,y)

            self.bottomRightPlot.set_ylim(ymax=max(max(y)*1.05,0.1))
            self.bottomRightPlot.set_xlim(xmin=min(x))
            self.bottomRightPlot.set_xlim(xmax=max(x))

        self.topLeftCanvas.draw()
        self.topRightCanvas.draw()
        self.bottomLeftCanvas.draw()
        self.bottomRightCanvas.draw()

    def onSelectSParameter(self,toP,fromP):
        self.buttons[self.toPort-1][self.fromPort-1].config(relief=RAISED)
        self.toPort = toP
        self.fromPort = fromP
        self.buttons[self.toPort-1][self.fromPort-1].config(relief=SUNKEN)
        self.PlotSParameter()

    def onAutoscale(self):
        self.plt.autoscale(True)
        self.f.canvas.draw()

    def onUnwrap(self):
        fr=self.sp.FrequencyResponse(self.toPort,self.fromPort)
        ir=fr.ImpulseResponse()
        if ir is not None:
            idx = ir.Values('abs').index(max(ir.Values('abs')))
            TD = ir.Times()[idx] # the time of the main peak
        else:
            TD=0.
        self.delay.SetValueFromString(str(TD))
        self.delayViewerProperty.onUntouched(None)

    def onDelayEntered(self):
        self.topRightPlot.cla()
        fr=self.sp.FrequencyResponse(self.toPort,self.fromPort)
        TD = self.delay.GetValue()
        fr=fr._DelayBy(-TD)
        lw=[min(1.,math.sqrt(w))*1.5 for w in fr.Response('mag')]
        y=fr.Response('deg')
        x=fr.Frequencies('GHz')
        fastway=True
        if self.variableLineWidth.get():
            if fastway:
                segments = [[[x[i],y[i]],[x[i+1],y[i+1]]] for i in range(len(x)-1)]
                slw=lw[:-1]
                lc = LineCollection(segments, linewidths=slw,color='blue')
                self.topRightPlot.add_collection(lc)
            else:
                for i in range(len(x)-1):
                    if self.logScale.get():
                        self.topRightPlot.semilogx(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
                    else:
                        self.topRightPlot.plot(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
        else:
            if self.logScale.get():
                self.topRightPlot.semilogx(x,y)
            else:
                self.topRightPlot.plot(x,y)
        self.topRightPlot.set_xlim(xmin=min(x))
        self.topRightPlot.set_xlim(xmax=max(x))
        self.topRightPlot.set_ylim(ymin=min(y)-1)
        self.topRightPlot.set_ylim(ymax=max(y)+1)
        self.topRightCanvas.draw()

    def onReferenceImpedanceEntered(self):
        self.sp.SetReferenceImpedance(self.referenceImpedance.GetValue())
        self.PlotSParameter()

    def onReadSParametersFromFile(self):
        import SignalIntegrity as si
        filename=AskOpenFileName(filetypes=[('s-parameter files', ('*.s*p'))],
                                 initialdir=self.fileparts.AbsoluteFilePath(),
                                 parent=self)
        if filename is None:
            return
        self.fileparts=FileParts(filename)
        if self.fileparts.fileext=='':
            return

        self.title('S-parameters: '+self.fileparts.FileNameTitle())

        self.sp=si.sp.SParameterFile(filename)
        self.referenceImpedance.SetValueFromString(str(self.sp.m_Z0))
        self.referenceImpedanceProperty.propertyString.set(self.referenceImpedance.PropertyString(stype='entry'))
        for widget in self.sButtonsFrame.winfo_children():
            widget.destroy()
        numPorts=self.sp.m_P
        self.buttonLabels=[['s'+str(toP+1)+str(fromP+1) for fromP in range(numPorts)] for toP in range(numPorts)]
        self.buttons=[]
        for toP in range(numPorts):
            buttonrow=[]
            rowFrame=Frame(self.sButtonsFrame)
            rowFrame.pack(side=TOP,expand=NO,fill=NONE)
            for fromP in range(numPorts):
                thisButton=Button(rowFrame,text=self.buttonLabels[toP][fromP],command=lambda x=toP+1,y=fromP+1: self.onSelectSParameter(x,y))
                thisButton.pack(side=LEFT,fill=NONE,expand=NO)
                buttonrow.append(thisButton)
            self.buttons.append(buttonrow)
        self.fromPort = 1
        self.toPort = 1
        self.buttons[self.toPort-1][self.fromPort-1].config(relief=SUNKEN)
        self.PlotSParameter()

    def onWriteSParametersToFile(self):
        ports=self.sp.m_P
        extension='.s'+str(ports)+'p'
        filename=AskSaveAsFilename(filetypes=[('s-parameters', extension)],
                    defaultextension=extension,
                    initialdir=self.fileparts.AbsoluteFilePath(),
                    initialfile=self.fileparts.FileNameWithExtension(extension),
                    parent=self)
        if filename is None:
            return
        self.fileparts=FileParts(filename)
        self.sp.WriteToFile(filename,'R '+str(self.sp.m_Z0))

    def onResample(self):
        import SignalIntegrity as si
        self.sp=self.sp.Resample(si.fd.EvenlySpacedFrequencyList(
            self.parent.calculationProperties.endFrequency,
            self.parent.calculationProperties.frequencyPoints))
        self.PlotSParameter()

    def onCalculationProperties(self):
        self.parent.onCalculationProperties()
        #self.parent.calculationProperties.CalculationPropertiesDialog().lift(self)

    def onHelp(self):
        import webbrowser
        helpfile=self.parent.helpSystemKeys['sec:S-parameter-Viewer']
        if helpfile is None:
            tkMessageBox.showerror('Help System','Cannot find or open this help element')
            return
        url = os.path.dirname(os.path.abspath(__file__))+'/Help/PySIHelp.html.LyXconv/'+helpfile
        webbrowser.open(url)

    def onControlHelp(self):
        Doer.inHelp=True
        self.config(cursor='question_arrow')

    def onEscape(self):
        Doer.inHelp=False
        self.config(cursor='left_ptr')

    def onEnforcePassivity(self):
        self.sp.EnforcePassivity()
        self.PlotSParameter()

    def onEnforceCausality(self):
        self.sp.EnforceCausality()
        self.PlotSParameter()

    def onWaveletDenoise(self):
        self.sp.WaveletDenoise()
        self.PlotSParameter()



