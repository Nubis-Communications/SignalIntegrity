"""
TestSources.py
"""

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
from TestVoltageAmplifier import *
from TestCurrentAmplifier import *
from TestTransconductanceAmplifier import *
from TestTransresistanceAmplifier import *
from TestIdealTransformer import *
from TestTransistor import *
from TestOperationalAmplifier import *

if __name__ == '__main__':
    unittest.main()
