#ifndef NORMAL_DISTRIBUTION
#define NORMAL_DISTRIBUTION

#include <cmath>
#include <random>
#include "distribution.h"

namespace {
const long double sqrt2 = std::sqrt(2);
}  // anon namespace

// The implementation of a Gaussian distribution in terms of distribution.h
class NormalDistribution : public Distribution {
 public:
  NormalDistribution(long double mean, long double stddev) :
    nd(mean, stddev), mean(mean), stddev(stddev) {}

  long double CdfAt(long double pt) {
    return 0.5 * (1 + std::erf((pt - mean) / (stddev * sqrt2)));
  }

  long double Draw(std::mt19937 &gen) {
    return nd(gen);
  }

  long double StdDev() {
    return stddev;
  }

 private:
  std::normal_distribution<long double> nd;
  long double mean;
  long double stddev;
};

#endif // NORMAL_DISTRIBUTION
