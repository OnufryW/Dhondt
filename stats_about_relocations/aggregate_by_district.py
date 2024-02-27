import sys

DISTRICT_DEFS = '../district_definitions/2023_district_definitions.csv'

def validate_district_defs(pref_map):
  # Validates that the map is prefix-unique (that is, that for any two 
  # keys in the map, one isn't a prefix of the other).
  for key in pref_map:
    for l in range(len(key)):
      assert key[:l] not in pref_map


def parse_district_defs():
  pref_map = {}
  with open(DISTRICT_DEFS, 'r') as defs:
    for l in defs.readlines():
      if l[0] == '#': continue
      if not l: continue
      split_l = l.split(';')
      assert split_l[0].strip() not in pref_map
      pref_map[split_l[0].strip()] = split_l[1].strip()
  validate_district_defs(pref_map)
  return pref_map


def to_teryt(s):
  s = s.strip()
  if len(s) > 7:
    raise ValueError
  while len(s) != 7:
    s = '0' + s
  int(s)
  return s

def is_teryt(s):
  try:
    to_teryt(s)
  except ValueError:
    return False
  return True


def to_int(s):
  try:
    return int(s)
  except ValueError:
    return 0


def aggregate_file(filename):
  pref_map = parse_district_defs()
  res = {}
  with open(filename, 'r') as f:
    for l in f.readlines():
      spl = l.split(',')
      if not is_teryt(spl[0]):
        continue
      teryt = to_teryt(spl[0])
      district = ''
      while teryt and not district:
        if teryt in pref_map:
          district = pref_map[teryt]
        else:
          teryt = teryt[:-1]
      if not district:
        raise AssertionError(l + ',' + to_teryt(spl[0]))
      if district not in res:
        res[district] = 0
      for v in spl[1:]:
        res[district] += to_int(v)
  return res


def output_csv(filename, res_map):
  total = 0
  with open(filename, 'w') as f:
    for d in res_map:
      total += res_map[d]
      f.write(str(d) + ';' + str(res_map[d]) + '\n')
  print('Total accumulated value: ', total)


assert len(sys.argv) == 3
output_csv(sys.argv[2], aggregate_file(sys.argv[1]))
