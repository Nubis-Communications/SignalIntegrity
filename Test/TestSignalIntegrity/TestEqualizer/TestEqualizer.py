"""
TestEqualizer.py
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

import unittest
import os
from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
import SignalIntegrity.Lib as si
import numpy as np

class TestEqualizerTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testEqualizer(self):
        project_file=os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                  '../../../SignalIntegrity/App/Examples/HDMICable/PRBSTest.si'))
        app=SignalIntegrityAppHeadless()
        opened = app.OpenProjectFile(project_file)
        assert(opened)
        result = app.Simulate(EyeDiagrams=False)
        wf=result.OutputWaveform('Vdiff')
        wfd=wf*si.td.f.WaveformDecimator(8,1)
        wfd.WriteToFile(os.path.abspath(os.path.join(os.path.dirname(__file__),'eq_test.txt')))
        eq=si.eq.Equalizer(400,0,40,si.eq.LevelsRange(-0.5,0.5,4)).initialize_tap_values_to_default()
        # wfd=np.arange(0,10)
        eq.equalize_values(wfd,num_iterations=25,lamda=1)
        pass
    def testPAM6Equalizer(self):
        project_file=os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                  '../TestPAM6/PAM6.si'))
        print('pam6')
        app=SignalIntegrityAppHeadless()
        opened = app.OpenProjectFile(project_file)
        assert(opened)
        result = app.Simulate(EyeDiagrams=False)
        wf=result.OutputWaveform('Vout')
        wfd=wf*si.td.f.WaveformDecimator(8,5)
        wfd.WriteToFile(os.path.abspath(os.path.join(os.path.dirname(__file__),'eq_test_pam6.txt')))
        eq=si.eq.Equalizer(10,0,3,si.eq.LevelsRange(-0.5,0.5,6)).initialize_tap_values_to_default()
        # wfd=np.arange(0,10)
        eq.equalize_values(wfd,num_iterations=50,lamda=1)
        pass
    def testAMDEqualizer(self):
        project_file=os.path.abspath(os.path.join(os.path.dirname(__file__),
            '../../../../Nitro/Schematics/400G/Schematics/AMDSimulation.si'))
        print('pam6')
        eq=si.eq.Equalizer(50,0,10,si.eq.LevelsRange(-0.2,0.2,6)).initialize_tap_values_to_default()
        args={'RxSerdes_FFEtaps':str(eq.ffe_tap_values_list).replace(' ',''),
              'RxSerdes_FFEpre':eq.num_precursor_taps}
        app=SignalIntegrityAppHeadless()
        opened = app.OpenProjectFile(project_file,args=args)
        assert(opened)
        app.SaveProject()
        result = app.Simulate(EyeDiagrams=False)
        wf=result.OutputWaveform('Vo')
        phases=round(wf.td.Fs/float(result['variables']['BaudRate']))
        wfd=wf*si.td.f.WaveformDecimator(phases,3)
        # wfd=np.arange(0,10)
        eq.equalize_values(wfd,num_iterations=150,lamda=1)

        print(str(eq.ffe_tap_values_list).replace(' ',''))
        args={'RxSerdes_FFEtaps':str(eq.ffe_tap_values_list).replace(' ',''),
              'RxSerdes_FFEpre':eq.num_precursor_taps}
        app=SignalIntegrityAppHeadless()
        opened = app.OpenProjectFile(project_file,args=args)
        assert(opened)
        app.SaveProject()
        import matplotlib.pyplot as plt
        plt.cla()
        plt.plot(eq.mse_list)
        plt.grid()
        plt.show()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()