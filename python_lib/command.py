# Defines an (implicit) command class that operates (and possibly modifies)
# the 'tables', which is implicitly a dict of in-memory tables (keyed by name).
# The internal representation of a table is a pair:
# - a dict (which maps column names to row indices, zero indexed)
# - a list of lists (the rows)
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
    self.line = line
    self.start = start
    self.end = end

  def Eval(self, params):
    if self.is_value:
      return self.variable_or_value
    else:
      if self.variable_or_value not in params:
        raise ValueError(
          'Failed to find paramter {} at line {}, positions {}:{}. Present parameters are {}'.format(
              self.variable_or_value, self.line, self.start, self.end,
              ' '.join(list(params.keys()))))
      return params[self.variable_or_value]

class Command:
  def __init__(self, line, command):
    self.line = line
    self.command = command

  def ErrorStr(self):
    return self.command + ' in line ' + str(self.line + 1)

class Load(Command):
  def __init__(self, line, name, path, options={}):
    super().__init__(line, 'LOAD')
    self.name = name
    self.path = path
    self.options = options
    # Defaults:
    if SEPARATOR not in options:
      options[SEPARATOR] = ';'
    if 'IGNORE QUOTED SEPARATOR' not in options:
      options['IGNORE QUOTED SEPARATOR'] = False

  def SplitQuotedLine(self, line, separator):
    res = []
    curquote = None
    curline = []
    for c in line:
      if c in ['\'', '"']:
        curline.append(c)
        if curquote == None:
          curquote = c
        elif curquote == c:
          curquote = None
      elif c == separator and curquote is None:
        res.append(''.join(curline).strip())
        curline = []
      else:
        curline.append(c)
    res.append(''.join(curline).strip())
    return res

  # Headered SSV file, rectangle-shaped.
  # TODO: add option for separator, possibly also header presense, and
  # maybe more table shapes?
  def ReadLines(self, lines):
    header_row_parsed = False
    rows = []
    for row_number, row in enumerate(lines):
      if not row or row[0] == '#':
        continue
      if self.options['IGNORE QUOTED SEPARATOR']:
        r = self.SplitQuotedLine(row, self.options[SEPARATOR])
      else:
        r = [v.strip() for v in row.split(self.options[SEPARATOR])]
      if not header_row_parsed:
        header = {}
        for i, v in enumerate(r):
          header[v] = i
        header_row_parsed = True
        continue
      if len(r) != len(header):
        raise ValueError(
            'FAILED {}: Line {} has length {}, header has length {}'.format(
                self.ErrorStr(), row_number, len(r), len(header)), header,
                r)
      rows.append(r)
    if header is None:
      raise ValueError('FAILED {}: No lines in file'.format(self.ErrorStr()))
    return (header, rows)

  def Eval(self, tables, params):
    assert self.name not in tables
    path = self.path.Eval(params)
    with open(path, 'r') as inf:
      tables[self.name] = self.ReadLines(inf.readlines())

class Dump(Command):
  def __init__(self, line, name, path, options={}):
    super().__init__(line, 'DUMP')
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
  def Eval(self, tables, params):
    name = self.name.Eval(params)
    path = self.path.Eval(params)
    if name not in tables:
      raise ValueError(self.ErrorStr(),
          'Name "{}" not in tables: {}'.format(
              name, tables.keys()))
    assert name in tables
    header, rows = tables[name]
    if path == 'stdout':
      self.WriteLines(header, rows, sys.stdout)
    else:
      with open(path, 'x') as outf:
        self.WriteLines(header, rows, outf)

# A sequence of commands to be executed one by one.
class Sequence:
  def __init__(self, seq):
    self.seq = seq

  def Eval(self, tables, params):
    for comm in self.seq:
      comm.Eval(tables, params)

