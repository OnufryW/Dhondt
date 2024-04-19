import unittest

import visualize as v

class TestBoundaries(unittest.TestCase):
  def testCeilD(self):
    self.assertEqual(10, v.ceilD(5, 10))
    self.assertEqual(10, v.ceilD(10, 10))
    self.assertEqual(0.1, v.ceilD(0.01, 0.1))
    self.assertEqual(0, v.ceilD(-1, 3))
    self.assertEqual(-1.5, v.ceilD(-2, 1.5))

  def testHowManyLower(self):
    self.assertEqual(5, v.howManyLower([1,2,3,4,5], 6))
    self.assertEqual(4, v.howManyLower([1,2,3,4,5], 5))
    self.assertEqual(0, v.howManyLower([1,2,3,4,5], 1))
    self.assertEqual(3, v.howManyLower([1,3,6,12,24,48,122], 7))

  def testBestBoundErr(self):
    self.assertEqual((0.125**2, 10), v.getBestBoundErr(
        [1,3,6,12,24,48,51,132], 0.25, 40, 10))
    self.assertEqual(5, v.getBestBoundErr(
        [1,3,5,6,8,10,12], 1/3, 10, 5)[1])
    self.assertEqual(5, v.getBestBoundErr(
        [1,3,5,6,8,9,12], 1/3, 10, 5)[1])

  def testGetProposedBounds(self):
    vals = [1, 3, 6, 12, 24, 48, 51, 132]
    self.assertEqual([10, 30, 50], v.getProposedBounds(vals, 4))
    # Actual vote strength data from last election.
    vals = [45624, 46194, 48503, 48538, 48872, 46310, 45687, 47003,
            45655, 44091, 44427, 45583, 47345, 47476, 44843, 49174,
            48900, 49037, 50432, 48716, 47996, 44199, 44918, 44864,
            47406, 45526, 44534, 46277, 43045, 47699, 43847, 47244,
            47080, 49896, 48882, 49297, 46582, 45915, 45849, 46021,
            46192]
    self.assertEqual([45000., 46000., 47000., 48000.],
                     v.getProposedBounds(vals, 5))
    # Pers vote shift data.
    vals = [0, 0.3141, 0, 0.7669, -0.436, 0, 0, 0, -0.7632, 0, -0.0787,
            0, 0.5768, 0, 0.5768, 0, 0, -0.5750, 0, 0, 0.8174, -0.2261,
            0, 0, 0, 0, -0.081, 0, -0.3134, -0.6551, -0.4520, 0.6210,
            -0.2725, -0.7043, 0, -0.0734, 0, 0.1416, -0.0002, 0, 
            0.7424, 0, -0.0093]
    self.assertEqual([-0.4, -0.2, 0, 0.19999999999999996, 0.4, 0.6],
                     v.getProposedBounds(vals, 7))

if __name__ == '__main__':
  unittest.main()
