# This is an in-memory kinda SQL interpreter.
import math

import tokenizer
import expression
import command
from tokens import *

UNARY_FUNCTIONS = {
  'sqrt': lambda a: math.sqrt(a),
  'int': lambda a: int(a),
  'len': lambda a: len(a),
  'not': lambda a: not a,
  'abs': lambda a: abs(a)
}
BINARY_FUNCTIONS = {
  'min': lambda a, b: min(a,b),
  'beginning': lambda a, b: a[:b],
  'end': lambda a, b: a[b:],
  'and': lambda a, b: a and b,
  'or': lambda a, b: a or b,
}
TERNARY_FUNCTIONS = {
  'if': 'SPECIAL',
  'substr': lambda a, b, c: a[b:c],
  'replace': lambda a, b, c: a.replace(b, c),
}
RANGE_FUNCTIONS = {
  'concat_range': ('', lambda a, b: a + b),
  'sum_range': (0, lambda a, b: a + b),
  'and_range': (True, lambda a, b: a and b),
}
AGGREGATE_FUNCTIONS = {
  'sum': (0, lambda a, b: a + b),
  'max': (None, lambda a, b: b if a is None else max(a,b)),
  'and': (0, lambda a, b: a + b),
}
SPECIAL_FUNCTIONS = {
  'dhondt', 'at', 'index', 'name', 'curr', 'currname', 'numcolumns'
}
FUNCTION_NAMES = list(UNARY_FUNCTIONS.keys()) + list(BINARY_FUNCTIONS.keys()) + list(TERNARY_FUNCTIONS.keys()) + list(RANGE_FUNCTIONS.keys()) + list(AGGREGATE_FUNCTIONS.keys()) + list(SPECIAL_FUNCTIONS)
KEYWORDS = FUNCTION_NAMES + [
  'LOAD', 'DUMP', 'FROM', 'TO', 'SEPARATOR', 'WITH', 'TRANSFORM', 'AS',
  'PARAM', 'PREFIX', 'IMPORT']

def TryPop(tokens, expected_type=None, expected_value=None):
  if not tokens:
    return None
  if expected_type is not None and tokens[0].typ != expected_type:
    return None
  if expected_value is not None and tokens[0].value != expected_value:
    return None
  return tokens.pop(0)

def InvalidToken(message, token):
  raise ValueError(*message, token.DebugString())

def FailedPop(tokens, message):
  if not tokens:
    raise ValueError(message, 'Token list empty')
  else:
    raise ValueError(message, tokens[0].DebugString())

def ForcePop(tokens, expected_type=None, expected_value=None):
  token = TryPop(tokens, expected_type, expected_value)
  if token is None:
    if expected_type is not None:
      if expected_value is not None:
        mess = ['Trying to pop', expected_value, 'of type', expected_type]
      else:
        mess = ['Trying to pop a token of type', expected_type]
    else:
      mess = ['Trying to pop any token']
    FailedPop(tokens, mess)
  return token

def GetNumber(token):
  if token.typ != NUMBER:
    InvalidToken(['Unexpected token type when trying to parse number'], token)
  if token.value.find('.') == -1:
    return expression.Constant(int(token.value), token)
  else:
    return expression.Constant(float(token.value), token)

def GetRange(tokens, settings):
  if rangetoken := TryPop(tokens, SYMBOL, '['):
    if midtoken := TryPop(tokens, SYMBOL, ':'):
      beg = expression.Constant(1, midtoken)
    else:
      beg = GetExpression(tokens, settings)
      midtoken = ForcePop(tokens, SYMBOL, ':')
    if TryPop(tokens, SYMBOL, ']'):
      end = expression.NumColumnsExpr(midtoken)
    else:
      endval = GetExpression(tokens, settings)
      end = expression.If(
          expression.BinaryExpr(
              endval, expression.Constant(0, midtoken), lambda a, b: a < b,
              midtoken, '<'),
          expression.NumColumnsExpr(midtoken), endval, midtoken)
      ForcePop(tokens, SYMBOL, ']')
    return beg, end
  begtoken = TryPop(tokens, NUMBER)
  midtoken = ForcePop(tokens, SYMBOL, ':')
  endtoken = TryPop(tokens, NUMBER)
  if begtoken:
    beg = expression.Constant(int(begtoken.value), begtoken)
  else:
    beg = expression.Constant(1, midtoken)
  endval = int(endtoken.value) if endtoken else -1
  endtoken = endtoken if endtoken else midtoken
  end = expression.If(
            expression.Constant(endval < 0, endtoken),
            expression.NumColumnsExpr(endtoken),
            expression.Constant(endval, endtoken), endtoken)
  return beg, end

