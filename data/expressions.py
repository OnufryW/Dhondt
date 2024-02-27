# Various expression classes that can operate on a CSV row.

class Ref:
  def __init__(self, number):
    self.number = number

  def Get(self, row):
    return row[self.number - 1]

class Const:
  def __init__(self, val):
    self.val = val

  def Get(self, row):
    return self.val

class Add:
  def __init__(self, v1, v2):
    self.v1 = v1
    self.v2 = v2

  def Get(self, row):
    return self.v1.Get(row) + self.v2.Get(row)

class SumFrom:
  def __init__(self, number):
    self.number = number

  def Get(self, row):
    return sum([int(v) for v in row[self.number-1:]])

class Equals:
  def __init__(self, v1, v2):
    self.v1 = v1
    self.v2 = v2

  def Get(self, row):
    return self.v1.Get(row) == self.v2.Get(row)

class StripQuote:
  def __init__(self, inner):
    self.inner = inner

  def Get(self, row):
    inner = self.inner.Get(row)
    if isinstance(inner, str) and inner and inner[0] == '"' and inner[-1] == '"':
      return inner[1:-1]
    return inner

class RemoveInternalCommas:
  def __init__(self, inner):
    self.inner = inner

  def Get(self, row):
    inner = self.inner.Get(row)
    return inner.replace(',', '')

class DashAsZero:
  def __init__(self, inner):
    self.inner = inner

  def Get(self, row):
    inner = self.inner.Get(row)
    return 0 if inner == '-' else inner

class EmptyAsZero:
  def __init__(self, inner):
    self.inner = inner

  def Get(self, row):
    inner = self.inner.Get(row)
    return 0 if not inner else inner

class ToInt:
  def __init__(self, inner):
    self.inner = inner

  def Get(self, row):
    return int(self.inner.Get(row))

class IsInteger:
  def __init__(self, inner):
    self.inner = inner

  def Get(self, row):
    try:
      int(self.inner.Get(row))
    except ValueError:
      return False
    return True

class ToString:
  def __init__(self, inner):
    self.inner = inner

  def Get(self, row):
    return str(self.inner.Get(row))

def ParseOperator(code, inner):
  assert code in 'QCDEIS'
  if code == 'Q':
    return StripQuote(inner)
  elif code == 'C':
    return RemoveInternalCommas(inner)
  elif code == 'D':
    return DashAsZero(inner)
  elif code == 'E':
    return EmptyAsZero(inner)
  elif code == 'I':
    return ToInt(inner)
  elif code == 'S':
    return ToString(inner)
  assert False


def ParseReference(config, context_column):
  if config[0] in 'QCDEIS':
    i = ParseReference(config[1:], context_column)
    return ParseOperator(config[0], i)
  elif config == '?':
    assert context_column > 0
    return Ref(context_column)
  else:
    n = int(config)
    return Ref(n)


# Returns a class with a "Get(row)" method.
def Parse(config, context_column):
  config = config.strip()
  if config.startswith('IsInteger('):
    assert config[-1] == ')'
    return IsInteger(Parse(config[10:-1], context_column))
  if config.startswith('Sum('):
    assert config[-1] == ')'
    return SumFrom(int(config[4:-1]))
  if config.find('=') != -1:
    vals = [Parse(el, context_column) for el in config.split('=')]
    assert len(vals) == 2
    return Equals(vals[0], vals[1])
  if config.find('+') != -1:
    vals = [Parse(el, context_column) for el in config.split('+')]
    while len(vals) > 1:
      v1 = vals.pop()
      v2 = vals.pop()
      vals.append(Add(v1, v2))
    return vals[0]
  if config[0] == '$':
    return ParseReference(config[1:], context_column)
  elif config[0] == '"':
    assert config[-1] == '"'
    return Const(config[1:-1])
  else:
    return Const(int(config))

