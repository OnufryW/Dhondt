#ifndef ASSIGN_SEATS_TO_PARTY
#define ASSIGN_SEATS_TO_PARTY

#include <string>
#include <map>
#include <vector>
#include <cstdlib>
#include <cassert>

#include "country_vote_bar.h"
#include "election_results.h"
#include "dhondt.h"
#include "map_tools.h"

// Takes actual election results, and the information which district gets
// how many seats, and calculates the total seats each party obtains.
// Votes is given in standard format: committee -> district -> int.
std::map<std::string, int> AssignSeatsToParty(
    const std::map<std::string, int> &district_seats,
    const std::map<std::string, std::map<std::string, int>> &votes) {
  std::map<std::string, int> results;
  std::map<std::string, bool> bar = PassesBar(votes);
  for (auto const &district_to_votemap : PivotMap(votes)) {
    std::string district = district_to_votemap.first;
    assert(district_seats.find(district) != district_seats.end());
    auto filtered_votes = FilterParties(district_to_votemap.second, bar);
    auto seat_counts = VotesToSeats(
        filtered_votes, district_seats.at(district));
    for (auto R : seat_counts) {
      results[R.first] += R.second;
    }
  }
  return results;
}

#endif // ASSIGN_SEATS_TO_PARTY
