"""
Simulator.py
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

import sys

if sys.version_info.major < 3:
    import Tkinter as tk
    import tkMessageBox as messagebox
else:
    import tkinter as tk
    from tkinter import messagebox

from SignalIntegrity.App.SParameterViewerWindow import SParametersDialog
from SignalIntegrity.App.MenuSystemHelpers import Doer
from SignalIntegrity.App.ProgressDialog import ProgressDialog
from SignalIntegrity.App.FilePicker import AskSaveAsFilename
from SignalIntegrity.App.ToSI import FromSI,ToSI
from SignalIntegrity.App.SParameterViewerPreferencesDialog import SParameterViewerPreferencesDialog

from SignalIntegrity.Lib.Test.TestHelpers import PlotTikZ

import SignalIntegrity.App.Project

import matplotlib
import matplotlib.pyplot

if not 'matplotlib.backends' in sys.modules:
    matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

from matplotlib.figure import Figure

import math
from numpy import mean,std

class SimulatorDialog(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent.parent)
        self.parent=parent
        self.withdraw()
        self.title('Simulation')
        self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        self.protocol("WM_DELETE_WINDOW", self.onClosing)

        # the Doers - the holder of the commands, menu elements, toolbar elements, and key bindings
        self.WaveformSaveDoer = Doer(self.onWriteSimulatorToFile).AddHelpElement('Control-Help:Save-Waveforms').AddToolTip('Save waveforms to files')
        # TODO: someday allow waveform reading
        self.WaveformReadDoer = Doer(self.onReadSimulatorFromFile).AddHelpElement('Control-Help:Read-Waveforms').Activate(False).AddToolTip('Read waveforms from files')
        self.Matplotlib2tikzDoer = Doer(self.onMatplotlib2TikZ).AddHelpElement('Control-Help:Simulator-output-to-LaTeX').AddToolTip('Output plots to LaTeX')
        # ------
        self.SelectionsDisplayAllDoer = Doer(self.onSelectionsDisplayAll).AddHelpElement('Control-Help:Display-All').AddToolTip('Display all waveforms')
        self.SelectionsDisplayNoneDoer = Doer(self.onSelectionsDisplayNone).AddHelpElement('Control-Help:Display-None').AddToolTip('Turn off display of all waveforms')
        self.SelectionsToggleAllDoer = Doer(self.onSelectionsToggle).AddHelpElement('Control-Help:Toggle-Selections').AddToolTip('Toggle all waveform display')
        # ------
        self.CalculationPropertiesDoer = Doer(self.onCalculationProperties).AddHelpElement('Control-Help:Calculation-Properties').AddToolTip('Edit calculation properties')
        self.ExamineTransferMatricesDoer = Doer(self.onExamineTransferMatrices).AddHelpElement('Control-Help:View-Transfer-Parameters').AddToolTip('View transfer parameters')
        self.SimulateDoer = Doer(self.parent.parent.onCalculate).AddHelpElement('Control-Help:Recalculate').AddToolTip('Recalculate simulation')
        # ------
        self.ShowGridsDoer = Doer(self.onShowGrids).AddHelpElement('Control-Help:Show-Grids').AddToolTip('Show grids in plots')
        self.ViewTimeDomainDoer = Doer(self.onViewTimeDomain).AddHelpElement('Control-Help:View-Time-domain').AddToolTip('View time-domain waveforms')
        self.ViewSpectralContentDoer = Doer(self.onViewSpectralContent).AddHelpElement('Control-Help:View-Spectral-Content').AddToolTip('View spectral content of waveforms')
        self.ViewSpectralDensityDoer = Doer(self.onViewSpectralDensity).AddHelpElement('Control-Help:View-Spectral-Density').AddToolTip('View spectral density of waveforms')
        # ------
        self.HelpDoer = Doer(self.onHelp).AddHelpElement('Control-Help:Simulator-Open-Help-File').AddToolTip('Open the help system in a browser')
        self.ControlHelpDoer = Doer(self.onControlHelp).AddHelpElement('Control-Help:Simulator-Control-Help').AddToolTip('Get help on a control')
        self.PreferencesDoer=Doer(self.onPreferences).AddHelpElement('Control-Help:Simulator-Preferences').AddToolTip('Edit the preferences')
        # ------
        self.EscapeDoer = Doer(self.onEscape).AddKeyBindElement(self,'<Escape>').DisableHelp()

        # The menu system
        TheMenu=tk.Menu(self)
        self.TheMenu=TheMenu
        self.config(menu=TheMenu)
        FileMenu=tk.Menu(self)
        TheMenu.add_cascade(label='File',menu=FileMenu,underline=0)
        self.WaveformSaveDoer.AddMenuElement(FileMenu,label="Save Waveforms",underline=0)
        self.WaveformReadDoer.AddMenuElement(FileMenu,label="Read Waveforms",underline=0)
        FileMenu.add_separator()
        self.Matplotlib2tikzDoer.AddMenuElement(FileMenu,label='Output to LaTeX (TikZ)',underline=10)
        # ------
        self.SelectionMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Selection',menu=self.SelectionMenu,underline=0)
        self.SelectionsDisplayAllDoer.AddMenuElement(self.SelectionMenu,label='Display All',underline=8)
        self.SelectionsDisplayNoneDoer.AddMenuElement(self.SelectionMenu,label='Dispay None',underline=7)
        self.SelectionsToggleAllDoer.AddMenuElement(self.SelectionMenu,label='Toggle All',underline=0)
        self.SelectionMenu.add_separator()
        # ------
        CalcMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Calculate',menu=CalcMenu,underline=0)
        self.CalculationPropertiesDoer.AddMenuElement(CalcMenu,label='Calculation Properties',underline=12)
        self.ExamineTransferMatricesDoer.AddMenuElement(CalcMenu,label='View Transfer Parameters',underline=0)
        CalcMenu.add_separator()
        self.SimulateDoer.AddMenuElement(CalcMenu,label='Recalculate',underline=0)
        # ------
        ViewMenu=tk.Menu(self)
        TheMenu.add_cascade(label='View',menu=ViewMenu,underline=0)
        self.ShowGridsDoer.AddCheckButtonMenuElement(ViewMenu,label='Show Grids',underline=5)
        self.ShowGridsDoer.Set(SignalIntegrity.App.Preferences['Appearance.GridsOnPlots'])
        self.ViewTimeDomainDoer.AddCheckButtonMenuElement(ViewMenu,label='View Time-domain',underline=5)
        self.ViewTimeDomainDoer.Set(True)
        self.ViewSpectralContentDoer.AddCheckButtonMenuElement(ViewMenu,label='View Spectral Content',underline=14)
        self.ViewSpectralDensityDoer.AddCheckButtonMenuElement(ViewMenu,label='View Spectral Density',underline=14)
        # ------
        HelpMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Help',menu=HelpMenu,underline=0)
        self.HelpDoer.AddMenuElement(HelpMenu,label='Open Help File',underline=0)
        self.ControlHelpDoer.AddMenuElement(HelpMenu,label='Control Help',underline=0)
        self.PreferencesDoer.AddMenuElement(HelpMenu,label='Preferences',underline=0)

        # The Toolbar
        ToolBarFrame = tk.Frame(self)
        ToolBarFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        iconsdir=SignalIntegrity.App.IconsDir+''
        self.WaveformReadDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'document-open-2.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.WaveformSaveDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'document-save-2.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        tk.Frame(self,height=2,bd=2,relief=tk.RAISED).pack(side=tk.LEFT,fill=tk.X,padx=5,pady=5)
        self.CalculationPropertiesDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'tooloptions.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.SimulateDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'system-run-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        tk.Frame(ToolBarFrame,height=2,bd=2,relief=tk.RAISED).pack(side=tk.LEFT,fill=tk.X,padx=5,pady=5)
        self.HelpDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'help-contents-5.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.ControlHelpDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'help-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)

        labelFrame = tk.Frame(self)
        labelFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.plotLabel = tk.Label(labelFrame,fg='black')
        self.plotLabel.pack(fill=tk.X)

        plotWidth=SignalIntegrity.App.Preferences['Appearance.PlotWidth']
        plotHeight=SignalIntegrity.App.Preferences['Appearance.PlotHeight']
        plotDPI=SignalIntegrity.App.Preferences['Appearance.PlotDPI']

        self.f = Figure(figsize=(plotWidth,plotHeight), dpi=plotDPI)

        self.plt = self.f.add_subplot(111)
        self.plt.set_xlabel('time (ns)')
        self.plt.set_ylabel('amplitude')

        self.waveformList=None
        self.waveformNamesList=None
        self.canvas = FigureCanvasTkAgg(self.f, master=self)
        #canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        toolbar = NavigationToolbar2Tk( self.canvas, self )
        toolbar.update()
        toolbar.pan()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        controlsFrame = tk.Frame(self)
        tk.Button(controlsFrame,text='autoscale',command=self.onAutoscale).pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        controlsFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)

        try:
            try:
                from tikzplotlib import save as tikz_save
            except:
                try:
                    from matplotlib2tikz import save as tikz_save
                except:
                    self.Matplotlib2tikzDoer.Activate(False)
        except:
            self.Matplotlib2tikzDoer.Activate(False)

        self.ExamineTransferMatricesDoer.Activate(False)
        self.SimulateDoer.Activate(False)
        self.ZoomsInitialized=False

        self.geometry("%+d%+d" % (self.parent.parent.root.winfo_x()+self.parent.parent.root.winfo_width()/2-self.winfo_width()/2,
            self.parent.parent.root.winfo_y()+self.parent.parent.root.winfo_height()/2-self.winfo_height()/2))

    def onXLimitChange(self,ax):
        xlim=ax.get_xlim()
        self.minx=xlim[0]
        self.maxx=xlim[1]

    def onYLimitChange(self,ax):
        ylim=ax.get_ylim()
        self.miny=ylim[0]
        self.maxy=ylim[1]

    def onClosing(self):
        self.withdraw()
        self.destroy()

    def destroy(self):
        tk.Toplevel.withdraw(self)
        tk.Toplevel.destroy(self)

    def onAutoscale(self):
        self.plt.autoscale(True)
        self.f.canvas.draw()

    def PlotWaveformsFrequencyContent(self,density=False):
        self.lift(self.parent.parent)
        self.plt.cla()

        import SignalIntegrity.Lib as si
        fd=si.fd.EvenlySpacedFrequencyList(
            SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
            SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints']
            )

        if not SignalIntegrity.App.Preferences['Appearance.PlotCursorValues']:
            self.plt.format_coord = lambda x, y: ''

        if not self.waveformList == None:
            self.plt.autoscale(False)

        self.frequencyContentList=[wf.FrequencyContent().LimitEndFrequency(SignalIntegrity.App.Project['CalculationProperties.EndFrequency'])
            for wf in self.waveformList]

        minf=None
        maxf=None
        for wfi in range(len(self.waveformList)):
            fc=self.frequencyContentList[wfi]
            fcFrequencies=fc.Frequencies()
            if len(fcFrequencies)==0:
                continue
            fcValues=fc.Values('dBm')
            fcName=str(self.waveformNamesList[wfi])
            minf=fcFrequencies[0] if minf is None else min(minf,fcFrequencies[0])
            maxf=fcFrequencies[-1] if maxf is None else max(maxf,fcFrequencies[-1])

        freqLabel='Hz'
        freqLabelDivisor=1.
        if not self.waveformList is None:
            if (not minf is None) and (not maxf is None):
                durLabelFrequency=(maxf-minf)
                freqLabel=ToSI(durLabelFrequency,'Hz')[-3:]
                freqLabelDivisor=FromSI('1. '+freqLabel,'Hz')
                minf=minf/freqLabelDivisor
                maxf=maxf/freqLabelDivisor

            if not self.ZoomsInitialized:
                self.minx=minf
                self.maxx=maxf

            if self.minx != None:
                self.plt.set_xlim(left=self.minx)

            if self.maxx != None:
                self.plt.set_xlim(right=self.maxx)

        if density:
            self.plotLabel.config(text='Spectral Density')
            self.plt.set_ylabel('magnitude (dBm/'+freqLabel+')',fontsize=10)
        else:
            self.plotLabel.config(text='Spectral Content')
            self.plt.set_ylabel('magnitude (dBm)',fontsize=10)

        minv=None
        maxv=None
        minvStd=None
        for wfi in range(len(self.frequencyContentList)):
            fc=self.frequencyContentList[wfi]
            fcFrequencies=fc.Frequencies(freqLabelDivisor)
            if len(fcFrequencies)==0:
                continue
            if density:
                adder=10.*math.log10(freqLabelDivisor)
                fcValues=[v+adder for v in fc.Values('dBmPerHz')]
            else:
                fcValues=fc.Values('dBm')
            minv=min(fcValues) if minv is None else min(minv,min(fcValues))
            maxv=max(fcValues) if maxv is None else max(maxv,max(fcValues))
            minvStd=mean(fcValues)-0.5*std(fcValues) if minvStd is None else min(minvStd,mean(fcValues)-0.5*std(fcValues))

            fcName=str(self.waveformNamesList[wfi])
            fcColor=self.waveformColorIndexList[wfi]

            self.plt.plot(fcFrequencies,fcValues,label=fcName,c=fcColor)

        if minv != None or minvStd != None:
            minv = max(minv,minvStd)

        self.plt.set_xlabel('frequency ('+freqLabel+')',fontsize=10)
        self.plt.legend(loc='upper right',labelspacing=0.1)

        if not self.ZoomsInitialized:
            self.miny=minv
            self.maxy=maxv

        if self.miny != None:
            self.plt.set_ylim(bottom=self.miny)
        if self.maxy != None:
            self.plt.set_ylim(top=self.maxy)

        if self.ShowGridsDoer.Bool():
            self.plt.grid(True)

        self.ZoomsInitialized=True
        self.f.canvas.draw()

        self.plt.callbacks.connect('xlim_changed', self.onXLimitChange)
        self.plt.callbacks.connect('ylim_changed', self.onYLimitChange)

        return self

    def UpdateWaveforms(self,waveformList, waveformNamesList):
        self.totalwaveformList=waveformList
        self.totalwaveformNamesList=waveformNamesList
        # ------
        self.SelectionDoerList = [Doer(lambda x=s: self.onSelection(x)) for s in range(len(self.totalwaveformNamesList))]
        # ------
        # ------
        self.SelectionMenu.delete(5, tk.END)
        for s in range(len(self.totalwaveformNamesList)):
            self.SelectionDoerList[s].AddCheckButtonMenuElement(self.SelectionMenu,label=self.totalwaveformNamesList[s])
            self.SelectionDoerList[s].Set(True)
        self.TheMenu.entryconfigure('Selection', state= tk.DISABLED if len(self.totalwaveformNamesList) <= 1 else tk.ACTIVE)
        # ------

        self.onSelection()
        return self

    def onSelectionsDisplayAll(self):
        for sd in self.SelectionDoerList:
            sd.Set(True)
        self.onSelection()

    def onSelectionsDisplayNone(self):
        for sd in self.SelectionDoerList:
            sd.Set(False)
        self.onSelection()

    def onSelectionsToggle(self):
        for sd in self.SelectionDoerList:
            sd.Set(not sd.Bool())
        self.onSelection()

    def onSelection(self,x=None):
        self.waveformList=[]
        self.waveformNamesList=[]
        self.waveformColorIndexList=[]
        colors=matplotlib.pyplot.rcParams['axes.prop_cycle'].by_key()['color']
        for si in range(len(self.SelectionDoerList)):
            if self.SelectionDoerList[si].Bool():
                self.waveformList.append(self.totalwaveformList[si])
                self.waveformNamesList.append(self.totalwaveformNamesList[si])
                self.waveformColorIndexList.append(colors[si%len(colors)])

#         if self.waveformList == []:
#             self.waveformList = None
#             self.waveformNamesList = None

        if self.ViewTimeDomainDoer.Bool():
            self.PlotWaveformsTimeDomain()
        elif self.ViewSpectralContentDoer.Bool():
            self.PlotWaveformsFrequencyContent(density=False)
        elif self.ViewSpectralDensityDoer.Bool():
            self.PlotWaveformsFrequencyContent(density=True)
        return self

    def onShowGrids(self):
        SignalIntegrity.App.Preferences['Appearance.GridsOnPlots']=self.ShowGridsDoer.Bool()
        SignalIntegrity.App.Preferences.SaveToFile()
        self.onSelection()

    def onViewTimeDomain(self):
        self.ZoomsInitialized=False
        self.ViewSpectralDensityDoer.Set(False)
        self.ViewSpectralContentDoer.Set(False)
        self.PlotWaveformsTimeDomain()

    def onViewSpectralContent(self):
        self.ZoomsInitialized=False
        self.ViewTimeDomainDoer.Set(False)
        self.ViewSpectralDensityDoer.Set(False)
        self.PlotWaveformsFrequencyContent(density=False)

    def onViewSpectralDensity(self):
        self.ZoomsInitialized=False
        self.ViewTimeDomainDoer.Set(False)
        self.ViewSpectralContentDoer.Set(False)
        self.PlotWaveformsFrequencyContent(density=True)

    def PlotWaveformsTimeDomain(self):
        self.lift(self.parent.parent)
        self.plt.cla()
        self.plt.set_ylabel('amplitude',fontsize=10)
        self.plotLabel.config(text='Time-domain View')

        if not SignalIntegrity.App.Preferences['Appearance.PlotCursorValues']:
            self.plt.format_coord = lambda x, y: ''

        if not self.waveformList == None:
            self.plt.autoscale(False)

        mint=None
        maxt=None
        for wfi in range(len(self.waveformList)):
            wf=self.waveformList[wfi]
            wfTimes=wf.Times()
            if len(wfTimes)==0:
                continue
            wfValues=wf.Values()
            wfName=str(self.waveformNamesList[wfi])
            mint=wfTimes[0] if mint is None else min(mint,wfTimes[0])
            maxt=wfTimes[-1] if maxt is None else max(maxt,wfTimes[-1])

        timeLabel='s'
        timeLabelDivisor=1.
        if not self.waveformList is None:
            if (not mint is None) and (not maxt is None):
                durLabelTime=(maxt-mint)
                timeLabel=ToSI(durLabelTime,'s')[-2:]
                timeLabelDivisor=FromSI('1. '+timeLabel,'s')
                mint=mint/timeLabelDivisor
                maxt=maxt/timeLabelDivisor

        if not self.ZoomsInitialized:
            self.minx=mint
            self.maxx=maxt

        if self.minx != None:
            self.plt.set_xlim(left=self.minx)

        if self.maxx != None:
            self.plt.set_xlim(right=self.maxx)

        minv=None
        maxv=None
        for wfi in range(len(self.waveformList)):
            wf=self.waveformList[wfi]
            wfTimes=wf.Times(timeLabelDivisor)
            if len(wfTimes)==0:
                continue
            wfValues=wf.Values()
            wfName=str(self.waveformNamesList[wfi])
            wfColor=self.waveformColorIndexList[wfi]
            plotlog=False
            plotdB=False
            if plotlog:
                self.plt.semilogy(wfTimes,wf.Values('abs'),label=wfName,c=wfColor)
            elif plotdB:
                self.plt.plot(wfTimes,[max(20.*math.log10(abs(a)),-200.) for a in wf.Values('abs')],label=wfName,c=wfColor)
            else:
                self.plt.plot(wfTimes,wfValues,label=wfName,c=wfColor)
            minv=min(wfValues) if minv is None else min(minv,min(wfValues))
            maxv=max(wfValues) if maxv is None else max(maxv,max(wfValues))

        self.plt.set_xlabel('time ('+timeLabel+')',fontsize=10)
        self.plt.legend(loc='upper right',labelspacing=0.1)

        if not self.ZoomsInitialized:
            self.miny=minv
            self.maxy=maxv

        if self.miny != None:
            self.plt.set_ylim(bottom=self.miny)

        if self.maxy != None:
            self.plt.set_ylim(top=self.maxy)

        if self.ShowGridsDoer.Bool():
            self.plt.grid(True)

        self.ZoomsInitialized=True
        self.f.canvas.draw()

        self.plt.callbacks.connect('xlim_changed', self.onXLimitChange)
        self.plt.callbacks.connect('ylim_changed', self.onYLimitChange)

        return self

    def onWriteSimulatorToFile(self):
        for wfi in range(len(self.waveformNamesList)):
            outputWaveformName=self.waveformNamesList[wfi]
            outputWaveform=self.waveformList[wfi]
            if self.parent.parent.fileparts.filename=='':
                filename=outputWaveformName
            else:
                filename=self.parent.parent.fileparts.filename+'_'+outputWaveformName
            filename=AskSaveAsFilename(parent=self,filetypes=[('waveform', '.txt')],
                            defaultextension='.txt',
                            initialdir=self.parent.parent.fileparts.AbsoluteFilePath(),
                            initialfile=filename+'.txt')
            if filename is None:
                continue
            outputWaveform.WriteToFile(filename)

    def onReadSimulatorFromFile(self):
        pass
    def onCalculationProperties(self):
        self.parent.parent.onCalculationProperties()

    def onExamineTransferMatrices(self):
        buttonLabelList=[[out+' due to '+inp for inp in self.parent.sourceNames] for out in self.parent.outputWaveformLabels]
        maxLength=len(max([item for sublist in buttonLabelList for item in sublist],key=len))
        buttonLabelList=[[item.ljust(maxLength) for item in sublist] for sublist in buttonLabelList]
        sp=self.parent.transferMatrices.SParameters()
        SParametersDialog(self.parent.parent,sp,
                          self.parent.parent.fileparts.FullFilePathExtension('s'+str(sp.m_P)+'p'),
                          'Transfer Parameters',buttonLabelList)

    def onMatplotlib2TikZ(self):
        if self.ViewTimeDomainDoer.Bool():
            suffix='Waveforms'
        elif self.ViewSpectralContentDoer.Bool():
            suffix='SpectralContent'
        elif self.ViewSpectralDensityDoer.Bool():
            suffix='SpectralDensity'
        filename=AskSaveAsFilename(parent=self,filetypes=[('tex', '.tex')],
                                   defaultextension='.tex',
                                   initialdir=self.parent.parent.fileparts.AbsoluteFilePath(),
                                   initialfile=self.parent.parent.fileparts.filename+suffix+'.tex')
        if filename is None:
            return
        try:
            PlotTikZ(filename,self.f)
        except:
            messagebox.showerror('Export LaTeX','LaTeX could not be generated or written ')
    def onHelp(self):
        if Doer.helpKeys is None:
            messagebox.showerror('Help System','Cannot find or open this help element')
            return
        Doer.helpKeys.Open('sec:Simulator-Dialog')

    def onControlHelp(self):
        Doer.inHelp=True
        self.config(cursor='question_arrow')

    def onEscape(self):
        Doer.inHelp=False
        self.config(cursor='left_ptr')

    def onPreferences(self):
        if not hasattr(self, 'preferencesDialog'):
            self.preferencesDialog = SParameterViewerPreferencesDialog(self,SignalIntegrity.App.Preferences)
        if self.preferencesDialog == None:
            self.preferencesDialog= SParameterViewerPreferencesDialog(self,SignalIntegrity.App.Preferences)
        else:
            if not self.preferencesDialog.winfo_exists():
                self.preferencesDialog=SParameterViewerPreferencesDialog(self,SignalIntegrity.App.Preferences)

class Simulator(object):
    def __init__(self,parent):
        self.parent=parent
    def SimulatorDialog(self):
        if not hasattr(self,'simulatorDialog'):
            self.simulatorDialog=SimulatorDialog(self)
        if self.simulatorDialog == None:
            self.simulatorDialog=SimulatorDialog(self)
        else:
            if not self.simulatorDialog.winfo_exists():
                self.simulatorDialog=SimulatorDialog(self)
        return self.simulatorDialog
    def UpdateWaveforms(self,outputWaveformList,outputWaveformLabels):
        self.SimulatorDialog().UpdateWaveforms(outputWaveformList,outputWaveformLabels).state('normal')
    def _ProcessWaveforms(self,callback=None):
        return self.transferMatriceProcessor.ProcessWaveforms(self.inputWaveformList)
    def Simulate(self):
        netList=self.parent.Drawing.schematic.NetList()
        netListText=netList.Text()
        import SignalIntegrity.Lib as si
        fd=si.fd.EvenlySpacedFrequencyList(
            SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
            SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints']
            )
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.parent.fileparts.FileNameTitle()
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        snp=si.p.SimulatorNumericParser(fd,cacheFileName=cacheFileName)
        snp.AddLines(netListText)
        progressDialog=ProgressDialog(self.parent,"Transfer Parameters",snp,snp.TransferMatrices, granularity=1.0)
        try:
            self.transferMatrices=progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Simulator',e.parameter+': '+e.message)
            return

        #self.transferMatrices.SParameters().WriteToFile('xfer.sXp')

        self.outputWaveformLabels=netList.OutputNames()

        try:
            self.inputWaveformList=self.parent.Drawing.schematic.InputWaveforms()
            self.sourceNames=netList.SourceNames()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Simulator',e.parameter+': '+e.message)
            return

        diresp=si.fd.Differentiator(fd).Response()

        for r in range(len(self.outputWaveformLabels)):
            for c in range(len(self.inputWaveformList)):
                if self.outputWaveformLabels[r][:3]=='di/' or self.outputWaveformLabels[r][:2]=='d/':
                    #print 'differentiate: '+self.outputWaveformLabels[r]
                    for n in range(len(self.transferMatrices)):
                        self.transferMatrices[n][r][c]=self.transferMatrices[n][r][c]*diresp[n]

        self.transferMatriceProcessor=si.td.f.TransferMatricesProcessor(self.transferMatrices)
        si.td.wf.Waveform.adaptionStrategy='SinX' if SignalIntegrity.App.Preferences['Calculation.UseSinX'] else 'Linear'

        progressDialog=ProgressDialog(self.parent,"Waveform Processing",self.transferMatriceProcessor,self._ProcessWaveforms)
        try:
            outputWaveformList = progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Simulator',e.parameter+': '+e.message)
            return

        for r in range(len(outputWaveformList)):
            if self.outputWaveformLabels[r][:3]=='di/' or self.outputWaveformLabels[r][:2]=='i/':
                #print 'integrate: '+self.outputWaveformLabels[r]
                outputWaveformList[r]=outputWaveformList[r].Integral()

        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = self.outputWaveformLabels[outputWaveformIndex]
            for device in self.parent.Drawing.schematic.deviceList:
                if device['partname'].GetValue() in ['Output','DifferentialVoltageOutput','CurrentOutput']:
                    if device['ref'].GetValue() == outputWaveformLabel:
                        # probes may have different kinds of gain specified
                        gainProperty = device['gain']
                        gain=gainProperty.GetValue()
                        offset=device['offset'].GetValue()
                        delay=device['td'].GetValue()
                        if gain != 1.0 or offset != 0.0 or delay != 0.0:
                            outputWaveform = outputWaveform.DelayBy(delay)*gain+offset
                        outputWaveformList[outputWaveformIndex]=outputWaveform
                        break
        userSampleRate=SignalIntegrity.App.Project['CalculationProperties.UserSampleRate']
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,int(wf.td.K*userSampleRate/wf.td.Fs),userSampleRate))
                for wf in outputWaveformList]
        self.SimulatorDialog().title('Sim: '+self.parent.fileparts.FileNameTitle())
        self.SimulatorDialog().ExamineTransferMatricesDoer.Activate(True)
        self.SimulatorDialog().SimulateDoer.Activate(True)
        self.UpdateWaveforms(outputWaveformList, self.outputWaveformLabels)

    def VirtualProbe(self):
        netList=self.parent.Drawing.schematic.NetList()
        netListText=netList.Text()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.parent.fileparts.FileNameTitle()
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        snp=si.p.VirtualProbeNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
                SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints']),
            cacheFileName=cacheFileName)
        snp.AddLines(netListText)
        progressDialog=ProgressDialog(self.parent,"Transfer Parameters",snp,snp.TransferMatrices, granularity=1.0)
        try:
            self.transferMatrices=progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Virtual Probe',e.parameter+': '+e.message)
            return

        self.transferMatriceProcessor=si.td.f.TransferMatricesProcessor(self.transferMatrices)
        si.td.wf.Waveform.adaptionStrategy='SinX' if SignalIntegrity.App.Preferences['Calculation.UseSinX'] else 'Linear'

        try:
            self.inputWaveformList=self.parent.Drawing.schematic.InputWaveforms()
            self.sourceNames=netList.MeasureNames()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Virtual Probe',e.parameter+': '+e.message)
            return

        progressDialog=ProgressDialog(self.parent,"Waveform Processing",self.transferMatriceProcessor,self._ProcessWaveforms)
        try:
            outputWaveformList = progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Virtual Probe',e.parameter+': '+e.message)
            return

        self.outputWaveformLabels=netList.OutputNames()

        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = self.outputWaveformLabels[outputWaveformIndex]
            for device in self.parent.Drawing.schematic.deviceList:
                if device['partname'].GetValue() in ['Output','DifferentialVoltageOutput','CurrentOutput']:
                    if device['ref'].GetValue() == outputWaveformLabel:
                        # probes may have different kinds of gain specified
                        gainProperty = device['gain']
                        gain=gainProperty.GetValue()
                        offset=device['offset'].GetValue()
                        delay=device['td'].GetValue()
                        if gain != 1.0 or offset != 0.0 or delay != 0.0:
                            outputWaveform = outputWaveform.DelayBy(delay)*gain+offset
                        outputWaveformList[outputWaveformIndex]=outputWaveform
                        break
        userSampleRate=SignalIntegrity.App.Project['CalculationProperties.UserSampleRate']
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,int(wf.td.K*userSampleRate/wf.td.Fs),userSampleRate))
                for wf in outputWaveformList]
        self.SimulatorDialog().title('Virtual Probe: '+self.parent.fileparts.FileNameTitle())
        self.SimulatorDialog().ExamineTransferMatricesDoer.Activate(True)
        self.SimulatorDialog().SimulateDoer.Activate(True)
        self.UpdateWaveforms(outputWaveformList, self.outputWaveformLabels)
