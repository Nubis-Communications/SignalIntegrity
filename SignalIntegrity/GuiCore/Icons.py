"""
Icons.py
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

# Toolbar and menu icons for both alternative GUIs, keyed by GuiCore.Menus command id.
# Each is the body of a 32x32 SVG; 'ID-' prefixes gradient ids so icons can be inlined
# together in one HTML page.  Colours are chosen to read on light and dark themes.

def _linear(name,top,bottom,horizontal=False):
    x2,y2=('1','0') if horizontal else ('0','1')
    return ('<linearGradient id="ID-%s" x1="0" y1="0" x2="%s" y2="%s"><stop offset="0" stop-color="%s"/>'
            '<stop offset="1" stop-color="%s"/></linearGradient>')%(name,x2,y2,top,bottom)

def _radial(name,inner,middle,outer):
    return ('<radialGradient id="ID-%s" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="%s"/>'
            '<stop offset=".6" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient>')%(name,inner,middle,outer)

_PAGE=('<path d="M7.5 3H19l7 7v17.5A1.5 1.5 0 0 1 24.5 29h-17A1.5 1.5 0 0 1 6 27.5v-23A1.5 1.5 0 0 1 7.5 3z" '
       'fill="url(#ID-page)" stroke="#4a78c2" stroke-width="1.2"/>'
       '<path d="M19 3v5.5A1.5 1.5 0 0 0 20.5 10H26" fill="#b9d2f7" stroke="#4a78c2" stroke-width="1.2" stroke-linejoin="round"/>')

_LENS=('<circle cx="13" cy="13" r="8.5" fill="url(#ID-lens)" stroke="#2c5282" stroke-width="2.2"/>'
       '<path d="M19.6 19.6l7 7" stroke="#5a3e1b" stroke-width="4.4" stroke-linecap="round"/>'
       '<path d="M19.6 19.6l7 7" stroke="#b7834a" stroke-width="2" stroke-linecap="round"/>')

_FLOPPY=('<path d="M5 5.5A1.5 1.5 0 0 1 6.5 4h16.8L28 8.7v17.8a1.5 1.5 0 0 1-1.5 1.5h-20A1.5 1.5 0 0 1 5 26.5z" '
         'fill="url(#ID-disk)" stroke="#1e4f9a" stroke-width="1.2"/>'
         '<rect x="10" y="4" width="11" height="8" rx="1" fill="#e8eef7" stroke="#1e4f9a" stroke-width=".8"/>'
         '<rect x="17.3" y="5.5" width="2.4" height="5" rx=".5" fill="#2a5fb8"/>'
         '<rect x="8.5" y="16" width="15" height="10.5" rx="1" fill="#ffffff" stroke="#1e4f9a" stroke-width=".8"/>'
         '<path d="M11 19.5h10M11 22.8h10" stroke="#9fb3d1" stroke-width="1.3" stroke-linecap="round"/>')

ICONS={
    'new':'<defs>'+_linear('page','#ffffff','#d6e6ff')+_linear('badge','#68d391','#25855a')+'</defs>'+_PAGE+
        '<circle cx="23" cy="23" r="7" fill="url(#ID-badge)" stroke="#1c6b45" stroke-width="1"/>'
        '<path d="M23 19.3v7.4M19.3 23h7.4" stroke="#ffffff" stroke-width="2.4" stroke-linecap="round"/>',
    'open':'<defs>'+_linear('back','#f6c453','#d9922b')+_linear('front','#ffe39a','#f0ad3a')+'</defs>'
        '<path d="M3 8.5A1.5 1.5 0 0 1 4.5 7h7l2.5 3h12.5A1.5 1.5 0 0 1 28 11.5V25a1.5 1.5 0 0 1-1.5 1.5h-22A1.5 1.5 0 0 1 3 25z" '
        'fill="url(#ID-back)" stroke="#a8691a" stroke-width="1.1"/>'
        '<rect x="7" y="9" width="18" height="10" rx="1" fill="#ffffff" stroke="#c9d3e0" stroke-width=".8"/>'
        '<path d="M3.3 26.2L7 14.6A1.6 1.6 0 0 1 8.5 13.5H29a1 1 0 0 1 .95 1.3l-3.5 10.6a1.6 1.6 0 0 1-1.5 1.1H4.5z" '
        'fill="url(#ID-front)" stroke="#a8691a" stroke-width="1.1" stroke-linejoin="round"/>',
    'save':'<defs>'+_linear('disk','#64a5f5','#2a5fb8')+'</defs>'+_FLOPPY,
    'saveAs':'<defs>'+_linear('disk','#64a5f5','#2a5fb8')+_linear('pencil','#fbd38d','#dd6b20',True)+'</defs>'+_FLOPPY+
        '<g transform="rotate(45 24 20)"><rect x="21.8" y="10" width="4.4" height="13" rx=".8" fill="url(#ID-pencil)" stroke="#7b341e" stroke-width=".9"/>'
        '<path d="M21.8 23h4.4L24 27.5z" fill="#fde8c8" stroke="#7b341e" stroke-width=".9" stroke-linejoin="round"/></g>',
    'netlist':'<defs>'+_linear('page','#ffffff','#d6e6ff')+'</defs>'+_PAGE+
        '<path d="M10 13h12M10 16.5h9M10 20h12M10 23.5h7" stroke="#4a78c2" stroke-width="1.8" stroke-linecap="round"/>'
        '<circle cx="10" cy="13" r="1.3" fill="#dd6b20"/><circle cx="10" cy="20" r="1.3" fill="#dd6b20"/>',
    'zoomIn':'<defs>'+_radial('lens','#ffffff','#c7e3ff','#7fb6ef')+'</defs>'+_LENS+
        '<path d="M13 9v8M9 13h8" stroke="#25855a" stroke-width="2.6" stroke-linecap="round"/>',
    'zoomOut':'<defs>'+_radial('lens','#ffffff','#c7e3ff','#7fb6ef')+'</defs>'+_LENS+
        '<path d="M9 13h8" stroke="#c53030" stroke-width="2.6" stroke-linecap="round"/>',
    'zoomFit':'<defs>'+_linear('screen','#ebf8ff','#90cdf4')+'</defs>'
        '<rect x="8.5" y="9.5" width="15" height="13" rx="1.6" fill="url(#ID-screen)" stroke="#2c5282" stroke-width="1.2"/>'
        '<path d="M11 18h3l1.5-4.5 2 7 1.6-4h2" fill="none" stroke="#25855a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M4 10V4h6M22 4h6v6M28 22v6h-6M10 28H4v-6" fill="none" stroke="#3182ce" stroke-width="2.8" '
        'stroke-linecap="round" stroke-linejoin="round"/>',
    'wire':'<defs>'+_linear('wire','#38b2ac','#2b6cb0',True)+'</defs>'
        '<path d="M5 26V14h11V6h11" fill="none" stroke="#38b2ac" stroke-opacity=".25" stroke-width="6" '
        'stroke-linejoin="round" stroke-linecap="round"/>'
        '<path d="M5 26V14h11V6h11" fill="none" stroke="url(#ID-wire)" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
        '<circle cx="5" cy="26" r="2.8" fill="#ffffff" stroke="#2b6cb0" stroke-width="1.7"/>'
        '<circle cx="16" cy="14" r="2.8" fill="#f6ad55" stroke="#c05621" stroke-width="1.5"/>'
        '<circle cx="27" cy="6" r="2.8" fill="#ffffff" stroke="#2b6cb0" stroke-width="1.7"/>',
    'rotate':'<defs>'+_linear('arc','#b794f4','#553c9a')+'</defs>'
        '<path d="M25.5 16A9.5 9.5 0 1 1 22.7 9.3" fill="none" stroke="url(#ID-arc)" stroke-width="4" stroke-linecap="round"/>'
        '<path d="M27.4 13.2L19.6 11.6L25 5.2z" fill="#6b46c1" stroke="#44337a" stroke-width=".9" stroke-linejoin="round"/>'
        '<rect x="12" y="13.2" width="8" height="5.6" rx="1.2" fill="#e9d8fd" stroke="#6b46c1" stroke-width="1.2"/>',
    'delete':'<defs>'+_linear('can','#fc8181','#c53030')+_linear('lid','#feb2b2','#e53e3e')+'</defs>'
        '<path d="M12.5 6.2V4.6a1.1 1.1 0 0 1 1.1-1.1h4.8a1.1 1.1 0 0 1 1.1 1.1v1.6" fill="none" stroke="#9b2c2c" stroke-width="1.6"/>'
        '<rect x="5.5" y="6" width="21" height="4" rx="1.3" fill="url(#ID-lid)" stroke="#9b2c2c" stroke-width="1.1"/>'
        '<path d="M8 11h16l-1.4 15.7a1.8 1.8 0 0 1-1.8 1.6h-9.6a1.8 1.8 0 0 1-1.8-1.6z" fill="url(#ID-can)" stroke="#9b2c2c" stroke-width="1.1"/>'
        '<path d="M12.8 14.5v10M16 14.5v10M19.2 14.5v10" stroke="#ffffff" stroke-opacity=".8" stroke-width="1.6" stroke-linecap="round"/>',
    'cancel':'<defs>'+_linear('disc','#fc8181','#c53030')+'</defs>'
        '<circle cx="16" cy="16" r="12" fill="url(#ID-disc)" stroke="#9b2c2c" stroke-width="1.2"/>'
        '<path d="M11 11l10 10M21 11L11 21" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>',
    'properties':'<defs>'+_linear('panel','#ebf8ff','#bee3f8')+'</defs>'
        '<rect x="4" y="4" width="24" height="24" rx="4" fill="url(#ID-panel)" stroke="#2c5282" stroke-width="1.2"/>'
        '<path d="M9 11h14M9 16h14M9 21h14" stroke="#2c5282" stroke-width="1.7" stroke-linecap="round"/>'
        '<circle cx="13" cy="11" r="2.6" fill="#ed8936" stroke="#9c4221"/><circle cx="20" cy="16" r="2.6" fill="#48bb78" stroke="#276749"/>'
        '<circle cx="11.5" cy="21" r="2.6" fill="#9f7aea" stroke="#553c9a"/>',
    'viewDevice':'<defs>'+_linear('chip','#63b3ed','#2b6cb0')+'</defs>'
        '<path d="M8 11V7.5M13 11V7.5M18 11V7.5M8 26v3.5M13 26v3.5M18 26v3.5" stroke="#718096" stroke-width="1.8" stroke-linecap="round"/>'
        '<rect x="4.5" y="10.5" width="17" height="16" rx="2" fill="url(#ID-chip)" stroke="#2c5282" stroke-width="1.2"/>'
        '<circle cx="8" cy="14" r="1.3" fill="#ebf8ff"/>'
        '<path d="M28 4L17 15" stroke="#dd6b20" stroke-width="3.2" stroke-linecap="round"/>'
        '<path d="M12.5 19.5V12.6l6.9 6.9z" fill="#dd6b20" stroke="#9c4221" stroke-width=".8" stroke-linejoin="round"/>',
    'up':'<defs>'+_linear('tray','#bee3f8','#4299e1')+'</defs>'
        '<path d="M4 18h7l2 3h6l2-3h7v8.5a1.5 1.5 0 0 1-1.5 1.5h-21A1.5 1.5 0 0 1 4 26.5z" fill="url(#ID-tray)" stroke="#2c5282" '
        'stroke-width="1.2" stroke-linejoin="round"/>'
        '<path d="M16 19V8" stroke="#38a169" stroke-width="3.6" stroke-linecap="round"/>'
        '<path d="M9.5 11L16 3.5l6.5 7.5z" fill="#48bb78" stroke="#276749" stroke-width="1" stroke-linejoin="round"/>',
    'simulate':'<defs>'+_linear('screen','#2d3748','#11151c')+_linear('badge','#68d391','#25855a')+'</defs>'
        '<rect x="2.5" y="4.5" width="25" height="19" rx="3" fill="url(#ID-screen)" stroke="#0d1117" stroke-width="1.1"/>'
        '<path d="M2.5 14h25M15 4.5v19" stroke="#4a5568" stroke-width=".7"/>'
        '<path d="M5 19.5h4.5c2 0 2-10 4-10s3 5 5 5 2.5-2 4.5-2h2" fill="none" stroke="#68d391" stroke-opacity=".35" stroke-width="4" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M5 19.5h4.5c2 0 2-10 4-10s3 5 5 5 2.5-2 4.5-2h2" fill="none" stroke="#9ae6b4" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="24.5" cy="23.5" r="6.5" fill="url(#ID-badge)" stroke="#ffffff" stroke-width="1.3"/>'
        '<path d="M22.5 20.2v6.6l5.4-3.3z" fill="#ffffff"/>',
    'sparameters':'<defs>'+_radial('chart','#ffffff','#e6f2ff','#bee3f8')+'</defs>'
        '<circle cx="16" cy="16" r="12.5" fill="url(#ID-chart)" stroke="#2b6cb0" stroke-width="1.6"/>'
        '<path d="M3.5 16h25" stroke="#3182ce" stroke-width=".9"/>'
        '<circle cx="22.25" cy="16" r="6.25" fill="none" stroke="#3182ce" stroke-width=".9"/>'
        '<circle cx="19.1" cy="16" r="9.4" fill="none" stroke="#3182ce" stroke-width=".7" stroke-opacity=".7"/>'
        '<path d="M28.5 16A12.5 12.5 0 0 1 16 3.5M28.5 16A12.5 12.5 0 0 0 16 28.5" fill="none" stroke="#3182ce" stroke-width=".9"/>'
        '<path d="M23.5 8.5c-6.5 1.5-10.5 7-8.5 12s8.5 4 9.5-1.5" fill="none" stroke="#dd6b20" stroke-width="2.3" stroke-linecap="round"/>'
        '<circle cx="24.5" cy="19" r="2" fill="#dd6b20" stroke="#ffffff" stroke-width=".8"/>',
    'virtualprobe':'<defs>'+_linear('body','#fbd38d','#dd6b20',True)+'</defs>'
        '<path d="M3 26.5h26" stroke="#718096" stroke-width="2.2" stroke-linecap="round"/>'
        '<path d="M3 10c2-5.5 4-5.5 6 0s4 5.5 6 0" fill="none" stroke="#38a169" stroke-width="2.2" stroke-linecap="round"/>'
        '<g transform="rotate(35 19 13)"><rect x="15.5" y="-1" width="7" height="17" rx="3" fill="url(#ID-body)" stroke="#9c4221" stroke-width="1.1"/>'
        '<rect x="15.5" y="10.5" width="7" height="2" fill="#7b341e"/>'
        '<path d="M17 16h4l-1.5 7.5h-1z" fill="#e2e8f0" stroke="#4a5568" stroke-width=".9" stroke-linejoin="round"/></g>'
        '<circle cx="13.3" cy="26.5" r="2" fill="#f6ad55" stroke="#9c4221" stroke-width=".9"/>',
    'deembed':'<defs>'+_linear('left','#63b3ed','#2b6cb0')+_linear('right','#fed7d7','#fc8181')+'</defs>'
        '<path d="M1.5 18h2M14 18h4M28.5 18h2" stroke="#718096" stroke-width="2.2" stroke-linecap="round"/>'
        '<rect x="3.5" y="12.5" width="10.5" height="11" rx="1.6" fill="url(#ID-left)" stroke="#2c5282" stroke-width="1.2"/>'
        '<rect x="18" y="12.5" width="10.5" height="11" rx="1.6" fill="url(#ID-right)" stroke="#c53030" stroke-width="1.2" '
        'stroke-dasharray="2.6 1.6"/>'
        '<circle cx="25.5" cy="8" r="5.3" fill="#e53e3e" stroke="#ffffff" stroke-width="1.2"/>'
        '<path d="M22.8 8h5.4" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round"/>',
    'about':'<defs>'+_linear('disc','#63b3ed','#2b6cb0')+'</defs>'
        '<circle cx="16" cy="16" r="12.5" fill="url(#ID-disc)" stroke="#2c5282" stroke-width="1.2"/>'
        '<circle cx="16" cy="9.8" r="2" fill="#ffffff"/>'
        '<path d="M16 14.5v9" stroke="#ffffff" stroke-width="3.2" stroke-linecap="round"/>',
}
ALIASES={'deletePart':'delete','deleteWire':'delete'}

def HasIcon(commandId):
    return ALIASES.get(commandId,commandId) in ICONS

def Svg(commandId,size=32):
    """@return a standalone SVG document for the command's icon"""
    body=ICONS[ALIASES.get(commandId,commandId)].replace('ID-','si-'+commandId+'-')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="%d" height="%d">'%(size,size))+body+'</svg>'

def AllSvgs(ids):
    return {i:Svg(i) for i in ids if HasIcon(i)}