# A request to execute another file. The parser is passed in, because
# there's a circular dependency here I need to resolve somehow.
class Import(Command):
  def __init__(self, line, path, options, parser):
    super().__init__(line, 'IMPORT')
    self.path = path
    self.parser = parser
    self.prefix = '' if PREFIX not in options else options[PREFIX]
    self.extra_params = (
        {} if EXTRA_PARAMS not in options else options[EXTRA_PARAMS])
    self.extra_tables = (
        [] if EXTRA_TABLES not in options else options[EXTRA_TABLES])

  def Eval(self, tables, params):
    path = self.path.Eval(params)
    # Step one: Parse the relevant file.
    with open(path, 'r') as config_file:
      try:
        child_command = self.parser(config_file.readlines())
      except Exception as e:
        raise ValueError(
            'FAILED {}: Failure parsing imported file {}'.format(
                self.ErrorStr(), path)) from e 
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
    # Step four: prepare child tables.
    child_tables = {}
    for table in self.extra_tables:
      table_name = table.Eval(params)
      assert table_name in tables
      child_tables[table_name] = tables[table_name]
    # Step five: actually execute child
    try:
      child_command.Eval(child_tables, child_params)
    except ValueError as e:
      raise ValueError('Failure in imported file ' + path) from e
    # Step six: roll back the directory shift
    os.chdir(oldpath)
    # Step seven: copy results of child execution into parent tables
    for table in child_tables:
      new_table_name = self.prefix + table
      assert new_table_name not in tables
      tables[new_table_name] = child_tables[table]

class SingleExpression:
  def __init__(self, expr, columnname):
    self.expr = expr
    self.columnname = columnname

  def AppendHeader(self, new_header, old_header):
    assert self.columnname not in new_header
    new_header[self.columnname] = len(new_header)

  def AppendValues(self, context, row, header, input_row):
    context['$$last'] = len(header) + 1
    try:
      row.append(self.expr.Eval(context))
    except Exception as e:
      msg = 'Failure evaluating {} (column {}) for row {}'
      raise ValueError(msg.format(
          self.columnname, len(row) + 1, input_row)) from e

class RangeExpression:
  def __init__(self, expr, range_beg, range_end, header_expr):
    self.expr = expr
    self.range_beg = range_beg - 1
    self.range_end = range_end - 1
    self.header_expr = header_expr

  def AppendHeader(self, new_header, old_header):
    old_header_rev = {}
    for x in old_header:
      old_header_rev[old_header[x]] = x
    self.range_end = self.range_end if self.range_end >= 0 else len(old_header)
    for col in range(self.range_beg, self.range_end):
      col_header = old_header_rev[col]
      if self.header_expr is not None:
        context = {'?header': col_header}
        col_header = self.header_expr.Eval(context)
      new_header[col_header] = len(new_header)

  def AppendValues(self, context, row, header, input_row):
    if '__dynamic' not in context:
      context['__dynamic'] = {}
    header_rev = {}
    for name in header:
      header_rev[header[name]] = name
    for x in range(self.range_beg, self.range_end):
      context['__dynamic']['?'] = str(x + 1)
      context['?header'] = header_rev[x]
      context['$$last'] = len(header) + 1
      try:
        row.append(self.expr.Eval(context))
      except Exception as e:
        msg = 'Failure evaluating {} (column {} in range {}-{}) for row {}'
        raise ValueError(msg.format(header_rev[x], x+1, self.range_beg+1,
                                    self.range_end+1, input_row)) from e
    del context['__dynamic']['?']

def SourceAndTarget(source, target, tables, params):
  source_table = source.Eval(params)
  assert source_table in tables
  if target is not None:
    target_table = target.Eval(params)
    assert target_table not in tables
  else:
    target_table = source_table
  return source_table, target_table

def RowContext(row, header):
  context = {}
  for i in range(len(row)):
    context[str(i+1)] = row[i]
  for x in header:
    context[x] = row[header[x]]
  return context

