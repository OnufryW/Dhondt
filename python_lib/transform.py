# Usage: python3 transform.py PATH_TO_CONFIG_FILE [PARAM_NAME PARAM_VAL]*

import sys

import sql

assert len(sys.argv) % 2 == 0
with open(sys.argv[1], 'r') as configfile:
  print('Parsing command file: ', sys.argv[1])
  comm = sql.GetCommandList(configfile.readlines())
print('Parsed successfully, running')
print()
params = {}
for i in range(2, len(sys.argv), 2):
  params[sys.argv[i]] = sys.argv[i+1]
comm.Eval({}, params)
print()
print('Run ended with success')

