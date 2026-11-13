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

def IsolateSettings(test):
    """points the GUI settings (theme, recent projects) at a temporary folder for one test"""
    import tempfile, shutil
    from unittest import mock
    from SignalIntegrity.GuiCore.Settings import ENVIRONMENT_VARIABLE
    directory=tempfile.mkdtemp()
    patch=mock.patch.dict(os.environ,{ENVIRONMENT_VARIABLE:directory})
    patch.start()
    test.addCleanup(shutil.rmtree,directory,True)
    test.addCleanup(patch.stop)
    return directory

@unittest.skipUnless(havePySide6,'PySide6 is not installed')
class TestQtAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qapp=QApplication.instance() or QApplication([])
    def setUp(self):
        from SignalIntegrity.QtApp.MainWindow import MainWindow
        IsolateSettings(self)
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

@unittest.skipUnless(havePySide6,'PySide6 is not installed')
class TestQtStencilAndThemesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qapp=QApplication.instance() or QApplication([])
    def setUp(self):
        import tempfile
        from SignalIntegrity.QtApp.MainWindow import MainWindow
        self.cwd=os.getcwd()
        self.directory=tempfile.mkdtemp()
        IsolateSettings(self)
        self.errors=[]
        self.window=MainWindow()
        self.window.Error=self.errors.append
        self.window.resize(1200,800)
    def tearDown(self):
        import shutil
        from SignalIntegrity.QtApp import Theme
        Theme.Apply('builtin:light',save=False)
        self.window.close()
        os.chdir(self.cwd)
        shutil.rmtree(self.directory,ignore_errors=True)
    def _Part(self,description):
        return [p['index'] for p in self.window.partsDock.catalog if p['description']==description][0]
    def testStencilPopulatedAndFiltered(self):
        dock=self.window.partsDock
        tree=dock.tree
        self.assertGreater(len(dock.catalog),100)
        self.assertGreater(tree.topLevelItemCount(),10)
        self.assertFalse(dock.widget().isEnabled())    # nothing open yet
        dock.search.setText('skin resistor')
        visible=[tree.topLevelItem(i).child(k).text(0) for i in range(tree.topLevelItemCount())
                 for k in range(tree.topLevelItem(i).childCount())
                 if not tree.topLevelItem(i).isHidden() and not tree.topLevelItem(i).child(k).isHidden()]
        self.assertEqual(visible,['Two Port Skin-Effect Resistor'])
    def testNewDropPlaceDelete(self):
        from PySide6.QtCore import Qt, QPoint, QPointF
        from PySide6.QtGui import QDropEvent
        from PySide6.QtTest import QTest
        self.assertTrue(self.window.OpenProject(os.path.join(self.directory,'fresh'),new=True))
        self.assertTrue(self.window.partsDock.widget().isEnabled())
        view=self.window.view
        # drag a resistor from the stencil and drop it on the schematic
        item=[it for it in self.window.partsDock.tree.findItems('Two Port Resistor',Qt.MatchExactly|Qt.MatchRecursive)][0]
        data=self.window.partsDock.tree.mimeData([item])
        drop=QDropEvent(QPointF(view.viewport().rect().center()),Qt.CopyAction,data,Qt.LeftButton,Qt.NoModifier)
        view.dropEvent(drop)
        self.assertEqual([d['ref'] for d in view.devices],['R1'])
        self.assertEqual(self.window.selected,0)
        self.assertTrue(self.window.deleteAction.isEnabled())
        # double-click arms placement, a click places it
        self.window.OnPlaceRequested(self._Part('One Port Capacitor to Ground'))
        self.assertIsNotNone(view.placing)
        QTest.mouseClick(view.viewport(),Qt.LeftButton,Qt.NoModifier,view.viewport().rect().center()+QPoint(80,0))
        self.assertIsNone(view.placing)
        self.assertEqual([d['ref'] for d in view.devices],['R1','C1'])
        # Esc cancels placement
        self.window.OnPlaceRequested(0)
        QTest.keyClick(view,Qt.Key_Escape)
        self.assertIsNone(view.placing)
        self.assertEqual(len(view.devices),2)
        # Delete removes the selected part
        QTest.keyClick(view,Qt.Key_Delete)
        self.assertEqual([d['ref'] for d in view.devices],['R1'])
        self.assertIsNone(self.window.selected)
        self.assertFalse(self.window.deleteAction.isEnabled())
        self.window.OnSave()
        self.assertEqual(self.errors,[])
    def testThemeSwitchRecolors(self):
        from SignalIntegrity.GuiCore import Themes
        from SignalIntegrity.QtApp import Theme
        self.window.OpenProject(os.path.join(EXAMPLES,'RLC.si'))
        def background():
            return self.window.view.backgroundBrush().color().name()
        self.window.SetTheme('builtin:dark')
        dark=Themes.LoadTheme('builtin:dark')[1]
        self.assertEqual(background(),dark['schematicBackground'])
        self.assertEqual(Theme.CurrentId(),'builtin:dark')
        self.assertEqual(Themes.SavedThemeId(),'builtin:dark')
        from PySide6.QtCore import Qt
        inks={item.pen().color().name() for item in self.window.view.scene().items()
              if hasattr(item,'pen') and item.pen().style()!=Qt.NoPen}
        self.assertIn(dark['schematicInk'],inks)
        self.assertNotIn('#000000',inks)
        # a theme file the user picks from disk
        path=os.path.join(self.directory,'mine.json')
        with open(path,'w') as f:
            f.write('{"name":"Mine","type":"dark","colors":{"editor.background":"#202030",}}')
        self.window.SetTheme(path)
        self.assertEqual(background(),'#202030')
        self.assertEqual(self.window.themeName,'Mine')
        self.window.SetTheme(os.path.join(self.directory,'missing.json'))
        self.assertEqual(len(self.errors),1)
        self.assertEqual(background(),'#202030')
        self.window.BuildThemeMenu()
        labels=[a.text() for a in self.window.themeMenu.actions()]
        self.assertIn('SignalIntegrity Dark',labels)
        self.assertIn('Load Theme File...',labels)
    def testMenusLikeTk(self):
        from SignalIntegrity.GuiCore.Menus import CommandIds
        titles=[a.text().replace('&','') for a in self.window.menuBar().actions()]
        self.assertEqual(titles,['File','Edit','Parts','Wires','View','Calculate','Variables','Help'])
        self.assertEqual(sorted(self.window.actions),sorted(CommandIds('qt')))
        fileMenu=self.window.menuBar().actions()[0].menu()
        self.assertIn('Open Recent Projects',[a.text() for a in fileMenu.actions()])
    def testRecentProjects(self):
        recent=self.window.submenus['recent']
        self.window.BuildRecentMenu()
        self.assertEqual([a.text() for a in recent.actions() if not a.isSeparator()][0],'(no recent projects)')
        self.window.OpenProject(os.path.join(EXAMPLES,'RLC.si'))
        self.window.OpenProject(os.path.join(self.directory,'fresh'),new=True)
        self.window.BuildRecentMenu()
        entries=[a for a in recent.actions() if a.toolTip().endswith('.si')]
        self.assertEqual([os.path.basename(a.toolTip()) for a in entries],['fresh.si','RLC.si'])
        entries[1].trigger()
        self.assertIn('RLC.si',self.window.windowTitle())
        [a for a in recent.actions() if a.text()=='Clear Recent Projects'][0].trigger()
        self.assertEqual([a.text() for a in recent.actions() if not a.isSeparator()][0],'(no recent projects)')
    def testDrawSelectDeleteWire(self):
        from PySide6.QtCore import Qt, QPointF
        from PySide6.QtTest import QTest
        import importlib
        BuildDivider=importlib.import_module('TestGuiCore.TestGuiCore').BuildDivider
        session=self.window.session
        BuildDivider(session,self.directory)
        self.window.ShowLevel(session.Render())
        self.window.show()
        view=self.window.view
        at=lambda x,y: view.mapFromScene(QPointF(x,y))
        self.assertFalse(view.wiring)
        self.window.wireAction.trigger()
        self.assertTrue(view.wiring and self.window.wireAction.isChecked())
        # clicks snap to the grid; a double-click finishes the wire
        QTest.mouseClick(view.viewport(),Qt.LeftButton,Qt.NoModifier,at(97,159))
        QTest.mouseClick(view.viewport(),Qt.LeftButton,Qt.NoModifier,at(96,97))
        QTest.mouseDClick(view.viewport(),Qt.LeftButton,Qt.NoModifier,at(239,96))
        self.assertEqual([w['points'] for w in session.Wires()],[[96.,160.,96.,96.,240.,96.]])
        # still in wire mode: a right-click finishes the next wire
        for x,y in ((304,96),(400,96),(496,96),(496,80)):
            QTest.mouseClick(view.viewport(),Qt.LeftButton,Qt.NoModifier,at(x,y))
        QTest.mouseClick(view.viewport(),Qt.RightButton,Qt.NoModifier,at(496,80))
        self.assertEqual(len(session.Wires()),3)
        self.assertTrue(self.window.calculationActions['simulate'].isEnabled())
        self.assertIn('connect R1 2 R2 1',session.NetList())
        # Esc drops a half-drawn wire, a second Esc leaves wire mode
        QTest.mouseClick(view.viewport(),Qt.LeftButton,Qt.NoModifier,at(600,300))
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import QEvent
        move=QPointF(at(700,300))
        self.qapp.sendEvent(view.viewport(),QMouseEvent(QEvent.MouseMove,move,view.viewport().mapToGlobal(move),
                                                       Qt.NoButton,Qt.NoButton,Qt.NoModifier))
        self.assertEqual(view.wireCursor,(704.,304.))
        self.assertIsNotNone(view.wirePreview)
        self.window.actions['cancel'].trigger()
        self.assertTrue(view.wiring)
        self.assertEqual(view.wirePoints,[])
        self.assertIsNone(view.wirePreview)
        self.window.actions['cancel'].trigger()
        self.assertFalse(view.wiring or self.window.wireAction.isChecked())
        # clicking a wire selects it; Delete Selected removes it
        QTest.mouseClick(view.viewport(),Qt.LeftButton,Qt.NoModifier,at(96,130))
        self.assertEqual(self.window.SelectedWire(),0)
        self.assertIsNone(self.window.selected)
        self.assertTrue(self.window.actions['deleteWire'].isEnabled())
        self.assertFalse(self.window.actions['deletePart'].isEnabled())
        self.window.deleteAction.trigger()
        self.assertEqual(len(session.Wires()),2)
        self.assertIsNone(self.window.SelectedWire())
        self.assertEqual(self.errors,[])
    def testEditingCommands(self):
        import shutil
        from PySide6.QtCore import Qt, QPointF
        from PySide6.QtTest import QTest
        shutil.copy(os.path.join(EXAMPLES,'RLC.si'),self.directory)
        w=self.window
        w.OpenProject(os.path.join(self.directory,'RLC.si'))
        a=w.actions
        self.assertFalse(a['undo'].isEnabled() or a['redo'].isEnabled() or a['paste'].isEnabled())
        resistor=[d['index'] for d in w.view.devices if d['partname']=='Resistor'][0]
        w.OnDeviceClicked(resistor)
        count=len(w.view.devices)
        a['copy'].trigger()
        self.assertTrue(a['paste'].isEnabled())
        a['paste'].trigger()
        self.assertEqual(len(w.view.devices),count+1)
        self.assertEqual(w.view.devices[w.selected]['ref'],'R2')
        a['duplicate'].trigger()
        self.assertEqual(w.view.devices[w.selected]['ref'],'R3')
        a['flipVertical'].trigger()
        self.assertTrue(w.session.app.Drawing.schematic.deviceList[w.selected].partPicture.current.mirroredVertically)
        self.assertEqual(a['undo'].text(),'Undo flip part')
        for _ in range(3):
            a['undo'].trigger()
        self.assertEqual(len(w.view.devices),count)
        self.assertTrue(a['redo'].isEnabled())
        a['redo'].trigger()
        self.assertEqual(len(w.view.devices),count+1)
        # drag a wire corner one grid down
        w.show()
        view=w.view
        at=lambda x,y: view.mapFromScene(QPointF(x,y))
        wire=w.session.Wires()[0]
        x,y=wire['points'][0],wire['points'][1]
        QTest.mousePress(view.viewport(),Qt.LeftButton,Qt.NoModifier,at(x,y))
        self.assertEqual(w.drawing['selectedVertex'],[0,0])
        self.assertTrue(a['deleteVertex'].isEnabled() and a['duplicateVertex'].isEnabled())
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import QEvent
        target=QPointF(at(x,y+2*view.grid))
        self.qapp.sendEvent(view.viewport(),QMouseEvent(QEvent.MouseMove,target,view.viewport().mapToGlobal(target),
                                                       Qt.LeftButton,Qt.LeftButton,Qt.NoModifier))
        self.assertIsNotNone(view.wirePreview)
        QTest.mouseRelease(view.viewport(),Qt.LeftButton,Qt.NoModifier,at(x,y+2*view.grid))
        corners=[[ww['points'][k],ww['points'][k+1]] for ww in w.session.Wires() for k in range(0,len(ww['points']),2)]
        self.assertIn([x,y+2*view.grid],corners)
        self.assertEqual(a['undo'].text(),'Undo move vertex')
        self.assertEqual(self.errors,[])
    def testEquationsPreferencesAndResultWindows(self):
        from unittest import mock
        from PySide6.QtWidgets import QDialog
        from SignalIntegrity.QtApp.Dialogs import TextEditorDialog, PreferencesDialog
        from SignalIntegrity.QtApp.SimulatorWindow import NoiseWindow, SParametersWindow
        w=self.window
        w.OpenProject(os.path.join(self.directory,'eq'),new=True)
        dialog=TextEditorDialog('Equations','x = 1 +',w.session.CheckEquations)
        self.assertNotEqual(dialog.status.text(),'No Errors')
        dialog.editor.setPlainText('x = 1 + 2'); dialog.Check()
        self.assertEqual(dialog.status.text(),'No Errors')
        with mock.patch.object(TextEditorDialog,'exec',return_value=QDialog.Accepted), \
             mock.patch.object(TextEditorDialog,'Text',return_value='a = 3'):
            w.actions['equations'].trigger()
        self.assertEqual(w.session.Equations(),'a = 3')
        self.assertTrue(w.actions['undo'].isEnabled())
        prefsFile=os.path.join(self.directory,'preferences.xml')
        with mock.patch.dict(os.environ,{'SIGNALINTEGRITY_PREFERENCES':prefsFile}):
            from SignalIntegrity.GuiCore.Session import ProjectSession
            ProjectSession()
            prefs=PreferencesDialog()
            editor=prefs.editors['Appearance.FontSize']
            editor.setText('14'); editor.editingFinished.emit()
            self.assertIn('= 14',prefs.status.text())
            editor.setText('huge'); editor.editingFinished.emit()
            self.assertIn('invalid',prefs.status.text())
            with open(prefsFile) as f:
                self.assertIn('<FontSize>14</FontSize>',f.read())
        ProjectSession()
        session=w.session
        session.Open(os.path.join(os.path.dirname(EXAMPLES),'..','..','Test','TestSignalIntegrity','TestStatisticalNoise','StatisticalNoise.si'))
        result=session.Calculate('simulate')
        noise=NoiseWindow(result)
        self.assertEqual(noise.table.topLevelItemCount(),2)
        self.assertEqual(noise.table.topLevelItem(0).childCount(),2)
        self.assertEqual(len(noise.panel.axes.get_lines()),2)
        noise.close()
        session.Open(os.path.join(EXAMPLES,'RLCTest2SP.si'))
        sp=SParametersWindow(session.Calculate('sparameters'))
        titles=[sp.tabs.tabText(i) for i in range(sp.tabs.count())]
        self.assertEqual([t.split()[-1] for t in titles][-3:],['impulse','step','impedance'])
        sp.tabs.setCurrentIndex(titles.index([t for t in titles if t.endswith('impedance')][0]))
        self.assertEqual(len(sp.panels[-1].axes.get_lines()),3)
        sp.close()
        self.assertEqual(self.errors,[])

if __name__ == '__main__':
    unittest.main()
