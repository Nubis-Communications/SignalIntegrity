"""
About.py
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
    import ScrolledText as scrolledtext
else:
    import tkinter as tk
    from tkinter import scrolledtext
import webbrowser
import textwrap

from SignalIntegrity.__about__ import __version__,__url__,__copyright__,__description__,__author__,__email__,__project__
import SignalIntegrity.App.Project

class CreditsDialog(tk.Toplevel):
    def __init__(self,parent):
        self.parent=parent
        textToShow = [' '+__project__+' was written by:','','\t {} \t <{}>'.format(__author__,__email__)]
        tk.Toplevel.__init__(self, parent)
        self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.title('Credits')
        self.text=scrolledtext.ScrolledText(self,height=8,width=50)
        self.text.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        for line in textToShow:
            self.text.insert(tk.END,line+'\n')
        buttonsFrame = tk.Frame(self)
        buttonsFrame.pack(side=tk.TOP,expand=tk.YES,fill=tk.X,anchor='s')
        closeButton = tk.Button(buttonsFrame,text='Close',command=self.destroy)
        closeButton.pack(side=tk.LEFT,expand=tk.YES)
        self.text.focus_set()
        self.geometry("%+d%+d" % (self.parent.winfo_x()+self.parent.winfo_width()/2-self.winfo_width()/2,
            self.parent.winfo_y()+self.parent.winfo_height()/2-self.winfo_height()/2))
        self.text.configure(state='disabled')
 
class LicenseDialog(tk.Toplevel):
    def __init__(self,parent):
        self.parent=parent
        textToShow=[
            'Copyright (c) 2018 Teledyne LeCroy, Inc.',
            'All rights reserved worldwide.',
            '',
            'This file is part of SignalIntegrity.',
            '',
            'SignalIntegrity is free software: You can redistribute it and/or modify it under the terms',
            'of the GNU General Public License as published by the Free Software Foundation, either',
            'version 3 of the License, or any later version.',
            '',
            'This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;',
            'without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.',
            'See the GNU General Public License for more details.',
            '',
            'You should have received a copy of the GNU General Public License along with this program.',
            'If not, see <https://www.gnu.org/licenses/>']
        tk.Toplevel.__init__(self, parent)
        self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.gnuimg=tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'gpl.gif')
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.title('License')
        self.gnu=tk.Button(self,image=self.gnuimg,command=self.onHyper)
        self.gnu.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)
        self.text=scrolledtext.ScrolledText(self)
        self.text.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        for line in textToShow:
            self.text.insert(tk.END,line+'\n')
        buttonsFrame = tk.Frame(self)
        buttonsFrame.pack(side=tk.TOP,expand=tk.YES,fill=tk.X,anchor='s')
        closeButton = tk.Button(buttonsFrame,text='Close',command=self.destroy)
        closeButton.pack(side=tk.LEFT,expand=tk.YES)
        self.text.focus_set()
        self.geometry("%+d%+d" % (self.parent.winfo_x()+self.parent.winfo_width()/2-self.winfo_width()/2,
            self.parent.winfo_y()+self.parent.winfo_height()/2-self.winfo_height()/2))
        self.text.configure(state='disabled')
    def onHyper(self):
        webbrowser.open_new(r"https://www.gnu.org/licenses/gpl-3.0.html")

class AboutDialog(tk.Toplevel):
    def __init__(self,parent):
        self.parent = parent

        tk.Toplevel.__init__(self, parent)

        self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.img2 = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'tlecroy-logo-15.gif')
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.title('About '+__project__)
        self.focus_set()
        lecroyLabel = tk.Label(self,image=self.img2)
        lecroyLabel.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)
        iconLabel = tk.Label(self, image=self.img)
        iconLabel.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)
        msg = tk.Message(self,text=__description__,justify=tk.CENTER, width=500)
        msg.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)
        msg = tk.Message(self,text="version: %s on Python %d.%d" % (__version__,sys.version_info.major,sys.version_info.minor),justify=tk.CENTER, width=500)
        msg.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)
        msg = tk.Message(self,text=__copyright__,justify=tk.CENTER, width=500)
        msg.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)
        hyperLink = tk.Button(self,text=__url__, command=self.onHyper, borderwidth=0)
        hyperLink.pack(side=tk.TOP,expand=tk.YES,fill=tk.X)
        buttonsFrame = tk.Frame(self)
        buttonsFrame.pack(side=tk.TOP,expand=tk.YES,fill=tk.X,anchor='s')
        creditsButton = tk.Button(buttonsFrame,text='Credits', command=self.onCredits, width=10)
        creditsButton.pack(side=tk.LEFT,expand=tk.YES)
        licenseButton = tk.Button(buttonsFrame,text='License', command=self.onLicense, width=10)
        licenseButton.pack(side=tk.LEFT,expand=tk.YES)
        closeButton = tk.Button(buttonsFrame,text='Close',command=self.destroy, width=10)
        closeButton.pack(side=tk.LEFT,expand=tk.YES)
        self.geometry("%+d%+d" % (self.parent.root.winfo_x()+self.parent.root.winfo_width()/2-self.winfo_width()/2,
            self.parent.root.winfo_y()+self.parent.root.winfo_height()/2-self.winfo_height()/2))

    def onCredits(self):
        CreditsDialog(self)

    def onLicense(self):
        LicenseDialog(self)

    def onHyper(self):
        webbrowser.open_new(__url__)
