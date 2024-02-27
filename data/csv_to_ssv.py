# Transforms a comma-separated values file to a semicolon-separated-values,
# by changing all commas to semicolons. Assumes no semicolons, or commas
# that should be preserved, exist in the file.

# usage:
# python3 csv_to_ssv.py INFILE_PATH OUTFILE_PATH

import sys

assert len(sys.argv) == 3
infile = sys.argv[1]
outfile = sys.argv[2]

with open(infile, 'r') as inf:
  with open(outfile, 'w') as outf:
    for line in inf.readlines():
      outf.write(line.replace(',', ';'))
