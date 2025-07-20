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
import visualize

SEPARATOR = 'separator'
PREFIX = 'prefix'
EXTRA_PARAMS = 'extra_params'
SOURCES = 'sources'
PARAM_PREFIX = 'param_prefix'
TARGET_TABLE = 'target_table'

INPUT_TABLES = '__input_table_names'

class Const:
  def __init__(self, value):
    self.value = value

  def Eval(self, params):
    return self.value

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

def ParamContext(params):
  return {'__params': params}

def RowContext(row, header, params):
  context = ParamContext(params)
  context['?last'] = len(header) + 1
  context['__data'] = row
  for x in header:
    context[x] = header[x] + 1
  return context

class Command:
  def __init__(self, line, command):
    self.line = line
    self.command = command

  def ErrorStr(self):
    return self.command + ' in line ' + str(self.line + 1)

  def Raise(self, msg):
    raise ValueError('FAILED ' + self.ErrorStr() + ': ', msg)

  def RaiseFrom(self, msg, e):
    raise ValueError('FAILED ' + self.ErrorStr() + ': ', msg, str(e)
        ).with_traceback(e.__traceback__) from None

  def Source(self, source, tables, params):
    source_table = source.Eval(ParamContext(params))
    if source_table not in tables:
      self.Raise('Source table {} not present in tables: {}'.format(
          source_table, tables.keys()))
    return source_table

  def SourceAndTarget(self, source, target, tables, params):
    source_table = self.Source(source, tables, params)
    if target is not None:
      target_table = target.Eval(ParamContext(params))
      if target_table in tables:
        self.Raise('Target table {} already present in tables!'.format(
            target_table))
    else:
      target_table = source_table
    return source_table, target_table


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
        self.Raise('Line {} has length {}, header has length {}'.format(
            row_number, len(r), len(header)))
      rows.append(r)
    if header is None:
      self.Raise('No lines in file')
    return (header, rows)

  def Eval(self, tables, params):
    assert self.name not in tables
    path = self.path.Eval(ParamContext(params))
    try:
      with open(path, 'r') as inf:
        tables[self.name] = self.ReadLines(inf.readlines())
    except BaseException as e:
      self.RaiseFrom('Failed to read from {}'.format(path), e)
    return []


class Empty(Command):
  def __init__(self, line, target):
    super().__init__(line, 'EMPTY')
    self.target = target

  def Eval(self, tables, params):
    target = self.target.Eval(ParamContext(params))
    if target in tables:
      self.Raise('Target table {} already present in tables!'.format(target))
    tables[target] = ({}, [])
    return []


