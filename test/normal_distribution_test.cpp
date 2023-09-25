#include <iostream>
#include <cassert>
#include <random>
#include "../lib/normal_distribution.h"
#include "../lib/distribution.h"
#include "test_util.h"

using std::cout;

void TestCdf(long double pt, long double expected, NormalDistribution &nd,
             long double eps = EPS) {
  cout << "[ RUNNING ] Cdf test at " << pt << std::endl;
  assert_eq_eps(expected, nd.CdfAt(pt), "cdf", eps);
  cout << "[ OK ]" << std::endl;
}

void MonteCarloTestCdf(long double pt, int retries, NormalDistribution &nd,
                       int seed) {
  cout << "[ RUNNING ] Random density test at " << pt << std::endl;
  // Running with a fixed seed to avoid flakiness.
  std::mt19937 gen(seed);
  long double hits = 0;
  for (int i = 0; i < retries; ++i) {
    if (nd.Draw(gen) < pt) hits += 1;
  }
  long double rate = nd.CdfAt(pt);
  long double stddev = sqrtl(rate * (1. - rate) / retries);
  // Expect the actual result to be within three standard deviations of the
  // expected result.
  assert_eq_eps(rate, hits / retries, "cdf", 3 * stddev);
  cout << "[ OK ]" << std::endl;
}

int main() {
  // First, test the properties of the standard normal distribution.
  NormalDistribution standard(0, 1);
  TestCdf(0, 0.5L, standard);
  TestCdf(1, 0.8413, standard, 0.0001);
  TestCdf(2, 0.9772, standard, 0.0001);

  // Test a few other distributions.
  NormalDistribution mean_one(1, 1);
  TestCdf(0, standard.CdfAt(-1), mean_one);
  TestCdf(0.5, standard.CdfAt(-0.5), mean_one);

  NormalDistribution wide(0, 1000);
  TestCdf(0, 0.5, wide);
  TestCdf(500, standard.CdfAt(0.5), wide);
  TestCdf(2000, standard.CdfAt(2), wide);

  NormalDistribution skew(0.5, 0.5);
  TestCdf(0.5, 0.5, skew);
  TestCdf(1, standard.CdfAt(1), skew);
  TestCdf(2, standard.CdfAt(3), skew);

  // A bunch of Monte Carlo tests. Pick a fixed twister to avoid flakiness.
  MonteCarloTestCdf(1.5, 1000, standard, 1234);
  MonteCarloTestCdf(-0.5, 1000, standard, 2345);
  MonteCarloTestCdf(0.33, 1000, mean_one, 3456);
  MonteCarloTestCdf(-2023, 1000, wide, 4567);
  MonteCarloTestCdf(472, 1000, wide, 5678);
  MonteCarloTestCdf(0.12, 1000, skew, 6789);
  MonteCarloTestCdf(2.1, 1000, skew, 7890);
  // Two high accuracy tests, one in the middle, one on the edge.
  MonteCarloTestCdf(0, 100000, standard, 12345);
  MonteCarloTestCdf(2.5, 100000, standard, 67890);
}
