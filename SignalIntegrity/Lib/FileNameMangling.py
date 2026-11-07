"""
FileNameMangling.py

A mangled file name allows a file that cannot be reached through a relative path
(for example, a file on another drive) to be archived alongside the project that
references it.  The mangled name encodes the original absolute path, so the
project file itself is left untouched and continues to reference the absolute
path; the mangled copy is found at reference time instead.
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
import re

#: character that introduces and separates the elements of a mangled file name
FileNameMangleSeparator='#'

#: only s-parameter file names ('.s1p', '.S12P', ...) are mangled, for now
MangleableExtensionPattern=re.compile(r'^\.s\d+p$',re.IGNORECASE)

def MangleableFileName(path):
    """Whether a file name is eligible for mangling.
    @param path string the path to examine.
    @return bool True if the extension is '.sXp', where X is a number.
    """
    if path is None:
        return False
    return MangleableExtensionPattern.match(os.path.splitext(str(path))[1]) is not None

def MangledFileName(path):
    """Produces the mangled file name for a path.
    @param path string the path to mangle.
    @return string the mangled file name (a bare file name, with no directory), or
    an empty string if the path is not eligible for mangling.
    @remark The path is made absolute, the ':' after a drive letter is dropped
    and the drive letter is lowercased (paths are case-insensitive on the systems
    that have drive letters, so this keeps the name stable), and every path
    separator becomes the separator character, which also introduces the name.
    'z:/t4_ic_files/foo.s3p' therefore becomes '#z#t4_ic_files#foo.s3p'.  The
    extension survives as the last '.' separated element, so the port count it
    carries can still be read from it.
    """
    if not MangleableFileName(path):
        return ''
    path=str(path)
    if path=='':
        return ''
    path=os.path.abspath(path).replace('\\','/')
    drive,rest=os.path.splitdrive(path)
    if drive.endswith(':'):
        drive=drive[:-1].lower()
    path=(drive+rest).replace('\\','/')
    return FileNameMangleSeparator+FileNameMangleSeparator.join(path.split('/'))

def IsMangledFileName(name):
    """Whether a file name is a mangled file name.
    @param name string the file name to examine.
    @return bool True if the name is a mangled file name.
    """
    if name is None:
        return False
    return os.path.basename(str(name).replace('\\','/')).startswith(FileNameMangleSeparator)

def ResolveFileName(name,searchDir=None):
    """Resolves a file name, preferring a mangled copy in the project directory.
    @param name string the file name referenced.
    @param searchDir string (optional, defaults to the current directory) the
    directory of the project making the reference.
    @return string the mangled copy if one exists, otherwise the name unchanged.
    @remark Only absolute names eligible for mangling are resolved; a relative name
    already refers to something reachable from the project.  The lookup is
    unconditional - whenever a mangled copy is present it is used in preference to
    the absolute path, which is what makes an extracted archive calculate
    identically on a machine that cannot reach the original location.
    """
    if name is None:
        return name
    name=str(name)
    if name=='' or not os.path.isabs(name):
        return name
    if searchDir is None:
        searchDir=os.getcwd()
    mangledName=MangledFileName(name)
    if mangledName=='':
        return name
    mangledPath=os.path.join(searchDir,mangledName)
    if os.path.exists(mangledPath):
        return mangledPath
    # the mangled name is derived from a path whose case may not match the case
    # the copy was made under, so a case insensitive match is accepted as well
    try:
        entries=os.listdir(searchDir)
    except OSError:
        return name
    mangledNameLower=mangledName.lower()
    for entry in entries:
        if entry.lower()==mangledNameLower:
            return os.path.join(searchDir,entry)
    return name
