import imageio.v3 as iio
import ipympl
import math
import matplotlib.pyplot as plt
import numpy as np
import sys

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
      lowDiff = floorD(vals[math.floor(len(vals) - targetSize - delta)] -
                       vals[math.ceil(targetSize + delta)], diffSkip)
      highDiff = ceilD(vals[math.ceil(len(vals) - targetSize + delta)] -
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

