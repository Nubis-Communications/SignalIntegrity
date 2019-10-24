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

from elyxer.util.trace import Trace


class StatementParser(object):
  "A parser for a statement."

  def __init__(self, chooser):
    self.chooser = chooser

  def checkvariable(self, token):
    "Check if the token is a valid variable name."
    for char in token:
      if not Tokenizer.isalphanumeric(char):
        return False
    return True

  def autoincrease(self, tok):
    "Process a Java autoincrease (++)."
    variable = tok.autoincreases.pop()
    return variable + ' += 1'

  def autodecrease(self, tok):
    "Process a Java autodecrease (--)."
    variable = tok.autodecreases.pop()
    return variable + ' -= 1'

  def translateclass(self, tok):
    "Translate a class definition."
    tok.checknext('class')
    name = tok.next()
    tok.inclass = name
    inheritance = ''
    while tok.peek() != '{':
      inheritance += ' ' + tok.next()
    Trace.error('Unused inheritance ' + inheritance)
    return 'class ' + name + '(object):'

  def translateinternal(self, tok):
    "Translate an internal element (attribute or method)."
    token = self.membertoken(tok)
    name = self.membertoken(tok)
    if token == tok.inclass and name == '(':
      # constructor
      return self.translatemethod(token, tok)
    after = tok.next()
    while after == '[':
      tok.checknext(']')
      after = tok.next()
    if after == ';':
      return self.translateemptyattribute(name)
    if after == '(':
      return self.translatemethod(name, tok)
    if after != '=':
      Trace.error('Weird token after member: ' + token + ' ' + name + ' ' + after)
    return self.translateattribute(name, tok)

  def membertoken(self, tok):
    "Get the next member token, excluding static, []..."
    token = tok.next()
    if token in ['static', 'synchronized', 'final']:
      return self.membertoken(tok)
    if token == '[':
      tok.checknext(']')
      return self.membertoken(tok)
    return token

  def translatemethod(self, name, tok):
    "Translate a class method."
    tok.inmethod = name
    pars = self.listparameters(tok)
    self.expectblock(tok)
    parlist = ', '
    for par in pars:
      if not ' ' in par:
        Trace.error('Invalid parameter declaration: ' + par)
      else:
        newpar = par.strip().split(' ', 1)[1]
        parlist += newpar + ', '
    parlist = parlist[:-2]
    return '\ndef ' + name + '(self' + parlist + '):'

  def translateemptyattribute(self, name):
    "Translate an empty attribute definition."
    return name + ' = None'

  def translateattribute(self, name, tok):
    "Translate a class attribute."
    return name + ' = ' + self.parseupto(';', tok)

  def listparameters(self, tok):
    "Parse the parameters of a method definition, return them as a list."
    params = self.parseinparens(tok)[1:-1]
    pars = params.split(',')
    if pars[0] == '':
      return []
    return pars

  def processtoken(self, tok):
    "Process a single token."
    token = tok.current()
    if token in self.chooser.javatokens:
      function = getattr(self.chooser, self.chooser.javatokens[token])
      return function(tok)
    if token in tok.javasymbols:
      return self.processsymbol(tok)
    return token
  
  def processsymbol(self, tok):
    "Process a single java symbol."
    if tok.current() == '"' or tok.current() == '\'':
      return self.parsequoted(tok.current(), tok)
    if tok.current() == '{':
      return '{' + self.parseupto('}', tok) + '}'
    if tok.current() == '}':
      Trace.error('Erroneously closing }')
      return ''
    if tok.current() == '(':
      result = self.parseinparens(tok)
      return result
    if tok.current() == '[':
      result = self.parseinsquare(tok)
      return result
    if tok.current() == ')':
      Trace.error('Erroneously closing )')
      return ')'
    if tok.current() in tok.modified:
      return tok.modified[tok.current()]
    return tok.current()

  def parsequoted(self, quote, tok):
    "Parse a quoted sentence, with variable quotes."
    result = tok.current() + tok.pos.globincluding(quote)
    while result.endswith('\\' + quote) and not result.endswith('\\\\' + quote):
      result += tok.pos.globincluding(quote)
    return result

  def parseparameters(self, tok):
    "Parse the parameters to a method invocation."
    result = '('
    while tok.current() != ')':
      param = self.parsevalue(tok, [',',')'])
      result += param + ', '
    if len(result) == 1:
      return '()'
    return result[:-2] + ')'

  def parseparens(self, tok):
    "Parse a couple of () and the contents inside."
    tok.checknext('(')
    return self.parseinparens(tok)

  def parseinparens(self, tok):
    "Parse the contents inside ()."
    contents = self.parseupto(')', tok)
    if '{' in contents:
      # anonymous function; ignore
      return '()'
    if Tokenizer.isalphanumeric(contents):
      if Tokenizer.isalphanumeric(tok.peek()):
        # type cast; ignore
        return ''
    result = '(' + contents + ')'
    return result
    result = self.parseinbrackets('(', ')', tok)

  def parseinsquare(self, tok):
    "Parse the contents inside []."
    return self.parseinbrackets('[', ']', tok)

  def parseinbrackets(self, opening, closing, tok):
    "Parse the contents in any kind of brackets."
    result = self.parseupto(closing, tok)
    return opening + result + closing

  def parsecondition(self, tok, ending):
    "Parse a condition given the ending token."
    return self.parseupto(ending, tok)

  def parsevalue(self, tok, endings = [';']):
    "Parse a value (to be assigned or returned)."
    return self.parsetoendings(tok, endings)

  def parseinvocation(self, tok, previous = None):
    "Parse a class or method invocation."
    result = previous or ''
    name = tok.current()
    tok.checknext('(')
    params = self.parseparameters(tok)
    result += name + params
    if tok.peek() != '.':
      return result
    tok.checknext('.')
    return self.parseinvocation(tok, result + '.')

  def parseupto(self, ending, tok):
    "Parse the tokenizer up to the supplied ending."
    return self.parsetoendings(tok, [ending])

  def parsetoendings(self, tok, endings):
    "Parse the tokenizer up to a number of endings."
    result = ''
    tok.next()
    while not tok.current() in endings:
      processed = self.processtoken(tok)
      if processed == '++':
        processed = '+ 1'
        Trace.debug('Increasing ' + result + ' for endings: ' + unicode(endings))
        tok.autoincreases.append(result)
      if processed == '--':
        Trace.debug('Decreasing ' + result)
        processed = '- 1'
        tok.autodecreases.append(result)
      if processed != '.' and not result.endswith('.'):
        processed = ' ' + processed
      result += processed
      if not tok.current in endings:
        tok.next()
    if len(result) > 0:
      result = result[1:]
    Trace.debug('Left after ' + tok.current() + ', endings ' + unicode(endings) + ', result: ' + result)
    return result

  def expectblock(self, tok):
    "Mark that a block is to be expected."
    tok.depth += 1
    tok.waitingforblock = True

