#ifndef CHOOSE
#define CHOOSE

#include <random>
#include <cassert>
#include <cmath>
#include <vector>

// I have no idea how to do it effectively. Does someone?

// This is just straightforward simulation.
int ChooseManual(int N, int K, int L, std::mt19937 &gen) {
  int res = 0;
  while (K) {
    std::uniform_int_distribution D(0, N-1);
    if (D(gen) < L) {
      L -= 1;
      res += 1;
    }
    N -= 1;
    K -= 1;
  }
  return res;
}

std::vector<double> factorials;

double factorial(int k) {
  if (factorials.empty()) factorials.push_back(1);
  while (factorials.size() <= (size_t) k) {
    factorials.push_back(factorials.back() * factorials.size());
  }
  return factorials[k];
}

double PoissonDensity(double lambda, int k) {
  return std::pow(lambda, k) * std::exp(-lambda) / factorial(k);
}

// This assumes we're in the Poisson domain (sum of rare events).
int ChoosePoisson(int N, int K, int L, std::mt19937 &gen) {
  int res = 0;
  double lambda = (double) L * (double) K / (double) N;
  std::uniform_real_distribution<double> dis(0.0, 1.0);
  double choice = dis(gen);
  while (choice > PoissonDensity(lambda, res)) {
    choice -= PoissonDensity(lambda, res);
    res += 1;
  }
  return res;
}

// This assumes we're in the CLT domain (sum of many events).
int ChooseNormal(int N, int K, int L, std::mt19937 &gen) {
  // Expected value. Hard to guess which approximation is better - on one
  // hand, the CLT approximation would be better with more events (so, L
  // random draws with probability K/N each), but on the other hand I think
  // the approximation by independent events is better with K random draws
  // with probability L/N each. I think the independence approximation has
  // larger errors, so...
  double single = (double) L / (double) N;
  double expected = K * single;
  double variance = std::sqrt(K * single * (1. - single));
  std::normal_distribution<double> nd(expected, variance);
  double res = nd(gen) + 0.5;
  assert (res > 0);
  return res;
}

// Assume we have a population of size N, and we select K elements without
// repetition. We also have a fixed subset of size L of the population.
// Returns the correctly distributed number of elements from the fixed
// subset we select.
int Choose(int N, int K, int L, std::mt19937 &gen) {
  assert(K <= N);
  assert(L <= N);
  assert(K >= 0);
  assert(L >= 0);
  // Make K and L small.
  if (N - K < K) {
    // We choose N-K elementst that remain. The remainder from L are chosen.
    return L - Choose(N, N-K, L, gen);
  }
  if (N - L < L) {
    // Just note that L and K are symmetrical - we have two populations, 
    // and ask how many elements intersect.
    return K - Choose(N, K, N-L, gen);
  }
  // Make K smaller than L.
  if (K > L) {
    return Choose(N, L, K, gen);
  }
  if (K <= 500) return ChooseManual(N, K, L, gen);
  // Now 100 < K <= L <= N / 2. I'll want to apply some sort of a law of
  // large numbers. Our lives would be simpler if the events were
  // independent. In the simulation, we're looking at probability being
  // N / L, where N and potentially L shifts by 1 with each draw. In the
  // worst case 500 = K = L = N/2. In this case, the CDFs shift by no more
  // than 10%, and the absolute value of the difference is around 2.5 
  // (with an expected value of the result being 250, so the delta is ~1%).
  // I consider that acceptable error.
  // So, let's assume we just have independent draws. In this case, we need
  // to pick the law - Poisson, or CLT. I'm gonna put the difference at 
  // an expected value of 20 (where the expected value is K * L / N).
  if ((long long) K * (long long) L / (long long) N > 20LL) {
    return ChooseNormal(N, K, L, gen);
  } else {
    return ChoosePoisson(N, K, L, gen);
  }
}

// Assume we have a population of size N, and for each member of that
// population we choose them with probability p. Returns the correctly
// distributed number of elements chosen.
int Select(int N, double p, std::mt19937 &gen) {
  assert(N >= 0);
  assert(p >= 0);
  assert(p <= 1);
  int res = 0;
  std::uniform_real_distribution D(0., 1.);
  for (int i = 0; i < N; ++i) {
    if (D(gen) < p) {
      res += 1;
    }
  }
  return res;
}

#endif // CHOOSE
