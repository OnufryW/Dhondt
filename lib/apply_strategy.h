#ifndef APPLY_STRATEGY
#define APPLY_STRATEGY

#include <set>
#include <map>
#include <string>
#include <random>
#include "choose.h"
#include "map_tools.h"

std::map<std::string, std::map<std::string, int>> CalculateDeltas(
    const std::map<std::string, std::map<std::string, int>> &votes,
    Strategy &strategy, const std::set<std::string> &rejected_parties,
    int voters_used, std::mt19937 &gen) {
  int total_voters = SumMap(SumSubmaps(votes));
  std::map<std::string, std::map<std::string, int>> deltas;
  for (const auto &committee_data : votes) {
    deltas[committee_data.first] = {};
    for (const auto &district_data : committee_data.second) {
      deltas[committee_data.first][district_data.first] = 0;
    }
  }
  for (const auto &committee_data : votes) {
    auto committee = committee_data.first;
    // Rejected parties never apply our strategies.
    if (rejected_parties.find(committee) != rejected_parties.end()) {
      continue;
    }
    for (const auto &district_data : committee_data.second) {
      auto district = district_data.first;
      if (strategy.IsSource(district, committee)) {
        int applicable_voters =
            Choose(total_voters, voters_used, district_data.second, gen);
        total_voters -= applicable_voters;
        voters_used -= applicable_voters;
        double prob_weight = 1;
        for (const auto &component :
             strategy.GetStrategy(district, committee)) {
          int appliers = Select(
              applicable_voters, component.probability / prob_weight,
              gen);
          prob_weight -= component.probability;
          deltas[committee][district] -= appliers;
          deltas[component.target_committee]
                [component.target_district_id] += appliers;
          applicable_voters -= appliers;
        }
      }
    }
  }
  return deltas;
}

// Assumes that voters_used voters apply the strategy, and change their
// votes according to it (if the strategy does tell them to change votes)
// Returns the vote map (committee->district->number of votes)
std::map<std::string, std::map<std::string, int>> ApplyStrategy(
    const std::map<std::string, std::map<std::string, int>> &votes,
    Strategy &strategy, const std::set<std::string> &rejected_parties,
    int voters_used, std::mt19937 &gen) {
  auto deltas = CalculateDeltas(
      votes, strategy, rejected_parties, voters_used, gen);
  auto new_votes = votes;
  for (const auto &committee_data : votes) {
    auto committee = committee_data.first;
    for (const auto &district_data : committee_data.second) {
      auto district = district_data.first;
      new_votes[committee][district] += deltas[committee][district];
    }
  }
  return new_votes;
}

// Assumes that voters_used voters cancelled their use of the strategy
// - assume they did vote according to the strategy, and now they don't.
// Might end up impossible to apply, in which case we return an empty
// map, and "success" is set to false.
// Returns the vote map (committee -> district -> num votes)
std::map<std::string, std::map<std::string, int>> ReverseStrategy(
    const std::map<std::string, std::map<std::string, int>> &votes,
    Strategy &strategy, const std::set<std::string> &rejected_parties,
    int voters_used, std::mt19937 &gen, bool &success) {
  auto deltas = CalculateDeltas(
      votes, strategy, rejected_parties, voters_used, gen);
  auto new_votes = votes;
  for (const auto &committee_data : votes) {
    auto committee = committee_data.first;
    for (const auto &district_data : committee_data.second) {
      auto district = district_data.first;
      new_votes[committee][district] -= deltas[committee][district];
      if (new_votes[committee][district] < 0) {
        success = false;
        return {};
      }
    }
  }
  success = true;
  return new_votes;
}

#endif // APPLY_STRATEGY