class Transform(Command):
  def __init__(self, line, source_table, target_table, expr_list):
    super().__init__(line, 'TRANSFORM')
    self.source_table = source_table
    self.target_table = target_table
    self.expr_list = expr_list

  def Eval(self, tables, params):
    source_table, target_table = SourceAndTarget(
        self.source_table, self.target_table, tables, params)
    header, rows = tables[source_table]
    new_header = {}
    for expr in self.expr_list:
      expr.AppendHeader(new_header, header)
    new_rows = []
    for row in rows:
      new_row = []
      assert len(row) == len(header)
      # Construct the expression evaluation context
      for expr in self.expr_list:
        expr.AppendValues(RowContext(row, header), new_row, header, row)
      assert len(new_row) == len(new_header)
      new_rows.append(new_row)
    tables[target_table] = (new_header, new_rows)

class Aggregate(Command):
  def __init__(self, line, source_table, target_table, group_list, expr_list):
    super().__init__(line, 'TRANSFORM')
    self.source_table = source_table
    self.target_table = target_table
    self.group_list = group_list
    self.expr_list = expr_list

  def Eval(self, tables, params):
    source_table, target_table = SourceAndTarget(
        self.source_table, self.target_table, tables, params)
    header, rows = tables[source_table]

    # Define the new header.
    new_header = {}
    for expr in self.expr_list:
      expr.AppendHeader(new_header, header)

    # Accumulate the set of group keys.
    group_keys = set()
    for group_key in self.group_list:
      if isinstance(group_key, int):
        group_keys.add(group_key - 1)
      else:
        assert group_key in header
        group_keys.add(header[group_key])

    # Accumulate the set of groups, and rows associated with each.
    groups = {}
    for row in rows:
      agg_key = tuple([row[key] for key in group_keys])
      if agg_key not in groups:
        groups[agg_key] = []
      groups[agg_key].append(row)
    
    # Calculate the new rows.
    new_rows = []
    for agg_key in groups:
      # Define the evaluation context.
      context = {'__group_context': [{} for _ in groups[agg_key]]}
      for column in header:
        col_num = header[column]
        if header[column] in group_keys:
          context[column] = groups[agg_key][0][col_num]
          context[str(col_num + 1)] = groups[agg_key][0][col_num]
        else:
          for i, row in enumerate(groups[agg_key]):
            row_context = context['__group_context'][i]
            row_context[column] = row[col_num]
            row_context[str(col_num + 1)] = row[col_num]
      # The 'debug' row value
      debug_row = [context[x] for x in context if x != '__group_context']
      # Calculate the expressions.
      new_row = []
      for expr in self.expr_list:
        # TODO:  
        expr.AppendValues(context, new_row, header, debug_row)
      assert len(new_row) == len(new_header)
      new_rows.append(new_row)

    tables[target_table] = (new_header, new_rows)

class Join(Command):
  def __init__(self, line, left_table, right_table, target_table,
               left_expr, right_expr, comparator, unmatched_keys,
               unmatched_values):
    super().__init__(line, 'JOIN')
    self.left_table = left_table
    self.right_table = right_table
    self.target_table = target_table
    self.left_expr = left_expr
    self.right_expr = right_expr
    self.comparator = comparator
    self.unmatched_keys = unmatched_keys
    self.unmatched_values = unmatched_values

  def FindRow(self, keys, key, left_table):
    for x in keys:
      empty_row = [''] * len(keys[x][0])
      break
    if self.comparator == 'EQ':
      if key not in keys:
        if self.unmatched_values:
          return empty_row
        raise ValueError(
            self.ErrorStr(), 'Failed to find key {} in table {}'.format(
                key, left_table))
      keys[key][1] = True
      return keys[key][0]
    elif self.comparator == 'PREFIX':
      found_prefix = None
      for preflen in range(len(key)+1):
        if key[:preflen] in keys:
          if found_prefix is not None:
            raise ValueError(
                self.ErrorStr(),
                'Found two prefixes matching {}: {} and {}'.format(
                    key, found_prefix, key[:preflen]))
          found_prefix = key[:preflen]
      if found_prefix is None:
        if self.unmatched_values:
          return empty_row
        raise ValueError(self.ErrorStr(),
                         'Failed to find prefix for key {}'.format(key))
      keys[found_prefix][1] = True
      return keys[found_prefix][0]

  def Eval(self, tables, params):
    left_table = self.left_table.Eval(params)
    right_table = self.right_table.Eval(params)
    target_table = self.target_table.Eval(params)
    assert left_table in tables
    left_header, left_rows = tables[left_table]
    assert right_table in tables
    right_header, right_rows = tables[right_table]
    assert target_table not in tables
    header = {}
    for column in left_header:
      header[column] = left_header[column]
    for column in right_header:
      header[column] = right_header[column] + len(left_header)
    keys = {}
    rows = []
    for row in left_rows:
      context = RowContext(row, left_header)
      keys[self.left_expr.Eval(context)] = [row, False]
    for row in right_rows:
      context = RowContext(row, right_header)
      key = self.right_expr.Eval(context)
      rows.append(self.FindRow(keys, key, left_table) + row)
    for row in right_rows:
      empty_row = [''] * len(row)
      break
    if self.unmatched_keys in ['RAISE', 'INCLUDE']:
      for key in keys:
        if not keys[key][1]:
          if self.unmatched_keys == 'INCLUDE':
            rows.append(keys[key][0] + empty_row)
          else:
            raise ValueError(
                self.ErrorStr(),
                'Key {} from {} not matched by any value'.format(
                    key, left_table))
    tables[target_table] = (header, rows)

