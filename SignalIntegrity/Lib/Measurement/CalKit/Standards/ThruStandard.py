"""
Thru Standard
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

from SignalIntegrity.Lib.Measurement.CalKit.Standards.Offset import Offset

class ThruStandard(Offset):
    """Class providing the s-parameters of a thru standard as commonly defined
    for a calibration kit."""
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,f0=1e9):
        """Constructor
        @param f list of frequencies
        @param offsetDelay (optional) float electrical length of offset in s (defaults to 0 s)
        @param offsetZ0 (optional) float real characteristic impedance of offset (defaults to 50 Ohms)
        @param offsetLoss (optional) float loss due to skin-effect defined in GOhms/s at 1 GHz (defaults to 0).
        @param f0 (optional) float frequency where the offset loss is defined (defaults to 1e9).
        The result is that the class becomes the base-class SParameters with the s-parameters
        of a thru standard."""
        Offset.__init__(self,f,offsetDelay,offsetZ0,offsetLoss,f0)
