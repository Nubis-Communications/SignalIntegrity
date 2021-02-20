"""
Projects.py
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
    from Tkinter import ttk
else:
    import tkinter as tk
    from tkinter import ttk

import SignalIntegrity.App.Project
from SignalIntegrity.App.ProjectFile import ProjectConfiguration,PageConfiguration

class Projects(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent
#         self.tabControl=ttk.Notebook(self)
#         self.tab1=ttk.Frame(self.tabControl)
#         self.tabControl.add(self.tab1,text='Page 1')
#         self.tabControl.pack(expand=1,fill=tk.BOTH)
#         self.canvas = tk.Canvas(self.tab1,relief=tk.SUNKEN,borderwidth=1,width=600,height=600)
#         self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
#         self.schematic = Schematic()
    def InitFromProject(self):
        drawingProperties=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        # the canvas and geometry must be set prior to the remainder of the schematic initialization
        # otherwise it will not be the right size.  In the past, the xml happened to have the drawing
        # properties first, which made it work, but it was an accident.
        #self.canvas.config(width=drawingProperties['Width'],height=drawingProperties['Height'])
        self.parent.root.geometry(drawingProperties['Geometry'].split('+')[0])
        self.schematic = Schematic()
        self.schematic.InitFromProject()
        self.stateMachine = DrawingStateMachine(self)

class Project(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent)