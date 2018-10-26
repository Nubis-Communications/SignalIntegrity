"""
Short Standard
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

from SignalIntegrity.Lib.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
from SignalIntegrity.Lib.Measurement.CalKit.Standards.TerminationPolynomial import TerminationLPolynomial
from SignalIntegrity.Lib.Measurement.CalKit.Standards.Offset import Offset
from SignalIntegrity.Lib.SParameters.SParameters import SParameters

class ShortStandard(SParameters):
    """Class providing the s-parameters of a short standard as commonly defined
    for a calibration kit."""
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,
                 L0=0.0,L1=0.0,L2=0.0,L3=0.0):
        """Constructor
        @param f list of frequencies
        @param offsetDelay (optional) float electrical length of offset in s (defaults to 0 s)
        @param offsetZ0 (optional) float real characteristic impedance of offset (defaults to 50 Ohms)
        @param offsetLoss (optional) float loss due to skin-effect defined in GOhms/s at 1 GHz (defaults to 0).
        @param L0 (optional) float polynomial coefficient for inductance of short termination
        @param L1 (optional) float polynomial coefficient for inductance of short termination
        @param L2 (optional) float polynomial coefficient for inductance of short termination
        @param L3 (optional) float polynomial coefficient for inductance of short termination
        The result is that the class becomes the base-class SParameters with the s-parameters
        of a short standard.

        Termination inductance polynomial is L0+f*(L1+f*(L2+f*L3)).
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.Parsers.SystemDescriptionParser import SystemDescriptionParser
        # pragma: include
        sspn=SystemSParametersNumeric(SystemDescriptionParser().AddLines(
            ['device offset 2','device L 1','port 1 offset 1','connect offset 2 L 1']
            ).SystemDescription())
        offsetSParameters=Offset(f,offsetDelay,offsetZ0,offsetLoss)
        terminationSParameters=TerminationLPolynomial(f,L0,L1,L2,L3)
        sp=[]
        for n in range(len(f)):
            sspn.AssignSParameters('offset',offsetSParameters[n])
            sspn.AssignSParameters('L',terminationSParameters[n])
            sp.append(sspn.SParameters())
        SParameters.__init__(self,f,sp)