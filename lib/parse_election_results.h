#ifndef PARSE_ELECTION_RESULTS
#define PARSE_ELECTION_RESULTS

#include <string>
#include <map>
#include "parse_csv.h"
#include "election_results.h"

/* We're only parsing election results provided in the 2023 format (described in
 * data/sejm_election_results/by_district/README.md)
 * So, we define the positions of the key columns below. */
const int district_id_index = 0;
const int total_voters_index = 4;
const int total_votes_index = 25;

ElectionResults *ElectionResultsFromFile(const std::string &filename) {
  auto parsed_vote_lines = ParseFile(filename);
  std::map<std::string, DistrictResults> election_results;
  for (int i = 1; i < (int) parsed_vote_lines.size(); ++i) {
    std::string district_id = parsed_vote_lines[i][district_id_index];
    int total_votes = std::atoi(parsed_vote_lines[i][total_votes_index].c_str());
    int total_voters = atoi(parsed_vote_lines[i][total_voters_index].c_str());
    std::map<std::string, int> vcbp;
    for (int j = total_votes_index + 1;
         j < (int) parsed_vote_lines[i].size();
         ++j) {
      vcbp[parsed_vote_lines[0][j]] = std::atoi(parsed_vote_lines[i][j].c_str());
    }
    election_results[district_id] = DistrictResults(vcbp, district_id,
        total_votes, total_voters);
  }
  return new ElectionResults(election_results);
}

#endif // PARSE_ELECTION_RESULTS
