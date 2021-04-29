"""
SParameterViewerWindow.py
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
    from tkinter import  messagebox

import matplotlib
import math

from SignalIntegrity.App.PartProperty import PartPropertyDelay,PartPropertyReferenceImpedance
from SignalIntegrity.App.Files import FileParts
from SignalIntegrity.App.MenuSystemHelpers import Doer,StatusBar
from SignalIntegrity.App.FilePicker import AskOpenFileName,AskSaveAsFilename
from SignalIntegrity.App.ToSI import ToSI,FromSI
from SignalIntegrity.App.SParameterProperties import SParameterProperties,SParameterPlotsConfiguration
from SignalIntegrity.App.SParameterPropertiesDialog import SParameterPropertiesDialog
from SignalIntegrity.App.InformationMessage import InformationMessage
from SignalIntegrity.App.CalculationPropertiesProject import CalculationPropertySI
from SignalIntegrity.App.SParameterViewerPreferencesDialog import SParameterViewerPreferencesDialog

import SignalIntegrity.App.Project

import SignalIntegrity.Lib as si

if not 'matplotlib.backends' in sys.modules:
    matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

from matplotlib.figure import Figure
from matplotlib.collections import LineCollection

from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

class NavigationToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, window,homeCallback=None):
        NavigationToolbar2Tk.__init__(self,canvas,window)
        self.homeCallback=homeCallback
    def home(self, *args):
        if not self.homeCallback is None:
            self.homeCallback()

class SParametersDialog(tk.Toplevel):
    def __init__(self, parent,sp,filename=None,title=None,buttonLabels=None):
        tk.Toplevel.__init__(self, parent)
        self.parent=parent
        self.withdraw()

        self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        self.protocol("WM_DELETE_WINDOW", self.onClosing)

        # the Doers - the holder of the commands, menu elements, toolbar elements, and key bindings
        self.ReadSParametersFromFileDoer = Doer(self.onReadSParametersFromFile).AddKeyBindElement(self,'<Control-o>').AddHelpElement('Control-Help:Open-S-parameter-File').AddToolTip('Open s-parameter file')
        self.WriteSParametersToFileDoer = Doer(self.onWriteSParametersToFile).AddKeyBindElement(self,'<Control-s>').AddHelpElement('Control-Help:Save-S-parameter-File').AddToolTip('Save s-parameters to file')
        self.Matplotlib2tikzDoer = Doer(self.onMatplotlib2TikZ).AddToolTip('Output plots to LaTeX files')
        # ------
        self.CalculationPropertiesDoer = Doer(self.onCalculationProperties).AddHelpElement('Control-Help:Calculation-Properties').AddToolTip('Edit calculation properties')
        self.SParameterPropertiesDoer = Doer(self.onSParameterProperties).AddHelpElement('Control-Help:S-Parameter-Properties').AddToolTip('Edit s-parameter properties')
        self.EnforcePassivityDoer = Doer(self.onEnforcePassivity).AddHelpElement('Control-Help:Enforce-Passivity').AddToolTip('Enforce passivity on s-parameters')
        self.EnforceCausalityDoer = Doer(self.onEnforceCausality).AddHelpElement('Control-Help:Enforce-Causality').AddToolTip('Enforce causality on s-parameters')
        self.EnforceBothPassivityAndCausalityDoer = Doer(self.onEnforceBothPassivityAndCausality).AddHelpElement('Control-Help:Enforce-Both-Passivity-and-Reciprocity').AddToolTip('Enforce passivity and reciprocity on s-parameters')
        self.EnforceReciprocityDoer = Doer(self.onEnforceReciprocity).AddHelpElement('Control-Help:Enforce-Reciprocity').AddToolTip('Enforce reciprocity on s-parameters')
        self.EnforceAllDoer = Doer(self.onEnforceAll).AddHelpElement('Control-Help:Enforce-All').AddToolTip('Enforce passivity, reciprocity, and causality on s-parameters')
        self.WaveletDenoiseDoer = Doer(self.onWaveletDenoise).AddHelpElement('Control-Help:Wavelet-Denoise').AddToolTip('Denoise s-parameters with wavelets')
        # ------
        self.HelpDoer = Doer(self.onHelp).AddHelpElement('Control-Help:S-Parameter-Viewer-Open-Help-File').AddToolTip('Open the help system in a browser')
        self.ControlHelpDoer = Doer(self.onControlHelp).AddHelpElement('Control-Help:S-Parameter-Viewer-Control-Help').AddToolTip('Get help on a control')
        self.PreferencesDoer=Doer(self.onPreferences).AddHelpElement('Control-Help:S-Parameter-Viewer-Preferences').AddToolTip('Edit the preferences')
        # ------
        self.ShowGridsDoer = Doer(self.onShowGrids).AddHelpElement('Control-Help:Show-Grids').AddToolTip('Show grids in plots')
        self.VariableLineWidthDoer = Doer(self.onVariableLineWidth).AddHelpElement('Control-Help:Variable-Line-Width').AddToolTip('Variable line width in plots')
        self.ShowPassivityViolationsDoer = Doer(self.onShowPassivityViolations).AddHelpElement('Control-Help:Show-Passivity-Violations').AddToolTip('Show passivity violations in plots')
        self.ShowCausalityViolationsDoer = Doer(self.onShowCausalityViolations).AddHelpElement('Control-Help:Show-Causality-Violations').AddToolTip('Show causality violations in plots')
        self.ShowImpedanceDoer = Doer(self.onShowImpedance).AddHelpElement('Control-Help:Show-Impedance').AddToolTip('Show impedance plots')
        self.ShowExcessInductanceDoer = Doer(self.onShowExcessInductance).AddHelpElement('Control-Help:Show-Excess-Inductance').AddToolTip('Show excess inductance in plots')
        self.ShowExcessCapacitanceDoer = Doer(self.onShowExcessCapacitance).AddHelpElement('Control-Help:Show-Excess-Capacitance').AddToolTip('Show excess capacitance in plots')
        self.LogScaleDoer = Doer(self.onLogScale).AddHelpElement('Control-Help:Log-Scale').AddToolTip('Show frequency plots log scale')
        self.LinearVerticalScaleDoer = Doer(self.onLinearVerticalScale).AddHelpElement('Control-Help:Linear-Vertical-Scale').AddToolTip('Show frequency plots linear vertical scale')
        # ------
        self.Zoom={
            'AreSParameterLike':False,
            'Frequencies':{
                'JoinWithin':Doer(self.onJoinFrequenciesWithin).AddHelpElement('Control-Help:S-Parameter-Viewer-Frequency-Zoom'),
                'JoinWithOthers':Doer(self.onJoinFrequenciesWithOthers).AddHelpElement('Control-Help:S-Parameter-Viewer-Frequency-Zoom'),
                'Join':{
                    'All':Doer(self.onFrequenciesJoinAll).AddHelpElement('Control-Help:S-Parameter-Viewer-Frequency-Zoom'),
                    'OffDiagonal':Doer(self.onFrequenciesJoinOffDiagonal).AddHelpElement('Control-Help:S-Parameter-Viewer-Frequency-Zoom'),
                    'Reciprocals':Doer(self.onFrequenciesJoinReciprocals).AddHelpElement('Control-Help:S-Parameter-Viewer-Frequency-Zoom'),
                    'Reflects':Doer(self.onFrequenciesJoinReflects).AddHelpElement('Control-Help:S-Parameter-Viewer-Frequency-Zoom')
                }},
            'Times':{
                'JoinWithin':Doer(self.onJoinTimesWithin).AddHelpElement('Control-Help:S-Parameter-Viewer-Time-Zoom'),
                'JoinWithOthers':Doer(self.onJoinTimesWithOthers).AddHelpElement('Control-Help:S-Parameter-Viewer-Time-Zoom'),
                'Join':{
                    'All':Doer(self.onTimesJoinAll).AddHelpElement('Control-Help:S-Parameter-Viewer-Time-Zoom'),
                    'OffDiagonal':Doer(self.onTimesJoinOffDiagonal).AddHelpElement('Control-Help:S-Parameter-Viewer-Time-Zoom'),
                    'Reciprocals':Doer(self.onTimesJoinReciprocals).AddHelpElement('Control-Help:S-Parameter-Viewer-Time-Zoom'),
                    'Reflects':Doer(self.onTimesJoinReflects).AddHelpElement('Control-Help:S-Parameter-Viewer-Time-Zoom')
                }},
            'Vertical':{
                'JoinMagnitudeWithOthers':Doer(self.onJoinMagnitudeWithOthers).AddHelpElement('Control-Help:S-Parameter-Viewer-Vertical-Zoom'),
                'JoinPhaseWithOthers':Doer(self.onJoinPhaseWithOthers).AddHelpElement('Control-Help:S-Parameter-Viewer-Vertical-Zoom'),
                'JoinImpulseWithOthers':Doer(self.onJoinImpulseWithOthers).AddHelpElement('Control-Help:S-Parameter-Viewer-Vertical-Zoom'),
                'JoinStepImpedanceWithOthers':Doer(self.onJoinStepImpedanceWithOthers).AddHelpElement('Control-Help:S-Parameter-Viewer-Vertical-Zoom'),
                'Join':{
                    'All':Doer(self.onVerticalJoinAll).AddHelpElement('Control-Help:S-Parameter-Viewer-Vertical-Zoom'),
                    'OffDiagonal':Doer(self.onVerticalJoinOffDiagonal).AddHelpElement('Control-Help:S-Parameter-Viewer-Vertical-Zoom'),
                    'Reciprocals':Doer(self.onVerticalJoinReciprocals).AddHelpElement('Control-Help:S-Parameter-Viewer-Vertical-Zoom'),
                    'Reflects':Doer(self.onVerticalJoinReflects).AddHelpElement('Control-Help:S-Parameter-Viewer-Vertical-Zoom')
            }}}
        #-------
        self.EscapeDoer = Doer(self.onEscape).AddKeyBindElement(self,'<Escape>').DisableHelp()

        # The menu system
        TheMenu=tk.Menu(self)
        self.config(menu=TheMenu)
        # ------
        FileMenu=tk.Menu(self)
        TheMenu.add_cascade(label='File',menu=FileMenu,underline=0)
        self.WriteSParametersToFileDoer.AddMenuElement(FileMenu,label="Save",accelerator='Ctrl+S',underline=0)
        self.ReadSParametersFromFileDoer.AddMenuElement(FileMenu,label="Open File",accelerator='Ctrl+O',underline=0)
        FileMenu.add_separator()
        self.Matplotlib2tikzDoer.AddMenuElement(FileMenu,label='Output to LaTeX (TikZ)',underline=10)
        # ------
        self.SelectionMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Selection',menu=self.SelectionMenu,underline=0)
        # ------
        PropertiesMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Properties',menu=PropertiesMenu,underline=0)
        #self.CalculationPropertiesDoer.AddMenuElement(PropertiesMenu,label='Calculation Properties',underline=0)
        self.SParameterPropertiesDoer.AddMenuElement(PropertiesMenu,label='S-parameter Properties',underline=0)
        #PropertiesMenu.add_separator()
        #PropertiesMenu.add_separator()
        self.EnforcePassivityDoer.AddMenuElement(PropertiesMenu,label='Enforce Passivity',underline=8)
        self.EnforceCausalityDoer.AddMenuElement(PropertiesMenu,label='Enforce Causality',underline=8)
        self.EnforceBothPassivityAndCausalityDoer.AddMenuElement(PropertiesMenu,label='Enforce Both Passivity and Causality',underline=8)
        self.EnforceReciprocityDoer.AddMenuElement(PropertiesMenu,label='Enforce Reciprocity',underline=8)
        self.EnforceAllDoer.AddMenuElement(PropertiesMenu,label='Enforce All',underline=8)
        self.WaveletDenoiseDoer.AddMenuElement(PropertiesMenu,label='Wavelet Denoise',underline=0)
        # ------
        ViewMenu=tk.Menu(self)
        TheMenu.add_cascade(label='View',menu=ViewMenu,underline=0)
        self.ShowGridsDoer.AddCheckButtonMenuElement(ViewMenu,label='Show Grids',underline=5)
        self.VariableLineWidthDoer.AddCheckButtonMenuElement(ViewMenu,label='Variable Line Width',underline=9)
        self.ShowPassivityViolationsDoer.AddCheckButtonMenuElement(ViewMenu,label='Show Passivity Violations',underline=5)
        self.ShowCausalityViolationsDoer.AddCheckButtonMenuElement(ViewMenu,label='Show Causality Violations',underline=6)
        self.ShowImpedanceDoer.AddCheckButtonMenuElement(ViewMenu,label='Show Impedance',underline=5)
        self.ShowExcessInductanceDoer.AddCheckButtonMenuElement(ViewMenu,label='Show Excess Inductance',underline=13)
        self.ShowExcessCapacitanceDoer.AddCheckButtonMenuElement(ViewMenu,label='Show Excess Capacitance',underline=12)
        self.LogScaleDoer.AddCheckButtonMenuElement(ViewMenu,label='Log Scale',underline=4)
        self.LinearVerticalScaleDoer.AddCheckButtonMenuElement(ViewMenu,label='Linear Vertical Scale',underline=8)
        #-------
        ZoomMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Zoom',menu=ZoomMenu,underline=0)
        ZoomFrequenciesMenu=tk.Menu(self)
        ZoomMenu.add_cascade(label='Frequencies',menu=ZoomFrequenciesMenu,underline=0)
        self.Zoom['Frequencies']['JoinWithin'].AddCheckButtonMenuElement(ZoomFrequenciesMenu,label='Join Within Views',underline=5)
        ZoomFrequenciesMenu.add_separator()
        self.Zoom['Frequencies']['JoinWithOthers'].AddCheckButtonMenuElement(ZoomFrequenciesMenu,label='Join With Other Views',underline=10)
        ZoomFrequenciesMenu.add_separator()
        self.Zoom['Frequencies']['Join']['All'].AddCheckButtonMenuElement(ZoomFrequenciesMenu,label='Join All Views',underline=5)
        self.Zoom['Frequencies']['Join']['OffDiagonal'].AddCheckButtonMenuElement(ZoomFrequenciesMenu,label='Join Off-Diagnonal Views',underline=9)
        self.Zoom['Frequencies']['Join']['Reciprocals'].AddCheckButtonMenuElement(ZoomFrequenciesMenu,label='Join Reciprocal Views',underline=5)
        self.Zoom['Frequencies']['Join']['Reflects'].AddCheckButtonMenuElement(ZoomFrequenciesMenu,label='Join Reflect Views',underline=7)
        ZoomTimesMenu=tk.Menu(self)
        ZoomMenu.add_cascade(label='Times',menu=ZoomTimesMenu,underline=0)
        self.Zoom['Times']['JoinWithin'].AddCheckButtonMenuElement(ZoomTimesMenu,label='Join Within Views',underline=5)
        ZoomTimesMenu.add_separator()
        self.Zoom['Times']['JoinWithOthers'].AddCheckButtonMenuElement(ZoomTimesMenu,label='Join With Other Views',underline=10)
        ZoomTimesMenu.add_separator()
        self.Zoom['Times']['Join']['All'].AddCheckButtonMenuElement(ZoomTimesMenu,label='Join All Views',underline=5)
        self.Zoom['Times']['Join']['OffDiagonal'].AddCheckButtonMenuElement(ZoomTimesMenu,label='Join Off-Diagnonal Views',underline=9)
        self.Zoom['Times']['Join']['Reciprocals'].AddCheckButtonMenuElement(ZoomTimesMenu,label='Join Reciprocal Views',underline=5)
        self.Zoom['Times']['Join']['Reflects'].AddCheckButtonMenuElement(ZoomTimesMenu,label='Join Reflect Views',underline=7)
        ZoomVerticalMenu=tk.Menu(self)
        ZoomMenu.add_cascade(label='Vertical',menu=ZoomVerticalMenu,underline=0)
        self.Zoom['Vertical']['JoinMagnitudeWithOthers'].AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join Magnitude Zooms With Other Views',underline=None)
        self.Zoom['Vertical']['JoinPhaseWithOthers'].AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join Phase Zooms With Other Views',underline=None)
        self.Zoom['Vertical']['JoinImpulseWithOthers'].AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join Impulse Response Zooms With Other Views',underline=None)
        self.Zoom['Vertical']['JoinStepImpedanceWithOthers'].AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join Step Response/Impedance Zooms With Other Views',underline=None)
        ZoomVerticalMenu.add_separator()
        self.Zoom['Vertical']['Join']['All'].AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join All Views',underline=5)
        self.Zoom['Vertical']['Join']['OffDiagonal'].AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join Off-Diagnonal Views',underline=9)
        self.Zoom['Vertical']['Join']['Reciprocals'].AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join Reciprocal Views',underline=5)
        self.Zoom['Vertical']['Join']['Reflects'].AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join Reflect Views',underline=7)
        # ------
        HelpMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Help',menu=HelpMenu,underline=0)
        self.HelpDoer.AddMenuElement(HelpMenu,label='Open Help File',underline=0)
        self.ControlHelpDoer.AddMenuElement(HelpMenu,label='Control Help',underline=0)
        self.PreferencesDoer.AddMenuElement(HelpMenu,label='Preferences',underline=0)
        self.TheMenu=TheMenu

        # The Toolbar
        ToolBarFrame = tk.Frame(self)
        ToolBarFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.ReadSParametersFromFileDoer.AddToolBarElement(ToolBarFrame,iconfile=SignalIntegrity.App.IconsDir+'document-open-2.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.WriteSParametersToFileDoer.AddToolBarElement(ToolBarFrame,iconfile=SignalIntegrity.App.IconsDir+'document-save-2.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        tk.Frame(ToolBarFrame,height=2,bd=2,relief=tk.RAISED).pack(side=tk.LEFT,fill=tk.X,padx=5,pady=5)
        self.SParameterPropertiesDoer.AddToolBarElement(ToolBarFrame,iconfile=SignalIntegrity.App.IconsDir+'tooloptions.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        tk.Frame(ToolBarFrame,height=2,bd=2,relief=tk.RAISED).pack(side=tk.LEFT,fill=tk.X,padx=5,pady=5)
        self.HelpDoer.AddToolBarElement(ToolBarFrame,iconfile=SignalIntegrity.App.IconsDir+'help-contents-5.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.ControlHelpDoer.AddToolBarElement(ToolBarFrame,iconfile=SignalIntegrity.App.IconsDir+'help-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)

        self.dialogFrame = tk.Frame(self, borderwidth=5)
        self.dialogFrame.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)

        self.statusbar=StatusBar(self.dialogFrame)
        self.statusbar.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)

        topFrame=tk.Frame(self.dialogFrame)
        topFrame.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)
        bottomFrame=tk.Frame(self.dialogFrame)
        bottomFrame.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)
        topLeftFrame=tk.Frame(topFrame)
        topLeftFrame.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES)
        self.topLeftLabel = tk.Label(topLeftFrame,fg='black')
        self.topLeftLabel.pack(fill=tk.X)
        topRightFrame=tk.Frame(topFrame)
        topRightFrame.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES)
        self.topRightLabel = tk.Label(topRightFrame,fg='black')
        self.topRightLabel.pack(fill=tk.X)
        bottomLeftFrame=tk.Frame(bottomFrame)
        bottomLeftFrame.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES)
        self.bottomLeftLabel = tk.Label(bottomLeftFrame,fg='black')
        self.bottomLeftLabel.pack(fill=tk.X)
        bottomRightFrame=tk.Frame(bottomFrame)
        bottomRightFrame.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES)
        self.bottomRightlabel = tk.Label(bottomRightFrame,fg='black')
        self.bottomRightlabel.pack(fill=tk.X)

        plotWidth=SignalIntegrity.App.Preferences['Appearance.PlotWidth']
        plotHeight=SignalIntegrity.App.Preferences['Appearance.PlotHeight']
        plotDPI=SignalIntegrity.App.Preferences['Appearance.PlotDPI']

        self.topLeftFigure=Figure(figsize=(plotWidth,plotHeight), dpi=plotDPI)
        self.topLeftPlot=self.topLeftFigure.add_subplot(111)
        self.topLeftCanvas=FigureCanvasTkAgg(self.topLeftFigure, master=topLeftFrame)
        self.topLeftCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=1)
        self.topLeftToolbar = NavigationToolbar( self.topLeftCanvas, topLeftFrame ,self.onTopLeftHome)
        self.topLeftToolbar.update()
        self.topLeftCanvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.topLeftToolbar.pan()

        self.topRightFigure=Figure(figsize=(plotWidth,plotHeight), dpi=plotDPI)
        self.topRightPlot=self.topRightFigure.add_subplot(111)
        self.topRightCanvas=FigureCanvasTkAgg(self.topRightFigure, master=topRightFrame)
        self.topRightCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=1)
        self.topRightToolbar = NavigationToolbar( self.topRightCanvas, topRightFrame ,self.onTopRightHome)
        self.topRightToolbar.update()
        self.topRightCanvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.topRightToolbar.pan()
        self.topRightCanvasControlsFrame=tk.Frame(topRightFrame)
        self.topRightCanvasControlsFrame.pack(side=tk.TOP, fill=tk.X, expand=tk.NO)
        tk.Button(self.topRightCanvasControlsFrame,text='unwrap',command=self.onUnwrap).pack(side=tk.LEFT,expand=tk.NO,fill=tk.NONE)
        self.delayViewerProperty=CalculationPropertySI(self.topRightCanvasControlsFrame,'Delay',self.onDelayEntered,None,None,None,'s')
        self.delayViewerProperty.label.config(width=10)

        self.bottomLeftFigure=Figure(figsize=(plotWidth,plotHeight), dpi=plotDPI)
        self.bottomLeftPlot=self.bottomLeftFigure.add_subplot(111)
        self.bottomLeftCanvas=FigureCanvasTkAgg(self.bottomLeftFigure, master=bottomLeftFrame)
        self.bottomLeftCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=1)
        self.bottomLeftToolbar = NavigationToolbar( self.bottomLeftCanvas, bottomLeftFrame ,self.onBottomLeftHome)
        self.bottomLeftToolbar.update()
        self.bottomLeftCanvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.bottomLeftToolbar.pan()

        self.bottomRightFigure=Figure(figsize=(plotWidth,plotHeight), dpi=plotDPI)
        self.bottomRightPlot=self.bottomRightFigure.add_subplot(111)
        self.bottomRightCanvas=FigureCanvasTkAgg(self.bottomRightFigure, master=bottomRightFrame)
        self.bottomRightCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=1)
        self.bottomRightToolbar = NavigationToolbar( self.bottomRightCanvas, bottomRightFrame , self.onBottomRightHome)
        self.bottomRightToolbar.update()
        self.bottomRightCanvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.bottomRightToolbar.pan()

        self.controlsFrame = tk.Frame(self.dialogFrame)
        self.controlsFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.sButtonsFrame = tk.Frame(self.controlsFrame, bd=1, relief=tk.SUNKEN)
        self.sButtonsFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.NONE)

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

        self.NewSParameters(sp,filename,title,buttonLabels)
        self.deiconify()

    def NewSParameters(self,sp,filename=None,title=None,buttonLabels=None):
        self.calibration=None
        if isinstance(sp,si.m.cal.Calibration):
            self.calibration=sp
            fixtureList=self.calibration.Fixtures()
            ports=len(fixtureList)
            buttonLabelsList=[None for _ in range(ports)]
            titleList=['Error Terms - Port '+str(p+1) for p in range(ports)]
            fileNameList=[filename for _ in range(ports)]
            for i in range(ports):
                buttonLabels=[[' 0  ' for _ in range(2*ports)] for _ in range(2*ports)]
                for r in range(ports):
                    buttonLabels[i+ports][i]=' 1  '
                    buttonLabels[r][i] = 'ED'+str(i+1)+' ' if r==i else 'EX'+str(r+1)+str(i+1)
                    buttonLabels[r][ports+r]='ER'+str(i+1)+' ' if r==i else 'ET'+str(r+1)+str(i+1)
                    buttonLabels[r+ports][ports+r]='ES'+str(i+1)+' ' if r==i else 'EL'+str(r+1)+str(i+1)
                buttonLabelsList[i]=buttonLabels
            sp = [(fixture,filename,title,buttonlabel) for (fixture,filename,title,buttonlabel) in zip(fixtureList,fileNameList,titleList,buttonLabelsList)]

        # handle lists of s-parameters
        if isinstance(sp,list):
            self.spList=sp
            sp=self.spList[0][0]
            filename=self.spList[0][1]
            title=self.spList[0][2]
            buttonLabels=self.spList[0][3]
        else:
            self.spList=[[sp,filename,'S-Parameters' if title == None else title,buttonLabels]]

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

        # ------
        self.SelectionDoerList = [Doer(lambda x=s: self.onSelection(x)) for s in range(len(self.spList))]
        # ------

        # ------
        self.SelectionMenu.delete(0, tk.END)
        for s in range(len(self.spList)):
            self.SelectionDoerList[s].AddMenuElement(self.SelectionMenu,label=self.spList[s][2])
        self.TheMenu.entryconfigure('Selection', state= tk.DISABLED if len(self.spList) <= 1 else tk.ACTIVE)
        # ------

        self.sp=sp
        self.properties=SParameterProperties()
        self.UpdatePreferences()
        self.UpdatePropertiesFromSParameters(new=True)

        # button labels are a proxy for transfer parameters (until I do something better)
        areSParameters=(buttonLabels == None)
        isCalibration=(self.calibration != None)
        self.ShowPassivityViolationsDoer.Activate(areSParameters)
        self.ShowCausalityViolationsDoer.Activate(areSParameters)
        self.ShowImpedanceDoer.Activate(areSParameters)
        self.ShowExcessInductanceDoer.Activate(areSParameters)
        self.ShowExcessCapacitanceDoer.Activate(areSParameters)
        #self.LogScaleDoer.Activate(False)
        self.EnforcePassivityDoer.Activate(areSParameters)
        self.EnforceCausalityDoer.Activate(areSParameters)
        self.EnforceBothPassivityAndCausalityDoer.Activate(areSParameters)
        self.EnforceReciprocityDoer.Activate(areSParameters)
        self.EnforceAllDoer.Activate(areSParameters)
        self.WaveletDenoiseDoer.Activate(areSParameters)
        self.ReadSParametersFromFileDoer.Activate(areSParameters or isCalibration)
        self.Zoom['AreSParameterLike']=(areSParameters or isCalibration)
        if buttonLabels == None:
            numPorts=self.sp.m_P
            (formatStr1,formatStr2)=('{:1d}','{:1d}') if numPorts < 10 else ('{:2d}','{:3d}') # assumes less than 100
            buttonLabels=[['s'+formatStr1.format(toP+1)+formatStr2.format(fromP+1) for fromP in range(numPorts)] for toP in range(numPorts)]
            self.spList[0][3]=buttonLabels
        else:
            if self.calibration == None:
                # @todo:  This is totally wrong to directly write the preferences to enforce this.  It ends up updating the preferences
                # behind the user's back
                self.Zoom['Times']['Join']['All'].Set(True)
                self.Zoom['Frequencies']['Join']['All'].Set(True)
                self.Zoom['Vertical']['Join']['All'].Set(True)
                self.UpdatePropertiesFromSParameters()
                self.ZoomJoinActivations()

        self.buttonLabels=buttonLabels

        self.fromPort = 1
        self.toPort = 1
        self.LimitChangeLock=False
        self.onSelection(0)

    def onShowGrids(self):
        SignalIntegrity.App.Preferences['Appearance.GridsOnPlots']=self.ShowGridsDoer.Bool()
        SignalIntegrity.App.Preferences.SaveToFile()
        self.PlotSParameter()

    def onVariableLineWidth(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.VariableLineWidth']=self.VariableLineWidthDoer.Bool()
        SignalIntegrity.App.Preferences.SaveToFile()
        self.PlotSParameter()

    def onShowPassivityViolations(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowPassivityViolations']=self.ShowPassivityViolationsDoer.Bool()
        SignalIntegrity.App.Preferences.SaveToFile()
        self.PlotSParameter()

    def onShowCausalityViolations(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowCausalityViolations']=self.ShowCausalityViolationsDoer.Bool()
        SignalIntegrity.App.Preferences.SaveToFile()
        self.PlotSParameter()

    def onShowImpedance(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowImpedance']=self.ShowImpedanceDoer.Bool()
        self.ShowExcessInductanceDoer.Set(False)
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowExcessInductance']=False
        self.ShowExcessCapacitanceDoer.Set(False)
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowExcessCapacitance']=False
        SignalIntegrity.App.Preferences.SaveToFile()
        self.PlotSParameter()

    def onShowExcessInductance(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowExcessInductance']=self.ShowExcessInductanceDoer.Bool()
        self.ShowImpedanceDoer.Set(False)
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowImpedance']=False
        self.ShowExcessCapacitanceDoer.Set(False)
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowExcessCapacitance']=False
        SignalIntegrity.App.Preferences.SaveToFile()
        self.PlotSParameter()

    def onShowExcessCapacitance(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowExcessCapacitance']=self.ShowExcessCapacitanceDoer.Bool()
        self.ShowImpedanceDoer.Set(False)
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowImpedance']=False
        self.ShowExcessInductanceDoer.Set(False)
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowExcessInductance']=False
        SignalIntegrity.App.Preferences.SaveToFile()
        self.PlotSParameter()

    def onLogScale(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.LogScale']=self.LogScaleDoer.Bool()
        SignalIntegrity.App.Preferences.SaveToFile()
        self.PlotSParameter()

    def onLinearVerticalScale(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Plot.LinearVerticalScale']=self.LinearVerticalScaleDoer.Bool()
        SignalIntegrity.App.Preferences.SaveToFile()
        self.PlotSParameter()

    def ZoomJoinActivations(self):
        self.Zoom['Frequencies']['Join']['All'].Activate(self.Zoom['Frequencies']['JoinWithOthers'].Bool())
        self.Zoom['Frequencies']['Join']['OffDiagonal'].Activate(self.Zoom['Frequencies']['JoinWithOthers'].Bool() and not self.Zoom['Frequencies']['Join']['All'].Bool() and self.Zoom['AreSParameterLike'])
        self.Zoom['Frequencies']['Join']['Reciprocals'].Activate(self.Zoom['Frequencies']['JoinWithOthers'].Bool() and not self.Zoom['Frequencies']['Join']['All'].Bool() and not self.Zoom['Frequencies']['Join']['OffDiagonal'].Bool() and self.Zoom['AreSParameterLike'])        
        self.Zoom['Frequencies']['Join']['Reflects'].Activate(self.Zoom['Frequencies']['JoinWithOthers'].Bool() and not self.Zoom['Frequencies']['Join']['All'].Bool() and self.Zoom['AreSParameterLike'])
        self.Zoom['Times']['Join']['All'].Activate(self.Zoom['Times']['JoinWithOthers'].Bool())
        self.Zoom['Times']['Join']['OffDiagonal'].Activate(self.Zoom['Times']['JoinWithOthers'].Bool() and not self.Zoom['Times']['Join']['All'].Bool() and self.Zoom['AreSParameterLike'])
        self.Zoom['Times']['Join']['Reciprocals'].Activate(self.Zoom['Times']['JoinWithOthers'].Bool() and not self.Zoom['Times']['Join']['All'].Bool() and not self.Zoom['Times']['Join']['OffDiagonal'].Bool() and self.Zoom['AreSParameterLike'])        
        self.Zoom['Times']['Join']['Reflects'].Activate(self.Zoom['Times']['JoinWithOthers'].Bool() and not self.Zoom['Times']['Join']['All'].Bool() and self.Zoom['AreSParameterLike'])
        verticalsActive = self.Zoom['Vertical']['JoinMagnitudeWithOthers'].Bool() or self.Zoom['Vertical']['JoinPhaseWithOthers'].Bool() or self.Zoom['Vertical']['JoinImpulseWithOthers'].Bool() or self.Zoom['Vertical']['JoinStepImpedanceWithOthers'].Bool()
        self.Zoom['Vertical']['Join']['All'].Activate(verticalsActive)
        self.Zoom['Vertical']['Join']['OffDiagonal'].Activate(verticalsActive and not self.Zoom['Vertical']['Join']['All'].Bool() and self.Zoom['AreSParameterLike'])
        self.Zoom['Vertical']['Join']['Reciprocals'].Activate(verticalsActive and not self.Zoom['Vertical']['Join']['All'].Bool() and not self.Zoom['Vertical']['Join']['OffDiagonal'].Bool() and self.Zoom['AreSParameterLike'])        
        self.Zoom['Vertical']['Join']['Reflects'].Activate(verticalsActive and not self.Zoom['Vertical']['Join']['All'].Bool() and self.Zoom['AreSParameterLike'])
        SignalIntegrity.App.Preferences.SaveToFile()

    def onJoinFrequenciesWithin(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Frequencies.JoinWithin']=self.Zoom['Frequencies']['JoinWithin'].Bool()
        self.ZoomJoinActivations()

    def onJoinTimesWithin(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Times.JoinWithin']=self.Zoom['Times']['JoinWithin'].Bool()
        self.ZoomJoinActivations()

    def onJoinFrequenciesWithOthers(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Frequencies.JoinWithOthers']=self.Zoom['Frequencies']['JoinWithOthers'].Bool()
        self.ZoomJoinActivations()

    def onJoinTimesWithOthers(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Times.JoinWithOthers']=self.Zoom['Times']['JoinWithOthers'].Bool()
        self.ZoomJoinActivations()

    def onJoinMagnitudeWithOthers(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.JoinMagnitudeWithOthers']=self.Zoom['Vertical']['JoinMagnitudeWithOthers'].Bool()
        self.ZoomJoinActivations()

    def onJoinPhaseWithOthers(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.JoinPhaseWithOthers']=self.Zoom['Vertical']['JoinPhaseWithOthers'].Bool()
        self.ZoomJoinActivations()

    def onJoinImpulseWithOthers(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.JoinImpulseWithOthers']=self.Zoom['Vertical']['JoinImpulseWithOthers'].Bool()
        self.ZoomJoinActivations()

    def onJoinStepImpedanceWithOthers(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.JoinStepImpedanceWithOthers']=self.Zoom['Vertical']['JoinStepImpedanceWithOthers'].Bool()
        self.ZoomJoinActivations()

    def onFrequenciesJoinAll(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Frequencies.Join.All']=self.Zoom['Frequencies']['Join']['All'].Bool()
        self.ZoomJoinActivations()

    def onFrequenciesJoinOffDiagonal(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Frequencies.Join.OffDiagonal']=self.Zoom['Frequencies']['Join']['OffDiagonal'].Bool()
        self.ZoomJoinActivations()

    def onFrequenciesJoinReciprocals(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Frequencies.Join.Reciprocals']=self.Zoom['Frequencies']['Join']['Reciprocals'].Bool()
        self.ZoomJoinActivations()

    def onFrequenciesJoinReflects(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Frequencies.Join.Reflects']=self.Zoom['Frequencies']['Join']['Reflects'].Bool()
        self.ZoomJoinActivations()

    def onTimesJoinAll(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Times.Join.All']=self.Zoom['Times']['Join']['All'].Bool()
        self.ZoomJoinActivations()

    def onTimesJoinOffDiagonal(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Times.Join.OffDiagonal']=self.Zoom['Times']['Join']['OffDiagonal'].Bool()
        self.ZoomJoinActivations()

    def onTimesJoinReciprocals(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Times.Join.Reciprocals']=self.Zoom['Times']['Join']['Reciprocals'].Bool()
        self.ZoomJoinActivations()

    def onTimesJoinReflects(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Times.Join.Reflects']=self.Zoom['Times']['Join']['Reflects'].Bool()
        self.ZoomJoinActivations()

    def onVerticalJoinAll(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.Join.All']=self.Zoom['Vertical']['Join']['All'].Bool()
        self.ZoomJoinActivations()

    def onVerticalJoinOffDiagonal(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.Join.OffDiagonal']=self.Zoom['Vertical']['Join']['OffDiagonal'].Bool()
        self.ZoomJoinActivations()

    def onVerticalJoinReciprocals(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.Join.Reciprocals']=self.Zoom['Vertical']['Join']['Reciprocals'].Bool()
        self.ZoomJoinActivations()

    def onVerticalJoinReflects(self):
        SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.Join.Reflects']=self.Zoom['Vertical']['Join']['Reflects'].Bool()
        self.ZoomJoinActivations()

    def JoinIt(self,thisToPortToJoin,thisFromPortToJoin,category):
        zoomProperties=self.Zoom[category]['Join']
        if zoomProperties['All'].Bool():
            return True
        if (thisToPortToJoin == thisFromPortToJoin) and (self.fromPort == self.toPort) and zoomProperties['Reflects'].Bool():
            return True
        if (thisToPortToJoin != thisFromPortToJoin) and (self.fromPort != self.toPort) and zoomProperties['OffDiagonal'].Bool():
            return True
        if (thisToPortToJoin == self.fromPort) and (thisFromPortToJoin == self.toPort) and zoomProperties['Reciprocals'].Bool():
            return True
        return False

    def onTopLeftXLimitChange(self,ax):
        if not self.LimitChangeLock:
            self.LimitChangeLock=True
            xlim=ax.get_xlim()
            if not self.topLeftPlotProperties is None:
                self.topLeftPlotProperties['MinX']=xlim[0]
                self.topLeftPlotProperties['MaxX']=xlim[1]
                if self.Zoom['Frequencies']['JoinWithin'].Bool():
                    self.topRightPlotProperties['MinX']=self.topLeftPlotProperties['MinX']
                    self.topRightPlotProperties['MaxX']=self.topLeftPlotProperties['MaxX']
                    self.topRightPlot.set_xlim(left=self.topRightPlotProperties['MinX'])
                    self.topRightPlot.set_xlim(right=self.topRightPlotProperties['MaxX'])
                    self.topRightCanvas.draw()
                if self.Zoom['Frequencies']['JoinWithOthers'].Bool():
                    spPlotPropertiesToJoinFrom=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
                    for thisToPort in range(1,self.sp.m_P+1):
                        for thisFromPort in range(1,self.sp.m_P+1):
                            if self.JoinIt(thisToPort,thisFromPort,'Frequencies'):
                                spPlotPropertiesToJoinTo=self.properties['Plot.S'][thisToPort-1][thisFromPort-1]
                                spPlotPropertiesToJoinTo['Magnitude.XInitialized']=True
                                spPlotPropertiesToJoinTo['Magnitude.MinX']=spPlotPropertiesToJoinFrom['Magnitude.MinX']
                                spPlotPropertiesToJoinTo['Magnitude.MaxX']=spPlotPropertiesToJoinFrom['Magnitude.MaxX']
                                if self.Zoom['Frequencies']['JoinWithin'].Bool():
                                    spPlotPropertiesToJoinTo['Phase.XInitialized']=True
                                    spPlotPropertiesToJoinTo['Phase.MinX']=spPlotPropertiesToJoinFrom['Magnitude.MinX']
                                    spPlotPropertiesToJoinTo['Phase.MaxX']=spPlotPropertiesToJoinFrom['Magnitude.MaxX']
            self.LimitChangeLock=False

    def onTopLeftYLimitChange(self,ax):
        if not self.LimitChangeLock:
            self.LimitChangeLock=True
            ylim=ax.get_ylim()
            if not self.topLeftPlotProperties is None:
                self.topLeftPlotProperties['MinY']=ylim[0]
                self.topLeftPlotProperties['MaxY']=ylim[1]
                if self.Zoom['Vertical']['JoinMagnitudeWithOthers'].Bool():
                    spPlotPropertiesToJoinFrom=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
                    for thisToPort in range(1,self.sp.m_P+1):
                        for thisFromPort in range(1,self.sp.m_P+1):
                            if self.JoinIt(thisToPort,thisFromPort,'Vertical'):
                                spPlotPropertiesToJoinTo=self.properties['Plot.S'][thisToPort-1][thisFromPort-1]
                                spPlotPropertiesToJoinTo['Magnitude.YInitialized']=True
                                spPlotPropertiesToJoinTo['Magnitude.MinY']=spPlotPropertiesToJoinFrom['Magnitude.MinY']
                                spPlotPropertiesToJoinTo['Magnitude.MaxY']=spPlotPropertiesToJoinFrom['Magnitude.MaxY']
            self.LimitChangeLock=False

    def onTopRightXLimitChange(self,ax):
        if not self.LimitChangeLock:
            self.LimitChangeLock=True
            xlim=ax.get_xlim()
            if not self.topRightPlotProperties is None:
                self.topRightPlotProperties['MinX']=xlim[0]
                self.topRightPlotProperties['MaxX']=xlim[1]
                if self.Zoom['Frequencies']['JoinWithin'].Bool():
                    self.topLeftPlotProperties['MinX']=self.topRightPlotProperties['MinX']
                    self.topLeftPlotProperties['MaxX']=self.topRightPlotProperties['MaxX']
                    self.topLeftPlot.set_xlim(left=self.topLeftPlotProperties['MinX'])
                    self.topLeftPlot.set_xlim(right=self.topLeftPlotProperties['MaxX'])
                    self.topLeftCanvas.draw()
                if self.Zoom['Frequencies']['JoinWithOthers'].Bool():
                    spPlotPropertiesToJoinFrom=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
                    for thisToPort in range(1,self.sp.m_P+1):
                        for thisFromPort in range(1,self.sp.m_P+1):
                            if self.JoinIt(thisToPort,thisFromPort,'Frequencies'):
                                spPlotPropertiesToJoinTo=self.properties['Plot.S'][thisToPort-1][thisFromPort-1]
                                spPlotPropertiesToJoinTo['Phase.XInitialized']=True
                                spPlotPropertiesToJoinTo['Phase.MinX']=spPlotPropertiesToJoinFrom['Phase.MinX']
                                spPlotPropertiesToJoinTo['Phase.MaxX']=spPlotPropertiesToJoinFrom['Phase.MaxX']
                                if self.Zoom['Frequencies']['JoinWithin'].Bool():
                                    spPlotPropertiesToJoinTo['Magnitude.XInitialized']=True
                                    spPlotPropertiesToJoinTo['Magnitude.MinX']=spPlotPropertiesToJoinFrom['Phase.MinX']
                                    spPlotPropertiesToJoinTo['Magnitude.MaxX']=spPlotPropertiesToJoinFrom['Phase.MaxX']
            self.LimitChangeLock=False

    def onTopRightYLimitChange(self,ax):
        if not self.LimitChangeLock:
            self.LimitChangeLock=True
            ylim=ax.get_ylim()
            if not self.topRightPlotProperties is None:
                self.topRightPlotProperties['MinY']=ylim[0]
                self.topRightPlotProperties['MaxY']=ylim[1]
                if self.Zoom['Vertical']['JoinPhaseWithOthers'].Bool():
                    spPlotPropertiesToJoinFrom=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
                    for thisToPort in range(1,self.sp.m_P+1):
                        for thisFromPort in range(1,self.sp.m_P+1):
                            if self.JoinIt(thisToPort,thisFromPort,'Vertical'):
                                spPlotPropertiesToJoinTo=self.properties['Plot.S'][thisToPort-1][thisFromPort-1]
                                spPlotPropertiesToJoinTo['Phase.YInitialized']=True
                                spPlotPropertiesToJoinTo['Phase.MinY']=spPlotPropertiesToJoinFrom['Phase.MinY']
                                spPlotPropertiesToJoinTo['Phase.MaxY']=spPlotPropertiesToJoinFrom['Phase.MaxY']
            self.LimitChangeLock=False

    def onBottomLeftXLimitChange(self,ax):
        if not self.LimitChangeLock:
            self.LimitChangeLock=True
            xlim=ax.get_xlim()
            if not self.bottomLeftPlotProperties is None:
                self.bottomLeftPlotProperties['MinX']=xlim[0]
                self.bottomLeftPlotProperties['MaxX']=xlim[1]
                if self.Zoom['Times']['JoinWithin'].Bool():
                    if (self.fromPort == self.toPort):
                        self.plotProperties['Impedance.MinX']=self.plotProperties['Impulse.MinX']/2.
                        self.plotProperties['Impedance.MaxX']=self.plotProperties['Impulse.MaxX']/2.
                        self.plotProperties['Impedance.Initialized']=True
                    self.plotProperties['Step.MinX']=self.plotProperties['Impulse.MinX']
                    self.plotProperties['Step.MaxX']=self.plotProperties['Impulse.MaxX']
                    self.plotProperties['Step.Initialized']=True
                    self.bottomRightPlot.set_xlim(left=self.bottomRightPlotProperties['MinX'])
                    self.bottomRightPlot.set_xlim(right=self.bottomRightPlotProperties['MaxX'])
                    self.bottomRightCanvas.draw()
                if self.Zoom['Times']['JoinWithOthers'].Bool():
                    spPlotPropertiesToJoinFrom=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
                    for thisToPort in range(1,self.sp.m_P+1):
                        for thisFromPort in range(1,self.sp.m_P+1):
                            if self.JoinIt(thisToPort,thisFromPort,'Times'):
                                spPlotPropertiesToJoinTo=self.properties['Plot.S'][thisToPort-1][thisFromPort-1]
                                spPlotPropertiesToJoinTo['Impulse.XInitialized']=True
                                spPlotPropertiesToJoinTo['Impulse.MinX']=spPlotPropertiesToJoinFrom['Impulse.MinX']
                                spPlotPropertiesToJoinTo['Impulse.MaxX']=spPlotPropertiesToJoinFrom['Impulse.MaxX']
                                if self.Zoom['Times']['JoinWithin'].Bool():
                                    spPlotPropertiesToJoinTo['Step.XInitialized']=True
                                    spPlotPropertiesToJoinTo['Step.MinX']=spPlotPropertiesToJoinFrom['Step.MinX']
                                    spPlotPropertiesToJoinTo['Step.MaxX']=spPlotPropertiesToJoinFrom['Step.MaxX']
                                    spPlotPropertiesToJoinTo['Impedance.XInitialized']=True
                                    spPlotPropertiesToJoinTo['Impedance.MinX']=spPlotPropertiesToJoinFrom['Impedance.MinX']
                                    spPlotPropertiesToJoinTo['Impedance.MaxX']=spPlotPropertiesToJoinFrom['Impedance.MaxX']
            self.LimitChangeLock=False

    def onBottomLeftYLimitChange(self,ax):
        if not self.LimitChangeLock:
            self.LimitChangeLock=True
            ylim=ax.get_ylim()
            if not self.bottomLeftPlotProperties is None:
                self.bottomLeftPlotProperties['MinY']=ylim[0]
                self.bottomLeftPlotProperties['MaxY']=ylim[1]
                if self.Zoom['Vertical']['JoinImpulseWithOthers'].Bool():
                    spPlotPropertiesToJoinFrom=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
                    for thisToPort in range(1,self.sp.m_P+1):
                        for thisFromPort in range(1,self.sp.m_P+1):
                            if self.JoinIt(thisToPort,thisFromPort,'Vertical'):
                                spPlotPropertiesToJoinTo=self.properties['Plot.S'][thisToPort-1][thisFromPort-1]
                                spPlotPropertiesToJoinTo['Impulse.YInitialized']=True
                                spPlotPropertiesToJoinTo['Impulse.MinY']=spPlotPropertiesToJoinFrom['Impulse.MinY']
                                spPlotPropertiesToJoinTo['Impulse.MaxY']=spPlotPropertiesToJoinFrom['Impulse.MaxY']
            self.LimitChangeLock=False

    def onBottomRightXLimitChange(self,ax):
        if not self.LimitChangeLock:
            self.LimitChangeLock=True
            xlim=ax.get_xlim()
            if not self.bottomRightPlotProperties is None:
                self.bottomRightPlotProperties['MinX']=xlim[0]
                self.bottomRightPlotProperties['MaxX']=xlim[1]
                if self.Zoom['Times']['JoinWithin'].Bool():
                    if (self.ShowImpedanceDoer.Bool() or self.ShowExcessInductanceDoer.Bool() or self.ShowExcessCapacitanceDoer.Bool()) and (self.fromPort == self.toPort):
                        self.plotProperties['Impulse.MinX']=self.plotProperties['Impedance.MinX']*2.
                        self.plotProperties['Impulse.MaxX']=self.plotProperties['Impedance.MaxX']*2.
                        self.plotProperties['Impulse.Initialized']=True
                        self.plotProperties['Step.MinX']=self.plotProperties['Impedance.MinX']*2.
                        self.plotProperties['Step.MaxX']=self.plotProperties['Impedance.MaxX']*2.
                        self.plotProperties['Step.Initialized']=True
                    else:
                        self.plotProperties['Impulse.MinX']=self.plotProperties['Step.MinX']
                        self.plotProperties['Impulse.MaxX']=self.plotProperties['Step.MaxX']
                        self.plotProperties['Impulse.Initialized']=True
                        self.plotProperties['Impedance.MinX']=self.plotProperties['Step.MinX']/2.
                        self.plotProperties['Impedance.MaxX']=self.plotProperties['Step.MaxX']/2.
                        self.plotProperties['Impedance.Initialized']=True
                    self.bottomLeftPlot.set_xlim(left=self.bottomLeftPlotProperties['MinX'])
                    self.bottomLeftPlot.set_xlim(right=self.bottomLeftPlotProperties['MaxX'])
                    self.bottomLeftCanvas.draw()
                if self.Zoom['Times']['JoinWithOthers'].Bool():
                    spPlotPropertiesToJoinFrom=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
                    for thisToPort in range(1,self.sp.m_P+1):
                        for thisFromPort in range(1,self.sp.m_P+1):
                            if self.JoinIt(thisToPort,thisFromPort,'Times'):
                                spPlotPropertiesToJoinTo=self.properties['Plot.S'][thisToPort-1][thisFromPort-1]
                                if (self.ShowImpedanceDoer.Bool() or self.ShowExcessInductanceDoer.Bool() or self.ShowExcessCapacitanceDoer.Bool()) and (self.fromPort == self.toPort):
                                    spPlotPropertiesToJoinTo['Impedance.XInitialized']=True
                                    spPlotPropertiesToJoinTo['Impedance.MinX']=spPlotPropertiesToJoinFrom['Impedance.MinX']
                                    spPlotPropertiesToJoinTo['Impedance.MaxX']=spPlotPropertiesToJoinFrom['Impedance.MaxX']
                                else:
                                    spPlotPropertiesToJoinTo['Step.XInitialized']=True
                                    spPlotPropertiesToJoinTo['Step.MinX']=spPlotPropertiesToJoinFrom['Step.MinX']
                                    spPlotPropertiesToJoinTo['Step.MaxX']=spPlotPropertiesToJoinFrom['Step.MaxX']
                                if self.Zoom['Times']['JoinWithin'].Bool():
                                    spPlotPropertiesToJoinTo['Impulse.XInitialized']=True
                                    spPlotPropertiesToJoinTo['Impulse.MinX']=spPlotPropertiesToJoinFrom['Impulse.MinX']
                                    spPlotPropertiesToJoinTo['Impulse.MaxX']=spPlotPropertiesToJoinFrom['Impulse.MaxX']
            self.LimitChangeLock=False

    def onBottomRightYLimitChange(self,ax):
        if not self.LimitChangeLock:
            self.LimitChangeLock=True
            ylim=ax.get_ylim()
            if not self.bottomRightPlotProperties is None:
                self.bottomRightPlotProperties['MinY']=(ylim[0]-self.bottomRightPlotProperties['B'])/self.bottomRightPlotProperties['M']
                self.bottomRightPlotProperties['MaxY']=(ylim[1]-self.bottomRightPlotProperties['B'])/self.bottomRightPlotProperties['M']
                if self.Zoom['Vertical']['JoinStepImpedanceWithOthers'].Bool():
                    spPlotPropertiesToJoinFrom=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
                    for thisToPort in range(1,self.sp.m_P+1):
                        for thisFromPort in range(1,self.sp.m_P+1):
                            if self.JoinIt(thisToPort,thisFromPort,'Vertical'):
                                spPlotPropertiesToJoinTo=self.properties['Plot.S'][thisToPort-1][thisFromPort-1]
                                if (self.ShowImpedanceDoer.Bool() or self.ShowExcessInductanceDoer.Bool() or self.ShowExcessCapacitanceDoer.Bool()) and (self.fromPort == self.toPort):
                                    spPlotPropertiesToJoinTo['Impedance.YInitialized']=True
                                    spPlotPropertiesToJoinTo['Impedance.MinY']=spPlotPropertiesToJoinFrom['Impedance.MinY']
                                    spPlotPropertiesToJoinTo['Impedance.MaxY']=spPlotPropertiesToJoinFrom['Impedance.MaxY']
                                else:
                                    spPlotPropertiesToJoinTo['Step.YInitialized']=True
                                    spPlotPropertiesToJoinTo['Step.MinY']=spPlotPropertiesToJoinFrom['Step.MinY']
                                    spPlotPropertiesToJoinTo['Step.MaxY']=spPlotPropertiesToJoinFrom['Step.MaxY']
            self.LimitChangeLock=False

    def onTopLeftHome(self):
        if not self.topLeftPlotProperties is None:
            self.topLeftPlotProperties['XInitialized']=False
            self.topLeftPlotProperties['YInitialized']=False
            self.PlotSParameter()

    def onTopRightHome(self):
        if not self.topRightPlotProperties is None:
            self.topRightPlotProperties['XInitialized']=False
            self.topRightPlotProperties['YInitialized']=False
            self.PlotSParameter()

    def onBottomLeftHome(self):
        if not self.bottomLeftPlotProperties is None:
            self.bottomLeftPlotProperties['XInitialized']=False
            self.bottomLeftPlotProperties['YInitialized']=False
            self.PlotSParameter()

    def onBottomRightHome(self):
        if not self.bottomRightPlotProperties is None:
            self.bottomRightPlotProperties['XInitialized']=False
            self.bottomRightPlotProperties['YInitialized']=False
            self.PlotSParameter()

    def UpdatePreferences(self):
        self.ShowGridsDoer.Set(SignalIntegrity.App.Preferences['Appearance.GridsOnPlots'])
        self.VariableLineWidthDoer.Set(SignalIntegrity.App.Preferences['SParameterProperties.Plot.VariableLineWidth'])
        self.ShowPassivityViolationsDoer.Set(SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowPassivityViolations'])
        self.ShowCausalityViolationsDoer.Set(SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowCausalityViolations'])
        self.ShowImpedanceDoer.Set(SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowImpedance'])
        self.ShowExcessInductanceDoer.Set(SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowExcessInductance'])
        self.ShowExcessCapacitanceDoer.Set(SignalIntegrity.App.Preferences['SParameterProperties.Plot.ShowExcessCapacitance'])
        self.LogScaleDoer.Set(SignalIntegrity.App.Preferences['SParameterProperties.Plot.LogScale'])
        self.LinearVerticalScaleDoer.Set(SignalIntegrity.App.Preferences['SParameterProperties.Plot.LinearVerticalScale'])
        self.Zoom['Frequencies']['JoinWithin'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Frequencies.JoinWithin'])
        self.Zoom['Times']['JoinWithin'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Times.JoinWithin'])
        self.Zoom['Frequencies']['JoinWithOthers'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Frequencies.JoinWithOthers'])
        self.Zoom['Times']['JoinWithOthers'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Times.JoinWithOthers'])
        self.Zoom['Vertical']['JoinMagnitudeWithOthers'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.JoinMagnitudeWithOthers'])
        self.Zoom['Vertical']['JoinPhaseWithOthers'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.JoinPhaseWithOthers'])
        self.Zoom['Vertical']['JoinImpulseWithOthers'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.JoinImpulseWithOthers'])
        self.Zoom['Vertical']['JoinStepImpedanceWithOthers'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.JoinStepImpedanceWithOthers'])
        self.Zoom['Frequencies']['Join']['All'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Frequencies.Join.All'])
        self.Zoom['Frequencies']['Join']['OffDiagonal'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Frequencies.Join.OffDiagonal'])
        self.Zoom['Frequencies']['Join']['Reciprocals'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Frequencies.Join.Reciprocals'])
        self.Zoom['Frequencies']['Join']['Reflects'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Frequencies.Join.Reflects'])
        self.Zoom['Times']['Join']['All'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Times.Join.All'])
        self.Zoom['Times']['Join']['OffDiagonal'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Times.Join.OffDiagonal'])
        self.Zoom['Times']['Join']['Reciprocals'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Times.Join.Reciprocals'])
        self.Zoom['Times']['Join']['Reflects'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Times.Join.Reflects'])
        self.Zoom['Vertical']['Join']['All'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.Join.All'])
        self.Zoom['Vertical']['Join']['OffDiagonal'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.Join.OffDiagonal'])
        self.Zoom['Vertical']['Join']['Reciprocals'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.Join.Reciprocals'])
        self.Zoom['Vertical']['Join']['Reflects'].Set(SignalIntegrity.App.Preferences['SParameterProperties.Zoom.Vertical.Join.Reflects'])

    def UpdatePropertiesFromSParameters(self,new=False):
        self.properties['FrequencyPoints']=len(self.sp.m_f)-1
        self.properties['EndFrequency']=self.sp.m_f[-1]
        self.properties['ReferenceImpedance']=self.sp.m_Z0
        if si.fd.FrequencyList(self.sp.m_f).CheckEvenlySpaced():
            self.properties.CalculateOthersFromBaseInformation()
            (negativeTime,positiveTime)=self.sp.DetermineImpulseResponseLength()
            self.properties['TimeLimitNegative']=negativeTime
            self.properties['TimeLimitPositive']=positiveTime
            self.statusbar.set(str(self.properties['FrequencyPoints'])+
                '(+1) frequency points to '+ToSI(self.properties['EndFrequency'],'Hz')+
                ', Evenly Spaced in '+ToSI(self.properties['FrequencyResolution'],'Hz')+
                ' steps, Z0='+ToSI(self.properties['ReferenceImpedance'],'ohm'))
        else:
            self.statusbar.set(str(self.properties['FrequencyPoints']+1)+
                ' frequency points, last frequency is '+ToSI(self.properties['EndFrequency'],'Hz')+
                ', Unevenly spaced, Z0='+ToSI(self.properties['ReferenceImpedance'],'ohm'))
            self.properties['BaseSampleRate']=None
            self.properties['BaseSamplePeriod']=None
            self.properties['UserSamplePeriod']=None
            self.properties['TimePoints']=None
            self.properties['FrequencyResolution']=None
            self.properties['ImpulseResponseLength']=None
            self.properties['TimeLimitNegative']=None
            self.properties['TimeLimitPositive']=None
        if new:
            self.properties['Plot.S']=[[SParameterPlotsConfiguration() for _ in range(self.sp.m_P)] for _ in range(self.sp.m_P)]
        self.ZoomJoinActivations()

    def UpdateSParametersFromProperties(self):
        msg=None
        spChanged=False
        if not self.properties['TimePoints'] is None:
            (negativeTime,positiveTime)=self.sp.DetermineImpulseResponseLength()
            if not (negativeTime is None) and not (positiveTime is None) and not (self.properties['TimeLimitNegative'] is None) and not (self.properties['TimeLimitPositive'] is None):
                if (self.properties['TimeLimitNegative']>negativeTime) or\
                    self.properties['TimeLimitPositive']<positiveTime:
                    if msg is None:
                        msg=InformationMessage(self,'S-parameters : '+self.fileparts.FileNameWithExtension(), 'recalculating s-parameters based on changes\n Please wait.....')
                    self.sp=self.sp.LimitImpulseResponseLength((self.properties['TimeLimitNegative'],self.properties['TimeLimitPositive']))
                    spChanged=True
            if not si.fd.FrequencyList(self.sp.m_f).CheckEvenlySpaced() or\
                (self.properties['FrequencyPoints']!=len(self.sp.m_f)-1) or\
                (self.properties['EndFrequency']!=self.sp.m_f[-1]):
                if msg is None:
                    msg=InformationMessage(self,'S-parameters : '+self.fileparts.FileNameWithExtension(), 'recalculating s-parameters based on changes\n Please wait.....')
                self.sp=self.sp.Resample(si.fd.EvenlySpacedFrequencyList(
                    self.properties['EndFrequency'],
                    self.properties['FrequencyPoints']))
                spChanged=True

        if self.properties['ReferenceImpedance'] != self.sp.m_Z0:
            if msg is None:
                msg=InformationMessage(self,'S-parameters : '+self.fileparts.FileNameWithExtension(), 'recalculating s-parameters based on changes\n Please wait.....')
            self.sp.SetReferenceImpedance(self.properties['ReferenceImpedance'])
            spChanged=True

        if spChanged:
            self.UpdatePropertiesFromSParameters()
        if not msg is None:
            msg.destroy()
        if spChanged:
            self.PlotSParameter()

    def onClosing(self):
        self.withdraw()
        self.destroy()

    def destroy(self):
        tk.Toplevel.withdraw(self)
        tk.Toplevel.destroy(self)

    def PlotSParameter(self):
        self.topLeftPlot.cla()
        self.topRightPlot.cla()
        self.bottomLeftPlot.cla()
        self.bottomRightPlot.cla()

        self.topLeftPlotProperties=None
        self.topRightPlotProperties=None
        self.bottomLeftPlotProperties=None
        self.bottomRightPlotProperties=None
        self.plotProperties=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]

        if not SignalIntegrity.App.Preferences['Appearance.PlotCursorValues']:
            self.topLeftPlot.format_coord = lambda x, y: ''
            self.topRightPlot.format_coord = lambda x, y: ''
            self.bottomLeftPlot.format_coord = lambda x, y: ''
            self.bottomRightPlot.format_coord = lambda x, y: ''

        fr=self.sp.FrequencyResponse(self.toPort,self.fromPort)
        ir=fr.ImpulseResponse()

        y=fr.Response('mag') if self.LinearVerticalScaleDoer.Bool() else fr.Response('dB')

        self.freqLabel=ToSI(fr.Frequencies()[-1],'Hz')[-3:]
        freqLabelDivisor=FromSI('1. '+self.freqLabel,'Hz')

        x=fr.Frequencies(freqLabelDivisor)

        if self.ShowPassivityViolationsDoer.Bool():
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

        if self.VariableLineWidthDoer.Bool():
            if fastway:
                segments = [[[x[i],y[i]],[x[i+1],y[i+1]]] for i in range(len(x)-1)]
                slw=lw[:-1]
                lc = LineCollection(segments, linewidths=slw,color='blue')
                self.topLeftPlot.add_collection(lc)
            else:
                for i in range(len(x)-1):
                    if self.LogScaleDoer.Bool():
                        self.topLeftPlot.semilogx(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
                    else:
                        self.topLeftPlot.plot(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
        else:
            if self.LogScaleDoer.Bool():
                self.topLeftPlot.semilogx(x,y)
            else:
                self.topLeftPlot.plot(x,y)

        if self.ShowPassivityViolationsDoer.Bool():
            self.topLeftPlot.scatter(
                [c[0] for c in self.passivityViolations],
                [c[1] for c in self.passivityViolations],
                s=[c[2] for c in self.passivityViolations],
                color='red')

        self.topLeftPlotProperties=self.plotProperties['Magnitude']
        self.topLeftLabel.config(text='Magnitude')

        if not self.topLeftPlotProperties['XInitialized']:
            self.topLeftPlotProperties['MinX']=min(x)
            self.topLeftPlotProperties['MaxX']=max(x)
            self.topLeftPlotProperties['XInitialized']=True
        if not self.topLeftPlotProperties['YInitialized']:
            self.topLeftPlotProperties['MinY']=min(max(min(y)-1.,-60.0),max(y)+1.)
            self.topLeftPlotProperties['MaxY']=max(max(min(y)-1.,-60.0),max(y)+1.)
            self.topLeftPlotProperties['YInitialized']=True

        if self.LogScaleDoer.Bool():
            if max(x)>0:
                for value in x:
                    if value>0.:
                        self.topLeftPlot.set_xlim(left=value)
                        break
        else:
            self.topLeftPlot.set_xlim(left=self.topLeftPlotProperties['MinX'])
        self.topLeftPlot.set_xlim(right=self.topLeftPlotProperties['MaxX'])
        self.topLeftPlot.set_ylim(bottom=self.topLeftPlotProperties['MinY'])
        self.topLeftPlot.set_ylim(top=self.topLeftPlotProperties['MaxY'])

        self.topLeftPlot.set_ylabel('magnitude (abs)'  if self.LinearVerticalScaleDoer.Bool() else 'magnitude (dB)',fontsize=10)
        self.topLeftPlot.set_xlabel('frequency ('+self.freqLabel+')',fontsize=10)

        if self.ShowGridsDoer.Bool():
            self.topLeftPlot.grid(True, 'both')

        TD = self.plotProperties['Delay']
        frph=fr._DelayBy(-TD)

        y=frph.Response('deg')

        x=frph.Frequencies(freqLabelDivisor)

        if self.VariableLineWidthDoer.Bool():
            if fastway:
                segments = [[[x[i],y[i]],[x[i+1],y[i+1]]] for i in range(len(x)-1)]
                slw=lw[:-1]
                lc = LineCollection(segments, linewidths=slw,color='blue')
                self.topRightPlot.add_collection(lc)
            else:
                for i in range(len(x)-1):
                    if self.LogScaleDoer.Bool():
                        self.topRightPlot.semilogx(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
                    else:
                        self.topRightPlot.plot(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
        else:
            if self.LogScaleDoer.Bool():
                self.topRightPlot.semilogx(x,y)
            else:
                self.topRightPlot.plot(x,y)

        self.topRightPlotProperties=self.plotProperties['Phase']
        self.topRightLabel.config(text='Phase')

        if not self.topRightPlotProperties['XInitialized']:
            self.topRightPlotProperties['MinX']=min(x)
            self.topRightPlotProperties['MaxX']=max(x)
            self.topRightPlotProperties['XInitialized']=True
        if not self.topRightPlotProperties['YInitialized']:
            self.topRightPlotProperties['MinY']=min(y)-1
            self.topRightPlotProperties['MaxY']=max(y)+1
            self.topRightPlotProperties['YInitialized']=True

        if self.LogScaleDoer.Bool():
            if max(x)>0:
                for value in x:
                    if value>0:
                        self.topRightPlot.set_xlim(left=value)
                        break
        else:
            self.topRightPlot.set_xlim(left=self.topRightPlotProperties['MinX'])
        self.topRightPlot.set_xlim(right=self.topRightPlotProperties['MaxX'])
        self.topRightPlot.set_ylim(bottom=self.topRightPlotProperties['MinY'])
        self.topRightPlot.set_ylim(top=self.topRightPlotProperties['MaxY'])

        self.topRightPlot.set_ylabel('phase (degrees)',fontsize=10)
        self.topRightPlot.set_xlabel('frequency ('+self.freqLabel+')',fontsize=10)

        if self.ShowGridsDoer.Bool():
            self.topRightPlot.grid(True, 'both')

        if ir is not None:
            if self.buttonLabels[self.toPort-1][self.fromPort-1][:2]=='i/' or self.buttonLabels[self.toPort-1][self.fromPort-1][:3]=='di/':
                print('Integrate')
                ir=si.td.wf.ImpulseResponse(ir.Integral(addPoint=False))
            if self.buttonLabels[self.toPort-1][self.fromPort-1][:3]=='di/':
                print('Integrate')
                ir=si.td.wf.ImpulseResponse(ir.Integral(addPoint=False)*ir.td.Fs)

            y=ir.Values()

            timeLabel=ToSI(ir.Times()[-1],'s')[-2:]
            timeLabelDivisor=FromSI('1. '+timeLabel,'s')

            x=ir.Times(timeLabelDivisor)

            self.bottomLeftPlot.plot(x,y)

            if self.ShowCausalityViolationsDoer.Bool():
                minv=0.00001; maxv=0.1
                minx=math.log10(minv); maxx=math.log10(maxv)
                miny=0.; maxy=20.
                m=(maxy-miny)/(maxx-minx); b=miny-m*minx
                self.causalityViolations=[]
                Ts=1./ir.td.Fs/1e-9
                for k in range(len(x)):
                    if x[k]<=-Ts and abs(y[k])>0:
                        dotsize=max(math.log10(min(maxv,max(minv,abs(y[k]))))*m+b,1e-15)
                        if dotsize>2e-15:
                            self.causalityViolations.append([k,dotsize])
                self.bottomLeftPlot.scatter(
                    [x[c[0]] for c in self.causalityViolations],
                    [y[c[0]] for c in self.causalityViolations],
                    s=[c[1] for c in self.causalityViolations],
                    color='red')

            self.bottomLeftPlotProperties=self.plotProperties['Impulse']
            self.bottomLeftLabel.config(text='Impulse Response')

            if not self.bottomLeftPlotProperties['XInitialized']:
                self.bottomLeftPlotProperties['MinX']=min(x)
                self.bottomLeftPlotProperties['MaxX']=max(x)
                self.bottomLeftPlotProperties['XInitialized']=True
            if not self.bottomLeftPlotProperties['YInitialized']:
                self.bottomLeftPlotProperties['MinY']=min(min(y)*1.05,-0.1)
                self.bottomLeftPlotProperties['MaxY']=max(max(y)*1.05,0.1)
                self.bottomLeftPlotProperties['YInitialized']=True

            self.bottomLeftPlot.set_xlim(left=self.bottomLeftPlotProperties['MinX'])
            self.bottomLeftPlot.set_xlim(right=self.bottomLeftPlotProperties['MaxX'])
            self.bottomLeftPlot.set_ylim(bottom=self.bottomLeftPlotProperties['MinY'])
            self.bottomLeftPlot.set_ylim(top=self.bottomLeftPlotProperties['MaxY'])

            self.bottomLeftPlot.set_ylabel('amplitude',fontsize=10)
            self.bottomLeftPlot.set_xlabel('time ('+timeLabel+')',fontsize=10)

            if self.ShowGridsDoer.Bool():
                self.bottomLeftPlot.grid(True)

            firFilter=ir.FirFilter()
            stepWaveformTimeDescriptor=ir.td/firFilter.FilterDescriptor()
            stepWaveform=si.td.wf.StepWaveform(stepWaveformTimeDescriptor)
            stepResponse=stepWaveform*firFilter
            y=stepResponse.Values()
            x=stepResponse.Times(timeLabelDivisor)
            Ts=1./(stepWaveformTimeDescriptor.Fs)

            self.bottomRightToolbar.update()

            if (self.ShowImpedanceDoer.Bool() or self.ShowExcessInductanceDoer.Bool() or self.ShowExcessCapacitanceDoer.Bool()) and (self.fromPort == self.toPort):
                self.bottomRightPlotProperties=self.plotProperties['Impedance']
                Z0=self.properties['ReferenceImpedance']
                y=[3000. if (1-yv)<=.000001 else min(Z0*(1+yv)/(1-yv),3000) for yv in y]
                x=[xv/2 for xv in x]
                self.bottomRightPlot.set_ylabel('impedance (ohms)',fontsize=10)
                self.bottomRightPlot.set_xlabel('length ('+timeLabel+')',fontsize=10)

                if not self.bottomRightPlotProperties['YInitialized']:
                    self.bottomRightPlotProperties['MinY']=min(min(y)*1.05,Z0-1)
                    self.bottomRightPlotProperties['MaxY']=max(max(y)*1.05,0.1)
                    self.bottomRightPlotProperties['YInitialized']=True
                maxy=self.bottomRightPlotProperties['MaxY']
                miny=self.bottomRightPlotProperties['MinY']

                if self.ShowImpedanceDoer.Bool():
                    self.bottomRightlabel.config(text='Impedance Profile')
                    self.bottomRightPlot.set_ylabel('impedance (Ohms)',fontsize=10)
                elif self.ShowExcessInductanceDoer.Bool():
                    maxy=(maxy-Z0)*Ts/2.
                    miny=(miny-Z0)*Ts/2.
                    span=max(abs(maxy),abs(miny))
                    yLabel=ToSI(span,'H')[-2:]
                    yLabelDivisor=FromSI('1. '+yLabel,'H')
                    maxy=maxy/yLabelDivisor
                    miny=miny/yLabelDivisor
                    y=[(yv-Z0)*Ts/2./yLabelDivisor for yv in y]
                    self.bottomRightlabel.config(text='Excess Inductance Profile')
                    self.bottomRightPlot.set_ylabel('Excess L ('+yLabel+')',fontsize=10)
                elif self.ShowExcessCapacitanceDoer.Bool():
                    maxy=(1./maxy-1./Z0)*Ts/2.
                    miny=(1./miny-1./Z0)*Ts/2.
                    span=max(abs(maxy),abs(miny))
                    yLabel=ToSI(span,'F')[-2:]
                    yLabelDivisor=FromSI('1. '+yLabel,'F')
                    maxy=maxy/yLabelDivisor
                    miny=miny/yLabelDivisor
                    y=[(1./yv-1./Z0)*Ts/2./yLabelDivisor for yv in y]
                    self.bottomRightlabel.config(text='Excess Capacitance Profile')
                    self.bottomRightPlot.set_ylabel('Excess C ('+yLabel+')',fontsize=10)

                self.bottomRightPlotProperties['M']=(maxy-miny)/(self.bottomRightPlotProperties['MaxY']-self.bottomRightPlotProperties['MinY'])
                self.bottomRightPlotProperties['B']=maxy-(self.bottomRightPlotProperties['M']*self.bottomRightPlotProperties['MaxY'])

            else:
                self.bottomRightlabel.config(text='Step Response')
                self.bottomRightPlotProperties=self.plotProperties['Step']
                self.bottomRightPlot.set_ylabel('amplitude',fontsize=10)
                self.bottomRightPlot.set_xlabel('time ('+timeLabel+')',fontsize=10)
                if not self.bottomRightPlotProperties['YInitialized']:
                    self.bottomRightPlotProperties['MinY']=min(min(y)*1.05,-0.1)
                    self.bottomRightPlotProperties['MaxY']=max(max(y)*1.05,0.1)
                    self.bottomRightPlotProperties['YInitialized']=True

            self.bottomRightPlot.plot(x,y)

            if self.ShowCausalityViolationsDoer.Bool():
                self.bottomRightPlot.scatter(
                    [x[c[0]] for c in self.causalityViolations],
                    [y[c[0]] for c in self.causalityViolations],
                    s=[c[1] for c in self.causalityViolations],
                    color='red')

            if not self.bottomRightPlotProperties['XInitialized']:
                self.bottomRightPlotProperties['MinX']=min(x)
                self.bottomRightPlotProperties['MaxX']=max(x)
                self.bottomRightPlotProperties['XInitialized']=True
                if (self.ShowImpedanceDoer.Bool() or self.ShowExcessInductanceDoer.Bool() or self.ShowExcessCapacitanceDoer.Bool()) and (self.fromPort == self.toPort):
                    self.plotProperties['Step.MinX']=self.bottomRightPlotProperties['MinX']*2.0
                    self.plotProperties['Step.MaxX']=self.bottomRightPlotProperties['MaxX']*2.0
                    self.plotProperties['Step.XInitialized']=True
                else:
                    self.plotProperties['Impedance.MinX']=self.bottomRightPlotProperties['MinX']/2.0
                    self.plotProperties['Impedance.MaxX']=self.bottomRightPlotProperties['MaxX']/2.0
                    self.plotProperties['Impedance.XInitialized']=True

            self.bottomRightPlot.set_xlim(left=self.bottomRightPlotProperties['MinX'])
            self.bottomRightPlot.set_xlim(right=self.bottomRightPlotProperties['MaxX'])
            self.bottomRightPlot.set_ylim(bottom=self.bottomRightPlotProperties['MinY']*self.bottomRightPlotProperties['M']+self.bottomRightPlotProperties['B'])
            self.bottomRightPlot.set_ylim(top=self.bottomRightPlotProperties['MaxY']*self.bottomRightPlotProperties['M']+self.bottomRightPlotProperties['B'])

        if self.ShowGridsDoer.Bool():
            self.bottomRightPlot.grid(True)

        self.topLeftCanvas.draw()
        self.topRightCanvas.draw()
        self.bottomLeftCanvas.draw()
        self.bottomRightCanvas.draw()

        self.topLeftToolbar.update()
        self.topRightToolbar.update()
        self.bottomLeftToolbar.update()
        self.bottomRightToolbar.update()

        self.topLeftPlot.callbacks.connect('xlim_changed', self.onTopLeftXLimitChange)
        self.topLeftPlot.callbacks.connect('ylim_changed', self.onTopLeftYLimitChange)
        self.topRightPlot.callbacks.connect('xlim_changed', self.onTopRightXLimitChange)
        self.topRightPlot.callbacks.connect('ylim_changed', self.onTopRightYLimitChange)
        self.bottomLeftPlot.callbacks.connect('xlim_changed', self.onBottomLeftXLimitChange)
        self.bottomLeftPlot.callbacks.connect('ylim_changed', self.onBottomLeftYLimitChange)
        self.bottomRightPlot.callbacks.connect('xlim_changed', self.onBottomRightXLimitChange)
        self.bottomRightPlot.callbacks.connect('ylim_changed', self.onBottomRightYLimitChange)

    def onSelectSParameter(self,toP,fromP):
        self.buttons[self.toPort-1][self.fromPort-1].config(relief=tk.RAISED)
        self.toPort = toP
        self.fromPort = fromP
        self.buttons[self.toPort-1][self.fromPort-1].config(relief=tk.SUNKEN)
        self.plotProperties=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
        self.delayViewerProperty.SetString(self.plotProperties['Delay'])
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
        self.plotProperties['Delay']=TD
        self.delayViewerProperty.SetString(TD)
        self.delayViewerProperty.onEntered(None)

    def onDelayEntered(self,event):
        self.topRightPlot.cla()
        fr=self.sp.FrequencyResponse(self.toPort,self.fromPort)
        TD = self.delayViewerProperty.GetString()
        self.delayViewerProperty.SetString(TD)
        self.plotProperties['Delay']=TD
        fr=fr._DelayBy(-TD)
        lw=[min(1.,math.sqrt(w))*1.5 for w in fr.Response('mag')]
        y=fr.Response('deg')
        x=fr.Frequencies('GHz')
        fastway=True
        if self.VariableLineWidthDoer.Bool():
            if fastway:
                segments = [[[x[i],y[i]],[x[i+1],y[i+1]]] for i in range(len(x)-1)]
                slw=lw[:-1]
                lc = LineCollection(segments, linewidths=slw,color='blue')
                self.topRightPlot.add_collection(lc)
            else:
                for i in range(len(x)-1):
                    if self.LogScaleDoer.Bool():
                        self.topRightPlot.semilogx(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
                    else:
                        self.topRightPlot.plot(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
        else:
            if self.LogScaleDoer.Bool():
                self.topRightPlot.semilogx(x,y)
            else:
                self.topRightPlot.plot(x,y)

        if not self.topRightPlotProperties['XInitialized']:
            self.topRightPlotProperties['MinX']=min(x)
            self.topRightPlotProperties['MaxX']=max(x)
            self.topRightPlotProperties['XInitialized']=True
        if not self.topRightPlotProperties['YInitialized']:
            self.topRightPlotProperties['MinY']=min(y)-1
            self.topRightPlotProperties['MaxY']=max(y)+1
            self.topRightPlotProperties['YInitialized']=True

        if self.LogScaleDoer.Bool():
            if max(x)>0:
                for value in x:
                    if value>0:
                        self.topRightPlot.set_xlim(left=value)
                        break
        else:
            self.topRightPlot.set_xlim(left=self.topRightPlotProperties['MinX'])
        self.topRightPlot.set_xlim(right=self.topRightPlotProperties['MaxX'])
        self.topRightPlot.set_ylim(bottom=self.topRightPlotProperties['MinY'])
        self.topRightPlot.set_ylim(top=self.topRightPlotProperties['MaxY'])

        self.topRightPlot.set_ylabel('phase (degrees)',fontsize=10)
        self.topRightPlot.set_xlabel('frequency ('+self.freqLabel+')',fontsize=10)

        if self.ShowGridsDoer.Bool():
            self.topRightPlot.grid(True, 'both')

        self.topRightCanvas.draw()
        self.topRightToolbar.update()

    def onReadSParametersFromFile(self):
        filename=AskOpenFileName(filetypes=[('s-parameter files', ('*.s*p','*.S*P')),('calibration files', ('*.cal'))],
                                 initialdir=self.fileparts.AbsoluteFilePath(),
                                 initialfile=self.fileparts.FileNameWithExtension(),
                                 parent=self)
        if filename is None:
            return
        self.fileparts=FileParts(filename)
        if self.fileparts.fileext=='':
            return

        if self.fileparts.fileext=='.cal':
            sp=si.m.cal.Calibration(0,0)
            try:
                sp.ReadFromFile(filename)
            except:
                messagebox.showerror('Calibration File','could not be read ')
                return
        else:
            sp=si.sp.SParameterFile(filename)

        self.NewSParameters(sp, filename)

    def onWriteSParametersToFile(self):
        ports=self.sp.m_P
        extension='.s'+str(ports)+'p','.S'+str(ports)+'P'
        filetypes=[('s-parameters', extension)]
        if self.calibration != None:
            extension=('.cal')
            filetypes=[('calibration file', '.cal')]+filetypes
        filename=AskSaveAsFilename(filetypes=filetypes,
                    defaultextension=extension[0],
                    initialdir=self.fileparts.AbsoluteFilePath(),
                    initialfile=self.fileparts.FileNameWithExtension(extension[0]),
                    parent=self)
        if filename is None:
            return
        self.fileparts=FileParts(filename)
        if self.fileparts.fileext=='.cal':
            self.calibration.WriteToFile(filename)
        else:
            self.sp.numDigits=SignalIntegrity.App.Preferences['SParameterProperties.SignificantDigits']
            self.sp.WriteToFile(filename,'R '+str(self.sp.m_Z0))

    def onCalculationProperties(self):
        self.parent.onCalculationProperties()

    def onSParameterProperties(self):
        if not hasattr(self, 'SParameterPropertiesDialog'):
            self.SParameterPropertiesDialog = SParameterPropertiesDialog(self,self.properties)
        if self.SParameterPropertiesDialog == None:
            self.SParameterPropertiesDialog= SParameterPropertiesDialog(self,self.properties)
        else:
            if not self.SParameterPropertiesDialog.winfo_exists():
                self.SParameterPropertiesDialog=SParameterPropertiesDialog(self,self.properties)
        self.SParameterPropertiesDialog.grab_set()


    def onMatplotlib2TikZ(self):
        variableNameText='_'+'_'.join((self.buttonLabels[self.toPort-1][self.fromPort-1]).split(' '))
        filename=AskSaveAsFilename(parent=self,filetypes=[('tex', '.tex')],
                                   defaultextension='.tex',
                                   initialdir=self.fileparts.AbsoluteFilePath(),
                                   initialfile=self.fileparts.filename+variableNameText+'_Magnitude.tex')
        if filename is None:
            return

        try:
            si.test.PlotTikZ(filename,self.topLeftFigure)
        except:
            messagebox.showerror('Export LaTeX','LaTeX could not be generated or written ')                
        fp=FileParts(filename.replace('_Magnitude.tex', '').replace('Magnitude.tex', ''))
        filename=fp.filename

        filename=AskSaveAsFilename(parent=self,filetypes=[('tex', '.tex')],
                                   defaultextension='.tex',
                                   initialdir=self.fileparts.AbsoluteFilePath(),
                                   initialfile=filename+'_Phase.tex')
        if filename is None:
            return

        try:
            si.test.PlotTikZ(filename,self.topRightFigure)
        except:
            messagebox.showerror('Export LaTeX','LaTeX could not be generated or written ')                
        fp=FileParts(filename.replace('_Phase.tex', '').replace('Phase.tex', ''))
        filename=fp.filename

        filename=AskSaveAsFilename(parent=self,filetypes=[('tex', '.tex')],
                                   defaultextension='.tex',
                                   initialdir=self.fileparts.AbsoluteFilePath(),
                                   initialfile=filename+'_ImpulseResponse.tex')
        if filename is None:
            return

        try:
            si.test.PlotTikZ(filename,self.bottomLeftFigure)
        except:
            messagebox.showerror('Export LaTeX','LaTeX could not be generated or written ')                
        fp=FileParts(filename.replace('_ImpulseResponse.tex', '').replace('ImpulseResponse.tex', ''))
        filename=fp.filename

        filename=AskSaveAsFilename(parent=self,filetypes=[('tex', '.tex')],
                                   defaultextension='.tex',
                                   initialdir=self.fileparts.AbsoluteFilePath(),
                                   initialfile=filename+'_StepResponse.tex')
        if filename is None:
            return

        try:
            si.test.PlotTikZ(filename,self.bottomRightFigure)
        except:
            messagebox.showerror('Export LaTeX','LaTeX could not be generated or written ')

    def onHelp(self):
        if Doer.helpKeys is None:
            messagebox.showerror('Help System','Cannot find or open this help element')
            return
        Doer.helpKeys.Open('sec:S-parameter-Viewer')

    def onControlHelp(self):
        Doer.inHelp=True
        self.config(cursor='question_arrow')

    def onEscape(self):
        Doer.inHelp=False
        self.config(cursor='left_ptr')

    def onEnforcePassivity(self):
        self.sp.EnforcePassivity()
        self.UpdatePropertiesFromSParameters()
        self.PlotSParameter()

    def onEnforceCausality(self):
        self.sp.EnforceCausality()
        self.UpdatePropertiesFromSParameters()
        self.PlotSParameter()

    def onEnforceBothPassivityAndCausality(self):
        self.sp.EnforceBothPassivityAndCausality(maxIterations=30,causalityThreshold=1e-5)
        self.UpdatePropertiesFromSParameters()
        self.PlotSParameter()

    def onEnforceReciprocity(self):
        self.sp.EnforceReciprocity()
        self.UpdatePropertiesFromSParameters()
        self.PlotSParameter()

    def onEnforceAll(self):
        self.sp.EnforceAll(maxIterations=30,causalityThreshold=1e-5)
        self.UpdatePropertiesFromSParameters()
        self.PlotSParameter()

    def onWaveletDenoise(self):
        self.sp.WaveletDenoise()
        self.UpdatePropertiesFromSParameters()
        self.PlotSParameter()

    def onPreferences(self):
        if not hasattr(self, 'preferencesDialog'):
            self.preferencesDialog = SParameterViewerPreferencesDialog(self,SignalIntegrity.App.Preferences)
        if self.preferencesDialog == None:
            self.preferencesDialog= SParameterViewerPreferencesDialog(self,SignalIntegrity.App.Preferences)
        else:
            if not self.preferencesDialog.winfo_exists():
                self.preferencesDialog=SParameterViewerPreferencesDialog(self,SignalIntegrity.App.Preferences)

    def onSelection(self,x):
        self.sp=self.spList[x][0]
        self.properties=SParameterProperties()
        self.UpdatePropertiesFromSParameters(new=True)
        filename=self.spList[x][1]
        title=self.spList[x][2]
        self.buttonLabels=self.spList[x][3]
        
        self.filename=self.spList[x][1]
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

        sButtonsFrame = tk.Frame(self.controlsFrame, bd=1, relief=tk.SUNKEN)
        self.buttons=[]
        for toP in range(len(self.buttonLabels)):
            buttonrow=[]
            rowFrame=tk.Frame(sButtonsFrame)
            rowFrame.pack(side=tk.TOP,expand=tk.NO,fill=tk.NONE)
            for fromP in range(len(self.buttonLabels[0])):
                thisButton=tk.Button(rowFrame,text=self.buttonLabels[toP][fromP],width=len(self.buttonLabels[toP][fromP]),command=lambda x=toP+1,y=fromP+1: self.onSelectSParameter(x,y))
                thisButton.pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
                buttonrow.append(thisButton)
            self.buttons.append(buttonrow)
        self.sButtonsFrame.pack_forget()
        self.sButtonsFrame=sButtonsFrame
        self.sButtonsFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.NONE)
        self.update_idletasks()
        self.onSelectSParameter(self.toPort, self.fromPort)
