"""
EyeDiagramMeasurementsDialog.py
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
import tkinter.font as tkfont
import math

from SignalIntegrity.App.MenuSystemHelpers import StatusBar
import SignalIntegrity.App.Project
import SignalIntegrity.App.Preferences
from SignalIntegrity.Lib.ToSI import ToSI


class EyeDiagramMeasurementsDialog(tk.Toplevel):
    def __init__(self, parent, name):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.displayScale = getattr(parent, 'displayScale', 1.0)
        self.withdraw()
        self.name = name
        self.title('Eye Diagram: ' + name)
        self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir + 'AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        self.protocol("WM_DELETE_WINDOW", self.onClosing)

        self.statusbar = StatusBar(self, displayScale=self.displayScale)
        self.statusbar.pack(side=tk.TOP, fill=tk.X, expand=tk.NO)

        self.tabControl = ttk.Notebook(self, style='EyeDiagram.TNotebook')
        self.tabControl.pack(expand=1, fill=tk.BOTH)

        self._treeStyle = ttk.Style(self)
        self._headerFont = tkfont.nametofont('TkHeadingFont').copy()
        self._headerFont.configure(weight='bold')
        self._treeStyle.configure('EyeDiagram.Treeview.Heading', font=self._headerFont)
        self._cellFont = tkfont.nametofont('TkDefaultFont').copy()
        if self.displayScale > 1.0:
            self._treeStyle.configure(
                'EyeDiagram.Treeview',
                font=self._cellFont,
                rowheight=self._cellFont.metrics('linespace') + self._scaled(6))
        self._groupFont = self._cellFont.copy()
        self._groupFont.configure(weight='bold')

        self.tab1 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1, text='Vertical/Horizontal')
        self.tab2 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab2, text='Error Rates')
        self.tab3 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab3, text='Optical')

        self._tree1 = self._makeTree(self.tab1)
        self._tree2 = self._makeTree(self.tab2)
        self._tree3 = self._makeTree(self.tab3)

        self._hasAutoSized = False
        self.bind('<FocusIn>', self.onFocus)
        self.resizable(True, True)
        self.deiconify()
        self.lift()

    # ── widget helpers ────────────────────────────────────────────────────────

    def _scaled(self, value):
        return round(value * self.displayScale)

    def _makeTree(self, parent):
        """Create a Treeview with horizontal + vertical scrollbars inside *parent*."""
        xScroll = ttk.Scrollbar(parent, orient=tk.HORIZONTAL)
        xScroll.pack(side=tk.BOTTOM, fill=tk.X)
        frame = tk.Frame(parent, relief=tk.RIDGE, borderwidth=self._scaled(5))
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        tree = ttk.Treeview(frame, show='headings', style='EyeDiagram.Treeview')
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        yScroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        yScroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=yScroll.set, xscrollcommand=xScroll.set)
        xScroll.configure(command=tree.xview)
        tree.tag_configure('group', background='#e8e8e8', font=self._groupFont)
        return tree

    def _clearTree(self, tree):
        tree['columns'] = ()
        for item in tree.get_children():
            tree.delete(item)

    def _fmt(self, value, unit):
        if value is None:
            return '-'
        try:
            return ToSI(value, unit)
        except Exception:
            return str(value)

    def _autoSizeColumns(self, tree, all_center=False, min_width=80, max_width=700, pad=24):
        for i, col in enumerate(tree['columns']):
            max_px = self._headerFont.measure(str(col))
            for item in tree.get_children(''):
                vals = tree.item(item, 'values')
                if i < len(vals):
                    max_px = max(max_px, self._cellFont.measure(str(vals[i])))
            width = max(self._scaled(min_width),
                        min(self._scaled(max_width), max_px + self._scaled(pad)))
            anchor = 'center' if (all_center or i > 0) else 'w'
            tree.column(col, width=width, anchor=anchor, stretch=tk.NO)

    def _autoSizeWindow(self):
        self.update_idletasks()
        active = [t for t in (self._tree1, self._tree2, self._tree3) if t['columns']]
        if not active:
            return
        max_w = max(
            sum(int(t.column(c, 'width')) for c in t['columns']) + self._scaled(35)
            for t in active
        )
        try:
            row_height = int(self._treeStyle.lookup('EyeDiagram.Treeview', 'rowheight'))
        except (TypeError, ValueError):
            row_height = 0
        if row_height <= 0:
            row_height = self._cellFont.metrics('linespace') + self._scaled(6)
        heading_height = self._headerFont.metrics('linespace') + self._scaled(10)
        max_rows = max(len(t.get_children('')) for t in active)
        table_h  = heading_height + max_rows * row_height + self._scaled(10)
        window_w = max(self._scaled(400), max_w)
        window_h = max(self._scaled(300),
                       min(self._scaled(1000), table_h + self.statusbar.winfo_reqheight() + self._scaled(70)))
        self.geometry(f'{window_w}x{window_h}')

    # ── standard dialog overrides ─────────────────────────────────────────────

    def onFocus(self, event):
        if event.widget == self:
            if self.parent.winfo_exists():
                self.parent.lift()
                self.lift()

    def onClosing(self):
        self.withdraw()
        self.destroy()

    def destroy(self):
        tk.Toplevel.withdraw(self)
        tk.Toplevel.destroy(self)

    # ── main update ───────────────────────────────────────────────────────────

    def UpdateMeasurements(self, meas):
        self.withdraw()
        if meas is None:
            self.deiconify()
            return

        self._clearTree(self._tree1)
        self._clearTree(self._tree2)
        self._clearTree(self._tree3)

        verticalUnit = {'V': 'V', 'A': 'A', 'W': 'W', 'FW': '', 'AW': 'A', 'VW': 'V'}[meas['WaveformType']]
        noiseUnit    = {'V': 'Vrms', 'A': 'Arms', 'W': 'Wrms', '': '', 'AW': 'Arms', 'VW': 'Vrms'}[verticalUnit]

        # ── Tab 1: Vertical / Horizontal ──────────────────────────────────────
        n_eyes   = len(meas.get('Eye',   []))
        n_levels = len(meas.get('Level', []))
        n_vals   = max(n_eyes, n_levels, 1)
        val_ids  = [f'_v{i}' for i in range(n_vals)]

        self._tree1['columns'] = ['Measurement'] + val_ids
        self._tree1.heading('Measurement', text='Measurement')
        self._tree1.column('Measurement', width=self._scaled(200), anchor='w', stretch=tk.NO)
        for vid in val_ids:
            self._tree1.heading(vid, text='')
            self._tree1.column(vid, width=self._scaled(110), anchor='center', stretch=tk.NO)

        def group1(title, subcol_labels):
            row = [title] + subcol_labels + ['' for _ in range(n_vals - len(subcol_labels))]
            self._tree1.insert('', tk.END, values=row, tags=('group',))

        def eye_row(label, param, subparam, unit):
            vals = [self._fmt(meas['Eye'][e][param][subparam], unit) for e in range(n_eyes)]
            self._tree1.insert('', tk.END, values=[label] + vals + ['' for _ in range(n_vals - n_eyes)])

        def level_row(label, param, subparam, unit):
            vals = [self._fmt(meas['Level'][e][param][subparam], unit) for e in range(n_levels)]
            self._tree1.insert('', tk.END, values=[label] + vals + ['' for _ in range(n_vals - n_levels)])

        def scalar_row1(label, val_str):
            self._tree1.insert('', tk.END, values=[label, val_str] + ['' for _ in range(n_vals - 1)])

        group1('Timing', [f'Eye {i}' for i in range(n_eyes)])
        eye_row('Start', 'Start', 'Time', 's')
        eye_row('End',   'End',   'Time', 's')
        eye_row('Width', 'Width', 'Time', 's')

        group1('Vertical', [f'Eye {i}' for i in range(n_eyes)])
        eye_row('Low',                 'Low',    'Value', verticalUnit)
        eye_row('Midpoint',            'Mid',    'Value', verticalUnit)
        eye_row('Best Decision Level', 'Best',   'Value', verticalUnit)
        eye_row('High',                'High',   'Value', verticalUnit)
        eye_row('Height',              'Height', 'Value', verticalUnit)
        eye_row('AV',                  'AV',     'Value', verticalUnit)

        group1('Extents', [f'Level {i}' for i in range(n_levels)])
        level_row('Min',   'Min',   'Value', verticalUnit)
        level_row('Max',   'Max',   'Value', verticalUnit)
        level_row('Delta', 'Delta', 'Value', verticalUnit)
        level_row('Mean',  'Mean',  'Value', verticalUnit)

        group1('Signal & Noise', [])
        if n_eyes > 1:
            lin = meas.get('Linearity')
            if lin is not None:
                scalar_row1('Eye Linearity', self._fmt(lin * 100., '%'))
            try:
                scalar_row1('RLM', self._fmt(meas['RLM'] * 100., '%'))
            except Exception:
                pass
        scalar_row1('Signal Power',   self._fmt(meas.get('RMS'),           noiseUnit))
        scalar_row1('Noise',          self._fmt(meas.get('Noise'),         noiseUnit))
        scalar_row1('Residual Error', self._fmt(meas.get('NoiseResidual'), noiseUnit))
        scalar_row1('SDR',            self._fmt(meas.get('SDR'),           'dB'))
        if meas.get('SNR') is not None:
            scalar_row1('SNR',  self._fmt(meas['SNR'],        'dB'))
            scalar_row1('SNDR', self._fmt(meas.get('SNDR'),   'dB'))

        group1('Resolution', [])
        scalar_row1('Vertical Resolution',   self._fmt(meas.get('VerticalResolution'),   verticalUnit))
        scalar_row1('Horizontal Resolution', self._fmt(meas.get('HorizontalResolution'), 's'))

        self._autoSizeColumns(self._tree1)

        # ── Tab 2: Error Rates ────────────────────────────────────────────────
        if 'Probabilities' in meas:
            SymbolCode      = meas['Probabilities']['SymbolCodes']
            GrayCode        = meas['Probabilities']['GrayCodes']
            numberOfSymbols = len(SymbolCode)
            symbolDigits    = math.floor(math.log2(numberOfSymbols) + 0.5)
            sym_str         = lambda s: bin(s)[2:].rjust(symbolDigits, '0')
            has_gray        = numberOfSymbols > 2

            # columns needed: max of (interp matrix columns, error-rate table columns)
            n_interp   = 1 + (1 if has_gray else 0) + numberOfSymbols
            n_er       = 1 + (1 if has_gray else 0) + 1 + (1 if has_gray else 0) + 1 + (1 if has_gray else 0)
            total_cols = max(n_interp, n_er)
            col_ids    = [f'_c{i}' for i in range(total_cols)]

            self._tree2['columns'] = col_ids
            for cid in col_ids:
                self._tree2.heading(cid, text='')
                self._tree2.column(cid, width=self._scaled(80), anchor='center', stretch=tk.NO)

            def insert2(values, is_group=False):
                padded = list(values) + ['' for _ in range(total_cols - len(values))]
                if is_group:
                    self._tree2.insert('', tk.END, values=padded, tags=('group',))
                else:
                    self._tree2.insert('', tk.END, values=padded)

            SER_ps     = meas['Probabilities']['ErrorRate']['Symbol']['PerSymbol']
            BER_ps     = meas['Probabilities']['ErrorRate']['Bit']['Standard']['PerSymbol']
            GrayBER_ps = meas['Probabilities']['ErrorRate']['Bit']['Gray']['PerSymbol']

            er_hdr = ['Symbol']
            if has_gray: er_hdr.append('Gray Code')
            er_hdr.append('Probability')
            if has_gray: er_hdr.append('SER')
            er_hdr.append('BER')
            if has_gray: er_hdr.append('Gray BER')

            # Interpretation matrix
            insert2(['Symbol Interpretation Matrix'], is_group=True)
            hdr = ['Symbol']
            if has_gray: hdr.append('Gray Code')
            hdr += [f'\u2192{sym_str(s)}' for s in SymbolCode]
            insert2(hdr, is_group=True)
            Prob_interp = meas['Probabilities']['Interpretation']
            for s in range(numberOfSymbols):
                row = [sym_str(SymbolCode[s])]
                if has_gray: row.append(sym_str(GrayCode[s]))
                row += ['{:.3E}'.format(Prob_interp[s][o]) for o in range(numberOfSymbols)]
                insert2(row)

            # Nominal error rates
            insert2(['Nominal Error Rates'], is_group=True)
            insert2(er_hdr, is_group=True)
            nom_prob = 1. / numberOfSymbols
            for s in range(numberOfSymbols):
                row = [sym_str(SymbolCode[s])]
                if has_gray: row.append(sym_str(GrayCode[s]))
                row.append('{:.3E}'.format(nom_prob))
                if has_gray: row.append('{:.3E}'.format(SER_ps[s]))
                row.append('{:.3E}'.format(BER_ps[s]))
                if has_gray: row.append('{:.3E}'.format(GrayBER_ps[s]))
                insert2(row)
            totals = ['Totals']
            if has_gray: totals.append('')
            totals.append('{:.3E}'.format(1.))
            if has_gray: totals.append('{:.3E}'.format(meas['Probabilities']['ErrorRate']['Symbol']['Nominal']))
            totals.append('{:.3E}'.format(meas['Probabilities']['ErrorRate']['Bit']['Standard']['Nominal']))
            if has_gray: totals.append('{:.3E}'.format(meas['Probabilities']['ErrorRate']['Bit']['Gray']['Nominal']))
            insert2(totals)

            # Measured error rates
            insert2(['Measured Error Rates'], is_group=True)
            insert2(er_hdr, is_group=True)
            meas_prob_sym = meas['Probabilities']['Symbol']
            for s in range(numberOfSymbols):
                row = [sym_str(SymbolCode[s])]
                if has_gray: row.append(sym_str(GrayCode[s]))
                row.append('{:.3E}'.format(meas_prob_sym[s]))
                if has_gray: row.append('{:.3E}'.format(SER_ps[s]))
                row.append('{:.3E}'.format(BER_ps[s]))
                if has_gray: row.append('{:.3E}'.format(GrayBER_ps[s]))
                insert2(row)
            totals = ['Totals']
            if has_gray: totals.append('')
            totals.append('{:.3E}'.format(sum(meas_prob_sym)))
            if has_gray: totals.append('{:.3E}'.format(meas['Probabilities']['ErrorRate']['Symbol']['Measured']))
            totals.append('{:.3E}'.format(meas['Probabilities']['ErrorRate']['Bit']['Standard']['Measured']))
            if has_gray: totals.append('{:.3E}'.format(meas['Probabilities']['ErrorRate']['Bit']['Gray']['Measured']))
            insert2(totals)

            self._autoSizeColumns(self._tree2, all_center=True)
            self.tabControl.tab(1, state='normal')
        else:
            self.tabControl.tab(1, state='disabled')

        # ── Tab 3: Optical ────────────────────────────────────────────────────
        if 'Optical' in meas:
            self._tree3['columns'] = ['Measurement', 'Linear', 'dB']
            self._tree3.heading('Measurement', text='Measurement')
            self._tree3.column('Measurement', width=self._scaled(260), anchor='w', stretch=tk.NO)
            self._tree3.heading('Linear', text='Linear')
            self._tree3.column('Linear', width=self._scaled(120), anchor='center', stretch=tk.NO)
            self._tree3.heading('dB', text='dB')
            self._tree3.column('dB', width=self._scaled(120), anchor='center', stretch=tk.NO)

            optical  = meas['Optical']
            wt_label = {'W': 'W', 'FW': 'Fractional Power',
                        'AW': 'Current Proportional to Power',
                        'VW': 'Voltage Proportional to Power'}[meas['WaveformType']]

            def opt_group(title):
                self._tree3.insert('', tk.END, values=[title, '', ''], tags=('group',))

            def ToSINone(d, sa):
                return None if d is None else ToSI(d, sa, round=3)

            def opt_row(label, lin_val, lin_unit, log_val, log_unit):
                lin = ToSINone(lin_val, lin_unit) or '-'
                log = ToSINone(log_val, log_unit) or '-'
                self._tree3.insert('', tk.END, values=[label, lin, log])

            opt_group(f'Optical Power: {wt_label}')
            if 'Pin' in optical:
                opt_row('Input Power (Pin)',
                        optical['Pin']['Linear']['Value'], optical['Pin']['Linear']['Unit'],
                        optical['Pin']['Log']['Value'],    optical['Pin']['Log']['Unit'])
            opt_row('High Level (PH)',
                    optical['PH']['Linear']['Value'], optical['PH']['Linear']['Unit'],
                    optical['PH']['Log']['Value'],    optical['PH']['Log']['Unit'])
            opt_row('Low Level (PL)',
                    optical['PL']['Linear']['Value'], optical['PL']['Linear']['Unit'],
                    optical['PL']['Log']['Value'],    optical['PL']['Log']['Unit'])
            opt_row('Average Power (Pavg)',
                    optical['Pavg']['Linear']['Value'], optical['Pavg']['Linear']['Unit'],
                    optical['Pavg']['Log']['Value'],    optical['Pavg']['Log']['Unit'])
            opt_row('Modulation Amplitude (OMA)',
                    optical['OMA']['Linear']['Value'], optical['OMA']['Linear']['Unit'],
                    optical['OMA']['Log']['Value'],    optical['OMA']['Log']['Unit'])
            opt_row('Extinction Ratio (ER)',
                    optical['ER']['Linear']['Value'], optical['ER']['Linear']['Unit'],
                    optical['ER']['Log']['Value'],    optical['ER']['Log']['Unit'])
            if 'IL' in optical:
                opt_row('Insertion Loss (IL)',
                        optical['IL']['Linear']['Value'], optical['IL']['Linear']['Unit'],
                        optical['IL']['Log']['Value'],    optical['IL']['Log']['Unit'])
            if 'Loss' in optical:
                opt_row('Loss (Pin \u2212 Pavg)',
                        optical['Loss']['Linear']['Value'], optical['Loss']['Linear']['Unit'],
                        optical['Loss']['Log']['Value'],    optical['Loss']['Log']['Unit'])
            if 'TP' in optical:
                opt_row('Transmission Penalty (TP)',
                        optical['TP']['Linear']['Value'], optical['TP']['Linear']['Unit'],
                        optical['TP']['Log']['Value'],    optical['TP']['Log']['Unit'])
            if 'Q' in optical:
                opt_group('Q Measurements')
                self._tree3.insert('', tk.END,
                    values=['BER', '{:.3E}'.format(optical['Q']['BERMeasured']), ''])
                self._tree3.insert('', tk.END,
                    values=['Q Factor',
                            ToSINone(optical['Q']['QFactor'],   '') or '-',
                            ToSINone(optical['Q']['QFactordB'], 'dB') or '-'])
                if 'QFactorExpected' in optical['Q']:
                    self._tree3.insert('', tk.END,
                        values=['BER Expected', '{:.3E}'.format(optical['Q']['BERExpected']), ''])
                    self._tree3.insert('', tk.END,
                        values=['Q Factor Expected',
                                ToSINone(optical['Q']['QFactorExpected'],   '') or '-',
                                ToSINone(optical['Q']['QFactorExpecteddB'], 'dB') or '-'])
                    self._tree3.insert('', tk.END,
                        values=['Tx Penalty', '',
                                ToSINone(optical['Q']['TxPenalty'], 'dB') or '-'])

            self._autoSizeColumns(self._tree3)
            self.tabControl.tab(2, state='normal')
        else:
            self.tabControl.tab(2, state='disabled')

        # ── status bar & window sizing ────────────────────────────────────────
        self.statusbar.set(f"All Measurements Taken at: {10.0 ** meas['BERForMeasure']:.3E}")

        if not self._hasAutoSized:
            self._autoSizeWindow()
            self._hasAutoSized = True

        self.deiconify()
        self.lift()
