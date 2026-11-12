"""Message-box functions retaining Tk's return-value conventions."""

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

from tkinter import messagebox as native
from SignalIntegrity.App.Dialogs import DialogParent, MessageDialog, UseThemedDialogs


def _show(title, message, icon, kind, **options):
    if not UseThemedDialogs(options.get('parent')):
        return native._show(title, message, icon, kind, **options)
    options = options.copy()
    parent = DialogParent(options.pop('parent', None))
    icon = options.pop('icon', icon)
    kind = options.pop('type', kind)
    return MessageDialog(parent, title, message, icon, kind, **options).Show()


def showinfo(title=None, message=None, **options):
    return _show(title, message, 'info', 'ok', **options)


def showwarning(title=None, message=None, **options):
    return _show(title, message, 'warning', 'ok', **options)


def showerror(title=None, message=None, **options):
    return _show(title, message, 'error', 'ok', **options)


def askquestion(title=None, message=None, **options):
    return _show(title, message, 'question', 'yesno', **options)


def askokcancel(title=None, message=None, **options):
    return _show(title, message, 'question', 'okcancel', **options) == 'ok'


def askyesno(title=None, message=None, **options):
    return _show(title, message, 'question', 'yesno', **options) == 'yes'


def askyesnocancel(title=None, message=None, **options):
    result = _show(title, message, 'question', 'yesnocancel', **options)
    return None if result == 'cancel' else result == 'yes'


def askretrycancel(title=None, message=None, **options):
    return _show(title, message, 'warning', 'retrycancel', **options) == 'retry'
