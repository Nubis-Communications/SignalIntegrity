"""
setup.py
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

from setuptools import setup,find_packages
import os
import unittest

try:
    from Test.TestSignalIntegrity import *
except:
    pass

from SignalIntegrity.__about__ import __version__,__url__,__copyright__,__description__,__author__,__email__,__license__

install_requires=['setuptools>=24.2.0','pip>=9.0.0','numpy>=1.13.0','matplotlib>=2.2.3','urllib3>=1.22.0']

pathToIcons='PySIApp/icons/png'
pathToMoreIcons=pathToIcons+'/16x16/actions'
pathToHelp='http://teledynelecroy.github.io/PySI/PySIApp/Help/PySIHelp.html.LyXconv/PySIHelp-Section-1.html#toc-Section-1'

setup(
    name='PySI',
    version=__version__,
    license=__license__,
    description=__description__,
    author=__author__,
    author_email=__email__,
    url=__url__,
    package_dir={'SignalIntegrity':'SignalIntegrity'},
    packages=find_packages(''),
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
                ('.', ['LICENSE.txt','README.md'])],
    install_requires=install_requires,
    python_requires='>=2.7.15',
    entry_points={
      'console_scripts': [
          'PySI = PySIApp.PySIApp:main']},
    test_suite='Test.TestSignalIntegrity.TestAll'
    )
