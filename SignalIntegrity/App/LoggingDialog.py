"""
LoggingDialog.py

The dialog that controls the logging categories and depth.
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
import tkinter as tk

from SignalIntegrity.App.CalculationPropertiesProject import PropertiesDialog,CalculationProperty,CalculationPropertyTrueFalseButton,CalculationPropertyChoices
from SignalIntegrity.Lib.Log import Categories,Levels,LogConfiguration

class LoggingDialog(PropertiesDialog):
    """Dialog for turning the logging categories on and off.

    Each category is turned on or off individually and a single depth applies to
    all of the categories that are turned on.
    """
    def __init__(self,parent,preferences):
        PropertiesDialog.__init__(self,parent,preferences,parent,'Logging')
        self.enabled=CalculationPropertyTrueFalseButton(self.propertyListFrame,'enable logging',None,
            self.onUpdatePreferences,preferences,'Logging.Enabled')
        self.level=CalculationPropertyChoices(self.propertyListFrame,'logging depth',None,
            self.onUpdatePreferences,[(level.lower(),level) for level in Levels],preferences,'Logging.Level')
        self.CategoriesFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.CategoriesFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        # one on/off button per logging category, generated from the categories
        # themselves so that adding a category needs no change here.
        self.categories={category:CalculationPropertyTrueFalseButton(self.CategoriesFrame,'log '+category,None,
                            self.onUpdatePreferences,preferences,'Logging.Categories.'+category,
                            tooltip=Categories[category])
                         for category in sorted(Categories.keys())}
        self.DestinationsFrame=tk.Frame(self.propertyListFrame, relief=tk.RIDGE, borderwidth=5)
        self.DestinationsFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.console=CalculationPropertyTrueFalseButton(self.DestinationsFrame,'log to console',None,
            self.onUpdatePreferences,preferences,'Logging.Console')
        self.file=CalculationPropertyTrueFalseButton(self.DestinationsFrame,'log to file',None,
            self.onUpdatePreferences,preferences,'Logging.File')
        self.fileName=CalculationProperty(self.DestinationsFrame,'log file',None,
            self.onUpdatePreferences,preferences,'Logging.FileName')
        self.Finish()

    def onUpdatePreferences(self):
        self.ShowProperties()
        self.project.SaveToFile()
        # applied as an explicit user action, which is why it is applied at the
        # highest precedence - it must not be undone the next time a project (or a
        # sub-project) re-applies the preferences.
        LogConfiguration.Configure(self.project['Logging'].Dictionary(),source='api')

    def ShowProperties(self):
        enabled=self.project['Logging.Enabled']
        self.level.Show(enabled)
        for category in self.categories:
            self.categories[category].Show(enabled)
        self.console.Show(enabled)
        self.file.Show(enabled)
        self.fileName.Show(enabled and self.project['Logging.File'])

    def Finish(self):
        self.ShowProperties()
        PropertiesDialog.Finish(self)
