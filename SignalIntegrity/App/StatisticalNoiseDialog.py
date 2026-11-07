"""
StatisticalNoiseDialog.py
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

import sys

import tkinter as tk
from tkinter import messagebox

from SignalIntegrity.App.MenuSystemHelpers import Doer,StatusBar
from SignalIntegrity.App.SParameterViewerPreferencesDialog import SParameterViewerPreferencesDialog
from SignalIntegrity.App.StatisticalNoiseMeasurementsDialog import StatisticalNoiseMeasurementsDialog
from SignalIntegrity.Lib.ToSI import FromSI,ToSI

import SignalIntegrity.App.Project

import math

import SignalIntegrity.Lib as si

class StatisticalNoiseDialog(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent.parent)
        self.parent=parent
        self.displayScale=getattr(parent.parent,'displayScale',1.0)
        self.withdraw()
        self.title('Statistical Noise')
        self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        self.protocol("WM_DELETE_WINDOW", self.onClosing)

        import matplotlib.pyplot
        import matplotlib
        if not 'matplotlib.backends' in sys.modules:
            matplotlib.use('TkAgg')

        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

        from matplotlib.figure import Figure

        # the Doers - the holder of the commands, menu elements, toolbar elements, and key bindings
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
        self.LogScaleDoer = Doer(self.onLogScale).AddHelpElement('Control-Help:Sim-Log-Scale').AddToolTip('Show frequency plots log scale')
        self.NoiseMeasurementsDoer = Doer(self.onNoiseMeasurements).AddHelpElement('Control-Help:Noise-Measurements').AddToolTip('View the noise measurements')
        # ------
        self.HelpDoer = Doer(self.onHelp).AddHelpElement('Control-Help:Statistical-Noise-Open-Help-File').AddToolTip('Open the help system in a browser')
        self.ControlHelpDoer = Doer(self.onControlHelp).AddHelpElement('Control-Help:Statistical-Noise-Control-Help').AddToolTip('Get help on a control')
        # ------
        self.EscapeDoer = Doer(self.onEscape).AddKeyBindElement(self,'<Escape>').DisableHelp()

        # The menu system
        TheMenu=tk.Menu(self)
        self.TheMenu=TheMenu
        self.config(menu=TheMenu)
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
        self.LogScaleDoer.AddCheckButtonMenuElement(ViewMenu,label='Log Frequency Scale',underline=0)
        self.LogScaleDoer.Set(SignalIntegrity.App.Preferences['SParameterProperties.Plot.LogScale'])
        self.NoiseMeasurementsDoer.AddMenuElement(ViewMenu,label='Noise Measurements',underline=0)
        # ------
        HelpMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Help',menu=HelpMenu,underline=0)
        self.HelpDoer.AddMenuElement(HelpMenu,label='Open Help File',underline=0)
        self.ControlHelpDoer.AddMenuElement(HelpMenu,label='Control Help',underline=0)

        # The Toolbar
        ToolBarFrame = tk.Frame(self)
        ToolBarFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        iconsdir=SignalIntegrity.App.IconsDir+''
        self.HelpDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'help-contents-5.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.ControlHelpDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'help-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)

        self.statusbar=StatusBar(self,displayScale=self.displayScale)
        self.statusbar.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        labelFrame = tk.Frame(self)
        labelFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.plotLabel = tk.Label(labelFrame,fg='black')
        plotLabelPadding=round(3*self.displayScale) if self.displayScale > 1.0 else 0
        self.plotLabel.pack(fill=tk.X,pady=plotLabelPadding)

        plotWidth=SignalIntegrity.App.Preferences['Appearance.PlotWidth']
        plotHeight=SignalIntegrity.App.Preferences['Appearance.PlotHeight']
        plotDPI=SignalIntegrity.App.Preferences['Appearance.PlotDPI']

        self.f = Figure(figsize=(plotWidth,plotHeight), dpi=plotDPI)

        self.plt = self.f.add_subplot(111)
        self.plt.set_xlabel('frequency')
        self.plt.set_ylabel('magnitude')

        self.canvas = FigureCanvasTkAgg(self.f, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        toolbar = NavigationToolbar2Tk( self.canvas, self )
        toolbar.update()
        toolbar.pan()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        controlsFrame = tk.Frame(self)
        tk.Button(controlsFrame,text='autoscale',command=self.onAutoscale).pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        controlsFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)

        self.ExamineTransferMatricesDoer.Activate(False)
        self.SimulateDoer.Activate(False)
        self.NoiseMeasurementsDoer.Activate(False)
        self.ZoomsInitialized=False

        self.geometry("%+d%+d" % (self.parent.parent.root.winfo_x()+self.parent.parent.root.winfo_width()//2-self.winfo_width()//2,
            self.parent.parent.root.winfo_y()+self.parent.parent.root.winfo_height()//2-self.winfo_height()//2))

        self.lift()
        self.attributes('-topmost',True)
        self.after_idle(self.attributes,'-topmost',False)

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

    def onHelp(self):
        if Doer.helpKeys is None:
            messagebox.showerror('Help System','Cannot find or open this help element')
            return
        Doer.helpKeys.Open('sec:Statistical-Noise-Dialog')

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

    def PlotWaveformsFrequencyContent(self):
        self.lift(self.parent.parent)
        self.plt.cla()

        if not SignalIntegrity.App.Preferences['Appearance.PlotCursorValues']:
            self.plt.format_coord = lambda x, y: ''

        if not self.waveformList == None:
            self.plt.autoscale(False)

        self.frequencyContentList=[wf for wf in self.waveformList]

        minv=None
        maxv=None
        # frequency range placeholders
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

            if self.LogScaleDoer.Bool():
                if self.minx <= 0.:
                    if max(fcFrequencies)>0:
                        for value in fcFrequencies:
                            if value>0.:
                                self.minx=value/freqLabelDivisor
                                break

            if self.minx != None:
                self.plt.set_xlim(left=self.minx)

            if self.maxx != None:
                self.plt.set_xlim(right=self.maxx)

        self.plotLabel.config(text='Spectral Density')
        self.plt.set_ylabel('magnitude (dBm/'+freqLabel+')',fontsize=10)

        # Fixed thresholds for display range calculation
        # LowerLimit: only consider spectral density values above this limit (dBm/Hz)
        # DisplayAbout: add this margin (in dB) above and below the measured min/max
        LowerLimit = -200.0
        DisplayAbout = 1.0

        # We'll compute both filtered (values > LowerLimit) min/max and overall min/max
        minv_filtered = None
        maxv_filtered = None
        minv_all = None
        maxv_all = None

        for wfi in range(len(self.frequencyContentList)):
            fc=self.frequencyContentList[wfi]
            fcFrequencies=fc.Frequencies(freqLabelDivisor)
            if len(fcFrequencies)==0:
                continue

            adder=10.*math.log10(freqLabelDivisor)
            fcValues=[v+adder for v in fc.Values('dBmPerHz')]

            # update overall min/max
            minv_all = min(fcValues) if minv_all is None else min(minv_all, min(fcValues))
            maxv_all = max(fcValues) if maxv_all is None else max(maxv_all, max(fcValues))

            # update filtered min/max considering only values above LowerLimit
            filtered = [v for v in fcValues if v > LowerLimit]
            if len(filtered) > 0:
                minv_filtered = min(filtered) if minv_filtered is None else min(minv_filtered, min(filtered))
                maxv_filtered = max(filtered) if maxv_filtered is None else max(maxv_filtered, max(filtered))

            fcName=str(self.waveformNamesList[wfi])
            fcColor=self.waveformColorIndexList[wfi]

            if self.LogScaleDoer.Bool():
                self.plt.semilogx(fcFrequencies,fcValues,label=fcName,c=fcColor)
            else:
                self.plt.plot(fcFrequencies,fcValues,label=fcName,c=fcColor)

        self.plt.set_xlabel('frequency ('+freqLabel+')',fontsize=10)
        labelSpacing=0.5 if sys.platform.startswith('linux') and self.displayScale > 1.0 else 0.1
        self.plt.legend(loc='upper right',labelspacing=labelSpacing)

        # Choose filtered min/max if available, otherwise fall back to overall min/max
        if minv_filtered is not None and maxv_filtered is not None:
            minv = minv_filtered
            maxv = maxv_filtered
        else:
            minv = minv_all
            maxv = maxv_all

        # Apply display margin
        if not self.ZoomsInitialized:
            if minv is not None:
                self.miny = minv - DisplayAbout
            else:
                self.miny = None
            if maxv is not None:
                self.maxy = maxv + DisplayAbout
            else:
                self.maxy = None

        if self.miny != None:
            self.plt.set_ylim(bottom=self.miny)
        if self.maxy != None:
            self.plt.set_ylim(top=self.maxy)

        if self.ShowGridsDoer.Bool():
            self.plt.grid(True, 'both')

        self.ZoomsInitialized=True
        self.f.canvas.draw()

        self.plt.callbacks.connect('xlim_changed', self.onXLimitChange)
        self.plt.callbacks.connect('ylim_changed', self.onYLimitChange)

        return self

    def UpdateNoiseSpectralDensities(self,statistical_noise_analysis,waveformTypes=None):
        # waveformTypes is either None, or a list of strings per waveform where each element is either 'dots' or 'lines'
        self.statistical_noise_analysis=statistical_noise_analysis
        self.totalwaveformTypesList=waveformTypes
        # ------
        # Only the outputs designated for display (via each probe's 'include in
        # noise' property) are shown in the plots.  Eye probes with the property
        # turned off remain in the results dictionary (for the eye diagrams) but
        # are omitted here.  displayIndexList maps each displayed selection back
        # to its index in the full output_names / spectral density lists.
        output_names=self.statistical_noise_analysis['output_names']
        displayNames=self.statistical_noise_analysis.get('noise_display_output_names',output_names)
        self.displayIndexList=[oi for oi in range(len(output_names)) if output_names[oi] in displayNames]
        # ------
        self.SelectionDoerList = [Doer(lambda x=s: self.onSelection(x)) for s in range(len(self.displayIndexList))]
        # ------
        # ------
        self.SelectionMenu.delete(5, tk.END)
        for s in range(len(self.displayIndexList)):
            self.SelectionDoerList[s].AddCheckButtonMenuElement(self.SelectionMenu,label=output_names[self.displayIndexList[s]])
            self.SelectionDoerList[s].Set(True)
        self.TheMenu.entryconfigure('Selection', state= tk.DISABLED if len(self.displayIndexList) <= 1 else tk.ACTIVE)
        self.NoiseMeasurementsDoer.Activate(len(self.displayIndexList) > 0)
        # ------
        self.onSelection()
        if hasattr(self,'noiseMeasurementsDialog'):
            if self.noiseMeasurementsDialog != None:
                if self.noiseMeasurementsDialog.winfo_exists():
                    self.StatisticalNoiseMeasurementsDialog().UpdateMeasurements(self.statistical_noise_analysis)
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
        self.waveformTypesList=[]
        import matplotlib
        colors=matplotlib.pyplot.rcParams['axes.prop_cycle'].by_key()['color']
        for seli in range(len(self.SelectionDoerList)):
            if self.SelectionDoerList[seli].Bool():
                oi=self.displayIndexList[seli]
                self.waveformList.append(self.statistical_noise_analysis['output_noise_spectral_density_list'][oi])
                self.waveformNamesList.append(self.statistical_noise_analysis['output_names'][oi])
                self.waveformColorIndexList.append(colors[oi%len(colors)])
                self.waveformTypesList.append(self.totalwaveformTypesList[oi] if self.totalwaveformTypesList != None else 'lines')

        if len(self.waveformList) == 1:
            fl = si.fd.FrequencyList(self.waveformList[0].Frequencies())
            if fl.CheckEvenlySpaced():
                sd = self.statistical_noise_analysis['output_noise_spectral_density'][self.waveformNamesList[0]]
                # select the display units based on the probe type: a current
                # probe reports Arms / Arms/sqrt(Hz), a voltage probe reports
                # Vrms / Vrms/sqrt(Hz).
                probe_type = sd.get('type','voltage')
                if probe_type == 'current':
                    rms_units = 'Arms'
                    density_hz_units = 'Arms/sqrt(Hz)'
                    density_ghz_units = 'Arms/sqrt(GHz)'
                else:
                    rms_units = 'Vrms'
                    density_hz_units = 'Vrms/sqrt(Hz)'
                    density_ghz_units = 'Vrms/sqrt(GHz)'
                integrated_noise_dBm = sd['dBm']
                integrated_noise_rms = sd['rms']
                noise_density_dBmPerHz = sd['dBm/Hz']
                noise_density_dBmPerGHz = sd['dBm/GHz']
                noise_density_rmsPerRootHz = sd['rms/sqrt(Hz)']
                noise_density_rmsPerRootGHz = sd['rms/sqrt(GHz)']
                try:
                    signal_spectral_density = self.statistical_noise_analysis['signal_noise_spectral_density'][self.waveformNamesList[0]]
                    integrated_signal_noise_dBm = signal_spectral_density['dBm']
                    integrated_signal_noise_rms = signal_spectral_density['rms']
                    signal_noise_string = f"Signal power:  {ToSI(integrated_signal_noise_rms,rms_units,round=3)}, {ToSI(integrated_signal_noise_dBm,'dBm',round=3)}\n"
                    snr_values = self.statistical_noise_analysis['signal_to_noise_ratio'][self.waveformNamesList[0]]
                    signal_noise_string+= (
                        f"Total noise: {ToSI(integrated_noise_rms,rms_units,round=3)}, "
                        f"{ToSI(integrated_noise_dBm,'dBm',round=3)}, "
                        f"SNR: {ToSI(integrated_signal_noise_dBm-integrated_noise_dBm,'dB',round=3)}, "
                        f"Salz SNR: {ToSI(snr_values['SalzSNR'],'dB',round=3)}\n")
                except:
                    signal_noise_string = ''
                noise_string = f"Total noise: {ToSI(integrated_noise_rms,rms_units,round=3)}, {ToSI(integrated_noise_dBm,'dBm',round=3)}\n"
                noise_string += signal_noise_string
                noise_string += f"Average noise density: {ToSI(noise_density_rmsPerRootGHz,density_ghz_units,round=3)}, "
                noise_string += f"{ToSI(noise_density_dBmPerGHz,'dBm/GHz',round=3)}\n"
                noise_string += 'or:\n'
                noise_string += f"{ToSI(noise_density_rmsPerRootHz,density_hz_units,round=3)}, "
                noise_string += f"{ToSI(noise_density_dBmPerHz,'dBm/Hz',round=3)}"
                self.statusbar.set(f"{ToSI(fl.N,'Pts')} (+1) from DC to {ToSI(fl.Fe,'Hz')}, evenly spaced\n{noise_string}")
            else:
                self.statusbar.set(f"{ToSI(len(fl),'Pts')} from {ToSI(fl[0],'Hz')} to {ToSI(fl[-1],'Hz')}, unevenly spaced")
        elif len(self.waveformList) == 0:
            self.statusbar.set('No Waveforms')
        else:
            self.statusbar.set('Multiple Waveforms')

        self.PlotWaveformsFrequencyContent()

        return self

    def onShowGrids(self):
        SignalIntegrity.App.Preferences['Appearance.GridsOnPlots']=self.ShowGridsDoer.Bool()
        SignalIntegrity.App.Preferences.SaveToFile()
        self.onSelection()

    def onLogScale(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.LogScale']=self.LogScaleDoer.Bool()
        SignalIntegrity.App.Preferences.SaveToFile()
        self.onSelection()

    def onCalculationProperties(self):
        self.parent.parent.onCalculationProperties()

    def onExamineTransferMatrices(self):
        buttonLabelList=[[out+' due to '+inp for inp in self.statistical_noise_analysis['input_names']] for out in self.statistical_noise_analysis['output_names']]
        maxLength=len(max([item for sublist in buttonLabelList for item in sublist],key=len))
        buttonLabelList=[[item.ljust(maxLength) for item in sublist] for sublist in buttonLabelList]
        sp=self.statistical_noise_analysis['transfer_matrices'].SParameters()
        from SignalIntegrity.App.SParameterViewerWindow import SParametersDialog
        SParametersDialog(self.parent.parent,sp,
                          self.parent.parent.fileparts.FullFilePathExtension('s'+str(sp.m_P)+'p'),
                          'Noise Transfer Parameters',buttonLabelList,showBottomPlots=False)

    def StatisticalNoiseMeasurementsDialog(self):
        if not hasattr(self,'noiseMeasurementsDialog'):
            self.noiseMeasurementsDialog=StatisticalNoiseMeasurementsDialog(self)
        if self.noiseMeasurementsDialog == None:
            self.noiseMeasurementsDialog=StatisticalNoiseMeasurementsDialog(self)
        else:
            if not self.noiseMeasurementsDialog.winfo_exists():
                self.noiseMeasurementsDialog=StatisticalNoiseMeasurementsDialog(self)
        return self.noiseMeasurementsDialog

    def onNoiseMeasurements(self):
        windowOpen=hasattr(self,'noiseMeasurementsDialog')\
            and (self.noiseMeasurementsDialog != None)\
            and bool(self.noiseMeasurementsDialog.winfo_exists())
        if not windowOpen:
            self.StatisticalNoiseMeasurementsDialog().UpdateMeasurements(self.statistical_noise_analysis)
        self.StatisticalNoiseMeasurementsDialog().lift()
