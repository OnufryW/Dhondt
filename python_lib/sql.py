# This is an in-memory kinda SQL interpreter.
import math

import tokenizer
import expression
import command
from tokens import *

UNARY_FUNCTIONS = {
  'sqrt': lambda a: math.sqrt(a),
  'int': lambda a: int(a),
}
BINARY_FUNCTIONS = {
  'min': lambda a, b: min(a,b)
}
TERNARY_FUNCTIONS = {
  'if': lambda a, b, c: b if a else c
}
FUNCTION_NAMES = list(UNARY_FUNCTIONS.keys()) + list(BINARY_FUNCTIONS.keys()) + list(TERNARY_FUNCTIONS.keys())
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

def InvalidToken(token, message):
  print(*message)
  print('Actual token is', token.value, 'of type', token.typ)
  assert False

def FailedPop(tokens, message):
  print(*message)
  if not tokens:
    print('Token list empty!')
  else:
    print('First token is', tokens[0].value, 'of type', tokens[0].typ)
  assert False

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

def GetFactor(tokens):
  token = ForcePop(tokens)
  if token.typ == NUMBER:
    if token.value.find('.') == -1:
      return expression.Constant(int(token.value))
    else:
      return expression.Constant(float(token.value))
  elif token.typ == WORD:
    if token.value in FUNCTION_NAMES:
      ForcePop(tokens, SYMBOL, '(')
      if token.value in UNARY_FUNCTIONS:
        arg = GetExpression(tokens)
        ForcePop(tokens, SYMBOL, ')')
        return expression.UnaryExpr(arg, UNARY_FUNCTIONS[token.value])
      elif token.value in BINARY_FUNCTIONS:
        arg1 = GetExpression(tokens)
        ForcePop(tokens, SYMBOL, ',')
        arg2 = GetExpression(tokens)
        ForcePop(tokens, SYMBOL, ')')
        return expression.BinaryExpr(arg1, arg2, BINARY_FUNCTIONS[token.value])
      elif token.value in TERNARY_FUNCTIONS:
        arg1 = GetExpression(tokens)
        ForcePop(tokens, SYMBOL, ',')
        arg2 = GetExpression(tokens)
        ForcePop(tokens, SYMBOL, ',')
        arg3 = GetExpression(tokens)
        ForcePop(tokens, SYMBOL, ')')
        return expression.TernaryExpr(arg1, arg2, arg3, TERNARY_FUNCTIONS[token.value])
      assert False
    elif token.value in KEYWORDS:
      assert False
    else:
      return expression.Variable(token.value)
  elif token.typ == VARIABLE:
    return expression.Variable(token.value)
  elif token.typ == SYMBOL:
    if token.value == '(':
      expr = GetExpression(tokens)
      ForcePop(tokens, SYMBOL, ')')
      return expr
    assert False
  elif token.typ == QUOTED:
    return expression.Constant(token.value)
  assert False

def GetProduct(tokens):
  left = GetFactor(tokens)
  while tokens and tokens[0].typ == 'symbol' and tokens[0].value in '*/':
    token = ForcePop(tokens).value
    right = GetFactor(tokens)
    if token == '*':
      left = expression.Product(left, right)
    else:
      left = expression.Quotient(left, right)
  return left

def GetSum(tokens):
  left = GetProduct(tokens)
  while tokens and tokens[0].typ == 'symbol' and tokens[0].value in '+-':
    token = ForcePop(tokens).value
    right = GetProduct(tokens)
    if token == '+':
      left = expression.Sum(left, right)
    else:
      left = expression.Difference(left, right)
  return left

def GetComparison(tokens):
  left = GetSum(tokens)
  if tokens and tokens[0].typ == 'symbol' and tokens[0].value in '<=>':
    token = ForcePop(tokens).value
    right = GetSum(tokens)
    if token == '=':
      return expression.Equal(left, right)
    elif token == '<':
      return expression.Lesser(left, right)
    else:
      return expression.Greater(left, right)
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
def GetExpression(tokens):
  return GetComparison(tokens)

#----------------------------------------------------------------------#

def GetOrVar(tokens, allowed_constant_types):
  token = ForcePop(tokens)
  if token.typ == VARIABLE:
    return command.VariableOrValue(token.value, False)
  else:
    if token.typ not in allowed_constant_types:
      InvalidToken(token, [
          'GetOrVar token expected types', allowed_constant_types])
    return command.VariableOrValue(token.value, True)

def GetQuotedOrVar(tokens):
  return GetOrVar(tokens, [QUOTED])

def GetWordOrVar(tokens):
  return GetOrVar(tokens, [WORD])

def GetWordOrQuoted(tokens):
  token = ForcePop(tokens)
  if token.typ not in [WORD, QUOTED]:
    InvalidToken(token, ['Expected word or quoted word'])
  return token.value

