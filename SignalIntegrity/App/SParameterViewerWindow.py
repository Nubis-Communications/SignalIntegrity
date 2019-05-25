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

        img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, img)
        self.protocol("WM_DELETE_WINDOW", self.onClosing)

        self.variableLineWidth = tk.BooleanVar()
        self.showPassivityViolations = tk.BooleanVar()
        self.showCausalityViolations = tk.BooleanVar()
        self.showImpedance = tk.BooleanVar()
        self.logScale =  tk.BooleanVar()

        self.JoinFrequenciesWithin = tk.BooleanVar()
        self.JoinTimesWithin = tk.BooleanVar()
        self.JoinFrequenciesWithOthers = tk.BooleanVar()
        self.JoinTimesWithOthers = tk.BooleanVar()
        self.JoinMagnitudeWithOthers = tk.BooleanVar()
        self.JoinPhaseWithOthers = tk.BooleanVar()
        self.JoinImpulseWithOthers = tk.BooleanVar()
        self.JoinStepImpedanceWithOthers = tk.BooleanVar()
        self.FrequenciesJoinAll = tk.BooleanVar()
        self.FrequenciesJoinOffDiagonal = tk.BooleanVar()
        self.FrequenciesJoinReciprocals = tk.BooleanVar()
        self.FrequenciesJoinReflects = tk.BooleanVar()
        self.TimesJoinAll = tk.BooleanVar()
        self.TimesJoinOffDiagonal = tk.BooleanVar()
        self.TimesJoinReciprocals = tk.BooleanVar()
        self.TimesJoinReflects = tk.BooleanVar()
        self.VerticalJoinAll = tk.BooleanVar()
        self.VerticalJoinOffDiagonal = tk.BooleanVar()
        self.VerticalJoinReciprocals = tk.BooleanVar()
        self.VerticalJoinReflects = tk.BooleanVar()
        # the Doers - the holder of the commands, menu elements, toolbar elements, and key bindings
        self.ReadSParametersFromFileDoer = Doer(self.onReadSParametersFromFile).AddKeyBindElement(self,'<Control-o>').AddHelpElement('Control-Help:Open-S-parameter-File')
        self.WriteSParametersToFileDoer = Doer(self.onWriteSParametersToFile).AddKeyBindElement(self,'<Control-s>').AddHelpElement('Control-Help:Save-S-parameter-File')
        self.Matplotlib2tikzDoer = Doer(self.onMatplotlib2TikZ)
        # ------
        self.CalculationPropertiesDoer = Doer(self.onCalculationProperties).AddHelpElement('Control-Help:Calculation-Properties')
        self.SParameterPropertiesDoer = Doer(self.onSParameterProperties)
        self.EnforcePassivityDoer = Doer(self.onEnforcePassivity).AddHelpElement('Control-Help:Enforce-Passivity')
        self.EnforceCausalityDoer = Doer(self.onEnforceCausality).AddHelpElement('Control-Help:Enforce-Causality')
        self.WaveletDenoiseDoer = Doer(self.onWaveletDenoise).AddHelpElement('Control-Help:Wavelet-Denoise')
        # ------
        self.HelpDoer = Doer(self.onHelp).AddHelpElement('Control-Help:Open-Help-File')
        self.ControlHelpDoer = Doer(self.onControlHelp).AddHelpElement('Control-Help:Control-Help')
        # ------
        self.VariableLineWidthDoer = Doer(self.onVariableLineWidth).AddHelpElement('Control-Help:Variable-Line-Width')
        self.ShowPassivityViolationsDoer = Doer(self.onShowPassivityViolations).AddHelpElement('Control-Help:Show-Passivity-Violations')
        self.ShowCausalityViolationsDoer = Doer(self.onShowCausalityViolations).AddHelpElement('Control-Help:Show-Causality-Violations')
        self.ShowImpedanceDoer = Doer(self.onShowImpedance).AddHelpElement('Control-Help:Show-Impedance')
        self.LogScaleDoer = Doer(self.onLogScale).AddHelpElement('Control-Help:Log-Scale')
        # ------
        self.JoinFrequenciesWithinDoer = Doer(self.onJoinFrequenciesWithin)
        self.JoinTimesWithinDoer = Doer(self.onJoinTimesWithin)
        self.JoinFrequenciesWithOthersDoer = Doer(self.onJoinFrequenciesWithOthers)
        self.JoinTimesWithOthersDoer = Doer(self.onJoinTimesWithOthers)
        self.JoinMagnitudeWithOthersDoer = Doer(self.onJoinMagnitudeWithOthers)
        self.JoinPhaseWithOthersDoer = Doer(self.onJoinPhaseWithOthers)
        self.JoinImpulseWithOthersDoer = Doer(self.onJoinImpulseWithOthers)
        self.JoinStepImpedanceWithOthersDoer = Doer(self.onJoinStepImpedanceWithOthers)
        self.FrequenciesJoinAllDoer = Doer(self.onFrequenciesJoinAll)
        self.FrequenciesJoinOffDiagonalDoer = Doer(self.onFrequenciesJoinOffDiagonal)
        self.FrequenciesJoinReciprocalsDoer = Doer(self.onFrequenciesJoinReciprocals)
        self.FrequenciesJoinReflectsDoer = Doer(self.onFrequenciesJoinReflects)
        self.TimesJoinAllDoer = Doer(self.onTimesJoinAll)
        self.TimesJoinOffDiagonalDoer = Doer(self.onTimesJoinOffDiagonal)
        self.TimesJoinReciprocalsDoer = Doer(self.onTimesJoinReciprocals)
        self.TimesJoinReflectsDoer = Doer(self.onTimesJoinReflects)
        self.VerticalJoinAllDoer = Doer(self.onVerticalJoinAll)
        self.VerticalJoinOffDiagonalDoer = Doer(self.onVerticalJoinOffDiagonal)
        self.VerticalJoinReciprocalsDoer = Doer(self.onVerticalJoinReciprocals)
        self.VerticalJoinReflectsDoer = Doer(self.onVerticalJoinReflects)
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
        PropertiesMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Properties',menu=PropertiesMenu,underline=0)
        #self.CalculationPropertiesDoer.AddMenuElement(PropertiesMenu,label='Calculation Properties',underline=0)
        self.SParameterPropertiesDoer.AddMenuElement(PropertiesMenu,label='S-parameter Properties',underline=0)
        #PropertiesMenu.add_separator()
        #PropertiesMenu.add_separator()
        self.EnforcePassivityDoer.AddMenuElement(PropertiesMenu,label='Enforce Passivity',underline=8)
        self.EnforceCausalityDoer.AddMenuElement(PropertiesMenu,label='Enforce Causality',underline=9)
        self.WaveletDenoiseDoer.AddMenuElement(PropertiesMenu,label='Wavelet Denoise',underline=0)
        # ------
        ViewMenu=tk.Menu(self)
        TheMenu.add_cascade(label='View',menu=ViewMenu,underline=0)
        self.VariableLineWidthDoer.AddCheckButtonMenuElement(ViewMenu,label='Variable Line Width',underline=9,onvalue=True,offvalue=False,variable=self.variableLineWidth)
        self.ShowPassivityViolationsDoer.AddCheckButtonMenuElement(ViewMenu,label='Show Passivity Violations',underline=5,onvalue=True,offvalue=False,variable=self.showPassivityViolations)
        self.ShowCausalityViolationsDoer.AddCheckButtonMenuElement(ViewMenu,label='Show Causality Violations',underline=6,onvalue=True,offvalue=False,variable=self.showCausalityViolations)
        self.ShowImpedanceDoer.AddCheckButtonMenuElement(ViewMenu,label='Show Impedance',underline=5,onvalue=True,offvalue=False,variable=self.showImpedance)
        self.LogScaleDoer.AddCheckButtonMenuElement(ViewMenu,label='Log Scale',underline=4,onvalue=True,offvalue=False,variable=self.logScale)
        #-------
        ZoomMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Zoom',menu=ZoomMenu,underline=0)
        ZoomFrequenciesMenu=tk.Menu(self)
        ZoomMenu.add_cascade(label='Frequencies',menu=ZoomFrequenciesMenu,underline=0)
        self.JoinFrequenciesWithinDoer.AddCheckButtonMenuElement(ZoomFrequenciesMenu,label='Join Within Views',underline=5,onvalue=True,offvalue=False,variable=self.JoinFrequenciesWithin)
        ZoomFrequenciesMenu.add_separator()
        self.JoinFrequenciesWithOthersDoer.AddCheckButtonMenuElement(ZoomFrequenciesMenu,label='Join With Other Views',underline=10,onvalue=True,offvalue=False,variable=self.JoinFrequenciesWithOthers)
        ZoomFrequenciesMenu.add_separator()
        self.FrequenciesJoinAllDoer.AddCheckButtonMenuElement(ZoomFrequenciesMenu,label='Join All Views',underline=5,onvalue=True,offvalue=False,variable=self.FrequenciesJoinAll)
        self.FrequenciesJoinOffDiagonalDoer.AddCheckButtonMenuElement(ZoomFrequenciesMenu,label='Join Off-Diagnonal Views',underline=9,onvalue=True,offvalue=False,variable=self.FrequenciesJoinOffDiagonal)
        self.FrequenciesJoinReciprocalsDoer.AddCheckButtonMenuElement(ZoomFrequenciesMenu,label='Join Reciprocal Views',underline=5,onvalue=True,offvalue=False,variable=self.FrequenciesJoinReciprocals)
        self.FrequenciesJoinReflectsDoer.AddCheckButtonMenuElement(ZoomFrequenciesMenu,label='Join Reflect Views',underline=7,onvalue=True,offvalue=False,variable=self.FrequenciesJoinReflects)
        ZoomTimesMenu=tk.Menu(self)
        ZoomMenu.add_cascade(label='Times',menu=ZoomTimesMenu,underline=0)
        self.JoinTimesWithinDoer.AddCheckButtonMenuElement(ZoomTimesMenu,label='Join Within Views',underline=5,onvalue=True,offvalue=False,variable=self.JoinTimesWithin)
        ZoomTimesMenu.add_separator()
        self.JoinTimesWithOthersDoer.AddCheckButtonMenuElement(ZoomTimesMenu,label='Join With Other Views',underline=10,onvalue=True,offvalue=False,variable=self.JoinTimesWithOthers)
        ZoomTimesMenu.add_separator()
        self.TimesJoinAllDoer.AddCheckButtonMenuElement(ZoomTimesMenu,label='Join All Views',underline=5,onvalue=True,offvalue=False,variable=self.TimesJoinAll)
        self.TimesJoinOffDiagonalDoer.AddCheckButtonMenuElement(ZoomTimesMenu,label='Join Off-Diagnonal Views',underline=9,onvalue=True,offvalue=False,variable=self.TimesJoinOffDiagonal)
        self.TimesJoinReciprocalsDoer.AddCheckButtonMenuElement(ZoomTimesMenu,label='Join Reciprocal Views',underline=5,onvalue=True,offvalue=False,variable=self.TimesJoinReciprocals)
        self.TimesJoinReflectsDoer.AddCheckButtonMenuElement(ZoomTimesMenu,label='Join Reflect Views',underline=7,onvalue=True,offvalue=False,variable=self.TimesJoinReflects)
        ZoomVerticalMenu=tk.Menu(self)
        ZoomMenu.add_cascade(label='Vertical',menu=ZoomVerticalMenu,underline=0)
        self.JoinMagnitudeWithOthersDoer.AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join Magnitude Zooms With Other Views',underline=None,onvalue=True,offvalue=False,variable=self.JoinMagnitudeWithOthers)
        self.JoinPhaseWithOthersDoer.AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join Phase Zooms With Other Views',underline=None,onvalue=True,offvalue=False,variable=self.JoinPhaseWithOthers)
        self.JoinImpulseWithOthersDoer.AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join Impulse Response Zooms With Other Views',underline=None,onvalue=True,offvalue=False,variable=self.JoinImpulseWithOthers)
        self.JoinStepImpedanceWithOthersDoer.AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join Step Response/Impedance Zooms With Other Views',underline=None,onvalue=True,offvalue=False,variable=self.JoinStepImpedanceWithOthers)
        ZoomVerticalMenu.add_separator()
        self.VerticalJoinAllDoer.AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join All Views',underline=5,onvalue=True,offvalue=False,variable=self.VerticalJoinAll)
        self.VerticalJoinOffDiagonalDoer.AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join Off-Diagnonal Views',underline=9,onvalue=True,offvalue=False,variable=self.VerticalJoinOffDiagonal)
        self.VerticalJoinReciprocalsDoer.AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join Reciprocal Views',underline=5,onvalue=True,offvalue=False,variable=self.VerticalJoinReciprocals)
        self.VerticalJoinReflectsDoer.AddCheckButtonMenuElement(ZoomVerticalMenu,label='Join Reflect Views',underline=7,onvalue=True,offvalue=False,variable=self.VerticalJoinReflects)
        # ------
        HelpMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Help',menu=HelpMenu,underline=0)
        self.HelpDoer.AddMenuElement(HelpMenu,label='Open Help File',underline=0)
        self.ControlHelpDoer.AddMenuElement(HelpMenu,label='Control Help',underline=0)

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

        self.topLeftFigure=Figure(figsize=(5,2), dpi=100)
        self.topLeftPlot=self.topLeftFigure.add_subplot(111)
        self.topLeftCanvas=FigureCanvasTkAgg(self.topLeftFigure, master=topLeftFrame)
        self.topLeftCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=1)
        self.topLeftToolbar = NavigationToolbar( self.topLeftCanvas, topLeftFrame ,self.onTopLeftHome)
        self.topLeftToolbar.update()
        self.topLeftCanvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.topLeftToolbar.pan()

        self.topRightFigure=Figure(figsize=(5,2), dpi=100)
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

        self.bottomLeftFigure=Figure(figsize=(5,2), dpi=100)
        self.bottomLeftPlot=self.bottomLeftFigure.add_subplot(111)
        self.bottomLeftCanvas=FigureCanvasTkAgg(self.bottomLeftFigure, master=bottomLeftFrame)
        self.bottomLeftCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=1)
        self.bottomLeftToolbar = NavigationToolbar( self.bottomLeftCanvas, bottomLeftFrame ,self.onBottomLeftHome)
        self.bottomLeftToolbar.update()
        self.bottomLeftCanvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.bottomLeftToolbar.pan()

        self.bottomRightFigure=Figure(figsize=(5,2), dpi=100)
        self.bottomRightPlot=self.bottomRightFigure.add_subplot(111)
        self.bottomRightCanvas=FigureCanvasTkAgg(self.bottomRightFigure, master=bottomRightFrame)
        self.bottomRightCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=1)
        self.bottomRightToolbar = NavigationToolbar( self.bottomRightCanvas, bottomRightFrame , self.onBottomRightHome)
        self.bottomRightToolbar.update()
        self.bottomRightCanvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.bottomRightToolbar.pan()

        controlsFrame = tk.Frame(self.dialogFrame)
        controlsFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.sButtonsFrame = tk.Frame(controlsFrame, bd=1, relief=tk.SUNKEN)
        self.sButtonsFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.NONE)

        self.sp=sp
        self.properties=SParameterProperties()
        self.UpdatePropertiesFromSParameters(new=True)

        if buttonLabels is None:
            numPorts=self.sp.m_P
            buttonLabels=[['s'+str(toP+1)+str(fromP+1) for fromP in range(numPorts)] for toP in range(numPorts)]
        else:
            # button labels are a proxy for transfer parameters (until I do something better)
            self.properties['Plot.ShowPassivityViolations']=False
            self.showPassivityViolations.set(False)
            self.ShowPassivityViolationsDoer.Activate(False)
            self.ShowCausalityViolationsDoer.Activate(False)
            self.ShowImpedanceDoer.Activate(False)
            #self.LogScaleDoer.Activate(False)
            self.EnforcePassivityDoer.Activate(False)
            self.EnforceCausalityDoer.Activate(False)
            self.WaveletDenoiseDoer.Activate(False)
            self.ReadSParametersFromFileDoer.Activate(False)

            self.properties['Zoom.Times.Join.All']=True
            self.properties['Zoom.Frequencies.Join.All']=True
            self.properties['Zoom.Vertical.Join.All']=True
            self.UpdatePropertiesFromSParameters()
            self.ZoomJoinActivations()

        self.buttonLabels=buttonLabels

        self.buttons=[]
        for toP in range(len(buttonLabels)):
            buttonrow=[]
            rowFrame=tk.Frame(self.sButtonsFrame)
            rowFrame.pack(side=tk.TOP,expand=tk.NO,fill=tk.NONE)
            for fromP in range(len(buttonLabels[0])):
                thisButton=tk.Button(rowFrame,text=buttonLabels[toP][fromP],width=len(buttonLabels[toP][fromP]),command=lambda x=toP+1,y=fromP+1: self.onSelectSParameter(x,y))
                thisButton.pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
                buttonrow.append(thisButton)
            self.buttons.append(buttonrow)

        self.fromPort = 1
        self.toPort = 1

        self.LimitChangeLock=False

        try:
            from matplotlib2tikz import save as tikz_save
        except:
            self.Matplotlib2tikzDoer.Activate(False)

        self.onSelectSParameter(self.toPort, self.fromPort)
