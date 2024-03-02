# The expression class, which provides the (implicit) Expression class,
# which has a single Eval(context) function.

class BinaryExpr:
  def __init__(self, left, right, op):
    self.left = left
    self.right = right
    self.op = op

  def Eval(self, context):
    return self.op(self.left.Eval(context), self.right.Eval(context))


class Sum(BinaryExpr):
  def __init__(self, left, right):
    super().__init__(left, right, lambda a, b: a+b)

class Difference(BinaryExpr):
  def __init__(self, left, right):
    super().__init__(left, right, lambda a, b: a-b)

class Product(BinaryExpr):
  def __init__(self, left, right):
    super().__init__(left, right, lambda a, b: a*b)

class Quotient(BinaryExpr):
  def __init__(self, left, right):
    super().__init__(left, right, lambda a, b: a/b)

class Equal(BinaryExpr):
  def __init__(self, left, right):
    super().__init__(left, right, lambda a, b: a == b)

class Lesser(BinaryExpr):
  def __init__(self, left, right):
    super().__init__(left, right, lambda a, b: a < b)

class Greater(BinaryExpr):
  def __init__(self, left, right):
    super().__init__(left, right, lambda a, b: a > b)

class UnaryExpr:
  def __init__(self, arg, op):
    self.arg = arg
    self.op = op

  def Eval(self, context):
    return self.op(self.arg.Eval(context))

class TernaryExpr:
  def __init__(self, arg1, arg2, arg3, op):
    self.arg1 = arg1
    self.arg2 = arg2
    self.arg3 = arg3
    self.op = op

  def Eval(self, context):
    return self.op(self.arg1.Eval(context), self.arg2.Eval(context),
                   self.arg3.Eval(context))

class Variable:
  def __init__(self, name):
    self.name = name

  def Eval(self, context):
    return context[self.name]

class Constant:
  def __init__(self, val):
    self.val = val

  def Eval(self, context):
    return self.val
