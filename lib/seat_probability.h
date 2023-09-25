#ifndef SEAT_PROBABILITY
#define SEAT_PROBABILITY

#include <map>
#include <string>
#include <vector>
#include <random>
#include <cmath>
#include "dhondt.h"
#include "distribution.h"
#include "normal_distribution.h"

const double stddev_percent = 3.0;

// Assume that we know the vote values for all other parties; and we know
// that our party will have a number of votes distributed according to
// a given distribution.
// Calculates the probability that adding one vote to our party would
// increase the number of seats it gets (by 1, under sane conditions it won't
// increase by more).
long double SeatShiftProbability(const std::map<std::string, int> &votes,
                                 int total_seats, Distribution &our_votes) {
  long double res = 0;
  std::vector<int> key_values = KeyVoteValues(votes, total_seats);
  for (int val : key_values) {
    res += our_votes.CdfAt(val) - our_votes.CdfAt(val - 1);
  }
  return res;
}

long double SeatShiftProbabilityAllRandom(
    const std::map<std::string, int> &votes, int total_seats,
    std::string party, int repeats, std::mt19937 &gen) {
  std::vector<long double> results;
  std::map<std::string, Distribution*> distributions;
  long long total_votes = 0;
  for (const auto &p: votes) {
    total_votes += p.second;
  }
  for (const auto &p: votes) {
    distributions[p.first] = new NormalDistribution(
        p.second, total_votes * stddev_percent / 100);
  }
  for (int r = 0; r < repeats; r++) {
    std::map<std::string, int> random_votes;
    for (const auto& p : votes) if (p.first != party) {
      random_votes[p.first] = std::max(
          std::round(distributions[p.first]->Draw(gen)), 1.L);
    }
    results.push_back(SeatShiftProbability(
        random_votes, total_seats, *distributions[party]));
  }
  unsigned i = 0;
  // Adding all the results, bottom up, to avoid rounding errors.
  while (i + 1 < results.size()) {
    results.push_back(results[i] + results[i+1]);
    i += 2;
  }
  return results[i] / repeats;
}

#endif // SEAT_PROBABILITY
