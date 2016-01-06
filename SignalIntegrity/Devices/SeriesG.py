'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.Devices.SeriesZ import SeriesZ

def SeriesG(G,Z0=50.):
    infinity=1e25
    try: Z = 1.0/G
    except ZeroDivisionError: Z = infinity
    return SeriesZ(Z,Z0)
