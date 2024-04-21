"""
Converts a BMP file where the G color (0,255,0) with some tolerance
denotes the template to a template file (which is basically a list of
intervals (with a constant y) that are a part of the template.

The format of the template file is a series of lines, where each line
contains three integers: the y coordinate, and x1, x2, where [x1, x2)
is in the template.

Note: I could compress this file 2-3x by storing the ints as two-byte
sequences (I don't expect to process maps larger than 64K pixels in one
direction), but it's probably not worth it now (and it would be harder to
parse and debug).

Usage: python3 bmp_to_template.py bmp_file_name template_file_name
"""

import imageio.v3 as iio
import sys
import template_tools

if len(sys.argv) != 3:
  print('Usage: {} BMP_FILE_NAME TEMPLATE_FILE_NAME'.format(sys.argv[0]))
  sys.exit(1)

bmp = iio.imread(sys.argv[1])
template = template_tools.bmp_to_intervals(bmp, 50)
with open(sys.argv[2], 'w') as template_file:
  template_tools.write_template(template, template_file)

