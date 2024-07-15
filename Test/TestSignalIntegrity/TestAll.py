"""
TestAll.py
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
import matplotlib
matplotlib.use('Tkagg')

import unittest

from TestAdaptDecimate import *
from TestBook import *
from TestBookDevices import *
from TestCascading import *
from TestChirpZTransform import *
from TestClassWriter import *
from TestClockRecovery import *
from TestCOMModels import *
from TestCommonElements import *
from TestConversions import *
from TestDeembedding import *
from TestDwellTime import *
from TestDescriptors import *
from TestDeviceParser import *
from TestEncryption import *
from TestExceptions import *
from TestEyeDiagram import *
from TestFilters import *
from TestFrequencyContent import *
from TestFrequencyList import *
from TestHDMICable import *
from TestHeaders import *
from TestHiRes import *
from TestImpedanceProfile import *
from TestImpulseResponseFilter import *
from TestLaplace import *
from TestLeCroyWaveforms import *
from TestMixedModeTermination import *
from TestNewtonsMethod import *
from TestOpticalCalculator import *
from TestPI import *
from TestPDN import *
from TestPowerDelivery import *
from TestPRBS import *
from TestProbeOnOff import *
from TestProbes import *
from TestRefImp import *
from TestRLGC import *
from TestRLGCLevMar import *
from TestRoutineWriter import *
#from TestSenseResistorInductance import *
from TestSeries import *
from TestSimulator import *
#from TestSimulatorNumericParser import *
from TestSources import *
from TestSParameterEnforcements import *
from TestSParameterFile import *
from TestSParametersParser import *
from TestSplines import *
from TestSubcircuit import *
from TestSubProjectReferenceImpedance import *
from TestSystemDescription import *
from TestTDRErrorTerms import *
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
from TestSystemVariables import *
from TestWaveformOnlySimulations import *
from YuriyWaveTest import *
from TestLevMarNumeric import *
from TestVNACalibrationObject import *
from TestWElement import *


if __name__ == '__main__':
    unittest.main()
