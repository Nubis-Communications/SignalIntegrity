"""
Pages.py
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

from SignalIntegrity.App.Drawing import Drawing

class Pages(tk.Frame):
    def __init__(self,parent,root):
        tk.Frame.__init__(self,parent)
        self.parent=parent
        self.root=root
        self.tabControl=ttk.Notebook(self)
        selectedProject=SignalIntegrity.App.Project['Selected']
        self.tabList=[ttk.Frame(self.tabControl) for _ in range(len(selectedProject['Pages']))]
        for t in range(len(self.tabList)):
            self.tabControl.add(self.tabList[t],text=f'Page {t}')
        self.tabControl.pack(expand=1,fill=tk.BOTH)
        selectedPage=selectedProject['Selected']
        self.drawingList=[None for _ in range(len(self.tabList))]
        self.drawingList[selectedPage] = Drawing(self,root)

class Page(tk.Frame):