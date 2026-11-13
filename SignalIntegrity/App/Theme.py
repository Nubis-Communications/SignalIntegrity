"""Shared, opt-in Tk/ttk appearance for the desktop applications."""

# Copyright (c) 2026 Nubis Communications, Inc.
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
from tkinter import colorchooser
from weakref import WeakKeyDictionary
from SignalIntegrity.App.Dialogs import DIALOG_STYLES


THEME_NAMES = ('Legacy', 'Light', 'Dark')

PALETTES = {
    'Light': {
        'background': '#f3f4f6', 'foreground': '#202124',
        'activebackground': '#e2e8f0', 'activeforeground': '#202124',
        'disabledforeground': '#667085', 'selectbackground': '#2563eb',
        'selectforeground': '#ffffff', 'selectcolor': '#ffffff',
        'insertbackground': '#202124', 'troughcolor': '#e2e8f0',
        'fieldbackground': '#ffffff', 'readonlybackground': '#e2e8f0',
        'schematicforeground': '#202124', 'schematicselection': '#1d4ed8',
    },
    'Dark': {
        'background': '#252830', 'foreground': '#f1f3f5',
        'activebackground': '#3b4252', 'activeforeground': '#ffffff',
        'disabledforeground': '#a0a8b8', 'selectbackground': '#2563eb',
        'selectforeground': '#ffffff', 'selectcolor': '#3b4252',
        'insertbackground': '#f1f3f5', 'troughcolor': '#191c22',
        'fieldbackground': '#191c22', 'readonlybackground': '#343a46',
        'schematicforeground': '#f1f3f5', 'schematicselection': '#8ab4ff',
    },
}

PALETTE_VARIANTS = {
    'Light': {
        'Default': {},
        'Warm': {
            'background': '#faf7f0', 'foreground': '#302b25',
            'fieldbackground': '#fffdf9', 'readonlybackground': '#e9e3d8',
            'activebackground': '#e9e3d8', 'activeforeground': '#302b25',
            'insertbackground': '#302b25', 'schematicforeground': '#302b25',
            'troughcolor': '#e9e3d8',
        },
        'Cool': {
            'background': '#edf3fa', 'foreground': '#203047',
            'fieldbackground': '#f8fbff', 'readonlybackground': '#dce6f2',
            'activebackground': '#dce6f2', 'activeforeground': '#203047',
            'insertbackground': '#203047', 'schematicforeground': '#203047',
            'troughcolor': '#dce6f2',
        },
    },
    'Dark': {
        'Default': {},
        'Slate': {
            'background': '#303b4b', 'fieldbackground': '#222c3a',
            'readonlybackground': '#3e4b5d', 'activebackground': '#3e4b5d',
            'troughcolor': '#222c3a', 'selectcolor': '#3e4b5d',
        },
        'Midnight': {
            'background': '#111827', 'fieldbackground': '#0b1220',
            'readonlybackground': '#253248', 'activebackground': '#253248',
            'troughcolor': '#0b1220', 'selectcolor': '#253248',
        },
    },
}


def ThemeColorPath(preferences):
    name = preferences['Appearance.Theme']
    return 'Appearance.Color.' if name == 'Legacy' else 'Appearance.Themes.' + name + '.'


def ContrastRatio(root, foreground, background):
    def luminance(color):
        channels = [value / 65535.0 for value in root.winfo_rgb(color)]
        linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
                  for value in channels]
        return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))
    first, second = sorted((luminance(foreground), luminance(background)))
    return (second + 0.05) / (first + 0.05)


