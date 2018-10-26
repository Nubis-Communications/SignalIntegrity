"""
PySIConvolve.py
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
