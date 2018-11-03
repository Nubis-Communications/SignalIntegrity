"""
 admittance parameters to s-parameter conversion
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
from numpy import identity

from SignalIntegrity.Lib.Conversions.Z0KHelper import Z0KHelper

def Y2S(Y,Z0=None,K=None):
    """Converts Y-parameters to s-parameters
    @param Y list of list representing Y-parameter matrix to convert
    @param Z0 (optional) float or complex or list of reference impedance (defaults to None).
    @param K (optional) float or complex or list of scaling factor (defaults to None).
    @see Z0KHelper to see how the reference impedance
    and scaling factor are determined."""
    (Z0,K)=Z0KHelper((Z0,K),len(Y))
    I=matrix(identity(len(Y)))
    Y=matrix(Y)
    return (K.getI()*(I+Z0*Y).getI()*(I-Z0*Y)*K).tolist()
