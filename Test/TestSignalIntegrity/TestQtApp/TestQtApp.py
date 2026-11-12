"""
TestQtApp.py
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

try:
    import PySide6
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    from PySide6.QtWidgets import QApplication, QMessageBox
    havePySide6=True
except ImportError:
    havePySide6=False

EXAMPLES=os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
    '..','..','..','SignalIntegrity','App','Examples'))

@unittest.skipUnless(havePySide6,'PySide6 is not installed')
class TestQtAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qapp=QApplication.instance() or QApplication([])
    def setUp(self):
        from SignalIntegrity.QtApp.MainWindow import MainWindow
        self.cwd=os.getcwd()
        self.errors=[]
        self.window=MainWindow()
        self.window.Error=self.errors.append
    def tearDown(self):
        for w in self.window.resultsWindows:
            w.close()
        self.window.close()
        os.chdir(self.cwd)
    def _Wait(self):
        while self.window.worker is not None:
            self.window.worker.wait(50)
            self.qapp.processEvents()
    def testStartsEmpty(self):
        self.assertEqual(len(self.window.view.scene().items()),0)
        self.assertFalse(self.window.saveAction.isEnabled())
        self.assertFalse(any(a.isEnabled() for a in self.window.calculationActions.values()))
    def testOpenRendersSchematic(self):
        self.assertTrue(self.window.OpenProject(os.path.join(EXAMPLES,'RLC.si')))
        self.assertGreater(len(self.window.view.scene().items()),20)
        self.assertIn('RLC.si',self.window.windowTitle())
        self.assertTrue(self.window.calculationActions['simulate'].isEnabled())
        self.assertFalse(self.window.calculationActions['sparameters'].isEnabled())
        self.assertEqual(self.window.calculationEdits['FrequencyPoints'].text(),'2000')
    def testOpenMissingReportsError(self):
        self.assertFalse(self.window.OpenProject(os.path.join(EXAMPLES,'Missing.si')))
        self.assertEqual(len(self.errors),1)
    def testSelectAndEditProperty(self):
        self.window.OpenProject(os.path.join(EXAMPLES,'RLC.si'))
        device=[d for d in self.window.view.devices if d['partname']=='Resistor'][0]
        self.window.OnDeviceClicked(device['index'])
        self.assertEqual(self.window.selected,device['index'])
        self.assertTrue(self.window.rotateAction.isEnabled())
        row=self.window.propertyKeywords.index('r')
        self.window.propertiesTable.item(row,1).setText('22')
        self.assertTrue(self.window.propertiesTable.item(row,1).text().startswith('22.0'))
        self.assertIn('device R1 1 R 22.0',self.window.session.NetList())
        self.assertEqual(self.errors,[])
    def testSimulateShowsResults(self):
        self.window.OpenProject(os.path.join(EXAMPLES,'RLC.si'))
        self.window.RunCalculation('simulate')
        self._Wait()
        self.assertEqual(self.errors,[])
        self.assertEqual(len(self.window.resultsWindows),1)
        axes=self.window.resultsWindows[0].figures[0].axes[0]
        self.assertEqual([line.get_label() for line in axes.get_lines()],['Vout'])
    def testSParametersShowsResults(self):
        self.window.OpenProject(os.path.join(EXAMPLES,'RLCTest2SP.si'))
        self.window.RunCalculation('sparameters')
        self._Wait()
        self.assertEqual(self.errors,[])
        figures=self.window.resultsWindows[0].figures
        self.assertEqual(len(figures),2)
        lines=len(figures[0].axes[0].get_lines())
        self.assertEqual(int(round(lines**0.5))**2,lines)

if __name__ == '__main__':
    unittest.main()
