"""
Converts a template file to a BMP. This is mostly for debugging.

Usage: python3 template_to_bmp.py template_file_name bmp_file_name base_file_name
"""

import imageio.v3 as iio
import sys
import template_tools

if len(sys.argv) != 4:
  print('Usage: {} TEMPLATE_FILE_NAME BMP_FILE_NAME BASE_FILE_NAME'.format(sys.argv[0]))
  sys.exit(1)

with open(sys.argv[1], 'r') as templatefile:
  template = template_tools.read_template(templatefile)
base = iio.imread(sys.argv[3])
template_tools.apply_template(base, template, (255,0,0))
iio.imwrite(uri=sys.argv[2], image=base)

