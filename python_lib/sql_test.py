import unittest
import os

import sql
import tokenizer

def tokenValues(s):
  return [t.value for t in tokenizer.tokenize([s])]

def fullTokens(s):
  return [t.value + '$' + t.typ for t in tokenizer.tokenize([s])]

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
    
  def test_variable(self):
    self.assertEqual(['Krowa'], tokenValues('$Krowa'))
    self.assertEqual(['?'], tokenValues('$?'))
    self.assertEqual(['?header'], tokenValues('$?header'))
    self.assertEqual(['?header', 'header', '?'],
        tokenValues('$?header$header$?'))
    self.assertEqual(['', '(', '?', ')',], tokenValues('$($?)'))

  def test_token_types(self):
    self.assertEqual(['A$word', '=$symbol', '4$number'],
                     fullTokens('A = 4'))

def evaluate(s, c={}):
  return sql.GetExpression(tokenizer.tokenize([s])).Eval(c)

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

  def test_range_sum(self):
    self.assertEqual(9, evaluate('sum_range(2:5)',
                                 {'1': 1, '2': 2, '3': 3, '4': 4}))

  def test_aggregate(self):
    self.assertEqual(9, evaluate('sum(arg)',
                                 {'__group_context': [{'arg': 3}, {'arg': 6}]}))

  def dhondt_helper(self, seats, votes, expected):
    context = {}
    for i, v in enumerate(votes):
      context[str(i+1)] = v
    context['__dynamic'] = {}
    for i, v in enumerate(votes):
      context['__dynamic']['?'] = str(i+1)
      expr = 'dhondt({}, {}, 1:{})'.format(seats, v, len(votes) + 1)
      self.assertEqual(expected[i], evaluate(expr, context))

  def test_dhondt(self):
    self.dhondt_helper(4, [20, 4], [4, 0])
    self.dhondt_helper(4, [20, 7], [3, 1])
    self.dhondt_helper(3, [20, 16, 10], [2, 1, 0])

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

  def test_ignore_quoted_separator(self):
    content = ['ID$NAME$VALUE', '1$"$"$"\'\'$$"""', '2$$', '3$\'"$\'$"$"']
    expected = ['ID;NAME;VALUE', '1;"$";"\'\'$$"""', '2;;', '3;\'"$\';"$"']
    command = [
        'LOAD x FROM "x.csv" WITH SEPARATOR "$" WITH IGNORE QUOTED SEPARATOR;',
        'DUMP x TO "y.csv";']
    with TempFile('x.csv', content):
      self.assertEqual(expected, ExecAndRead(command, 'y.csv'))

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

  def test_import_with_table(self):
    content = SomeContent()
    command = ['LOAD table FROM "in.ssv";',
               'IMPORT "config" WITH TABLE table WITH PREFIX v;']
    child_command = ['DUMP table TO "out.ssv";']
    with TempFile('in.ssv', content):
      with TempFile('config', child_command):
        outfile = ExecAndRead(command, 'out.ssv')
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

  def test_range_dhondt(self):
    content = ['ID;Seats;B;C;D', 'X;5;10;7;3', 'Y;3;13;5;12']
    command = ['LOAD t FROM "in";',
               'TRANSFORM t WITH ID AS ID, int($?) FOR 2:;',
               'TRANSFORM t WITH ID AS ID, dhondt(Seats, $?, 3:) FOR 3:;'
               'DUMP t TO "out";']
    expected = ['ID;B;C;D', 'X;3;2;0', 'Y;2;0;1']
    with TempFile('in', content):
      self.assertEqual(expected, ExecAndRead(command, 'out'))

  def test_range_expression_custom_header(self):
    content = ['ColA;ColB;ColC', '1;2;3', '4;5;6']
    command = '$? FOR 2: AS $?header + "_new"'
    expected = ['ColB_new;ColC_new', '2;3', '5;6']
    self.assertEqual(expected, Transform(content, command))

  def test_refer_variable(self):
    content = ['A;B;C', '1;2;A', '3;4;B']
    command = '$(C) AS selected'
    expected = ['selected', '1', '4']
    self.assertEqual(expected, Transform(content, command))

  def test_refer_variable_range(self):
    content = ['A;B;C;D', '1;2;A;A', '3;4;B;A']
    command = '$($?) FOR 3:'
    expected = ['C;D', '1;1', '4;3']
    self.assertEqual(expected, Transform(content, command))

  def test_header_access(self):
    content = ['A;B', 'x;y', 'z;v']
    command = '$?header + $? FOR 1:'
    expected = ['A;B', 'Ax;By', 'Az;Bv']
    self.assertEqual(expected, Transform(content, command))

def Aggregate(content, aggregate):
  command = [
      'LOAD table FROM "in";',
      'TRANSFORM table WITH int($?) FOR 1:;',
      aggregate,
      'DUMP newt TO "out";']
  with TempFile('in', content):
    return ExecAndRead(command, 'out')

def SimpleAggregate(content, group, exprs):
  return Aggregate(
    content,
    'AGGREGATE table TO newt BY ' + group + ' WITH ' + exprs + ';')

