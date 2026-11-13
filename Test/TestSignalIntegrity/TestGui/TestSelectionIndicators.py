"""
TestSelectionIndicators.py
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
import os
from tkinter import font as tkfont
import unittest
from unittest.mock import patch

from SignalIntegrity.App import MenuSystemHelpers as helpers
import SignalIntegrity.App
from SignalIntegrity.App.CalculationPropertiesProject import CalculationPropertyChoices


class TestSelectionIndicators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root=tk.Tk()
        except tk.TclError as error:
            if os.environ.get('SIGNALINTEGRITY_REQUIRE_GUI_TESTS') == '1':
                raise
            raise unittest.SkipTest('Tk display unavailable: '+str(error))
        cls.root.withdraw()
        cls.addClassCleanup(cls.root.destroy)
        cls.addClassCleanup(cls.root.update_idletasks)

    def tearDown(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def testLinuxIndicatorsFollowFontWithoutDoubleScaling(self):
        sizes=[]
        with patch.object(helpers.sys,'platform','linux'):
            for scale in (1.0,1.5,2.0):
                with self.subTest(scale=scale):
                    self.root.tk.call('tk','scaling',(96.0/72.0)*scale)
                    font=tkfont.Font(root=self.root,family='Arial',size=12)
                    radio=helpers.SizeSelectionIndicator(tk.Radiobutton(self.root,font=font))
                    checkbox=helpers.SizeSelectionIndicator(tk.Checkbutton(self.root,font=font))
                    size=radio._indicatorImages[0].width()
                    self.assertEqual(size,checkbox._indicatorImages[0].width())
                    self.assertGreaterEqual(size,font.metrics('linespace')*0.65)
                    self.assertLess(size,font.metrics('linespace'))
                    sizes.append(size)
                    radio.destroy()
                    checkbox.destroy()
        self.assertGreater(sizes[-1],sizes[0]*1.8)
        self.assertLess(sizes[-1],sizes[0]*2.2)

    def testLinuxRadioAndCheckboxSelection(self):
        changes=[]
        with patch.object(helpers.sys,'platform','linux'):
            choices=CalculationPropertyChoices(
                self.root,'Noise type',lambda event: changes.append('radio'),None,
                [('White noise','white'),('Spectral density file','file')])
            radios=choices.entry.winfo_children()
            self.assertTrue(all(hasattr(radio,'_indicatorImages') for radio in radios))
            radios[1].invoke()
            self.assertEqual(choices.Get(),'file')
            self.assertEqual(changes,['radio'])
            value=tk.BooleanVar(master=self.root,value=False)
            checkbox=helpers.SizeSelectionIndicator(tk.Checkbutton(
                self.root,variable=value,command=lambda: changes.append('checkbox')))
            checkbox.invoke()
            self.assertTrue(value.get())
            checkbox.invoke()
            self.assertFalse(value.get())
            self.assertEqual(changes,['radio','checkbox','checkbox'])

    def testOtherPlatformsKeepNativeIndicators(self):
        for platform in ('win32','darwin'):
            with self.subTest(platform=platform),patch.object(helpers.sys,'platform',platform):
                for widgetType in (tk.Radiobutton,tk.Checkbutton):
                    widget=widgetType(self.root)
                    self.assertIs(helpers.SizeSelectionIndicator(widget),widget)
                    self.assertFalse(hasattr(widget,'_indicatorImages'))
                    self.assertTrue(widget.cget('indicatoron'))

    def testVariableIconsUseToolbarScaling(self):
        for filename in ('edit-add-2.gif','up.gif','down.gif','edit-delete-6.gif','edit-3.gif'):
            with self.subTest(filename=filename):
                path=SignalIntegrity.App.IconsDir+filename
                with patch.object(helpers.sys,'platform','linux'),patch.dict(helpers.os.environ,{'GDK_SCALE':'1'}):
                    self.root.tk.call('tk','scaling',96.0/72.0)
                    toolbar=helpers.ToolBarElement(self.root,iconfile=path)
                    width,height=toolbar.icon.width(),toolbar.icon.height()
                    self.root.tk.call('tk','scaling',(96.0/72.0)*2.0)
                    toolbar.UpdateIcon()
                self.assertEqual(toolbar.icon.width(),width*2)
                self.assertEqual(toolbar.icon.height(),height*2)
                toolbar.button.destroy()
