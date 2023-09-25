#ifndef PARSE_PRESIDENTIAL_RESULTS
#define PARSE_PRESIDENTIAL_RESULTS

#include <cassert>
#include <string>
#include <map>
#include "parse_csv.h"

// Parse the CSV with the results of the presidential election into
// a map from candidate to a map from district to votes.
std::map<std::string, std::map<std::string, int>> Presidential2020FromFile(
    const std::string &filename) {
  auto parsed_vote_lines = ParseFile(filename);
  std::map<std::string, std::map<std::string, int>> results;
  for (size_t j = 1; j < parsed_vote_lines[0].size(); ++j) {
    results[parsed_vote_lines[0][j]] = {};
  }
  for (size_t i = 1; i < parsed_vote_lines.size(); ++i) {
    assert(parsed_vote_lines[i].size() == parsed_vote_lines[0].size());
    std::string district_id = parsed_vote_lines[i][0];
    for (size_t j = 1; j < parsed_vote_lines[i].size(); ++j) {
      results[parsed_vote_lines[0][j]][parsed_vote_lines[i][0]] =
          atoi(parsed_vote_lines[i][j].c_str());
    }
  }
  return results;
}

#endif // PARSE_PRESIDENTIAL_RESULTS