class TestAggregate(unittest.TestCase):
  def test_aggregate_in_place(self):
    content = ['ColA', '1', '2']
    command = ['LOAD table FROM "in";',
               'AGGREGATE table WITH 1 AS one;',
               'DUMP table TO "out";']
    expected = ['one', '1']
    with TempFile('in', content):
      self.assertEqual(expected, ExecAndRead(command, 'out'))

  def test_empty_key_list(self):
    command = 'AGGREGATE table TO newt WITH sum($1) AS sA, sum($2) AS sB;'
    content = ['A;B', '1;2', '0;2', '0;3']
    expected = ['sA;sB', '1;7']
    self.assertEqual(expected, Aggregate(content, command))

  def test_full_split(self):
    content = ['ColA;ColB', '1;1', '2;2']
    groups = '$1'
    exprs = 'ColA AS ColA, sum(ColB) AS ColB'
    expected = ['ColA;ColB', '1;1', '2;2']
    self.assertEqual(expected, SimpleAggregate(content, groups, exprs))

  def test_actual_grouping(self):
    content = ['A;B;C', '1;1;1', '1;1;2', '1;2;0', '2;1;0', '2;2;7', '2;2;0']
    groups = 'A, $2'
    exprs = '$1 AS a, B AS b, sum(C) AS c'
    expected = ['a;b;c', '1;1;3', '1;2;0', '2;1;0', '2;2;7']
    self.assertEqual(expected, SimpleAggregate(content, groups, exprs))

  def test_non_contiguous_rows(self):
    content = ['X;Y', '1;1', '2;2', '1;1']
    groups = 'X'
    exprs = 'sum(Y) AS s'
    expected = ['s', '2', '2']
    self.assertEqual(expected, SimpleAggregate(content, groups, exprs))
  
  def test_complex_expression(self):
    content = ['A;B;C;D', '1;2;3;4', '1;4;9;16', '2;3;3;4']
    groups = 'D'
    exprs = 'D AS D, sum(A) + max(B) + D - max(C) * max(C) AS res'
    expected = ['D;res', '4;1', '16;-60']
    self.assertEqual(expected, SimpleAggregate(content, groups, exprs))

  def test_inner_expression(self):
    content = ['A;B;C', '1;4;2', '1;6;3', '2;2;2']
    groups = 'A'
    exprs = 'A AS A, int(sum(B / C)) AS sum_of_quotients'
    expected = ['A;sum_of_quotients', '1;4', '2;1']
    self.assertEqual(expected, SimpleAggregate(content, groups, exprs))

  def test_range_expression(self):
    content = ['A;B;C', '1;2;3', '1;2;3', '2;3;4']
    groups = 'A'
    exprs = 'A AS A, sum($?) FOR 2:4'
    expected = ['A;B;C', '1;4;6', '2;3;4']
    self.assertEqual(expected, SimpleAggregate(content, groups, exprs))

def Join(left_content, right_content, on_clause):
  lines = ['LOAD left FROM "left.csv";',
           'LOAD right FROM "right.csv";',
           'JOIN left INTO right ON ' + on_clause + ' AS out;',
           'DUMP out TO "out.csv";']
  with TempFile('left.csv', left_content):
    with TempFile('right.csv', right_content):
      return ExecAndRead(lines, 'out.csv')

