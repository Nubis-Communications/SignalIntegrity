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
# Alex 20090324
# eLyXer postprocessor code


class Postprocessor(object):
  "Postprocess a container keeping some context"

  stages = []

  def __init__(self):
    self.stages = StageDict(Postprocessor.stages, self)
    self.current = None
    self.last = None

  def postprocess(self, next):
    "Postprocess a container and its contents."
    self.postrecursive(self.current)
    result = self.postcurrent(next)
    self.last = self.current
    self.current = next
    return result

  def postrecursive(self, container):
    "Postprocess the container contents recursively"
    if not hasattr(container, 'contents'):
      return
    if len(container.contents) == 0:
      return
    if hasattr(container, 'postprocess'):
      if not container.postprocess:
        return
    postprocessor = Postprocessor()
    contents = []
    for element in container.contents:
      post = postprocessor.postprocess(element)
      if post:
        contents.append(post)
    # two rounds to empty the pipeline
    for i in range(2):
      post = postprocessor.postprocess(None)
      if post:
        contents.append(post)
    container.contents = contents

  def postcurrent(self, next):
    "Postprocess the current element taking into account next and last."
    stage = self.stages.getstage(self.current)
    if not stage:
      return self.current
    return stage.postprocess(self.last, self.current, next)

class StageDict(object):
  "A dictionary of stages corresponding to classes"

  def __init__(self, classes, postprocessor):
    "Instantiate an element from elyxer.each class and store as a dictionary"
    instances = self.instantiate(classes, postprocessor)
    self.stagedict = dict([(x.processedclass, x) for x in instances])

  def instantiate(self, classes, postprocessor):
    "Instantiate an element from elyxer.each class"
    stages = [x.__new__(x) for x in classes]
    for element in stages:
      element.__init__()
      element.postprocessor = postprocessor
    return stages

  def getstage(self, element):
    "Get the stage for a given element, if the type is in the dict"
    if not element.__class__ in self.stagedict:
      return None
    return self.stagedict[element.__class__]