class Union(Command):
  def __init__(self, line, sources, target, schema):
    super().__init__(line, 'UNION')
    self.sources = sources
    self.target = target
    self.schema = schema
    assert schema in ('EQUAL', 'REORDERED', 'INTERSECTION', 'UNION', 'FIRST')

  def ValidateHeadersMatch(self, tables, sources, checkposition):
    missing_key_msg = (
"""Cannot union {} and {}, headers do not match. {} contains column {}, while {} doesn't.""")
    key_position_msg = (
"""Cannot union {} and {}, headers do not match. In {}, {} is column {}, while in {} it's column {}.""")
    for index in range(len(sources)):
      for a, b in [(sources[0], sources[index]), (sources[index], sources[0])]:
        for key in tables[a][0]:
          if key not in tables[b][0]:
            self.Raise(missing_key_msg.format(a, b, a, key, b))
          if checkposition and tables[a][0][key] != tables[b][0][key]:
            self.Raise(key_position_msg.format(
                a, b, a, key, tables[a][0][key], b, tables[b][0][key]))

  def IntersectSchema(self, target, source):
    for key in list(target.keys()):
      if key not in source:
        del target[key]
    keypairs = [(target[key], key) for key in target]
    sort(keypairs)
    for i, (_, key) in enumerate(keypairs):
      target[key] = i

  def UnionSchema(self, target, source):
    keypairs = [(source[key], key) for key in source]
    keypairs.sort()
    for _, key in keypairs:
      if key not in target:
        target[key] = len(target)

  def TransformRow(self, row, sourceschema, targetschema):
    result = [''] * len(targetschema)
    for key in sourceschema:
      if key in targetschema:
        result[targetschema[key]] = row[sourceschema[key]]
    return result

  def Eval(self, tables, params):
    sources = [self.Source(x, tables, params) for x in self.sources]
    targetschema = tables[sources[0]][0].copy()
    if self.schema in ('EQUAL', 'REORDERED'):
      self.ValidateHeadersMatch(tables, sources, self.schema == 'EQUAL')
    for source in sources:
      if self.schema == 'INTERSECTION':
        self.IntersectSchema(targetschema, tables[source][0])
      elif self.schema == 'UNION':
        self.UnionSchema(targetschema, tables[source][0])
    target = self.target.Eval(ParamContext(params))
    if target in tables and target not in sources:
      self.Raise('Target table {} already present in tables!'.format(target))
    new_rows = []
    for source in sources:
      for row in tables[source][1]:
        new_rows.append(self.TransformRow(row, tables[source][0], targetschema))
    tables[target] = (targetschema, new_rows)
    return []

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
    name = self.Source(self.name, tables, params)
    path = self.path.Eval(ParamContext(params))
    header, rows = tables[name]
    if path == 'stdout':
      res = []
      res.append(self.options[SEPARATOR].join(header))
      for row in rows:
        res.append(self.options[SEPARATOR].join([str(x) for x in row]))
      return res
    else:
      with open(path, 'x') as outf:
        self.WriteLines(header, rows, outf)
      return []

class List(Command):
  def __init__(self, line):
    super().__init__(line, "LIST TABLES")
  
  def Eval(self, tables, params):
    return tables.keys()

class Describe(Command):
  def __init__(self, line, name):
    super().__init__(line, "DESCRIBE")
    self.name = name

  def Eval(self, tables, params):
    name = self.Source(self.name, tables, params)
    header, rows = tables[name]
    res = []
    if not rows:
      for column in header:
        res.append(column)
    else:
      for i, column in enumerate(header):
        res.append('{}: sample value {} of type {}'.format(
            column, str(rows[0][i]), str(type(rows[0][i]))[8:-2]))
    res.append('{} rows in total'.format(len(rows)))
    return res

# A sequence of commands to be executed one by one.
class Sequence:
  def __init__(self, seq):
    self.seq = seq

  def Eval(self, tables, params):
    res = []
    for comm in self.seq:
      res.extend(comm.Eval(tables, params))
    return res

class Run(Command):
  def __init__(self, line, runnables, random_names, parser):
    super().__init__(line, 'RUN')
    self.random_names = random_names
    self.runnables = []
    for r in runnables:
      source_options = {
         EXTRA_PARAMS: [],
         SOURCES: [],
         PARAM_PREFIX: None,
         TARGET_TABLE: None,
      }
      sources = []
      for source in r['FROM']:
        sources.append(RunInput(source[2], source, source_options, parser))
      options = {EXTRA_PARAMS: r['PARAMS'],
                 SOURCES: sources,
                 PARAM_PREFIX: r['PARAM_PREFIX'],
                 TARGET_TABLE: r['INTO']}
      self.runnables.append(RunInput(r['LINE'], r['INPUT'], options, parser))

  def Eval(self, tables, params):
    res = []
    for runnable in self.runnables:
      res.extend(runnable.Eval(tables, params))
    for random_name in self.random_names:
      del tables[random_name]
    return res

