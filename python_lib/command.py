# Defines an (implicit) command class that operates (and possibly modifies)
# the context, which is implicitly a dict of in-memory tables (keyed by name).
# The internal representation of a table is a pair:
# - a list of lists (the rows)
# - a dict (which maps column names to row indices, zero indexed)
#
# Commands also take 'params', which are a string-to-string mapping
# of parameters that affect execution.

import os
import sys

SEPARATOR = 'separator'
PREFIX = 'prefix'
EXTRA_PARAMS = 'extra_params'
EXTRA_TABLES = 'extra_tables'

class VariableOrValue:
  def __init__(self, variable_or_value, is_value, line, start, end):
    self.variable_or_value = variable_or_value
    self.is_value = is_value

  def Eval(self, params):
    if self.is_value:
      return self.variable_or_value
    else:
      if self.variable_or_value not in params:
        raise ValueError(
          'Failed to find paramter {} at line {}, positions {}:{}',
          'Present parameters are {}'.format(
              self.variable_or_value, self.line, self.start, self.end,
              ' '.join(list(params.keys()))))
      return params[self.variable_or_value]

class Load:
  def __init__(self, name, path, options={}):
    self.name = name
    self.path = path
    self.options = options
    # Defaults:
    if SEPARATOR not in options:
      options[SEPARATOR] = ';'

  # Headered SSV file, rectangle-shaped.
  # TODO: add option for separator, possibly also header presense, and
  # maybe more table shapes?
  def ReadLines(self, lines):
    header_row_parsed = False
    rows = []
    for row in lines:
      if not row or row[0] == '#':
        continue
      r = [v.strip() for v in row.split(self.options[SEPARATOR])]
      if not header_row_parsed:
        header = {}
        for i, v in enumerate(r):
          header[v] = i
        header_row_parsed = True
        continue
      assert len(r) == len(header)
      rows.append(r)
    assert header is not None
    return (header, rows)

  def Eval(self, context, params):
    assert self.name not in context
    path = self.path.Eval(params)
    with open(path, 'r') as inf:
      context[self.name] = self.ReadLines(inf.readlines())

class Dump:
  def __init__(self, name, path, options={}):
    self.name = name
    self.path = path
    self.options = options
    # Defaults:
    if SEPARATOR not in options:
      options[SEPARATOR] = ';'

  def WriteLines(self, header, rows, outf):
    outf.write(self.options[SEPARATOR].join(header) + '\n')
    for row in rows:
      outf.write(self.options[SEPARATOR].join([str(x) for x in row]) + '\n')

  # Dump into a headered SSV file
  def Eval(self, context, params):
    name = self.name.Eval(params)
    path = self.path.Eval(params)
    assert name in context
    header, rows = context[name]
    if path == 'stdout':
      self.WriteLines(header, rows, sys.stdout)
    else:
      with open(path, 'x') as outf:
        self.WriteLines(header, rows, outf)

# A sequence of commands to be executed one by one.
class Sequence:
  def __init__(self, seq):
    self.seq = seq

  def Eval(self, context, params):
    for comm in self.seq:
      comm.Eval(context, params)

# A request to execute another file. The parser is passed in, because
# there's a circular dependency here I need to resolve somehow.
class Import:
  def __init__(self, path, options, parser):
    self.path = path
    self.parser = parser
    self.prefix = '' if PREFIX not in options else options[PREFIX]
    self.extra_params = (
        {} if EXTRA_PARAMS not in options else options[EXTRA_PARAMS])
    self.extra_tables = (
        [] if EXTRA_TABLES not in options else options[EXTRA_TABLES])

  def Eval(self, context, params):
    path = self.path.Eval(params)
    # Step one: Parse the relevant file.
    with open(path, 'r') as config_file:
      child_command = self.parser(config_file.readlines())
    # Step two: prepare the new parameters for the execution.
    child_params = {}
    # TODO: consider an option where we're explicitly not passing params in
    for param in params:
      child_params[param] = params[param]
    for param in self.extra_params:
      child_params[param] = self.extra_params[param].Eval(params)
    # Step three: prepare to shift directory
    rootpath = os.path.dirname(os.path.abspath(path))
    oldpath = os.getcwd()
    os.chdir(rootpath)
    # Step four: prepare child context.
    child_context = {}
    for table in self.extra_tables:
      table_name = table.Eval(params)
      assert table_name in context
      child_context[table_name] = context[table_name]
    # Step five: actually execute child
    child_command.Eval(child_context, child_params)
    # Step six: roll back the directory shift
    os.chdir(oldpath)
    # Step seven: copy results of child execution into parent context
    for table in child_context:
      new_table_name = self.prefix + table
      assert new_table_name not in context
      context[new_table_name] = child_context[table]

