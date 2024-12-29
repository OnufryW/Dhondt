import heapq
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

class AggregateExpr(Expression):
  def __init__(self, child, acc, token, descr):
    super().__init__(token, descr)
    self.child = child
    self.base = acc[0]
    self.op = acc[1]

  # For aggregated expressions, the context includes a special key,
  # __group_data, which stores the aggregated data. This value of this key
  # is a standard 'data' map where values are not individual elements, 
  # but lists (where the list is the full list of values that grouped up to
  # the row we're currently evaluating).
  def Eval(self, context):
    # __group_data stores a list of sub-contexts, one for each row.
    # We Eval the child expression in the context of every row, one
    # by one, and then apply the aggregation.
    if '__group_data' not in context:
      raise ValueError(self.ErrorStr(),
                       'Cannot evaluate outside of aggregation context')
    acc = self.base
    original_data = context['__data']
    group_context = context['__group_data']
    del context['__group_data']
    for inner_context in group_context:
      context['__data'] = original_data | inner_context
      val = self.child.Eval(context)
      try:
        acc = self.op(acc, val)
      except Exception as e:
        raise ValueError(self.ErrorStr(),
            'When accumulating {} to {}'.format(acc, val)) from e
    context['__data'] = original_data
    context['__group_data'] = group_context
    return acc

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
    beg = self.beg.Eval(context) - 1
    end = self.end.Eval(context) - 1
    if end < 0:
      end = context['?last']
    for col in range(beg, end):
      arg = context['__data'][col]
      try:
        val = self.acc[1](val, arg)
      except Exception as e:
        raise ValueError(self.ErrorStr(), 'Accumulating', arg, 'to', val,
                         'at pos', col) from e
    return val

# Note: This isn't super-efficient, as we do the whole d'Hondt calculation
# for each party over and over again; instead of doing it once. However,
# I expect O(10) parties and O(40) districts, so it should be fine.
class DhondtExpr(Expression):
  def __init__(self, seats, myvotes, beg, end, token):
    super().__init__(token, 'dhondt')
    self.seats = seats
    self.myvotes = myvotes
    self.beg = beg
    self.end = end

  def Calc(self, my_votes, index, other_votes, seats):
    # 'index' should be the my index amongst the other votes, and should
    # be a fractional number.
    division_level = {index: (my_votes, 1)}
    candidates = []
    heapq.heappush(candidates, (-my_votes, index))
    for i, v in enumerate(other_votes):
      division_level[i] = (v, 1)
      heapq.heappush(candidates, (-v, i))
    res = 0
    for seat in range(seats):
      _, ind = heapq.heappop(candidates)
      votes, div = division_level[ind]
      division_level[ind] = (votes, div+1)
      heapq.heappush(candidates, (-votes / (div+1), ind))
      if ind == index:
        res += 1
    return res

  def Eval(self, context):
    beg = self.beg.Eval(context) - 1
    end = self.end.Eval(context) - 1
    if end < 0:
      end = context['?last']
    my_index = self.myvotes.Eval(context) - 1
    if my_index < beg or my_index >= end:
      raise ValueError(self.ErrorStr(),
        ('Second argument of dhondt {} should be in the range [{},{}) ' +
         'specified by the third').format(my_index, beg, end))
    other_votes = [context['__data'][col]
                   for col in range(beg, end) if col != my_index]
    my_votes = context['__data'][my_index]
    seats = self.seats.Eval(context)
    return self.Calc(my_votes, my_index-beg-0.5, other_votes, seats)

def GetValueFromContext(name, context):
  origname = name
  backtracks = 0
  # TODO: Could I avoid evaluating this with every single row, while still
  # allowing reference variables to work?
  while name.startswith('!'):
    backtracks += 1
    name = name[1:]
  path = [name]
  while True:
    curname = path[-1]
    try:
      curname = int(curname) - 1
      break
    except:
      pass
    if curname not in context:
      if len(path) == 1:
        raise ValueError('Name {} not present in context: {}'.format(
            name, context.keys()))
      else:
        raise ValueError(
            'Name {} (reached via path {}) not in context {}'.format(
                name, path, context.keys()))
    if len(path) > len(context) + 1:
      raise ValueError('A loop while resolving {} in context {}: {}'.format(
          path[0], context.keys(), path))
    path.append(context[curname])
  if backtracks == 0:
    if isinstance(context['__data'], dict):
      if curname not in context['__data']:
        if '__group_data' in context and curname in context['__group_data']:
          raise ValueError(
              ('Referring to non-group-key column {} ({}) outside ' +
               'of aggregation').format(origname, curname))
        else:
          raise ValueError(
            'Referring to value {} ({}) outside of range of columns'.format(
                origname, curname))
    else:
      assert isinstance(context['__data'], list)
      if curname >= len(context['__data']):
        raise ValueError(('Referring to value {} ({}) outside ' +
                          'of range of columns').format(origname, curname))
    return context['__data'][curname]
  elif backtracks > len(path):
    raise ValueError('Too many !s in {}: {}, resolution path is {}'.format(
        origname, backtracks, path))
  else:
    return path[-backtracks]

