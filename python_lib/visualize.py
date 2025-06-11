import imageio.v3 as iio
import math
import os
import pathlib
import sys
from visual_templates import template_tools
import writing

class VisualizeError(Exception):
  def __init__(self, msg):
    super().__init__(msg)

def ceilD(val, D):
  """Returns the smallest multiple of D which is no less than val."""
  residue = val % D
  if residue:
    return val - residue + D
  return val

def floorD(val, D):
  """Returns the largest multiple of D which is no larger than val."""
  return val - (val % D)

def howManyLower(vals, X):
  """Returns the number of entries in the sorted list vals that are < X."""
  lo = -1
  hi = len(vals)
  while hi - lo > 1:
    med = (hi + lo) // 2
    if vals[med] < X:
      lo = med
    else:
      hi = med
  return hi

def getBestBoundErr(vals, cutoff, diff, D):
  """
  Args:
    val: a sorted list of numbers
    cutoff: a number in (0, 0.5) - how much we want to cut off at each end.
    diff: a number (of the same 'type' as the entries of val)
    D: a number, of which the chosen x should be a multiple

  Given the sorted list val, we are looking for to extract some choose an
  interval of values [x, x+diff), such that:
    - x is a multiple of D
    - the number of vals <x and >=x+diff are both as close to cutoff as
      possible. "As close as possible" is measured here by the square error:
      if the fraction of vals below the interval is f, then the error
      contributed by the lower end is (f - cutoff)**2.

  Returns:
    The lowest possible error, and the value of x that attains it.
  """
  lo = floorD(vals[0], D)
  hi = ceilD(vals[-1], D)

  EPS = D / 10
  while hi - lo > D + EPS:  # EPS is needed, because there can be rounding errs.
    med = (hi + lo) / 2
    if (med + EPS) % D > 2 * EPS:
      med += D / 2
    if howManyLower(vals, med) + howManyLower(vals, med + diff) < len(vals):
      lo = med
    else:
      hi = med
  def calcErr(v):
    return (v - cutoff) ** 2
  def calcErrFromB(x):
    l = len(vals)
    return (calcErr(howManyLower(vals, x) / l) +
            calcErr((l - howManyLower(vals, x + diff)) / l))
  errLo = calcErrFromB(lo)
  errHi = calcErrFromB(hi)
  if errLo < errHi:
    return errLo, lo
  return errHi, hi

def getProposedBounds(vals, numBands, tolerance=0.5):
  """
  Args:
    vals: a list of numbers
    numBands: the number of bands into which we want to divide those numbers.
      The bands in the middle will each contain numbers in some interval
      [x, x+D). The lowest and highest band will contain, respectively,
      everything below and everything above. Both these bands need to contain
      between (1 - tolerance) (len(vals) / numBands) and 
      (1 + tolerance) (len(vals) / numBands) elements of val.
    tolerance: a number, below 0.5.

  What we're trying to achieve here is a choice where the band boundaries are
  as "nice-looking" as possible - which means "as divisible by 10 as possible,
  and among those, preferably divisible by 5 or 2. And among those, we prefer
  the one where the total error (as defined in getBestBoundErr) is the smallest.

  Returns: a list of all the range boundaries.
  """
  # For 2 bands, we'd have to handle a somewhat different problem.
  assert numBands > 2
  # Note: this code will loop forever if there are too many equal values on one
  # of the boundaries. Maybe we could check for this...
  vals = sorted(vals)
  startingD = 1
  while startingD < vals[-1] - vals[0]:
    startingD *= 10

  """ What we do here:
    - first, we select D, which is going to be the largest common divisor of all
      boundaries between bands.
    - then, the difference between the low and high bound has to be a multiple
      of D * (numBands - 2). We iterate over all the possible values between
      the lowest and highest possible differences that still leave roughly
      a tolerance-sized error.
    - for each such difference value, we check what's the best position of the
      middle interval, and find the best option across differences and intervals
    - if we found something that meets the tolerance bounds, we take the best
      option, and return it. If not, try a smaller D.
  """
  while True:
    for D in [startingD, startingD / 2, startingD / 5]:
      targetSize = len(vals) / numBands
      diffSkip = D * (numBands - 2)
      delta = tolerance * targetSize
      lowDiff = floorD(
          vals[math.floor(max(len(vals) - targetSize - delta, 0))] -
          vals[math.ceil(targetSize + delta)], diffSkip)
      highDiff = ceilD(
          vals[min(math.ceil(len(vals) - targetSize + delta), len(vals) - 1)] -
          vals[math.floor(targetSize - delta)], diffSkip)
      bestErr = None
      currDiff = max(0, lowDiff)
      while True:
        err, start = getBestBoundErr(vals, 1 / numBands, currDiff, D)
        if (abs(howManyLower(vals, start) - targetSize) <= delta and
            abs(len(vals) - howManyLower(vals, start + currDiff)
                - targetSize) <= delta):
          if bestErr is None or bestErr > err:
            bestErr = err
            best = (start, currDiff)
        currDiff += diffSkip
        if currDiff > highDiff + D / 2:
          break
      if bestErr is not None:
        return [best[0] + k * best[1] / (numBands - 2) 
                for k in range(numBands - 1)]
    startingD /= 10

