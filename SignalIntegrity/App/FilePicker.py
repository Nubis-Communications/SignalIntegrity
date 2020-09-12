"""
FilePicker.py
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
    import tkFileDialog as filedialog
else:
    from tkinter import filedialog

from SignalIntegrity.App.Files import FileParts

def _FileNameChecker(filename):
    if filename is None:
        return None
    if isinstance(filename,tuple):
        return None
    filename=str(filename)
    if filename=='':
        return None
    return filename

def AskSaveAsFilename(**kw):
    filename=filedialog.asksaveasfilename(**kw)
    return _FileNameChecker(filename)

def AskOpenFileName(**kw):
    if 'filetypes' in kw:
        if 'initialfile' in kw:
            ext=FileParts(kw['initialfile']).fileext
            filetypes=kw['filetypes']
            filetypeext=[lext for (filetype,lext) in filetypes]
            if ext in filetypeext:
                extindex=filetypeext.index(ext)
                if extindex != 0:
                    kw['filetypes']=[filetypes[extindex]]+filetypes[0:extindex]+filetypes[extindex+1:]
    filename=filedialog.askopenfilename(**kw)
    return _FileNameChecker(filename)
