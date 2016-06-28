#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Peter.Pupalaikis
#
# Created:     24/05/2016
# Copyright:   (c) Peter.Pupalaikis 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import ctypes
import os

lib=ctypes.cdll.LoadLibrary(os.path.dirname(__file__)+'/PySIConvolve.so')
lib.PySIConvolve.argtypes = [ctypes.c_int,
                            ctypes.POINTER(ctypes.c_float),
                            ctypes.c_int,
                            ctypes.POINTER(ctypes.c_float),
                            ctypes.POINTER(ctypes.c_float)]
lib.PySIConvolve.restype = None

def PySIConvolve(values,taps):
    resultBufferLength=len(values)-len(taps)+1
    if resultBufferLength <= 0:
        return None
    resultBuffer=(ctypes.c_float*resultBufferLength)()
    valuesbuffer=(ctypes.c_float*len(values))()
    tapsbuffer=(ctypes.c_float*len(taps))()
    for k in range(len(values)):
        valuesbuffer[k]=ctypes.c_float(values[k])
    for m in range(len(taps)):
        tapsbuffer[m]=ctypes.c_float(taps[m])
    lib.PySIConvolve(len(values),valuesbuffer,len(taps),tapsbuffer,resultBuffer)
    return [resultBuffer[i] for i in range(resultBufferLength)]
