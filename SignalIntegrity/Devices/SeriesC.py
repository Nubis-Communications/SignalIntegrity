from SignalIntegrity.Devices.SeriesG import SeriesG
from numpy import math

def SeriesC(C,f,Z0=None,df=0.,esr=0.):
    G=C*2.*math.pi*f*(1j+df)
    try: G=G+1/esr
    except: pass
    return SeriesG(G,Z0)