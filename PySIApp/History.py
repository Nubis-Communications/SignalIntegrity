#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      peter.pupalaikis
#
# Created:     01/12/2015
# Copyright:   (c) peter.pupalaikis 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import copy

class HistoryElement(object):
    def __init__(self,eventName,schematic):
        self.eventName=eventName
        self.schematic=copy.deepcopy(schematic)

class History(object):
    def __init__(self,parent):
        self.parent=parent
        self.history=[HistoryElement('new',copy.deepcopy(self.parent.Drawing.schematic))]
        self.maxlength=100
        self.current=0
        self.FigureState()
    def Event(self,eventName):
        if self.current == -1: # nothing in history buffer
            pass
        elif self.current == len(self.history)-1: # at end of history buffer
            if len(self.history) == self.maxlength:
                self.history=self.history[1:]
                self.current=self.current-1
        else: # somewhere in the middle due to a previous undo
            self.history=self.history[:self.current+1]
            self.current=len(self.history)-1
        element=HistoryElement(eventName,self.parent.Drawing.schematic)
        self.history.append(element)
        self.current=self.current+1
        self.FigureState()
    def Undo(self):
        if self.current <= 0:
            return
        undoMessage=self.history[self.current].eventName
        self.current=self.current-1
        element=copy.deepcopy(self.history[self.current])
        self.parent.Drawing.schematic = element.schematic
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
        self.parent.Drawing.schematic = element.schematic
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
