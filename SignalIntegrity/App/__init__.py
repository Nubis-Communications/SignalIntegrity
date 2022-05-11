"""
__init__.py
"""
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
from .SignalIntegrityApp import SignalIntegrityApp
from .SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
from .Project import Project
import os
InstallDir=os.path.dirname(os.path.abspath(__file__))+'/'
IconsBaseDir=InstallDir+'icons/png/'
IconsDir=IconsBaseDir+'16x16/actions/'