"""
TestSenseResistorInductance.py
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
import unittest
import SignalIntegrity as si
import math
import os

class Test(unittest.TestCase,si.test.SourcesTesterHelper):
    def testSenseResistorInductanceVirtualProbeSymbolic(self):
        vpp=si.p.VirtualProbeParser()
        vpp.AddLines([
            'device L1 2',
            'device R1 2',
            'device R2 1',
            'device L2 2',
            'device L3 2',
            'device R3 2',
            'device R4 1',
            'device D1 4',
            'device G1 1 ground',
            'device O1 1 open',
            'device G2 1 ground',
            'device D2 4',
            'device G3 1 ground',
            'device O2 1 open',
            'connect L3 1 L1 1 G2 1',
            'stim m1 G2 1',
            'connect L1 2 D1 2 R1 1',
            'connect L2 1 R1 2',
            'connect R2 1 D1 1 L2 2',
            'connect D2 2 L3 2 R3 1',
            'connect R3 2 R4 1 D2 1',
            'connect G1 1 D1 3',
            'meas O1 1',
            'connect O1 1 D1 4',
            'connect D2 3 G3 1',
            'output O2 1',
            'connect O2 1 D2 4'
        ])        
        sd=vpp.SystemDescription()
        sd.AssignSParameters('L1',si.sy.SeriesZ('s\\cdot L'))
        sd.AssignSParameters('R1',si.sy.SeriesZ('R_{s}'))
        sd.AssignSParameters('R2',si.sy.ShuntZ(1, 'R_{l}'))
        sd.AssignSParameters('L2',si.sy.SeriesZ('s\\cdot L_{s}'))
        sd.AssignSParameters('L3',si.sy.SeriesZ('s\\cdot L'))
        sd.AssignSParameters('R3',si.sy.SeriesZ('R_{s}'))
        sd.AssignSParameters('R4',si.sy.ShuntZ(1, 'R_{l}'))
        sd.AssignSParameters('D1',si.sy.VoltageControlledVoltageSource('\\frac{1}{R_{s}}'))
        sd.AssignSParameters('D2',si.sy.VoltageControlledVoltageSource('\\frac{1}{R_{s}}'))
        
        vps=si.sd.VirtualProbeSymbolic(sd,docstart='\\documentclass[10pt]{article}\n'+'\\usepackage{amsmath}\n'+\
        '\\usepackage{bbold}\n'+'\\usepackage[paperwidth=25in,paperheight=16in]{geometry}\n'+'\\begin{document}')
        vps.DocStart()
        vps.LaTeXTransferMatrix()
        vps.DocEnd()
        vps.Emit()
        self.CheckSymbolicResult(self.id(), vps, 'sense resistor result')

    def testSenseResistorInductanceVirtualProbeSymbolicReduction(self):
        return
    
        from sympy import Matrix
        from sympy import Symbol

        s=Symbol('s')
        L=Symbol('L')
        Ls=Symbol('Ls')
        Z0=Symbol('Z0')
        Rs=Symbol('Rs')
        Rl=Symbol('Rl')

        S=Matrix([
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,(s*L)/(s*L+2*Z0),0,0,0,(2*Z0)/(s*L+2*Z0),0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,(2*Z0)/(s*L+2*Z0),0,0,0,(s*L)/(s*L+2*Z0),0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,(2*Z0)/(Rs+2*Z0),0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,Rs/(Rs+2*Z0),0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,Rs/(Rs+2*Z0),0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,(2*Z0)/(Rs+2*Z0),0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,(Rl-Z0)/(Rl+Z0),0,0,0,0,0,0,0],
            [0,0,0,(s*Ls)/(s*Ls+2*Z0),0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,(2*Z0)/(s*Ls+2*Z0),0,0,0,0,0,0],
            [0,0,0,(2*Z0)/(s*Ls+2*Z0),0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,(s*Ls)/(s*Ls+2*Z0),0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,(s*Ls)/(s*Ls+2*Z0),0,0,0,0,0,0,0,(2*Z0)/(s*Ls+2*Z0),0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,(2*Z0)/(s*Ls+2*Z0),0,0,0,0,0,0,0,(s*Ls)/(s*Ls+2*Z0),0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,Rs/(Rs+2*Z0),0,(2*Z0)/(Rs+2*Z0),0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,(2*Z0)/(Rs+2*Z0),0,Rs/(Rs+2*Z0),0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,(Rl-Z0)/(Rl+Z0),0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,-1/Rs,0,0,1/Rs,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1/Rs,0,0,-1/Rs,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,-1/Rs,0,0,0,1/Rs],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1/Rs,0,0,0,-1/Rs],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [-1./3.,0,0,0,0,0,0,2./3.,0,0,0,0,0,0,0,0,0,0,2./3.,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [2./3.,0,0,0,0,0,0,-1./3.,0,0,0,0,0,0,0,0,0,0,2./3.,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [2./3.,0,0,0,0,0,0,2./3.,0,0,0,0,0,0,0,0,0,0,-1./3.,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,2./3.,2./3.,0,0,0,0,0,0,0,0,0,0,-1./3.,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,-1./3.,2./3.,0,0,0,0,0,0,0,0,0,0,2./3.,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,2./3.,-1./3.,0,0,0,0,0,0,0,0,0,0,2./3.,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,+2./3.,0,+2./3.,0,0,0,0,0,-1./3.,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,-1./3.,0,+2./3.,0,0,0,0,0,+2./3.,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,+2./3.,0,-1./3.,0,0,0,0,0,+2./3.,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                  ])
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSenseResistorInductanceVirtualProbeSymbolic']
    unittest.main()