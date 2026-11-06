"""
InformationDialog.py
"""

# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# Copyright (c) 2021-2025 Nubis Communications, Inc.
# Copyright (c) 2026 Ciena, Inc.
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

import tkinter as tk

import SignalIntegrity.App.Project
from SignalIntegrity.App.MenuSystemHelpers import ToolBarElement

class InformationMessage(tk.Toplevel):
    def __init__(self, parent, title, message):
        tk.Toplevel.__init__(self, parent)
        self.withdraw()
        self.parent=parent
        self.title(title)
        self.info=ToolBarElement(self,iconfile=SignalIntegrity.App.IconsDir+'dialog-information-4.gif',
                                borderwidth=0).button
        self.info.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES)
        self.label=tk.Label(self,height=3,width=50,text=message)
        self.label.pack(side=tk.LEFT,expand=tk.YES, fill=tk.BOTH)
        self.deiconify()
        self.lift(self.parent)
        self.update_idletasks()
        self.grab_set()
