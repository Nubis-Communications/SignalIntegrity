"""
EquationsDialog.py
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
    import tkFont as font
    import tkMessageBox as messagebox
else:
    import tkinter as tk
    from tkinter import font
    from tkinter import messagebox

import os

import SignalIntegrity.App.Project
from SignalIntegrity.App.FilePicker import AskSaveAsFilename,AskOpenFileName
from SignalIntegrity.App.MenuSystemHelpers import Doer,StatusBar

import re

class EquationsDialog(tk.Toplevel):
    def __init__(self,parent):
        tk.Toplevel.__init__(self, parent)
        self.project='Equations'
        self.titleText='Equations'
        self.parent=parent
        self.__root = self
        self.withdraw()

        self.statusbar=StatusBar(self)

        # the Doers - the holder of the commands, menu elements, toolbar elements, and key bindings
        self.NewFileDoer = Doer(self.onNewFile)
        self.OpenFileDoer = Doer(self.onOpenFile)
        self.SaveFileDoer = Doer(self.onSaveFile)
        # ------
        self.ExitDoer = Doer(self.onExit)

        self.CutDoer = Doer(self.onCut)
        self.CopyDoer = Doer(self.onCopy)
        self.PasteDoer = Doer(self.onPaste)

        self.AutoDebugDoer = Doer(self.onAutoDebug).AddHelpElement('Control-Help:Equations-Auto-Debug').AddToolTip('Automatically debug script as edited')
        self.ExcuteDoer = Doer(self.onExecute).AddHelpElement('Control-Help:Equations-Execute').AddToolTip('Execute the script')

        self.AboutDoer = Doer(self.onAbout).AddHelpElement('sec:Equations')

        # The menu system
        TheMenu=tk.Menu(self)
        self.config(menu=TheMenu)
#         FileMenu=tk.Menu(self)
#         TheMenu.add_cascade(label='File',menu=FileMenu,underline=0)
#         self.NewFileDoer.AddMenuElement(FileMenu,label="New",accelerator='Ctrl+N',underline=0)
#         self.OpenFileDoer.AddMenuElement(FileMenu,label="Open",accelerator='Ctrl+O',underline=0)
#         self.SaveFileDoer.AddMenuElement(FileMenu,label="Save",accelerator='Ctrl+S',underline=0)
#         FileMenu.add_separator()
#         self.ExitDoer.AddMenuElement(FileMenu,label="Exit",accelerator='Ctrl+X',underline=1)
        # ------
        EditMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Edit',menu=EditMenu,underline=0)
        self.CutDoer.AddMenuElement(EditMenu,label="Cut",accelerator='Ctrl+C',underline=0)
        self.CopyDoer.AddMenuElement(EditMenu,label="Copy",accelerator='Ctrl+X',underline=1)
        self.PasteDoer.AddMenuElement(EditMenu,label="Paste",accelerator='Ctrl+V',underline=0)
        # ------
        DebugMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Debug',menu=DebugMenu,underline=0)
        self.ExcuteDoer.AddMenuElement(DebugMenu,label='Execute script',underline=0)
        DebugMenu.add_separator()
        self.AutoDebugDoer.AddCheckButtonMenuElement(DebugMenu,label='Auto debug',underline=0)
        self.AutoDebugDoer.Set(SignalIntegrity.App.Project['Equations.AutoDebug'])
        # ------
        HelpMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Help',menu=HelpMenu,underline=0)
        self.AboutDoer.AddMenuElement(HelpMenu,label='About',underline=0)

        # text area
        use_chlorophyll=True
        if use_chlorophyll:
            try:
                from chlorophyll import CodeView
                self.TextArea = CodeView(self.__root,height=1)
            except:
                self.TextArea = tk.Text(self.__root,height=1)
        else:
            self.TextArea = tk.Text(self.__root)
        self.TextArea.bind('<Button-1>',self.onTouched)
        self.TextArea.bind('<Return>',self.onTouched)
        self.TextArea.pack(expand=tk.TRUE, fill=tk.BOTH)
        thisfont = font.Font(font=self.TextArea['font'])
        # Set Tab size
        tab_size = thisfont.measure('    ')
        self.TextArea.config(tabs=tab_size)
        self.__file = None
        self.__root.title(self.titleText) 
        self.TextArea.insert(1.0,SignalIntegrity.App.Project[self.project].GetTextString())
        self.TextArea.config(height=min(25,max(1,len(SignalIntegrity.App.Project[self.project]['Lines']))))
        self.protocol("WM_DELETE_WINDOW", self.onExit)
        self.statusbar.pack(side=tk.BOTTOM,fill=tk.X,expand=tk.NO)
        # self.TextArea.bind(":", self.autoindent)
        self.onTouched()
        self.deiconify()

    def autoindent(self,event):
        # the text widget that received the event
        widget = event.widget

        # get current line
        line = widget.get("insert linestart", "insert lineend")

        # compute the indentation of the current line
        match = re.match(r'^(\s+)', line)
        current_indent = len(match.group(0)) if match else 0

        # compute the new indentation
        new_indent = current_indent + 4

        # insert the character that triggered the event,
        # a newline, and then new indentation
        widget.insert("insert", event.char + "\n" + " "*new_indent)

        # return 'break' to prevent the default behavior
        return "break"

    def onExit(self):
        SignalIntegrity.App.Project[self.project].PutTextString(self.TextArea.get(1.0,tk.END))
        self.parent.statusbar.set(self.titleText+' Modified')
        self.parent.history.Event('modify '+self.titleText)
        self.__root.destroy()
        self.parent.Drawing.DrawSchematic()

    def onAbout(self): 
        self.AboutDoer.OpenHelp()

    def onOpenFile(self): 
        self.__file = AskOpenFileName(defaultextension=".txt", 
                                    filetypes=[("All Files","*.*"), 
                                        ("Text Documents","*.txt")]) 
        if self.__file == "": 
            # no file to open 
            self.__file = None
        else:
            # Try to open the file 
            # set the window title 
            self.__root.title(os.path.basename(self.__file) + " - Notepad") 
            self.TextArea.delete(1.0,tk.END) 

            file = open(self.__file,"r") 

            self.TextArea.insert(1.0,file.read()) 

            file.close() 

    def onNewFile(self): 
        self.__root.title("Untitled - Notepad") 
        self.__file = None
        self.TextArea.delete(1.0,tk.END) 

    def onSaveFile(self): 

        if self.__file == None: 
            # Save as new file 
            self.__file = AskSaveAsFilename(initialfile='Untitled.txt', 
                                            defaultextension=".txt", 
                                            filetypes=[("All Files","*.*"), 
                                                ("Text Documents","*.txt")]) 

            if self.__file == "": 
                self.__file = None
            else: 
                # Try to save the file 
                file = open(self.__file,"w") 
                file.write(self.TextArea.get(1.0,tk.END)) 
                file.close() 
                # Change the window title 
                self.__root.title(os.path.basename(self.__file) + " - Notepad") 
        else: 
            file = open(self.__file,"w") 
            file.write(self.TextArea.get(1.0,tk.END)) 
            file.close() 

    def onCut(self): 
        self.TextArea.event_generate("<<Cut>>")

    def onCopy(self): 
        self.TextArea.event_generate("<<Copy>>")

    def onPaste(self): 
        self.TextArea.event_generate("<<Paste>>")

    def onAutoDebug(self):
        SignalIntegrity.App.Project['Equations.AutoDebug']=self.AutoDebugDoer.Bool()
        self.onTouched()

    def onExecute(self):
        self.onTouched(None,True)
        SignalIntegrity.App.Project[self.project].PutTextString(self.TextArea.get(1.0,tk.END))
        self.parent.Drawing.DrawSchematic()

    def onTouched(self,event=None,force=False):
        if force or SignalIntegrity.App.Project['Equations.AutoDebug']:
            result=SignalIntegrity.App.Project.EvaluateEquations(self.TextArea.get(1.0,tk.END))
            if result == None:
                self.statusbar.set('No Errors')
            else:
                self.statusbar.set(str(result))
        else:
            self.statusbar.set('')