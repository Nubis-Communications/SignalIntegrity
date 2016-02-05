#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      peter.pupalaikis
#
# Created:     05/02/2016
# Copyright:   (c) peter.pupalaikis 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import unittest

import SignalIntegrity as si
import math
import os
from TestHelpers import *

class Test(unittest.TestCase,RoutineWriterTesterHelper,ResponseTesterHelper,SourcesTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testTeeTerminationSymbolic(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sdp=si.p.SystemDescriptionParser().File('TerminationDifferentialTee.txt')
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('R1',si.sy.SeriesZ('Z_1'))
        ssps.AssignSParameters('R2',si.sy.SeriesZ('Z_2'))
        ssps.AssignSParameters('R3',si.sy.ShuntZ(1,'Z_3'))
        ssps.DocStart()
        ssps.LaTeXSolution(size='big')
        ssps.DocEnd()
        ssps.Emit()


if __name__ == '__main__':
    unittest.main()