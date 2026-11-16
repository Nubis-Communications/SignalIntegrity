"""
Dialogs.py
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
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QPlainTextEdit, QLabel, QDialogButtonBox, QTabWidget, QWidget,
    QFormLayout, QCheckBox, QLineEdit, QScrollArea)

class TextEditorDialog(QDialog):
    """the tk Equations and Post-Processing editors: a monospaced script editor; when check is
    given, the script is checked as it is typed (tk's auto-debug) and the result shown below"""
    def __init__(self,title,text,check=None,helpTopic=None,parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(720,480)
        self.check=check
        layout=QVBoxLayout(self)
        self.editor=QPlainTextEdit(text)
        font=QFont('Consolas'); font.setStyleHint(QFont.Monospace)
        self.editor.setFont(font)
        self.editor.setTabStopDistance(4*self.editor.fontMetrics().horizontalAdvance(' '))
        layout.addWidget(self.editor,1)
        self.status=QLabel('')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel|
                                 (QDialogButtonBox.Help if helpTopic else QDialogButtonBox.NoButton))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        if helpTopic:
            from SignalIntegrity.GuiCore import Help
            buttons.helpRequested.connect(lambda: Help.Open(helpTopic))
        layout.addWidget(buttons)
        if check is not None:
            self.timer=QTimer(self); self.timer.setSingleShot(True); self.timer.setInterval(400)
            self.timer.timeout.connect(self.Check)
            self.editor.textChanged.connect(self.timer.start)
            self.Check()
    def Text(self):
        return self.editor.toPlainText()
    def Check(self):
        error=self.check(self.Text())
        self.status.setText('No Errors' if error is None else error)

class PreferencesDialog(QDialog):
    """the SignalIntegrity preferences (shared with the tk app), one tab per section; each change is
    saved when it is made, as the tk preferences dialog does"""
    def __init__(self,parent=None):
        super().__init__(parent)
        from SignalIntegrity.GuiCore import Preferences
        self.setWindowTitle('Preferences')
        self.resize(640,560)
        layout=QVBoxLayout(self)
        tabs=QTabWidget()
        layout.addWidget(tabs,1)
        self.status=QLabel('Saved to '+Preferences.FileName())
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        buttons=QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.editors={}
        for section in Preferences.Items():
            page=QWidget()
            form=QFormLayout(page)
            for item in section['items']:
                if item['type']=='bool':
                    editor=QCheckBox()
                    editor.setChecked(bool(item['value']))
                    editor.toggled.connect(lambda checked,p=item['path']: self.Set(p,checked))
                else:
                    editor=QLineEdit('' if item['value'] in (None,'None') else str(item['value']))
                    editor.editingFinished.connect(lambda p=item['path'],e=editor: self.Set(p,e.text()))
                self.editors[item['path']]=editor
                form.addRow(item['label'],editor)
            scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(page)
            tabs.addTab(scroll,section['label'])
    def Set(self,path,value):
        from SignalIntegrity.GuiCore import Preferences
        try:
            stored=Preferences.Set(path,value)
            self.status.setText('saved '+path+' = '+str(stored))
        except Preferences.PreferencesError as e:
            self.status.setText(str(e))
