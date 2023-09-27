#ifndef DISTRIBUTION
#define DISTRIBUTION

#include <random>

// A probability distribution. Allows getting the density at a point,
// the CDF (that is, the probability that a randomly drawn point is <= pt)
// and drawing a random number, supplying an UNRG.
class Distribution {
 public:
  virtual long double DensityAt(long double pt) = 0;
  virtual long double CdfAt(long double pt) = 0;
  virtual long double Draw(std::mt19937 &gen) = 0;
};

#endif // DISTRIBUTION
