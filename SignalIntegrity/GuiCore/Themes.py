"""
Themes.py
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
import glob
import json
import os
import re
import sys
import zipfile

class ThemeError(Exception):
    pass

MATPLOTLIB_COLORS=['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']

# color themes in the VS Code format, so built-in and published themes go through one mapping
BUILTIN={
    'builtin:light':{'name':'SignalIntegrity Light','type':'light','colors':{
        'editor.background':'#ffffff','editor.foreground':'#000000','foreground':'#222222',
        'sideBar.background':'#ffffff','sideBar.foreground':'#222222','panel.border':'#d0d0d0',
        'editorGroupHeader.tabsBackground':'#f3f3f3','focusBorder':'#0a64c8',
        'button.background':'#0a64c8','button.foreground':'#ffffff','input.background':'#ffffff',
        'list.activeSelectionBackground':'#e8f0fb','list.activeSelectionForeground':'#222222',
        'list.hoverBackground':'#e8f0fb','statusBar.background':'#ffffff','statusBar.foreground':'#222222',
        'textLink.foreground':'#0000ff','editorLineNumber.foreground':'#dddddd'}},
    'builtin:dark':{'name':'SignalIntegrity Dark','type':'dark','colors':{
        'editor.background':'#15191f','editor.foreground':'#d6dde6','foreground':'#cdd5df',
        'sideBar.background':'#1b2028','sideBar.foreground':'#cdd5df','panel.border':'#2e3642',
        'editorGroupHeader.tabsBackground':'#12161b','focusBorder':'#3aa0ff',
        'button.background':'#2f7fd8','button.foreground':'#ffffff','input.background':'#11151a',
        'list.activeSelectionBackground':'#26405f','list.activeSelectionForeground':'#ffffff',
        'list.hoverBackground':'#232b36','statusBar.background':'#12161b','statusBar.foreground':'#aab4c0',
        'textLink.foreground':'#4fb3ff','editorLineNumber.foreground':'#323b47',
        'terminal.ansiBlue':'#4fb3ff','terminal.ansiYellow':'#ffb454','terminal.ansiGreen':'#7fd962',
        'terminal.ansiRed':'#ff6b6b','terminal.ansiMagenta':'#d29bff','terminal.ansiCyan':'#5ce1e6'}},
}

_TRAILING_COMMA=re.compile(r',[ \t\r\n]*[}\]]')

def _StripJsonc(text):
    """removes // and /* */ comments and trailing commas outside of strings (VS Code theme files are JSONC)"""
    def scan(text,handle):
        out=[]; i=0; n=len(text); inString=False
        while i<n:
            c=text[i]
            if inString:
                out.append(c)
                if c=='\\' and i+1<n:
                    out.append(text[i+1]); i+=2; continue
                if c=='"':
                    inString=False
                i+=1; continue
            if c=='"':
                inString=True; out.append(c); i+=1; continue
            skipTo=handle(text,i)
            if skipTo is not None:
                i=skipTo; continue
            out.append(c); i+=1
        return ''.join(out)
    def comment(text,i):
        if text.startswith('//',i):
            j=text.find('\n',i); return len(text) if j<0 else j
        if text.startswith('/*',i):
            j=text.find('*/',i+2); return len(text) if j<0 else j+2
        return None
    def trailingComma(text,i):
        return i+1 if _TRAILING_COMMA.match(text,i) else None
    # comments go first so a comment between a trailing comma and the bracket doesn't hide it
    return scan(scan(text,comment),trailingComma)

def ParseJsonc(text):
    try:
        return json.loads(_StripJsonc(text.lstrip('\ufeff')))
    except ValueError as e:
        raise ThemeError('not a valid theme file: '+str(e))