#         self.buttons[self.toPort-1][self.fromPort-1].config(relief=tk.SUNKEN)
#         self.PlotSParameter()
        self.deiconify()
#         self.geometry("%+d%+d" % (self.parent.root.winfo_x()+self.parent.root.winfo_width()/2-self.winfo_width()/2,
#             self.parent.root.winfo_y()+self.parent.root.winfo_height()/2-self.winfo_height()/2))

    def onVariableLineWidth(self):
        self.properties['Plot.VariableLineWidth']=bool(self.variableLineWidth.get())
        self.PlotSParameter()

    def onShowPassivityViolations(self):
        self.properties['Plot.ShowPassivityViolations']=bool(self.showPassivityViolations.get())
        self.PlotSParameter()

    def onShowCausalityViolations(self):
        self.properties['Plot.ShowCausalityViolations']=bool(self.showCausalityViolations.get())
        self.PlotSParameter()

    def onShowImpedance(self):
        self.properties['Plot.ShowImpedance']=bool(self.showImpedance.get())
        self.PlotSParameter()

    def onLogScale(self):
        self.properties['Plot.LogScale']=bool(self.logScale.get())
        self.PlotSParameter()

    def ZoomJoinActivations(self):
        self.FrequenciesJoinAllDoer.Activate(self.properties['Zoom.Frequencies.JoinWithOthers'])
        self.FrequenciesJoinOffDiagonalDoer.Activate(self.properties['Zoom.Frequencies.JoinWithOthers']
            and not self.properties['Zoom.Frequencies.Join.All'])
        self.FrequenciesJoinReciprocalsDoer.Activate(self.properties['Zoom.Frequencies.JoinWithOthers']
            and not self.properties['Zoom.Frequencies.Join.All'] and not self.properties['Zoom.Frequencies.Join.OffDiagonal'])        
        self.FrequenciesJoinReflectsDoer.Activate(self.properties['Zoom.Frequencies.JoinWithOthers']
            and not self.properties['Zoom.Frequencies.Join.All'])
        self.TimesJoinAllDoer.Activate(self.properties['Zoom.Times.JoinWithOthers'])
        self.TimesJoinOffDiagonalDoer.Activate(self.properties['Zoom.Times.JoinWithOthers']
            and not self.properties['Zoom.Times.Join.All'])
        self.TimesJoinReciprocalsDoer.Activate(self.properties['Zoom.Times.JoinWithOthers']
            and not self.properties['Zoom.Times.Join.All'] and not self.properties['Zoom.Times.Join.OffDiagonal'])        
        self.TimesJoinReflectsDoer.Activate(self.properties['Zoom.Times.JoinWithOthers']
            and not self.properties['Zoom.Times.Join.All'])
        verticalsActive = self.properties['Zoom.Vertical.JoinMagnitudeWithOthers'] or\
                self.properties['Zoom.Vertical.JoinPhaseWithOthers'] or\
                self.properties['Zoom.Vertical.JoinImpulseWithOthers'] or\
                self.properties['Zoom.Vertical.JoinStepImpedanceWithOthers']
        self.VerticalJoinAllDoer.Activate(verticalsActive)
        self.VerticalJoinOffDiagonalDoer.Activate(verticalsActive
            and not self.properties['Zoom.Vertical.Join.All'])
        self.VerticalJoinReciprocalsDoer.Activate(verticalsActive
            and not self.properties['Zoom.Vertical.Join.All'] and not self.properties['Zoom.Vertical.Join.OffDiagonal'])        
        self.VerticalJoinReflectsDoer.Activate(verticalsActive
            and not self.properties['Zoom.Vertical.Join.All'])


    def onJoinFrequenciesWithin(self):
        self.properties['Zoom.Frequencies.JoinWithin']=bool(self.JoinFrequenciesWithin.get())
        self.ZoomJoinActivations()

    def onJoinTimesWithin(self):
        self.properties['Zoom.Times.JoinWithin']=bool(self.JoinTimesWithin.get())
        self.ZoomJoinActivations()

    def onJoinFrequenciesWithOthers(self):
        self.properties['Zoom.Frequencies.JoinWithOthers']=bool(self.JoinFrequenciesWithOthers.get())
        self.ZoomJoinActivations()

    def onJoinTimesWithOthers(self):
        self.properties['Zoom.Times.JoinWithOthers']=bool(self.JoinTimesWithOthers.get())
        self.ZoomJoinActivations()

    def onJoinMagnitudeWithOthers(self):
        self.properties['Zoom.Vertical.JoinMagnitudeWithOthers']=bool(self.JoinMagnitudeWithOthers.get())
        self.ZoomJoinActivations()

    def onJoinPhaseWithOthers(self):
        self.properties['Zoom.Vertical.JoinPhaseWithOthers']=bool(self.JoinPhaseWithOthers.get())
        self.ZoomJoinActivations()

    def onJoinImpulseWithOthers(self):
        self.properties['Zoom.Vertical.JoinImpulseWithOthers']=bool(self.JoinImpulseWithOthers.get())
        self.ZoomJoinActivations()

    def onJoinStepImpedanceWithOthers(self):
        self.properties['Zoom.Vertical.JoinStepImpedanceWithOthers']=bool(self.JoinStepImpedanceWithOthers.get())
        self.ZoomJoinActivations()

    def onFrequenciesJoinAll(self):
        self.properties['Zoom.Frequencies.Join.All']=bool(self.FrequenciesJoinAll.get())
        self.ZoomJoinActivations()

    def onFrequenciesJoinOffDiagonal(self):
        self.properties['Zoom.Frequencies.Join.OffDiagonal']=bool(self.FrequenciesJoinOffDiagonal.get())
        self.ZoomJoinActivations()

    def onFrequenciesJoinReciprocals(self):
        self.properties['Zoom.Frequencies.Join.Reciprocals']=bool(self.FrequenciesJoinReciprocals.get())
        self.ZoomJoinActivations()

    def onFrequenciesJoinReflects(self):
        self.properties['Zoom.Frequencies.Join.Reflects']=bool(self.FrequenciesJoinReflects.get())
        self.ZoomJoinActivations()

    def onTimesJoinAll(self):
        self.properties['Zoom.Times.Join.All']=bool(self.TimesJoinAll.get())
        self.ZoomJoinActivations()

    def onTimesJoinOffDiagonal(self):
        self.properties['Zoom.Times.Join.OffDiagonal']=bool(self.TimesJoinOffDiagonal.get())
        self.ZoomJoinActivations()

    def onTimesJoinReciprocals(self):
        self.properties['Zoom.Times.Join.Reciprocals']=bool(self.TimesJoinReciprocals.get())
        self.ZoomJoinActivations()

    def onTimesJoinReflects(self):
        self.properties['Zoom.Times.Join.Reflects']=bool(self.TimesJoinReflects.get())
        self.ZoomJoinActivations()

    def onVerticalJoinAll(self):
        self.properties['Zoom.Vertical.Join.All']=bool(self.VerticalJoinAll.get())
        self.ZoomJoinActivations()

    def onVerticalJoinOffDiagonal(self):
        self.properties['Zoom.Vertical.Join.OffDiagonal']=bool(self.VerticalJoinOffDiagonal.get())
        self.ZoomJoinActivations()

    def onVerticalJoinReciprocals(self):
        self.properties['Zoom.Vertical.Join.Reciprocals']=bool(self.VerticalJoinReciprocals.get())
        self.ZoomJoinActivations()

    def onVerticalJoinReflects(self):
        self.properties['Zoom.Vertical.Join.Reflects']=bool(self.VerticalJoinReflects.get())
        self.ZoomJoinActivations()

    def JoinIt(self,thisToPortToJoin,thisFromPortToJoin,category):
        zoomProperties=self.properties['Zoom'][category]['Join']
        if zoomProperties['All']:
            return True
        if (thisToPortToJoin == thisFromPortToJoin) and (self.fromPort == self.toPort) and zoomProperties['Reflects']:
            return True
        if (thisToPortToJoin != thisFromPortToJoin) and (self.fromPort != self.toPort) and zoomProperties['OffDiagonal']:
            return True
        if (thisToPortToJoin == self.fromPort) and (thisFromPortToJoin == self.toPort) and zoomProperties['Reciprocals']:
            return True
        return False

    def onTopLeftXLimitChange(self,ax):
        if not self.LimitChangeLock:
            self.LimitChangeLock=True
            xlim=ax.get_xlim()
            if not self.topLeftPlotProperties is None:
                self.topLeftPlotProperties['MinX']=xlim[0]
                self.topLeftPlotProperties['MaxX']=xlim[1]
                if self.properties['Zoom.Frequencies.JoinWithin']:
                    self.topRightPlotProperties['MinX']=self.topLeftPlotProperties['MinX']
                    self.topRightPlotProperties['MaxX']=self.topLeftPlotProperties['MaxX']
                    self.topRightPlot.set_xlim(left=self.topRightPlotProperties['MinX'])
                    self.topRightPlot.set_xlim(right=self.topRightPlotProperties['MaxX'])
                    self.topRightCanvas.draw()
                if self.properties['Zoom.Frequencies.JoinWithOthers']:
                    spPlotPropertiesToJoinFrom=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
                    for thisToPort in range(1,self.sp.m_P+1):
                        for thisFromPort in range(1,self.sp.m_P+1):
                            if self.JoinIt(thisToPort,thisFromPort,'Frequencies'):
                                spPlotPropertiesToJoinTo=self.properties['Plot.S'][thisToPort-1][thisFromPort-1]
                                spPlotPropertiesToJoinTo['Magnitude.XInitialized']=True
                                spPlotPropertiesToJoinTo['Magnitude.MinX']=spPlotPropertiesToJoinFrom['Magnitude.MinX']
                                spPlotPropertiesToJoinTo['Magnitude.MaxX']=spPlotPropertiesToJoinFrom['Magnitude.MaxX']
                                if self.properties['Zoom.Frequencies.JoinWithin']:
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
                if self.properties['Zoom.Vertical.JoinMagnitudeWithOthers']:
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
                if self.properties['Zoom.Frequencies.JoinWithin']:
                    self.topLeftPlotProperties['MinX']=self.topRightPlotProperties['MinX']
                    self.topLeftPlotProperties['MaxX']=self.topRightPlotProperties['MaxX']
                    self.topLeftPlot.set_xlim(left=self.topLeftPlotProperties['MinX'])
                    self.topLeftPlot.set_xlim(right=self.topLeftPlotProperties['MaxX'])
                    self.topLeftCanvas.draw()
                if self.properties['Zoom.Frequencies.JoinWithOthers']:
                    spPlotPropertiesToJoinFrom=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
                    for thisToPort in range(1,self.sp.m_P+1):
                        for thisFromPort in range(1,self.sp.m_P+1):
                            if self.JoinIt(thisToPort,thisFromPort,'Frequencies'):
                                spPlotPropertiesToJoinTo=self.properties['Plot.S'][thisToPort-1][thisFromPort-1]
                                spPlotPropertiesToJoinTo['Phase.XInitialized']=True
                                spPlotPropertiesToJoinTo['Phase.MinX']=spPlotPropertiesToJoinFrom['Phase.MinX']
                                spPlotPropertiesToJoinTo['Phase.MaxX']=spPlotPropertiesToJoinFrom['Phase.MaxX']
                                if self.properties['Zoom.Frequencies.JoinWithin']:
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
                if self.properties['Zoom.Vertical.JoinPhaseWithOthers']:
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
                if self.properties['Zoom.Times.JoinWithin']:
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
                if self.properties['Zoom.Times.JoinWithOthers']:
                    spPlotPropertiesToJoinFrom=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
                    for thisToPort in range(1,self.sp.m_P+1):
                        for thisFromPort in range(1,self.sp.m_P+1):
                            if self.JoinIt(thisToPort,thisFromPort,'Times'):
                                spPlotPropertiesToJoinTo=self.properties['Plot.S'][thisToPort-1][thisFromPort-1]
                                spPlotPropertiesToJoinTo['Impulse.XInitialized']=True
                                spPlotPropertiesToJoinTo['Impulse.MinX']=spPlotPropertiesToJoinFrom['Impulse.MinX']
                                spPlotPropertiesToJoinTo['Impulse.MaxX']=spPlotPropertiesToJoinFrom['Impulse.MaxX']
                                if self.properties['Zoom.Times.JoinWithin']:
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
                if self.properties['Zoom.Vertical.JoinImpulseWithOthers']:
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
                if self.properties['Zoom.Times.JoinWithin']:
                    if self.properties['Plot.ShowImpedance'] and (self.fromPort == self.toPort):
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
                if self.properties['Zoom.Times.JoinWithOthers']:
                    spPlotPropertiesToJoinFrom=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
                    for thisToPort in range(1,self.sp.m_P+1):
                        for thisFromPort in range(1,self.sp.m_P+1):
                            if self.JoinIt(thisToPort,thisFromPort,'Times'):
                                spPlotPropertiesToJoinTo=self.properties['Plot.S'][thisToPort-1][thisFromPort-1]
                                if self.properties['Plot.ShowImpedance'] and (self.fromPort == self.toPort):
                                    spPlotPropertiesToJoinTo['Impedance.XInitialized']=True
                                    spPlotPropertiesToJoinTo['Impedance.MinX']=spPlotPropertiesToJoinFrom['Impedance.MinX']
                                    spPlotPropertiesToJoinTo['Impedance.MaxX']=spPlotPropertiesToJoinFrom['Impedance.MaxX']
                                else:
                                    spPlotPropertiesToJoinTo['Step.XInitialized']=True
                                    spPlotPropertiesToJoinTo['Step.MinX']=spPlotPropertiesToJoinFrom['Step.MinX']
                                    spPlotPropertiesToJoinTo['Step.MaxX']=spPlotPropertiesToJoinFrom['Step.MaxX']
                                if self.properties['Zoom.Times.JoinWithin']:
                                    spPlotPropertiesToJoinTo['Impulse.XInitialized']=True
                                    spPlotPropertiesToJoinTo['Impulse.MinX']=spPlotPropertiesToJoinFrom['Impulse.MinX']
                                    spPlotPropertiesToJoinTo['Impulse.MaxX']=spPlotPropertiesToJoinFrom['Impulse.MaxX']
            self.LimitChangeLock=False

    def onBottomRightYLimitChange(self,ax):
        if not self.LimitChangeLock:
            self.LimitChangeLock=True
            ylim=ax.get_ylim()
            if not self.bottomRightPlotProperties is None:
                self.bottomRightPlotProperties['MinY']=ylim[0]
                self.bottomRightPlotProperties['MaxY']=ylim[1]
                if self.properties['Zoom.Vertical.JoinStepImpedanceWithOthers']:
                    spPlotPropertiesToJoinFrom=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
                    for thisToPort in range(1,self.sp.m_P+1):
                        for thisFromPort in range(1,self.sp.m_P+1):
                            if self.JoinIt(thisToPort,thisFromPort,'Vertical'):
                                spPlotPropertiesToJoinTo=self.properties['Plot.S'][thisToPort-1][thisFromPort-1]
                                if self.properties['Plot.ShowImpedance'] and (self.fromPort == self.toPort):
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
                ' steps, Z0='+ToSI(self.properties['ReferenceImpedance'],'Ohm'))
        else:
            self.statusbar.set(str(self.properties['FrequencyPoints']+1)+
                ' frequency points, last frequency is '+ToSI(self.properties['EndFrequency'],'Hz')+
                ', Unevenly spaced, Z0='+ToSI(self.properties['ReferenceImpedance'],'Ohm'))
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
        self.variableLineWidth.set(self.properties['Plot.VariableLineWidth'])
        self.showPassivityViolations.set(self.properties['Plot.ShowPassivityViolations'])
        self.showCausalityViolations.set(self.properties['Plot.ShowCausalityViolations'])
        self.showImpedance.set(self.properties['Plot.ShowImpedance'])
        self.logScale.set(self.properties['Plot.LogScale'])
        self.JoinFrequenciesWithin.set(self.properties['Zoom.Frequencies.JoinWithin'])
        self.JoinTimesWithin.set(self.properties['Zoom.Times.JoinWithin'])
        self.JoinFrequenciesWithOthers.set(self.properties['Zoom.Frequencies.JoinWithOthers'])
        self.JoinTimesWithOthers.set(self.properties['Zoom.Times.JoinWithOthers'])
        self.JoinMagnitudeWithOthers.set(self.properties['Zoom.Vertical.JoinMagnitudeWithOthers'])
        self.JoinPhaseWithOthers.set(self.properties['Zoom.Vertical.JoinPhaseWithOthers'])
        self.JoinImpulseWithOthers.set(self.properties['Zoom.Vertical.JoinImpulseWithOthers'])
        self.JoinStepImpedanceWithOthers.set(self.properties['Zoom.Vertical.JoinStepImpedanceWithOthers'])
        self.FrequenciesJoinAll.set(self.properties['Zoom.Frequencies.Join.All'])
        self.FrequenciesJoinOffDiagonal.set(self.properties['Zoom.Frequencies.Join.OffDiagonal'])
        self.FrequenciesJoinReciprocals.set(self.properties['Zoom.Frequencies.Join.Reciprocals'])
        self.FrequenciesJoinReflects.set(self.properties['Zoom.Frequencies.Join.Reflects'])
        self.TimesJoinAll.set(self.properties['Zoom.Times.Join.All'])
        self.TimesJoinOffDiagonal.set(self.properties['Zoom.Times.Join.OffDiagonal'])
        self.TimesJoinReciprocals.set(self.properties['Zoom.Times.Join.Reciprocals'])
        self.TimesJoinReflects.set(self.properties['Zoom.Times.Join.Reflects'])
        self.VerticalJoinAll.set(self.properties['Zoom.Vertical.Join.All'])
        self.VerticalJoinOffDiagonal.set(self.properties['Zoom.Vertical.Join.OffDiagonal'])
        self.VerticalJoinReciprocals.set(self.properties['Zoom.Vertical.Join.Reciprocals'])
        self.VerticalJoinReflects.set(self.properties['Zoom.Vertical.Join.Reflects'])
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

        y=fr.Response('dB')

        self.freqLabel=ToSI(fr.Frequencies()[-1],'Hz')[-3:]
        freqLabelDivisor=FromSI('1. '+self.freqLabel,'Hz')

        x=fr.Frequencies(freqLabelDivisor)

        if self.properties['Plot.ShowPassivityViolations']:
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

        if self.properties['Plot.VariableLineWidth']:
            if fastway:
                segments = [[[x[i],y[i]],[x[i+1],y[i+1]]] for i in range(len(x)-1)]
                slw=lw[:-1]
                lc = LineCollection(segments, linewidths=slw,color='blue')
                self.topLeftPlot.add_collection(lc)
            else:
                for i in range(len(x)-1):
                    if self.properties['Plot.LogScale']:
                        self.topLeftPlot.semilogx(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
                    else:
                        self.topLeftPlot.plot(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
        else:
            if self.properties['Plot.LogScale']:
                self.topLeftPlot.semilogx(x,y)
            else:
                self.topLeftPlot.plot(x,y)

        if self.properties['Plot.ShowPassivityViolations']:
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
            self.topLeftPlotProperties['MinY']=max(min(y)-1.,-60.0)
            self.topLeftPlotProperties['MaxY']=max(y)+1.
            self.topLeftPlotProperties['YInitialized']=True

        if self.properties['Plot.LogScale']:
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

        self.topLeftPlot.set_ylabel('magnitude (dB)',fontsize=10)
        self.topLeftPlot.set_xlabel('frequency ('+self.freqLabel+')',fontsize=10)

        TD = self.plotProperties['Delay']
        frph=fr._DelayBy(-TD)

        y=frph.Response('deg')

        x=frph.Frequencies(freqLabelDivisor)

        if self.properties['Plot.VariableLineWidth']:
            if fastway:
                segments = [[[x[i],y[i]],[x[i+1],y[i+1]]] for i in range(len(x)-1)]
                slw=lw[:-1]
                lc = LineCollection(segments, linewidths=slw,color='blue')
                self.topRightPlot.add_collection(lc)
            else:
                for i in range(len(x)-1):
                    if self.properties['Plot.LogScale']:
                        self.topRightPlot.semilogx(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
                    else:
                        self.topRightPlot.plot(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
        else:
            if self.properties['Plot.LogScale']:
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

        if self.properties['Plot.LogScale']:
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

            if self.properties['Plot.ShowCausalityViolations']:
                self.causalityViolations=[]
                Ts=1./ir.td.Fs/1e-9
                for k in range(len(x)):
                    if x[k]<=-Ts and abs(y[k])>0:
                        dotsize=max(min(20.,abs(y[k])/0.1*20.),1e-15)
                        self.causalityViolations.append([x[k],y[k],dotsize])
                self.bottomLeftPlot.scatter(
                    [c[0] for c in self.causalityViolations],
                    [c[1] for c in self.causalityViolations],
                    s=[c[2] for c in self.causalityViolations],
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

            firFilter=ir.FirFilter()
            stepWaveformTimeDescriptor=ir.td/firFilter.FilterDescriptor()
            stepWaveform=si.td.wf.StepWaveform(stepWaveformTimeDescriptor)
            stepResponse=stepWaveform*firFilter
            y=stepResponse.Values()
            x=stepResponse.Times(timeLabelDivisor)

            self.bottomRightToolbar.update()

            if self.properties['Plot.ShowImpedance'] and (self.fromPort == self.toPort):
                self.bottomRightlabel.config(text='Impdedance Profile')
                self.bottomRightPlotProperties=self.plotProperties['Impedance']
                Z0=self.properties['ReferenceImpedance']
                y=[3000. if (1-yv)<=.000001 else min(Z0*(1+yv)/(1-yv),3000) for yv in y]
                x=[xv/2 for xv in x]
                self.bottomRightPlot.set_ylabel('impedance (Ohms)',fontsize=10)
                self.bottomRightPlot.set_xlabel('length ('+timeLabel+')',fontsize=10)

                if not self.bottomRightPlotProperties['YInitialized']:
                    self.bottomRightPlotProperties['MinY']=min(min(y)*1.05,Z0-1)
            else:
                self.bottomRightlabel.config(text='Step Response')
                self.bottomRightPlotProperties=self.plotProperties['Step']
                self.bottomRightPlot.set_ylabel('amplitude',fontsize=10)
                self.bottomRightPlot.set_xlabel('time ('+timeLabel+')',fontsize=10)
                if not self.bottomRightPlotProperties['YInitialized']:
                    self.bottomRightPlotProperties['MinY']=min(min(y)*1.05,-0.1)

            self.bottomRightPlot.plot(x,y)

            if not self.bottomRightPlotProperties['XInitialized']:
                self.bottomRightPlotProperties['MinX']=min(x)
                self.bottomRightPlotProperties['MaxX']=max(x)
                self.bottomRightPlotProperties['XInitialized']=True
                if self.properties['Plot.ShowImpedance'] and (self.fromPort == self.toPort):
                    self.plotProperties['Step.MinX']=self.bottomRightPlotProperties['MinX']*2.0
                    self.plotProperties['Step.MaxX']=self.bottomRightPlotProperties['MaxX']*2.0
                    self.plotProperties['Step.XInitialized']=True
                else:
                    self.plotProperties['Impedance.MinX']=self.bottomRightPlotProperties['MinX']/2.0
                    self.plotProperties['Impedance.MaxX']=self.bottomRightPlotProperties['MaxX']/2.0
                    self.plotProperties['Impedance.XInitialized']=True
            if not self.bottomRightPlotProperties['YInitialized']:
                self.bottomRightPlotProperties['MaxY']=max(max(y)*1.05,0.1)
                self.bottomRightPlotProperties['YInitialized']=True

            self.bottomRightPlot.set_xlim(left=self.bottomRightPlotProperties['MinX'])
            self.bottomRightPlot.set_xlim(right=self.bottomRightPlotProperties['MaxX'])
            self.bottomRightPlot.set_ylim(bottom=self.bottomRightPlotProperties['MinY'])
            self.bottomRightPlot.set_ylim(top=self.bottomRightPlotProperties['MaxY'])

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
        if self.properties['Plot.VariableLineWidth']:
            if fastway:
                segments = [[[x[i],y[i]],[x[i+1],y[i+1]]] for i in range(len(x)-1)]
                slw=lw[:-1]
                lc = LineCollection(segments, linewidths=slw,color='blue')
                self.topRightPlot.add_collection(lc)
            else:
                for i in range(len(x)-1):
                    if self.properties['Plot.LogScale']:
                        self.topRightPlot.semilogx(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
                    else:
                        self.topRightPlot.plot(x[i:i+2],y[i:i+2],linewidth=lw[i],color='blue')
        else:
            if self.properties['Plot.LogScale']:
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

        if self.properties['Plot.LogScale']:
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
        self.topRightCanvas.draw()
        self.topRightToolbar.update()


    def onReadSParametersFromFile(self):
        filename=AskOpenFileName(filetypes=[('s-parameter files', ('*.s*p'))],
                                 initialdir=self.fileparts.AbsoluteFilePath(),
                                 initialfile=self.fileparts.FileNameWithExtension(),
                                 parent=self)
        if filename is None:
            return
        self.fileparts=FileParts(filename)
        if self.fileparts.fileext=='':
            return

        self.title('S-parameters: '+self.fileparts.FileNameTitle())

        self.sp=si.sp.SParameterFile(filename)
        self.UpdatePropertiesFromSParameters(new=True)
        for widget in self.sButtonsFrame.winfo_children():
            widget.destroy()
        numPorts=self.sp.m_P
        self.buttonLabels=[['s'+str(toP+1)+str(fromP+1) for fromP in range(numPorts)] for toP in range(numPorts)]
        self.buttons=[]
        for toP in range(numPorts):
            buttonrow=[]
            rowFrame=tk.Frame(self.sButtonsFrame)
            rowFrame.pack(side=tk.TOP,expand=tk.NO,fill=tk.NONE)
            for fromP in range(numPorts):
                thisButton=tk.Button(rowFrame,text=self.buttonLabels[toP][fromP],command=lambda x=toP+1,y=fromP+1: self.onSelectSParameter(x,y))
                thisButton.pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
                buttonrow.append(thisButton)
            self.buttons.append(buttonrow)
        self.fromPort = 1
        self.toPort = 1
        self.buttons[self.toPort-1][self.fromPort-1].config(relief=tk.SUNKEN)
        self.plotProperties=self.properties['Plot.S'][self.toPort-1][self.fromPort-1]
        self.delayViewerProperty.SetString(self.plotProperties['Delay'])
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
        filename=AskSaveAsFilename(parent=self,filetypes=[('tex', '.tex')],
                                   defaultextension='.tex',
                                   initialdir=self.fileparts.AbsoluteFilePath(),
                                   initialfile=self.fileparts.filename+'Magnitude.tex')
        if filename is None:
            return

        try:
            si.test.PlotTikZ(filename,self.topLeftFigure)
        except:
            messagebox.showerror('Export LaTeX','LaTeX could not be generated or written ')                
        fp=FileParts(filename.replace('Magnitude.tex', ''))
        filename=fp.filename

        filename=AskSaveAsFilename(parent=self,filetypes=[('tex', '.tex')],
                                   defaultextension='.tex',
                                   initialdir=self.fileparts.AbsoluteFilePath(),
                                   initialfile=filename+'Phase.tex')
        if filename is None:
            return

        try:
            si.test.PlotTikZ(filename,self.topRightFigure)
        except:
            messagebox.showerror('Export LaTeX','LaTeX could not be generated or written ')                
        fp=FileParts(filename.replace('Phase.tex', ''))
        filename=fp.filename

        filename=AskSaveAsFilename(parent=self,filetypes=[('tex', '.tex')],
                                   defaultextension='.tex',
                                   initialdir=self.fileparts.AbsoluteFilePath(),
                                   initialfile=filename+'ImpulseResponse.tex')
        if filename is None:
            return

        try:
            si.test.PlotTikZ(filename,self.bottomLeftFigure)
        except:
            messagebox.showerror('Export LaTeX','LaTeX could not be generated or written ')                
        fp=FileParts(filename.replace('ImpulseResponse.tex', ''))
        filename=fp.filename

        filename=AskSaveAsFilename(parent=self,filetypes=[('tex', '.tex')],
                                   defaultextension='.tex',
                                   initialdir=self.fileparts.AbsoluteFilePath(),
                                   initialfile=filename+'StepResponse.tex')
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

    def onWaveletDenoise(self):
        self.sp.WaveletDenoise()
        self.UpdatePropertiesFromSParameters()
        self.PlotSParameter()



