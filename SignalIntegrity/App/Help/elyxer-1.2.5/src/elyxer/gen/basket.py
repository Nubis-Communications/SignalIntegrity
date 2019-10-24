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
# Alex 20091101
# eLyXer output baskets
# http://www.nongnu.org/elyxer/


from elyxer.util.options import *
from elyxer.util.clone import *
from elyxer.gen.toc import *


class Basket(object):
  "A basket to place a set of containers. Can write them, store them..."

  def setwriter(self, writer):
    self.writer = writer
    return self

class WriterBasket(Basket):
  "A writer of containers. Just writes them out to a writer."

  def write(self, container):
    "Write a container to the line writer."
    self.writer.write(container.gethtml())

  def finish(self):
    "Mark as finished."
    self.writer.close()

class KeeperBasket(Basket):
  "Keeps all containers stored."

  def __init__(self):
    self.contents = []

  def write(self, container):
    "Keep the container."
    self.contents.append(container)

  def finish(self):
    "Finish the basket by flushing to disk."
    self.flush()

  def flush(self):
    "Flush the contents to the writer."
    for container in self.contents:
      self.writer.write(container.gethtml())
    self.writer.close()

class TOCBasket(Basket):
  "A basket to place the TOC of a document."

  def __init__(self):
    self.converter = TOCConverter()

  def setwriter(self, writer):
    Basket.setwriter(self, writer)
    Options.nocopy = True
    self.writer.write(LyXHeader().gethtml())
    return self

  def write(self, container):
    "Write the table of contents for a container."
    entry = self.converter.convertindented(container)
    if entry:
      self.writer.write(entry.gethtml())

  def finish(self):
    "Mark as finished."
    self.writer.write(LyXFooter().gethtml())
    self.writer.close()