class _Source(object):
    """reads files from a folder or from inside a .vsix package"""
    def __init__(self,location):
        self.vsix=location.lower().endswith('.vsix')
        self.location=location
        self.zip=zipfile.ZipFile(location) if self.vsix else None
    def Read(self,path):
        if self.vsix:
            try:
                return self.zip.read(path.replace('\\','/')).decode('utf-8-sig')
            except KeyError:
                raise ThemeError('missing '+path+' in '+self.location)
        with open(path,encoding='utf-8-sig') as f:
            return f.read()
    def Join(self,base,relative):
        if self.vsix:
            return os.path.normpath(os.path.join(os.path.dirname(base),relative)).replace('\\','/')
        return os.path.normpath(os.path.join(os.path.dirname(base),relative))

def _LoadThemeFile(source,path,depth=0):
    if depth>8:
        raise ThemeError('theme includes are nested too deeply')
    if not path.lower().endswith('.json'):
        raise ThemeError('only JSON color themes are supported: '+path)
    theme=ParseJsonc(source.Read(path))
    if not isinstance(theme,dict):
        raise ThemeError('not a color theme: '+path)
    colors={}
    include=theme.get('include')
    if isinstance(include,str):
        colors.update(_LoadThemeFile(source,source.Join(path,include),depth+1)['colors'])
    if isinstance(theme.get('colors'),dict):
        colors.update({k:v for k,v in theme['colors'].items() if isinstance(v,str)})
    return {'name':theme.get('name'),'type':theme.get('type'),'colors':colors}

def _Localize(label,nls):
    if isinstance(label,str) and label.startswith('%') and label.endswith('%'):
        value=nls.get(label[1:-1],label)
        return value.get('message',label) if isinstance(value,dict) else value
    return label

def _ExtensionThemes(source,root):
    """themes contributed by one extension: root is the folder (or 'extension' inside a .vsix)"""
    join=(lambda *p: '/'.join(p)) if source.vsix else os.path.join
    try:
        package=ParseJsonc(source.Read(join(root,'package.json')))
    except (ThemeError,OSError):
        return []
    try:
        nls=ParseJsonc(source.Read(join(root,'package.nls.json')))
    except (ThemeError,OSError):
        nls={}
    themes=[]
    for t in (package.get('contributes') or {}).get('themes') or []:
        path=t.get('path')
        if not isinstance(path,str) or not path.lower().endswith('.json'):
            continue
        full=os.path.normpath(join(root,path))
        if source.vsix:
            full=full.replace('\\','/')
        label=_Localize(t.get('label') or t.get('id') or os.path.basename(path),nls)
        uiTheme=t.get('uiTheme','vs-dark')
        themes.append({'id':(source.location+'::'+full) if source.vsix else full,
                       'label':str(label),'uiTheme':uiTheme,
                       'extension':_Localize(package.get('displayName') or package.get('name',''),nls)})
    return themes

def VSCodeExtensionFolders():
    """folders that hold installed and built-in VS Code (and compatible editor) extensions"""
    home=os.path.expanduser('~')
    folders=[os.path.join(home,d,'extensions') for d in ('.vscode','.vscode-insiders','.vscode-oss','.cursor','.windsurf')]
    apps=[]
    if sys.platform.startswith('win'):
        for base in (os.environ.get('LOCALAPPDATA',''),os.environ.get('ProgramFiles',''),os.environ.get('ProgramFiles(x86)','')):
            if base:
                apps+=glob.glob(os.path.join(base,'Programs','Microsoft VS Code*'))+glob.glob(os.path.join(base,'Microsoft VS Code*'))
    elif sys.platform=='darwin':
        apps+=glob.glob('/Applications/Visual Studio Code*.app/Contents/Resources')
    else:
        apps+=['/usr/share/code','/usr/share/code-insiders','/opt/visual-studio-code','/snap/code/current/usr/share/code']
    for app in apps:
        # newer Windows installs keep resources under a commit-hash folder
        folders+=glob.glob(os.path.join(app,'resources','app','extensions'))+glob.glob(os.path.join(app,'*','resources','app','extensions'))
        folders+=glob.glob(os.path.join(app,'app','extensions'))
    return [f for f in dict.fromkeys(folders) if os.path.isdir(f)]

