'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
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