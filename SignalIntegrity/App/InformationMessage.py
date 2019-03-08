"""
InformationDialog.py
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
else:
    import tkinter as tk

import SignalIntegrity.App.Project

class InformationMessage(tk.Toplevel):
    def __init__(self, parent, title, message):
        tk.Toplevel.__init__(self, parent)
        self.withdraw()
        self.parent=parent
        self.title(title)
        #img = tk.PhotoImage(file=SignalIntegrity.App.IconsDir+'dialog-information-4.gif')
        #self.tk.call('wm', 'iconphoto', self._w, img)
        #self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.infoimg=tk.PhotoImage(file=SignalIntegrity.App.IconsDir+'dialog-information-4.gif')
        self.info=tk.Button(self,image=self.infoimg,borderwidth=0)
        self.info.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES)
        self.label=tk.Label(self,height=3,width=50,text=message)
        self.label.pack(side=tk.LEFT,expand=tk.YES, fill=tk.BOTH)
        self.deiconify()
        self.lift(self.parent)
        self.update_idletasks()
        self.grab_set()