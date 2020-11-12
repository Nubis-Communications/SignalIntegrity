def SeriesRse(f,Rse,Z0=None):
    return SeriesZ(Rse*(1+1j)*math.sqrt(f),Z0)