class Tokenizer(object):
  "Tokenizes a parse position."

  unmodified = [
      '&', '|', '=', '(', ')', '{', '}', '.', '+', '-', '"', ',', '/',
      '*', '<', '>', '\'', '[', ']', '%', ';',
      '!=','<=','>=', '==', '++', '--'
      ]
  modified = {
      '&&':'and', '||':'or', '!':'not'
      }
  comments = ['//', '/*']
  javasymbols = comments + unmodified + modified.keys()

  def __init__(self, pos):
    self.pos = pos
    self.currenttoken = None
    self.peeked = None
    self.autoincreases = []
    self.autodecreases = []
    self.depth = 0
    self.waitingforblock = False
    self.inclass = None
    self.inmethod = None
    self.variables = ['this']
    self.infor = 0

  def next(self):
    "Get the next single token, and store it for current()."
    if self.peeked:
      self.currenttoken = self.peeked
      self.peeked = None
    else:
      self.currenttoken = self.extractwithoutcomments()
    return self.currenttoken

  def checknext(self, token):
    "Check that the next token is the parameter."
    self.next()
    if self.currenttoken != token:
      Trace.error('Expected token ' + token + ', found ' + self.currenttoken)
      return False
    return True

  def extractwithoutcomments(self):
    "Get the next single token without comments."
    token = self.extracttoken()
    while token in self.comments:
      self.skipcomment(token)
      token = self.extracttoken()
    self.pos.skipspace()
    return token

  def extracttoken(self):
    "Extract the next token."
    if self.finished():
      return None
    if self.pos.checkidentifier():
      return self.pos.globidentifier()
    if self.pos.current() in self.javasymbols:
      result = self.pos.skipcurrent()
      while result + self.pos.current() in self.javasymbols:
        result += self.pos.skipcurrent()
      return result
    current = self.pos.skipcurrent()
    raise Exception('Unrecognized character: ' + current)

  def current(self):
    "Get the current token."
    return self.currenttoken

  def finished(self):
    "Find out if the tokenizer has finished tokenizing."
    self.pos.skipspace()
    return self.pos.finished()

  def iscurrentidentifier(self):
    "Return if the current token is an identifier (alphanumeric or _ characters)."
    if self.currenttoken.replace('_', '').isalnum():
      return True
    return False

  def skipcomment(self, token):
    "Skip over a comment."
    if token == '//':
      comment = self.pos.globexcluding('\n')
      return
    if token == '/*':
      while not self.pos.checkskip('/'):
        comment = self.pos.globincluding('*')
      return
    Trace.error('Unknown comment type ' + token)
  
  def peek(self):
    "Look ahead at the next token, without advancing the parse position."
    token = self.extractwithoutcomments()
    self.peeked = token
    return token

  def mark(self):
    "Mark the current state and return a handle."
    Trace.error('Unimplemented mark()')
    return None

  def revert(self, state):
    "Revert to a previous state as returned by mark()."
    Trace.error('Unimplemented revert()')


