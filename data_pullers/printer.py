def ValidateCanonicalResults(results):
  codes = [row[0] for row in results]
  duplicates = [code for code in codes if codes.count(code) > 1]
  print(duplicates)
  assert not duplicates

def PrintToSsv(results, keys, parties, filename):
  parties = list(parties)
  with open(filename, mode='w') as f:
    f.write(';'.join(keys + parties) + '\n')
    for row in results:
      res = []
      for key in keys:
        res.append(str(results[row][key]))
      for party in parties:
        if party in results[row]['results']:
          res.append(str(results[row]['results'][party]))
        else:
          res.append('0')
      f.write(';'.join(res) + '\n')
