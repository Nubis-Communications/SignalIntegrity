"""
PySIException.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

import inspect

class PySIException(Exception):
    def __init__(self,value,message=''):
        self.parameter=value
        self.message=message
    def __str__(self):
        return str(self.parameter)
    def __eq__(self,other):
        if isinstance(other,PySIException):
            return str(self) == str(other)
        elif isinstance(other,str):
            return str(self) == other
        elif inspect.isclass(other):
            return self == eval(str(other).split('.')[-1].strip('\'>'))()
        else:
            return False

class PySIExceptionSystemDescription(PySIException):
    def __init__(self,message=''):
        PySIException.__init__(self,'SystemDescription',message)

class PySIExceptionSParameterFile(PySIException):
    def __init__(self,message=''):
        PySIException.__init__(self,'SParameterFile',message)

class PySIExceptionDeembedder(PySIException):
    def __init__(self,message=''):
        PySIException.__init__(self,'Deembedder',message)

class PySIExceptionWaveformFile(PySIException):
    def __init__(self,message=''):
        PySIException.__init__(self,'WaveformFile',message)

class PySIExceptionWaveform(PySIException):
    def __init__(self,message=''):
        PySIException.__init__(self,'Waveform',message)

class PySIExceptionSimulator(PySIException):
    def __init__(self,message=''):
        PySIException.__init__(self,'Simulator',message)

class PySIExceptionVirtualProbe(PySIException):
    def __init__(self,message=''):
        PySIException.__init__(self,'VirtualProbe',message)

class PySIExceptionSParameters(PySIException):
    def __init__(self,message=''):
        PySIException.__init__(self,'S-Parameters',message)

class PySIExceptionNumeric(PySIException):
    def __init__(self,message=''):
        PySIException.__init__(self,'Numeric',message)

class PySIExceptionDeviceParser(PySIException):
    def __init__(self,message=''):
        PySIException.__init__(self,'DeviceParser',message)

class PySIExceptionFitter(PySIException):
    def __init__(self,message=''):
        PySIException.__init__(self,'Fitter',message)
