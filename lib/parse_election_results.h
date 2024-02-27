#ifndef PARSE_ELECTION_RESULTS
#define PARSE_ELECTION_RESULTS

#include <string>
#include <map>
#include "parse_csv.h"
#include "election_results.h"

std::vector<bool> valid_startpoints(const std::vector<std::string> &votes) {
  std::vector<bool> res(votes.size());
  int ctotal = 0;
  for (int i = (int) votes.size() - 1; i >= 0; i--) {
    int val = atoi(votes[i].c_str());
    res[i] = (val == ctotal);
    ctotal += val;
  }
  return res;
}

// The problem we're solving here is that the length of the CSV line is
// somewhat undetermined. However, the last entries are the party vote
// counts, which I'm looking for, and they're preceded by the total vote
// count. So, what we do is we try to find the total_vote_count column,
// by looking at which values happen to be sums of all the values after
// them; the total vote count column will be the column for which this
// holds for all the rows.
int total_counts_index(const std::vector<std::vector<std::string>> &votes) {
  std::vector<bool> is_valid_startpoint(votes[0].size(), true);
  for (int i = 1; i < (int) votes.size(); ++i) {
    std::vector<bool> line_startpoints = valid_startpoints(votes[i]);
    if (line_startpoints.size() != is_valid_startpoint.size()) {
      return -1;
    }
    for (int i = 0; i < (int) line_startpoints.size(); ++i) {
      is_valid_startpoint[i] = is_valid_startpoint[i] && line_startpoints[i];
    }
  }
  for (int i = 0; i < (int) is_valid_startpoint.size(); ++i) {
    if (is_valid_startpoint[i]) return i;
  }
  return -1;
}

ElectionResults *FromFile2019(const std::string &filename) {
  auto parsed_vote_lines = ParseFile(filename);
  int total_index = total_counts_index(parsed_vote_lines);
  if (total_index == -1) return nullptr;
  std::map<std::string, DistrictResults> election_results;
  for (int i = 1; i < (int) parsed_vote_lines.size(); ++i) {
    std::string district_id = parsed_vote_lines[i][0];
    std::string district_name = parsed_vote_lines[i][1];
    // Note: here and elsewhere in this file using atoi instead of
    // std::atoi, because I want to also parse empty strings to zeroes.
    int total_votes = atoi(parsed_vote_lines[i][total_index].c_str());
    int total_voters = atoi(parsed_vote_lines[i][3].c_str());
    std::map<std::string, int> vcbp;
    for (int j = total_index + 1; j < (int) parsed_vote_lines[i].size(); ++j) {
      vcbp[parsed_vote_lines[0][j]] = atoi(parsed_vote_lines[i][j].c_str());
    }
    election_results[district_id] = DistrictResults(vcbp, district_id,
        district_name, total_votes, total_voters);
  }
  return new ElectionResults(election_results);
}

#endif // PARSE_ELECTION_RESULTS
