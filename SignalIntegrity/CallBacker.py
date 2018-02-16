"""
Handles Callbacks that allow progress reporting during long calculations and
capability to abort.
"""
#  Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
#  Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
#  All Rights Reserved.
#
#  Explicit license in accompanying README.txt file.  If you don't have that file
#  or do not agree to the terms in that file, then you are not licensed to use
#  this material whatsoever.

## CallBacker
#
#  To use callbacks, a class is derived from CallBacker.
#
#  Either the constructor of the derived class or some other mechanism should
#  provide means for supplying the callback function, which is installed in a
#  call to __init__.
#
#  The derived class, during some long operation, then calls the callback function
#  periodically.  The callback function then has the opportunity to report its
#  progress.  Returning False in the callback function should cause the operation
#  to abort.
#
#  Here's a mini example derived class using CallBacker:
#
# \code{.py}
# class ProcessingClass(Callbacker):
#     def __init__(self,callback=None):
#         ...
#         Callbacker.__init__(callback)
#         ...
#     def LongProcessingFunction(self):
#         for m in range(100):
#             ...
#             do some calculating.
#             ...
#             if not self.CallBack(m):
#                 process was aborted
#                 return
# \endcode
class CallBacker(object):

    ## @param callback (optional, defaults to None) a callback function to call
    #
    # The callback function should take a number as an argument, which represents
    # the progress.
    def __init__(self,callback=None):
        self.InstallCallback(callback)
    def HasACallBack(self):
        return not self.callback is None
    ## @param progressPercent the progress in percent
    #
    # This function is called periodically, which in turn calls any installed
    # callback function.
    def CallBack(self,progressPercent):
        if not self.callback is None:
            return self.callback(progressPercent)
        else:
            return True
    ## This is an alternate way to supply the callback, if it cannot be installed
    # during initialization of the derived class.
    #
    # @param callback (optional, defaults to None) a callback function to call
    #
    # The callback function should take a number as an argument, which represents
    # the progress.
    def InstallCallback(self,callback=None):
        self.callback = callback
    ## Removes any callback previously installed.
    def RemoveCallback(self):
        self.InstallCallback()