colourScales = {
  'greyscale5': [[255,255,255], [190,190,190], [125,125,125], [60,60,60],
                 [0,0,0]],
  'green5': [[77,255,77], [0,204,0], [0,153,0], [0,102,0], [0,64,0]],
  'red5': [[255,102,102], [230,26,26], [179,0,0], [128,0,0], [77,0,0]],
  'blue5': [[0,255,255], [0,191,255], [0,128,255], [0,64,255], [0,0,191]],
  'test3': [[0,0,1], [0,0,2], [0,0,3]],
  'greentored9': [[0,2.5*90,0], [2.5*55,2.5*90,0], [2.5*78,2.5*90,0], 
                  [2.5*90,2.5*78,0], [2.5*100,2.5*70,0],
                  [2.5*94,2.5*38,2.5*4], [2.5*90,2.5*23,2.5*8], 
                  [2.5*78,2.5*8,2.5*8], [2.5*55,2.5*12,2.5*12]],
}

def addLegend(img, colorscale, boundaries):
  legendBot = img.shape[0] - 5
  legendTop = int(0.79 * legendBot) - 5
  legendWid = int(0.057 * img.shape[1])
  legendSquareHgt = (legendBot - legendTop) // len(colorscale)
  for index, color in enumerate(colorscale):
    for x in range(1, legendWid):
      for y in range(legendBot - (index + 1) * legendSquareHgt,
                     legendBot - index * legendSquareHgt - 1):
        img[y][x][0] = color[0]
        img[y][x][1] = color[1]
        img[y][x][2] = color[2]
        # if len(img[y][x] > 3):
        #   img[y][x][3] = 255
    fontSize = None
    for candFontSize in sorted(writing.FONTS):
      if candFontSize < legendSquareHgt - 1:
        fontSize = candFontSize
    if not fontSize:
      raise VisualizeError(
          'Failed to find font size smaller than {} for legend'.format(
              legendSquareHgt - 1))
    basey = legendBot - (index + 1) * legendSquareHgt + (legendSquareHgt - fontSize)
    basex = legendWid + 10
    if index == 0:
      basex = writing.putWord(img, basex, basey, fontSize, 'pon.')
      basex += 2
      basex = writing.putNumber(img, basex, basey, fontSize, boundaries[0])
    elif index == len(boundaries):
      basex = writing.putWord(img, basex, basey, fontSize, 'pow.')
      basex += 2
      basex = writing.putNumber(img, basex, basey, fontSize, boundaries[-1])
    else:
      basex = writing.putNumber(img, basex, basey, fontSize,
                                boundaries[index - 1])
      basex += 2
      basex = writing.putChar(img, basex, basey, fontSize, '-')
      basex += 2
      basex = writing.putNumber(img, basex, basey, fontSize,
                                boundaries[index])

def Visualize(data, outfile, basename, colours, lowbound, highbound,
              legend=True, header=None, title=None):
  if colours not in colourScales:
    raise VisualizeError('Unknown colour scale: {}'.format(colours))
  cols = colourScales[colours]
  nb = len(cols)
  if lowbound is None:
    boundaries = getProposedBounds(data.values(), nb)
  else:
    boundaries = [
        (k*highbound + (nb-k-2)*lowbound) / (nb-2) for k in range(nb-1)]
  basedir = pathlib.Path(__file__).parent.resolve() / 'visual_templates'
  if not (basedir / basename).exists():
    raise VisualizeError('Unknown visualization base ' + basename)
  try:
    base = iio.imread(uri=str(basedir / basename / 'base.bmp'))
  except Exception as e:
    raise VisualizeError('Unknown visualization base ' + basename) from e
  for datum in data:
    datum_tmpl = basedir / basename / (str(datum) + '.template')
    if not datum_tmpl.exists():
      raise VisualizeError('Unknown region {} in base {}'.format(
          datum, basename))
    with datum_tmpl.open('r') as datum_tmpl_file:
      template = template_tools.read_template(datum_tmpl_file)
    colIndex = 0
    while colIndex < len(boundaries) and data[datum] >= boundaries[colIndex]:
      colIndex += 1
    template_tools.apply_template(base, template, cols[colIndex])
  if legend:
    addLegend(base, cols, boundaries)
  if header:
    writing.putStr(base, 0, 0, 12, header)
  if title:
    writing.putStr(base, base.shape[1] // 2, 0, 19, title)
  iio.imwrite(uri=outfile, image=base)

