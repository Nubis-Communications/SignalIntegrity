"""
BathtubCurveDialog.py
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
import numpy as np

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
from SignalIntegrity.Lib.TimeDomain.Waveform import Waveform

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

class BathtubCurveDialog(tk.Toplevel):
    def __init__(self, parent, name):
        tk.Toplevel.__init__(self, parent)
        self.parent=parent
        self.withdraw()
        self.name=name
        self.title('Bathtub Curve: '+name)
        self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        self.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.dialogFrame = tk.Frame(self, borderwidth=5)
        self.dialogFrame.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)
        self.deiconify()

    def onClosing(self):
        self.withdraw()
        self.destroy()

    def destroy(self):
        tk.Toplevel.withdraw(self)
        tk.Toplevel.destroy(self)

    def UpdateMeasurements(self,measDict):
        if (measDict is None) or (not 'Bathtub' in measDict.keys()):
            self.withdraw()
            return
        self.dialogFrame.pack_forget()
        self.dialogFrame = tk.Frame(self, borderwidth=5)
        self.dialogFrame.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)
        leftFrame=tk.Frame(self.dialogFrame)
        leftFrame.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES)
        rightFrame=tk.Frame(self.dialogFrame)
        rightFrame.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES,anchor=tk.NW)
        leftPlotFrame=tk.Frame(leftFrame)
        leftPlotFrame.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES)
        self.leftLabel = tk.Label(leftPlotFrame,fg='black')
        self.leftLabel.pack(fill=tk.X)
        numberOfEyes=len(measDict['Eye'])
        rightPlotFrames=[tk.Frame(rightFrame) for _ in range(numberOfEyes)]
        self.rightPlotLabels=[None for _ in range(numberOfEyes)]
        for e in range(numberOfEyes):
            rightPlotFrames[e].pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES,anchor=tk.NW)
            self.rightPlotLabels[e]=tk.Label(rightPlotFrames[e],fg='black')
            self.rightPlotLabels[e].pack(fill=tk.X)

        plotWidth=SignalIntegrity.App.Preferences['Appearance.PlotWidth']
        plotHeight=SignalIntegrity.App.Preferences['Appearance.PlotHeight']
        plotDPI=SignalIntegrity.App.Preferences['Appearance.PlotDPI']

        self.leftFigure=Figure(figsize=(plotWidth,plotHeight), dpi=plotDPI)
        self.leftPlot=self.leftFigure.add_subplot(111)
        self.leftCanvas=FigureCanvasTkAgg(self.leftFigure, master=leftPlotFrame)
        self.leftCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=1)
        self.leftToolbar = NavigationToolbar( self.leftCanvas, leftPlotFrame ,self.onLeftHome)
        self.leftToolbar.update()
        self.leftCanvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.leftToolbar.pan()

        self.rightFigures=[Figure(figsize=(plotWidth,plotHeight), dpi=plotDPI) for e in range(numberOfEyes)]
        self.rightPlots=[None for e in range(numberOfEyes)]
        self.rightCanvases=[None for e in range(numberOfEyes)]
        self.rightToolbars = [None for e in range(numberOfEyes)]

        for e in range(numberOfEyes):
            self.rightPlots[e]=self.rightFigures[e].add_subplot(111)
            self.rightCanvases[e]=FigureCanvasTkAgg(self.rightFigures[e], master=rightPlotFrames[e])
            self.rightCanvases[e].get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=1)
            self.rightToolbars[e]=NavigationToolbar( self.rightCanvases[e], rightPlotFrames[e] ,self.onRightHome)
            self.rightToolbars[e].update()
            self.rightCanvases[e]._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            self.rightToolbars[e].pan()

        self.leftPlot.cla()
        for e in range(len(self.rightPlots)):
            self.rightPlots[e].cla()

        if not SignalIntegrity.App.Preferences['Appearance.PlotCursorValues']:
            self.leftPlot.format_coord = lambda x, y: ''
            for e in range(len(self.rightPlots)):
                self.rightPlots[e].format_coord = lambda x, y: ''

        wf=measDict['Bathtub']['Vertical']['Data']
        x=wf['x']
        y=wf['y']

        self.voltLabel=' '+ToSI(x[-1],'V').split(' ')[-1]
        voltLabelDivisor=FromSI('1. '+self.voltLabel,'V')

        x=[v/voltLabelDivisor for v in x]

        lowerLimit=1e-30
        try:
            wf=measDict['Bathtub']['Vertical']['Level'][0]['LeftEst']['Est']['Wf']
            if not wf is None:
                self.leftPlot.semilogy([v/voltLabelDivisor for v in wf['x']],wf['y'],color='green',linewidth=6)
        except Exception as ex:
            print(ex)

        try:
            wf=measDict['Bathtub']['Vertical']['Level'][numberOfEyes]['RightEst']['Est']['Wf']
            if not wf is None:
                self.leftPlot.semilogy([v/voltLabelDivisor for v in wf['x']],wf['y'],color='green',linewidth=6)
        except Exception as ex:
            print(ex)

        for e in range(len(measDict['Bathtub']['Vertical']['Level'])):
            try:
                wf=measDict['Bathtub']['Vertical']['Level'][e]['RightEst']['Est']['Wf']
                if not wf is None:
                    self.leftPlot.semilogy([v/voltLabelDivisor for v in wf['x']],wf['y'],color='green',linewidth=6)
            except Exception as ex:
                print(ex)
            try:
                wf=measDict['Bathtub']['Vertical']['Level'][e]['LeftEst']['Est']['Wf']
                if not wf is None:
                    self.leftPlot.semilogy([v/voltLabelDivisor for v in wf['x']],wf['y'],color='green',linewidth=6)
            except Exception as ex:
                print(ex)
        # now, gather all of the curve fits and actual data into probability histograms that span the entire
        # eye
        for t in range(numberOfEyes+1):
            try:
                # probablity histogram
                yCombo=measDict['Bathtub']['Vertical']['Level'][t]['Hist']
                self.leftPlot.semilogy(x,[np.nan if v < lowerLimit else v for v in yCombo],color='green',linewidth=3)
                # compute the CDF from the left and the right
                self.leftPlot.semilogy(x,[np.nan if v < lowerLimit else v for v in measDict['Bathtub']['Vertical']['Level'][t]['CDFFromLeft']],color='red')
                self.leftPlot.semilogy(x,[np.nan if v < lowerLimit else v for v in measDict['Bathtub']['Vertical']['Level'][t]['CDFFromRight']],color='red')
            except Exception as ex:
                print(ex)
                pass

        y=[v if v != 0 else np.nan for v in y]
        self.leftPlot.semilogy(x,y,color='blue')

        for e in range(len(measDict['Eye'])):
            self.leftPlot.axvline(x=measDict['Eye'][e]['Decision']['Volt']/voltLabelDivisor, color='red',linestyle='--')

        self.leftLabel.config(text='Vertical Bathtub Curve')

        self.leftPlot.set_ylabel('probability',fontsize=10)
        self.leftPlot.set_xlabel('voltage ('+self.voltLabel+')',fontsize=10)

        self.leftPlot.grid(True, 'both')

        for ee in range(len(measDict['Bathtub']['Horizontal'])):
            e=numberOfEyes-1-ee

            wf=measDict['Bathtub']['Horizontal'][e]['Data']
            x=wf.Times()
            y=wf.Values()

            self.timeLabel=ToSI(x[-1],'s')[-3:]
            timeLabelDivisor=FromSI('1. '+self.timeLabel,'s')

            x=[v/timeLabelDivisor for v in x]
            y=[v if v != 0 else np.nan for v in y]
            self.rightPlots[ee].semilogy(x,y)
            self.rightPlots[ee].axvline(x=0.0, color='red',linestyle='--')

            self.rightPlotLabels[ee].config(text='Horizontal Bathtub Curve'+(f' for Eye {e}' if len(measDict['Bathtub']['Horizontal']) > 1 else ''))

            self.rightPlots[ee].set_ylabel('probability',fontsize=10)
            self.rightPlots[ee].set_xlabel('time ('+self.timeLabel+')',fontsize=10)

            self.rightPlots[ee].grid(True, 'both')
        self.deiconify()
    def onLeftHome(self):
        pass

    def onRightHome(self):
        pass