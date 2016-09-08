'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''

class CallBacker(object):
    def __init__(self,callback=None):
        self.InstallCallback(callback)
    def HasACallBack(self):
        return not self.callback is None 
    def CallBack(self,progressPercent):
        '''
            The idea here is that this function is called periodically during a long computation with the
            progress of the calculation in percent.  If there is no callback function installed, return
            True to indicate continuing with the computation.  The callback, if installed, should return
            False if the computation should be aborted otherwise returns True.
        '''
        if not self.callback is None:
            return self.callback(progressPercent)
        else:
            return True
    def InstallCallback(self,callback=None):
        self.callback = callback
    def RemoveCallback(self):
        self.InstallCallback()