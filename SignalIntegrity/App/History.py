"""
History.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
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
import copy
import SignalIntegrity.App.Project

class HistoryElement(object):
    def __init__(self,eventName,project):
        self.eventName=eventName
        self.project=copy.deepcopy(project)

class History(object):
    def __init__(self,parent):
        self.parent=parent
        self.history=[]
        self.maxlength=100
        self.current=-1
        self.FigureState()
    def Event(self,eventName):
        if SignalIntegrity.App.Project is None:
            return
        if self.current == -1: # nothing in history buffer
            pass
        elif self.current == len(self.history)-1: # at end of history buffer
            if len(self.history) == self.maxlength:
                self.history=self.history[1:]
                self.current=self.current-1
        else: # somewhere in the middle due to a previous undo
            self.history=self.history[:self.current+1]
            self.current=len(self.history)-1
        element=HistoryElement(eventName,SignalIntegrity.App.Project.Write(self.parent))
        self.history.append(element)
        self.current=self.current+1
        self.FigureState()
    def Undo(self):
        if self.current <= 0:
            return
        undoMessage=self.history[self.current].eventName
        self.current=self.current-1
        element=copy.deepcopy(self.history[self.current])
        SignalIntegrity.App.Project = element.project.Read()
        self.parent.Drawing.InitFromProject()
        self.parent.Drawing.stateMachine.state='Nothing'
        self.parent.Drawing.stateMachine.ForceIntializeState()
        self.FigureState()
        self.parent.statusbar.set('Undid: '+undoMessage)
    def Redo(self):
        if self.current == -1:
            return
        if self.current+1 == len(self.history):
            return
        self.current=self.current+1
        element=copy.deepcopy(self.history[self.current])
        SignalIntegrity.App.Project = element.project.Read()
        self.parent.Drawing.InitFromProject()
        self.parent.Drawing.stateMachine.state = 'Nothing'
        self.parent.Drawing.stateMachine.ForceIntializeState()
        self.FigureState()
        self.parent.statusbar.set('Redid: '+element.eventName)
    def FigureState(self):
        if len(self.history) <= 1:
            self.parent.UndoDoer.Activate(False)
            self.parent.RedoDoer.Activate(False)
            self.current=len(self.history)-1
        else:
            if self.current <= 0:
                self.parent.UndoDoer.Activate(False)
            else:
                self.parent.UndoDoer.Activate(True)
            if self.current+1 < len(self.history):
                self.parent.RedoDoer.Activate(True)
            else:
                self.parent.RedoDoer.Activate(False)
