#ifndef ASSIGN_SEATS
#define ASSIGN_SEATS
#include "country_vote_bar.h"
#include "election_results.h"
#include "dhondt.h"
#include <string>
#include <map>
#include <vector>
#include <cstdlib>
#include <cassert>

// Takes actual election results, and the information which district gets
// how many seats, and calculates the total seats each party obtains.
std::map<std::string, int> AssignSeatsToParty(
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
