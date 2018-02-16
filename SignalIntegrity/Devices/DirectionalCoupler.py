"""
 Directional Coupler
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.


## DirectionalCoupler
#
# @param ports integer number of ports (3 or 4)
# @return s-parameter matrix of a three or four port directional coupler
#
# port 1 and 2 are a thru connection.
#
# port 3 picks off the wave going from port 1 to 2.
#
# port 4 (optional) picks off the wave going from port 2 to port 1.
#
# @note the directional coupler is completely ideal and is not passive
# in that the picked off wave is an exact copy of the wave going between
# the ports specified above.
#
def DirectionalCoupler(ports):
    if ports==3:
        return [[0,1,0],
                [1,0,0],
                [1,0,0]]
    elif ports==4:
        return [[0,1,0,0],
                [1,0,0,0],
                [1,0,0,0],
                [0,1,0,0]]
