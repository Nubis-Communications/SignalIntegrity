"""
Menus.py
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

# The menu bar and toolbar of both alternative GUIs, laid out like the tk app's menus.
# A GUI implements one handler per command id; adding a command here (and its handlers) is
# the only change needed to put it in both menu bars.  Tests check every id has a handler.

def Command(id,label,shortcut=None,only=None,checkable=False):
    """a menu command; only is 'qt' or 'web' for commands that exist in one GUI"""
    return {'kind':'command','id':id,'label':label,'shortcut':shortcut,'only':only,'checkable':checkable}

def Submenu(id,label,only=None):
    """a submenu the GUI fills when it opens (recent projects, themes, panels)"""
    return {'kind':'submenu','id':id,'label':label,'only':only}

SEPARATOR={'kind':'separator'}

MENUS=[
    ('File',[Command('new','New Project...','Ctrl+N'),
             Command('open','Open Project...','Ctrl+O'),
             Submenu('recent','Open Recent Projects'),
             SEPARATOR,
             Command('save','Save Project','Ctrl+S'),
             Command('saveAs','Save Project As...','Ctrl+Shift+S'),
             SEPARATOR,
             Command('archive','Archive Project'),
             Command('extractArchive','Extract Archived Project...'),
             SEPARATOR,
             Command('exportNetlist','Export NetList...'),
             Command('exportTikz','Export LaTeX (TikZ)...'),
             Command('exportImage','Export Bitmap Image...'),
             SEPARATOR,
             Command('netlist','Show Netlist'),
             SEPARATOR,
             Command('exit','Exit','Ctrl+Q',only='qt')]),
    ('Edit',[Command('undo','Undo','Ctrl+Z'),
             Command('redo','Redo','Ctrl+Shift+Z'),
             SEPARATOR,
             Command('cut','Cut','Ctrl+X'),
             Command('copy','Copy','Ctrl+C'),
             Command('paste','Paste','Ctrl+V'),
             Command('duplicate','Duplicate','Ctrl+D'),
             Command('delete','Delete Selected','Del'),
             SEPARATOR,
             Command('cancel','Cancel Placing or Wiring','Esc')]),
    ('Parts',[Command('properties','Edit Properties'),
              Command('rotate','Rotate Part','Ctrl+R'),
              Command('flipHorizontal','Flip Horizontally'),
              Command('flipVertical','Flip Vertically'),
              Command('deletePart','Delete Part')]),
    ('Wires',[Command('wire','Add Wire','W',checkable=True),
              Command('deleteVertex','Delete Vertex'),
              Command('duplicateVertex','Duplicate Vertex'),
              Command('deleteWire','Delete Wire')]),
    ('View',[Command('zoomIn','Zoom In','Ctrl++'),
             Command('zoomOut','Zoom Out','Ctrl+-'),
             Command('zoomFit','Zoom to Fit','Ctrl+0'),
             SEPARATOR,
             Command('viewDevice','View / Open Project','Ctrl+E'),
             Command('up','Up to Parent Project','Alt+Up'),
             SEPARATOR,
             Submenu('panels','Panels',only='qt'),
             Submenu('theme','Theme')]),
    ('Calculate',[Command('postProcessing','Post-Processing...'),
                  SEPARATOR,
                  Command('simulate','Simulate'),
                  Command('sparameters','Calculate S-parameters'),
                  Command('virtualprobe','Virtual Probe'),
                  Command('deembed','Deembed')]),
    ('Variables',[Command('equations','Schematic Equations...')]),
    ('Help',[Command('help','Open Help','F1'),
             Command('documentation','Software Documentation'),
             SEPARATOR,
             Command('preferences','Preferences...'),
             SEPARATOR,
             Command('about','About')]),
]

TOOLBAR=['new','open','save',None,'undo','redo',None,'zoomIn','zoomOut','zoomFit',None,
         'wire','rotate','flipHorizontal','duplicate','delete',None,'viewDevice','up',None,
         'simulate','sparameters','virtualprobe','deembed',None,'help']

# the Calculate commands, named as ProjectSession.CALCULATIONS so GUIs can map them in one loop
CALCULATION_IDS=['simulate','sparameters','virtualprobe','deembed']

# short captions shown under the toolbar icons (GuiCore.Icons has the icons)
TOOLBAR_LABELS={'new':'New','open':'Open','save':'Save','undo':'Undo','redo':'Redo',
                'zoomIn':'Zoom In','zoomOut':'Zoom Out','zoomFit':'Fit',
                'wire':'Wire','rotate':'Rotate','flipHorizontal':'Flip','duplicate':'Duplicate','delete':'Delete',
                'viewDevice':'View','up':'Up',
                'simulate':'Simulate','sparameters':'S-params','virtualprobe':'V-Probe','deembed':'De-embed','help':'Help'}

# toolbar icon size in pixels
TOOLBAR_ICON_SIZE=24

def MenusFor(gui):
    """@return MENUS without the entries that belong to the other GUI ('qt' or 'web') or separators left dangling"""
    result=[]
    for title,items in MENUS:
        kept=[]
        for item in items:
            if item.get('only') not in (None,gui):
                continue
            if item['kind']=='separator' and (not kept or kept[-1]['kind']=='separator'):
                continue
            kept.append(item)
        while kept and kept[-1]['kind']=='separator':
            kept.pop()
        result.append((title,kept))
    return result

def CommandIds(gui):
    return [item['id'] for _,items in MenusFor(gui) for item in items if item['kind']=='command']

def SubmenuIds(gui):
    return [item['id'] for _,items in MenusFor(gui) for item in items if item['kind']=='submenu']