def GetFactor(tokens, settings):
  token = ForcePop(tokens)
  if token.typ == NUMBER:
    return GetNumber(token)
  elif token.typ == WORD:
    if token.value in FUNCTION_NAMES:
      ForcePop(tokens, SYMBOL, '(')
      if token.value in UNARY_FUNCTIONS:
        arg = GetExpression(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        return expression.UnaryExpr(
            arg, UNARY_FUNCTIONS[token.value], token, token.value)
      elif token.value in BINARY_FUNCTIONS:
        arg1 = GetExpression(tokens, settings)
        ForcePop(tokens, SYMBOL, ',')
        arg2 = GetExpression(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        return expression.BinaryExpr(
            arg1, arg2, BINARY_FUNCTIONS[token.value], token, token.value)
      elif token.value in TERNARY_FUNCTIONS:
        arg1 = GetExpression(tokens, settings)
        ForcePop(tokens, SYMBOL, ',')
        arg2 = GetExpression(tokens, settings)
        ForcePop(tokens, SYMBOL, ',')
        arg3 = GetExpression(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        if token.value == 'if':
          return expression.If(arg1, arg2, arg3, token)
        return expression.TernaryExpr(
            arg1, arg2, arg3, TERNARY_FUNCTIONS[token.value], token,
            token.value)
      elif token.value in RANGE_FUNCTIONS:
        beg, end = GetRange(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        return expression.RangeExpr(beg, end, RANGE_FUNCTIONS[token.value],
                                    token, token.value)
      elif token.value == 'dhondt':
        seats = GetExpression(tokens, settings)
        ForcePop(tokens, SYMBOL, ',')
        votes = GetExpression(tokens, settings)
        ForcePop(tokens, SYMBOL, ',')
        beg, end = GetRange(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        return expression.DhondtExpr(seats, votes, beg, end, token)
      elif token.value == 'curr':
        ForcePop(tokens, SYMBOL, ')')
        return expression.CurrExpr(token)
      elif token.value == 'currname':
        ForcePop(tokens, SYMBOL, ')')
        return expression.CurrNameExpr(token)
      elif token.value == 'numcolumns':
        ForcePop(tokens, SYMBOL, ')')
        return expression.NumColumnsExpr(token)
      elif token.value == 'at':
        arg = GetExpression(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        return expression.AtExpr(arg, token)
      elif token.value == 'index':
        arg = GetExpression(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        return expression.IndexExpr(arg, token)
      elif token.value == 'name':
        arg = GetExpression(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        return expression.NameExpr(arg, token)
      elif token.value in AGGREGATE_FUNCTIONS:
        arg = GetExpression(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        return expression.AggregateExpr(arg, AGGREGATE_FUNCTIONS[token.value],
                                        token, token.value)
      InvalidToken(['Weird function name when trying to get factor'], token)
    elif token.value in KEYWORDS:
      InvalidToken(['Keyword when trying to get factor'], token)
    else:
      if WORDS_AS_CONSTANTS in settings and settings[WORDS_AS_CONSTANTS]:
        return expression.Constant(token.value, token)
      return expression.AtExpr(expression.Constant(token.value, token), token)
  elif token.typ == PARAM:
    return expression.ParamExpr(expression.Constant(token.value, token), token)
  elif token.typ == SYMBOL:
    if token.value == '(':
      expr = GetExpression(tokens, settings)
      ForcePop(tokens, SYMBOL, ')')
      return expr
    if token.value == '-':
      number_token = ForcePop(tokens, NUMBER)
      number = GetNumber(number_token)
      number.val = -number.val
      return number
    InvalidToken(['Unexpected symbol when trying to get factor'], token)
  elif token.typ == QUOTED:
    return expression.Constant(token.value, token)
  InvalidToken(['Unexpected token when trying to get factor'], token)

def GetProduct(tokens, settings):
  left = GetFactor(tokens, settings)
  while tokens and tokens[0].typ == 'symbol' and tokens[0].value in '*/':
    token = ForcePop(tokens)
    right = GetFactor(tokens, settings)
    if token.value == '*':
      left = expression.Product(left, right, token)
    else:
      left = expression.Quotient(left, right, token)
  return left

def GetSum(tokens, settings):
  left = GetProduct(tokens, settings)
  while tokens and tokens[0].typ == 'symbol' and tokens[0].value in '+-':
    token = ForcePop(tokens)
    right = GetProduct(tokens, settings)
    if token.value == '+':
      left = expression.Sum(left, right, token)
    else:
      left = expression.Difference(left, right, token)
  return left

def GetComparison(tokens, settings):
  left = GetSum(tokens, settings)
  if tokens and tokens[0].typ == 'symbol' and tokens[0].value in '<=>':
    token = ForcePop(tokens)
    right = GetSum(tokens, settings)
    if token.value == '=':
      return expression.Equal(left, right, token)
    elif token.value == '<':
      return expression.Lesser(left, right, token)
    else:
      return expression.Greater(left, right, token)
  return left

# Expression grammar
# expr = comparison
# comparison = sum | sum = sum | sum < sum | sum > sum
# sum = product | sum + product | sum - product
# product = factor | factor * factor | factor / factor
# factor = functioncall | variable | number | group
# functioncall = FUNCTIONNAME ( args )
# args = '' | expr commalist
# commalist = '' | , expr commalist
# variable = WORD_NOT_KEYWORD
# number = NUMBER
# group = ( expr )

# There are two modes of expression getting, depending on how we interpret
# a free-standing string (a "word" without quotes). In the standard mode, we
# treat this as a column name reference (and we implement it as an AtExpr). In
# some contexts, however, mostly where we know there will be no row when
# interpreting the expression, we will interpret an unquoted word as a string
# constant, for the convenience of not typing out the quotes.
#
# Out of the two ways of implementing this - a global variable or a context
# passed all along - I chose the latter. I encapsulated this into a settings
# dict, which right now has one entry: 'words_as_constants', defaulting to
# False.
WORDS_AS_CONSTANTS = 'words_as_constants'
def GetExpression(tokens, settings):
  return GetComparison(tokens, settings)

#----------------------------------------------------------------------#

def GetLoadTable(tokens, line):
  name = ForcePop(tokens, WORD).value
  ForcePop(tokens, WORD, 'FROM')
  path = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  options = {}
  while token := TryPop(tokens, WORD, 'WITH'):
    if token := TryPop(tokens, WORD, 'SEPARATOR'):
      options[command.SEPARATOR] = ForcePop(tokens, QUOTED).value
    elif token := TryPop(tokens, WORD, 'IGNORE'):
      ForcePop(tokens, WORD, 'QUOTED')
      ForcePop(tokens, WORD, 'SEPARATOR')
      options['IGNORE QUOTED SEPARATOR'] = True
    else:
      FailedPop(tokens, ['Invalid optional argument to LOAD TABLE'])
  return command.Load(line, name, path, options)

def GetDumpTable(tokens, line):
  name = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  if TryPop(tokens, WORD, 'TO'):
    path = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  else:
    path = expression.Constant('stdout', tokens[0])
  return command.Dump(line, name, path)

def GetImport(tokens, line):
  path = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  options = {command.PREFIX: expression.Constant('', tokens[0]),
             command.EXTRA_PARAMS: {},
             command.EXTRA_TABLES: [],
             command.PARAM_PREFIX: expression.Constant('', tokens[0])}
  while token := TryPop(tokens, WORD, 'WITH'):
    if TryPop(tokens, WORD, 'PREFIX'):
      prefix = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
      options[command.PREFIX] = prefix
    elif TryPop(tokens, WORD, 'PARAM'):
      key = ForcePop(tokens, WORD)
      val = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
      options[command.EXTRA_PARAMS][key.value] = val
    elif TryPop(tokens, WORD, 'TABLE'):
      table_name = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
      options[command.EXTRA_TABLES].append(table_name)
    elif TryPop(tokens, WORD, 'PARAM_PREFIX'):
      prefix = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
      options[command.PARAM_PREFIX] = prefix
    else:
      FailedPop(tokens, ['Invalid optional argument to IMPORT'])
  return command.Import(line, path, options, GetCommandList)

def GetExprList(tokens):
  expr_list = []
  while True:
    expr = GetExpression(tokens, {})
    asorfor = ForcePop(tokens, WORD)
    if asorfor.value not in ['AS', 'FOR']:
      InvalidToken(['The AS or FOR clause in an expression'], asorfor)
    if asorfor.value == 'AS':
      columnname = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
      expr_list.append(command.SingleExpression(expr, columnname))
    else:
      range_begin, range_end = GetRange(tokens, {})
      header_expr = expression.CurrNameExpr(asorfor)
      if TryPop(tokens, WORD, 'AS'):
        header_expr = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
      expr_list.append(command.RangeExpression(
          expr, range_begin, range_end, header_expr))
    if TryPop(tokens, SYMBOL, ',') is None:
      return expr_list

def GetTransform(tokens, line):
  source_table = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  target_table = None
  if TryPop(tokens, WORD, 'TO'):
    target_table = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  ForcePop(tokens, WORD, 'WITH')
  expr_list = GetExprList(tokens)
  return command.Transform(line, source_table, target_table, expr_list)

def GetAggregate(tokens, line):
  source_table = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  target_table = None
  if TryPop(tokens, WORD, 'TO'):
    target_table = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  group_list = []
  if TryPop(tokens, WORD, 'BY'):
    while True:
      group_key = None
      if word := TryPop(tokens, WORD):
        group_key = word.value
      elif var := TryPop(tokens, PARAM):
        try:
          group_key = int(var.value)
        except ValueError:
          group_key = var.value
      else:
        FailedPop(tokens, ['Word or variable expected as group key'])
      group_list.append(group_key)
      if TryPop(tokens, SYMBOL, ',') is None:
        break
  ForcePop(tokens, WORD, 'WITH')
  expr_list = GetExprList(tokens)
  return command.Aggregate(
      line, source_table, target_table, group_list, expr_list)
      
def GetJoin(tokens, line):
  left_table = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  ForcePop(tokens, WORD, 'INTO')
  right_table = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  ForcePop(tokens, WORD, 'ON')
  left_expr = GetExpression(tokens, {})
  comparator = None
  if TryPop(tokens, WORD, 'EQ'):
    comparator = 'EQ'
  elif TryPop(tokens, WORD, 'PREFIX'):
    comparator = 'PREFIX'
  else:
    FailedPop(tokens, ['Invalid comparator'])
  right_expr = GetExpression(tokens, {})
  unmatched_keys = 'IGNORE'
  unmatched_values = False
  while TryPop(tokens, WORD, 'WITH'):
    if TryPop(tokens, WORD, 'INSERT'):
      if TryPop(tokens, WORD, 'UNMATCHED'):
        ForcePop(tokens, WORD, 'VALUES')
        unmatched_values = True
      elif TryPop(tokens, WORD, 'MISSING'):
        ForcePop(tokens, WORD, 'KEYS')
        unmatched_keys = 'INCLUDE'
      else:
        FailedPop(tokens, ['Option on join, WITH INSERT...'])
    elif TryPop(tokens, WORD, 'RAISE'):
      ForcePop(tokens, WORD, 'UNMATCHED')
      ForcePop(tokens, WORD, 'KEYS')
      unmatched_keys = 'RAISE'
  ForcePop(tokens, WORD, 'AS')
  target_table = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  return command.Join(line, left_table, right_table, target_table,
                      left_expr, right_expr, comparator, unmatched_keys,
                      unmatched_values)

def GetAppend(tokens, line):
  expr_list = [GetExpression(tokens, {WORDS_AS_CONSTANTS: True})]
  while TryPop(tokens, SYMBOL, ','):
    expr_list.append(GetExpression(tokens, {WORDS_AS_CONSTANTS: True}))
  ForcePop(tokens, WORD, 'TO')
  table = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  return command.Append(line, expr_list, table)

def GetPivot(tokens, line):
  table = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  target = None
  headers_from = None
  headers_to = None
  if TryPop(tokens, WORD, 'TO'):
    target = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  while TryPop(tokens, WORD, 'WITH'):
    if TryPop(tokens, WORD, 'NEW_HEADERS_FROM'):
      headers_from = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
    elif TryPop(tokens, WORD, 'OLD_HEADERS_TO'):
      headers_to = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
    else:
      FailedPop(tokens, ['Option for pivot'])
  return command.Pivot(line, table, target, headers_from, headers_to)

def GetFilter(tokens, line):
  table = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  target = None
  if TryPop(tokens, WORD, 'TO'):
    target = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  ForcePop(tokens, WORD, 'BY')
  expr = GetExpression(tokens, {})
  return command.Filter(line, table, target, expr)

def GetDrop(tokens, line):
  table = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  return command.Drop(line, table)

def GetList(tokens, line):
  ForcePop(tokens, WORD, 'TABLES')
  return command.List(line)

def GetDescribe(tokens, line):
  table = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  return command.Describe(line, table)

def GetVisualize(tokens, line):
  table = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  base_token = ForcePop(tokens, WORD, 'TO')
  outfile = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
  base = None
  colours = None
  idname = expression.Constant('id')
  dataname = expression.Constant('data')
  lowerBound = None
  higherBound = None
  legend = None
  title = expression.Constant('', base_token)
  header = expression.Constant(
      'Obliczenia i opracowanie mapy:\nMałgorzata i Jakub Onufry Wojtaszczyk',
      base_token)
  while TryPop(tokens, WORD, 'WITH'):
    if TryPop(tokens, WORD, 'BASE'):
      base = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
    elif TryPop(tokens, WORD, 'COLOURS'):
      colours = ForcePop(tokens, QUOTED).value
    elif TryPop(tokens, WORD, 'ID'):
      idname = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
    elif TryPop(tokens, WORD, 'DATA'):
      dataname = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
    elif TryPop(tokens, WORD, 'LOWER'):
      ForcePop(tokens, WORD, 'BOUND')
      lowerBound = ForcePop(tokens, NUMBER).value
    elif TryPop(tokens, WORD, 'HIGHER'):
      ForcePop(tokens, WORD, 'BOUND')
      higherBound = ForcePop(tokens, NUMBER).value
    elif TryPop(tokens, WORD, 'TITLE'):
      title = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
    elif TryPop(tokens, WORD, 'HEADER'):
      header = GetExpression(tokens, {WORDS_AS_CONSTANTS: True})
    elif TryPop(tokens, WORD, 'LEGEND'):
      legend = True
      if TryPop(tokens, WORD, 'NONE'):
        legend = False
    else:
      FailedPop(tokens, ['Invalid option for visualize'])
  if base is None:
    raise ValueError('Missing WITH BASE for VISUALIZE command in line', line)
  return command.Visualize(line, table, outfile, base, colours, idname,
                           dataname, lowerBound, higherBound, legend,
                           header, title)

def GetBody(tokens):
  if t := TryPop(tokens, WORD, 'LOAD'):
    return GetLoadTable(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'DUMP'):
    return GetDumpTable(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'IMPORT'):
    return GetImport(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'TRANSFORM'):
    return GetTransform(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'AGGREGATE'):
    return GetAggregate(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'JOIN'):
    return GetJoin(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'APPEND'):
    return GetAppend(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'PIVOT'):
    return GetPivot(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'DROP'):
    return GetDrop(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'VISUALIZE'):
    return GetVisualize(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'LIST'):
    return GetList(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'DESCRIBE'):
    return GetDescribe(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'FILTER'):
    return GetFilter(tokens, t.line)
  else:
    FailedPop(tokens, ['Expecting a command keyword.'])

def GetCommand(tokens):
  body = GetBody(tokens)
  ForcePop(tokens, SYMBOL, ';')
  return body

# Command grammar:
# command = body ;
# body = load_table | dump_table | transform_table | join_tables

####### File operations
# load_table = LOAD word FROM quoted_or_var 
#    [WITH SEPARATOR word]
#    [WITH IGNORE QUOTED SEPARATOR]
# dump_table = DUMP word [TO quoted_or_var]
#   (TODO: again, dumping options, default to SSV? Something else?)
#   (Allow 'quoted_or_var' to be STDOUT)
# import data = IMPORT quoted_or_var [WITH PREFIX word]
#                                    [WITH PARAM word quoted_or_var]
#                                    [WITH TABLE word_or_var]

####### Transformations
# transform = TRANSFORM word_or_variable [TO word_or_variable] WITH expr_list
# expr_list = expr | expr, expr_list
# expr = expression AS word | expression FOR range
# range = integer | integer: | :integer | integer:integer
# Missing "TO" means that the table is transformed in place.
# Expressions will be evaluated in a context where we can refer to
# column values
# Each 'expression AS word' clause produces a column named 'word' in the
# output table, where the value is the expression.
# Each 'expression FOR range' clause produces a set of columns, length of
# range, each named the same as it was in the original table.
# In expression, we can refer to columns by column_name (which has to be
# a valid variable name for that), by $column_name, or by $integer, where
# integer is the one-indexed index of the column. In the FOR expressions,
# we can also refer to the "currently processed" column as $?
# quoted_or_var = quoted | variable
# word_or_var = word | variable

####### Aggregations.
# aggregate = AGGREGATE word_or_variable [TO word_or_variable]
#     BY column_list WITH expr_list
# column_list = {empty} | var_or_word | var_or_word, column_list
# The column list is the "group by" clause.
# The expressions can also include aggregate functions.

####### Joins
# join = JOIN word_or_var INTO word_or_var ON expression comparator expression 
#            [WITH INSERT MISSING KEYS]
#            [WITH INSERT UNMATCHED VALUES]
#            [WITH RAISE UNMATCHED KEYS]
#            AS word_or_var
# comparator = EQ | PREFIX
#
# The assumption here is that every item in the right table has exactly
# one match (equality or prefix) in the left table. Or, in other words,
# the left table is the lookup source, and the right table does the lookups.
# WITH INSERT MISSING KEYS means that any key that doesn't get matched to some
#  value will be inserted, with empty strings as the values for all columns
#  from the right table.
# WITH INSERT UNMATCHED VALUES means that instead of throwing an exception,
#  we will insert a row with empty strings as values for columns from the left
#  table.
# WITH RAISE UNMATCHED KEYS means that an exception will be raised if any key
#  is not matched at least ones.

##### Append row
# append = APPEND expression_list TO word_or_var
# expression_list = expression | expression, expression_list
#
# Appends a row at the end of the table. Expressions should be constants.
# Length of expression list must match length of row in the table.

##### Pivot the table.
# pivot = PIVOT word_or_variable
#    [TO word_or_variable]
#    [WITH NEW_HEADERS_FROM word_or_variable]
#    [WITH OLD_HEADERS_TO word_or_variable]
#
# Transforms the table by making rows into columns, and columns into rows.
# The first option tells us which column is to be used as headers. The
# entries in this column have to be unique. If not chosen; the headers will
# just be 1, 2, 3...
# The second option tells us what should the name of the column containing
# the headers of the old table be (if unselected, no such column is created)
# The "TO" option gives the name of the output table. If not chosen, the
# pivot output overwrites the source table.

##### Drop a table, so that we can reuse the name.
# drop = DROP word_or_variable

##### Visualize a table, dumping it to a bmp file.
# visualize = VISUALIZE word_or_variable
#    TO quoted_or_variable
#    WITH BASE quoted_or_variable
#    [WITH COLOURS quoted]
#    [WITH ID word_or_variable]
#    [WITH DATA word_or_variable]
#    [WITH LOWER BOUND number]
#    [WITH HIGHER BOUND number]
#
# Dumps the table into a bmp file (the name is provided after TO). The base
# (and templates list) is the WITH BASE argument.
# If WITH COULOURS is provided, it should be a valid colour scheme.
# If WITH ID is provided, it is the name of the column containing the IDs
#   of the geographical areas; the values in that column must match the
#   names used by the chosen base. By default, the column name 'id' is used.
# If WITH DATA is provided, it is the name of the column containing the data
#   to visualize (which should be numbers). By default, 'data' is used.
# If WITH {LOWER / HIGHER} BOUND is provided, it is used at the lower or
#   higher bound for the data colour bands. For now, if you provide one,
#   you need to provide both.

def GetCommandList(lines):
  tokens = tokenizer.tokenize(lines)
  comms = []
  while tokens:
    comms.append(GetCommand(tokens))
  return command.Sequence(comms)
