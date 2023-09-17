#ifndef NORMAL_DISTRIBUTION
#define NORMAL_DISTRIBUTION

#include <cmath>
#include <random>
#include "distribution.h"

namespace {
long double sq(long double x) { return x * x; }
const long double sqrt2 = sqrtl(2);
}  // anon namespace

// The implementation of a Gaussian distribution in terms of distribution.h
class NormalDistribution : public Distribution {
 public:
  NormalDistribution(long double mean, long double stddev) :
    nd(mean, stddev), mean(mean), stddev(stddev) {}
  
  long double DensityAt(long double pt) {
    return
        exp(-sq(pt-mean) / (2 * sq(stddev))) / (stddev * sqrt(2 * M_PIl));
  }

  long double CdfAt(long double pt) {
    return 0.5 * (1 + erf((pt - mean) / (stddev * sqrt2)));
  }

  long double Draw(std::mt19937 &gen) {
    return nd(gen);
  }

 private:
  std::normal_distribution<long double> nd;
  long double mean;
  long double stddev;
};

#endif // NORMAL_DISTRIBUTION
