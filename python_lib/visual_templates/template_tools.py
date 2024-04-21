def bmp_to_intervals(bmp, green_threshold=200):
  """
  Args:
    bmp: A bitmap, which has a pair of integers "shape", and is an array
      of size [.shape[0]][.shape[1]][3] of values between 0 and 256.
    green_threshold: the threshold value, above which green pixels are
      considered to be a part of the template.

  Returns:
    A "template", which is a pair of:
      - A list of triples (y, x_start, x_end) that describe a set of
        intervals with constant y disjointly covering the template.
      - A pair of integers, describing the intended shape of the bitmap
        the template applies to.
  """
  intervals = []
  for y in range(bmp.shape[1]):
    interval_begin = None
    for x in range(bmp.shape[0]):
      if (bmp[x][y][0] == 0 and bmp[x][y][2] == 0 and 
          bmp[x][y][1] > green_threshold):
        if interval_begin is None:
          interval_begin = x
      else:
        if interval_begin is not None:
          intervals.append((y, interval_begin, x))
          interval_begin = None
    if interval_begin is not None:
      intervals.append((y, interval_begin, bmp.shape[0]))
  return (intervals, bmp.shape)

def write_template(template, outfile):
  """
  Write a template to file.

  Args:
    template: A "template", as above.
    outfile: the file object to write to.

  Returns: None
  """
  intervals, shape = template
  outfile.write('{} {}\n'.format(shape[0], shape[1]))
  for y, x1, x2 in intervals:
    outfile.write('{} {} {}\n'.format(y, x1, x2))

def read_template(infile):
  """
  Read a template from a file.

  Args:
    infile: a file object we're reading from.

  Returns:
    A "template", as above.
  """
  shape = None
  intervals = []
  for line in infile:
    if shape is None:
      shape = [int(x) for x in line.strip().split()]
      assert len(shape) == 2
    else:
      interval = [int(x) for x in line.strip().split()]
      assert len(interval) == 3
      intervals.append(interval)
  return (intervals, shape)

def apply_template(bmp, template, color):
  """
  Modify a bitmap by filling in the template with a color.

  Args:
    bmp: The bitmap object to which the template is being applied
    template: The template to apply, as above
    color: the RGB triple that the template shape will be colored in

  Returns: None
  """
  intervals, shape = template
  assert(bmp.shape[0] == shape[0] and bmp.shape[1] == shape[1])
  for y, x1, x2 in intervals:
    for x in range(x1, x2):
      bmp[x][y][0] = color[0]
      bmp[x][y][1] = color[1]
      bmp[x][y][2] = color[2]
      if len(bmp[x][y]) == 4:
        bmp[x][y][3] = 255
