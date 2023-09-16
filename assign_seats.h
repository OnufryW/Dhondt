#ifndef ASSIGN_SEATS
#define ASSIGN_SEATS
#include "lib/election_results.h"
#include "country_vote_bar.h"
#include "lib/dhondt.h"
#include <string>
#include <map>
#include <vector>
#include <cstdlib>
#include <cassert>

std::map<std::string, int> GetElectionResults(
    const std::map<std::string, int> &district_seats,
    ElectionResults *er) {
  std::map<std::string, int> results;
  std::map<std::string, bool> bar = PassesBar(er);
  assert(er != nullptr);
  for (auto D : er->ByDistrict()) {
    std::string district = D.first;
    assert(district_seats.find(district) != district_seats.end());
    auto filtered_votes = FilterParties(D.second.VoteCountByParty(), bar);
    auto seat_counts = VotesToSeats(
        filtered_votes, district_seats.find(district)->second);
    for (auto R : seat_counts) {
      results[R.first] += R.second;
    }
  }
  return results;
}

#endif // ASSIGN_SEATS