def DiscoverThemes(folders=None):
    """@return built-in themes followed by every JSON color theme of installed VS Code extensions"""
    themes=[{'id':k,'label':v['name'],'uiTheme':'vs' if v['type']=='light' else 'vs-dark','extension':'SignalIntegrity'}
            for k,v in BUILTIN.items()]
    seen=set()
    for folder in VSCodeExtensionFolders() if folders is None else folders:
        try:
            names=sorted(os.listdir(folder))
        except OSError:
            continue
        for name in names:
            root=os.path.join(folder,name)
            if os.path.isdir(root):
                for t in _ExtensionThemes(_Source(root),root):
                    key=(t['label'],t['extension'])
                    if key not in seen:
                        seen.add(key); themes.append(t)
    return themes

def ThemesInPackage(location):
    """themes in a .vsix file or an extension folder"""
    if location.lower().endswith('.vsix'):
        source=_Source(location)
        return _ExtensionThemes(source,'extension')
    return _ExtensionThemes(_Source(location),location)

def LoadTheme(themeId):
    """loads a built-in theme, a theme JSON file, an extension folder or .vsix (first theme),
    or a 'package.vsix::extension/themes/x.json' id
    @return (name, palette dict)"""
    if themeId in BUILTIN:
        theme=dict(BUILTIN[themeId])
    else:
        location,inner=(themeId.split('::',1)+[None])[:2]
        if not os.path.exists(location):
            raise ThemeError('theme not found: '+location)
        if inner is None and (os.path.isdir(location) or location.lower().endswith('.vsix')):
            themes=ThemesInPackage(location)
            if not themes:
                raise ThemeError('no JSON color themes in '+location)
            return LoadTheme(themes[0]['id'])
        source=_Source(location)
        theme=_LoadThemeFile(source,inner if inner is not None else location)
        if not theme.get('name'):
            theme['name']=os.path.splitext(os.path.basename(inner or location))[0]
    return theme['name'],Palette(theme)

# ---- color handling
def _Rgb(value):
    if not isinstance(value,str):
        return None
    m=re.fullmatch(r'#([0-9a-fA-F]{3,8})',value.strip())
    if not m:
        return None
    h=m.group(1)
    if len(h) in (3,4):
        h=''.join(c*2 for c in h)
    if len(h) not in (6,8):
        return None
    rgb=tuple(int(h[i:i+2],16) for i in (0,2,4))
    alpha=int(h[6:8],16)/255. if len(h)==8 else 1.
    return rgb,alpha

def _Hex(rgb):
    return '#%02x%02x%02x'%tuple(max(0,min(255,int(round(c)))) for c in rgb)

def _Blend(color,under,alpha):
    return tuple(c*alpha+u*(1-alpha) for c,u in zip(color,under))

def _Luminance(rgb):
    def channel(c):
        c=c/255.
        return c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    r,g,b=(channel(c) for c in rgb)
    return 0.2126*r+0.7152*g+0.0722*b

def _Contrast(a,b):
    la,lb=sorted((_Luminance(a),_Luminance(b)),reverse=True)
    return (la+0.05)/(lb+0.05)