def GetLoadTable(tokens):
  name = ForcePop(tokens, WORD).value
  ForcePop(tokens, WORD, 'FROM')
  path = GetQuotedOrVar(tokens)
  options = {}
  while token := TryPop(tokens, WORD, 'WITH'):
    if token := TryPop(tokens, WORD, 'SEPARATOR'):
      options[command.SEPARATOR] = ForcePop(tokens, QUOTED).value
    else:
      FailedPop(tokens, ['Invalid optional argument to LOAD TABLE'])
  return command.Load(name, path, options)

def GetDumpTable(tokens):
  name = GetWordOrVar(tokens)
  ForcePop(tokens, WORD, 'TO')
  path = GetQuotedOrVar(tokens)
  return command.Dump(name, path)

def GetImport(tokens):
  path = GetQuotedOrVar(tokens)
  options = {}
  while token := TryPop(tokens, WORD, 'WITH'):
    if TryPop(tokens, WORD, 'PREFIX'):
      options[command.PREFIX] = GetWordOrQuoted(tokens)
    elif TryPop(tokens, WORD, 'PARAM'):
      key = ForcePop(tokens, WORD)
      val = GetQuotedOrVar(tokens)
      if command.EXTRA_PARAMS not in options:
        options[command.EXTRA_PARAMS] = {}
      options[command.EXTRA_PARAMS][key.value] = val
    else:
      FailedPop(tokens, ['Invalid optional argument to IMPORT'])
  return command.Import(path, options, GetCommandList)

def GetTransform(tokens):
  source_table = GetWordOrVar(tokens)
  ForcePop(tokens, WORD, 'TO')
  target_table = GetWordOrVar(tokens)
  ForcePop(tokens, WORD, 'WITH')
  expr_list = []
  while True:
    expr = GetExpression(tokens)
    asorfor = ForcePop(tokens, WORD)
    if asorfor.value not in ['AS', 'FOR']:
      InvalidToken(asorfor, ['The AS or FOR clause in an expression'])
    if asorfor.value == 'AS':
      columnname = ForcePop(tokens, WORD).value
      expr_list.append(command.SingleExpression(expr, columnname))
    else:
      range_begin_token = TryPop(tokens, NUMBER)
      range_begin = int(range_begin_token.value) if range_begin_token else 1
      ForcePop(tokens, SYMBOL, ':')
      range_end_token = TryPop(tokens, NUMBER)
      range_end = int(range_end_token.value) if range_end_token else -1
      expr_list.append(command.RangeExpression(expr, range_begin, range_end))
    if TryPop(tokens, SYMBOL, ',') is None:
      break
  return command.Transform(source_table, target_table, expr_list)


def GetBody(tokens):
  if TryPop(tokens, WORD, 'LOAD'):
    return GetLoadTable(tokens)
  elif TryPop(tokens, WORD, 'DUMP'):
    return GetDumpTable(tokens)
  elif TryPop(tokens, WORD, 'IMPORT'):
    return GetImport(tokens)
  elif TryPop(tokens, WORD, 'TRANSFORM'):
    return GetTransform(tokens)
  # TODO: Transforms, joins and aggregates go here.
  else:
    FailedPop(tokens, ['Invalid command'])

def GetCommand(tokens):
  body = GetBody(tokens)
  ForcePop(tokens, SYMBOL, ';')
  return body

# Command grammar:
# command = body ;
# body = load_table | dump_table | transform_table | join_tables
# load_table = LOAD word FROM quoted_or_var [WITH SEPARATOR word]
#   (TODO: loading options: with/without header? SSV format?)
# dump_table = DUMP word TO quoted_or_var
#   (TODO: again, dumping options, default to SSV? Something else?)
#   (Allow 'quoted_or_var' to be STDOUT)
# import data = IMPORT quoted_or_var [WITH PREFIX word]
#                                    [WITH PARAM word quoted_or_var]
# transform = TRANSFORM word_or_variable TO word_or_variable WITH expr_list
# expr_list = expr | expr, expr_list
# expr = expression AS word | expression FOR range
# range = integer | integer: | :integer | integer:integer
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

# TODO: aggregations
# TODO: pivoting the table.
# TODO join_tables = ...
#   (TODO: This, I think, is simpler, take two tables, create a table that
#    has the columns of both, joined by key, options requiring full/left/
#    right joins)

def GetCommandList(lines):
  to_tokenize = []
  for line in lines:
    line = line.strip()
    if not line or line[0] == '#':
      continue
    to_tokenize.append(line)
  tokens = tokenizer.tokenize('\n'.join(to_tokenize))
  comms = []
  while tokens:
    comms.append(GetCommand(tokens))
  return command.Sequence(comms)
