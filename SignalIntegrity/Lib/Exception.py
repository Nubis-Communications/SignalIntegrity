"""
 Exception.py
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

import inspect

class SignalIntegrityException(Exception):
    def __init__(self,value,message=''):
        self.parameter=value
        self.message=message
    def __str__(self):
        return str(self.parameter)
    def __eq__(self,other):
        if isinstance(other,SignalIntegrityException):
            return str(self) == str(other)
        elif isinstance(other,str):
            return str(self) == other
        elif inspect.isclass(other):
            return self == eval(str(other).split('.')[-1].strip('\'>'))()
        else:
            return False

class SignalIntegrityExceptionSystemDescription(SignalIntegrityException):
    def __init__(self,message=''):
        SignalIntegrityException.__init__(self,'SystemDescription',message)

class SignalIntegrityExceptionSParameterFile(SignalIntegrityException):
    def __init__(self,message=''):
        SignalIntegrityException.__init__(self,'SParameterFile',message)

class SignalIntegrityExceptionDeembedder(SignalIntegrityException):
    def __init__(self,message=''):
        SignalIntegrityException.__init__(self,'Deembedder',message)

class SignalIntegrityExceptionWaveformFile(SignalIntegrityException):
    def __init__(self,message=''):
        SignalIntegrityException.__init__(self,'WaveformFile',message)

class SignalIntegrityExceptionWaveform(SignalIntegrityException):
    def __init__(self,message=''):
        SignalIntegrityException.__init__(self,'Waveform',message)

class SignalIntegrityExceptionSimulator(SignalIntegrityException):
    def __init__(self,message=''):
        SignalIntegrityException.__init__(self,'Simulator',message)

class SignalIntegrityExceptionVirtualProbe(SignalIntegrityException):
    def __init__(self,message=''):
        SignalIntegrityException.__init__(self,'VirtualProbe',message)

class SignalIntegrityExceptionSParameters(SignalIntegrityException):
    def __init__(self,message=''):
        SignalIntegrityException.__init__(self,'S-Parameters',message)

class SignalIntegrityExceptionNumeric(SignalIntegrityException):
    def __init__(self,message=''):
        SignalIntegrityException.__init__(self,'Numeric',message)

class SignalIntegrityExceptionDeviceParser(SignalIntegrityException):
    def __init__(self,message=''):
        SignalIntegrityException.__init__(self,'DeviceParser',message)

class SignalIntegrityExceptionFitter(SignalIntegrityException):
    def __init__(self,message=''):
        SignalIntegrityException.__init__(self,'Fitter',message)
