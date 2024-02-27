# Used to validate the schema of a CSV file.

# Takes a config file that contains validation definitions, one per line.
# Each validation definition is a binary or a unary relation.

# Unary relations are of the format RELATION_NAME EXPRESSION
# Binary relations are EXPRESSION RELATION_NAME EXPRESSION
# Expression is either a constant, a column reference ($COLUMN_NUMBER),
# or expression + expression (interpreted as integer addition)
# or Sum(COLUMN_NUMBER), which means the sum of the values in all the columns
# starting from that one.

# Allowed unary relations:
# IsInteger (is an integer)

# Allowed binary relations:
# = (LHS and RHS are equal)

# All checks are applied to the value lines, not to the header line.
# All columns are one-indexed
# Usage of '?' means that a check should apply to all columns.

# Usage: python3 validate_csv_file.py INFILE CONFIGFILE
# Will toss an exception is something's wrong.

import sys
import expressions

failed_validations = {}

def Validate(val, desc, row):
  if val.Get(row) != True:
    if desc not in failed_validations:
      failed_validations[desc] = []
    failed_validations[desc].append(row)


assert len(sys.argv) == 3
infile = sys.argv[1]
configfile = sys.argv[2]

# OK, this is gonna be hacky.
validations = []
universals = []
with open(configfile, 'r') as cf:
  for line in cf.readlines():
    line = line.strip()
    if not line or line[0] == '#':
      continue
    if line.find('?') != -1:
      universals.append((lambda i, l=line: expressions.Parse(l, i), line))
    else:
      validations.append((expressions.Parse(line, -1), line))

header = None

with open(infile, 'r') as cf:
  passed_header_line = False
  for line in cf.readlines():
    line = line.strip()
    if not line or line[0] == '#':
      continue
    row = line.split(';')
    if not passed_header_line:
      passed_header_line = True
      header = row
      continue
    for c in range(len(row)):
      for u in universals:
        Validate(u[0](c+1), u[1] + ' for ' + str(c+1), row)
    for v in validations:
      Validate(v[0], v[1], row)

if failed_validations:
  for validation in failed_validations:
    failures = failed_validations[validation]
    print('Validation', validation, 'failed for', len(failures), 'rows')
    print('Sample row:')
    print('\n'.join(
        [str(i+1) + ' [' + header[i] + ']: ' + v for i, v in enumerate(failures[0])]))
    print()
else:
  print("Validation successful!")
