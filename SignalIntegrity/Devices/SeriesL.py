from SignalIntegrity.Devices.SeriesZ import SeriesZ
from numpy import math

def SeriesL(L,f,Z0=None):
    return SeriesZ(L*1j*2.*math.pi*f,Z0)