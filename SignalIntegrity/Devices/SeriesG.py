from SignalIntegrity.Devices.SeriesZ import SeriesZ

def SeriesG(G,Z0=50.):
    infinity=1e25
    try: Z = 1.0/G
    except ZeroDivisionError: Z = infinity
    return SeriesZ(Z,Z0)
