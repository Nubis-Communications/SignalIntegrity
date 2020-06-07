"""
MenuSystemHelpers.py
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

class ToolTip(object):
    """
    Tooltip recipe from
    http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml#e387
    """
    @staticmethod
    def createToolTip(widget, text):
        toolTip = ToolTip(widget)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + self.widget.winfo_rooty() - 27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class MenuElement(object):
    def __init__(self,menu,**kw):
        menu.add_command(kw)
        self.label=kw['label']
        self.menu=menu
        self.active=None
        if 'state' in kw:
            active=kw['state'] == 'normal'
        else:
            active=True
        self.Activate(active)
    def Activate(self,active):
        if active == self.active:
            return
        self.active=active
        self.menu.entryconfigure(self.label,state='normal' if self.active else 'disabled')

class CheckButtonMenuElement(object):
    def __init__(self,menu,**kw):
        menu.add_checkbutton(kw)
        self.label=kw['label']
        self.menu=menu
        self.active=None
        if 'state' in kw:
            active=kw['state'] == 'normal'
        else:
            active=True
        self.Activate(active)
    def Activate(self,active):
        if active == self.active:
            return
        self.active=active
        self.menu.entryconfigure(self.label,state='normal' if self.active else 'disabled')

class ToolBarElement(object):
    def __init__(self,frame,**kw):
        if 'iconfile' in kw:
            self.icon = tk.PhotoImage(file=kw['iconfile'])
            del kw['iconfile']
            kw['image']=self.icon
        self.button=tk.Button(frame,kw)
        self.active=None
        if 'state' in kw:
            active=kw['state'] == 'normal'
        else:
            active=True
        self.Activate(active)
    def Activate(self,active):
        if active == self.active:
            return
        self.active=active
        self.button.config(state='normal' if self.active else 'disabled')
    def Pack(self,**kw):
        self.button.pack(kw)
        return self

class KeyBindElement(object):
    def __init__(self,bindTo,key,func):
        self.bindTo=bindTo
        self.key=key
        self.func=func
        self.active=False
    def Activate(self,active):
        if active == self.active:
            return
        self.active=active
        if self.active:
            self.bindTo.bind(self.key,self.func)
        else:
            self.bindTo.unbind(self.key)

class Doer(object):
    inHelp=False
    helpKeys=None
    def __init__(self,command,active=True):
        self.active=active
        self.command=command
        self.menuElement=None
        self.toolBarElement=None
        self.keyBindElement=None
        self.controlHelpSectionString=None
        self.helpEnabled=True
        self.tooltiptext=None
    def AddMenuElement(self,menu,**kw):
        kw['command']=self.Execute
        self.menuElement=MenuElement(menu,**kw)
        self.menuElement.Activate(self.active)
        return self.menuElement
    def AddCheckButtonMenuElement(self,menu,**kw):
        self.variable=tk.BooleanVar()
        kw['variable']=self.variable
        kw['onvalue']=True
        kw['offvalue']=False
        kw['command']=self.Execute
        self.menuElement=CheckButtonMenuElement(menu,**kw)
        self.menuElement.Activate(self.active)
        return self.menuElement
    def AddToolBarElement(self,frame,**kw):
        kw['command']=self.Execute
        self.toolBarElement=ToolBarElement(frame,**kw)
        self.toolBarElement.Activate(self.active)
        if not self.tooltiptext == None:
            ToolTip(self.toolBarElement.button).createToolTip(self.toolBarElement.button, self.tooltiptext)
        return self.toolBarElement
    def AddKeyBindElement(self,bindTo,key):
        self.keyBindElement = KeyBindElement(bindTo,key,self.Execute)
        self.keyBindElement.Activate(self.active)
        return self
    def AddHelpElement(self,controlHelpSectionString):
        self.controlHelpSectionString=controlHelpSectionString
        return self
    def DisableHelp(self):
        self.helpEnabled=False
        return self
    def Execute(self,*args):
        if self.inHelp and self.helpEnabled:
            self.OpenHelp()
            return
        if self.active:
            return self.command()
    def OpenHelp(self):
        if not self.helpKeys is None:
            self.helpKeys.Open(self.controlHelpSectionString)
    def Activate(self,active):
        if self.active==active:
            return self
        self.active=active
        if self.menuElement is not None:
            self.menuElement.Activate(active)
        if self.toolBarElement is not None:
            self.toolBarElement.Activate(active)
        if self.keyBindElement is not None:
            self.keyBindElement.Activate(active)
        return self
    def Set(self,value):
        self.variable.set(value)
    def Bool(self):
        if self.active:
            return bool(self.variable.get())
        else:
            return False
    def AddToolTip(self,tooltiptext):
        self.tooltiptext=tooltiptext
        return self

class StatusBar(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.label.pack(fill=tk.X)
    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()
    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()
