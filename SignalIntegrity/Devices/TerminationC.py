from SignalIntegrity.Devices.TerminationZ import TerminationZ
from numpy import math

def TerminationC(C,f,Z0=None):
    try:
        Z=1./(C*1j*2.*math.pi*f)
    except ZeroDivisionError:
        Z=1e15
    return TerminationZ(Z,Z0)