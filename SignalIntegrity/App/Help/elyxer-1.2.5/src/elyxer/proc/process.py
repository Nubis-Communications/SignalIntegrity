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
# Alex 20100714
# eLyXer: internal processing code


from elyxer.util.trace import *
from elyxer.gen.header import *
from elyxer.ref.index import *
from elyxer.gen.layout import *
from elyxer.proc.postprocess import *


class Processor(object):
  "Process a container and its contents."

  prestages = []
  skipfiltered = ['LyXHeader', 'LyXFooter', 'Title', 'Author', 'TableOfContents']

  def __init__(self, filtering):
    "Set filtering mode (to skip postprocessing)."
    "With filtering on, the classes in skipfiltered are not processed at all."
    self.filtering = filtering
    self.postprocessor = Postprocessor()

  def process(self, container):
    "Do the whole processing on a container."
    if self.filtering and container.__class__.__name__ in self.skipfiltered:
      return None
    container = self.preprocess(container)
    self.processcontainer(container)
    if not container:
      # do not postprocess empty containers from elyxer.here
      return container
    return self.postprocess(container)

  def preprocess(self, root):
    "Preprocess a root container with all prestages."
    if not root:
      return None
    for stage in self.prestages:
      root = stage.preprocess(root)
      if not root:
        return None
    return root

  def processcontainer(self, container):
    "Process a container and its contents, recursively."
    if not container:
      return
    for element in container.contents:
      self.processcontainer(element)
    container.process()

  def postprocess(self, container):
    "Postprocess a container, unless filtering is on."
    if self.filtering:
      return container
    return self.postprocessor.postprocess(container)