class RunInput(Command):
  def __init__(self, line, inputdata, options, parser):
    super().__init__(line, 'RUN input')
    self.inputtype = inputdata[0]
    assert self.inputtype in ['FILE', 'COMMAND', 'TABLE']
    self.input = inputdata[1]
    self.parser = parser
    self.prefix = options[PREFIX] if PREFIX in options else None
    self.extra_params = options[EXTRA_PARAMS]
    self.sources = options[SOURCES]
    self.param_prefix = options[PARAM_PREFIX]
    self.target_table = options[TARGET_TABLE]

  def Eval(self, tables, params):
    res = []
    inputdata = self.input.Eval(ParamContext(params))
    prefix = self.prefix.Eval(ParamContext(params)) if self.prefix else ''
    param_prefix = self.param_prefix.Eval(ParamContext(params)) if self.param_prefix else ''
    # Step one: Parse the relevant file.
    if self.inputtype == 'FILE':
      try:
        with open(inputdata, 'r') as config_file:
          try:
            child_command = self.parser(config_file.readlines())
          except Exception as e:
            self.RaiseFrom('Failure parsing imported file {}'.format(
                inputdata), e)
      except OSError as e:
        self.RaiseFrom('Failed to open file {}'.format(inputdata), e)
    elif self.inputtype == 'COMMAND':
      child_command = self.parser([inputdata])
    elif self.inputtype == 'TABLE':
      source_table = self.Source(self.input, tables, params)
    # Step two: prepare the new parameters for the execution.
    child_params = {}
    # TODO: consider an option where we're explicitly not passing params in
    for param in params:
      # We don't copy input table parameters to the child (we take the ones
      # explicitly specified in params; we don't want to inherit the ones
      # that the parent file used).
      if param.startswith(param_prefix) and param != INPUT_TABLES:
        child_params[param[len(param_prefix):]] = params[param]
    for param in self.extra_params:
      child_params[param] = self.extra_params[param].Eval(
          ParamContext(params))
    # Step three: prepare to shift directory
    if self.inputtype == 'FILE': 
      rootpath = os.path.dirname(os.path.abspath(inputdata))
      oldpath = os.getcwd()
      os.chdir(rootpath)
    # Step four: prepare child tables.
    child_tables = {}
    child_params[INPUT_TABLES] = []
    for source in self.sources:
      grandchild_tables = {}
      if source.inputtype == 'TABLE':
        for tablename in tables:
          grandchild_tables[tablename] = tables[tablename]
      source.Eval(grandchild_tables, params)
      if len(grandchild_tables) != 1:
        self.Raise('Source produced {} tables: {}, expected 1'.format(
            len(grandchild_tables), list(grandchild_tables.keys())))
      table_name = list(grandchild_tables.keys())[0]
      if table_name in child_tables:
        self.Raise('Two FROM sources produced table with the same name' +
                     table_name)
      child_tables[table_name] = grandchild_tables[table_name]
      # We pass the input table names in order under a "magic" param.
      # We pass the evaluated table names, instead of expressions, because
      # the set of parameters might be different in the child, and we want
      # to keep the evaluation from the parent.
      child_params[INPUT_TABLES].append(table_name)
    # Step five: actually execute child
    if self.inputtype in ['FILE', 'COMMAND']:
      try:
        res = child_command.Eval(child_tables, child_params)
      except ValueError as e:
        if self.inputtype == 'FILE':
          self.RaiseFrom('Failure in imported file ' + inputdata, e)
        else:
          self.RaiseFrom('Failure in running command', e)
      finally:
        if self.inputtype == 'FILE':
          # Step six: roll back the directory shift
          os.chdir(oldpath)
    elif self.inputtype == 'TABLE':
      child_tables = {source_table: tables[source_table]}
    # Step seven: copy results of child execution into parent tables
    if self.target_table:
      target_name = self.target_table.Eval(ParamContext(params))
      if len(child_tables) != 1:
        self.Raise('Running with an INTO clause has to produce exactly 1 table, got {}: {}'.format(len(child_tables), list(child_tables.keys())))
      tables[target_name] = child_tables[list(child_tables.keys())[0]]
    elif self.inputtype != 'TABLE':
      for table in child_tables:
        new_table_name = prefix + table
        if new_table_name in tables:
          self.Raise('Cannot import table {}, it already exists'.format(
              new_table_name))
        tables[new_table_name] = child_tables[table]
    else:
      keys = list(tables.keys())
      for key in keys:
        if key != source_table:
          del tables[key]
    return res




