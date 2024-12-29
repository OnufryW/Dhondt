# This is the tokenizer for sql.py
from tokens import *

# Note to self: There's a lot of quadratic line parsing here. I've initially
# not passed curpos around, just used s truncating. However, I've added
# curpos for debugging reasons. So, now, the code could be changed not to
# modify s, just to modify curpos and operate on the immutable line.

def consumeWord(s, tokenList, line, curpos):
  pos = 0
  if s and s[0].isalpha():
    while pos < len(s) and (s[pos].isalnum() or s[pos] == '_'):
      pos += 1
    tokenList.append(Token(s[:pos], WORD, line, curpos, curpos + pos))
    s = s[pos:]
  return curpos + pos, s

def consumeQuotedWord(s, tokenList, line, curpos):
  if s and (s[0] == '"' or s[0] == '\''):
    quote = s[0]
    endpos = 1
    if len(s) == 1:
      raise ValueError('Unclosed quote at the end of the line ' + str(line))
    while s[endpos] != quote:
      endpos += 1
      if endpos >= len(s):
        raise ValueError('Unclosed quote: ' + s + ' in line ' + str(line))
    tokenList.append(
        Token(s[1:endpos], QUOTED, line, curpos, curpos+endpos+1))
    s = s[endpos+1:]
    return curpos + endpos + 1, s
  return curpos, s

def consumeVariable(s, tokenList, line, curpos):
  if s and s[0] == '$':
    pos = 1
    while pos < len(s) and (s[pos].isalnum() or s[pos] == "_"):
      pos += 1
    tokenList.append(Token(s[1:pos], PARAM, line, curpos, curpos+pos))
    s = s[pos:]
    return curpos + pos, s
  return curpos, s

def consumeSpace(s, tokenList, line, curpos):
  if s and s[0].isspace():
    s = s[1:]
    return curpos + 1, s
  return curpos, s

def consumeNumber(s, tokenList, line, curpos):
  pos = 0
  if s and s[0].isnumeric():
    while pos < len(s) and (s[pos].isnumeric() or s[pos] == '.'):
      pos += 1
    tokenList.append(Token(s[:pos], NUMBER, line, curpos, curpos+pos))
    s = s[pos:]
  return curpos + pos, s

def consumeSymbol(s, tokenList, line, curpos):
  if s and s[0] in '+-=*/,();:<>[]':
    tokenList.append(Token(s[0], SYMBOL, line, curpos, curpos+1))
    s = s[1:]
    return curpos + 1, s
  return curpos, s

def tokenize(lines):
  res = []
  for l, s in enumerate(lines):
    if not s.strip() or s.strip()[0] == '#':
      continue
    curbeg = 0
    while s:
      curlen = len(s)
      curbeg, s = consumeWord(s, res, l, curbeg)
      curbeg, s = consumeQuotedWord(s, res, l, curbeg)
      curbeg, s = consumeVariable(s, res, l, curbeg)
      curbeg, s = consumeSpace(s, res, l, curbeg)
      curbeg, s = consumeNumber(s, res, l, curbeg)
      curbeg, s = consumeSymbol(s, res, l, curbeg)
      if len(s) == curlen:
        raise ValueError(
            'Failed to consume a token on line', l, 'position', curbeg,
            ' - remaining string', s)
  return res
