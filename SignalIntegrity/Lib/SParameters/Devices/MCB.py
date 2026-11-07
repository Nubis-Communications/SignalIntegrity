"""MCB transmission-line device"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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

from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.SParameters.Devices.TransmissionLineEquation import TransmissionLineEquation


class MCB(SParameters):
    """s-parameters of four-port MCB transmission line built from two two-port lines
    @note MCB is a Module Compliance Board as defined in the IEEE 802.3 standards."""
    def __init__(self,f,Td=200e-12,lp=[1,2],rp=[3,4],Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param Td float electrical length (propagation time)
        @param lp list of ints left ports in order (top to bottom)
        @param rp list of ints right ports in order (top to bottom)
        @param Z0 (optional) float or complex reference impedance (defaults to 50 ohms)
        """
        self.m_lp=lp
        self.m_rp=rp
        eq=('10**(-(0.0912+0.3102*math.sqrt(f/1e9)+0.008578*(f/1e9)'
            '+0.000759*(f/1e9)**2)/20.)*cmath.exp(-j*2.*pi*f*'+repr(float(Td))+')')
        self.m_line1=TransmissionLineEquation(f,eq,Z0)
        self.m_line2=TransmissionLineEquation(f,eq,Z0)
        SParameters.__init__(self,f,None,Z0)

    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        # upper pair uses canonical ports 1,3; lower pair uses canonical ports 2,4
        h1=self.m_line1[n]
        h2=self.m_line2[n]
        sc=[[0. for _ in range(4)] for _ in range(4)]
        sc[0][0]=h1[0][0]; sc[0][2]=h1[0][1]; sc[2][0]=h1[1][0]; sc[2][2]=h1[1][1]
        sc[1][1]=h2[0][0]; sc[1][3]=h2[0][1]; sc[3][1]=h2[1][0]; sc[3][3]=h2[1][1]
        order=self.m_lp+self.m_rp
        if len(order) != 4 or sorted(order) != [1,2,3,4]:
            raise IndexError('port number incorrect')
        inverse=[0]*4
        for canonical_index,external_port in enumerate(order):
            inverse[external_port-1]=canonical_index
        return [[sc[inverse[r]][inverse[c]] for c in range(4)] for r in range(4)]

