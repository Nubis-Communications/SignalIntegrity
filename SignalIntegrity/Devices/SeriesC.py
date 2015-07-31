from SignalIntegrity.Devices.SeriesZ import SeriesZ
from numpy import math

def SeriesC(C,f,Z0=None):
    try:
        Z=1./(C*1j*2.*math.pi*f)
    except ZeroDivisionError:
        Z=1e15
    return SeriesZ(Z,Z0)