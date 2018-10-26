"""
TestSingulars.py
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

import unittest
import SignalIntegrity.Lib as si
import os
import copy

class TestSingularsTest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
    def id(self):
        return 'TestSingulars_'+'_'.join(unittest.TestCase.id(self).split('.')[-1:])
    def testParallelTeeSymbolic(self):
        ssps=si.sd.SystemSParametersSymbolic()
        ssps.AddDevice('T1',3,si.dev.Tee())
        ssps.AddDevice('T2',3,si.dev.Tee())
        ssps.AddPort('T1',1,1)
        ssps.AddPort('T2',1,2)
        ssps.ConnectDevicePort('T1',2,'T2',2)
        ssps.ConnectDevicePort('T1',3,'T2',3)
        ssps.DocStart()
        ssps.LaTeXSolution(solvetype='direct')
        ssps.LaTeXSystemEquation()
        print ssps.DeviceNames()
        ANodes=ssps.PortBNames()
        BNodes=ssps.PortANames()
        OtherNodes=ssps.OtherNames(ANodes+BNodes)
        RemoveNodes=ANodes+OtherNodes
        A11=ssps.WeightsMatrix(BNodes,BNodes)
        print ssps._LaTeXMatrix(A11)
        #return
        A12=ssps.WeightsMatrix(BNodes,RemoveNodes)
        A21=ssps.WeightsMatrix(RemoveNodes,BNodes)
        A22=ssps.WeightsMatrix(RemoveNodes,RemoveNodes)
        ssps._AddEq('\mathbf{A_{11}}='+ssps._LaTeXMatrix(A11))
        ssps._AddEq('\mathbf{A_{12}}='+ssps._LaTeXMatrix(A12))
        ssps._AddEq('\mathbf{A_{21}}='+ssps._LaTeXMatrix(A21))
        ssps._AddEq('\mathbf{A_{22}}='+ssps._LaTeXMatrix(A22))
        ssps._AddEq('\mathbf{n_1}='+ssps._LaTeXMatrix(si.helper.SubscriptedVector(BNodes)))
        ssps._AddEq('\mathbf{n_2}='+ssps._LaTeXMatrix(si.helper.SubscriptedVector(RemoveNodes)))
        ssps.DocEnd()
        ssps.WriteToFile(self.id())
