'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from Tkinter import *
import os

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

class ToolBarElement(object):
    def __init__(self,frame,**kw):
        if 'iconfile' in kw:
            self.icon = PhotoImage(file=kw['iconfile'])
            del kw['iconfile']
            kw['image']=self.icon
        self.button=Button(frame,kw)
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
    def __init__(self,command,active=True):
        self.active=active
        self.command=command
        self.menuElement=None
        self.toolBarElement=None
        self.keyBindElement=None
        self.url=None
        self.helpEnabled=True
    def AddMenuElement(self,menu,**kw):
        kw['command']=self.Execute
        self.menuElement=MenuElement(menu,**kw)
        self.menuElement.Activate(self.active)
        return self.menuElement
    def AddToolBarElement(self,frame,**kw):
        kw['command']=self.Execute
        self.toolBarElement=ToolBarElement(frame,**kw)
        self.toolBarElement.Activate(self.active)
        return self.toolBarElement
    def AddKeyBindElement(self,bindTo,key):
        self.keyBindElement = KeyBindElement(bindTo,key,self.Execute)
        self.keyBindElement.Activate(self.active)
        return self
    def AddHelpElement(self,url):
        self.url=url
        return self
    def DisableHelp(self):
        self.helpEnabled=False
        return self
    def Execute(self,*args):
        if self.inHelp and self.helpEnabled:
            if not self.url is None:
                import webbrowser
                url = os.path.dirname(os.path.abspath(__file__))+'/Help/PySIHelp.html.LyXconv/'+self.url
                url=url.replace('\\','/')
                webbrowser.open(url)
            return
        if self.active:
            return self.command()
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

class StatusBar(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)
    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()
    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()