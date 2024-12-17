# Usage: python3 cadmium.py

import command
import os
import sys
import sql
import terminal
import tokenizer
import traceback

def usage():
  print('Usage:')
  print('"python3 cadmium.py" runs the interactive interpreter')
  print('"python3 cadmium.py CONFIGFILE_PATH [PARAM_NAME PARAM_VALUE]" executes a config filie')
  sys.exit(1)

if len(sys.argv) > 1 and len(sys.argv) % 2:
  usage()

if len(sys.argv) > 1:
  try:
    with open(sys.argv[1], 'r') as configfile:
      print('Parsing command file: ', sys.argv[1])
      comm = sql.GetCommandList(configfile.readlines())
  except Exception as e:
    print(str(e))
    sys.exit(1)
  print('Parsed successfully, running')
  print()
  params = {}
  for i in range(2, len(sys.argv), 2):
    params[sys.argv[i]] = sys.argv[i+1]
  rootpath = os.path.dirname(os.path.abspath(sys.argv[1]))
  oldpath = os.path.abspath(os.getcwd())
  os.chdir(rootpath)
  try:
    for l in comm.Eval({}, params):
      print(l)
  except Exception as e:
    print(str(e))
    if True:
      # TODO: Disable this.
      for l in traceback.format_list(traceback.extract_tb(e.__traceback__)):
        print(l)
    sys.exit(1)
  finally:
    os.chdir(oldpath)
  print()
  print('Run ended with success')
else:
  welcome = [
    'Welcome to the interactive Cadmium interpreter!',
    '',
    'Aside from the standard Cadmium commands, you can use HISTORY PRINT to output to stdout all the commands issued thus far (except "PRINT" commands) so you can copy them to a file.',
    '']
  tables = {}
  def execute(cmd):
    # TODO: consider the option of setting persistent params.
    words = cmd.strip().strip(';').lower().split()
    if not words:
      return []
    if words[0] == 'history':
      if len(words) != 2:
        raise ValueError(
            'History only takes one argument (print, store or load)')
      if words[1] == 'print':
        return terminal.history
      elif words[1] == 'store':
        with open('history', 'w') as hfile:
          for cmd in terminal.history:
            hfile.write(cmd + '\n')
        return []
      elif words[1] == 'load':
        with open('history', 'r') as hfile:
          for cmd in hfile.readlines():
            terminal.history.append(cmd)
        return []
      else:
        raise ValueError(
            'History argument needs to be print, store or load')
    else:
      cmds = []
      tokens = tokenizer.tokenize([cmd])
      while tokens:
        cmds.append(sql.GetCommand(tokens))
      comm = command.Sequence(cmds)
      return comm.Eval(tables, {})
  terminal.run(execute, welcome)
