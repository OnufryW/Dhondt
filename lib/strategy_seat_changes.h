#ifndef STRATEGY_SEAT_CHANGES
#define STRATEGY_SEAT_CHANGES

#include <set>
#include <map>
#include <string>
#include <random>
#include "apply_strategy.h"

// Outputs a map committee -> district -> expected seat count change.
std::map<std::string, std::map<std::string, double>> CheckStrategyResults(
    const std::map<std::string, std::map<std::string, int>> &votes,
    const std::map<std::string, int> &seat_counts_per_district,
    Strategy &strategy, const std::set<std::string> &rejected_parties,
    int min_voters, int max_voters, int repeats,
    std::mt19937 &gen, long long &affected_voters) {
  std::map<std::string, std::map<std::string, double>> res;
  for (const auto &c_d : votes) {
    for (const auto &d_d : c_d.second) {
      res[c_d.first][d_d.first] = 0;
    }
  }

  std::map<std::string, std::map<std::string, int>> seat_baseline;
  auto by_district = PivotMap(votes);
  for (const auto &d_d : by_district) {
    seat_baseline[d_d.first] =
        VotesToSeats(d_d.second, seat_counts_per_district.at(d_d.first));
  }
  seat_baseline = PivotMap(seat_baseline);

  std::uniform_int_distribution applied_voters(min_voters, max_voters);
  int successful_attempts = 0;
  affected_voters = 0;
  for (int attempt = 0; attempt < repeats; ++attempt) {
    int voters = applied_voters(gen);
    int affected_voters_in_cycle = 0;
    bool success = true;
    std::map<std::string, std::map<std::string, int>> res_votes;
    if (voters > 0) {
      res_votes = ApplyStrategy(votes, strategy, rejected_parties, voters,
                                gen, affected_voters_in_cycle);
    } else {
      res_votes = ReverseStrategy(
        votes, strategy, rejected_parties,
        -voters, gen, success, affected_voters_in_cycle);
    }
    if (success) {
      successful_attempts += 1;
      affected_voters += affected_voters_in_cycle;
      res_votes = PivotMap(res_votes);
      for (const auto &d_d : res_votes) {
        auto new_seats =
            VotesToSeats(d_d.second, seat_counts_per_district.at(d_d.first));
        for (const auto &c_d : new_seats) {
          res[c_d.first][d_d.first] += new_seats[c_d.first];
        }
      }
    }
  }
  if (successful_attempts < repeats / 10 || successful_attempts == 0) {
    affected_voters = 0;
    return {};
  }
  affected_voters /= successful_attempts;
  for (auto &c_d : res) {
    for (auto &d_d : c_d.second) {
      d_d.second /= successful_attempts;
      d_d.second -= seat_baseline[c_d.first][d_d.first];
    }
  }
  return res;
}

#endif // STRATEGY_SEAT_CHANGES
