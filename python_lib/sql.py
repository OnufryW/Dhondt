# This is an in-memory kinda SQL interpreter.
import math
import random

import tokenizer
import expression
import command
from tokens import *

# Types:
BOOL = 'bool'
INT = 'integer'
FLOAT = 'real number'
STRING = 'string'

ANY = [BOOL, INT, FLOAT, STRING]

BOOL_1 = lambda a : BOOL
INT_1 = lambda a : INT
FLOAT_1 = lambda a : FLOAT
MIRROR_1 = lambda a : a

STRING_2 = lambda a, b: STRING
BOOL_2 = lambda a, b: BOOL

STRING_3 = lambda a, b, c: STRING

NUMERIC = lambda a, b: INT if a == INT and b == INT else FLOAT

def assert_and_return(x):
  assert(x)
  return x

UNARY_FUNCTIONS = {
  'sqrt': (lambda a: math.sqrt(a), [INT, FLOAT], FLOAT_1),
  'int': (lambda a: int(a), [INT, FLOAT, STRING], INT_1),
  'len': (lambda a: len(a), [STRING], INT_1),
  'not': (lambda a: not a, [BOOL], BOOL_1),
  'abs': (lambda a: abs(a), [INT, FLOAT], MIRROR_1),
  'assert': (assert_and_return, [BOOL], BOOL_1)
}
BINARY_FUNCTIONS = {
  'min': (lambda a, b: min(a,b), [INT, FLOAT], [INT, FLOAT], NUMERIC),
  'beginning': (lambda a, b: a[:b], [STRING], [INT], STRING_2),
  'end': (lambda a, b: a[b:], [STRING], [INT], STRING_2),
  'and': (lambda a, b: a and b, [BOOL], [BOOL], BOOL_2),
  'or': (lambda a, b: a or b, [BOOL], [BOOL], BOOL_2),
  'startswith': (lambda a, b: a.startswith(b), [STRING], [STRING], BOOL_2),
  'contains': (lambda a, b: b in a, [STRING], [STRING], BOOL_2)
}
TERNARY_FUNCTIONS = {
  'if': ('SPECIAL', [BOOL], ANY, ANY, lambda a, b, c: b),
  'substr': (lambda a, b, c: a[b:c], [STRING], [INT], [INT], STRING_3),
  'replace': (lambda a, b, c: a.replace(b, c), [STRING], [STRING], [STRING],
              STRING_3)
}
# For now, since the range functions are applied straight to columns, the
# allowed input types are ignored.
RANGE_FUNCTIONS = {
  'concat_range': ('', lambda a, b: a + b, [STRING], [STRING]),
  'sum_range': (0, lambda a, b: a + b, [INT, FLOAT], [INT, FLOAT]),
  'and_range': (True, lambda a, b: a and b, [BOOL], [BOOL]),
}
AGGREGATE_FUNCTIONS = {
  'sum': (0, lambda a, b: a + b, [INT, FLOAT], MIRROR_1),
  'max': (None, lambda a, b: b if a is None else max(a,b), 
          [INT, FLOAT, STRING], MIRROR_1),
  'and': (0, lambda a, b: a + b, [BOOL], MIRROR_1),
}

# Calculates the possible output types of a function.
# Say the function has k arguments. Then intypes is a list of length k,
# the i-th element is a list of accepted types of the i-th argument.
# Argtypes is also a list, and the i-th element is the list of possible
# types of the i-th argument. And f is a function that takes k types, and
# returns the output type if the arguments are of those types.
def CalcTypesGeneric(intypes, argtypes, f):
  assert(len(intypes) == len(argtypes))
  if len(intypes) == 0:
    return [f()]
  res = set()
  for t in intypes[0]:
    if t in argtypes[0]:
      def prepacked_f(*args):
        return f(*(tuple([t] + list(args))))
      res.update(CalcTypesGeneric(intypes[1:], argtypes[1:], prepacked_f))
  return list(res)

