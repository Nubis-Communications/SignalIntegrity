from SignalIntegrity.Devices.SeriesZ import SeriesZ
from numpy import math

def SeriesC(C,f,Z0=None):
    return SeriesZ(1./(C*1j*2.*math.pi*f),Z0)