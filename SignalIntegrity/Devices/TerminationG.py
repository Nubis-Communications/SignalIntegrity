from SignalIntegrity.Devices.TerminationZ import TerminationZ
from numpy import math

def TerminationG(G,Z0=50.):
    infinity=1e25
    try: Z = 1.0/G
    except ZeroDivisionError: Z = infinity
    return TerminationZ(Z,Z0)
