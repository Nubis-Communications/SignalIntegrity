"""
TestAll.py
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
import matplotlib
matplotlib.use('Tkagg')

import unittest

from TestAdaptDecimate import *
from TestBook import *
from TestBookDevices import *
from TestChirpZTransform import *
from TestClassWriter import *
from TestCommonElements import *
from TestConversions import *
from TestDeembedding import *
from TestDescriptors import *
from TestDeviceParser import *
from TestExceptions import *
from TestFrequencyList import *
from TestHeaders import *
from TestHiRes import *
from TestImpedanceProfile import *
from TestMixedModeTermination import *
from TestNewtonsMethod import *
from TestPI import *
from TestPRBS import *
from TestRefImp import *
from TestRLGC import *
from TestRLGCLevMar import *
from TestRoutineWriter import *
#from TestSenseResistorInductance import *
from TestSimulator import *
#from TestSimulatorNumericParser import *
from TestSources import *
from TestSParameterEnforcements import *
from TestSParameterFile import *
from TestSplines import *
from TestSubcircuit import *
from TestSystemDescription import *
from TestTeeProblem import *
from TestTimeDomain import *
from TestTline import *
from TestVirtualProbe import *
from TestWavelets import *
from TDRSimulationTwoPort import *
from TDRSimulationFourPort import *
from TDRSimulationFourPortScaled import *
from TestSignalIntegrityApp import *
from TestSParametersParser import *
from YuriyWaveTest import *
from TestLevMarNumeric import *

if __name__ == '__main__':
    unittest.main()
