"""
NetListDialog.py
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

import tkinter as tk
from tkinter import scrolledtext

from SignalIntegrity.App.FilePicker import AskSaveAsFilename
# import SignalIntegrity.App.Project

class NetListFrame(tk.Frame):
    def __init__(self,parent,textToShow):
        tk.Frame.__init__(self,parent)
        self.title = 'NetList'
        self.text=scrolledtext.ScrolledText(self)
        self.text.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        for line in textToShow:
            self.text.insert(tk.END,line+'\n')
        self.text.configure(state='disabled')

class NetListDialog(tk.Toplevel):
    def __init__(self,parent,textToShow):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('NetList')
        self.textToShow=textToShow

        self.parent = parent

        self.result = None

        self.NetListFrame = NetListFrame(self,textToShow)
        self.initial_focus = self.body(self.NetListFrame)
        self.NetListFrame.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES,padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):
        extension='.txt'
        filename=AskSaveAsFilename(parent=self,
                                   filetypes=[('text', extension)],
                                   defaultextension='.txt',
                                   initialdir=self.parent.fileparts.AbsoluteFilePath(),
                                   initialfile=self.parent.fileparts.filename+'.txt')
        if filename is None:
            self.initial_focus.focus_set() # put focus back
            return
        with open(filename,"w") as f:
            for line in self.textToShow:
                f.write(line+'\n')

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1 # override

    def apply(self):
        pass

