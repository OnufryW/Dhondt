import unittest
import os

import sql
import tokenizer

def tokenValues(s):
  return [t.value for t in tokenizer.tokenize(s)]

def fullTokens(s):
  return [t.value + '$' + t.typ for t in tokenizer.tokenize(s)]

class TestTokenize(unittest.TestCase):
  def test_empty(self):
    self.assertEqual([], tokenValues(''))

  def test_expression(self):
    self.assertEqual(['2', '+', '2', '=', '4'],
                     tokenValues('2+2 = 4'))

  def test_longer_string(self):
    self.assertEqual(['my', 'cow', 'is', 'red'],
                     tokenValues('my cow is red'))

  def test_longer_numbers(self):
    self.assertEqual(['11', '*', '1.1', '=', '12.1'],
                     tokenValues('11*1.1 = 12.1'))

  def test_all_symbols(self):
    self.assertEqual(['+', '-', '*', '=', '/', ',', '(', ')', ';'],
                     tokenValues('+-*=/,();'))

  def test_quote_simple(self):
    self.assertEqual(['test$quoted'], fullTokens('"test"'))

  def test_quote_in_quote(self):
    self.assertEqual(['""'], tokenValues('\'""\''))

  def test_series_of_quotes(self):
    self.assertEqual(['', '', ''], tokenValues('""""\'\''))

  def test_token_types(self):
    self.assertEqual(['A$word', '=$symbol', '4$number'],
                     fullTokens('A = 4'))

def evaluate(s, c={}):
  return sql.GetExpression(tokenizer.tokenize(s)).Eval(c)

class TestExpression(unittest.TestCase):
  def test_integer(self):
    self.assertEqual(4, evaluate('4'))

  def test_float(self):
    self.assertEqual(0.5, evaluate('0.5'))

  def test_variable(self):
    self.assertEqual(4, evaluate('four', {'four': 4}))

  def test_basic_arithmetic(self):
    self.assertEqual(4, evaluate('2 + 2'))

  def test_arithmetic(self):
    self.assertEqual(3, evaluate('2 * 2 + 2 / 2 - 2'))

  def test_arithmetic_with_variables(self):
    self.assertEqual(0, evaluate('a - b', {'a': 2, 'b': 2}))

  def test_min(self):
    self.assertEqual(2, evaluate('min(2, 2+2)'))

  def test_sqrt(self):
    self.assertEqual(2.0, evaluate('sqrt(4)'))

  def test_binding_order(self):
    self.assertEqual(2, evaluate('2 - 1 + 1'))
    self.assertEqual(0, evaluate('4 - 1 - 1 - 1 - 1'))

  def test_comparison(self):
    self.assertTrue(evaluate('2 = 1 + 1'))
    self.assertFalse(evaluate('2 * 2 = 5'))
    self.assertTrue(evaluate('2 < 3', {}))
    self.assertFalse(evaluate('1 + 1 + 1 < 3 * 1'))
    self.assertFalse(evaluate('3 < 2'))
    self.assertTrue(evaluate('2 * 5 > 3 * 3'))
    self.assertFalse(evaluate('2 * 8 > 4 * 4'))
    self.assertFalse(evaluate('6 * 4 > 5 * 5'))

  def test_if_clause(self):
    self.assertEqual(3, evaluate('if(2 = 2, 3, 4)'))
    self.assertEqual(4, evaluate('1 + if(3 > 1, 3, 1) * if(3 < 1, 3, 1)'))

class TempFile(object):
  def __init__(self, path, lines):
    self.path = path
    self.lines = lines

  def __enter__(self):
    with open(self.path, 'x') as outfile:
      for l in self.lines:
        outfile.write(l + '\n')

  def __exit__(self, *args):
    os.remove(self.path)

def ExecAndRead(lines, path, params={}):
  command = sql.GetCommandList(lines)
  command.Eval({}, params)
  with open(path, 'r') as result:
    lines = [l.strip() for l in result.readlines()]
  os.remove(path)
  return lines

def SomeContent():
  # To be used only when the actual content is irrelevant.
  return [
      'ID;NAME;VAL',
      '1;La Isla Bonita;10',
      '2;Żółte Kalendarze;3']