class ThemeManager:
    def __init__(self, root):
        self.root = root
        self.name = 'Legacy'
        self.palette = None
        self.style = ttk.Style(root)
        self.legacyStyle = self.style.theme_use()
        button = tk.Button(root)
        entry = tk.Entry(root)
        scrollbar = tk.Scrollbar(root)
        checkbutton = tk.Checkbutton(root)
        listbox = tk.Listbox(root)
        self.legacyPalette = {
            key: button.cget(key) for key in (
                'background', 'foreground', 'activebackground',
                'activeforeground', 'disabledforeground')
        }
        self.legacyPalette.update({
            key: entry.cget(key) for key in (
                'selectbackground', 'selectforeground', 'insertbackground')
        })
        self.legacyPalette['selectcolor'] = checkbutton.cget('selectcolor')
        self.legacyPalette['troughcolor'] = scrollbar.cget('troughcolor')
        self.legacyEntry = {
            key: entry.cget(key) for key in (
                'background', 'readonlybackground', 'disabledbackground')
        }
        self.legacyListbox = {
            key: listbox.cget(key) for key in (
                'background', 'foreground', 'selectbackground', 'selectforeground')
        }
        button.destroy()
        entry.destroy()
        scrollbar.destroy()
        checkbutton.destroy()
        listbox.destroy()
        self.entryColors = WeakKeyDictionary()
        self.plotDefaults = None
        # Toplevel descendants do not include the root in their bindtags.
        root.bind_all('<Map>', self.OnMap, add='+')

    def Apply(self, preferences):
        if preferences['Appearance.DialogStyle'] not in DIALOG_STYLES:
            raise ValueError('Unknown dialog style: {!r}'.format(preferences['Appearance.DialogStyle']))
        name = preferences['Appearance.Theme']
        if name not in THEME_NAMES:
            raise ValueError('Unknown appearance theme: {!r}'.format(name))
        palette = self.legacyPalette.copy() if name == 'Legacy' else PALETTES[name].copy()
        if name == 'Legacy':
            for key, preference in (
                ('background', 'Background'), ('foreground', 'Foreground'),
                ('activebackground', 'ActiveBackground'), ('activeforeground', 'ActiveForeground'),
                ('disabledforeground', 'DisabledForeground'),
            ):
                color = preferences['Appearance.Color.' + preference]
                if color not in (None, 'None'):
                    palette[key] = color
        else:
            path = ThemeColorPath(preferences)
            variant = preferences[path + 'Palette']
            if variant not in PALETTE_VARIANTS[name]:
                raise ValueError('Unknown {} palette: {!r}'.format(name, variant))
            palette.update(PALETTE_VARIANTS[name][variant])
            background = preferences[path + 'Background']
            foreground = preferences[path + 'Foreground']
            if background not in (None, 'None'):
                palette.update(background=background, fieldbackground=background,
                               readonlybackground=background)
            if foreground not in (None, 'None'):
                palette.update(foreground=foreground, activeforeground=foreground,
                               insertbackground=foreground, schematicforeground=foreground)
        for key, color in palette.items():
            self.root.winfo_rgb(color)
        widgets = list(self.Widgets(self.root))
        for widget in widgets:
            self.RememberEntry(widget)
        self.name = name
        self.preferences = preferences
        self.palette = palette
        self.root.tk_setPalette(**{
            option: palette[key] for key, option in (
                ('background', 'background'), ('foreground', 'foreground'),
                ('activebackground', 'activeBackground'), ('activeforeground', 'activeForeground'),
                ('disabledforeground', 'disabledForeground'),
                ('selectbackground', 'selectBackground'), ('selectforeground', 'selectForeground'),
                ('selectcolor', 'selectColor'), ('insertbackground', 'insertBackground'),
                ('troughcolor', 'troughColor'),
            )
        })
        if name == 'Legacy':
            self.style.theme_use(self.legacyStyle)
            self.StyleComboboxListbox(self.legacyListbox)
        else:
            self.ApplyTtk(palette)
        for widget in widgets:
            self.StyleWidget(widget)
        self.ApplyPlots(preferences)
        self.root.update_idletasks()

    def Widgets(self, parent):
        yield parent
        for child in parent.winfo_children():
            yield from self.Widgets(child)

    def RememberEntry(self, widget):
        if isinstance(widget, tk.Entry) and not isinstance(widget, ttk.Widget) and widget not in self.entryColors:
            colors = {key: widget.cget(key) for key in self.legacyEntry}
            if self.name != 'Legacy':
                for key in colors:
                    role = 'fieldbackground' if key == 'background' else 'readonlybackground'
                    if colors[key] == self.palette[role] or (key == 'background' and colors[key] == self.palette['background']):
                        colors[key] = self.legacyEntry[key]
            self.entryColors[widget] = colors

    def StyleWidget(self, widget):
        if isinstance(widget, ttk.Treeview) and 'group' in widget.tk.splitlist(
                widget.tk.call(widget._w, 'tag', 'names')):
            widget.tag_configure(
                'group',
                background='#e8e8e8' if self.name == 'Legacy' else self.palette['readonlybackground'],
                foreground='' if self.name == 'Legacy' else self.palette['foreground'])
        if isinstance(widget, tk.Entry) and not isinstance(widget, ttk.Widget):
            self.RememberEntry(widget)
            if self.name == 'Legacy':
                widget.configure(**self.entryColors[widget])
            else:
                widget.configure(
                    background=self.palette['fieldbackground'],
                    readonlybackground=self.palette['readonlybackground'],
                    disabledbackground=self.palette['readonlybackground'])
        if hasattr(widget, 'ApplySchematicTheme'):
            widget.ApplySchematicTheme(self.palette if self.name != 'Legacy' else None)
        if hasattr(widget, 'toolbarElement'):
            widget.toolbarElement.UpdateIcon()
        elif hasattr(widget, 'iconRenderer'):
            widget.iconRenderer.UpdateIcon()
        if hasattr(widget, '_indicatorImages'):
            from SignalIntegrity.App.MenuSystemHelpers import SizeSelectionIndicator
            SizeSelectionIndicator(widget)

    def OnMap(self, event):
        if self.palette is not None:
            self.StyleWidget(event.widget)

    def ApplyTtk(self, palette):
        theme = 'SignalIntegrity'
        if theme not in self.style.theme_names():
            self.style.theme_create(theme, parent='clam')
        self.style.theme_settings(theme, {
            '.': {
                'configure': {
                    'background': palette['background'], 'foreground': palette['foreground'],
                    'fieldbackground': palette['fieldbackground'],
                    'troughcolor': palette['troughcolor'],
                    'selectbackground': palette['selectbackground'],
                    'selectforeground': palette['selectforeground'],
                    'insertcolor': palette['insertbackground'],
                    'bordercolor': palette['activebackground'],
                },
                'map': {
                    'foreground': [('disabled', palette['disabledforeground'])],
                    'background': [('active', palette['activebackground'])],
                },
            },
            'TButton': {'configure': {'padding': (6, 4)}},
            'TNotebook.Tab': {
                'configure': {'padding': (12, 4)},
                'map': {'background': [
                    ('selected', palette['fieldbackground']),
                    ('active', palette['activebackground']),
                ]},
            },
            'TCombobox': {
                'map': {
                    'fieldbackground': [
                        ('disabled', palette['readonlybackground']),
                        ('readonly', palette['fieldbackground']),
                    ],
                    'selectbackground': [('readonly', palette['fieldbackground'])],
                    'selectforeground': [('readonly', palette['foreground'])],
                },
            },
            'Treeview': {
                'configure': {'background': palette['fieldbackground']},
                'map': {
                    'background': [('selected', palette['selectbackground'])],
                    'foreground': [('selected', palette['selectforeground'])],
                },
            },
        })
        self.style.theme_use(theme)
        self.StyleComboboxListbox({
            'background': palette['fieldbackground'], 'foreground': palette['foreground'],
            'selectbackground': palette['selectbackground'],
            'selectforeground': palette['selectforeground'],
        })

    def StyleComboboxListbox(self, colors):
        for key, option in (
            ('background', 'background'), ('foreground', 'foreground'),
            ('selectbackground', 'selectBackground'), ('selectforeground', 'selectForeground'),
        ):
            self.root.option_add('*TCombobox*Listbox.' + option, colors[key])
        for widget in self.Widgets(self.root):
            if isinstance(widget, ttk.Combobox):
                popdown = self.root.tk.call('ttk::combobox::PopdownWindow', str(widget))
                options = [part for key, value in colors.items() for part in ('-' + key, value)]
                self.root.tk.call(str(popdown) + '.f.l', 'configure',
                                  *options)

    def ApplyPlots(self, preferences):
        import matplotlib as mpl
        keys = ('figure.facecolor', 'axes.facecolor', 'axes.edgecolor', 'axes.labelcolor',
                'text.color', 'xtick.color', 'ytick.color')
        if self.plotDefaults is None:
            self.plotDefaults = {key: mpl.rcParams[key] for key in keys}
        values = self.plotDefaults.copy()
        if self.name == 'Legacy':
            color = preferences['Appearance.Color.Plot']
            if color not in (None, 'None'):
                values['figure.facecolor'] = color
        else:
            # Keep scientific plots light; palette changes must not alter trace/eye colors.
            values.update({key: '#202124' for key in keys})
            values.update({'figure.facecolor': '#ffffff', 'axes.facecolor': '#ffffff'})
        mpl.rcParams.update(values)


