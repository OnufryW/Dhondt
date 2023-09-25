#ifndef COUNTRY_VOTE_BAR
#define COUNTRY_VOTE_BAR

#include <map>
#include <string>

// This is somewhat of a hack. I'm hereby assuming:
// 1) The only minority committee is the Germans, with the name as below
// 2) The string "KOALICYJNY" is a clear distinguisher for coalitions
//    (this does seem to hold up in both 2019 and 2023).
// Returns the bar (in percent) that the committe has to pass, country-wide,
// to receive seats.
int BarValue(std::string committee_name) {
  if (committee_name.find("MNIEJSZOŚĆ") != std::string::npos ||
      committee_name.find("Mniejszość") != std::string::npos) {
    return 0;
  }
  if (committee_name.find("KOALICYJNY") == 0 ||
      committee_name == "Trzecia Droga" ||
      committee_name == "Koalicja Obywatelska") return 8;
  return 5;
}

// Takes the election results, and returns a map from committee name to
// a boolean: true if the committee is eligible to receive seats.
// Votes should be given in standard format: committee -> district -> int
std::map<std::string, bool> PassesBar(
    const std::map<std::string, std::map<std::string, int>> &votes) {
  std::map<std::string, long long> total_votes_per_party;
  long long country_votes = 0;
  for (const auto &party : votes) {
    total_votes_per_party[party.first] = 0;
    for (const auto &district : party.second) {
      total_votes_per_party[party.first] += district.second;
      country_votes += district.second;
    }
  }
  std::map<std::string, bool> result;
  for (auto party : total_votes_per_party) {
    int bar = BarValue(party.first);
     result[party.first] = (bar * country_votes < 100LL * party.second);
  }
  return result;
}

// Takes a map (from committee to some integer), and removes from the
// map those committees that aren't eligible for seats.
std::map<std::string, int> FilterParties(std::map<std::string, int> votes,
                                         std::map<std::string, bool> bar) {
  std::map<std::string, int> result;
  for (auto P : votes) {
    if (bar[P.first]) {
      result[P.first] = P.second;
    }
  }
  return result;
}

#endif // COUNTRY_VOTE_BAR
