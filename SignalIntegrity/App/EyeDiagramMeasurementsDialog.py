"""
EyeDiagramMeasurementsDialog.py
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
import SignalIntegrity.App.Preferences
from SignalIntegrity.App.ToSI import ToSI

class EyeDiagramMeasurementsDialog(tk.Toplevel):
    labelwidth=25
    entrywidth=10
    def __init__(self, parent, name):
        tk.Toplevel.__init__(self, parent)
        self.parent=parent
        self.withdraw()
        self.name=name
        self.title('Eye Diagram: '+name)
        self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        self.protocol("WM_DELETE_WINDOW", self.onClosing)

        self.ParametersFrame=tk.Frame(self,relief=tk.RIDGE,borderwidth=5)
        self.ParametersFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)

        self.bind('<FocusIn>',self.onFocus)
        self.resizable(False, False)
        self.deiconify()
        self.lift()

    def onFocus(self,event):
        if event.widget == self:
            if self.parent.winfo_exists():
                self.parent.lift()
                self.lift()

    def onClosing(self):
        self.withdraw()
        self.destroy()

    def destroy(self):
        tk.Toplevel.withdraw(self)
        tk.Toplevel.destroy(self)

    def Line2(self,text):
        line=tk.Label(self.ParametersFrame,text=text,font='fixedsys')
        line.pack(side=tk.TOP,expand=tk.NO,fill=tk.X)

    def SingleLine(self,label,textEntry):
        lineFrame=tk.Frame(self.ParametersFrame)
        lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        text=label.ljust(self.labelwidth)
        line=tk.Label(lineFrame,text=text,font='fixedsys',width=self.labelwidth)
        line.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        entryFrame=tk.Frame(lineFrame,relief=tk.RIDGE,borderwidth=5)
        entryFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        entry=tk.Label(entryFrame,width=self.entrywidth,text=textEntry)
        entry.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)


    def Fields2(self,category,parameter,subparameter,label,unit=None):
        lineFrame=tk.Frame(self.ParametersFrame)
        lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        text=label.ljust(self.labelwidth)
        line=tk.Label(lineFrame,text=text,font='fixedsys')
        line.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        for e in range(len(self.meas[category])):
            entryFrame=tk.Frame(lineFrame,relief=tk.RIDGE,borderwidth=5)
            entryFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            entry=tk.Label(entryFrame,width=self.entrywidth,text=ToSI(self.meas[category][e][parameter][subparameter],unit))
            entry.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)

    def UpdateMeasurements(self,meas):
        self.withdraw()
        self.meas=meas
        if self.meas==None:
            return
        self.ParametersFrame.pack_forget()
        self.ParametersFrame=tk.Frame(self,relief=tk.RIDGE,borderwidth=5)
        self.ParametersFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        topline=''.join(['Eye'.ljust(self.labelwidth)]+[str(eye).center(self.entrywidth-1) for eye in range(len(self.meas['Eye']))]+[''.ljust(self.entrywidth-1)])
        self.Line2(topline)
        self.Line2('Timing')
        self.Fields2('Eye','Start','Time','Start','s')
        self.Fields2('Eye','End','Time','End','s')
        self.Fields2('Eye','Width','Time','Width','s')
        self.Line2('')
        self.Line2('Vertical')
        self.Fields2('Eye','Low','Volt','Low','V')
        self.Fields2('Eye','Mid','Volt','Midpoint','V')
        self.Fields2('Eye','High','Volt','High','V')
        self.Fields2('Eye','Height','Volt','Height','V')
        self.Fields2('Eye','AV','Volt','AV','V')
        self.Line2('')
        line=''.join(['Thresholds'.ljust(self.labelwidth)]+[str(th).center(self.entrywidth-1) for th in range(len(self.meas['Level']))])
        self.Line2(line)
        self.Fields2('Level','Min','Volt','Min','V')
        self.Fields2('Level', 'Max', 'Volt', 'Max','V')
        self.Fields2('Level', 'Delta', 'Volt', 'Delta','V')
        self.Fields2('Level', 'Mean', 'Volt', 'Mean','V')
        self.Line2('')
        self.SingleLine('Eye Linearity',ToSI(self.meas['Linearity']*100.,'%'))
        try:
            self.SingleLine('RLM',ToSI(self.meas['RLM']*100.,'%'))
        except:
            pass
        self.Line2('')
        self.SingleLine('Vertical Resolution',ToSI(self.meas['VerticalResolution'],'V'))
        self.SingleLine('Horizontal Resolution',ToSI(self.meas['HorizontalResolution'],'s'))
        self.deiconify()
