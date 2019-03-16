"""@namespace SignalIntegrity
Signal Integrity Tools"""

from __future__ import absolute_import

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
from . import SystemDescriptions as sd
from . import Conversions as cvt
from . import Devices as dev
from . import SParameters as sp
from . import Splines as spl
from . import Parsers as p
from . import SubCircuits as sub
from . import Helpers as helper
from . import Symbolic as sy
from . import ImpedanceProfile as ip
from . import ChirpZTransform as czt
from . import TimeDomain as td
from . import FrequencyDomain as fd
from .Exception import *
from . import Wavelets as wl
from .Rat import *
from . import Measurement as m
from . import Test as test
from . import Fit as fit
from . import Prbs as prbs