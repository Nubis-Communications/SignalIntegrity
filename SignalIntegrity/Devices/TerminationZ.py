from SignalIntegrity.Conversions import Z0KHelper   

def TerminationZ(Z,Z0=None,K=None):
    (Z0,K)=Z0KHelper((Z0,K),1)
    Z0=Z0.item(0,0)
    Z=float(Z.real)+float(Z.imag)*1j
    return [[(Z-Z0)/(Z+Z0)]]
    