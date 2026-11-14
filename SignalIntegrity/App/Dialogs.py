"""Theme-aware modal dialogs shared by the desktop applications."""

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

import fnmatch
import os
import tkinter as tk
from tkinter import ttk, filedialog

from SignalIntegrity.App.MenuSystemHelpers import IconLabel


DIALOG_STYLES = ('Native', 'Themed')


def DialogParent(parent=None):
    if parent is not None:
        if isinstance(parent, str):
            if tk._default_root is None:
                return None
            parent = tk._default_root.nametowidget(parent)
        return parent.winfo_toplevel()
    root = tk._default_root
    if root is None:
        return None
    return (root.grab_current() or root.focus_get() or root).winfo_toplevel()


def UseThemedDialogs(parent=None):
    parent = DialogParent(parent)
    theme = None if parent is None else getattr(parent._root(), 'appearanceTheme', None)
    if theme is None:
        return False
    style = theme.preferences['Appearance.DialogStyle']
    if style not in DIALOG_STYLES:
        raise ValueError('Unknown dialog style: {!r}'.format(style))
    return style == 'Themed'


def _WindowExists(window):
    try:
        return window.winfo_exists()
    except tk.TclError as error:
        if 'application has been destroyed' not in str(error):
            raise
        return False


def RunModal(window, parent, focus, widthScale=1):
    previousGrab = window.grab_current()
    previousGrabStatus = None if previousGrab is None else previousGrab.grab_status()
    previousFocus = window.focus_get()
    if parent.winfo_viewable():
        window.transient(parent)
    window.update_idletasks()
    width, height = window.winfo_reqwidth(), window.winfo_reqheight()
    size = ''
    if widthScale != 1:
        width = min(width * widthScale, window.winfo_screenwidth() - 40)
        size = '{}x{}'.format(width, height)
    if parent.winfo_viewable():
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
    else:
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
    if widthScale != 1 and 0 <= x < window.winfo_screenwidth():
        x = min(x, window.winfo_screenwidth() - width - 20)
    window.geometry(size + '+{}+{}'.format(max(0, x), max(0, y)))
    window.deiconify()
    window.wait_visibility()
    window.grab_set()
    focus.focus_set()
    try:
        window.wait_window()
    finally:
        if _WindowExists(window):
            window.destroy()
        if _WindowExists(parent):
            if previousGrab is not None and _WindowExists(previousGrab):
                if previousGrabStatus == 'global':
                    previousGrab.grab_set_global()
                else:
                    previousGrab.grab_set()
            if previousFocus is not None and _WindowExists(previousFocus):
                previousFocus.focus_set()


class MessageDialog(tk.Toplevel):
    buttonSets = {
        'ok': ('ok',), 'okcancel': ('ok', 'cancel'),
        'yesno': ('yes', 'no'), 'yesnocancel': ('yes', 'no', 'cancel'),
        'retrycancel': ('retry', 'cancel'),
    }
    icons = {'info': 'dialog-information-4', 'question': 'dialog-question',
             'error': 'dialog-error', 'warning': 'dialog-warning'}

    def __init__(self, parent, title, message, icon, kind, default=None, detail=None):
        if kind not in self.buttonSets or icon not in self.icons:
            raise tk.TclError('Unsupported message box type or icon')
        choices = self.buttonSets[kind]
        default = choices[0] if default is None else default
        if default not in choices:
            raise tk.TclError('Message box default must name one of its buttons')
        tk.Toplevel.__init__(self, parent)
        self.withdraw()
        self.parent = parent
        self.result = None
        self.title('' if title is None else title)
        self.resizable(False, False)
        body = ttk.Frame(self, padding=16)
        body.pack(fill=tk.BOTH, expand=True)
        IconLabel(body, iconfile=self.icons[icon], size=32).pack(side=tk.LEFT, anchor='n', padx=(0, 12))
        text = ttk.Frame(body)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(text, text='' if message is None else message,
                  wraplength=520, justify=tk.LEFT).pack(anchor='w')
        if detail:
            ttk.Label(text, text=detail, wraplength=520, justify=tk.LEFT).pack(anchor='w', pady=(10, 0))
        actions = ttk.Frame(self, padding=(16, 0, 16, 16))
        actions.pack(fill=tk.X)
        self.buttons = {}
        for choice in choices:
            button = ttk.Button(actions, text=choice.capitalize(), command=lambda choice=choice: self.Choose(choice))
            button.pack(side=tk.LEFT, padx=4)
            button.bind('<Return>', lambda event, choice=choice: self.Choose(choice))
            self.buttons[choice] = button
        self.defaultButton = self.buttons[default]
        self.cancelResult = 'cancel' if 'cancel' in choices else choices[-1]
        self.protocol('WM_DELETE_WINDOW', self.Cancel)
        self.bind('<Escape>', self.Cancel)
        self.bind('<Return>', lambda event: self.Choose(default))

    def Choose(self, result):
        self.result = result
        self.destroy()
        return 'break'

    def Cancel(self, event=None):
        return self.Choose(self.cancelResult)

    def Show(self):
        RunModal(self, self.parent, self.defaultButton)
        return self.result


