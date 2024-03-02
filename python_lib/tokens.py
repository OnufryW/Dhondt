# The common token class. This is in a separate file so we can import it
# into the main namespace in other files, without cluttering it with all
# of tokenize.py.
class Token:
  def __init__(self, value, typ):
    self.value = value
    self.typ = typ

WORD = 'word'
NUMBER = 'number'
SYMBOL = 'symbol'
QUOTED = 'quoted'
VARIABLE = 'variable'

def Symbol(val):
  return Token(val, SYMBOL)

