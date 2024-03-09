# The expression class, which provides the (implicit) Expression class,
# which has a single Eval(context) function.

class Expression:
  def __init__(self, token, descr):
    self.line = token.line
    self.startpos = token.start
    self.endpos = token.end
    self.descr = descr

  def DebugString(self):
    return '{} at line {}, positions {}:{}'.format(
        self.descr, self.line + 1, self.startpos + 1, self.endpos + 1)

  def ErrorStr(self):
    return 'Failed to evaluate ' + self.DebugString()

class BinaryExpr(Expression):
  def __init__(self, left, right, op, token, descr):
    super().__init__(token, descr)
    self.left = left
    self.right = right
    self.op = op

  def Eval(self, context):
    left = self.left.Eval(context)
    right = self.right.Eval(context)
    try:
      return self.op(left, right)
    except Exception as e:
      raise ValueError(self.ErrorStr()) from e

class Sum(BinaryExpr):
  def __init__(self, left, right, token):
    super().__init__(left, right, lambda a, b: a+b, token, 'sum')

class Difference(BinaryExpr):
  def __init__(self, left, right, token):
    super().__init__(left, right, lambda a, b: a-b, token, 'difference')

class Product(BinaryExpr):
  def __init__(self, left, right, token):
    super().__init__(left, right, lambda a, b: a*b, token, 'product')

class Quotient(BinaryExpr):
  def __init__(self, left, right, token):
    super().__init__(left, right, lambda a, b: a/b, token, 'quotient')

class Equal(BinaryExpr):
  def __init__(self, left, right, token):
    super().__init__(left, right, lambda a, b: a == b, token, 'equality')

class Lesser(BinaryExpr):
  def __init__(self, left, right, token):
    super().__init__(left, right, lambda a, b: a < b, token,
                     'lesser comparison')

class Greater(BinaryExpr):
  def __init__(self, left, right, token):
    super().__init__(left, right, lambda a, b: a > b, token,
                     'greater comparison')

class UnaryExpr(Expression):
  def __init__(self, arg, op, token, descr):
    super().__init__(token, descr)
    self.arg = arg
    self.op = op

  def Eval(self, context):
    arg = self.arg.Eval(context)
    try:
      return self.op(arg)
    except Exception as e:
      raise ValueError(self.ErrorStr()) from e

class TernaryExpr(Expression):
  def __init__(self, arg1, arg2, arg3, op, token, descr):
    super().__init__(token, descr)
    self.arg1 = arg1
    self.arg2 = arg2
    self.arg3 = arg3
    self.op = op

  def Eval(self, context):
    arg1 = self.arg1.Eval(context)
    arg2 = self.arg2.Eval(context)
    arg3 = self.arg3.Eval(context)
    try:
      return self.op(arg1, arg2, arg3)
    except Exception as e:
      raise ValueError(self.ErrorStr()) from e

class If(Expression):
  def __init__(self, condition, then, otherwise, token):
    super().__init__(token, 'conditional')
    self.condition = condition
    self.then = then
    self.otherwise = otherwise

  def Eval(self, context):
    # Note: I think this can't fail without children failing.
    condition = self.condition.Eval(context)
    if condition:
      return self.then.Eval(context)
    else:
      return self.otherwise.Eval(context)

class RangeExpr(Expression):
  def __init__(self, beg, end, acc, token, descr):
    super().__init__(token, descr)
    self.beg = beg
    self.end = end
    self.acc = acc

  def Eval(self, context):
    val = self.acc[0]
    end = self.end
    if end < 0:
      end = len(context) // 2 + 1
    for col in range(self.beg, end):
      argpos = str(col)
      if argpos not in context:
        raise ValueError(
            self.ErrorStr(),
            '{} not present in context: {}'.format(argpos, context))
      arg = context[argpos]
      try:
        val = self.acc[1](val, arg)
      except Exception as e:
        raise ValueError(self.ErrorStr(), 'Accumulating', arg, 'to', val,
                         'at pos', col) from e
    return val

class Variable(Expression):
  def __init__(self, name, token):
    super().__init__(token, 'variable ' + name)
    self.name = name

  def Eval(self, context):
    if self.name not in context:
      raise ValueError(
          self.ErrorStr(), 'Name not present in context: {}'.format(
              context.keys()))
    return context[self.name]

class Constant(Expression):
  def __init__(self, val, token):
    super().__init__(token, 'constant ' + str(val))
    self.val = val

  def Eval(self, context):
    return self.val
