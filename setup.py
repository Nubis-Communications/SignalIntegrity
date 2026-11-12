"""
setup.py
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

from setuptools import setup,find_packages
import codecs
import os
import unittest

#https://packaging.python.org/single_source_version/
base_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(base_dir, "SignalIntegrity", "__about__.py"), "r") as f:
    for line in f:
        if line[0]=='_' and '=' in line:
            token=line.split('=')
            keyValue=token[0].strip().strip('_')
            dataValue=eval(token[1].strip().strip(os.linesep))
            globals()['__'+keyValue+'__']=dataValue

install_requires=['setuptools>=58.2.0','pip>=20.2.4','numpy>=1.13.0','matplotlib>=2.2.3','urllib3>=1.22.0','Pillow>=5.4.1','scipy>=1.2.1']

pathToIcons='SignalIntegrity/App/icons/png'
pathToImages='SignalIntegrity/Images'
pathToHelp='https://nubis-communications.github.io/SignalIntegrity/SignalIntegrity/App/Help/site/index.html'
with open(os.path.join(base_dir, "README.md"), "r") as f:
    readmeFile=f.read()

setup(
    name=__project__,
    version=__version__,
    license=__license__,
    description=__description__,
    author=__author__,
    author_email=__email__,
    url=__url__,
    package_dir={'SignalIntegrity':'SignalIntegrity',
                 'SignalIntegrity.Lib':'SignalIntegrity/Lib',
                 'SignalIntegrity.App':'SignalIntegrity/App',
                 'SignalIntegrity.Utilities':'SignalIntegrity/Utilities'},
    packages=find_packages('.'),
    include_package_data=True,
    data_files=[('.',['LICENSE.txt','README.md']),
                (pathToIcons, [pathToIcons+'/AppIcon2.gif',
                               pathToIcons+'/AppIcon2.ico',
                               pathToIcons+'/gpl.gif']),
                (pathToImages,
                  [pathToImages+'/OpticalCalculations.png']),
                ('.', ['LICENSE.txt','README.md'])],
    install_requires=install_requires,
    extras_require={'test': ['pytest>=6'],
                    'qt': ['PySide6>=6.5']},
    python_requires='>=3.6',
    entry_points={
      'console_scripts': [
          'SignalIntegrity = SignalIntegrity.App.SignalIntegrityApp:main',
          'SignalIntegrityQt = SignalIntegrity.QtApp.SignalIntegrityQt:main',
          'ERL = SignalIntegrity.Utilities.ERL.ERL:ERL_Main',
          'PZ = SignalIntegrity.Utilities.PZ.PZ:PZ_Main',
          'IXT = SignalIntegrity.Utilities.IXT.IXT:IXT_Main']},
    long_description=readmeFile,
    long_description_content_type="text/markdown",
    classifiers=[
        __status__,
        __license__,
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Topic :: Scientific/Engineering",
    ],
    )
