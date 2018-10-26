"""
ReferenceImpedanceTransformer.py
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

import cmath

def ReferenceImpedanceTransformer(Z0f,Z0i=None,Kf=None,Ki=None):
    """ReferenceImpedanceTransformer
    Reference impedance transformer
    @param Z0f real or complex output reference impedance.
    @param Z0i real or complex input reference impedance.
    @param Kf (optional) real or complex scaling factor for the output (defaults to sqrt(Z0f))
    @param Ki (optional) real or complex scaling factor for the input (defaults to sqrt(Z0i))
    @return the list of list s-parameter matrix for a reference impedance transformer.
    @todo put Z0i=50.0 in the input arguments and remove check within the code
    @todo needs port numbering
    """
    Z0f=float(Z0f.real)+float(Z0f.imag)*1j
    if Z0i is None:
        Z0i=50.0
    Z0i=float(Z0i.real)+float(Z0i.imag)*1j
    if Kf is None:
        Kf=cmath.sqrt(Z0f)
    if Ki is None:
        Ki=cmath.sqrt(Z0i)
    Kf=float(Kf.real)+float(Kf.imag)*1j
    Ki=float(Ki.real)+float(Ki.imag)*1j
    p=(Z0f-Z0i)/(Z0f+Z0i)
    return [[p,(1.0-p)*Kf/Ki],[(1.0+p)*Ki/Kf,-p]]
