# Usage python3 validate.py PATH_TO_CONFIG_FILE PATH_TO_VALIDATION_FILE

import random
import sys

import sql

assert len(sys.argv) == 3
# Note: A part of the logic could be in a config file. The reason I'm not
# doing this is because I don't want to hardcode the absolute path to the
# config file; and at the same time I don't want to force cwd to be in
# some fixed relation to the location of the config file. So, here goes.

validator_commands = [
  'IMPORT "{}";'.format(sys.argv[1]),
  'IMPORT "{}" WITH TABLE table WITH PREFIX v_;'.format(sys.argv[2]),
  'TRANSFORM v_table WITH and_range(1:) AS all_correct, $? FOR 1:;'
]

validator = sql.GetCommandList(validator_commands)
context = {}
validator.Eval(context, {})
assert 'v_table' in context

header, rows = context['v_table']
reverse_header = {}
for title in header:
  reverse_header[header[title]] = title

# Check the validity of the result.
incorrect_rows = []
for i, row in enumerate(rows):
  if not row[0]:
    incorrect_rows.append((i, row))

if not incorrect_rows:
  print('Validation fully successful')
  sys.exit(0)
else:
  print('Validation failed, {} / {} rows incorrect'.format(
      len(incorrect_rows), len(rows)))

failures = []

for column in range(1, len(rows[0])):
  failure_count = 0
  failure_sample = None
  for i, row in incorrect_rows:
    if not row[column]:
      if random.randint(0, failure_count) == 0:
        failure_sample = (i, row)
      failure_count += 1
  if failure_count:
    failures.append(
        (failure_count, column, failure_sample[0]))

def PrintFailure(failure):
  print('Failure {}, with {} / {} rows failing, sample row {}'.format(
      reverse_header[failure[1]], failure[0], len(rows), failure[2]))

def PrintRow(index):
  header, rows = context['table']
  reverse_header = {}
  for title in header:
    reverse_header[header[title]] = title
  for column in range(len(rows[index])):
    print('[{}] {}: {}'.format(
        column + 1, reverse_header[column], rows[index][column]))

failures.sort()
failures.reverse()
for i, failure in enumerate(failures):
  PrintFailure(failure)
  if i < 1:
    PrintRow(failure[2])

sys.exit(1)