# A request to execute another file. The parser is passed in, because
# there's a circular dependency here I need to resolve somehow.
class Import(Command):
  def __init__(self, line, path, options, parser):
    super().__init__(line, 'IMPORT')
    self.path = path
    self.parser = parser
    self.prefix = options[PREFIX] if PREFIX in options else None
    self.extra_params = options[EXTRA_PARAMS]
    self.extra_tables = options[EXTRA_TABLES]
    self.param_prefix = options[PARAM_PREFIX]
    self.target_table = options[TARGET_TABLE]

  def Eval(self, tables, params):
    res = []
    path = self.path.Eval(ParamContext(params))
    prefix = self.prefix.Eval(ParamContext(params)) if self.prefix else ''
    param_prefix = self.param_prefix.Eval(ParamContext(params))
    # Step one: Parse the relevant file.
    try:
      with open(path, 'r') as config_file:
        try:
          child_command = self.parser(config_file.readlines())
        except Exception as e:
          self.RaiseFrom('Failure parsing imported file {}'.format(path), e)
    except OSError as e:
      self.RaiseFrom('Failed to open file {}'.format(path), e)
    # Step two: prepare the new parameters for the execution.
    child_params = {}
    # TODO: consider an option where we're explicitly not passing params in
    for param in params:
      # We don't copy input table parameters to the child (we take the ones
      # explicitly specified in params; we don't want to inherit the ones
      # that the parent file used).
      if param.startswith(param_prefix) and param != INPUT_TABLES:
        child_params[param[len(param_prefix):]] = params[param]
    for param in self.extra_params:
      child_params[param] = self.extra_params[param].Eval(
          ParamContext(params))
    # Step three: prepare to shift directory
    rootpath = os.path.dirname(os.path.abspath(path))
    oldpath = os.getcwd()
    os.chdir(rootpath)
    # Step four: prepare child tables.
    child_tables = {}
    child_params[INPUT_TABLES] = []
    for table in self.extra_tables:
      table_name = self.Source(table, tables, params)
      child_tables[table_name] = tables[table_name]
      # We pass the input table names in order under a "magic" param.
      # We pass the evaluated table names, instead of expressions, because
      # the set of parameters might be different in the child, and we want
      # to keep the evaluation from the parent.
      child_params[INPUT_TABLES].append(table_name)
    # Step five: actually execute child
    try:
      res = child_command.Eval(child_tables, child_params)
    except ValueError as e:
      self.RaiseFrom('Failure in imported file ' + path, e)
    finally:
      # Step six: roll back the directory shift
      os.chdir(oldpath)
    # Step seven: copy results of child execution into parent tables
    if self.target_table:
      target_name = self.target_table.Eval(ParamContext(params))
      if len(child_tables) != 1:
        self.Raise('Running with an INTO clause has to produce exactly 1 table, got {}: {}'.format(len(child_tables), list(child_tables.keys())))
      tables[target_name] = child_tables[list(child_tables.keys())[0]]
    else:
      for table in child_tables:
        new_table_name = prefix + table
        if new_table_name in tables:
          self.Raise('Cannot import table {}, it already exists'.format(
              new_table_name))
        tables[new_table_name] = child_tables[table]
    return res

class SingleExpression:
  def __init__(self, expr, columnname):
    self.expr = expr
    self.columnname = columnname

  def AppendHeader(self, new_header, old_header, params):
    context = RowContext(None, old_header, params)
    columnname = self.columnname.Eval(context)
    if columnname in new_header:
      raise ValueError('Column {} defined twice'.format(columnname))
    new_header[columnname] = len(new_header)

  def AppendValues(self, context, row, header, input_row):
    try:
      row.append(self.expr.Eval(context))
    except Exception as e:
      msg = 'Failure evaluating {} (column {}) for row {}: {}'
      raise ValueError(msg.format(
          self.columnname.Eval(context), len(row) + 1, input_row, str(e))) from e