def CalcType1(intypes, argtypes, f):
  return CalcTypesGeneric([intypes], [argtypes], f)

def CalcType2(intypes1, argtypes1, intypes2, argtypes2, f):
  return CalcTypesGeneric([intypes1, intypes2], [argtypes1, argtypes2], f)

def CalcType3(intypes1, argtypes1, intypes2, argtypes2, intypes3,
              argtypes3, f):
  return CalcTypesGeneric(
      [intypes1, intypes2, intypes3], [argtypes1, argtypes2, argtypes3], f)

SPECIAL_FUNCTIONS = {
  'niemeyer', 'dhondt', 'at', 'index', 'name', 'curr', 'currname', 'numcolumns'
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
    return (expression.Constant(int(token.value), token), [INT])
  else:
    return (expression.Constant(float(token.value), token), [FLOAT])

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
        arg = GetExpressionFull(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        f = UNARY_FUNCTIONS[token.value]
        typ = CalcType1(f[1], arg[1], f[2])
        return (expression.UnaryExpr(arg[0], f[0], token, token.value), typ)
      elif token.value in BINARY_FUNCTIONS:
        arg1 = GetExpressionFull(tokens, settings)
        ForcePop(tokens, SYMBOL, ',')
        arg2 = GetExpressionFull(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        f = BINARY_FUNCTIONS[token.value]
        typ = CalcType2(f[1], arg1[1], f[2], arg2[1], f[3])
        return (expression.BinaryExpr(
            arg1[0], arg2[0], f[0], token, token.value), typ)
      elif token.value in TERNARY_FUNCTIONS:
        arg1 = GetExpressionFull(tokens, settings)
        ForcePop(tokens, SYMBOL, ',')
        arg2 = GetExpressionFull(tokens, settings)
        ForcePop(tokens, SYMBOL, ',')
        arg3 = GetExpressionFull(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        f = TERNARY_FUNCTIONS[token.value]
        typ = CalcType3(f[1], arg1[1], f[2], arg2[1], f[3], arg3[1], f[4])
        if token.value == 'if':
          res = expression.If(arg1[0], arg2[0], arg3[0], token)
        else:
          res = expression.TernaryExpr(
              arg1[0], arg2[0], arg3[0], f[0], token, token.value)
        return (res, typ)
      elif token.value in RANGE_FUNCTIONS:
        beg, end = GetRange(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        f = RANGE_FUNCTIONS[token.value]
        return (expression.RangeExpr(
                    beg, end, (f[0], f[1]), token, token.value), f[3])
      elif token.value in ['dhondt', 'niemeyer']:
        exprtype = token.value
        seats = GetExpression(tokens, settings)
        ForcePop(tokens, SYMBOL, ',')
        votes = GetExpression(tokens, settings)
        ForcePop(tokens, SYMBOL, ',')
        beg, end = GetRange(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        if exprtype == 'dhondt':
          return (expression.DhondtExpr(seats, votes, beg, end, token), 
                  [INT])
        else:
          assert (exprtype == 'niemeyer')
          return (expression.NiemeyerExpr(seats, votes, beg, end, token),
                  [INT])
      elif token.value == 'curr':
        ForcePop(tokens, SYMBOL, ')')
        return (expression.CurrExpr(token), ANY)
      elif token.value == 'currname':
        ForcePop(tokens, SYMBOL, ')')
        return (expression.CurrNameExpr(token), [STRING])
      elif token.value == 'numcolumns':
        ForcePop(tokens, SYMBOL, ')')
        return (expression.NumColumnsExpr(token), [INT])
      elif token.value == 'at':
        arg = GetExpressionFull(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        return (expression.AtExpr(arg[0], token), ANY)
      elif token.value == 'index':
        arg = GetExpressionFull(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        return (expression.IndexExpr(arg[0], token), [INT])
      elif token.value == 'name':
        arg = GetExpressionFull(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        return (expression.NameExpr(arg[0], token), [STRING])
      elif token.value in AGGREGATE_FUNCTIONS:
        arg = GetExpressionFull(tokens, settings)
        ForcePop(tokens, SYMBOL, ')')
        f = AGGREGATE_FUNCTIONS[token.value]
        typ = CalcType1(f[2], arg[1], f[3])
        return (expression.AggregateExpr(arg[0], (f[0], f[1]), token, token.value), typ)
      InvalidToken(['Weird function name when trying to get factor'], token)
    elif token.value in KEYWORDS:
      InvalidToken(['Keyword when trying to get factor'], token)
    else:
      if settings[WORDS_AS_CONSTANTS]:
        return (expression.Constant(token.value, token), [STRING])
      return (expression.AtExpr(expression.Constant(token.value, token),
                  token), ANY)
  elif token.typ == PARAM:
    return (expression.ParamExpr(expression.Constant(token.value, token),
            token), [STRING])
  elif token.typ == SYMBOL:
    if token.value == '(':
      expr = GetExpressionFull(tokens, settings)
      ForcePop(tokens, SYMBOL, ')')
      return expr
    if token.value == '-':
      number_token = ForcePop(tokens, NUMBER)
      number = GetNumber(number_token)
      number[0].val = -number[0].val
      return number
    InvalidToken(['Unexpected symbol when trying to get factor'], token)
  elif token.typ == QUOTED:
    return (expression.Constant(token.value, token), [STRING])
  InvalidToken(['Unexpected token when trying to get factor'], token)

def GetProduct(tokens, settings):
  expr, typ = GetFactor(tokens, expect(settings, ANY))
  if INT not in typ and FLOAT not in typ:
    return (expr, typ)
  while tokens and tokens[0].typ == 'symbol' and tokens[0].value in '*/':
    typ = [t for t in typ if t == INT or t == FLOAT]
    token = ForcePop(tokens)
    rexpr, rtyp = GetFactor(tokens, settings)
    if INT not in rtyp and FLOAT not in rtyp:
      InvalidToken(['Can only divide and multiply numbers'], token)
    if FLOAT not in typ and FLOAT not in rtyp:
      typ = [INT]
    elif INT not in typ and FLOAT not in rtyp:
      typ = [FLOAT]
    else:
      typ = [INT, FLOAT]
    if token.value == '*':
      expr = expression.Product(expr, rexpr, token)
    else:
      expr = expression.Quotient(expr, rexpr, token)
  return (expr, typ)

def GetSum(tokens, settings):
  expr, typ = GetProduct(tokens, expect(settings, ANY))
  typ = [t for t in typ if t in settings[EXPECTED_TYPES]]
  if INT not in typ and FLOAT not in typ and STRING not in typ:
    return (expr, typ)
  while tokens and tokens[0].typ == 'symbol' and tokens[0].value in '+-':
    typ = [t for t in typ for t in [INT, FLOAT, STRING]]
    token = ForcePop(tokens)
    rexpr, rtyp = GetProduct(tokens, settings)
    ftyp = []
    if STRING in typ and STRING in rtyp and token.value == '+':
      ftyp.append(STRING)
    if INT in typ and INT in rtyp:
      ftyp.append(INT)
    if ((FLOAT in typ and (FLOAT in rtyp or INT in rtyp)) or
        (FLOAT in rtyp and (FLOAT in typ or INT in typ))):
      ftyp.append(FLOAT)
    if not ftyp:
      InvalidToken(['Can only add strings or numbers'], token)
    typ = ftyp
    if token.value == '+':
      expr = expression.Sum(expr, rexpr, token)
    else:
      expr = expression.Difference(expr, rexpr, token)
  return (expr, typ)

def GetComparison(tokens, settings):
  expr, typ = GetSum(tokens, expect(settings, ANY))
  if (tokens and tokens[0].typ == 'symbol' and tokens[0].value in '<=>' and
      BOOL in settings[EXPECTED_TYPES]):
    token = ForcePop(tokens)
    # TODO: I could do more string checks here; I don't accept any types.
    rexpr, _ = GetSum(tokens, expect(settings, ANY))
    if token.value == '=':
      return (expression.Equal(expr, rexpr, token), [BOOL])
    elif token.value == '<':
      return (expression.Lesser(expr, rexpr, token), [BOOL])
    else:
      return (expression.Greater(expr, rexpr, token), [BOOL])
  return (expr, typ)

def GetExpressionFull(tokens, settings):
  token = tokens[0]
  res, typ = GetComparison(tokens, settings)
  return (res, typ)

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
EXPECTED_TYPES = 'expected_types'

def lcompatible(typ):
  res = typ[:]
  if INT in typ and FLOAT not in typ:
    res.append(FLOAT)
  if FLOAT in typ and INT not in typ:
    res.append(INT)
  return res

def compatible(typ):
  if typ == INT or typ == FLOAT: return [INT, FLOAT]
  return [typ]

def expect(settings, expected_types):
  return {WORDS_AS_CONSTANTS: settings[WORDS_AS_CONSTANTS],
          EXPECTED_TYPES: expected_types}

def GetExpression(tokens, settings):
  token = tokens[0]
  if EXPECTED_TYPES not in settings:
    settings[EXPECTED_TYPES] = ANY
  if WORDS_AS_CONSTANTS not in settings:
    settings[WORDS_AS_CONSTANTS] = False
  expr, typ = GetExpressionFull(tokens, settings)
  accepted_typ = [t for t in typ if t in settings[EXPECTED_TYPES]]
  if not accepted_typ:
    raise InvalidToken([
        'Type mismatch, expected one of {}, got one of {}'.format(
            settings[EXPECTED_TYPES], typ)], token)
  return expr

#----------------------------------------------------------------------#
QUOTED_STRING = {WORDS_AS_CONSTANTS: False, EXPECTED_TYPES: [STRING]}
UNQUOTED_STRING = {WORDS_AS_CONSTANTS: True, EXPECTED_TYPES: [STRING]}

def GetLoadTable(tokens, line):
  name = ForcePop(tokens, WORD).value
  ForcePop(tokens, WORD, 'FROM')
  path = GetExpression(tokens, UNQUOTED_STRING)
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
  name = GetExpression(tokens, UNQUOTED_STRING)
  if TryPop(tokens, WORD, 'TO'):
    path = GetExpression(tokens, UNQUOTED_STRING)
  else:
    path = expression.Constant('stdout', tokens[0])
  return command.Dump(line, name, path)

def GetPrint(tokens, line):
  expr = GetExpression(tokens, UNQUOTED_STRING)
  if TryPop(tokens, WORD, 'TO'):
    path = GetExpression(tokens, UNQUOTED_STRING)
  else:
    path = expression.Constant('stdout', tokens[0])
  return command.Print(line, expr, path)


def GetRunSource(tokens):
  line = tokens[0].line
  if TryPop(tokens, WORD, 'FILE'):
    return ('FILE', GetExpression(tokens, QUOTED_STRING), line)
  elif TryPop(tokens, WORD, 'COMMAND'):
    return ('COMMAND', GetExpression(tokens, QUOTED_STRING), line)
  else:
    return ('TABLE', GetExpression(tokens, UNQUOTED_STRING), line)

def GetRun(tokens, line):
  runnables = []
  random_names = []
  storedtoken = tokens[0]
  while True:
    storedtoken = tokens[0]
    source = GetRunSource(tokens)
    runnable = {'INPUT': source, 'FROM': [], 'INTO': None, 'PARAMS': {},
                'PARAM_PREFIX': expression.Constant('', storedtoken),
                'LINE': storedtoken.line}
    param_prefix_set = False
    while True:
      if token := TryPop(tokens, WORD, 'FROM'):
        if runnable['FROM']:
          FailedPop(tokens, 'A RUN clause has multiple FROM clauses')
        inputs = []
        while True:
          inputs.append(GetRunSource(tokens))
          if not TryPop(tokens, SYMBOL, ','):
            break
        runnable['FROM'] = inputs
        continue
      elif token := TryPop(tokens, WORD, 'INTO'):
        if runnable['INTO']:
          FailedPop(tokens, 'A RUN clause has multiple INTO clauses')
        runnable['INTO'] = GetExpression(tokens, UNQUOTED_STRING)
        continue
      elif token := TryPop(tokens, WORD, 'WITH'):
        if token := TryPop(tokens, WORD, 'PARAM'):
          key = ForcePop(tokens, WORD).value
          if key in runnable['PARAMS']:
            FailedPop(tokens,
                'Parameter {} defined twice in RUN clause'.format(key))
          val = GetExpression(tokens, UNQUOTED_STRING)
          runnable['PARAMS'][key] = val
        elif token := TryPop(tokens, WORD, 'PARAM_PREFIX'):
          if param_prefix_set:
            FailedPop(tokens,
                      'Parameter prefix defined twice in run clause')
          param_prefix_set = True
          runnable['PARAM_PREFIX'] = GetExpression(tokens, UNQUOTED_STRING)
        else:
          FailedPop(tokens, ['Invalid optional argument to RUN'])
        continue
      break
    if runnables:
      random_name = '__input_table_' + ''.join([
          random.choice('0123456789') for _ in range(6)])
      if runnables[-1]['INTO']:
        FailedPop(tokens, 
            'Only the last entry in a RUN stream can have an INTO clause')
      if runnable['FROM']:
        FailedPop(tokens,
            'Only the first entry in a RUN stream can have a FROM clause')
      runnables[-1]['INTO'] = expression.Constant(random_name, storedtoken)
      runnable['FROM'].append(
          ('TABLE', expression.Constant(random_name, storedtoken),
           runnable['LINE']))
      random_names.append(random_name)
    runnables.append(runnable)
    if TryPop(tokens, SYMBOL, '>'):
      continue
    break
  return command.Run(line, runnables, random_names, GetCommandList)

def GetImport(tokens, line):
  path = GetExpression(tokens, UNQUOTED_STRING)
  options = {command.PREFIX: expression.Constant('', tokens[0]),
             command.EXTRA_PARAMS: {},
             command.EXTRA_TABLES: [],
             command.PARAM_PREFIX: expression.Constant('', tokens[0]),
             command.TARGET_TABLE: None}
  while token := TryPop(tokens, WORD, 'WITH'):
    if TryPop(tokens, WORD, 'PREFIX'):
      prefix = GetExpression(tokens, UNQUOTED_STRING)
      options[command.PREFIX] = prefix
    elif TryPop(tokens, WORD, 'PARAM'):
      key = ForcePop(tokens, WORD)
      val = GetExpression(tokens, UNQUOTED_STRING)
      options[command.EXTRA_PARAMS][key.value] = val
    elif TryPop(tokens, WORD, 'TABLE'):
      table_name = GetExpression(tokens, UNQUOTED_STRING)
      options[command.EXTRA_TABLES].append(table_name)
    elif TryPop(tokens, WORD, 'PARAM_PREFIX'):
      prefix = GetExpression(tokens, UNQUOTED_STRING)
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
      columnname = GetExpression(tokens, UNQUOTED_STRING)
      expr_list.append(command.SingleExpression(expr, columnname))
    else:
      range_begin, range_end = GetRange(tokens, {})
      header_expr = expression.CurrNameExpr(asorfor)
      if TryPop(tokens, WORD, 'AS'):
        header_expr = GetExpression(tokens, UNQUOTED_STRING)
      expr_list.append(command.RangeExpression(
          expr, range_begin, range_end, header_expr))
    if TryPop(tokens, SYMBOL, ',') is None:
      return expr_list

def GetTransform(tokens, line):
  source_table = GetExpression(tokens, UNQUOTED_STRING)
  target_table = None
  if TryPop(tokens, WORD, 'TO'):
    target_table = GetExpression(tokens, UNQUOTED_STRING)
  ForcePop(tokens, WORD, 'WITH')
  expr_list = GetExprList(tokens)
  return command.Transform(line, source_table, target_table, expr_list)

def GetAggregate(tokens, line):
  source_table = GetExpression(tokens, UNQUOTED_STRING)
  target_table = None
  if TryPop(tokens, WORD, 'TO'):
    target_table = GetExpression(tokens, UNQUOTED_STRING)
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
  left_table = GetExpression(tokens, UNQUOTED_STRING)
  ForcePop(tokens, WORD, 'INTO')
  right_table = GetExpression(tokens, UNQUOTED_STRING)
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
  target_table = GetExpression(tokens, UNQUOTED_STRING)
  return command.Join(line, left_table, right_table, target_table,
                      left_expr, right_expr, comparator, unmatched_keys,
                      unmatched_values)

def GetAppend(tokens, line):
  expr_list = [GetExpression(tokens, {})]
  while TryPop(tokens, SYMBOL, ','):
    expr_list.append(GetExpression(tokens, {}))
  ForcePop(tokens, WORD, 'TO')
  table = GetExpression(tokens, UNQUOTED_STRING)
  return command.Append(line, expr_list, table)

def GetPivot(tokens, line):
  table = GetExpression(tokens, UNQUOTED_STRING)
  target = None
  headers_from = None
  headers_to = None
  if TryPop(tokens, WORD, 'TO'):
    target = GetExpression(tokens, UNQUOTED_STRING)
  while TryPop(tokens, WORD, 'WITH'):
    if TryPop(tokens, WORD, 'NEW_HEADERS_FROM'):
      headers_from = GetExpression(tokens, UNQUOTED_STRING)
    elif TryPop(tokens, WORD, 'OLD_HEADERS_TO'):
      headers_to = GetExpression(tokens, UNQUOTED_STRING)
    else:
      FailedPop(tokens, ['Option for pivot'])
  return command.Pivot(line, table, target, headers_from, headers_to)

def GetFilter(tokens, line):
  table = GetExpression(tokens, UNQUOTED_STRING)
  target = None
  if TryPop(tokens, WORD, 'TO'):
    target = GetExpression(tokens, UNQUOTED_STRING)
  ForcePop(tokens, WORD, 'BY')
  expr = GetExpression(tokens, {})
  return command.Filter(line, table, target, expr)

def GetEmpty(tokens, line):
  ForcePop(tokens, WORD, 'AS')
  target = GetExpression(tokens, UNQUOTED_STRING)
  return command.Empty(line, target)

def GetUnion(tokens, line):
  sources = [GetExpression(tokens, UNQUOTED_STRING)]
  while TryPop(tokens, SYMBOL, ','):
    sources.append(GetExpression(tokens, UNQUOTED_STRING))
  ForcePop(tokens, WORD, 'TO')
  target = GetExpression(tokens, UNQUOTED_STRING)
  schema = 'EQUAL'
  if TryPop(tokens, WORD, 'WITH'):
    if TryPop(tokens, WORD, 'EQUAL'):
      ForcePop(tokens, WORD, 'SCHEMA')
      schema = 'EQUAL'
    elif TryPop(tokens, WORD, 'REORDERED'):
      ForcePop(tokens, WORD, 'SCHEMA')
      schema = 'REORDERED'
    elif TryPop(tokens, WORD, 'SKIP'):
      ForcePop(tokens, WORD, 'EXTRA')
      ForcePop(tokens, WORD, 'COLUMNS')
      schema = 'INTERSECTION'
    elif TryPop(tokens, WORD, 'ALL'):
      ForcePop(tokens, WORD, 'COLUMNS')
      schema = 'UNION'
    elif TryPop(tokens, WORD, 'FIRST'):
      ForcePop(tokens, WORD, 'TABLE')
      ForcePop(tokens, WORD, 'COLUMNS')
      schema = 'FIRST'
  return command.Union(line, sources, target, schema)

def GetDrop(tokens, line):
  table = GetExpression(tokens, UNQUOTED_STRING)
  return command.Drop(line, table)

def GetInput(tokens, line):
  ForcePop(tokens, WORD, 'TABLES')
  tables = []
  while True:
    table = GetExpression(tokens, UNQUOTED_STRING)
    tables.append(table)
    if not TryPop(tokens, SYMBOL, ','):
      break
  return command.Input(line, tables)

def GetOutput(tokens, line):
  ForcePop(tokens, WORD, 'TABLES')
  tables = []
  while True:
    table = GetExpression(tokens, UNQUOTED_STRING)
    tables.append(table)
    if not TryPop(tokens, SYMBOL, ','):
      break
  return command.Output(line, tables)

def GetList(tokens, line):
  ForcePop(tokens, WORD, 'TABLES')
  return command.List(line)

def GetDescribe(tokens, line):
  table = GetExpression(tokens, UNQUOTED_STRING)
  return command.Describe(line, table)

def GetVisualize(tokens, line):
  table = GetExpression(tokens, UNQUOTED_STRING)
  base_token = ForcePop(tokens, WORD, 'TO')
  outfile = GetExpression(tokens, UNQUOTED_STRING)
  base = None
  colours = None
  idname = expression.Constant('id', base_token)
  dataname = expression.Constant('data', base_token)
  lowerBound = None
  higherBound = None
  legend = None
  title = expression.Constant('', base_token)
  header = expression.Constant(
      'Obliczenia i opracowanie mapy:\nMałgorzata i Jakub Onufry Wojtaszczyk',
      base_token)
  while TryPop(tokens, WORD, 'WITH'):
    if TryPop(tokens, WORD, 'BASE'):
      base = GetExpression(tokens, UNQUOTED_STRING)
    elif TryPop(tokens, WORD, 'COLOURS'):
      colours = ForcePop(tokens, QUOTED).value
    elif TryPop(tokens, WORD, 'ID'):
      idname = GetExpression(tokens, UNQUOTED_STRING)
    elif TryPop(tokens, WORD, 'DATA'):
      dataname = GetExpression(tokens, UNQUOTED_STRING)
    elif TryPop(tokens, WORD, 'LOWER'):
      ForcePop(tokens, WORD, 'BOUND')
      lowerBound = ForcePop(tokens, NUMBER).value
    elif TryPop(tokens, WORD, 'HIGHER'):
      ForcePop(tokens, WORD, 'BOUND')
      higherBound = ForcePop(tokens, NUMBER).value
    elif TryPop(tokens, WORD, 'TITLE'):
      title = GetExpression(tokens, UNQUOTED_STRING)
    elif TryPop(tokens, WORD, 'HEADER'):
      header = GetExpression(tokens, UNQUOTED_STRING)
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
  elif t := TryPop(tokens, WORD, 'PRINT'):
    return GetPrint(tokens, t.line)
  # TODO: Remove IMPORT.
  elif t := TryPop(tokens, WORD, 'IMPORT'):
    return GetImport(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'RUN'):
    return GetRun(tokens, t.line)
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
  elif t := TryPop(tokens, WORD, 'INPUT'):
    return GetInput(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'OUTPUT'):
    return GetOutput(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'VISUALIZE'):
    return GetVisualize(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'LIST'):
    return GetList(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'DESCRIBE'):
    return GetDescribe(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'FILTER'):
    return GetFilter(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'EMPTY'):
    return GetEmpty(tokens, t.line)
  elif t := TryPop(tokens, WORD, 'UNION'):
    return GetUnion(tokens, t.line)
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
