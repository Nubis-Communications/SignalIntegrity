"""
PostProcessingDialog.py
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

class PostProcessingDialog(tk.Toplevel):
    def __init__(self,parent,title=None,width=300,height=300):
        tk.Toplevel.__init__(self, parent)
        self.parent=parent
        self.__root = self
        self.withdraw()
    # default window width and height 
        self.__thisWidth = width
        self.__thisHeight = height
        self.__thisTextArea = tk.Text(self.__root)
        self.__thisTextArea.pack()
        self.__thisMenuBar = tk.Menu(self.__root) 
        self.__thisFileMenu = tk.Menu(self.__thisMenuBar, tearoff=0) 
        self.__thisEditMenu = tk.Menu(self.__thisMenuBar, tearoff=0) 
        self.__thisHelpMenu = tk.Menu(self.__thisMenuBar, tearoff=0) 
    
    # To add scrollbar 
        #self.__thisScrollBar = tk.Scrollbar(self.__thisTextArea)
        #self.__thisScrollBar.pack()     
        self.__file = None

        # Set the window text 
        self.__root.title("Post-Processing") 

#         # Center the window 
#         screenWidth = self.__root.winfo_screenwidth() 
#         screenHeight = self.__root.winfo_screenheight() 
#     
#         # For left-alling 
#         left = (screenWidth / 2) - (self.__thisWidth / 2) 
#         
#         # For right-allign 
#         top = (screenHeight / 2) - (self.__thisHeight /2) 
#         
#         # For top and bottom 
#         self.__root.geometry('%dx%d+%d+%d' % (self.__thisWidth, 
#                                             self.__thisHeight, 
#                                             left, top)) 
# 
#         # To make the textarea auto resizable 
#         self.__root.grid_rowconfigure(0, weight=1) 
#         self.__root.grid_columnconfigure(0, weight=1) 

        # Add controls (widget) 
        #self.__thisTextArea.grid(sticky = tk.N + tk.E + tk.S + tk.W)
        #frame=tk.Frame(self)
        #frame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
 
        #self.__thisTextArea.pack(frame)
        
        # To open new file 
        self.__thisFileMenu.add_command(label="New", 
                                        command=self.__newFile)     
        
        # To open a already existing file 
        self.__thisFileMenu.add_command(label="Open", 
                                        command=self.__openFile) 
        
        # To save current file 
        self.__thisFileMenu.add_command(label="Save", 
                                        command=self.__saveFile)     

        # To create a line in the dialog         
        self.__thisFileMenu.add_separator()                                         
        self.__thisFileMenu.add_command(label="Exit", 
                                        command=self.__quitApplication) 
        self.__thisMenuBar.add_cascade(label="File", 
                                    menu=self.__thisFileMenu)     
        
        # To give a feature of cut 
        self.__thisEditMenu.add_command(label="Cut", 
                                        command=self.__cut)             
    
        # to give a feature of copy     
        self.__thisEditMenu.add_command(label="Copy", 
                                        command=self.__copy)         
        
        # To give a feature of paste 
        self.__thisEditMenu.add_command(label="Paste", 
                                        command=self.__paste)         
        
        # To give a feature of editing 
        self.__thisMenuBar.add_cascade(label="Edit", 
                                    menu=self.__thisEditMenu)     
        
        # To create a feature of description of the notepad 
        self.__thisHelpMenu.add_command(label="About Notepad", 
                                        command=self.__showAbout) 
        self.__thisMenuBar.add_cascade(label="Help", 
                                    menu=self.__thisHelpMenu) 

        self.__root.config(menu=self.__thisMenuBar) 

        #self.__thisScrollBar.pack(side=tk.RIGHT,fill=tk.Y)                     
        
        # Scrollbar will adjust automatically according to the content         
        #self.__thisScrollBar.config(command=self.__thisTextArea.yview)     
        #self.__thisTextArea.config(yscrollcommand=self.__thisScrollBar.set)
        self.__thisTextArea.insert(1.0,SignalIntegrity.App.Project['PostProcessing'].GetTextString())
        self.protocol("WM_DELETE_WINDOW", self.__quitApplication)
        self.deiconify()
        return
        
    def __quitApplication(self):
        SignalIntegrity.App.Project['PostProcessing'].PutTextString(self._PostProcessingDialog__thisTextArea.get(1.0,tk.END))
        self.parent.statusbar.set('Post-Processing Modified')
        self.parent.history.Event('modify post-processing')
        self.__root.destroy()

    def __showAbout(self): 
        tk.showinfo("Notepad","Mrinal Verma") 

    def __openFile(self): 
        
        self.__file = askopenfilename(defaultextension=".txt", 
                                    filetypes=[("All Files","*.*"), 
                                        ("Text Documents","*.txt")]) 

        if self.__file == "": 
            
            # no file to open 
            self.__file = None
        else: 
            
            # Try to open the file 
            # set the window title 
            self.__root.title(os.path.basename(self.__file) + " - Notepad") 
            self.__thisTextArea.delete(1.0,tk.END) 

            file = open(self.__file,"r") 

            self.__thisTextArea.insert(1.0,file.read()) 

            file.close() 

        
    def __newFile(self): 
        self.__root.title("Untitled - Notepad") 
        self.__file = None
        self.__thisTextArea.delete(1.0,tk.END) 

    def __saveFile(self): 

        if self.__file == None: 
            # Save as new file 
            self.__file = asksaveasfilename(initialfile='Untitled.txt', 
                                            defaultextension=".txt", 
                                            filetypes=[("All Files","*.*"), 
                                                ("Text Documents","*.txt")]) 

            if self.__file == "": 
                self.__file = None
            else: 
                
                # Try to save the file 
                file = open(self.__file,"w") 
                file.write(self.__thisTextArea.get(1.0,END)) 
                file.close() 
                
                # Change the window title 
                self.__root.title(os.path.basename(self.__file) + " - Notepad") 
                
            
        else: 
            file = open(self.__file,"w") 
            file.write(self.__thisTextArea.get(1.0,tk.END)) 
            file.close() 

    def __cut(self): 
        self.__thisTextArea.event_generate("<<Cut>>") 

    def __copy(self): 
        self.__thisTextArea.event_generate("<<Copy>>") 

    def __paste(self): 
        self.__thisTextArea.event_generate("<<Paste>>") 

    def run(self): 

        # Run main application 
        self.__root.mainloop() 



"""**************************************************************************************************************************************"""
"""
class Notepad: 
    __root = tk.Tk() 

    # default window width and height 
    __thisWidth = 300
    __thisHeight = 300
    __thisTextArea = tk.Text(__root) 
    __thisMenuBar = tk.Menu(__root) 
    __thisFileMenu = tk.Menu(__thisMenuBar, tearoff=0) 
    __thisEditMenu = tk.Menu(__thisMenuBar, tearoff=0) 
    __thisHelpMenu = tk.Menu(__thisMenuBar, tearoff=0) 
    
    # To add scrollbar 
    __thisScrollBar = tk.Scrollbar(__thisTextArea)     
    __file = None

    def __init__(self,**kwargs): 

        # Set icon 
        try: 
                self.__root.wm_iconbitmap("Notepad.ico") 
        except: 
                pass

        # Set window size (the default is 300x300) 

        try: 
            self.__thisWidth = kwargs['width'] 
        except KeyError: 
            pass

        try: 
            self.__thisHeight = kwargs['height'] 
        except KeyError: 
            pass

        # Set the window text 
        self.__root.title("Untitled - Notepad") 

        # Center the window 
        screenWidth = self.__root.winfo_screenwidth() 
        screenHeight = self.__root.winfo_screenheight() 
    
        # For left-alling 
        left = (screenWidth / 2) - (self.__thisWidth / 2) 
        
        # For right-allign 
        top = (screenHeight / 2) - (self.__thisHeight /2) 
        
        # For top and bottom 
        self.__root.geometry('%dx%d+%d+%d' % (self.__thisWidth, 
                                            self.__thisHeight, 
                                            left, top)) 

        # To make the textarea auto resizable 
        self.__root.grid_rowconfigure(0, weight=1) 
        self.__root.grid_columnconfigure(0, weight=1) 

        # Add controls (widget) 
        self.__thisTextArea.grid(sticky = tk.N + tk.E + tk.S + tk.W) 
        
        # To open new file 
        self.__thisFileMenu.add_command(label="New", 
                                        command=self.__newFile)     
        
        # To open a already existing file 
        self.__thisFileMenu.add_command(label="Open", 
                                        command=self.__openFile) 
        
        # To save current file 
        self.__thisFileMenu.add_command(label="Save", 
                                        command=self.__saveFile)     

        # To create a line in the dialog         
        self.__thisFileMenu.add_separator()                                         
        self.__thisFileMenu.add_command(label="Exit", 
                                        command=self.__quitApplication) 
        self.__thisMenuBar.add_cascade(label="File", 
                                    menu=self.__thisFileMenu)     
        
        # To give a feature of cut 
        self.__thisEditMenu.add_command(label="Cut", 
                                        command=self.__cut)             
    
        # to give a feature of copy     
        self.__thisEditMenu.add_command(label="Copy", 
                                        command=self.__copy)         
        
        # To give a feature of paste 
        self.__thisEditMenu.add_command(label="Paste", 
                                        command=self.__paste)         
        
        # To give a feature of editing 
        self.__thisMenuBar.add_cascade(label="Edit", 
                                    menu=self.__thisEditMenu)     
        
        # To create a feature of description of the notepad 
        self.__thisHelpMenu.add_command(label="About Notepad", 
                                        command=self.__showAbout) 
        self.__thisMenuBar.add_cascade(label="Help", 
                                    menu=self.__thisHelpMenu) 

        self.__root.config(menu=self.__thisMenuBar) 

        self.__thisScrollBar.pack(side=tk.RIGHT,fill=tk.Y)                     
        
        # Scrollbar will adjust automatically according to the content         
        self.__thisScrollBar.config(command=self.__thisTextArea.yview)     
        self.__thisTextArea.config(yscrollcommand=self.__thisScrollBar.set) 
    
        
    def __quitApplication(self): 
        self.__root.destroy() 
        # exit() 

    def __showAbout(self): 
        tk.showinfo("Notepad","Mrinal Verma") 

    def __openFile(self): 
        
        self.__file = askopenfilename(defaultextension=".txt", 
                                    filetypes=[("All Files","*.*"), 
                                        ("Text Documents","*.txt")]) 

        if self.__file == "": 
            
            # no file to open 
            self.__file = None
        else: 
            
            # Try to open the file 
            # set the window title 
            self.__root.title(os.path.basename(self.__file) + " - Notepad") 
            self.__thisTextArea.delete(1.0,tk.END) 

            file = open(self.__file,"r") 

            self.__thisTextArea.insert(1.0,file.read()) 

            file.close() 

        
    def __newFile(self): 
        self.__root.title("Untitled - Notepad") 
        self.__file = None
        self.__thisTextArea.delete(1.0,tk.END) 

    def __saveFile(self): 

        if self.__file == None: 
            # Save as new file 
            self.__file = asksaveasfilename(initialfile='Untitled.txt', 
                                            defaultextension=".txt", 
                                            filetypes=[("All Files","*.*"), 
                                                ("Text Documents","*.txt")]) 

            if self.__file == "": 
                self.__file = None
            else: 
                
                # Try to save the file 
                file = open(self.__file,"w") 
                file.write(self.__thisTextArea.get(1.0,END)) 
                file.close() 
                
                # Change the window title 
                self.__root.title(os.path.basename(self.__file) + " - Notepad") 
                
            
        else: 
            file = open(self.__file,"w") 
            file.write(self.__thisTextArea.get(1.0,tk.END)) 
            file.close() 

    def __cut(self): 
        self.__thisTextArea.event_generate("<<Cut>>") 

    def __copy(self): 
        self.__thisTextArea.event_generate("<<Copy>>") 

    def __paste(self): 
        self.__thisTextArea.event_generate("<<Paste>>") 

    def run(self): 

        # Run main application 
        self.__root.mainloop() 




# Run main application 
#notepad = Notepad(width=600,height=400) 
#notepad.run()
"""