class TestCommandList(unittest.TestCase):
  def test_load_and_dump(self):
    content = SomeContent()
    command = ['LOAD data FROM "test.csv";',
               'DUMP data TO "output.csv";']

    with TempFile('test.csv', content):
      self.assertEqual(content, ExecAndRead(command, 'output.csv'))

  def test_custom_separator(self):
    content = ['ID,NAME', '1,Smurf,', '2,Shrek,']
    expected = [x[:] for x in content]
    for x in expected:
      x.replace(',', ';')
    command = ['LOAD data FROM "temp.csv";',
               'DUMP data TO "output.ssv";']
    with TempFile('temp.csv', content):
      self.assertEqual(expected, ExecAndRead(command, 'output.ssv'))

  def test_variable_load_path_and_dump_table_and_path(self):
    content = SomeContent()
    command = ['LOAD table FROM $infile;',
               'DUMP $table TO $outfile;']
    params = {
      'infile': 'somefile.csv',
      'outfile': 'otherfile.csv',
      'table': 'table'
    }
    with TempFile('somefile.csv', content):
      output = ExecAndRead(command, 'otherfile.csv', params)
    self.assertEqual(content, output)

  def test_import_simple(self):
    content = SomeContent()
    command = ['IMPORT "configfile";']
    child_command = ['LOAD table FROM "temp.ssv";'
                     'DUMP table TO "res.ssv";']
    with TempFile('temp.ssv', content):
      with TempFile('configfile', child_command):
        outfile = ExecAndRead(command, 'res.ssv')
    self.assertEqual(content, outfile)

  def test_import_prefix(self):
    content = SomeContent()
    command = ['IMPORT "config" WITH PREFIX pref_;',
               'DUMP pref_table TO "res.ssv";']
    child_command = ['LOAD table FROM "temp.ssv";']
    with TempFile('temp.ssv', content):
      with TempFile('config', child_command):
        outfile = ExecAndRead(command, 'res.ssv')
    self.assertEqual(content, outfile)
  
  def test_import_params_passing_and_extra_params(self):
    content = SomeContent()
    command = ['IMPORT $childfile WITH PARAM infile "in.ssv";']
    child_command = ['LOAD table FROM $infile;',
                     'DUMP table TO $outfile;']
    params = {'outfile': 'out.ssv', 'childfile': 'conf.txt'}
    with TempFile('in.ssv', content):
      with TempFile('conf.txt', child_command):
        outfile = ExecAndRead(command, 'out.ssv', params)
    self.assertEqual(content, outfile)

  def test_import_param_renaming(self):
    content = SomeContent()
    command = ['IMPORT "config" WITH PARAM infile $child_infile;']
    child_command = ['LOAD table FROM $infile;'
                     'DUMP table TO "out.ssv";']
    with TempFile('in', content):
      with TempFile('config', child_command):
        outfile = ExecAndRead(command, 'out.ssv', {'child_infile': 'in'})
    self.assertEqual(content, outfile)
  
  def test_recursive_import(self):
    content = SomeContent()
    command = ['IMPORT "config1" WITH PREFIX "a_";',
               'DUMP a_b_c TO "out";']
    child1 = ['IMPORT "config2" WITH PREFIX "b_";']
    child2 = ['LOAD c FROM "in";']
    with TempFile('in', content):
      with TempFile('config1', child1):
        with TempFile('config2', child2):
          outfile = ExecAndRead(command, 'out')
    self.assertEqual(content, outfile)

  def test_import_chdir(self):
    content = SomeContent()
    command = ['IMPORT "testdata/config";', 'DUMP t TO "out";']
    child = ['LOAD t FROM "in";']
    with TempFile('testdata/in', content):
      with TempFile('testdata/config', child):
        outfile = ExecAndRead(command, 'out')
    self.assertEqual(content, outfile)

def Transform(content, exprs):
  command = ['LOAD table FROM "in";',
             'TRANSFORM table TO newtable WITH ' + exprs + ';',
             'DUMP newtable TO "out";']
  with TempFile('in', content):
    return ExecAndRead(command, 'out')

class TestTransform(unittest.TestCase):
  def test_one_column(self):
    content = ['ID', 'A', 'B']
    command = 'ID AS ID'
    self.assertEqual(content, Transform(content, command))

  def test_swap_columns(self):
    content = ['ColA;ColB', 'A;B']
    command = 'ColB AS ColB, ColA AS ColA'
    expected = ['ColB;ColA', 'B;A']
    self.assertEqual(expected, Transform(content, command))

  def test_column_by_index(self):
    content = ['ColA;ColB;ColC', '1;2;3']
    command = '$3 AS Val, $3 AS ValAgain'
    expected = ['Val;ValAgain', '3;3']
    self.assertEqual(expected, Transform(content, command))

  def test_constant(self):
    content = ['ColA;ColB', '1;2', 'A;B']
    command = 'ColA AS ColA, 1 AS ConstOne'
    expected = ['ColA;ConstOne', '1;1', 'A;1']
    self.assertEqual(expected, Transform(content, command))

  def test_expression(self):
    content = ['ColA;ColB;ColC', '1;2;3', '2;3;5', '1;-1;2']
    command = 'int(ColA) + 2 * int(ColB) - int(ColC) AS Val'
    expected = ['Val', '2', '3', '-3']
    self.assertEqual(expected, Transform(content, command))

  def test_range_expression_simple(self):
    content = ['ColA;ColB;ColC', '1;2;3']
    command = '$? FOR 2:4'
    expected = ['ColB;ColC', '2;3']
    self.assertEqual(expected, Transform(content, command))

if __name__ == '__main__':
  unittest.main()
