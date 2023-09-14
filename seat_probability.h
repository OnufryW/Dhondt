#ifndef SEAT_PROBABILITY
#define SEAT_PROBABILITY

#include <map>
#include <string>
#include <vector>
#include <random>
#include <cmath>
#include "dhondt.h"

namespace {

const long double sqrt2 = sqrt(2);

// Returns the density of the normal distribution with mean and stddev at pt.
long double DensityAt(long double pt, double mean, double stddev) {
  return exp(-(pt - mean) * (pt - mean) / (2 * stddev * stddev)) / 
         (stddev * sqrt(2 * M_PIl));
}

long double CdfFromHereToPlusOne(
    long double pt, long double mean, long double stddev) {
  return 0.5 * (erf((pt + 1 - mean) / (stddev * sqrt2)) -
                erf((pt - mean) / (stddev * sqrt2)));
}
}  // namespace

// Assume that we know the vote values for all other parties; and we know
// that our party will have a number of votes distributed according to
// a normal distribution with expected value and std_dev given.
// Calculates the probability that adding one vote to our party would
// increase the number of seats it gets (by 1, under sane conditions it won't
// increase by more).
long double SeatShiftProbability(const std::map<std::string, int> &votes,
                                 int total_seats, int expected_value,
                                 long double std_dev) {
  long double res = 0;
  std::vector<int> key_values = KeyVoteValues(votes, total_seats);
  for (int val : key_values) {
    res += CdfFromHereToPlusOne(val, expected_value, std_dev);
    //res += DensityAt(val + 0.5, expected_value, std_dev);
  }
  return res;
}

long double SeatShiftProbabilityAllRandom(
    const std::map<std::string, int> &votes, int total_seats,
    long double stddev, std::string party, int repeats, std::mt19937 &gen) {
  std::vector<long double> results;
  std::normal_distribution d{0.L, stddev};
  for (int r = 0; r < repeats; r++) {
    std::map<std::string, int> random_votes;
    for (const auto& p : votes) if (p.first != party) {
      random_votes[p.first] = std::max(std::round(d(gen) + p.second), 1.L);
    }
    results.push_back(SeatShiftProbability(
        random_votes, total_seats, votes.at(party), stddev));
  }
  unsigned i = 0;
  while (i + 1 < results.size()) {
    results.push_back(results[i] + results[i+1]);
    i += 2;
  }
  return results[i] / repeats;
}

#endif // SEAT_PROBABILITY
