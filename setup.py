"""
setup.py
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

install_requires=['setuptools>=24.2.0','pip>=9.0.0','numpy>=1.13.0','matplotlib>=2.2.3','urllib3>=1.22.0']

pathToIcons='SignalIntegrity/App/icons/png'
pathToMoreIcons=pathToIcons+'/16x16/actions'
pathToHelp='http://teledynelecroy.github.io/SignalIntegrity/SignalIntegrity/App/Help/Help.html.LyXconv/Help-Section-1.html#toc-Section-1'

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
				'SignalIntegrity.App':'SignalIntegrity/App'},
    packages=find_packages('.'),
    include_package_data=True,
    data_files=[('.',['LICENSE.txt','README.md']),
                (pathToIcons, [pathToIcons+'/AppIcon2.gif',
                               pathToIcons+'/gpl.gif',
                               pathToIcons+'/tlecroy-logo-15.gif']),
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
                  pathToMoreIcons+'/edit-redo-3.gif',
                  pathToMoreIcons+'/dialog-information-4.gif',
                  pathToMoreIcons+'/sp-view.gif'],
                 ),
                ('.', ['LICENSE.txt','README.md'])],
    install_requires=install_requires,
    python_requires='>=2.7.11,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*',
    entry_points={
      'console_scripts': [
          'SignalIntegrity = SignalIntegrity.App.SignalIntegrityApp:main']},
    long_description=readmeFile,
    long_description_content_type="text/markdown",
    classifiers=[
        __status__,
        __license__,
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Topic :: Scientific/Engineering",
    ],
    )