def Palette(theme):
    """maps VS Code theme colors to the colors the SignalIntegrity GUIs use"""
    dark=(theme.get('type') or 'dark') not in ('light','hcLight')
    colors=theme.get('colors') or {}
    base=BUILTIN['builtin:dark' if dark else 'builtin:light']['colors']
    background=_Rgb(colors.get('editor.background') or base['editor.background'])[0]
    def pick(*keys,under=None):
        under=background if under is None else under
        for key in keys:
            parsed=_Rgb(colors.get(key))
            if parsed is not None:
                rgb,alpha=parsed
                return _Blend(rgb,under,alpha)
        for key in keys:
            parsed=_Rgb(base.get(key))
            if parsed is not None:
                return parsed[0]
        return None
    foreground=pick('editor.foreground','foreground')
    panel=pick('sideBar.background','panel.background','editor.background')
    palette={
        'dark':dark,
        'background':background,
        'foreground':foreground,
        'panel':panel,
        'panelForeground':pick('sideBar.foreground','foreground','editor.foreground',under=panel),
        'toolbar':pick('editorGroupHeader.tabsBackground','titleBar.activeBackground','sideBar.background'),
        'border':pick('panel.border','sideBar.border','editorGroup.border','contrastBorder','editorLineNumber.foreground'),
        'accent':pick('focusBorder','button.background','textLink.foreground'),
        'buttonBackground':pick('button.background','focusBorder'),
        'buttonForeground':pick('button.foreground'),
        'inputBackground':pick('input.background','editor.background'),
        'inputForeground':pick('input.foreground','editor.foreground','foreground'),
        'selection':pick('list.activeSelectionBackground','editor.selectionBackground'),
        'selectionForeground':pick('list.activeSelectionForeground','foreground'),
        'hover':pick('list.hoverBackground','list.activeSelectionBackground'),
        'statusBar':pick('statusBar.background','sideBar.background'),
        'statusBarForeground':pick('statusBar.foreground','foreground'),
        'grid':pick('editorLineNumber.foreground','editorIndentGuide.background'),
    }
    # schematic ink and selection must stay readable on the drawing background
    ink=foreground
    selected=pick('textLink.foreground','focusBorder','button.background')
    if _Contrast(selected,background)<3.:
        selected=(64,160,255) if dark else (0,0,255)
    palette['schematicBackground']=background
    palette['schematicInk']=ink
    palette['schematicSelected']=selected
    palette['schematicDisabled']=pick('editorWarning.foreground','errorForeground') if dark else (250,128,114)
    if not dark:
        palette['grid']=_Blend(palette['grid'],background,0.6) if _Contrast(palette['grid'],background)>2. else palette['grid']
    traces=[]
    for key in ('terminal.ansiBlue','terminal.ansiYellow','terminal.ansiGreen','terminal.ansiRed','terminal.ansiMagenta',
                'terminal.ansiCyan','terminal.ansiBrightBlue','terminal.ansiBrightYellow','terminal.ansiBrightGreen','terminal.ansiBrightRed'):
        parsed=_Rgb(colors.get(key))
        if parsed is not None and _Contrast(parsed[0],background)>=2.:
            traces.append(_Hex(parsed[0]))
    if len(dict.fromkeys(traces))<4:
        traces=MATPLOTLIB_COLORS if not dark else ['#4fb3ff','#ffb454','#7fd962','#ff6b6b','#d29bff','#5ce1e6','#f78fb3','#c0c0c0','#e6db74','#66d9ef']
    result={k:(_Hex(v) if isinstance(v,tuple) else v) for k,v in palette.items()}
    result['traces']=list(dict.fromkeys(traces))
    return result

# ---- the theme the user picked, shared by both GUIs
def SettingsFile():
    from SignalIntegrity.GuiCore.Settings import SettingsDirectory
    return os.path.join(SettingsDirectory(),'gui-theme.json')

def SavedThemeId():
    try:
        with open(SettingsFile()) as f:
            value=json.load(f).get('theme')
        return value if isinstance(value,str) else 'builtin:light'
    except (OSError,ValueError,AttributeError):
        return 'builtin:light'

def SaveThemeId(themeId):
    path=SettingsFile()
    os.makedirs(os.path.dirname(path),exist_ok=True)
    with open(path,'w') as f:
        json.dump({'theme':themeId},f)

def CurrentTheme():
    """@return (id,name,palette) of the saved theme, falling back to the light theme"""
    themeId=SavedThemeId()
    try:
        name,palette=LoadTheme(themeId)
    except (ThemeError,OSError):
        themeId='builtin:light'
        name,palette=LoadTheme(themeId)
    return themeId,name,palette

def SchematicColorMap(palette):
    """maps the tk part-picture colors to theme colors"""
    return {'black':palette['schematicInk'],'blue':palette['schematicSelected'],
            'salmon':palette['schematicDisabled'],'white':palette['schematicBackground']}