class RangeExpression:
  def __init__(self, expr, range_beg, range_end, header_expr):
    self.expr = expr
    self.range_beg = range_beg
    self.range_end = range_end
    self.header_expr = header_expr

  def AppendHeader(self, new_header, old_header, params):
    context = RowContext(None, old_header, params)
    self.beg = self.range_beg.Eval(context)
    self.end = self.range_end.Eval(context)
    old_header_rev = {}
    for x in old_header:
      old_header_rev[old_header[x]] = x
    for col in range(self.beg - 1, self.end - 1):
      context['?'] = old_header_rev[col]
      col_header = self.header_expr.Eval(context)
      new_header[col_header] = len(new_header)

  def AppendValues(self, context, row, header, input_row):
    header_rev = {}
    for name in header:
      header_rev[header[name]] = name
    for x in range(self.beg - 1, self.end - 1):
      context['?'] = header_rev[x]
      try:
        row.append(self.expr.Eval(context))
      except Exception as e:
        msg = 'Failure evaluating {} (column {} in range {}-{}) for row {}'
        raise ValueError(msg.format(header_rev[x], x+1, self.beg+1,
                                    self.end+1, input_row) + str(e)) from e
      del context['?']

class Filter(Command):
  def __init__(self, line, source_table, target_table, expr):
    super().__init__(line, "FILTER")
    self.source_table = source_table
    self.target_table = target_table
    self.expr = expr

  def Eval(self, tables, params):
    source_table, target_table = self.SourceAndTarget(
        self.source_table, self.target_table, tables, params)
    header, rows = tables[source_table]
    new_rows = []
    for row in rows:
      if len(row) != len(header):
        self.Raise('Row {} has length {}, expected {}'.format(row, len(row),
            len(header)))
      try:
        val = self.expr.Eval(RowContext(row, header, params))
        if val:
          new_rows.append(row)
      except Exception as e:
        self.RaiseFrom('Failed to evaluate filter for row '.format(row), e)
    tables[target_table] = (header, new_rows)
    return []

class Transform(Command):
  def __init__(self, line, source_table, target_table, expr_list):
    super().__init__(line, 'TRANSFORM')
    self.source_table = source_table
    self.target_table = target_table
    self.expr_list = expr_list

  def Eval(self, tables, params):
    source_table, target_table = self.SourceAndTarget(
        self.source_table, self.target_table, tables, params)
    header, rows = tables[source_table]
    new_header = {}
    for expr in self.expr_list:
      expr.AppendHeader(new_header, header, params)
    new_rows = []
    for row in rows:
      new_row = []
      if len(row) != len(header):
        self.Raise('Row {} has length {}, expected {}'.format(
            row, len(row), len(header)))
      # Construct the expression evaluation context
      for expr in self.expr_list:
        expr.AppendValues(RowContext(row, header, params), new_row, header, row)
      if len(new_row) != len(new_header):
        self.Raise('Calculated row {} has length {}, expected {}'.format(
            new_row, len(new_row), len(new_header)))
      new_rows.append(new_row)
    tables[target_table] = (new_header, new_rows)
    return []

