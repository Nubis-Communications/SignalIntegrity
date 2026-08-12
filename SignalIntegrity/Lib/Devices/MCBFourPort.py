"""
MCBFourPort.py
"""

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

import cmath
import math


def MCBFourPort(f,Td=200e-12,lp=[1,2],rp=[3,4],Z0=50.):
    """MCBFourPort
    Four-port MCB transmission-line model.
    @param f float frequency
    @param Td float electrical delay in seconds
    @param lp list of ints left ports in order (top to bottom)
    @param rp list of ints right ports in order (top to bottom)
    @param Z0 (optional) float or complex reference impedance (defaults to 50 ohms)
    @return list of list s-parameters of four-port MCB line model
    @note return loss is idealized to zero at all four ports.
    """
    fGHz=f/1e9
    attenuationDB=0.0912+0.3102*math.sqrt(fGHz)+0.008578*fGHz+0.000759*fGHz*fGHz
    transmission=(10.**(-attenuationDB/20.))*cmath.exp(-1j*2.*math.pi*f*Td)
    sc=[[0.,0.,transmission,0.],
        [0.,0.,0.,transmission],
        [transmission,0.,0.,0.],
        [0.,transmission,0.,0.]]
    order=lp+rp
    if len(order) != 4:
        raise IndexError('port number incorrect')
    if sorted(order) != [1,2,3,4]:
        raise IndexError('port number incorrect')
    inverse=[0]*4
    for canonical_index,external_port in enumerate(order):
        inverse[external_port-1]=canonical_index
    return [[sc[inverse[r]][inverse[c]] for c in range(4)] for r in range(4)]
