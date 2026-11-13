"""
TestDisplayScaling.py
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

import os
import tkinter as tk
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from SignalIntegrity.App import MenuSystemHelpers as helpers


class TestDisplayScaling(unittest.TestCase):
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

    def testDisplayScaleUsesLinuxDpiAndEnvironment(self):
        originalScale=self.root.tk.call('tk','scaling')
        try:
            with patch.object(helpers.sys,'platform','linux'):
                for gdk,dpi in (('2','96'),('1','192')):
                    with self.subTest(gdk=gdk,dpi=dpi):
                        self.root.tk.call('tk','scaling',96.0/72.0)
                        with patch.dict(helpers.os.environ,{'GDK_SCALE':gdk}),patch.object(
                                helpers.subprocess,'run',return_value=SimpleNamespace(stdout='Xft.dpi: '+dpi)):
                            self.assertAlmostEqual(helpers.ConfigureDisplayScaling(self.root),2.0)
                        self.assertAlmostEqual(
                            float(self.root.tk.call('tk','scaling')),(96.0/72.0)*2.0,delta=0.02)
        finally:
            self.root.tk.call('tk','scaling',originalScale)

    def testDisplayScaleWithoutXrdbKeepsTkScale(self):
        originalScale=self.root.tk.call('tk','scaling')
        try:
            self.root.tk.call('tk','scaling',(96.0/72.0)*1.5)
            expected=float(self.root.tk.call('tk','scaling'))/(96.0/72.0)
            with patch.object(helpers.sys,'platform','linux'),patch.dict(
                    helpers.os.environ,{'GDK_SCALE':'1'}),patch.object(
                    helpers.subprocess,'run',side_effect=FileNotFoundError):
                self.assertAlmostEqual(helpers.ConfigureDisplayScaling(self.root),expected)
        finally:
            self.root.tk.call('tk','scaling',originalScale)

    def testDisplayScaleLeavesWindowsUnchanged(self):
        originalScale=self.root.tk.call('tk','scaling')
        with patch.object(helpers.sys,'platform','win32'),patch.object(helpers.subprocess,'run') as query:
            self.assertEqual(helpers.ConfigureDisplayScaling(self.root),1.0)
            self.assertEqual(self.root.tk.call('tk','scaling'),originalScale)
            query.assert_not_called()
