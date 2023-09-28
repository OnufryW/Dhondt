#ifndef SEAT_PROBABILITY
#define SEAT_PROBABILITY

#include <map>
#include <set>
#include <string>
#include <vector>
#include <random>
#include <cmath>
#include "dhondt.h"
#include "distribution.h"
#include "map_tools.h"
#include "party_vote_distribution.h"

const double stddev_percent = 3.0;

// Assume that we know the vote values for all other parties; and we know
// that our party will have a number of votes distributed according to
// a given distribution.
// Calculates the probability that adding one vote to our party would
// increase the number of seats it gets (by 1, under sane conditions it won't
// increase by more).
long double SeatShiftProbability(
    const std::map<std::string, int> &votes,
    int total_seats, Distribution &our_votes,
    const std::set<std::string> &rejected_parties) {
  long double res = 0;
  std::vector<int> key_values =
      KeyVoteValues(votes, total_seats, rejected_parties);
  for (int val : key_values) {
    res += our_votes.CdfAt(val) - our_votes.CdfAt(val - 1);
  }
  return res;
}

long double SeatShiftProbabilityAllRandom(
    const std::map<std::string, int> &votes, int total_seats,
    std::string party, int repeats, std::mt19937 &gen, Expression *stddev,
    const std::set<std::string> &rejected_parties) {
  std::vector<long double> results;
  std::map<std::string, Distribution*> distributions;
  long long total_votes = SumMap(votes);
  for (const auto &p: votes) {
    distributions[p.first] =
        GetPartyVoteDistribution(p.second, total_votes, stddev);
  }
  for (int r = 0; r < repeats; r++) {
    std::map<std::string, int> random_votes;
    for (const auto &p : votes) if (p.first != party) {
      random_votes[p.first] = std::max(
          std::round(distributions[p.first]->Draw(gen)), 1.L);
    }
    results.push_back(SeatShiftProbability(
        random_votes, total_seats, *distributions[party], rejected_parties));
  }
  unsigned i = 0;
  // Adding all the results, bottom up, to avoid rounding errors.
  while (i + 1 < results.size()) {
    results.push_back(results[i] + results[i+1]);
    i += 2;
  }
  return results[i] / repeats;
}

// Input is the standard committee -> district -> expected votes map,
// a map from districts to seat counts, the number of repeats in each
// district, a random generator, and the expression for generating the
// stddev.
// We also take a list of rejected parties. The idea is that we want to
// prevent the parties on this list from gaining votes. So, if the list is
// non-empty, we will count the vote as "gained" only if the party that
// loses the vote is one of the rejected parties.
std::map<std::string, std::map<std::string, double>> ProbabilisticSeatStrengths(
    const std::map<std::string, std::map<std::string, int>> &expected_votes,
    const std::map<std::string, int> &seat_counts,
    int repeats, std::mt19937 &gen, Expression *stddev,
    const std::set<std::string> &rejected_parties) {
  // Pivoted result, we'll proceed by districts.
  std::map<std::string, std::map<std::string, double>> pivoted_res;
  for (const auto &district_data : PivotMap(expected_votes)) {
    const std::string &district = district_data.first;
    pivoted_res[district] = {};
    for (const auto &committee_data : district_data.second) {
      const std::string &committee = committee_data.first;
      if (rejected_parties.find(committee) != rejected_parties.end()) {
        continue;
      }
      long double prob = SeatShiftProbabilityAllRandom(
          district_data.second, seat_counts.at(district), committee,
          repeats, gen, stddev, rejected_parties);
      pivoted_res[district][committee] = 1000000 * prob;
    }
  }
  return PivotMap(pivoted_res);
}  

#endif // SEAT_PROBABILITY
