# Used to transform a CSV file into another schema.
# Takes a "config" file that contains column definitions, one per line, and
# the last line can be special.
# Empty lines, and lines beginning with a hash, are ignored.

# The column definition consists of two parts, which are semicolon-separated.
# The first part is the column name, the second is the column value.
# The column name should be a string. It's either a string constant
# in double-quotes, or a variable (with possible modifiers)

# The column value is a string or an integer. It can be either a constant
# (numeric or string in double quotes), or an expression. Expressions, right
# now, only support number addition, constant numbers and variables.

# A variable (string or numeric) begins with a dollar sign (like PHP).
# Then we can have a number of capital english letters (with semantics below)
# And then we have an integer, which is a reference to a column in the source.
# The semantics are, of course, take the value of whatever's in the source.

# The letter modifiers supported:
# Q: strip quotes, if any, from around the value
# C: remove internal commas
# D: replace a dash, if it's the whole value, with a zero
# E: replace an empty string with a zero
# I: interpret as an integer
# S: interpret as a string (default)

# The last line can (does not have to) be a ..., followed by a column reference
# (that is, an integer), followed by the two parts, where expressions might
# contain a question mark instead of a standard column reference.
# This means we take all columns from the indicated one onward, and we transform
# them as specified, where the question mark refers to the transformed column.

# Column references are 1-indexed.
# Example: $12;$12 + $DCI8
# Example: ...14; $QS?; $I? + 5

# Usage: python3 transform_csv_file.py INFILE CONFIGFILE OUTFILE

import sys
import expressions

def ParseConfigLines(lines):
  last_line = None
  columns = []
  for line in lines:
    line = line.strip()
    if not line or line[0] == '#':
      continue
    assert last_line is None
    s = line.split(';')
    assert len(s) in (2, 3)
    if len(s) == 2:
      columns.append((expressions.Parse(s[0], -1), expressions.Parse(s[1], -1)))
    else:
      assert s[0][:3] == '...'
      start = int(s[0][3:].strip())
      header = lambda index, s=s: expressions.Parse(s[1], index)
      value = lambda index, s=s: expressions.Parse(s[2], index)
      last_line = (start, header, value)
  return (columns, last_line)


assert len(sys.argv) == 4
infile = sys.argv[1]
conffile = sys.argv[2]
outfile = sys.argv[3]

with open(conffile, 'r') as conf:
  config = ParseConfigLines(conf.readlines())
with open(infile, 'r') as inf:
  with open(outfile, 'w') as outf:
    header_row_parsed = False
    for row in inf.readlines():
      if not row or row[0] == '#':
        outf.write(row)
        continue
      r = [v.strip() for v in row.split(';')]
      if not header_row_parsed:
        header_row_parsed = True
        numcols = len(r)
        columns = config[0]
        if config[1]:
          for col in range(config[1][0], numcols+1):
            columns.append((config[1][1](col), config[1][2](col)))
        for i, c in enumerate(columns):
          if i:
            outf.write(';')
          outf.write(str(c[0].Get(r)))
      else:
        for i, c in enumerate(columns):
          if i:
            outf.write(';')
          outf.write(str(c[1].Get(r)))
      outf.write('\n')


