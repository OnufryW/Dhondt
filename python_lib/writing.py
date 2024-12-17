import imageio.v3 as iio
import pathlib

class VisualizeWriteError(Exception):
  def __init__(self, msg):
    super().__init__(msg)

FONTS = [12, 19]

basedir = pathlib.Path(__file__).parent.resolve() / 'chars'

def putChar(img, basex, basey, height, char):
  """
  Writes the character char onto the image with the specified height & pos.

  Args:
    img: ImageIO image
    basex: x coordinate of the upper-left corner of the text
    basey: y coordinate of the upper-left corner of the text
    height: height of the text (in pixels)
    char: the character to write

  Returns: the new basex value (that is, basex + width of char).
  """
  filename = basedir / str(height) / (str(char) + '.bmp')
  try:
    template = iio.imread(uri=filename)
  except Exception as e:
    raise VisualizeWriteError(
        'Failed to open template file {} for "{}" of height {}'.format(
            filename, char, height)) from e
  if template.shape[0] != height:
    raise VisualizeWriteError(
        'Corrupted template {} - expected height {}, got {}'.format(
            filename, height, template.shape[0]))
  for x in range(template.shape[1]):
    for y in range(template.shape[0]):
      if template[y][x][0] != 255:
        for band in range(3):
          img[basey + y][basex + x][band] = template[y][x][band]
  return basex + template.shape[1]

def putNumber(img, basex, basey, height, number):
  """
  Writes the given number onto the image with the specified height & pos.

  Args:
    img: ImageIO image
    basex: x coordinate of the upper-left corner of the text
    basey: y coordinate of the upper-left corner of the text
    height: height of the text (in pixels)
    number: the number to write

  Returns: the new basex value (that is, basex + width of the number).
  """
  s = str(number)
  end = len(s)
  for i, c in enumerate(s):
    if c == '.':
      end = i 
  for c in s:
    if c == '.':
      end = len(s)
    elif c != '-' and (end - i) % 3 == 0:
      basex += 2
    basex = putChar(img, basex, basey, height, c)
  return basex

def putWord(img, basex, basey, height, word):
  for c in word:
    basex = putChar(img, basex, basey, height, c)
  return basex

