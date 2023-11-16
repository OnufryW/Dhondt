#include <iostream>
#include <cassert>
#include <random>
#include "../lib/choose.h"
#include "test_util.h"

using std::cout;

#define DEBUG 0

// I want to test that we won't be too far from the real answer. The metric
// I'll use will be the integral of the absolute value of the difference
// between the CDFs, and I'll expect that to be no more than 1% of the
// expected value of the result (KL/N).
void TestCdf(int N, int K, int L, int seed) {
  cout << "[ RUNNING ] Choose CDF test for N: " << N << ", K: " << K
       << ", L: " << L << std::endl;
  std::mt19937 gen(seed);
  std::map<int, int> pdf_choice;
  std::map<int, int> pdf_manual;
  const int repeats = 10000;
  int mval = 0;
  for (int i = 0; i < repeats; ++i) {
    int r = ChooseManual(N, K, L, gen);
    pdf_manual[r] = pdf_manual[r] + 1;
    if (mval < r) mval = r;
    r = Choose(N, K, L, gen);
    pdf_choice[r] = pdf_choice[r] + 1;
    if (mval < r) mval = r;
  }
  long long cdf_delta = 0;
  long long cdf_delta_integral = 0;
  long long expected = 0;
  long long expected_square = 0;
  for (int i = 0; i <= mval; ++i) {
    expected += (long long) i * (long long) pdf_manual[i];
    expected_square +=
        (long long) i * (long long) i * (long long) pdf_manual[i];
    cdf_delta += pdf_choice[i] - pdf_manual[i];
    cdf_delta_integral += (cdf_delta < 0) ? -cdf_delta : cdf_delta;
  }
  long long stddev = expected_square * repeats - expected * expected;
  long long threshold = std::sqrt(stddev) / 20;
  if (cdf_delta_integral > threshold || DEBUG) {
    cout << "FAILED: Delta integral is " << cdf_delta_integral
         << ", vs threshold of " << threshold << std::endl;
    cout << "v;manual;choose" << std::endl;
    bool ready = false;
    for (int i = 0; i <= mval; ++i) {
      if (pdf_choice[i] + pdf_manual[i]) ready = true;
      if (ready) {
        cout << i << ";" << pdf_manual[i] << ";"
             << pdf_choice[i] << std::endl;
      }
    }
  }
  assert(cdf_delta_integral <= threshold);
  cout << "[ OK ]" << std::endl;
}

int main() {
  TestCdf(200, 50, 50, 1);  // Trivial test, check stability.
  TestCdf(1000000, 50, 50, 2);  // Again, stability test.
  TestCdf(800, 600, 300, 3);  // Reversing
  TestCdf(2000, 1000, 1000, 9);
  TestCdf(1002, 501, 501, 4);  // First approximation, CLT
  TestCdf(13000, 501, 501, 5);  // First approximation, Poisson
  TestCdf(200000, 2000, 600, 6);
  TestCdf(1000000, 10000, 1000, 7);
  TestCdf(40000, 10000, 5000, 8);
}
