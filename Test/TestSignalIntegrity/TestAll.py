"""
TestAll.py
"""

# Copyright (c) 2018 Teledyne LeCroy, all rights reserved worldwide.
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
import matplotlib
matplotlib.use('Tkagg')

import unittest

from TestConversions import *
from TestDeembedding import *
from TestRefImp import *
from TestSParameterFile import *
from TestSplines import *
from TestSystemDescription import *
from TestTline import *
from TestVirtualProbe import *
from TestBook import *
from TestSources import *
from TestRoutineWriter import *
from TestImpedanceProfile import *
from TestCommonElements import *
from TestTeeProblem import *
from TestChirpZTransform import *
from TestTimeDomain import *
from TestClassWriter import *
from TestSimulator import *
from TestSubcircuit import *
from TestExceptions import *
from TestDeviceParser import *
from TestMixedModeTermination import *
from TestWavelets import *
from TestSParameterEnforcements import *
from TestFrequencyList import *
from TestPI import *
from TestDescriptors import *
from TestAdaptDecimate import *
from TestSPARQSOLT import *
from TestSPARQFourPort import *
from TDRSimulationFourPortScaled import *
from Sequid import *
from YuriyWaveTest import *
from TestRLGCLevMar import *
from TestNewtonsMethod import *
from ScientificPulserSampler import *
from TestHeaders import *

if __name__ == '__main__':
    unittest.main()
