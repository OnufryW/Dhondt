# This is the tokenizer for sql.py
from tokens import *

def consumeWord(s, tokenList):
  if s and s[0].isalpha():
    pos = 0
    while pos < len(s) and (s[pos].isalnum() or s[pos] == '_'):
      pos += 1
    tokenList.append(Token(s[:pos], WORD))
    s = s[pos:]
  return s

def consumeQuotedWord(s, tokenList):
  if s and (s[0] == '"' or s[0] == '\''):
    quote = s[0]
    endpos = 1
    while s[endpos] != quote:
      endpos += 1
    tokenList.append(Token(s[1:endpos], QUOTED))
    s = s[endpos+1:]
  return s

def consumeVariable(s, tokenList):
  if s and s[0] == '$':
    pos = 1
    while pos < len(s) and (s[pos].isalnum() or s[pos] == '_'):
      pos += 1
    tokenList.append(Token(s[1:pos], VARIABLE))
    s = s[pos:]
  return s

def consumeWildcard(s, tokenList):
  if s.startswith('$?'):
    tokenList.append(Token('?', VARIABLE))
    s = s[2:]
  return s

def consumeSpace(s, tokenList):
  if s and s[0].isspace():
    s = s[1:]
  return s

def consumeNumber(s, tokenList):
  if s and s[0].isnumeric():
    pos = 0
    while pos < len(s) and (s[pos].isnumeric() or s[pos] == '.'):
      pos += 1
    tokenList.append(Token(s[:pos], NUMBER))
    s = s[pos:]
  return s

def consumeSymbol(s, tokenList):
  if s and s[0] in '+-=*/,();:<>':
    tokenList.append(Token(s[0], SYMBOL))
    s = s[1:]
  return s

def tokenize(s):
  res = []
  while s:
    curlen = len(s)
    s = consumeWord(s, res)
    s = consumeQuotedWord(s, res)
    # Note: ConsumeWildcard has to go just before ConsumeVariable
    s = consumeWildcard(s, res)
    s = consumeVariable(s, res)
    s = consumeSpace(s, res)
    s = consumeNumber(s, res)
    s = consumeSymbol(s, res)
    if len(s) == curlen:
      raise ValueError('Failed to consume a token from ' + s)
  return res