def ApplyTheme(root, preferences):
    if not hasattr(root, 'appearanceTheme'):
        root.appearanceTheme = ThemeManager(root)
    root.appearanceTheme.Apply(preferences)


class ThemedCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        self.themePalette = None
        tk.Canvas.__init__(self, parent, **kwargs)
        theme = getattr(self._root(), 'appearanceTheme', None)
        if theme is not None and theme.name != 'Legacy':
            self.ApplySchematicTheme(theme.palette)

    def _create(self, itemType, args, kwargs):
        kwargs = kwargs.copy()
        tags = list(self.tk.splitlist(kwargs.get('tags', ())))
        for option in ('fill', 'outline'):
            color = kwargs.get(option)
            if color in ('black', 'blue'):
                tags.append('_si_{}_{}'.format(option, color))
                if self.themePalette is not None:
                    role = 'schematicforeground' if color == 'black' else 'schematicselection'
                    kwargs[option] = self.themePalette[role]
        kwargs['tags'] = tags
        return tk.Canvas._create(self, itemType, args, kwargs)

    def ApplySchematicTheme(self, palette):
        self.themePalette = palette
        for option in ('fill', 'outline'):
            for color, role in (('black', 'schematicforeground'), ('blue', 'schematicselection')):
                self.itemconfigure('_si_{}_{}'.format(option, color),
                                   **{option: color if palette is None else palette[role]})