class Append(Command):
  def __init__(self, line, expr_list, table):
    super().__init__(line, 'APPEND')
    self.expr_list = expr_list
    self.table = table

  def Eval(self, tables, params):
    table = self.table.Eval(params)
    if table not in tables:
      raise ValueError(self.ErrorStr(), 'Table {} not found'.format(table))
    row = []
    for expr in self.expr_list:
      row.append(expr.Eval({}))
    if len(row) != len(tables[table][0]):
      raise ValueError(
          self.ErrorStr(),
          'Provided {} values, while table {} has {} columns'.format(
              len(row), table, len(tables[table][0])))
    tables[table][1].append(row)

class Pivot(Command):
  def __init__(self, line, source, target, headers_from, headers_to):
    super().__init__(line, 'PIVOT')
    self.source = source
    self.target = target
    self.headers_from = headers_from
    self.headers_to = headers_to

  def Eval(self, tables, params):
    source, target = SourceAndTarget(
        self.source, self.target, tables, params)
    skipped_source_col = None
    header = {}
    rows = []
    # Prepare the new header lambda, and the skipped row.
    if self.headers_from:
      headers_from = self.headers_from.Eval(params)
      if headers_from not in tables[source][0]:
        raise ValueError(
          self.ErrorStr(),
          'Source table {} does not have requested header column {}'.format(
              source, headers_from))
      header_column_index = tables[source][0][headers_from]
      skipped_source_col = header_column_index
      header_for_row = lambda i, row: row[header_column_index]
    else:
      header_for_row = lambda i, row: 'col_' + str(i+1)
    # Prepare empty new rows (one per old column, potentially minus headers)
    for _ in tables[source][0]:
      rows.append([])
    if skipped_source_col is not None:
      rows.pop()
    def target_row(source_col):
      if skipped_source_col is None:
        return source_col
      if source_col < skipped_source_col:
        return source_col
      elif source_col == skipped_source_col:
        return None
      else:
        return source_col - 1
    # Construct the headers column
    if self.headers_to:
      headers_to = self.headers_to.Eval(params)
      header[headers_to] = 0
      for h in tables[source][0]:
        if target_row(tables[source][0][h]) is not None:
          rows[target_row(tables[source][0][h])].append(h)
    # Construct the headers and the rest of the rows.
    for i, row in enumerate(tables[source][1]):
      h = header_for_row(i, row)
      if h in header.keys():
        raise ValueError(
            'Header column {} contains duplicate key {} in row {}'.format(
                headers_from, h, i))
      header[h] = i if self.headers_to is None else i + 1
      for j, val in enumerate(row):
        if target_row(j) is not None:
          rows[target_row(j)].append(val)
    tables[target] = (header, rows)
   
