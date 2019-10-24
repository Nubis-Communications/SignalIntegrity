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
# eLyXer object cloning

from elyxer.util.trace import Trace


class Cloner(object):
  "An object used to clone other objects."

  def clone(cls, original):
    "Return an exact copy of an object."
    "The original object must have an empty constructor."
    return cls.create(original.__class__)

  def create(cls, type):
    "Create an object of a given class."
    clone = type.__new__(type)
    clone.__init__()
    return clone

  clone = classmethod(clone)
  create = classmethod(create)

class ContainerExtractor(object):
  "A class to extract certain containers."

  def __init__(self, config):
    "The config parameter is a map containing three lists: allowed, copied and extracted."
    "Each of the three is a list of class names for containers."
    "Allowed containers are included as is into the result."
    "Cloned containers are cloned and placed into the result."
    "Extracted containers are looked into."
    "All other containers are silently ignored."
    self.allowed = config['allowed']
    self.cloned = config['cloned']
    self.extracted = config['extracted']

  def extract(self, container):
    "Extract a group of selected containers from elyxer.a container."
    list = []
    locate = lambda c: c.__class__.__name__ in self.allowed + self.cloned
    recursive = lambda c: c.__class__.__name__ in self.extracted
    process = lambda c: self.process(c, list)
    container.recursivesearch(locate, recursive, process)
    return list

  def process(self, container, list):
    "Add allowed containers, clone cloned containers and add the clone."
    name = container.__class__.__name__
    if name in self.allowed:
      list.append(container)
    elif name in self.cloned:
      list.append(self.safeclone(container))
    else:
      Trace.error('Unknown container class ' + name)

  def safeclone(self, container):
    "Return a new container with contents only in a safe list, recursively."
    clone = Cloner.clone(container)
    clone.output = container.output
    clone.contents = self.extract(container)
    return clone

