"""Integer ratios"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import math

def Rat(R,tol=0.0001):
    """integer ratio
    @param R float decimal, assumed rational number
    @param tol (optional) float tolerance for result (defaults to 0.0001)
    @return tuple (N,D) where N and D are integers up to ten digits long where
    N/D=R to the tolerance specified
    """
    N=10
    D=[]
    for n in range(N+1):
        D.append(int(math.floor(R)))
        B=R-D[n]
        if B < tol:
            break
        R = 1./B
    N = len(D)-1
    R=(1,0)
    for n in range(N+1):
        R=(R[0]*D[N-n]+R[1],R[0])
    return R