class TestJoin(unittest.TestCase):
  def test_single_row_join(self):
    left_content = ['A;B', '1;2']
    right_content = ['C;D', '1;3']
    expected = ['A;B;C;D', '1;2;1;3']
    self.assertEqual(expected, Join(left_content, right_content, 'A EQ C'))

  def test_multiple_rows(self):
    left_content = ['A;B', '1;A', '2;B']
    right_content = ['C;D', '2;X', '1;Y']
    expected = ['A;B;C;D', '2;B;2;X', '1;A;1;Y']
    self.assertEqual(expected, Join(left_content, right_content, 'A EQ C'))

  def test_unequal_match(self):
    left_content = ['A;B;C', 'X;One;Match', 'Y;Zero;Matches', 'Z;Two;M.']
    right_content = ['a;b', 'Z;1', 'Z;2', 'X;3']
    expected = [
        'A;B;C;a;b', 'Z;Two;M.;Z;1', 'Z;Two;M.;Z;2', 'X;One;Match;X;3']
    self.assertEqual(expected, Join(left_content, right_content, 'A EQ a'))

  def test_match_on_expression(self):
    left_content = ['S;W', '2;Two', '3;Three', '4;Four']
    right_content = ['x;y', '2;2', '2;0', '1;3', '4;0', '3;0', '1;1']
    expected = ['S;W;x;y', '4;Four;2;2', '2;Two;2;0', '4;Four;1;3',
                '4;Four;4;0', '3;Three;3;0', '2;Two;1;1']
    on_clause = 'int(S) EQ int(x) + int(y)'
    self.assertEqual(expected, Join(left_content, right_content, on_clause))

  def test_prefix_match(self):
    left_content = ['Prefix', 'A', 'BABA', 'ZE']
    right_content = ['Word', 'A', 'AA', 'ZERO']
    expected = ['Prefix;Word', 'A;A', 'A;AA', 'ZE;ZERO']
    on_clause = 'Prefix PREFIX Word'
    self.assertEqual(expected, Join(left_content, right_content, on_clause))

  def test_without_insert_unmatched_values(self):
    left_content = ['A', '1', '2']
    right_content = ['B', '1', '3']
    on_clause = 'A EQ B'
    self.assertRaises(ValueError, Join, left_content, right_content, on_clause)

  def test_insert_unmatched_values(self):
    left_content = ['A', '1', '2']
    right_content = ['B', '1', '3']
    expected = ['A;B', '1;1', ';3']
    on_clause = 'A EQ B WITH INSERT UNMATCHED VALUES'
    self.assertEqual(expected, Join(left_content, right_content, on_clause))

  def test_insert_unmatched_keys(self):
    left_content = ['A', '1', '2']
    right_content = ['B', '1', '1']
    expected = ['A;B', '1;1', '1;1', '2;']
    on_clause = 'A EQ B WITH INSERT MISSING KEYS'
    self.assertEqual(expected, Join(left_content, right_content, on_clause))

  def test_insert_unmatched_everything(self):
    left_content = ['A', '1', '2']
    right_content = ['B', '1', '3']
    expected = ['A;B', '1;1', ';3', '2;']
    on_clause = 'A EQ B WITH INSERT MISSING KEYS WITH INSERT UNMATCHED VALUES'
    self.assertEqual(expected, Join(left_content, right_content, on_clause))

  def test_raise_missing_keys(self):
    left_content = ['A', '1', '2']
    right_content = ['B', '1', '3']
    on_clause = 'A EQ B WITH RAISE UNMATCHED KEYS'
    self.assertRaises(ValueError, Join, left_content, right_content, on_clause)

  def test_join_single_row(self):
    left_content = ['A;B', '1;2']
    right_content = ['C;D', '3;4', '5;6']
    expected = ['A;B;C;D', '1;2;3;4', '1;2;5;6']
    on_clause = '1 EQ 1'
    self.assertEqual(expected, Join(left_content, right_content, on_clause))

class TestAppend(unittest.TestCase):
  def test_basic(self):
    lines = ['LOAD table FROM "data";',
             'APPEND 1, 2+2 TO table;',
             'DUMP table TO "out.csv";']
    content = ['A;B', '0;0', '1;1']
    expected = content + ['1;4']
    with TempFile('data', content):
      actual = ExecAndRead(lines, 'out.csv')
    self.assertEqual(expected, actual)

def Pivot(content, command, source, target):
  lines = ['LOAD {} FROM "in.csv";'.format(source),
           command,
           'DUMP {} TO "out.csv";'.format(target)]
  with TempFile('in.csv', content):
    return ExecAndRead(lines, 'out.csv')

class TestPivot(unittest.TestCase):
  def test_basic(self):
    content = ['A;B', '0;1', '2;3', '4;5']
    command = 'PIVOT table;'
    expected = ['col_1;col_2;col_3', '0;2;4', '1;3;5']
    self.assertEqual(expected, Pivot(content, command, 'table', 'table'))

  def test_change_target(self):
    content = ['A', '1']
    command = 'PIVOT table TO other;'
    expected = ['col_1', '1']
    self.assertEqual(expected, Pivot(content, command, 'table', 'other'))

  def test_with_new_headers(self):
    content = ['county;men;women', 'Foo;10;11', 'Bar;14;12', 'Baz;23;25']
    command = 'PIVOT table WITH NEW_HEADERS_FROM county;'
    expected = ['Foo;Bar;Baz', '10;14;23', '11;12;25']
    self.assertEqual(expected, Pivot(content, command, 'table', 'table'))

  def test_with_old_headers(self):
    content = ['PSL;PO;PiS', '12;25;31']
    command = 'PIVOT table WITH OLD_HEADERS_TO party;'
    expected = ['party;col_1', 'PSL;12', 'PO;25', 'PiS;31']
    self.assertEqual(expected, Pivot(content, command, 'table', 'table'))

  def test_all_options(self):
    content = ['City;Citizens;Eligible;Voters',
               'Warszawa;1800;1500;1200',
               'Krakow;800;700;500',
               'Wroclaw;700;600;550',
               'Lodz;650;500;380',
               'Poznan;550;400;370',
               'Gdansk;500;400;340']
    command = ('PIVOT source TO target WITH NEW_HEADERS_FROM City ' +
              'WITH OLD_HEADERS_TO datum;')
    expected = ['datum;Warszawa;Krakow;Wroclaw;Lodz;Poznan;Gdansk',
                'Citizens;1800;800;700;650;550;500',
                'Eligible;1500;700;600;500;400;400',
                'Voters;1200;500;550;380;370;340']
    self.assertEqual(expected, Pivot(content, command, 'source', 'target'))

if __name__ == '__main__':
  unittest.main()
