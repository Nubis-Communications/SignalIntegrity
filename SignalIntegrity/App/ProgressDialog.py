"""
ProgressDialog.py
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

from math import floor
       
class ProgressDialog(tk.Toplevel):
    def __init__(self, parent, title, classOfThing, thingToDo, granularity=1.0):
        tk.Toplevel.__init__(self, parent)
        self.parent=parent
        self.title(title)
        img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, img)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.barFrame=tk.Frame(self)
        self.barFrame.pack(side=tk.TOP)
        self.bar = tk.Canvas(self.barFrame,relief=tk.SUNKEN,borderwidth=1,width=600,height=10)
        self.bar.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)
        self.buttonFrame=tk.Frame(self)
        self.buttonFrame.pack(side=tk.TOP)
        self.stopButton = tk.Button(self.buttonFrame,text='Stop',command=self.onStop)
        self.stopButton.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.NO)
        self.stopCommand=False
        self.isShowing=False
        self.thingToDo = thingToDo
        self.classOfThing = classOfThing
        self.currentPercent = -1
        self.granularity = granularity
        self.geometry("%+d%+d" % (self.parent.root.winfo_x()+self.parent.root.winfo_width()/2-self.winfo_width()/2,
            self.parent.root.winfo_y()+self.parent.root.winfo_height()/2-self.winfo_height()/2))
        self.grab_set()

    def onStop(self):
        self.stopCommand=True
    def Callback(self,number):
        #return True
        if self.stopCommand:
            self.destroy()
            return False
        if not self.isShowing:
            pass
        self.isShowing=True
        if floor(number/self.granularity) != self.currentPercent:
            self.currentPercent = floor(number/self.granularity)  
            self.bar.create_rectangle(0,0,600*number/100.0,10,fill='blue')
            self.update()
        return True
    def GetResult(self):
        self.classOfThing.InstallCallback(self.Callback)
        self.Callback(0)
        try:
            self.result = self.thingToDo()
        except:
            raise
        finally:
            self.destroy()
            self.classOfThing.RemoveCallback()
        return self.result