class Aggregate(Command):
  def __init__(self, line, source_table, target_table, group_list, expr_list):
    super().__init__(line, 'AGGREGATE')
    self.source_table = source_table
    self.target_table = target_table
    self.group_list = group_list
    self.expr_list = expr_list

  def Eval(self, tables, params):
    source_table, target_table = self.SourceAndTarget(
        self.source_table, self.target_table, tables, params)
    header, rows = tables[source_table]

    # Define the new header.
    new_header = {}
    for expr in self.expr_list:
      expr.AppendHeader(new_header, header, params)

    # Accumulate the set of group keys.
    group_keys = set()
    for group_key in self.group_list:
      if isinstance(group_key, int):
        group_keys.add(group_key - 1)
      else:
        if group_key not in header:
          self.Raise('Unknown group key {}'.format(group_key))
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
      context = RowContext(None, header, params)
      context['__group_data'] = [{} for _ in groups[agg_key]]
      context['__data'] = {}
      for column in header:
        col_num = header[column]
        if col_num in group_keys:
          context['__data'][col_num] = groups[agg_key][0][col_num]
        else:
          for i, row in enumerate(groups[agg_key]):
            context['__group_data'][i][col_num] = row[col_num]
      # The 'debug' row value
      debug_row = [context['__data'][x] for x in context['__data']]
      # Calculate the expressions.
      new_row = []
      for expr in self.expr_list:
        expr.AppendValues(context, new_row, header, debug_row)
      if len(new_row) != len(new_header):
        self.Raise('Calculated row {} has length {}, expected {}'.format(
            new_row, len(new_row), len(new_header)))
      new_rows.append(new_row)

    tables[target_table] = (new_header, new_rows)
    return []

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
        self.Raise('Failed to find key {} in table {}'.format(key, left_table))
      keys[key][1] = True
      return keys[key][0]
    elif self.comparator == 'PREFIX':
      found_prefix = None
      for preflen in range(len(key)+1):
        if key[:preflen] in keys:
          if found_prefix is not None:
            self.Raise('Found two prefixes matching {}: {} and {}'.format(
                key, found_prefix, key[:preflen]))
          found_prefix = key[:preflen]
      if found_prefix is None:
        if self.unmatched_values:
          return empty_row
        self.Raise('Failed to find prefix for key {}'.format(key))
      keys[found_prefix][1] = True
      return keys[found_prefix][0]

  def Eval(self, tables, params):
    left_table = self.Source(self.left_table, tables, params)
    left_header, left_rows = tables[left_table]
    right_table = self.Source(self.right_table, tables, params)
    right_header, right_rows = tables[right_table]
    target_table = self.target_table.Eval(ParamContext(params))
    if target_table in tables:
      self.Raise('Cannot create table {}, it already exists'.format(
          target_table))
    header = {}
    for column in left_header:
      header[column] = left_header[column]
    for column in right_header:
      header[column] = right_header[column] + len(left_header)
    keys = {}
    rows = []
    for row in left_rows:
      context = RowContext(row, left_header, params)
      keys[self.left_expr.Eval(context)] = [row, False]
    for row in right_rows:
      context = RowContext(row, right_header, params)
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
            self.Raise('Key {} from {} not matched by any value'.format(
                key, left_table))
    tables[target_table] = (header, rows)
    return []

class Append(Command):
  def __init__(self, line, expr_list, table):
    super().__init__(line, 'APPEND')
    self.expr_list = expr_list
    self.table = table

  def Eval(self, tables, params):
    table = self.Source(self.table, tables, params)
    row = []
    for expr in self.expr_list:
      row.append(expr.Eval({}))
    if len(row) != len(tables[table][0]):
      self.Raise('Provided {} values, while table {} has {} columns'.format(
          len(row), table, len(tables[table][0])))
    tables[table][1].append(row)
    return []

class Drop(Command):
  def __init__(self, line, table):
    super().__init__(line, 'DROP')
    self.table = table

  def Eval(self, tables, params):
    target = self.Source(self.table, tables, params)
    del tables[target]
    return []

class Output(Command):
  def __init__(self, line, tables):
    super().__init__(line, 'OUTPUT TABLES')
    self.tables = tables

  def Eval(self, tables, params):
    output_tables = []
    for table in self.tables:
      output_tables.append(self.Source(table, tables, params))
    to_remove = []
    for table in tables:
      if table not in output_tables:
        to_remove.append(table)
    for table in to_remove:
      del tables[table]
    return []

class Input(Command):
  def __init__(self, line, tables):
    super().__init__(line, 'INPUT TABLES')
    self.tables = tables

  def Eval(self, tables, params):
    if params[INPUT_TABLES]:
      if len(self.tables) != len(params[INPUT_TABLES]):
        self.Raise(
          'INPUT TABLES specifies {} tables, but caller provided {}'.format(
            len(self.tables), num_param_tables))
      temp_tables = {}
      for old_name, new_name_expr in zip(params[INPUT_TABLES], self.tables):
        new_name = new_name_expr.Eval(ParamContext(params))
        temp_tables[new_name] = tables[old_name]
        del tables[old_name]
      for table_name in temp_tables:
        tables[table_name] = temp_tables[table_name]
    for t in self.tables:
      self.Source(t, tables, params)
    return []

