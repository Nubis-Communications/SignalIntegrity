"""
BuildHelpSystem.py
"""

# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# Copyright (c) 2021-2025 Nubis Communications, Inc.
# Copyright (c) 2026 Ciena, Inc.
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
import re

from urllib.request import urlopen
from urllib.request import pathname2url

import SignalIntegrity.App.Project

class HelpSystemKeys(object):
    controlHelpUrlBase=None
    keydict={}
    # Sub-path (relative to the App install directory / online URL base) where the
    # built MkDocs help site lives.  This replaces the old eLyXer output folder
    # 'Help/Help.html.LyXconv/'.
    helpSiteSubPath='Help/site/'
    # Relative path (from a help site page) to the Doxygen software documentation.
    # The help site lives two levels below the App base (Help/site/), which is the
    # same depth the old eLyXer output used, so this relative path is unchanged.
    softwareDocumentationRelPath='../../Doc/xhtml/index.xhtml'
    # Label prefixes that identify context-help anchors within the help pages.
    labelPrefixes=('sec:','sub:','Control-Help:','device:','par:','pc:')
    @staticmethod
    def InstallHelpURLBase(useOnlineHelp,urlBase):
        if useOnlineHelp:
            HelpSystemKeys.controlHelpUrlBase=urlBase+'/'
        else:
            # Build a proper file: URI from the local install directory.  Simply
            # prepending 'file://' to a Windows path (e.g. 'C:\\Users\\...\\App/')
            # produces an invalid URL that urlopen cannot open.  pathname2url
            # handles the drive letter, path separators and escaping correctly on
            # every platform.
            HelpSystemKeys.controlHelpUrlBase='file:'+pathname2url(SignalIntegrity.App.InstallDir)
        HelpSystemKeys.keydict={}
    def __init__(self,force=False):
        HelpSystemKeys.controlHelpUrlBase=None
        HelpSystemKeys.keydict={}
    def Read(self,force=False):
        self.keydict={}
        self.keydict['SoftwareDocumentation']=self.softwareDocumentationRelPath
        if force:
            raise ValueError
        try:
            lines = urlopen(self.controlHelpUrlBase+self.helpSiteSubPath+'helpkeys')
        except:
            return
        for line in lines:
            line=line.decode('ascii')
            tokens=line.strip().split(' >>> ')
            if len(tokens)==2:
                self.keydict[tokens[0]]=tokens[1]
    def SaveToFile(self):
        try:
            with open('helpkeys','w') as f:
                for key in self.keydict:
                    f.write(str(key)+' >>> '+str(self.keydict[key])+'\n')
        except:
            return
    def Open(self,helpString):
        if helpString is None or self.controlHelpUrlBase is None:
            return
        url=self[helpString]
        if not url is None:
            url = self.controlHelpUrlBase+self.helpSiteSubPath+url
            url=url.replace('\\','/')
            HelpSystemKeys._OpenUrl(url)
    @staticmethod
    def _OpenUrl(url):
        # Open a help URL in the user's default web browser, preserving any
        # '#fragment' (the context-help anchor).
        #
        # On Windows webbrowser.open() delegates to os.startfile() ->
        # ShellExecute, which converts a 'file:' URL to a bare filesystem path
        # and DISCARDS the '#fragment'.  The browser then opens at the top of the
        # page instead of the referenced section/subsection.  To avoid this we
        # launch the default browser directly with the full URL as a single
        # command-line argument (argv is not path-converted, so the fragment
        # survives).  Any failure falls back to the standard webbrowser.open().
        import webbrowser
        import sys
        if sys.platform.startswith('win') and '#' in url:
            try:
                argv=HelpSystemKeys._WindowsDefaultBrowserArgv()
                if argv:
                    import subprocess
                    subprocess.Popen(argv+[url])
                    return
            except Exception:
                pass
        webbrowser.open(url)
    @staticmethod
    def _WindowsDefaultBrowserArgv():
        # Return the default browser launch command (as an argv prefix, ready to
        # have the URL appended) by reading the Windows registry.  Returns None if
        # it cannot be determined.
        import winreg
        import shlex
        progid=None
        for scheme in ('https','http'):
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r'Software\Microsoft\Windows\Shell\Associations'
                        r'\UrlAssociations\%s\UserChoice'%scheme) as key:
                    progid,_=winreg.QueryValueEx(key,'ProgId')
                if progid:
                    break
            except OSError:
                continue
        if not progid:
            return None
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,
                    r'%s\shell\open\command'%progid) as key:
                command,_=winreg.QueryValueEx(key,None)
        except OSError:
            return None
        if not command:
            return None
        # e.g. '"C:\\...\\msedge.exe" --single-argument %1'.  Drop the '%1'/'%L'
        # placeholder (the URL is appended by the caller); keep any switches such
        # as '--single-argument' that tell the browser the next token is the URL.
        parts=shlex.split(command,posix=False)
        argv=[]
        for part in parts:
            token=part.strip('"')
            low=token.lower()
            if '%1' in low or '%l' in low or '%u' in low:
                continue
            argv.append(token)
        return argv if argv else None
    def Build(self):
        # Regenerate the key dictionary by scanning the locally built MkDocs help
        # site for anchor ids.  The site is expected under <InstallDir>/Help/site.
        self.keydict={}
        self.keydict['SoftwareDocumentation']=self.softwareDocumentationRelPath
        siteDir=os.path.join(SignalIntegrity.App.InstallDir,'Help','site')
        self.keydict.update(HelpSystemKeys.ScanSiteForKeys(siteDir))
    @staticmethod
    def ScanSiteForKeys(siteDir):
        # Walk a built MkDocs site directory and map every context-help anchor id
        # (i.e. any element id beginning with one of labelPrefixes) to its
        # 'relative/page.html#id' location.  Returns a dictionary of key -> value.
        keydict={}
        idre=re.compile(r'id="([^"]+)"')
        for root,_dirs,files in os.walk(siteDir):
            for name in files:
                if not name.endswith('.html'):
                    continue
                filepath=os.path.join(root,name)
                rel=os.path.relpath(filepath,siteDir).replace('\\','/')
                try:
                    with open(filepath,'r',encoding='utf-8') as f:
                        content=f.read()
                except:
                    continue
                for anchorId in idre.findall(content):
                    if anchorId.startswith(HelpSystemKeys.labelPrefixes) \
                            and anchorId not in keydict:
                        keydict[anchorId]=rel+'#'+anchorId
        return keydict
    def KeyValue(self,key):
        if key in self.keydict:
            return self.keydict[key]
        else:
            return None
    def __getitem__(self,item):
        if self.keydict == {}:
            self.Read()
        return self.KeyValue(item)
