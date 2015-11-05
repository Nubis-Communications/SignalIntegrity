from SignalIntegrity.Devices.TerminationZ import TerminationZ
from numpy import math

def TerminationL(L,f,Z0=None):
    return TerminationZ(L*1j*2.*math.pi*f,Z0)