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
        self.window.propertiesTable.item(row,3).setText('22')
        self.assertTrue(self.window.propertiesTable.item(row,3).text().startswith('22.0'))
        self.assertIn('device R1 1 R 22.0',self.window.session.NetList())
        self.assertEqual(self.errors,[])
    def testPropertyVisibilityCheckboxes(self):
        from PySide6.QtCore import Qt
        self.window.OpenProject(os.path.join(EXAMPLES,'PID','PIDSimulation.si'))
        pid=[d for d in self.window.view.devices if d['ref']=='PID'][0]['index']
        self.window.OnDeviceClicked(pid)
        row=self.window.propertyKeywords.index('ref')
        texts=lambda: [i.text() for i in self.window.view.scene().items() if hasattr(i,'text') and callable(i.text)]
        self.assertNotIn('ref PID',texts())
        self.window.propertiesTable.item(row,1).setCheckState(Qt.Checked)
        self.assertIn('ref PID',texts())
        self.window.variablesTable.item(0,0).setCheckState(Qt.Unchecked)
        self.assertNotIn('PID_P 60.0 ',texts())
        self.assertEqual(self.errors,[])
    def testTraversal(self):
        self.window.OpenProject(os.path.join(EXAMPLES,'PID','PIDSimulation.si'))
        pid=[d for d in self.window.view.devices if d['ref']=='PID'][0]['index']
        self.window.OnDeviceClicked(pid)
        self.assertTrue(self.window.viewDeviceAction.isEnabled())
        self.assertFalse(self.window.upAction.isEnabled())
        self.window.OnViewSelected()
        self.assertIn('PIDSimulation.si > PID.si (Read Only)',self.window.windowTitle())
        self.assertTrue(self.window.upAction.isEnabled())
        self.assertFalse(self.window.saveAction.isEnabled())
        self.assertEqual([self.window.variablesTable.item(r,2).text() for r in range(3)],['60.0','500.0','15.0'])
        self.window.OnAscend()
        self.assertNotIn('Read Only',self.window.windowTitle())
        self.assertEqual(self.window.selected,pid)
        self.assertEqual(self.errors,[])
    def testSimulateShowsResults(self):
        self.window.OpenProject(os.path.join(EXAMPLES,'RLC.si'))
        self.window.RunCalculation('simulate')
        self._Wait()
        self.assertEqual(self.errors,[])
        simulator=list(self.window.simulatorWindows.values())[0]
        self.assertEqual([line.get_label() for line in simulator.plt.get_lines()],['Vout'])
        # like the tk simulator dialog, the toolbar starts in pan mode
        self.assertEqual(str(simulator.panel.toolbar.mode),'pan/zoom')
    def testZoomRetainedAcrossRecalculation(self):
        self.window.OpenProject(os.path.join(EXAMPLES,'PID','PIDSimulation.si'))
        self.window.RunCalculation('simulate')
        self._Wait()
        simulator=list(self.window.simulatorWindows.values())[0]
        self.assertEqual([l.get_label() for l in simulator.plt.get_lines()],['VO','VPID','VU','P','I','D','Vin'])
        simulator.plt.set_xlim(-0.2,0.4)
        simulator.plt.set_ylim(-1.,2.)
        simulator.recalculate.emit()
        self._Wait()
        self.assertIs(list(self.window.simulatorWindows.values())[0],simulator)
        self.assertEqual(tuple(simulator.plt.get_xlim()),(-0.2,0.4))
        self.assertEqual(tuple(simulator.plt.get_ylim()),(-1.,2.))
        # hiding a waveform keeps the zoom too
        simulator.selections[0].setChecked(False)
        simulator.onSelection()
        self.assertEqual(tuple(simulator.plt.get_xlim()),(-0.2,0.4))
        self.assertNotIn('VO',[l.get_label() for l in simulator.plt.get_lines()])
        simulator.onAutoscale()
        self.assertNotEqual(tuple(simulator.plt.get_xlim()),(-0.2,0.4))
        simulator.contentAction.trigger()
        self.assertEqual(simulator.panel.label.text(),'Spectral Content')
        self.assertEqual(self.errors,[])
    def testSParametersShowsResults(self):
        self.window.OpenProject(os.path.join(EXAMPLES,'RLCTest2SP.si'))
        self.window.RunCalculation('sparameters')
        self._Wait()
        self.assertEqual(self.errors,[])
        panels=self.window.resultsWindows[0].panels
        self.assertEqual(len(panels),2)
        lines=len(panels[0].axes.get_lines())
        self.assertEqual(int(round(lines**0.5))**2,lines)
        self.assertEqual(str(panels[0].toolbar.mode),'pan/zoom')

if __name__ == '__main__':
    unittest.main()