class ThemedFileDialog(filedialog.FileDialog):
    def __init__(self, mode, parent=None, title=None, initialdir=None, initialfile='',
                 filetypes=(), defaultextension='', mustexist=False,
                 confirmoverwrite=True, typevariable=None, multiple=False):
        if mode not in ('open', 'save', 'directory'):
            raise ValueError('Unknown file dialog mode: ' + mode)
        if multiple:
            raise tk.TclError('Themed file dialogs support single selection only')
        self.parent = DialogParent(parent)
        self.mode = mode
        self.extension = defaultextension
        self.mustexist = mustexist
        self.confirmoverwrite = confirmoverwrite
        self.typevariable = typevariable
        self.result = None
        filedialog.FileDialog.__init__(self, self.parent, title or {
            'open': 'Open', 'save': 'Save As', 'directory': 'Select Folder'}[mode])
        self.top.withdraw()
        self.top.bind('<Escape>', self.cancel_command)
        self.ok_button.configure(text={'open': 'Open', 'save': 'Save', 'directory': 'Select Folder'}[mode])
        ttk.Label(self.top, text='Folder / filter:').pack(side=tk.TOP, fill=tk.X, before=self.filter)
        ttk.Label(self.top, text='Folder:' if mode == 'directory' else 'File name:').pack(
            side=tk.BOTTOM, fill=tk.X, after=self.selection)
        self.filetypes = tuple(filetypes) or (('All files', '*'),)
        typeRow = ttk.Frame(self.top, padding=4)
        typeRow.pack(side=tk.TOP, fill=tk.X, before=self.midframe)
        ttk.Label(typeRow, text='File type:').pack(side=tk.LEFT, padx=(0, 8))
        self.types = ttk.Combobox(typeRow, state='readonly', values=[item[0] for item in self.filetypes])
        self.types.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.types.current(0)
        if typevariable is not None:
            label = self.top.getvar(str(typevariable))
            labels = [item[0] for item in self.filetypes]
            if label in labels:
                self.types.current(labels.index(label))
        self.types.bind('<<ComboboxSelected>>', self.SelectType)
        if mode == 'directory':
            typeRow.pack_forget()
            self.files.configure(state='disabled')
            self.files.pack_forget()
            self.filesbar.pack_forget()
        self.directory = os.path.abspath(os.path.expanduser(initialdir or os.getcwd()))
        self.set_filter(self.directory, self.TypePattern())
        self.set_selection(initialfile or '')
        self.filter_command()

    def TypePattern(self):
        patterns = self.filetypes[self.types.current()][1]
        if isinstance(patterns, str):
            patterns = self.top.tk.splitlist(patterns)
        patterns = tuple('*' + pattern if pattern.startswith('.') else pattern for pattern in patterns)
        # A Tcl list string; Tk 9 returns lists from [format %s ...] as tuples, so build it directly.
        return ' '.join('{' + pattern + '}' if (not pattern or any(
            character.isspace() or character in '{}"\\[]$;' for character in pattern)) else pattern
            for pattern in patterns)

    def SelectType(self, event=None):
        self.set_filter(self.directory, self.TypePattern())
        if self.typevariable is not None:
            self.top.setvar(str(self.typevariable), self.types.get())
        self.filter_command()

    def filter_command(self, event=None):
        from SignalIntegrity.App import MessageBox
        directory, pattern = self.get_filter()
        directory = os.path.abspath(directory)
        try:
            patterns = self.top.tk.splitlist(pattern)
            names = sorted(os.listdir(directory), key=os.path.normcase)
        except (OSError, tk.TclError) as error:
            MessageBox.showerror('Open Folder', str(error), parent=self.top)
            return
        self.directory = directory
        self.set_filter(directory, pattern)
        self.dirs.delete(0, tk.END)
        self.files.delete(0, tk.END)
        self.dirs.insert(tk.END, os.pardir)
        for name in names:
            if os.path.isdir(os.path.join(directory, name)):
                self.dirs.insert(tk.END, name)
            elif self.mode != 'directory' and any(fnmatch.fnmatch(name, pattern) for pattern in patterns):
                self.files.insert(tk.END, name)
        self.set_selection(os.path.basename(self.get_selection()) if self.mode != 'directory' else '')

    def dirs_select_event(self, event):
        filedialog.FileDialog.dirs_select_event(self, event)
        if self.mode == 'directory':
            self.set_selection(self.get_filter()[0])

    def ok_command(self):
        from SignalIntegrity.App import MessageBox
        filename = os.path.abspath(os.path.join(self.directory, self.get_selection()))
        invalid = '\x00' in filename
        if os.name == 'nt':
            name = os.path.basename(filename)
            stem = name.split('.')[0].upper()
            reserved = ('CON', 'PRN', 'AUX', 'NUL') + tuple(
                prefix + str(number) for prefix in ('COM', 'LPT') for number in range(1, 10))
            invalid = invalid or stem in reserved or name.endswith(('.', ' ')) or any(
                char in '<>:"|?*' or ord(char) < 32 for char in name)
        if invalid:
            MessageBox.showerror('File Selection', 'Invalid file or folder name.', parent=self.top)
            return
        if self.mode != 'directory' and os.path.isdir(filename):
            self.set_filter(filename, self.get_filter()[1])
            self.filter_command()
            self.set_selection('')
            return
        if self.extension and not os.path.splitext(filename)[1] and (
                self.mode == 'save' or (self.mode == 'open' and not os.path.isfile(filename))):
            filename += self.extension if self.extension.startswith('.') else '.' + self.extension
        if self.mode == 'open' and not os.path.isfile(filename):
            MessageBox.showerror('Open File', 'Select an existing file.', parent=self.top)
            return
        if self.mode == 'directory':
            if not os.path.isdir(filename) and (self.mustexist or not os.path.isdir(os.path.dirname(filename))):
                MessageBox.showerror('Select Folder', 'Select an existing folder or a new folder in an existing directory.',
                                     parent=self.top)
                return
            if os.path.exists(filename) and not os.path.isdir(filename):
                MessageBox.showerror('Select Folder', 'The selection is not a folder.', parent=self.top)
                return
        if self.mode == 'save':
            if not os.path.isdir(os.path.dirname(filename)):
                MessageBox.showerror('Save As', 'The destination folder does not exist.', parent=self.top)
                return
            if os.path.lexists(filename) and self.confirmoverwrite and not MessageBox.askyesno(
                    'Confirm Save As', 'Replace the existing file?\n\n' + filename, default='no', parent=self.top):
                return
        self.quit(filename)

    def quit(self, how=None):
        if self.typevariable is not None:
            self.top.setvar(str(self.typevariable), self.types.get())
        self.result = how
        self.top.destroy()

    def Show(self):
        RunModal(self.top, self.parent, self.selection, widthScale=1 if self.mode == 'directory' else 3)
        return self.result
