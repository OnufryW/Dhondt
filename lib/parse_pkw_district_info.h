#ifndef PARSE_PKW_DISTRICT_INFO
#define PARSE_PKW_DISTRICT_INFO

#include "parse_election_results.h"
#include "parse_district_info.h"
#include "parse_csv.h"

std::map<std::string, int> VotesPerMandate(
    const std::string &district_info_filename,
    const std::string &election_results_filename,
    const std::string &pkw_data_filename) {
  ElectionResults *er = FromFile2019(election_results_filename);
  auto DI = DistrictInfoFromFile2019(district_info_filename);
  auto PKW = ParseFile(pkw_data_filename);
  std::map<std::string, int> result;
  // Number of votes actually cast in the old election, per district.
  std::map<std::string, int> total_votes_by_district;
  for (auto p : er->VoteCountsByParty()) {
    for (auto d : p.second) {
      total_votes_by_district[d.first] += d.second;
    }
  }
  for (auto line : PKW) {
    if (line[0] == PKW[0][0]) continue;  // Skip header line.
    // We calculate VotesCast * (Population Now / Population Then)
    //                        / Mandates in district
    // As the expected number of votes cast now.
    // Integer division, rounding down, it shouldn't matter. The result
    // of the multiplication might be high, so using long longs.
    std::string district = line[0];
    int votes_per_mandate =
        (long long) total_votes_by_district[district] * 
        (long long) atoi(line[1].c_str())
            / (long long) DI[district].citizens
            / (long long) DI[district].seats;
    result[district] = votes_per_mandate;
  }
  return result;
}

#endif // PARSE_PKW_DISTRICT_INFO
