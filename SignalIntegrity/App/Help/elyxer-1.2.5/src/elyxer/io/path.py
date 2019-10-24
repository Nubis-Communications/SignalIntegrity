#! /usr/bin/env python
# -*- coding: utf-8 -*-

#   eLyXer -- convert LyX source files to HTML output.
#
#   Copyright (C) 2009 Alex Fernández
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

# --end--
# Alex 20090905
# Path manipulations

import os
import os.path
import codecs
from elyxer.util.options import Options
from elyxer.util.trace import Trace


class Path(object):
  "Represents a generic path"

  def exists(self):
    "Check if the file exists"
    return os.path.exists(self.path)

  def open(self):
    "Open the file as readonly binary"
    return codecs.open(self.path, 'rb')

  def getmtime(self):
    "Return last modification time"
    return os.path.getmtime(self.path)

  def hasexts(self, exts):
    "Check if the file has one of the given extensions."
    for ext in exts:
      if self.hasext(ext):
        return True
    return False

  def hasext(self, ext):
    "Check if the file has the given extension"
    return self.getext() == ext

  def getext(self):
    "Get the current extension of the file."
    base, ext = os.path.splitext(self.path)
    return ext

  def __unicode__(self):
    "Return a unicode string representation"
    return self.path

  def __eq__(self, path):
    "Compare to another path"
    if not hasattr(path, 'path'):
      return False
    return self.path == path.path

class InputPath(Path):
  "Represents an input file"

  def __init__(self, url):
    "Create the input path based on url"
    self.url = url
    self.path = url
    if not os.path.isabs(url):
      self.path = os.path.join(Options.directory, url)

class OutputPath(Path):
  "Represents an output file"

  def __init__(self, inputpath):
    "Create the output path based on an input path"
    self.url = inputpath.url
    if os.path.isabs(self.url):
      self.url = os.path.basename(self.url)
    self.path = os.path.join(Options.destdirectory, self.url)
  
  def changeext(self, ext):
    "Change extension to the given one"
    base, oldext = os.path.splitext(self.path)
    self.path = base + ext
    base, oldext = os.path.splitext(self.url)
    self.url = base + ext

  def exists(self):
    "Check if the file exists"
    return os.path.exists(self.path)

  def createdirs(self):
    "Create any intermediate directories that don't exist"
    dir = os.path.dirname(self.path)
    if len(dir) > 0 and not os.path.exists(dir):
      os.makedirs(dir)

  def removebackdirs(self):
    "Remove any occurrences of ../ (or ..\ on Windows)"
    self.path = os.path.normpath(self.path)
    backdir = '..' + os.path.sep
    while self.path.startswith(backdir):
      self.path = self.path[len(backdir):]
    while self.url.startswith('../'):
      self.url = self.url[len('../'):]

