"""
PictureDialog.py
"""
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# Copyright (c) 2021-2025 Nubis Communications, Inc.
# Copyright (c) 2026 Ciena, Inc.
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
from SignalIntegrity.App import MessageBox as messagebox
import base64
import io
from PIL import Image, ImageTk
from SignalIntegrity.App.FilePicker import AskSaveAsFilename,AskOpenFileName
from SignalIntegrity.App.MenuSystemHelpers import Doer

class PictureDialog(tk.Toplevel):
    def __init__(self,parent, pil_image, titleName=None):
        self.parent = parent
        tk.Toplevel.__init__(self, parent)
        self.title(titleName)
        self.parent=parent
        self.__root = self
        self.withdraw()

        # the Doers - the holder of the commands, menu elements, toolbar elements, and key bindings
        self.LoadFileDoer = Doer(self.onLoadFile)
        self.SaveFileDoer = Doer(self.onSaveFile)
        # ------
        self.ExitDoer = Doer(self.onExit)

        #self.CutDoer = Doer(self.onCut)
        self.DeleteDoer = Doer(self.onDelete).AddKeyBindElement(self,'<Control-d>')
        self.CopyDoer = Doer(self.onCopy).AddKeyBindElement(self,'<Control-x>')
        self.PasteDoer = Doer(self.onPaste).AddKeyBindElement(self,'<Control-v>')

        self.AboutDoer = Doer(self.onAbout).AddHelpElement(help)

        # The menu system
        TheMenu=tk.Menu(self)
        self.config(menu=TheMenu)
        FileMenu=tk.Menu(self)
        TheMenu.add_cascade(label='File',menu=FileMenu,underline=0)
        self.LoadFileDoer.AddMenuElement(FileMenu,label="Open",accelerator='Ctrl+O',underline=0)
        self.SaveFileDoer.AddMenuElement(FileMenu,label="Save",accelerator='Ctrl+S',underline=0)
        FileMenu.add_separator()
        self.ExitDoer.AddMenuElement(FileMenu,label="Exit",accelerator='Ctrl+X',underline=1)
        # ------
        EditMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Edit',menu=EditMenu,underline=0)
        # self.CutDoer.AddMenuElement(EditMenu,label="Cut",accelerator='Ctrl+C',underline=0)
        self.DeleteDoer.AddMenuElement(EditMenu,label='Delete',accelerator='Ctrl+D',underline=0)
        self.CopyDoer.AddMenuElement(EditMenu,label="Copy",accelerator='Ctrl+X',underline=0)
        self.PasteDoer.AddMenuElement(EditMenu,label="Paste",accelerator='Ctrl+V',underline=0)
        # ------
        HelpMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Help',menu=HelpMenu,underline=0)
        self.AboutDoer.AddMenuElement(HelpMenu,label='About',underline=0)

        try:
            import pyperclipimg
            self.CopyDoer.Activate(True)
            self.PasteDoer.Activate(True)
        except:
            self.CopyDoer.Activate(False)
            self.PasteDoer.Activate(False)

        self.pil_image = pil_image
        if not self.pil_image is None:
            try:
                self.image = ImageTk.PhotoImage(pil_image) 

                self.imageFrame=tk.Frame(self, relief=tk.RIDGE, borderwidth=5)
                self.imageFrame.pack()
                image_label = tk.Label(self.imageFrame, image=self.image)
                image_label.pack(padx=10, pady=10)
            except:
                self.image = None
        else:
            self.image = None
        self.resizable(width=False, height=False)
        self.deiconify()

    def onLoadFile(self):
        self.onExit()
        self.parent.onEmbedPicture()
        self.parent.onViewPicture()

    def onSaveFile(self):
        fp=self.parent.fileparts
        filename = AskSaveAsFilename(filetypes=[('pictures', ('*.png', '*.jpg','*.bmp'))],
                                     initialdir=fp.AbsoluteFilePath(),
                                     initialfile=fp.FileNameWithExtension('.png'),
                                     parent=self)
        if filename == None:
            return
        try:
            self.pil_image.save(filename)
        except:
            messagebox.showerror('picture', 'image could not be saved')
            return

    def onDelete(self):
        if not messagebox.askokcancel('picture', 'Are you sure you want to delete the picture?'):
            return
        self.onExit()
        self.parent.onDeletePicture()

    def onCut(self):
        pass

    def onCopy(self):
        try:
            import pyperclipimg
            pyperclipimg.copy(self.pil_image)
        except:
            messagebox.showerror('picture','could not copy image to clipboard')

    def onPaste(self):
        self.onExit()
        self.parent.onPastePicture()

    def onExit(self):
        self.__root.destroy()

    def onAbout(self):
        pass

    @staticmethod
    def encode_image_to_base64_lines(image_data, line_length=76):
            base64_encoded_bytes = base64.b64encode(image_data)
            base64_string = base64_encoded_bytes.decode('utf-8')
            lines = [base64_string[i:i + line_length]+'\n' for i in range(0, len(base64_string), line_length)]
            return lines

    @staticmethod
    def encode_image_file_to_base64_lines(image_path, line_length=76):
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            return PictureDialog.encode_image_to_base64_lines(image_data,line_length)

    @staticmethod
    def uudecode_to_photoimage_from_text(text):
        decoded_bytes = base64.b64decode(text)
        image_stream = io.BytesIO(decoded_bytes)
        pil_image = Image.open(image_stream)
        return pil_image
