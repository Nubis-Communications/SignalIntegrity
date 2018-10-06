"""
setup.py
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
from setuptools import setup
import os
import unittest
from Test.TestSignalIntegrity import *

install_requires=['numpy','matplotlib']

pathToIcons='PySIApp/icons/png'
pathToMoreIcons=pathToIcons+'/16x16/actions'
pathToHelp='PySIApp/Help/PySIHelp.html.LyXconv'

setup(
      name='PySI',
      version='1.0',
      description='signal integrity tools',
      author='Peter J. Pupalaikis',
      author_email='peterp@lecroy.com',
      url='https://github.com/TeledyneLeCroy/PySI',
      packages=['SignalIntegrity',
                'SignalIntegrity.ChirpZTransform',
                'SignalIntegrity.Conversions',
                'SignalIntegrity.Devices',
                'SignalIntegrity.Fit'
                'SignalIntegrity.FrequencyDomain',
                'SignalIntegrity.Helpers',
                'SignalIntegrity.ImpedanceProfile',
                'SignalIntegrity.Measurement',
                'SignalIntegrity.Measurement.Calibration',
                'SignalIntegrity.Measurement.CalKit',
                'SignalIntegrity.Measurement.TDR',
                'SignalIntegrity.Oyster',
                'SignalIntegrity.Parsers',
                'SignalIntegrity.Parsers.Devices',
                'SignalIntegrity.Rat',
                'SignalIntegrity.SParameters',
                'SignalIntegrity.SParameters.Devices',
                'SignalIntegrity.Splines',
                'SignalIntegrity.SubCircuits',
                'SignalIntegrity.Symbolic',
                'SignalIntegrity.SystemDescriptions',
                'SignalIntegrity.Test',
                'SignalIntegrity.TimeDomain',
                'SignalIntegrity.TimeDomain.Filters',
                'SignalIntegrity.TimeDomain.Waveform',
                'SignalIntegrity.Wavelets',
                'PySIApp',
                'Test/TestSignalIntegrity',
                'TestPySIApp'],
      data_files=[(pathToIcons, [pathToIcons+'/AppIcon2.gif']),
                  (pathToMoreIcons,
                    [pathToMoreIcons+'/document-new-3.gif',
                    pathToMoreIcons+'/document-open-2.gif',
                    pathToMoreIcons+'/document-save-2.gif',
                    pathToMoreIcons+'/tooloptions.gif',
                    pathToMoreIcons+'/help-contents-5.gif',
                    pathToMoreIcons+'/edit-add-2.gif',
                    pathToMoreIcons+'/edit-delete-6.gif',
                    pathToMoreIcons+'/draw-line-3.gif',
                    pathToMoreIcons+'/edit-copy-3.gif',
                    pathToMoreIcons+'/object-rotate-left-4.gif',
                    pathToMoreIcons+'/object-flip-horizontal-3.gif',
                    pathToMoreIcons+'/object-flip-vertical-3.gif',
                    pathToMoreIcons+'/zoom-in-3.gif',
                    pathToMoreIcons+'/zoom-out-3.gif',
                    pathToMoreIcons+'/edit-move.gif',
                    pathToMoreIcons+'/system-run-3.gif',
                    pathToMoreIcons+'/help-3.gif',
                    pathToMoreIcons+'/edit-undo-3.gif',
                    pathToMoreIcons+'/edit-redo-3.gif'],
                   ),
                  (pathToHelp,[pathToHelp+'/'+x for x in os.listdir(pathToHelp)]),
                  ('.', ['LICENSE.txt','README.txt'])],
      install_requires=install_requires,
      entry_points={
        'console_scripts': [
            'PySI = PySIApp.PySIApp:main']},
      test_suite='Test.TestSignalIntegrity.TestAll'
      )

#       test_loader=unittest.TestLoader().loadTestsFromModule(TestSignalIntegrity.TestAll, use_load_tests=True),
#       test_suite='TestSignalIntegrity.TestAll'

