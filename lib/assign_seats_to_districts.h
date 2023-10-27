#ifndef ASSIGN_SEATS_TO_DISTRICTS
#define ASSIGN_SEATS_TO_DISTRICTS

#include <string>
#include <map>
#include <vector>
#include <algorithm>
#include <functional>

// Tries to assign seats to districts according to specified weights.
// Takes a map from district code to weight, and the total number of
// seats to assign, country-wide, and returns a map from district code
// to number of seats. Guarantees that:
// 1) The total number of seats assigned will be equal to total_seats
// 2) The number of seats assigned to a district will be equal to
//    (district_weight * total_seats) / (sum of all district weights)
//    rounded in one of the two possible directions
// 3) The first tiebreaker is the size of the remainder of the division
//    above (so, if one district has 2.3, and another has 1.7, and we have
//    4 seats to distribute, both will get 2).
// 4) The following tiebreakers are the total weight, and the code.
std::map<std::string, int> AssignSeatsToDistricts(
    const std::map<std::string, int> &weights, long long total_seats) {
  long long total_weights = 0;
  for (const auto &d : weights) {
    total_weights += d.second;
  }
  std::map<std::string, int> res;
  int assigned = 0;
  // Vector of (remainder, (original weight, district code))
  std::vector<std::pair<int, std::pair<int, std::string>>> remainders;
  for (const auto &d : weights) {
    long long base = (total_seats * d.second) / total_weights;
    res[d.first] = base;
    assigned += base;
    long long remainder = (total_seats * d.second) % total_weights;
    remainders.push_back(
        make_pair(remainder, make_pair(d.second, d.first)));
  }
  // The sort order is (remainder, original weight, district code), see #4
  // in the function comment.
  sort(remainders.begin(), remainders.end(),
      std::greater<std::pair<int, std::pair<int, std::string>>>());
  for (int i = 0; assigned < total_seats; i++) {
    res[remainders[i].second.second] += 1;
    assigned += 1;
  }
  return res;
}

#endif // ASSIGN_SEATS_TO_DISTRICTS
