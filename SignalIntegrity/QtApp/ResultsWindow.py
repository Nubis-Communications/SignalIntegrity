"""
ResultsWindow.py
"""
# Copyright (c) 2026 Nubis Communications, Inc.
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
from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT

def _PlotTab(figure):
    widget=QWidget()
    layout=QVBoxLayout(widget)
    canvas=FigureCanvasQTAgg(figure)
    layout.addWidget(NavigationToolbar2QT(canvas,widget))
    layout.addWidget(canvas)
    return widget

def _EngineeringAxis(values,unit):
    """@return (scale,label) so values*scale are in a readable SI prefix of unit"""
    peak=max((abs(v) for v in values),default=0.)
    for scale,prefix in ((1e-12,'T'),(1e-9,'G'),(1e-6,'M'),(1e-3,'k'),(1.,''),(1e3,'m'),(1e6,'u'),(1e9,'n'),(1e12,'p')):
        if peak*scale>=1. or scale==1e12:
            return scale,prefix+unit
    return 1.,unit

class ResultsWindow(QMainWindow):
    """shows calculation results from GuiCore.ProjectSession.Calculate as matplotlib plots"""
    def __init__(self,result,title='Results',parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(900,600)
        self.figures=[]
        tabs=QTabWidget()
        self.setCentralWidget(tabs)
        if result['waveforms']:
            figure=Figure(tight_layout=True)
            axes=figure.add_subplot(111)
            xs=[x for wf in result['waveforms'] for x in wf['x']]
            xscale,xlabel=_EngineeringAxis(xs,'s')
            for wf in result['waveforms']:
                axes.plot([x*xscale for x in wf['x']],wf['y'],label=wf['name'])
            axes.set_xlabel('time ('+xlabel+')')
            axes.set_ylabel('amplitude')
            axes.grid(True)
            axes.legend()
            self.figures.append(figure)
            tabs.addTab(_PlotTab(figure),'Waveforms')
        for sp in result['sparameters']:
            fscale,flabel=_EngineeringAxis(sp['frequencies'],'Hz')
            f=[v*fscale for v in sp['frequencies']]
            for quantity,ylabel in (('dB','magnitude (dB)'),('deg','phase (degrees)')):
                figure=Figure(tight_layout=True)
                axes=figure.add_subplot(111)
                for trace in sp['traces']:
                    axes.plot(f,trace[quantity],label=trace['name'])
                axes.set_xlabel('frequency ('+flabel+')')
                axes.set_ylabel(ylabel)
                axes.grid(True)
                if len(sp['traces'])<=16:
                    axes.legend()
                self.figures.append(figure)
                tabs.addTab(_PlotTab(figure),sp['name']+(' magnitude' if quantity=='dB' else ' phase'))
