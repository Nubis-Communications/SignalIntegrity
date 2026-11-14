"""
Theme.py
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
import os

from PySide6.QtGui import QPalette, QColor, QIcon
from PySide6.QtWidgets import QApplication

from SignalIntegrity.GuiCore import Themes

_current={'id':'builtin:light','name':'SignalIntegrity Light','palette':Themes.LoadTheme('builtin:light')[1]}

def Current():
    return _current['palette']

def CurrentId():
    return _current['id']

def AppIcon():
    return QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)),'icons','SignalIntegrityQt.png'))

_commandIcons={}

def CommandIcon(commandId):
    """QIcon for a GuiCore.Menus command from the shared SVG icons (empty if it has none)"""
    from SignalIntegrity.GuiCore import Icons
    if commandId not in _commandIcons:
        icon=QIcon()
        if Icons.HasIcon(commandId):
            from PySide6.QtCore import QByteArray, Qt
            from PySide6.QtGui import QPixmap, QPainter
            from PySide6.QtSvg import QSvgRenderer
            renderer=QSvgRenderer(QByteArray(Icons.Svg(commandId).encode()))
            for size in (16,24,32,48,64,96):
                pixmap=QPixmap(size,size)
                pixmap.fill(Qt.transparent)
                painter=QPainter(pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                renderer.render(painter)
                painter.end()
                icon.addPixmap(pixmap)
        _commandIcons[commandId]=icon
    return _commandIcons[commandId]

def StyleSheet(p):
    return f"""
QWidget {{ color: {p['foreground']}; }}
QMainWindow, QDialog {{ background: {p['background']}; }}
QDockWidget {{ color: {p['panelForeground']}; }}
QDockWidget::title {{ background: {p['toolbar']}; padding: 4px; border-bottom: 1px solid {p['border']}; }}
QTreeWidget, QTableWidget, QListWidget, QPlainTextEdit, QScrollArea {{
    background: {p['panel']}; color: {p['panelForeground']}; border: 1px solid {p['border']};
    alternate-background-color: {p['toolbar']}; }}
QTreeWidget::item:hover, QTableWidget::item:hover {{ background: {p['hover']}; }}
QTreeWidget::item:selected, QTableWidget::item:selected {{ background: {p['selection']}; color: {p['selectionForeground']}; }}
QHeaderView::section {{ background: {p['toolbar']}; color: {p['panelForeground']}; border: none;
    border-right: 1px solid {p['border']}; border-bottom: 1px solid {p['border']}; padding: 3px; }}
QTableWidget {{ gridline-color: {p['border']}; }}
QLineEdit, QComboBox {{ background: {p['inputBackground']}; color: {p['inputForeground']};
    border: 1px solid {p['border']}; border-radius: 3px; padding: 2px 4px; }}
QLineEdit:focus, QComboBox:focus {{ border-color: {p['accent']}; }}
QToolBar {{ background: {p['toolbar']}; border-bottom: 1px solid {p['border']}; spacing: 2px; padding: 2px 4px; }}
QToolBar::separator {{ background: {p['border']}; width: 1px; margin: 6px 5px; }}
QMenu::separator {{ height: 1px; background: {p['border']}; margin: 4px 8px; }}
QToolButton {{ color: {p['foreground']}; padding: 3px 4px; border-radius: 6px; border: 1px solid transparent; }}
QToolButton:hover {{ background: {p['hover']}; border-color: {p['border']}; }}
QToolButton:pressed {{ background: {p['selection']}; }}
QToolButton:checked {{ background: {p['selection']}; color: {p['selectionForeground']}; border-color: {p['accent']}; }}
QToolButton:disabled {{ color: {p['border']}; }}
QPushButton {{ background: {p['buttonBackground']}; color: {p['buttonForeground']}; border: none;
    border-radius: 3px; padding: 4px 12px; }}
QPushButton:disabled {{ background: {p['border']}; }}
QMenuBar {{ background: {p['toolbar']}; color: {p['foreground']}; }}
QMenuBar::item:selected, QMenu::item:selected {{ background: {p['selection']}; color: {p['selectionForeground']}; }}
QMenu {{ background: {p['panel']}; color: {p['panelForeground']}; border: 1px solid {p['border']}; }}
QMenu::item:disabled {{ color: {p['border']}; }}
QStatusBar {{ background: {p['statusBar']}; color: {p['statusBarForeground']}; }}
QTabWidget::pane {{ border: 1px solid {p['border']}; }}
QTabBar::tab {{ background: {p['toolbar']}; color: {p['foreground']}; padding: 4px 10px; border: 1px solid {p['border']}; }}
QTabBar::tab:selected {{ background: {p['background']}; border-bottom-color: {p['accent']}; }}
QToolTip {{ background: {p['panel']}; color: {p['panelForeground']}; border: 1px solid {p['border']}; }}
"""

def Apply(themeId=None,name=None,palette=None,save=True):
    """applies a theme to the whole application; with no arguments the saved theme is applied
    @return (id,name)"""
    if palette is None:
        if themeId is None:
            themeId,name,palette=Themes.CurrentTheme()
        else:
            loadedName,palette=Themes.LoadTheme(themeId)
            name=name or loadedName
    _current.update({'id':themeId,'name':name,'palette':palette})
    app=QApplication.instance()
    if app is not None:
        app.setStyle('Fusion')
        q=QPalette()
        p=palette
        for role,color in ((QPalette.Window,p['background']),(QPalette.WindowText,p['foreground']),
                           (QPalette.Base,p['panel']),(QPalette.AlternateBase,p['toolbar']),
                           (QPalette.Text,p['panelForeground']),(QPalette.Button,p['toolbar']),
                           (QPalette.ButtonText,p['foreground']),(QPalette.Highlight,p['selection']),
                           (QPalette.HighlightedText,p['selectionForeground']),(QPalette.ToolTipBase,p['panel']),
                           (QPalette.ToolTipText,p['panelForeground']),(QPalette.PlaceholderText,p['border']),
                           (QPalette.Link,p['accent'])):
            q.setColor(role,QColor(color))
        q.setColor(QPalette.Disabled,QPalette.Text,QColor(p['border']))
        q.setColor(QPalette.Disabled,QPalette.ButtonText,QColor(p['border']))
        q.setColor(QPalette.Disabled,QPalette.WindowText,QColor(p['border']))
        app.setPalette(q)
        app.setStyleSheet(StyleSheet(p))
    if save and themeId is not None:
        try:
            Themes.SaveThemeId(themeId)
        except OSError:
            pass
    return themeId,name

def StyleAxes(figure,axes,palette=None):
    """colors a matplotlib figure and axes for the theme"""
    p=Current() if palette is None else palette
    figure.set_facecolor(p['background'])
    axes.set_facecolor(p['background'])
    for spine in axes.spines.values():
        spine.set_color(p['border'] if not p['dark'] else p['foreground'])
    axes.tick_params(colors=p['foreground'],which='both')
    axes.xaxis.label.set_color(p['foreground'])
    axes.yaxis.label.set_color(p['foreground'])
    axes.title.set_color(p['foreground'])
    legend=axes.get_legend()
    if legend is not None:
        legend.get_frame().set_facecolor(p['panel'])
        legend.get_frame().set_edgecolor(p['border'])
        for text in legend.get_texts():
            text.set_color(p['foreground'])

def GridColor(palette=None):
    p=Current() if palette is None else palette
    return p['grid']