class Pivot(Command):
  def __init__(self, line, source, target, headers_from, headers_to):
    super().__init__(line, 'PIVOT')
    self.source = source
    self.target = target
    self.headers_from = headers_from
    self.headers_to = headers_to

  def Eval(self, tables, params):
    source, target = self.SourceAndTarget(
        self.source, self.target, tables, params)
    old_header, old_rows = tables[source]
    skipped_source_col = None
    header = {}
    rows = []
    # Prepare the new header lambda, and the skipped row.
    if self.headers_from:
      headers_from = self.headers_from.Eval(
          RowContext(None, old_header, params))
      if headers_from not in old_header:
        self.Raise(
          ('Source table {} does not have requested header column {}, ' +
          'present columns are {}').format(
              source, headers_from, old_header.keys()))
      header_column_index = old_header[headers_from]
      skipped_source_col = header_column_index
      header_for_row = lambda i, row: row[header_column_index]
    else:
      header_for_row = lambda i, row: 'col_' + str(i+1)
    # Prepare empty new rows (one per old column, potentially minus headers)
    for _ in old_header:
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
      headers_to = self.headers_to.Eval(RowContext(None, old_header, params))
      header[headers_to] = 0
      for h in old_header:
        if target_row(old_header[h]) is not None:
          rows[target_row(old_header[h])].append(h)
    # Construct the headers and the rest of the rows.
    for i, row in enumerate(old_rows):
      h = header_for_row(i, row)
      if h in header.keys():
        self.Raise(
            'Header column {} contains duplicate key {} in row {}'.format(
                headers_from, h, i))
      header[h] = i if self.headers_to is None else i + 1
      for j, val in enumerate(row):
        if target_row(j) is not None:
          rows[target_row(j)].append(val)
    tables[target] = (header, rows)
    return []

class Visualize(Command):
  def __init__(self, line, table, outfile, base, colours, idname, dataname,
               lowb, highb, legend, header, title):
    super().__init__(line, 'VISUALIZE')
    self.table = table
    self.outfile = outfile
    self.base = base
    self.colours = colours if colours is not None else 'greyscale5'
    self.idname = idname
    self.dataname = dataname
    self.legend = legend if legend is not None else True
    self.header = header
    self.title = title
    self.lowbound = lowb
    self.highbound = highb

  def GetColumnIndex(self, var, params, header):
    name = var.Eval(ParamContext(params))
    if name not in header:
      self.Raise('Unknown column name {}, column names are {}'.format(
          name, header.keys()))
    return header[name]

  def Eval(self, tables, params):
    header, rows = tables[self.Source(self.table, tables, params)]
    idcol = self.GetColumnIndex(self.idname, params, header)
    datacol = self.GetColumnIndex(self.dataname, params, header)
    base = self.base.Eval(ParamContext(params))
    outfile = self.outfile.Eval(ParamContext(params))
    map_header = self.header.Eval(ParamContext(params))
    map_title = self.title.Eval(ParamContext(params))
    data = {}
    if self.lowbound is None and self.highbound is not None:
      self.Raise('High bound specified, but low bound is not')
    if self.highbound is None and self.lowbound is not None:
      self.Raise('Low bound specified, but high bound is not')
    high = float(self.highbound) if self.highbound is not None else None
    low = float(self.lowbound) if self.lowbound is not None else None
    for row in rows:
      data[row[idcol]] = row[datacol]
    try:
      visualize.Visualize(data, outfile, base, self.colours, low, high,
                          self.legend, map_header, map_title)
    except Exception as e:
      self.RaiseFrom('Failed to visualize', e)
    return []

