'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''

from tkFileDialog import asksaveasfilename
from tkFileDialog import askopenfilename

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
    filename=asksaveasfilename(**kw)
    return _FileNameChecker(filename)

def AskOpenFileName(**kw):
    filename=askopenfilename(**kw)
    return _FileNameChecker(filename)
