"""
StatisticalNoiseMeasurementsDialog.py
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
from tkinter import ttk
from tkinter import messagebox
import tkinter.font as tkfont
import re
import csv

from SignalIntegrity.App.MenuSystemHelpers import Doer,StatusBar
from SignalIntegrity.App.FilePicker import AskSaveAsFilename
from SignalIntegrity.App.StatisticalNoisePreferencesDialog import StatisticalNoisePreferencesDialog
from SignalIntegrity.Lib.ToSI import ToSI
import SignalIntegrity.App.Project


class StatisticalNoiseMeasurementsDialog(tk.Toplevel):
    """Dialog that displays statistical noise measurements in a column-oriented table."""

    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.displayScale = getattr(parent, 'displayScale', 1.0)
        self.withdraw()
        self.title('Statistical Noise Measurements')
        self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir + 'AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        self.protocol('WM_DELETE_WINDOW', self.onClosing)

        # the Doers - the holder of the commands, menu elements, and key bindings
        # ------
        self.SaveCsvDoer = Doer(self.onSaveCsv).AddHelpElement('Control-Help:Statistical-Noise-Save-CSV').AddToolTip('Save the measurements to a csv file')
        # ------
        self.HelpDoer = Doer(self.onHelp).AddHelpElement('Control-Help:Statistical-Noise-Open-Help-File').AddToolTip('Open the help system in a browser')
        self.PreferencesDoer = Doer(self.onPreferences).AddHelpElement('Control-Help:Statistical-Noise-Preferences').AddToolTip('Edit statistical noise preferences')
        self.ControlHelpDoer = Doer(self.onControlHelp).AddHelpElement('Control-Help:Statistical-Noise-Control-Help').AddToolTip('Get help on a control')
        # ------
        self.EscapeDoer = Doer(self.onEscape).AddKeyBindElement(self,'<Escape>').DisableHelp()

        # The menu system
        TheMenu = tk.Menu(self)
        self.TheMenu = TheMenu
        self.config(menu=TheMenu)
        # ------
        FileMenu = tk.Menu(self)
        TheMenu.add_cascade(label='File', menu=FileMenu, underline=0)
        self.SaveCsvDoer.AddMenuElement(FileMenu, label='Save to CSV', underline=0)
        # ------
        HelpMenu = tk.Menu(self)
        TheMenu.add_cascade(label='Help', menu=HelpMenu, underline=0)
        self.HelpDoer.AddMenuElement(HelpMenu, label='Open Help File', underline=0)
        self.PreferencesDoer.AddMenuElement(HelpMenu, label='Preferences', underline=0)
        self.ControlHelpDoer.AddMenuElement(HelpMenu, label='Control Help', underline=0)

        self.measurements = None

        self.statusbar = StatusBar(self, displayScale=self.displayScale)
        self.statusbar.pack(side=tk.TOP, fill=tk.X, expand=tk.NO)

        self.tableFrame = tk.Frame(self, relief=tk.RIDGE, borderwidth=self._scaled(5))
        self.tableFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        self.treeStyle = ttk.Style(self)
        self.headerFont = tkfont.nametofont('TkHeadingFont').copy()
        self.headerFont.configure(weight='bold')
        self.treeStyle.configure('StatisticalNoise.Treeview.Heading', font=self.headerFont)
        self.cellFont = tkfont.nametofont('TkDefaultFont').copy()
        if self.displayScale > 1.0:
            self.treeStyle.configure(
                'StatisticalNoise.Treeview',
                font=self.cellFont,
                rowheight=self.cellFont.metrics('linespace') + self._scaled(6))

        self.measurementTree = ttk.Treeview(self.tableFrame, show='headings', style='StatisticalNoise.Treeview')
        self.measurementTree.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

        self.yScroll = ttk.Scrollbar(self.tableFrame, orient=tk.VERTICAL, command=self.measurementTree.yview)
        self.yScroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.measurementTree.configure(yscrollcommand=self.yScroll.set)

        self.xScroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.measurementTree.xview)
        self.xScroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.measurementTree.configure(xscrollcommand=self.xScroll.set)

        self.groupFont = tkfont.nametofont('TkDefaultFont').copy()
        self.groupFont.configure(weight='bold')
        self.measurementTree.tag_configure('group', background='#e8e8e8', font=self.groupFont)

        self._hasAutoSized = False
        self.resizable(True, True)
        self.deiconify()
        self.lift()

    def _scaled(self, value):
        return round(value * self.displayScale)

    def onClosing(self):
        self.withdraw()
        self.destroy()

    def destroy(self):
        tk.Toplevel.withdraw(self)
        tk.Toplevel.destroy(self)

    def onHelp(self):
        if Doer.helpKeys is None:
            messagebox.showerror('Help System', 'Cannot find or open this help element')
            return
        Doer.helpKeys.Open('sec:Statistical-Noise-Dialog')

    def onControlHelp(self):
        Doer.inHelp = True
        self.config(cursor='question_arrow')

    def onEscape(self):
        Doer.inHelp = False
        self.config(cursor='left_ptr')

    def onPreferences(self):
        if not hasattr(self, 'preferencesDialog') or self.preferencesDialog is None or not self.preferencesDialog.winfo_exists():
            self.preferencesDialog = StatisticalNoisePreferencesDialog(self, SignalIntegrity.App.Preferences)
        self.preferencesDialog.lift()

    def onSaveCsv(self):
        filename = AskSaveAsFilename(parent=self,
                                     filetypes=[('csv', '.csv')],
                                     defaultextension='.csv',
                                     initialfile='StatisticalNoiseMeasurements.csv')
        if filename is None:
            return
        columns = self.measurementTree['columns']
        if len(columns) == 0:
            messagebox.showerror('Save to CSV', 'There are no measurements to save')
            return
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow([self.measurementTree.heading(column, 'text') for column in columns])
                for item in self.measurementTree.get_children(''):
                    writer.writerow(list(self.measurementTree.item(item, 'values')))
            self.statusbar.set('Saved measurements to ' + filename)
        except Exception as e:
            messagebox.showerror('Save to CSV', 'Could not save file: ' + str(e))

    def UpdateMeasurementsView(self):
        # re-render the table using the last measurements (e.g. after a
        # preference change such as the display zero threshold).
        if self.measurements is not None:
            self.UpdateMeasurements(self.measurements)


    def _clearTable(self):
        self.measurementTree['columns'] = ()
        for item in self.measurementTree.get_children():
            self.measurementTree.delete(item)

    def _formatValue(self, value, units):
        if value is None:
            return '-'
        try:
            return self._normalizedUnitText(ToSI(value, units, round=3))
        except Exception:
            return self._normalizedUnitText(str(value))

    def _normalizedUnitText(self, text):
        if not isinstance(text, str):
            return text
        return re.sub(r'sqrt\(([^)]+)\)', r'√\1', text)

    def _dictValue(self, measurements, output_name, section_name, key_name):
        section = measurements.get(section_name, {})
        output_entry = section.get(output_name, {})
        return output_entry.get(key_name, None)

    def _outputType(self, measurements, output_name):
        entry = measurements.get('output_noise_spectral_density', {}).get(output_name, {})
        return entry.get('type', 'voltage')

    def _rmsUnits(self, measurements, output_name, base):
        # base is a neutral rms unit like 'rms', 'rms/sqrt(Hz)' or
        # 'rms/sqrt(GHz)'; prepend 'A' for a current probe, else 'V'.
        prefix = 'A' if self._outputType(measurements, output_name) == 'current' else 'V'
        return prefix + base

    def _snrDb(self, measurements, output_name):
        return self._dictValue(measurements, output_name, 'signal_to_noise_ratio', 'SNR')

    def _salzSnrDb(self, measurements, output_name):
        return self._dictValue(measurements, output_name, 'signal_to_noise_ratio', 'SalzSNR')

    def _contributionsDict(self, measurements):
        contributions = measurements.get('contributions', None)
        return contributions if isinstance(contributions, dict) else {}

    def _contributorValue(self, measurements, output_name, contributor_name, zeroThreshold=None, maximumSNR=None):
        contributions = self._contributionsDict(measurements)
        output_contrib = contributions.get(output_name, {})
        contributor = output_contrib.get(contributor_name, {})

        rms_value = contributor.get('rms', None)
        dbm_value = contributor.get('dBm', None)
        snr_value = contributor.get('SNR', None)

        # Blank a contributor whose rms magnitude is below the zero threshold.
        if (zeroThreshold is not None and zeroThreshold > 0
                and rms_value is not None and abs(rms_value) < zeroThreshold):
            return ''

        rms = self._formatValue(rms_value, self._rmsUnits(measurements, output_name, 'rms'))
        dbm = self._formatValue(dbm_value, 'dBm')

        # Blank an unphysically high SNR.
        if (maximumSNR is not None and maximumSNR > 0
                and snr_value is not None and snr_value > maximumSNR):
            snr = ''
        else:
            snr = self._formatValue(snr_value, 'dB')

        return f'{rms}, {dbm}, {snr}'

    def _contributorNames(self, measurements):
        contributions = self._contributionsDict(measurements)
        if len(contributions) == 0:
            return []

        input_names = measurements.get('input_names', [])
        if len(input_names) > 0:
            return list(input_names)

        ordered = []
        for output_name in measurements.get('output_names', []):
            for contributor_name, contributor_value in contributions.get(output_name, {}).items():
                if not isinstance(contributor_value, dict):
                    continue
                if contributor_name not in ordered:
                    ordered.append(contributor_name)
        return ordered

    def _insertGroupRow(self, title, column_count):
        values = [title] + ['' for _ in range(column_count - 1)]
        self.measurementTree.insert('', tk.END, values=values, tags=('group',))

    def _insertMeasurementRow(self, label, output_names, extractor, units, blankPredicate=None):
        # units may be a fixed string (e.g. 'dBm') or a callable(output_name)
        # returning the units for that output's column (used for rms quantities
        # whose units depend on whether the probe is a voltage or current probe).
        # blankPredicate is an optional callable(output_name) returning True when
        # the cell should be displayed with no value (e.g. below the zero
        # threshold or above the maximum SNR).
        row = [label]
        for output_name in output_names:
            if blankPredicate is not None and blankPredicate(output_name):
                row.append('')
                continue
            column_units = units(output_name) if callable(units) else units
            row.append(self._formatValue(extractor(output_name), column_units))
        self.measurementTree.insert('', tk.END, values=row)

    def _autoSizeOutputColumns(self, output_names, min_width=170, max_width=700, pad=24):
        for output_index, output_name in enumerate(output_names, start=1):
            max_pixels = self.headerFont.measure(str(output_name))
            for item in self.measurementTree.get_children(''):
                values = self.measurementTree.item(item, 'values')
                if output_index < len(values):
                    max_pixels = max(max_pixels, self.cellFont.measure(str(values[output_index])))
            width = max(self._scaled(min_width),
                        min(self._scaled(max_width), max_pixels + self._scaled(pad)))
            self.measurementTree.column(output_name, width=width, anchor='center', stretch=tk.NO)

    def _autoSizeWindowToTable(self):
        self.update_idletasks()

        columns = self.measurementTree['columns']
        table_width = sum(int(self.measurementTree.column(column_name, 'width')) for column_name in columns)
        table_width += self.yScroll.winfo_reqwidth()
        table_width += int(2 * self.tableFrame.cget('borderwidth'))

        row_count = len(self.measurementTree.get_children(''))
        try:
            row_height = int(self.treeStyle.lookup('StatisticalNoise.Treeview', 'rowheight'))
        except (TypeError, ValueError):
            row_height = 0
        if row_height <= 0:
            row_height = self.cellFont.metrics('linespace') + self._scaled(6)
        heading_height = self.headerFont.metrics('linespace') + self._scaled(10)
        table_height = heading_height + row_count * row_height
        table_height += int(2 * self.tableFrame.cget('borderwidth'))

        window_width = table_width
        window_height = table_height + self.statusbar.winfo_reqheight() + self.xScroll.winfo_reqheight()
        if self.displayScale > 1.0:
            window_height = max(self._scaled(300), min(self._scaled(1000), window_height))

        self.geometry(f'{window_width}x{window_height}')

    def UpdateMeasurements(self, measurements):
        """
        Update table content.

        Expected keys in measurements include:
          - output_names
          - output_noise_spectral_density
          - signal_noise_spectral_density (optional)
        """
        self.withdraw()
        self._clearTable()

        self.measurements = measurements

        if measurements is None:
            self.statusbar.set('No statistical noise measurements available')
            self.deiconify()
            return

        output_names = measurements.get('output_names', [])
        # Restrict the displayed columns to the outputs designated for display
        # (via each probe's 'include in noise' property).  Eye probes with the
        # property turned off remain in the results dictionary (so the eye
        # diagrams keep their external noise) but are excluded from this table.
        displayNames = measurements.get('noise_display_output_names', None)
        if displayNames is not None:
            output_names = [name for name in output_names if name in displayNames]
        if len(output_names) == 0:
            self.statusbar.set('No output probes in statistical noise measurements')
            self.deiconify()
            return

        # Display thresholds from preferences: linear/rms magnitudes below the
        # zero threshold are blanked, and SNRs above the maximum are blanked
        # (an unphysically high SNR indicates essentially zero noise).
        zeroThreshold = SignalIntegrity.App.Preferences['StatisticalNoise.ZeroThreshold']
        maximumSNR = SignalIntegrity.App.Preferences['StatisticalNoise.MaximumSNR']

        def below_threshold(value):
            return (zeroThreshold is not None and zeroThreshold > 0
                    and value is not None and abs(value) < zeroThreshold)

        def noise_blank(out):
            return below_threshold(self._dictValue(measurements, out, 'output_noise_spectral_density', 'rms'))

        def signal_blank(out):
            return below_threshold(self._dictValue(measurements, out, 'signal_noise_spectral_density', 'rms'))

        def snr_blank(out, snr_value):
            if noise_blank(out):
                return True
            return (maximumSNR is not None and maximumSNR > 0
                    and snr_value is not None and snr_value > maximumSNR)

        columns = ['Measurement'] + list(output_names)
        self.measurementTree['columns'] = columns

        self.measurementTree.heading('Measurement', text='Measurement')
        self.measurementTree.column('Measurement', width=self._scaled(260), anchor='w', stretch=tk.NO)

        for output_name in output_names:
            self.measurementTree.heading(output_name, text=output_name)
            self.measurementTree.column(output_name, width=self._scaled(170), anchor='center', stretch=tk.NO)

        column_count = len(columns)

        self._insertGroupRow('Signal Power', column_count)
        self._insertMeasurementRow(
            'Integrated signal power (rms)',
            output_names,
            lambda out: self._dictValue(measurements, out, 'signal_noise_spectral_density', 'rms'),
            lambda out: self._rmsUnits(measurements, out, 'rms'),
            blankPredicate=signal_blank)
        self._insertMeasurementRow(
            'Integrated signal power (dBm)',
            output_names,
            lambda out: self._dictValue(measurements, out, 'signal_noise_spectral_density', 'dBm'),
            'dBm',
            blankPredicate=signal_blank)

        self._insertGroupRow('Noise Power', column_count)
        self._insertMeasurementRow(
            'Total noise (rms)',
            output_names,
            lambda out: self._dictValue(measurements, out, 'output_noise_spectral_density', 'rms'),
            lambda out: self._rmsUnits(measurements, out, 'rms'),
            blankPredicate=noise_blank)
        self._insertMeasurementRow(
            'Total noise (dBm)',
            output_names,
            lambda out: self._dictValue(measurements, out, 'output_noise_spectral_density', 'dBm'),
            'dBm',
            blankPredicate=noise_blank)

        self._insertGroupRow('Signal-to-Noise Ratio', column_count)
        self._insertMeasurementRow(
            'SNR (dB)',
            output_names,
            lambda out: self._snrDb(measurements, out),
            'dB',
            blankPredicate=lambda out: snr_blank(out, self._snrDb(measurements, out)))
        self._insertMeasurementRow(
            'Salz SNR (dB)',
            output_names,
            lambda out: self._salzSnrDb(measurements, out),
            'dB',
            blankPredicate=lambda out: snr_blank(out, self._salzSnrDb(measurements, out)))

        self._insertGroupRow('Average Noise Density (Hz)', column_count)
        self._insertMeasurementRow(
            'Average noise density (rms/√Hz)',
            output_names,
            lambda out: self._dictValue(measurements, out, 'output_noise_spectral_density', 'rms/sqrt(Hz)'),
            lambda out: self._rmsUnits(measurements, out, 'rms/sqrt(Hz)'),
            blankPredicate=noise_blank)
        self._insertMeasurementRow(
            'Average noise density (dBm/Hz)',
            output_names,
            lambda out: self._dictValue(measurements, out, 'output_noise_spectral_density', 'dBm/Hz'),
            'dBm/Hz',
            blankPredicate=noise_blank)

        self._insertGroupRow('Average Noise Density (GHz)', column_count)
        self._insertMeasurementRow(
            'Average noise density (rms/√GHz)',
            output_names,
            lambda out: self._dictValue(measurements, out, 'output_noise_spectral_density', 'rms/sqrt(GHz)'),
            lambda out: self._rmsUnits(measurements, out, 'rms/sqrt(GHz)'),
            blankPredicate=noise_blank)
        self._insertMeasurementRow(
            'Average noise density (dBm/GHz)',
            output_names,
            lambda out: self._dictValue(measurements, out, 'output_noise_spectral_density', 'dBm/GHz'),
            'dBm/GHz',
            blankPredicate=noise_blank)

        contributor_names = self._contributorNames(measurements)
        if len(contributor_names) > 0:
            self._insertGroupRow('Noise Contributors (Vrms, dBm, SNR (dB))', column_count)
            for contributor_name in contributor_names:
                row = [contributor_name]
                for output_name in output_names:
                    row.append(self._contributorValue(measurements, output_name, contributor_name,
                                                       zeroThreshold, maximumSNR))
                self.measurementTree.insert('', tk.END, values=row)

        self._autoSizeOutputColumns(output_names)

        if not self._hasAutoSized:
            self._autoSizeWindowToTable()
            self._hasAutoSized = True

        has_signal = 'signal_noise_spectral_density' in measurements
        signal_note = 'with signal-power metrics' if has_signal else 'signal-power metrics unavailable'
        contributor_note = f', {len(contributor_names)} contributor(s)' if len(contributor_names) > 0 else ''
        self.statusbar.set(f'Showing noise measurements for {len(output_names)} output probe(s), {signal_note}{contributor_note}')

        self.deiconify()
        self.lift()