class ThemeSelector(tk.Frame):
    def __init__(self, parent, preferences, callback, labelWidth=45):
        tk.Frame.__init__(self, parent)
        self.preferences = preferences
        self.callback = callback
        self.pack(side=tk.TOP, fill=tk.X)
        themeRow = tk.Frame(self)
        themeRow.pack(fill=tk.X)
        tk.Label(themeRow, text='theme: ', width=labelWidth, anchor='e').pack(side=tk.LEFT)
        self.string = tk.StringVar(self, value=preferences['Appearance.Theme'])
        self.entry = ttk.Combobox(themeRow, textvariable=self.string, values=THEME_NAMES,
                                  state='readonly', width=30)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind('<<ComboboxSelected>>', self.OnSelected)
        paletteRow = tk.Frame(self)
        paletteRow.pack(fill=tk.X)
        tk.Label(paletteRow, text='palette: ', width=labelWidth, anchor='e').pack(side=tk.LEFT)
        self.paletteString = tk.StringVar(self)
        self.paletteEntry = ttk.Combobox(paletteRow, textvariable=self.paletteString, state='readonly')
        self.paletteEntry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.paletteEntry.bind('<<ComboboxSelected>>', self.OnPaletteSelected)
        self.resetButton = ttk.Button(paletteRow, text='Reset colors', command=self.ResetColors)
        self.resetButton.pack(side=tk.LEFT, padx=4)
        self.warning = tk.Label(self, anchor='e')
        self.warning.pack(fill=tk.X)
        self.Refresh()

    def OnSelected(self, event=None):
        self.preferences['Appearance.Theme'] = self.string.get()
        self.Refresh()
        self.callback()

    def OnPaletteSelected(self, event=None):
        self.preferences[ThemeColorPath(self.preferences) + 'Palette'] = self.paletteString.get()
        self.ResetColors()

    def ResetColors(self):
        path = ThemeColorPath(self.preferences)
        self.preferences[path + 'Background'] = None
        self.preferences[path + 'Foreground'] = None
        self.callback()

    def Refresh(self):
        name = self.preferences['Appearance.Theme']
        legacy = name == 'Legacy'
        self.paletteEntry.configure(state='disabled' if legacy else 'readonly',
                                    values=() if legacy else tuple(PALETTE_VARIANTS[name]))
        self.paletteString.set('' if legacy else self.preferences[ThemeColorPath(self.preferences) + 'Palette'])
        theme = getattr(self._root(), 'appearanceTheme', None)
        if theme is not None:
            palette = theme.palette
            lowContrast = ContrastRatio(self, palette['foreground'], palette['background']) < 4.5
            self.warning.configure(text='Low text contrast: choose a different foreground or background.'
                                   if lowContrast else '')


class DialogStyleSelector(tk.Frame):
    def __init__(self, parent, preferences, callback, labelWidth=45):
        tk.Frame.__init__(self, parent)
        self.preferences = preferences
        self.callback = callback
        self.pack(side=tk.TOP, fill=tk.X)
        tk.Label(self, text='dialog style: ', width=labelWidth, anchor='e').pack(side=tk.LEFT)
        self.string = tk.StringVar(self, value=preferences['Appearance.DialogStyle'])
        self.entry = ttk.Combobox(self, textvariable=self.string, values=DIALOG_STYLES, state='readonly', width=30)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind('<<ComboboxSelected>>', self.OnSelected)

    def OnSelected(self, event=None):
        self.preferences['Appearance.DialogStyle'] = self.string.get()
        self.callback()


class ThemeColorButton(tk.Frame):
    def __init__(self, parent, text, preferences, role, callback, labelWidth=45):
        tk.Frame.__init__(self, parent)
        self.preferences = preferences
        self.role = role
        self.callback = callback
        self.pack(side=tk.TOP, fill=tk.X)
        tk.Label(self, text=text + ': ', width=labelWidth, anchor='e').pack(side=tk.LEFT)
        self.entry = tk.Button(self, text='Choose...', command=self.OnChoose)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.Refresh()

    def Refresh(self):
        palette = self._root().appearanceTheme.palette
        color = palette[self.role.lower()]
        foreground = '#000000' if ContrastRatio(self, '#000000', color) >= 4.5 else '#ffffff'
        self.entry.configure(background=color, foreground=foreground, activebackground=color,
                             activeforeground=foreground)

    def OnChoose(self):
        color = colorchooser.askcolor(self.entry.cget('background'), parent=self)[1]
        if color is not None:
            self.preferences[ThemeColorPath(self.preferences) + self.role] = color
            self.callback()
