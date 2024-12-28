# Usage python3 validate.py PATH_TO_CONFIG_FILE PATH_TO_VALIDATION_FILE

import random
import sys

import sql

def printhelp(exitcode):
  print('Usage:')
  print('python3 validate.py PATH_TO_CONFIG_FILE PATH_TO_VALIDATION_FILE [OPTIONS] [PARAMS]')
  print()
  print('Valid options:')
  print('--samples_printed X')
  print('--allow_partial_success')
  print()
  print('Params are 2 strings - the key and the value for the tested table')
  sys.exit(exitcode)

if len(sys.argv) < 3:
  printhelp(1)

print('Validating {}'.format(sys.argv[1]))

samples_printed = 1
full_success_required = True
params = {}
pos = 3
while pos < len(sys.argv):
  if sys.argv[pos] == '--samples_printed':
    samples_printed = int(sys.argv[pos+1])
    pos += 2
  elif sys.argv[pos] == '--allow_partial_success':
    full_success_required = False
    pos += 1
  else:
    params[sys.argv[pos]] = sys.argv[pos+1]
    pos += 2

# Note: A part of the logic could be in a config file. The reason I'm not
# doing this is because I don't want to hardcode the absolute path to the
# config file; and at the same time I don't want to force cwd to be in
# some fixed relation to the location of the config file. So, here goes.

validator_commands = [
  'IMPORT "{}";'.format(sys.argv[1]),
  'IMPORT "{}" WITH TABLE table WITH PREFIX v_;'.format(sys.argv[2]),
  'TRANSFORM v_table WITH and_range(1:) AS all_correct, curr() FOR 1:;'
]

validator = sql.GetCommandList(validator_commands)
context = {}
validator.Eval(context, params)
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
  print('Validation of {} fully successful'.format(sys.argv[1]))
  sys.exit(0)

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
        (not reverse_header[column].startswith('optional_'),
         failure_count, column, failure_sample[0]))

if not full_success_required:
  partial_success = True
  for failure in failures:
    if failure[0]:
      partial_success = False
  if partial_success:
    print(
        'Validation of {} successful, {}/{} rows with soft failures'.format(
            sys.argv[1], len(incorrect_rows), len(rows)))
    sys.exit(0)

print('Validation of {} failed, {} / {} rows incorrect'.format(
    sys.argv[1], len(incorrect_rows), len(rows)))

def PrintFailure(failure):
  print('{}ailure {}, with {} / {} rows failing, sample row {}'.format(
      'F' if failure[0] else 'Soft f',
      reverse_header[failure[2]], failure[1], len(rows), failure[3]))

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
  if i < samples_printed:
    PrintRow(failure[3])

sys.exit(1)
