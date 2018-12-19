"""
DevicePicker.py
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
    import ttk
else:
    import tkinter as tk
    from tkinter import ttk

#from Device import *

class DevicePicker(tk.Frame):
    def __init__(self,parent,deviceList):
        tk.Frame.__init__(self,parent)
        self.config()
        self.tree = ttk.Treeview(self)
        self.tree.pack(fill=tk.BOTH,expand=tk.YES)
        self.tree["columns"]=("description")
        self.tree.column("description")
        self.tree.heading("description", text="Description")
        categories=[]
        indexIntoDeviceList=0
        for device in deviceList:
            parttype=device['partname'].GetValue()
            description='\ '.join(device['desc'].GetValue().split())
            category=device['cat'].GetValue()
            if category not in categories:
                self.tree.insert('','end',category,text=category,values=(category),tags='category')
                categories.append(category)
            self.tree.insert(category,'end',text=parttype,values=(description),tags=str(indexIntoDeviceList))
            indexIntoDeviceList=indexIntoDeviceList+1
        self.selected=None
        self.tree.bind('<<TreeviewSelect>>',self.onPartSelection)

    def onPartSelection(self,event):
        item = self.tree.selection()[0]
        self.selected=self.tree.item(item,'tags')[0]

class DevicePickerDialog(tk.Toplevel):
    def __init__(self,parent,deviceList):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Add Part')

        self.parent = parent

        self.result = None

        self.DevicePicker = DevicePicker(self,deviceList)
        self.initial_focus = self.body(self.DevicePicker)
        self.DevicePicker.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES,padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("500x500+%d+%d" % (parent.winfo_rootx()+50,
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

        w = tk.Button(box, text="OK", width=10, command=self.ok)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

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
        if (self.DevicePicker.selected != None):
            if self.DevicePicker.selected != 'category':
                self.result = int(self.DevicePicker.selected)
