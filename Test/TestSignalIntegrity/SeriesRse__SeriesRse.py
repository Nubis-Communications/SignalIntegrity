def SeriesRse(f,Rse,Z0=None):
    return SeriesZ(Rse*(1+1j)*np.sqrt(f),Z0)