class SingleExpression:
  def __init__(self, expr, columnname):
    self.expr = expr
    self.columnname = columnname

  def AppendHeader(self, new_header, old_header):
    assert self.columnname not in new_header
    new_header[self.columnname] = len(new_header)

  def AppendValues(self, context, row, header, input_row):
    try:
      row.append(self.expr.Eval(context))
    except Exception as e:
      msg = 'Failure evaluating {} (column {}) for row {}'
      raise ValueError(msg.format(
          self.columnname, len(row) + 1, input_row)) from e

class RangeExpression:
  def __init__(self, expr, range_beg, range_end):
    self.expr = expr
    self.range_beg = range_beg - 1
    self.range_end = range_end - 1

  def AppendHeader(self, new_header, old_header):
    old_header_rev = {}
    for x in old_header:
      old_header_rev[old_header[x]] = x
    self.range_end = self.range_end if self.range_end >= 0 else len(old_header)
    for col in range(self.range_beg, self.range_end):
      new_header[old_header_rev[col]] = len(new_header)

  def AppendValues(self, context, row, header, input_row):
    for x in range(self.range_beg, self.range_end):
      context['?'] = context[str(x + 1)]
      try:
        row.append(self.expr.Eval(context))
      except Exception as e:
        header_rev = {}
        for name in header:
          header_rev[header[name]] = name
        msg = 'Failure evaluating {} (column {} in range {}-{}) for row {}'
        raise ValueError(msg.format(header_rev[x], x+1, self.range_beg+1,
                                    self.range_end+1, input_row)) from e
    del context['?']

def SourceAndTarget(source, target, context, params):
  source_table = source.Eval(params)
  assert source_table in context
  if target is not None:
    target_table = target.Eval(params)
    assert target_table not in context
  else:
    target_table = source_table
  return source_table, target_table

class Transform:
  def __init__(self, source_table, target_table, expr_list):
    self.source_table = source_table
    self.target_table = target_table
    self.expr_list = expr_list

  def Eval(self, context, params):
    source_table, target_table = SourceAndTarget(
        self.source_table, self.target_table, context, params)
    header, rows = context[source_table]
    new_header = {}
    for expr in self.expr_list:
      expr.AppendHeader(new_header, header)
    new_rows = []
    for row in rows:
      new_row = []
      assert len(row) == len(header)
      # Construct the expression evaluation context
      expr_context = {}
      for i in range(len(row)):
        expr_context[str(i+1)] = row[i]
      for x in header:
        expr_context[x] = row[header[x]]
      for expr in self.expr_list:
        expr.AppendValues(expr_context, new_row, header, row)
      assert len(new_row) == len(new_header)
      new_rows.append(new_row)
    context[target_table] = (new_header, new_rows)

class Aggregate:
  def __init__(self, source_table, target_table, group_list, expr_list):
    self.source_table = source_table
    self.target_table = target_table
    self.group_list = group_list
    self.expr_list = expr_list

  def Eval(self, context, params):
    source_table, target_table = SourceAndTarget(
        self.source_table, self.target_table, context, params)
    header, rows = context[source_table]
    reverse_header = {}
    for title in header:
      reverse_header[header[title]] = title  
    group_keys = []
    for group_key in self.group_list:
      if isinstance(group_key, int):
        group_keys.append((group_key - 1, reverse_header[group_key - 1]))
      else:
        group_keys.append((header[group_key], group_key))

    new_header = {}
    for expr in self.expr_list:
      expr.AppendHeader(new_header, header)
    new_rows = []

    # Aggregate
    groups = {}
    for row in rows:
      agg_key = []
      for key in group_keys:
        agg_key.append(row[key[0]])
      agg_key = tuple(agg_key)
      if agg_key not in groups:
        groups[agg_key] = []
      groups[agg_key].append(row)

    for agg_key in groups:
      # Construct the expression evaluation context
      expr_context = {}
      rows = groups[agg_key]
      # Add the group key columns to context.
      for group_key in group_keys:
        expr_context[str(group_key[0] + 1)] = rows[0][group_key[0]]
        expr_context[group_key[1]] = rows[0][group_key[0]]
      aggregates = {}
      for x in header:
        agglist = [r[header[x]] for r in rows]
        aggregates[x] = agglist
        aggregates[str(header[x] + 1)] = agglist
      expr_context['__aggregates'] = aggregates
      new_row = []
      for expr in self.expr_list:
        expr.AppendValues(expr_context, new_row, header, group_keys)
      assert len(new_row) == len(new_header)
      new_rows.append(new_row)
    context[target_table] = (new_header, new_rows)

