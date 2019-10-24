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
# Alex 20091226
# Port a Java program to a Python equivalent. Used to port MathToWeb.

from elyxer.jtp.parser import *
from elyxer.jtp.grammar import *
from elyxer.util.trace import Trace


class JavaPorter(object):
  "Ports a Java file."

  def __init__(self):
    Grammar.instance.process()
    self.chooser = StatementChooser()

  def topy(self, filepos, writer):
    "Port the Java input file to Python."
    tok = Tokenizer(filepos)
    Grammar.instance.parse(tok)
    return
    while not tok.finished():
      statement = self.nextstatement(tok)
      writer.writeline(statement)
    writer.close()

  def nextstatement(self, tok):
    "Return the next statement."
    statement = None
    while not statement and not tok.finished():
      indent = self.chooser.getindent(tok)
      statement = self.parsestatement(tok)
    if not statement:
      return ''
    Trace.debug('Statement: ' + statement.strip())
    if statement.startswith('\n'):
      # displace newline
      return '\n' + indent + statement[1:]
    return indent + statement

  def parsestatement(self, tok):
    "Parse a single statement."
    pending = self.chooser.pendingstatement(tok)
    if pending:
      return pending
    return self.chooser.choose(tok)

class StatementChooser(object):
  "Chooses the next statement to parse, according to the first token."

  starttokens = {
      'if':'conditionblock', 'catch':'parametersblock', 'import':'ignorestatement',
      'public':'classormember', 'protected':'classormember', 'private':'classormember',
      'class':'parseclass', 'else':'elseblock', 'try':'tryblock',
      'return':'returnstatement', '{':'openblock', '}':'closeblock',
      'for':'forparens0', 'throw':'throwstatement', 'throws':'throwsdeclaration',
      ';':'ignorestatement', 'while':'conditionblock'
      }
  javatokens = {
      'new':'createstatement', 'this':'thisstatement'
      }

  def __init__(self):
    self.parser = StatementParser(self)

  def getindent(self, tok):
    "Get the indent for the next statement."
    return '  ' * tok.depth

  def choose(self, tok):
    "Parse a single statement."
    token = tok.next()
    if not token:
      return None
    if token in self.starttokens:
      function = getattr(self, self.starttokens[token])
    elif token in self.javatokens:
      function = getattr(self, self.javatokens[token])
    else:
      function = self.assigninvoke
    return function(tok)

  def pendingstatement(self, tok):
    "Return any pending statement from elyxer.before."
    if tok.infor != 0:
      tok.next()
      function = getattr(self, 'forparens' + unicode(tok.infor))
      return function(tok)
    if len(tok.autoincreases) != 0:
      return self.autoincrease(tok)
    if len(tok.autodecreases) != 0:
      return self.autodecrease(tok)
    return None

  def autoincrease(self, tok):
    "Process a Java autoincrease (++)."
    variable = tok.autoincreases.pop()
    return variable + ' += 1'
    
  def autodecrease(self, tok):
    "Process a Java autodecrease (--)."
    variable = tok.autodecreases.pop()
    return variable + ' -= 1'

  def classormember(self, tok):
    "Parse a class or member (attribute or method)."
    if tok.inclass:
      return self.parser.translateinternal(tok)
    else:
      return self.parser.translateclass(tok)

  def conditionblock(self, tok):
    "Parse a condition in () and then a block {} (if or while statements)."
    token = tok.current()
    tok.checknext('(')
    parens = self.parser.parsecondition(tok, ')')
    self.parser.expectblock(tok)
    return token + ' ' + parens + ':'

  def parametersblock(self, tok):
    "Parse a parameters () and then a block {} (catch statement)."
    tok.checknext('(')
    parens = self.parser.listparameters(tok)
    self.parser.expectblock(tok)
    return 'except:'

  def forparens0(self, tok):
    "Parse the first statement of a for loop."
    "The remaining parts of the for(;;){} are parsed later."
    tok.checknext('(')
    first = self.assigninvoke(tok, tok.next())
    tok.infor = 1
    return first

  def forparens1(self, tok):
    "Read the condition in a for loop."
    condition = tok.current() + ' ' + self.parser.parseupto(';', tok)
    tok.depth += 1
    tok.infor = 2
    return 'while ' + condition + ':'
  
  def forparens2(self, tok):
    "Read the repeating statement in a for loop."
    statement = tok.current() + ' ' + self.parser.parseupto(')', tok)
    tok.depth -= 1
    tok.infor = 0
    self.parser.expectblock(tok)
    return statement

  def tryblock(self, tok):
    "Parse a block after a try."
    self.parser.expectblock(tok)
    return tok.current() + ':'

  def elseblock(self, tok):
    "Parse a block after an else."
    self.parser.expectblock(tok)
    if tok.peek() == 'if':
      tok.next()
      self.closeblock(tok)
      return 'el' + self.conditionblock(tok)
    return 'else:'

  def openblock(self, tok):
    "Open a block of code."
    if tok.waitingforblock:
      tok.waitingforblock = False
    else:
      tok.depth += 1
    if tok.peek() == '}':
      return 'pass'
    return None

  def closeblock(self, tok):
    "Close a block of code."
    tok.depth -= 1
    return None

  def returnstatement(self, tok):
    "A statement that contains a value (a return statement)."
    self.onelineblock(tok)
    return 'return ' + self.parser.parsevalue(tok)

  def throwstatement(self, tok):
    "A statement to throw (raise) an exception."
    exception = tok.next()
    if exception == 'new':
      return 'raise ' + self.createstatement(tok)
    token = tok.next()
    if token == ';':
      return 'raise ' + exception
    Trace.error('Invalid throw statement: "throw ' + exception + ' ' + token + '"')
    return 'raise ' + exception

  def throwsdeclaration(self, tok):
    "A throws clause, should be ignored."
    name = tok.next()
    return ''

  def assigninvoke(self, tok, token = None):
    "An assignment or a method invocation."
    self.onelineblock(tok)
    if not token:
      token = tok.current()
    token2 = tok.next()
    if token2 == '=':
      # assignment
      return token + ' = ' + self.parser.parsevalue(tok)
    if token2 == '.':
      member = tok.next()
      return self.assigninvoke(tok, token + '.' + member)
    if token2 == '(':
      parameters = self.parser.parseparameters(tok)
      Trace.debug('Parameters: ' + parameters)
      return self.assigninvoke(tok, token + parameters)
    if token2 == '[':
      square = self.parser.parseinsquare(tok)
      return self.assigninvoke(tok, token + square)
    if token2 == '{':
      # ignore anonymous class
      self.parser.parseupto('}', tok)
      return token
    if token2 == '++':
      Trace.debug('Increasing invoked ' + token)
      tok.autoincreases.append(token)
      return self.assigninvoke(tok, token + ' + 1')
    if token2 == '--':
      Trace.debug('Decreasing invoked ' + token)
      tok.autodecreases.append(token)
      return self.assigninvoke(tok, token + ' - 1')
    if token2 in [';', ',', ')']:
      # finished invocation
      return token
    if token2 in tok.javasymbols:
      Trace.error('Unknown symbol ' + token2 + ' for ' + token)
      return '*error ' + token + ' ' + token2 + ' error*'
    token3 = tok.next()
    if token3 == ';':
      # a declaration; ignore
      return ''
    if token3 == '=':
      # declaration + assignment
      tok.variables.append(token2)
      return token2 + ' = ' + self.parser.parsevalue(tok)
    if token3 == '[':
      # array declaration
      self.parser.parseupto(']', tok)
      return self.assigninvoke(tok, token2)
    Trace.error('Unknown combination ' + token + '+' + token2 + '+' + token3)
    return '*error ' + token + ' ' + token2 + ' ' + token + ' error*'

  def onelineblock(self, tok):
    "Check if a block was expected."
    if tok.waitingforblock:
      tok.waitingforblock = False
      tok.depth -= 1

  def ignorestatement(self, tok):
    "Ignore a whole statement."
    while tok.current() != ';':
      tok.next()
    return None

  def createstatement(self, tok):
    "A statement to create an object and use it: new Class().do()."
    tok.next()
    return self.parser.parseinvocation(tok)

  def thisstatement(self, tok):
    "A statement starting with this, which translates to self."
    return self.assigninvoke(tok, 'self')


