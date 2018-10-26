"""
ShuntDevice.py
"""

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

from numpy import matrix

def ShuntDeviceFourPort(D):
    """ShuntDeviceFourPort
    Four-port Shunt Device
    @param D list of list s-parameter matrix of two-port shunt device
    @return list of list s-parameter matrix of four-port shunt device
    @remark ports 1 and 3 are connected to port 1 of the device D provided.\n
    ports 2 and 4 are connected to port 2 of the device D provided.\n
    @todo check the port numbering
    """
    D11=D[0][0]
    D12=D[0][1]
    D21=D[1][0]
    D22=D[1][1]
    DetD=D11*D22-D12*D21
    DN=-9.-3.*D11-3.*D22-DetD
    S=matrix([[3.-3.*D11+D22-DetD,-4.*D12,-6.-6.*D11-2.*D22-2*DetD,-4.*D12],
        [-4.*D21,3+D11-3.*D22-DetD,-4.*D21,-6.-2.*D11-6.*D22-2*DetD],
        [-6.-6.*D11-2.*D22-2.*DetD,-4.*D12,3.-3.*D11+D22-DetD,-4.*D12],
        [-4.*D21,-6.-2.*D11-6.*D22-2.*DetD,-4.*D21,3.+D11-3.*D22-DetD]])
    S=(S/DN).tolist()
    return S
