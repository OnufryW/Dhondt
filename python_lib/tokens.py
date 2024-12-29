# The common token class. This is in a separate file so we can import it
# into the main namespace in other files, without cluttering it with all
# of tokenize.py.
class Token:
  def __init__(self, value, typ, line=None, start=None, end=None):
    self.value = value
    self.typ = typ
    self.line = line
    self.start = start
    self.end = end

  def DebugString(self):
   return '{} of type {}, at line {}, positions [{}:{}]'.format(
      self.value, self.typ, self.line + 1, self.start, self.end) 

WORD = 'word'
NUMBER = 'number'
SYMBOL = 'symbol'
QUOTED = 'quoted'
PARAM = 'variable'

def Symbol(val):
  return Token(val, SYMBOL)

