"""
CalculationPropertiesProject.py
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
    import tkColorChooser as colorchooser
else:
    import tkinter as tk
    from tkinter import colorchooser

from SignalIntegrity.App.FilePicker import AskOpenFileName,AskSaveAsFilename
from SignalIntegrity.App.ToSI import FromSI,ToSI
from SignalIntegrity.App.Files import FileParts,ConvertFileNameToRelativePath
import SignalIntegrity.App.Project

class CalculationProperty(tk.Frame):
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,project=None,projectPath=None):
        tk.Frame.__init__(self,parentFrame)
        self.parentFrame=parentFrame
        self.enteredCallback=enteredCallback
        self.updateStringsCallback=updateStringsCallback
        self.project=project
        self.projectPath=projectPath
        self.pack(side=tk.TOP,fill=tk.X,expand=tk.YES)
        self.string=tk.StringVar()
        self.label = tk.Label(self,width=40,text=textLabel+': ',anchor='e')
        self.label.pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
        self.entry = tk.Entry(self,textvariable=self.string)
        self.entry.config(width=30,readonlybackground='light gray')
        self.entry.bind('<Return>',self.onEntered)
        self.entry.bind('<Tab>',self.onEntered)
        self.entry.bind('<Button-1>',self.onTouched)
        self.entry.bind('<Button-1>',self.onTouched)
        self.entry.bind('<Double-Button-1>',self.onCleared)
        self.entry.bind('<Button-3>',self.onUntouchedLoseFocus)
        self.entry.bind('<Escape>',self.onUntouchedLoseFocus)
        self.entry.bind('<FocusOut>',self.onUntouched)
        self.entry.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString((self.project[self.projectPath]))
        self.SetReadOnly(False)
    def SetReadOnly(self,readOnly=False):
        self.entry.config(state='readonly' if readOnly else tk.NORMAL)
    def SetString(self,value):
        self.string.set(value)
    def GetString(self):
        return self.string.get()
    def onEntered(self,event):
        if not ((self.project is None) or (self.projectPath is None)):
            if not self.GetString() is None:
                self.project[self.projectPath]=self.GetString()
        if not self.enteredCallback is None:
            self.enteredCallback(event)
        return self.onUntouchedLoseFocus(event)
    def onTouched(self,event):
        self.UpdateStrings()
    def onCleared(self,event):
        self.string.set('')
    def onUntouched(self,event):
        self.UpdateStrings()
    def onUntouchedLoseFocus(self,event):
        self.parentFrame.focus()
        return "break"
    def Show(self,whetherTo=True):
        if whetherTo:
            self.pack(side=tk.TOP,fill=tk.X,expand=tk.YES)
        else:
            self.pack_forget()
    def UpdateStrings(self):
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString((self.project[self.projectPath]))
        if not self.updateStringsCallback is None:
            self.updateStringsCallback()

class CalculationPropertyFileName(CalculationProperty):
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,fileparts,project=None,projectPath=None):
        self.fileparts=fileparts
        CalculationProperty.__init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,project,projectPath)
    def onTouched(self,event):
        fp=FileParts(self.fileparts.AbsoluteFilePath()+'/'+self.project[self.projectPath])
        filename=AskOpenFileName(filetypes=[('txt', '.txt')],
                                initialdir=fp.AbsoluteFilePath(),
                                initialfile=fp.FileNameWithExtension('txt'))
        if filename is None:
            return
        filename=ConvertFileNameToRelativePath(filename)
        self.project[self.projectPath]=filename
        self.UpdateStrings()

class CalculationPropertyFileNameSaveAs(CalculationProperty):
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,fileparts,project=None,projectPath=None):
        self.fileparts=fileparts
        CalculationProperty.__init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,project,projectPath)
    def onTouched(self,event):
        fp=FileParts(self.fileparts.AbsoluteFilePath()+'/'+self.project[self.projectPath])
        filename=AskSaveAsFilename(filetypes=[('txt', '.txt')],
                                   initialdir=fp.AbsoluteFilePath(),
                                   initialfile=fp.FileNameWithExtension('txt'))
        if filename is None:
            return
        filename=ConvertFileNameToRelativePath(filename)
        self.project[self.projectPath]=filename
        self.UpdateStrings()

class CalculationPropertySI(CalculationProperty):
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,project=None,projectPath=None,unit=None):
        self.unitString=unit
        CalculationProperty.__init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,project,projectPath)
    def SetString(self,value):
        try:
            self.string.set(ToSI(value,self.unitString))
        except:
            pass
    def GetString(self):
        return FromSI(self.string.get(),self.unitString)

class CalculationPropertyTrueFalseButton(tk.Frame):
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,project=None,projectPath=None):
        tk.Frame.__init__(self,parentFrame)
        self.parentFrame=parentFrame
        self.enteredCallback=enteredCallback
        self.updateStringsCallback=updateStringsCallback
        self.project=project
        self.projectPath=projectPath
        self.pack(side=tk.TOP,fill=tk.X,expand=tk.YES)
        self.string=tk.StringVar()
        self.label = tk.Label(self,width=40,text=textLabel+': ',anchor='e')
        self.label.pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
        self.entry = tk.Button(self,text='None',command=self.onPressed)
        self.entry.config(width=30)
        self.entry.bind('<Return>',self.onPressed)
        self.entry.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString(str(self.project[self.projectPath]))
    def SetString(self,value):
        self.string.set(value)
        self.entry.config(text=value)
    def GetString(self):
        return self.string.get()
    def onPressed(self,event=None):
        self.SetString('False' if self.GetString()=='True' else 'True')
        if not ((self.project is None) or (self.projectPath is None)):
            self.project[self.projectPath]=self.GetString()
        if not self.enteredCallback is None:
            self.enteredCallback(event)
        self.UpdateStrings()
    def Show(self,whetherTo=True):
        if whetherTo:
            self.pack(side=tk.TOP,fill=tk.X,expand=tk.YES)
        else:
            self.pack_forget()
    def UpdateStrings(self):
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString(str(self.project[self.projectPath]))
        if not self.updateStringsCallback is None:
            self.updateStringsCallback()

class CalculationPropertyChoices(tk.Frame):
    couplingChoices = [('50 Ohm', 'DC50'),('1 MOhm', 'DC1M')]
    bandwidthChoices = [('20 MHz', '20MHz'),('200 MHz','200MHz')]
    
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,choiceStrings,project=None,projectPath=None):
        tk.Frame.__init__(self,parentFrame)
        self.parentFrame=parentFrame
        self.enteredCallback=enteredCallback
        self.updateStringsCallback=updateStringsCallback
        self.choiceStrings=choiceStrings
        self.project=project
        self.projectPath=projectPath
        self.pack(side=tk.TOP,fill=tk.X,expand=tk.YES)
        self.string=tk.StringVar()
        self.label = tk.Label(self,width=40,text=textLabel+': ',anchor='e')
        self.label.pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
        self.entry = tk.Frame(self)
        self.entry.config(width=30,borderwidth=1,relief=tk.RAISED)
#         self.entry.bind('<Return>',self.onPressed)
#         self.entry.bind('<Tab>',self.onEntered)
        self.entry.bind('<Button-1>',self.onTouched)
#         self.entry.bind('<Double-Button-1>',self.onCleared)
#         self.entry.bind('<Button-3>',self.onUntouchedLoseFocus)
#         self.entry.bind('<Escape>',self.onUntouchedLoseFocus)
        self.entry.bind('<FocusOut>',self.onUntouched)
        self.entry.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        for text,value in self.choiceStrings:
            b = tk.Radiobutton(self.entry,text=text,variable=self.string,value=value,command=self.onPressed)
            b.pack(anchor=tk.W)
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString(str(self.project[self.projectPath]))
    def SetString(self,value):
        self.string.set(value)
        #self.entry.config(text=value)
    def GetString(self):
        return self.string.get()
    def onPressed(self,event=None):
        if not ((self.project is None) or (self.projectPath is None)):
            self.project[self.projectPath]=self.GetString()
        if not self.enteredCallback is None:
            self.enteredCallback(event)
        self.UpdateStrings()
    def onTouched(self,event):
        self.UpdateStrings()
    def onUntouched(self,event):
        self.UpdateStrings()
    def Show(self,whetherTo=True):
        if whetherTo:
            self.pack(side=tk.TOP,fill=tk.X,expand=tk.YES)
        else:
            self.pack_forget()
    def UpdateStrings(self):
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString(str(self.project[self.projectPath]))
        if not self.updateStringsCallback is None:
            self.updateStringsCallback()

class CalculationPropertyColor(tk.Frame):
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,project=None,projectPath=None):
        tk.Frame.__init__(self,parentFrame)
        self.parentFrame=parentFrame
        self.enteredCallback=enteredCallback
        self.updateStringsCallback=updateStringsCallback
        self.project=project
        self.projectPath=projectPath
        self.pack(side=tk.TOP,fill=tk.X,expand=tk.YES)
        self.string=tk.StringVar()
        self.label = tk.Label(self,width=40,text=textLabel+': ',anchor='e')
        self.label.pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
        self.entry = tk.Button(self,command=self.onPressed)
        self.entry.config(width=30)
        self.entry.bind('<Return>',self.onPressed)
        self.entry.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString(str(self.project[self.projectPath]))
    def SetString(self,value):
        self.string.set(value)
        try:
            self.entry.config(bg=value)
        except:
            pass
    def GetString(self):
        return self.string.get()
    def onPressed(self,event=None):
        color = colorchooser.askcolor()[1]
        if not color is None:
            self.SetString(color)
            if not ((self.project is None) or (self.projectPath is None)):
                self.project[self.projectPath]=self.GetString()
            if not self.enteredCallback is None:
                self.enteredCallback(event)
            self.UpdateStrings()
    def Show(self,whetherTo=True):
        if whetherTo:
            self.pack(side=tk.TOP,fill=tk.X,expand=tk.YES)
        else:
            self.pack_forget()
    def UpdateStrings(self):
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString(str(self.project[self.projectPath]))
        if not self.updateStringsCallback is None:
            self.updateStringsCallback()

class PropertiesDialog(tk.Toplevel):
    def __init__(self,parent,project,top,title):
        tk.Toplevel.__init__(self, parent)
        self.parent=parent
        self.top=top
        self.withdraw()
        self.title(title)
        img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, img)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.project=project
        self.propertyListFrame = tk.Frame(self,relief=tk.RIDGE, borderwidth=5)
        self.propertyListFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)

    def Finish(self):
#         (x,y)=(self.top.root.winfo_x()+self.top.root.winfo_width()/2-self.winfo_width()/2,
#             self.top.root.winfo_y()+self.top.root.winfo_height()/2-self.winfo_height()/2)
#         self.geometry("%+d%+d" % (x,y))
        self.deiconify()
    def onClosing(self):
        self.withdraw()
        self.destroy()
    def destroy(self):
        tk.Toplevel.withdraw(self)
        tk.Toplevel.destroy(self)
