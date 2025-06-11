# Join all the by-district files into one file, with an extra column with
# the district number.

import sys
sys.path.append('../../../python_lib')
import command
import sql
import tokenizer

# Unfortunately, I don't have a programmatic API for Cadmium that's easy to
# use and that I'd want to commit to maintaining. So, instead, I'm gonna
# parse strings. Sad, I know.

# This is basically copied over from cadmium.py. Consider extracting at least
# this into an interface?
# cmds is a list of strings, each string a semicolon-ending command.
def execute(cmds, tables):
  c = []
  tokens = tokenizer.tokenize(cmds)
  while tokens:
    c.append(sql.GetCommand(tokens))
  comm = command.Sequence(c)
  return comm.Eval(tables, {})

# Takes a single table, and unions the contents into "table".
def transform_single_table(index, tables):
  c = [
    'LOAD raw FROM "2023/okreg_{}_utf8.csv";'.format(index),
    """TRANSFORM raw WITH if(at(1) = '', -1, int(at(1))) AS teryt, at(2) AS community, at(3) AS county, 
          at(4) AS voivodship, int(at(5)) AS number_of_commissions, 
          int(at(6)) AS number_of_considered_commissions,
          if(curr() = '', 0, int(curr())) FOR 7:;""",
    """FILTER raw BY not(startswith(community, '"Dzielnice'));""",
    'EMPTY AS okr;',
    'TRANSFORM okr WITH 1 AS okręg;',
    'APPEND {} TO okr;'.format(index),
    'JOIN okr INTO raw ON 1 EQ 1 AS result{};'.format(index),
    'DROP okr;',
    'DROP raw;',
  ]
  execute(c, tables)

tables = {}
unioncmd = 'UNION'
for index in range(1, 101):
  transform_single_table(index, tables)
  unioncmd += ' result{}'.format(index)
  if index < 100:
    unioncmd += ','
unioncmd += ' TO table WITH ALL COLUMNS;'
transformcmd = 'TRANSFORM table WITH curr() FOR 1:7, if(curr() = "", 0, int(curr())) FOR 8:;'
execute([unioncmd, transformcmd], tables)

print(execute(['DUMP table TO "2023.csv";'], tables))
