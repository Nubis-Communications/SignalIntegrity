"""
Handles Callbacks that allow progress reporting during long calculations and capability to abort.
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

class CallBacker(object):
    """CallBacker

    To use callbacks, a class is derived from CallBacker.

    Either the constructor of the derived class or some other mechanism should
    provide means for supplying the callback function, which is installed in a
    call to __init__.

    The derived class, during some long operation, then calls the callback function
    periodically.  The callback function then has the opportunity to report its
    progress.  Returning False in the callback function should cause the operation
    to abort.

    Here's a mini example derived class using CallBacker:

    \code{.py}
    class ProcessingClass(Callbacker):
        def __init__(self,callback=None):
            ...
            Callbacker.__init__(callback)
            ...
        def LongProcessingFunction(self):
            for m in range(100):
                ...
                do some calculating.
                ...
                if not self.CallBack(m):
                    process was aborted
                    return
     \endcode
     """
    def __init__(self,callback=None):
        """Constructor
        @param callback (optional, defaults to None) a callback function to call
        The callback function should take a number as an argument, which represents
        the progress."""
        self.InstallCallback(callback)
    def HasACallBack(self):
        return not self.callback is None
    def CallBack(self,progressPercent):
        """This function is called periodically, which in turn calls any installed
        callback function.
        @param progressPercent the progress in percent
        """
        if not self.callback is None:
            return self.callback(progressPercent)
        else:
            return True
    def InstallCallback(self,callback=None):
        """This is an alternate way to supply the callback, if it cannot be installed
        during initialization of the derived class.
        @param callback (optional, defaults to None) a callback function to call
        The callback function should take a number as an argument, which represents
        the progress.
        """
        self.callback = callback
    def RemoveCallback(self):
        """Removes any callback previously installed."""
        self.InstallCallback()
