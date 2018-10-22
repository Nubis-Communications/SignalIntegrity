"""@namespace SignalIntegrity
Signal Integrity Tools"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import SystemDescriptions as sd
import Conversions as cvt
import Devices as dev
import SParameters as sp
import Splines as spl
import Parsers as p
import SubCircuits as sub
import Helpers as helper
import Symbolic as sy
import ImpedanceProfile as ip
import ChirpZTransform as czt
import TimeDomain as td
import FrequencyDomain as fd
from PySIException import *
import Wavelets as wl
from Rat import *
import Measurement as m
import Test as test
import Fit as fit
import Oyster as oy