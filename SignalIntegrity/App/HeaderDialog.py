"""
HeaderDialog.py
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
#     import tkFont as font
else:
    import tkinter as tk
#     from tkinter import font

import os

import SignalIntegrity.App.Project    
from SignalIntegrity.App.FilePicker import AskSaveAsFilename,AskOpenFileName
from SignalIntegrity.App.MenuSystemHelpers import Doer
from SignalIntegrity.App.Files import FileParts

class HeaderDialog(tk.Toplevel):
    def __init__(self,parent, titleName=None, fileparts=None):
        self.parent = parent
        if isinstance(fileparts,FileParts):
            lines=''
            width=0
            try:
                with open(fileparts.FullFilePathExtension(),'rt') as f:
                    keepGoing = True
                    while keepGoing:
                        line = f.readline()
                        if line[0] in ['!',' ','#','\n']:
                            if line[0] == '!':
                                lines=lines+line[1:-1]+'\n'
                                width=max(len(line),width)
                        else:
                            keepGoing = False
            except:
                return
        elif isinstance(fileparts,list):
            lines=fileparts
            width=max([len(line) for line in lines])
            lines=''.join([line.strip('\n')+'\n' for line in lines])
        else:
            return

        tk.Toplevel.__init__(self, parent)
        self.parent=parent
        self.__root = self
        self.withdraw()

        # the Doers - the holder of the commands, menu elements, toolbar elements, and key bindings
        self.ExitDoer = Doer(self.onExit)

        self.CutDoer = Doer(self.onCut)
        self.CopyDoer = Doer(self.onCopy)
        self.PasteDoer = Doer(self.onPaste)

        self.AboutDoer = Doer(self.onAbout).AddHelpElement('sec:Header')

        # The menu system
        TheMenu=tk.Menu(self)
        self.config(menu=TheMenu)

        EditMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Edit',menu=EditMenu,underline=0)
        self.CutDoer.AddMenuElement(EditMenu,label="Cut",accelerator='Ctrl+C',underline=0)
        self.CopyDoer.AddMenuElement(EditMenu,label="Copy",accelerator='Ctrl+X',underline=1)
        self.PasteDoer.AddMenuElement(EditMenu,label="Paste",accelerator='Ctrl+V',underline=0)
        # ------
        HelpMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Help',menu=HelpMenu,underline=0)
        self.AboutDoer.AddMenuElement(HelpMenu,label='About',underline=0)

        # text area
        self.Scrollbar = tk.Scrollbar(self.__root)
        self.Scrollbar.pack(side=tk.RIGHT,fill=tk.Y)
        self.TextArea = tk.Text(self.__root,width=width)
        self.TextArea.pack(side=tk.LEFT,expand=tk.TRUE, fill=tk.BOTH)
        self.Scrollbar.config(command=self.TextArea.yview)
        self.TextArea.config(yscrollcommand = self.Scrollbar.set)
        self.__file = None
        self.__root.title("Header: "+titleName) 
        self.TextArea.insert(1.0,lines)
        self.protocol("WM_DELETE_WINDOW", self.onExit)
        if isinstance(fileparts,FileParts):
            self.TextArea.configure(state="disabled")
            self.CutDoer.Activate(False)
            self.PasteDoer.Activate(False)
        self.deiconify()

    def onExit(self):
        try:
            self.parent.sp.header=self.TextArea.get("1.0","end-1c").split('\n')[:-1]
        except:
            pass
        self.__root.destroy()

    def onAbout(self): 
        self.AboutDoer.OpenHelp()

    def onCut(self): 
        self.TextArea.event_generate("<<Cut>>") 

    def onCopy(self): 
        self.TextArea.event_generate("<<Copy>>") 

    def onPaste(self): 
        self.TextArea.event_generate("<<Paste>>") 