class Variable(Expression):
  def __init__(self, name, token):
    super().__init__(token, 'variable ' + str(name))
    self.name = name

  def Eval(self, context):
    try:
      return GetValueFromContext(self.name, context)
    except Exception as e:
      raise ValueError(self.ErrorStr()) from e

class NumColumnsExpr(Expression):
  def __init__(self, token):
    super().__init__(token, 'numcolumns()')

  def Eval(self, context):
    return context['?last']

class CurrExpr(Expression):
  def __init__(self, token):
    super().__init__(token, 'curr()')

  def Eval(self, context):
    if '?' not in context:
      raise ValueError(self.ErrorStr(), 
                       'curr() can only be used in column range definitions')
    index = context[context['?']]
    if (isinstance(context['__data'], dict) and
        index - 1 not in context['__data']):
      raise ValueError(self.ErrorStr(),
                       'Current column is not a part of the group key')
    return context['__data'][index - 1]

class CurrNameExpr(Expression):
  def __init__(self, token):
    super().__init__(token, 'currname()')

  def Eval(self, context):
    if '?' not in context:
      raise ValueError(self.ErrorStr(), 
                       'currname() can only be used in column range definitions')
    return context['?']

class AtExpr(Expression):
  """ Evaluates the "at" function, taking either an column index or name,
      and returning the value of that column.

      In aggregation contexts, will only work if the column referred to is a
      part of the group key.
  """
  def __init__(self, arg, token):
    super().__init__(token, 'at')
    self.arg = arg

  def Eval(self, context):
    arg = self.arg.Eval(context)
    if isinstance(arg, str):
      # Get column index from column name:
      if arg not in context:
        raise ValueError(self.ErrorStr(), 'column {} unknown'.format(arg))
      arg = context[arg]
    if arg <= 0 or arg >= context['?last']:
      raise ValueError(self.ErrorStr(), 
                       'column index {} out of range'.format(arg))
    if isinstance(context['__data'], dict) and arg - 1 not in context['__data']:
      # Trying to refer to a non-key column in an aggregation.
      raise ValueError(self.ErrorStr(),
                       'Column {} is not a part of the group key'.format(arg))
    return context['__data'][arg - 1]

class IndexExpr(Expression):
  """ Evaluates the index (1-indexed) of a column, given a column name."""
  def __init__(self, arg, token):
    super().__init__(token, 'index')
    self.arg = arg

  def Eval(self, context):
    arg = self.arg.Eval(context)
    if isinstance(arg, int) and arg > 0 and arg < context['?last']:
      return arg
    if arg not in context:
      raise ValueError(self.ErrorStr(), 'column {} unknown'.format(arg))
    return context[arg]

class NameExpr(Expression):
  """ Evaluates the name of a column, given the 1-indexed index."""
  def __init__(self, arg, token):
    super().__init__(token, 'name')
    self.arg = arg

  def Eval(self, context):
    arg = self.arg.Eval(context)
    if isinstance(arg, str) and arg in context:
      return arg
    if not isinstance(arg, int):
      raise ValueError(
          self.ErrorStr(),
          'Argument of name has to be an integer, got {}'.format(arg))
    if arg <= 0 or arg >= context['?last']:
      raise ValueError(self.ErrorStr(),
                       'column index {} out of range'.format(arg))
    for name in context:
      if context[name] == arg:
        return name
    # For arg in the valid range, context has to contain a mapping to arg. 
    assert(False)

class ParamExpr(Expression):
  """ Evaluates the value of a parameter. """
  def __init__(self, arg, token):
    super().__init__(token, 'param')
    self.arg = arg

  def Eval(self, context):
    arg = self.arg.Eval(context)
    if arg not in context['__params']:
      raise ValueError('Parameter {} missing.'.format(arg))
    return context['__params'][arg]

class Constant(Expression):
  def __init__(self, val, token):
    super().__init__(token, 'constant ' + str(val))
    self.val = val

  def Eval(self, context):
    return self.val
