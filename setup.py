'''
Created on May 15, 2017

@author: pete
'''
from setuptools import setup

install_requires=['numpy','matplotlib']

pathToIcons='PySIApp/icons/png/'
pathToMoreIcons=pathToIcons+'16x16/actions/'

setup(
      name='PySI',
      version='1.0',
      description='signal integrity tools',
      author='Peter J. Pupalaikis',
      author_email='pete_pope@hotmail.com',
      url='https://github.com/TeledyneLeCroy/PyNN',
      packages=['SignalIntegrity',
                'SignalIntegrity.ChirpZTransform',
                'SignalIntegrity.Conversions',
                'SignalIntegrity.Devices',
                'SignalIntegrity.FrequencyDomain',
                'SignalIntegrity.Helpers',
                'SignalIntegrity.ImpedanceProfile',
                'SignalIntegrity.Parsers',
                'SignalIntegrity.Parsers.Devices',
                'SignalIntegrity.SParameters',
                'SignalIntegrity.SParameters.Devices',
                'SignalIntegrity.Splines',
                'SignalIntegrity.SubCircuits',
                'SignalIntegrity.Symbolic',
                'SignalIntegrity.SystemDescriptions',
                'SignalIntegrity.TimeDomain',
                'SignalIntegrity.TimeDomain.Filters',
                'SignalIntegrity.TimeDomain.Waveform',
                'SignalIntegrity.Wavelets',
                'PySIApp'],
      data_files=[(pathToIcons, [pathToIcons+'AppIcon2.gif']),
                  (pathToMoreIcons,
                    [pathToMoreIcons+'document-new-3.gif',
                    pathToMoreIcons+'document-open-2.gif',
                    pathToMoreIcons+'document-save-2.gif',
                    pathToMoreIcons+'tooloptions.gif',
                    pathToMoreIcons+'help-contents-5.gif',
                    pathToMoreIcons+'edit-add-2.gif',
                    pathToMoreIcons+'edit-delete-6.gif',
                    pathToMoreIcons+'draw-line-3.gif',
                    pathToMoreIcons+'edit-copy-3.gif',
                    pathToMoreIcons+'object-rotate-left-4.gif',
                    pathToMoreIcons+'object-flip-horizontal-3.gif',
                    pathToMoreIcons+'object-flip-vertical-3.gif',
                    pathToMoreIcons+'zoom-in-3.gif',
                    pathToMoreIcons+'zoom-out-3.gif',
                    pathToMoreIcons+'edit-move.gif',
                    pathToMoreIcons+'system-run-3.gif',
                    pathToMoreIcons+'help-3.gif',
                    pathToMoreIcons+'edit-undo-3.gif',
                    pathToMoreIcons+'edit-redo-3.gif']),
                  ('./', ['LICENSE.txt']),
                  ('./', ['README.txt'])],
      install_requires=install_requires,
      entry_points={
        'console_scripts': [
            'PySI = PySIApp.PySIApp:main']}
      )
