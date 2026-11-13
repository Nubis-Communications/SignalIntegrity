"""Focused tests for reversible desktop appearance."""

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

import ast
import os
import tempfile
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch
from unittest.mock import Mock
from types import SimpleNamespace

import matplotlib

from SignalIntegrity.App.Drawing import SchematicCanvas
from SignalIntegrity.App.DeviceProperties import DevicePartPictureCanvas
from SignalIntegrity.App.PreferencesFile import PreferencesFile
from SignalIntegrity.App.Theme import ApplyTheme, PALETTES, PALETTE_VARIANTS, ThemeSelector,ThemeColorButton,ContrastRatio
from SignalIntegrity.App.MenuSystemHelpers import ToolBarElement,ToolTip,Doer,IconLabel,SizeSelectionIndicator
from PIL import ImageTk
from SignalIntegrity.App.ToolbarIcons import ICON_PATHS,RenderToolbarIcon
from SignalIntegrity.App.TikZ import TikZ


class TestTheme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root = tk.Tk()
        except tk.TclError:
            if os.environ.get('SIGNALINTEGRITY_REQUIRE_GUI_TESTS') == '1':
                raise
            raise unittest.SkipTest('No Tk display available')
        cls.plotDefaults = matplotlib.rcParams.copy()

    @classmethod
    def tearDownClass(cls):
        cls.root.update_idletasks()
        cls.root.destroy()
        matplotlib.rcParams.update(cls.plotDefaults)

    def setUp(self):
        self.root.withdraw()
        self.preferences = PreferencesFile()
        self.apply('Legacy')

    def tearDown(self):
        self.preferences = PreferencesFile()
        self.apply('Legacy')
        for widget in self.root.winfo_children():
            widget.destroy()
        matplotlib.rcParams.update(self.plotDefaults)

    def apply(self, name):
        self.preferences['Appearance.Theme'] = name
        ApplyTheme(self.root, self.preferences)

    def test_switching_restores_legacy_controls_and_custom_preferences(self):
        entry = tk.Entry(self.root, readonlybackground='light gray')
        button = tk.Button(self.root)
        self.preferences['Appearance.Color.Background'] = '#eeddcc'
        self.preferences['Appearance.Color.Plot'] = '#ffeedd'
        self.apply('Legacy')
        baseline = (entry.cget('background'), entry.cget('readonlybackground'),
                    button.cget('background'), ttk.Style(self.root).theme_use())
        for name in ('Dark', 'Light', 'Dark'):
            self.apply(name)
            self.assertEqual(button.cget('background'), PALETTES[name]['background'])
            self.assertEqual(entry.cget('background'), PALETTES[name]['fieldbackground'])
            self.assertEqual(entry.cget('readonlybackground'), PALETTES[name]['readonlybackground'])
        self.apply('Legacy')
        self.assertEqual(baseline, (entry.cget('background'), entry.cget('readonlybackground'),
                                   button.cget('background'), ttk.Style(self.root).theme_use()))
        self.assertEqual(self.preferences['Appearance.Color.Background'], '#eeddcc')
        self.assertEqual(matplotlib.rcParams['figure.facecolor'], '#ffeedd')

    def test_new_controls_and_combobox_popdown_follow_theme(self):
        self.apply('Dark')
        entry = tk.Entry(self.root, readonlybackground='light gray')
        combo = ttk.Combobox(self.root, state='readonly', values=('one', 'two'))
        entry.pack()
        combo.pack()
        self.root.deiconify()
        self.root.update()
        self.assertEqual(entry.cget('readonlybackground'), PALETTES['Dark']['readonlybackground'])
        self.assertEqual(ttk.Style(self.root).lookup('TCombobox', 'fieldbackground', ('readonly',)),
                         PALETTES['Dark']['fieldbackground'])
        self.apply('Light')
        popdown = self.root.tk.call('ttk::combobox::PopdownWindow', str(combo))
        self.assertEqual(self.root.tk.call(str(popdown) + '.f.l', 'cget', '-background'),
                         PALETTES['Light']['fieldbackground'])
        self.apply('Legacy')
        self.assertEqual(entry.cget('readonlybackground'), 'light gray')

    def test_schematic_items_switch_without_mutating_export_colors_or_geometry(self):
        canvas = SchematicCanvas(self.root, 1.5)
        line = canvas.create_line(0, 0, 20, 20, fill='black', tags=('wire',))
        selected = canvas.create_oval(0, 0, 10, 10, fill='blue', outline='black')
        coords, width = canvas.coords(line), canvas.itemcget(line, 'width')
        export = TikZ()
        export.create_line(0, 0, 20, 20, fill='black')
        exportBefore = list(export.lineList)
        for name in ('Dark', 'Light'):
            self.apply(name)
            self.assertEqual(canvas.itemcget(line, 'fill'), PALETTES[name]['schematicforeground'])
            self.assertEqual(canvas.itemcget(selected, 'fill'), PALETTES[name]['schematicselection'])
            self.assertEqual(canvas.coords(line), coords)
            self.assertEqual(canvas.itemcget(line, 'width'), width)
            self.assertIn('wire', canvas.gettags(line))
            newLine = canvas.create_line(0, 0, 10, 10, fill='black')
            self.assertEqual(canvas.itemcget(newLine, 'fill'), PALETTES[name]['schematicforeground'])
        self.assertEqual(export.lineList, exportBefore)
        otherExport = TikZ()
        otherExport.create_line(0, 0, 20, 20, fill='black')
        self.assertEqual(otherExport.lineList, exportBefore)
        self.apply('Legacy')
        self.assertEqual(canvas.itemcget(line, 'fill'), 'black')
        self.assertEqual(canvas.itemcget(selected, 'fill'), 'blue')

    def test_device_preview_opened_in_dark_mode_remains_readable(self):
        self.apply('Dark')
        preview = DevicePartPictureCanvas(self.root, 2)
        line = preview.create_line(0, 0, 10, 10, fill='black')
        self.assertEqual(preview.itemcget(line, 'fill'), PALETTES['Dark']['schematicforeground'])
        self.apply('Legacy')
        self.assertEqual(preview.itemcget(line, 'fill'), 'black')

    def test_plot_heading_labels_follow_theme_without_darkening_figures(self):
        from SignalIntegrity.App.SimulatorDialog import SimulatorDialog
        from SignalIntegrity.App.StatisticalNoiseDialog import StatisticalNoiseDialog
        import SignalIntegrity.App
        self.preferences['Appearance.Color.Foreground'] = '#123456'
        self.preferences['Appearance.Themes.Dark.Foreground'] = '#aabbcc'
        self.apply('Dark')
        app = tk.Frame(self.root)
        app.root = self.root
        app.onCalculate = Mock()
        parent = tk.Frame(app)
        parent.parent = app
        dialogs = []
        with patch.object(SignalIntegrity.App, 'Preferences', self.preferences):
            try:
                for dialogClass, title in ((SimulatorDialog, 'Time-domain View'),
                                           (StatisticalNoiseDialog, 'Spectral Density')):
                    dialog = dialogClass(parent)
                    dialogs.append(dialog)
                    dialog.plotLabel.configure(text=title)
                    self.assertEqual(dialog.plotLabel.winfo_rgb(dialog.plotLabel.cget('foreground')),
                                     self.root.winfo_rgb('#aabbcc'))
                self.root.update_idletasks()
                for name in ('Light', 'Legacy', 'Dark'):
                    self.apply(name)
                    for dialog in dialogs:
                        self.assertEqual(dialog.plotLabel.winfo_rgb(dialog.plotLabel.cget('foreground')),
                                         self.root.winfo_rgb(self.root.appearanceTheme.palette['foreground']))
                        if name != 'Legacy':
                            self.assertEqual(dialog.f.get_facecolor(), (1.0, 1.0, 1.0, 1.0))
            finally:
                for dialog in dialogs:
                    dialog.destroy()

    def test_selector_persists_theme_without_changing_custom_colors(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'preferences.xml')
            self.preferences['Appearance.Color.Foreground'] = '#123456'
            selector = ThemeSelector(self.root, self.preferences, lambda: self.preferences.Write(path))
            selector.string.set('Dark')
            selector.entry.event_generate('<<ComboboxSelected>>')
            restored = PreferencesFile().Read(path)
            self.assertEqual(restored['Appearance.Theme'], 'Dark')
            self.assertEqual(restored['Appearance.Color.Foreground'], '#123456')
            oldPath = os.path.join(directory, 'old.xml')
            with open(oldPath, 'w') as stream:
                stream.write('<Preferences>\n<Appearance><FontSize>9</FontSize></Appearance>\n</Preferences>\n')
            self.assertEqual(PreferencesFile().Read(oldPath)['Appearance.Theme'], 'Legacy')

    def test_measurement_group_rows_follow_theme_on_open_and_palette_changes(self):
        from SignalIntegrity.App.EyeDiagramMeasurementsDialog import EyeDiagramMeasurementsDialog
        from SignalIntegrity.App.StatisticalNoiseMeasurementsDialog import StatisticalNoiseMeasurementsDialog
        import SignalIntegrity.App
        for initial in ('Dark', 'Legacy'):
            self.apply(initial)
            dialogs = []
            with patch.object(SignalIntegrity.App, 'Preferences', self.preferences):
                try:
                    eye = EyeDiagramMeasurementsDialog(self.root, 'Test')
                    dialogs.append(eye)
                    noise = StatisticalNoiseMeasurementsDialog(self.root)
                    dialogs.append(noise)
                    for name, variant in ((initial, 'Default'), ('Dark', 'Slate'),
                                          ('Dark', 'Midnight'), ('Light', 'Default'),
                                          ('Light', 'Warm'), ('Light', 'Cool'), ('Legacy', None)):
                        if name != 'Legacy':
                            self.preferences['Appearance.Themes.' + name + '.Palette'] = variant
                        if (name, variant) != (initial, 'Default'):
                            self.apply(name)
                        for tab, tree in ((eye.tab1, eye._tree1), (eye.tab2, eye._tree2),
                                          (eye.tab3, eye._tree3), (None, noise.measurementTree)):
                            if tab is not None:
                                eye.tabControl.select(tab)
                            self.root.update_idletasks()
                            with self.subTest(initial=initial, theme=name, palette=variant, tree=str(tree)):
                                background = str(tree.tag_configure('group', 'background'))
                                foreground = str(tree.tag_configure('group', 'foreground'))
                                if name == 'Legacy':
                                    self.assertEqual(background, '#e8e8e8')
                                    self.assertEqual(foreground, '')
                                else:
                                    palette = self.root.appearanceTheme.palette
                                    self.assertEqual(background, palette['readonlybackground'])
                                    self.assertEqual(foreground, palette['foreground'])
                                    self.assertGreaterEqual(
                                        ContrastRatio(self.root, foreground, background), 4.5)
                finally:
                    for dialog in dialogs:
                        dialog.destroy()

    def test_preference_selector_rows_follow_legacy_colors_and_theme_switches(self):
        from SignalIntegrity.App.Theme import DialogStyleSelector
        self.preferences['Appearance.Color.Background'] = '#eeddcc'
        self.preferences['Appearance.Color.Foreground'] = '#123456'
        self.apply('Legacy')
        parent = tk.Frame(self.root)
        selectors = (ThemeSelector(parent, self.preferences, lambda: None),
                     DialogStyleSelector(parent, self.preferences, lambda: None))

        def color(widget, option):
            value = widget.cget(option) if option in widget.keys() else ''
            if not value:
                value = ttk.Style(widget).lookup(widget.cget('style') or widget.winfo_class(), option)
            return widget.winfo_rgb(value)

        for name in ('Legacy', 'Dark', 'Light', 'Legacy'):
            self.apply(name)
            for selector in selectors:
                for widget in self.root.appearanceTheme.Widgets(selector):
                    if isinstance(widget, (tk.Frame, ttk.Frame, tk.Label, ttk.Label)):
                        self.assertEqual(color(widget, 'background'), color(parent, 'background'))
                    if isinstance(widget, (tk.Label, ttk.Label)):
                        self.assertEqual(color(widget, 'foreground'),
                                         self.root.winfo_rgb(self.root.appearanceTheme.palette['foreground']))

    def test_invalid_theme_and_color_are_reported_before_palette_changes(self):
        self.apply('Light')
        baseline = self.root.cget('background')
        with self.assertRaises(ValueError):
            self.apply('unknown')
        self.preferences['Appearance.Color.Background'] = 'not-a-color'
        with self.assertRaises(tk.TclError):
            self.apply('Legacy')
        self.assertEqual(self.root.cget('background'), baseline)

    def test_curated_palettes_have_readable_text_and_inputs(self):
        entry = tk.Entry(self.root)
        for name, variants in PALETTE_VARIANTS.items():
            for variant in variants:
                self.preferences['Appearance.Themes.' + name + '.Palette'] = variant
                self.apply(name)
                self.assertGreaterEqual(ContrastRatio(self.root, self.root.appearanceTheme.palette['foreground'],
                                                      self.root.cget('background')), 4.5)
                self.assertGreaterEqual(ContrastRatio(entry, entry.cget('foreground'),
                                                      entry.cget('background')), 4.5)

    def test_color_picker_overrides_survive_switching_and_reset_independently(self):
        self.preferences['Appearance.Color.Background'] = '#eeddcc'
        self.apply('Dark')
        selector = ThemeSelector(self.root, self.preferences, lambda: self.apply(self.preferences['Appearance.Theme']))
        background = ThemeColorButton(self.root, 'background color', self.preferences, 'Background',
                                      lambda: self.apply(self.preferences['Appearance.Theme']))
        with patch('SignalIntegrity.App.Theme.colorchooser.askcolor',
                   return_value=((18, 52, 86), '#123456')):
            background.OnChoose()
        self.assertEqual(self.root.cget('background'), '#123456')
        self.apply('Light')
        self.preferences['Appearance.Themes.Light.Foreground'] = '#101010'
        self.apply('Dark')
        self.assertEqual(self.root.cget('background'), '#123456')
        self.assertEqual(self.preferences['Appearance.Color.Background'], '#eeddcc')
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'preferences.xml')
            self.preferences.Write(path)
            self.assertEqual(PreferencesFile().Read(path)['Appearance.Themes.Dark.Background'], '#123456')
        selector.ResetColors()
        self.assertEqual(self.root.cget('background'), PALETTES['Dark']['background'])
        self.assertEqual(self.preferences['Appearance.Themes.Light.Foreground'], '#101010')
        self.preferences['Appearance.Themes.Dark.Background'] = '#000000'
        selector.paletteString.set('Slate')
        selector.paletteEntry.event_generate('<<ComboboxSelected>>')
        self.assertIn(self.preferences['Appearance.Themes.Dark.Background'], (None, 'None'))
        self.assertEqual(self.root.cget('background'), PALETTE_VARIANTS['Dark']['Slate']['background'])
        self.preferences['Appearance.Themes.Dark.Foreground'] = self.root.cget('background')
        self.apply('Dark')
        selector.Refresh()
        self.assertIn('Low text contrast', selector.warning.cget('text'))

    def test_toolbar_artwork_is_transparent_and_renders_at_two_sizes(self):
        for name in ICON_PATHS:
            for size in (20, 40):
                image = RenderToolbarIcon(name, (240, 245, 250), size)
                self.assertEqual(image.size, (size, size))
                self.assertEqual(image.getpixel((0, 0))[3], 0)
                alpha = [image.getpixel((x, y))[3] for y in range(size) for x in range(size)]
                self.assertGreater(max(alpha), 200)
                self.assertTrue(any(0 < value < 255 for value in alpha))

    def test_linux_selection_indicators_keep_size_and_follow_theme_colors(self):
        with patch('sys.platform','linux'):
            radio=SizeSelectionIndicator(tk.Radiobutton(self.root,text='Orientation'))
            checkbox=SizeSelectionIndicator(tk.Checkbutton(self.root))
            for widget in (radio,checkbox):
                size=widget._indicatorImages[0].width()
                for name in ('Dark','Light','Legacy'):
                    self.apply(name)
                    color=tuple(value//256 for value in widget.winfo_rgb(widget.cget('foreground')))
                    image=ImageTk.getimage(widget._indicatorImages[1])
                    self.assertEqual(image.size,(size,size))
                    pixels=[image.getpixel((x,y)) for x in range(size) for y in range(size)]
                    self.assertTrue(any(pixel[3] > 200 and
                                        all(abs(actual-expected) < 16
                                            for actual,expected in zip(pixel[:3],color))
                                        for pixel in pixels))

    def test_linux_picker_row_height_survives_theme_switches(self):
        from SignalIntegrity.App.DevicePicker import DevicePicker
        parent=tk.Frame(self.root)
        parent.displayScale=2.0
        picker=DevicePicker(parent,[])
        for name in ('Dark','Light','Legacy','Dark'):
            self.apply(name)
            self.root.update()
            self.assertEqual(int(picker.treeStyle.lookup('DevicePicker.Treeview','rowheight')),
                             picker.treeFont.metrics('linespace')+4)

    def test_toolbar_icons_follow_custom_foreground_disabled_state_and_scaling(self):
        self.apply('Dark')
        toolbar = ToolBarElement(self.root, iconfile='document-new-3.gif')
        originalImage = str(toolbar.icon)
        self.preferences['Appearance.Themes.Dark.Foreground'] = '#aabbcc'
        self.apply('Dark')
        self.assertNotEqual(str(toolbar.icon), originalImage)
        self.assertEqual(toolbar.iconKey[1], (170, 187, 204))
        toolbar.Activate(False)
        self.assertNotEqual(toolbar.iconKey[1], (170, 187, 204))
        originalScale = self.root.tk.call('tk', 'scaling')
        try:
            self.root.tk.call('tk', 'scaling', 2 * 96 / 72)
            toolbar.UpdateIcon()
            self.assertGreaterEqual(toolbar.icon.width(), 40)
            self.assertEqual(toolbar.icon.width(), toolbar.icon.height())
        finally:
            self.root.tk.call('tk', 'scaling', originalScale)

    def test_action_icons_render_without_legacy_bitmap_files(self):
        import SignalIntegrity.App

        appDir = os.path.dirname(SignalIntegrity.App.__file__)
        filenames = set()
        for sourceName in os.listdir(appDir):
            if not sourceName.endswith('.py'):
                continue
            with open(os.path.join(appDir, sourceName), encoding='utf-8-sig') as source:
                tree = ast.parse(source.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Str):
                    filename = os.path.basename(node.s)
                    name, extension = os.path.splitext(filename)
                    if (extension in ('.gif', '.png') and '*' not in name
                            and filename not in ('AppIcon2.gif', 'gpl.gif')):
                        filenames.add(filename)
        self.assertTrue(filenames)
        with patch('SignalIntegrity.App.MenuSystemHelpers.Image.open',
                   side_effect=AssertionError('Legacy action bitmap was loaded')):
            for theme in ('Legacy', 'Light', 'Dark'):
                self.apply(theme)
                for filename in sorted(filenames):
                    with self.subTest(theme=theme, icon=filename):
                        iconPath = os.path.join(SignalIntegrity.App.IconsDir, filename)
                        self.assertFalse(os.path.exists(iconPath))
                        toolbar = ToolBarElement(self.root, iconfile=iconPath)
                        self.assertEqual(toolbar.iconKey[0], os.path.splitext(filename)[0])
                        self.assertGreater(toolbar.icon.width(), 0)
                        toolbar.Activate(False)
                        toolbar.button.destroy()

    def test_information_and_question_dialog_icons_recolor_and_preserve_choices(self):
        from SignalIntegrity.App.InformationMessage import InformationMessage
        from SignalIntegrity.App.SignalIntegrityApp import SignalIntegrityApp
        self.apply('Dark')
        information = InformationMessage(self.root, 'Information', 'Details')
        try:
            toolbar = information.info.toolbarElement
            self.assertEqual(toolbar.iconKey[0], 'dialog-information-4')
            self.preferences['Appearance.Themes.Dark.Foreground'] = '#aabbcc'
            self.apply('Dark')
            self.assertEqual(toolbar.iconKey[1], (170, 187, 204))
        finally:
            information.destroy()

        def choose(dialog):
            message, buttons = dialog.winfo_children()
            label = next(child for child in message.winfo_children() if isinstance(child, IconLabel))
            self.assertEqual(label.iconRenderer.iconKey[0], 'dialog-question')
            self.assertEqual(label.iconRenderer.iconKey[1], (170, 187, 204))
            for name in ('Light', 'Dark', 'Legacy'):
                self.apply(name)
                expected = tuple(value // 257 for value in label.winfo_rgb(label.cget('foreground')))
                self.assertEqual(label.iconRenderer.iconKey[1], expected)
            button = next(child for child in buttons.winfo_children()
                          if child.cget('text').startswith('Keep Arguments'))
            button.invoke()

        with patch.object(tk.Toplevel, 'wait_window', autospec=True, side_effect=choose):
            self.assertEqual(SignalIntegrityApp.MakeWritableChoice(SimpleNamespace(root=self.root)), 'keep')

    def test_tooltip_text_remains_readable_in_named_themes(self):
        entry = tk.Entry(self.root)
        tooltip = ToolTip(entry)
        for name in ('Dark', 'Light'):
            self.apply(name)
            tooltip.showtip('Settings')
            label = tooltip.tipwindow.winfo_children()[0]
            self.assertGreaterEqual(ContrastRatio(label, label.cget('foreground'),
                                                  label.cget('background')), 4.5)
            tooltip.hidetip()

    def test_enabled_and_disabled_toolbar_colors_match_palette_without_changing_commands(self):
        calls = []
        doer = Doer(lambda: calls.append('clicked'))
        toolbar = doer.AddToolBarElement(self.root, iconfile='edit-3.gif')
        for name in ('Light', 'Dark'):
            self.apply(name)
            palette = self.root.appearanceTheme.palette
            for option in ('foreground', 'activeforeground', 'activebackground', 'disabledforeground'):
                self.assertEqual(self.root.winfo_rgb(toolbar.button.cget(option)),
                                 self.root.winfo_rgb(palette[option]))
            doer.Activate(False)
            self.apply(name)
            self.assertEqual(str(toolbar.button.cget('state')), 'disabled')
            self.assertFalse(doer.active)
            self.assertFalse(toolbar.active)
            self.assertEqual(toolbar.iconKey[1],
                             tuple(value // 257 for value in self.root.winfo_rgb(palette['disabledforeground'])))
            count = len(calls)
            toolbar.button.invoke()
            self.assertEqual(len(calls), count)
            doer.Activate(True)
            self.assertEqual(str(toolbar.button.cget('state')), 'normal')
            toolbar.button.invoke()
            self.assertEqual(len(calls), count + 1)

    def test_variables_dialog_icons_recolor_and_preserve_editing_commands(self):
        from SignalIntegrity.App.VariablesDialog import VariablesDialog,VariablePropertyDialog
        from SignalIntegrity.App.ProjectFile import VariableConfiguration
        self.apply('Dark')
        parent = tk.Frame(self.root)
        parent.Drawing = SimpleNamespace(schematic=SimpleNamespace(deviceList=[]), DrawSchematic=Mock())
        parent.statusbar = SimpleNamespace(set=Mock())
        parent.history = SimpleNamespace(Event=Mock())
        variables = []
        for name, value, readonly in (('alpha', '1', False), ('beta', '2', True)):
            variable = VariableConfiguration()
            variable['Name'], variable['Value'], variable['ReadOnly'] = name, value, readonly
            variables.append(variable)
        dialog = VariablesDialog(parent, project=variables, top=parent)

        def buttons(row):
            return [child for child in dialog.variablesFrame.winfo_children()[row].winfo_children()
                    if hasattr(child, 'toolbarElement')]

        try:
            row = buttons(0)
            self.assertEqual([button.toolbarElement.iconKey[0] for button in row],
                             ['edit-3', 'edit-delete-6', 'up', 'down'])
            self.assertEqual(dialog.addButton.toolbarElement.iconKey[0], 'edit-add-2')
            self.assertTrue(dialog.variableFrameList[1].readonly)
            previous = dialog.variablesFrame
            buttons(1)[2].invoke()
            self.assertEqual([variable['Name'] for variable in variables], ['beta', 'alpha'])
            self.assertFalse(previous.winfo_exists())
            self.assertTrue(dialog.variableFrameList[0].readonly)
            buttons(0)[3].invoke()
            self.assertEqual([variable['Value'] for variable in variables], ['1', '2'])
            self.apply('Light')
            expected = tuple(value // 257 for value in self.root.winfo_rgb(PALETTES['Light']['foreground']))
            self.assertTrue(all(button.toolbarElement.iconKey[1] == expected for button in buttons(0)))
            buttons(0)[1].invoke()
            self.assertEqual([variable['Name'] for variable in variables], ['beta'])
            parent.Drawing.DrawSchematic.assert_called_once()
            dialog.addButton.invoke()
            editor = next(child for child in dialog.winfo_children() if isinstance(child, VariablePropertyDialog))
            editor.project['Name'], editor.project['Value'] = 'gamma', '3'
            editor.ok(None)
            self.assertEqual([variable['Name'] for variable in variables], ['beta', 'gamma'])
            buttons(1)[0].invoke()
            editor = next(child for child in dialog.winfo_children() if isinstance(child, VariablePropertyDialog))
            editor.project['Description'] = 'edited'
            editor.ok(None)
            self.assertEqual(variables[1]['Description'], 'edited')
        finally:
            dialog.destroy()

    def test_new_output_variable_entries_are_readable_and_remain_readonly(self):
        from SignalIntegrity.App.VariablesDialog import VariablesDialog
        from SignalIntegrity.App.ProjectFile import VariableConfiguration
        self.apply('Dark')
        self.root.deiconify()
        parent = tk.Frame(self.root)
        parent.pack()
        self.root.update()
        variables = []
        for name, kind, readonly in (('input', 'float', False), ('output', 'float', True),
                                     ('count', 'int', True)):
            variable = VariableConfiguration()
            variable['Name'], variable['Type'], variable['ReadOnly'], variable['Value'] = name, kind, readonly, '42'
            variables.append(variable)
        dialog = VariablesDialog(parent, project=variables, top=parent)
        try:
            for redraw in (False, True):
                if redraw:
                    dialog.DrawVariables()
                self.root.update()
                for field in dialog.variableFrameList[1:]:
                    entry = field.entry
                    self.assertTrue(entry.winfo_ismapped())
                    self.assertEqual(entry.cget('readonlybackground'), PALETTES['Dark']['readonlybackground'])
                    self.assertGreaterEqual(ContrastRatio(entry, entry.cget('foreground'),
                                                         entry.cget('readonlybackground')), 4.5)
                    self.assertEqual(str(entry.cget('state')), 'readonly')
                    value = entry.get()
                    entry.insert(0, 'changed')
                    self.assertEqual(entry.get(), value)
                self.assertEqual(str(dialog.variableFrameList[0].entry.cget('state')), 'normal')
            self.apply('Legacy')
            self.assertEqual(dialog.variableFrameList[1].entry.cget('readonlybackground'), 'light gray')
        finally:
            dialog.destroy()

    def test_dialog_style_selection_persists_and_takes_effect_immediately(self):
        from SignalIntegrity.App.Theme import DialogStyleSelector
        from SignalIntegrity.App.Dialogs import UseThemedDialogs
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'preferences.xml')
            selector = DialogStyleSelector(self.root, self.preferences, lambda: self.preferences.Write(path))
            for style in ('Themed', 'Native'):
                selector.string.set(style)
                selector.entry.event_generate('<<ComboboxSelected>>')
                self.assertEqual(PreferencesFile().Read(path)['Appearance.DialogStyle'], style)
                self.assertEqual(UseThemedDialogs(self.root), style == 'Themed')

    def test_native_dialogs_keep_existing_routing_and_cancel_results(self):
        from SignalIntegrity.App import MessageBox,FilePicker
        with patch.object(MessageBox.native, '_show', return_value='cancel') as native:
            self.assertIsNone(MessageBox.askyesnocancel('Save', 'Save first?', parent=self.root))
            native.assert_called_once_with('Save', 'Save first?', 'question', 'yesnocancel', parent=self.root)
        for wrapper, nativeName in ((FilePicker.AskOpenFileName, 'askopenfilename'),
                                    (FilePicker.AskSaveAsFilename, 'asksaveasfilename'),
                                    (FilePicker.AskOpenDirectory, 'askdirectory')):
            with patch.object(FilePicker.filedialog, nativeName, return_value='') as native:
                self.assertIsNone(wrapper(parent=self.root, title='Select'))
                native.assert_called_once_with(parent=self.root, title='Select')

    def test_themed_message_boxes_preserve_answers_and_custom_colors(self):
        from SignalIntegrity.App import MessageBox
        self.preferences['Appearance.DialogStyle'] = 'Themed'
        self.preferences['Appearance.Themes.Dark.Foreground'] = '#aabbcc'
        self.apply('Dark')
        cases = ((MessageBox.showinfo, 'ok', 'ok'), (MessageBox.showwarning, 'ok', 'ok'),
                 (MessageBox.showerror, 'ok', 'ok'), (MessageBox.askquestion, 'no', 'no'),
                 (MessageBox.askyesno, 'yes', True), (MessageBox.askyesno, 'no', False),
                 (MessageBox.askyesnocancel, 'yes', True), (MessageBox.askyesnocancel, 'no', False),
                 (MessageBox.askyesnocancel, 'cancel', None), (MessageBox.askokcancel, 'cancel', False),
                 (MessageBox.askretrycancel, 'retry', True))
        for function, answer, expected in cases:
            def choose(window, parent, focus):
                icon = next(child for child in self.root.appearanceTheme.Widgets(window)
                            if isinstance(child, IconLabel))
                self.assertEqual(icon.iconRenderer.iconKey[1], (170, 187, 204))
                window.buttons[answer].invoke()
            with self.subTest(function=function.__name__, answer=answer):
                with patch('SignalIntegrity.App.Dialogs.RunModal', side_effect=choose):
                    self.assertEqual(function('Title', 'Message', detail='Details', parent=self.root), expected)

    def test_message_modal_restores_parent_grab_after_escape(self):
        from SignalIntegrity.App.Dialogs import MessageDialog,DialogParent
        parent = tk.Toplevel(self.root)
        parent.update()
        parent.grab_set()
        self.assertEqual(DialogParent(), parent)
        dialog = MessageDialog(parent, 'Save', 'Save first?', 'question', 'yesnocancel', default='cancel')
        def visible(event):
            if event.widget == dialog:
                dialog.unbind('<Visibility>')
                dialog.after_idle(lambda: dialog.defaultButton.event_generate('<Escape>'))
        dialog.bind('<Visibility>', visible)
        timeout = self.root.after(1000, lambda: dialog.Choose('timeout'))
        try:
            self.assertEqual(dialog.Show(), 'cancel')
            self.assertEqual(self.root.grab_current(), parent)
            self.assertFalse(dialog.winfo_exists())
        finally:
            self.root.after_cancel(timeout)
            parent.destroy()

    def test_themed_open_dialog_handles_multiple_patterns_filters_and_cancel(self):
        from SignalIntegrity.App import FilePicker,MessageBox
        self.preferences['Appearance.DialogStyle'] = 'Themed'
        self.apply('Dark')
        with tempfile.TemporaryDirectory() as directory:
            for name in ('a.png', 'b.jpg', 'c.txt'):
                with open(os.path.join(directory, name), 'w') as file:
                    file.write('test')
            def select(dialog):
                self.assertEqual(dialog.files.get(0, tk.END), ('a.png', 'b.jpg'))
                self.assertEqual(dialog.get_selection(), os.path.join(directory, ''))
                self.root.appearanceTheme.StyleWidget(dialog.selection)
                self.assertEqual(dialog.selection.cget('background'), PALETTES['Dark']['fieldbackground'])
                self.apply('Legacy')
                self.assertEqual(dialog.selection.cget('background'), self.root.appearanceTheme.legacyEntry['background'])
                self.apply('Dark')
                dialog.types.current(1)
                dialog.SelectType()
                self.assertEqual(dialog.files.get(0, tk.END), ('c.txt',))
                dialog.set_selection('missing.txt')
                with patch.object(MessageBox, 'showerror') as error:
                    dialog.ok_command()
                    error.assert_called_once()
                    self.assertTrue(dialog.top.winfo_exists())
                dialog.set_selection('c')
                dialog.ok_command()
                return dialog.result
            with patch.object(FilePicker.ThemedFileDialog, 'Show', autospec=True, side_effect=select):
                self.assertEqual(FilePicker.AskOpenFileName(parent=self.root, initialdir=directory,
                                 filetypes=[('Images', ('*.png', '*.jpg')), ('Text', '.txt')],
                                 defaultextension='.txt'),
                                 os.path.join(directory, 'c.txt'))
            def cancel(dialog):
                dialog.cancel_command()
                return dialog.result
            with patch.object(FilePicker.ThemedFileDialog, 'Show', autospec=True, side_effect=cancel):
                self.assertIsNone(FilePicker.AskOpenFileName(parent=self.root, initialdir=directory))

    def test_themed_file_dialog_initial_width_and_height(self):
        from SignalIntegrity.App.Dialogs import ThemedFileDialog
        with tempfile.TemporaryDirectory() as directory:
            for mode, limited in (('open', False), ('save', False), ('directory', False),
                                  ('open', True), ('save', True)):
                with self.subTest(mode=mode, limited=limited):
                    dialog = ThemedFileDialog(mode, parent=self.root, initialdir=directory)
                    dialog.top.update_idletasks()
                    width, height = dialog.top.winfo_reqwidth(), dialog.top.winfo_reqheight()
                    screenWidth = width * 2 if limited else dialog.top.winfo_screenwidth()
                    expectedWidth = min(width * 3, screenWidth - 40) if mode != 'directory' else width
                    dimensions = []
                    def visible(event):
                        if event.widget == dialog.top:
                            dialog.top.unbind('<Visibility>')
                            def inspect():
                                dimensions.append((dialog.top.winfo_width(), dialog.top.winfo_height()))
                                dialog.cancel_command()
                            dialog.top.after_idle(inspect)
                    dialog.top.bind('<Visibility>', visible)
                    timeout = self.root.after(3000, dialog.cancel_command)
                    try:
                        with patch.object(dialog.top, 'winfo_screenwidth', return_value=screenWidth):
                            self.assertIsNone(dialog.Show())
                        self.assertEqual(dimensions, [(expectedWidth, height)])
                    finally:
                        self.root.after_cancel(timeout)
                        if dialog.top.winfo_exists():
                            dialog.top.destroy()

    def test_themed_save_appends_extension_and_requires_overwrite_confirmation(self):
        from SignalIntegrity.App import FilePicker,MessageBox
        self.preferences['Appearance.DialogStyle'] = 'Themed'
        self.apply('Light')
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'existing.txt')
            with open(path, 'w') as file:
                file.write('unchanged')
            def save(dialog):
                for name in (('CON', 'bad?.txt') if os.name == 'nt' else ()):
                    dialog.set_selection(name)
                    with patch.object(MessageBox, 'showerror') as error:
                        dialog.ok_command()
                        error.assert_called_once()
                        self.assertIsNone(dialog.result)
                dialog.selection.delete(0, tk.END)
                dialog.selection.insert(0, 'existing')
                with patch.object(MessageBox, 'askyesno', return_value=False) as confirm:
                    dialog.ok_command()
                    self.assertTrue(dialog.top.winfo_exists())
                    self.assertIsNone(dialog.result)
                    self.assertEqual(confirm.call_args[1]['default'], 'no')
                with patch.object(MessageBox, 'askyesno', return_value=True):
                    dialog.ok_command()
                return dialog.result
            with patch.object(FilePicker.ThemedFileDialog, 'Show', autospec=True, side_effect=save):
                self.assertEqual(FilePicker.AskSaveAsFilename(parent=self.root, initialdir=directory,
                                                             defaultextension='.txt'), path)
            with open(path) as file:
                self.assertEqual(file.read(), 'unchanged')

    def test_themed_directory_picker_validates_selection_without_changing_cwd(self):
        from SignalIntegrity.App import FilePicker,MessageBox
        self.preferences['Appearance.DialogStyle'] = 'Themed'
        self.apply('Dark')
        cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as directory:
            subdirectory = os.path.join(directory, 'folder with spaces')
            os.mkdir(subdirectory)
            def select(dialog):
                dialog.set_selection('missing')
                with patch.object(MessageBox, 'showerror') as error:
                    dialog.ok_command()
                    error.assert_called_once()
                dialog.dirs.activate(dialog.dirs.get(0, tk.END).index('folder with spaces'))
                dialog.dirs_select_event(None)
                dialog.dirs_double_event(None)
                dialog.ok_command()
                return dialog.result
            with patch.object(FilePicker.ThemedFileDialog, 'Show', autospec=True, side_effect=select):
                self.assertEqual(FilePicker.AskOpenDirectory(parent=self.root, initialdir=directory,
                                                             mustexist=True), subdirectory)
            self.assertEqual(os.getcwd(), cwd)


if __name__ == '__main__':
    unittest.main()
