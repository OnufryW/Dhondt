#ifndef PARSE_DISTRICT_INFO
#define PARSE_DISTRICT_INFO

#include <cassert>
#include <cstdlib>
#include <string>
#include <map>
#include "parse_csv.h"
#include "district_info.h"

// Why, why do they do this? I mean, why have different column orders in
// different years? OK, they do have a header row, so I could also retrieve
// this by parsing the header row; but I don't trust them not to change
// the spelling in the header row the next time 'round :(
std::map<std::string, int> DistrictFileColumnIds(int year) {
  if (year == 2019) {
    return {
      {"CODE", 1},
      {"SEATS", 2},
      {"CITIZENS", 5},
      {"VOTERS", 6},
      {"DESCRIPTION", 0}
    };
  }
  if (year == 2023) {
    return {
      {"CODE", 0},
      {"SEATS", 1},
      {"CITIZENS", 4},
      {"VOTERS", 5},
      {"DESCRIPTION", 6}
    };
  }
  assert(false);
};

std::map<std::string, DistrictInfo> DistrictInfoFromFile2019(
    const std::string &filename, int year) {
  auto column_ids = DistrictFileColumnIds(year);
  auto parsed_district_lines = ParseFile(filename);
  std::map<std::string, DistrictInfo> result;
  // Starting from i=1, because the first line is a header line.
  for (int i = 1; i < (int) parsed_district_lines.size(); ++i) {
    auto row = parsed_district_lines[i];
    assert(row.size() >= 7);
    DistrictInfo d(row[column_ids["CODE"]],
                   atoi(row[column_ids["SEATS"]].c_str()),
                   std::atoi(row[column_ids["CITIZENS"]].c_str()),
                   std::atoi(row[column_ids["VOTERS"]].c_str()),
                   row[column_ids["DESCRIPTION"]]);
    assert(result.find(row[column_ids["CODE"]]) == result.end());
    result[row[column_ids["CODE"]]] = d;
  }
  return result;
}

#endif  // PARSE_DISTRICT_INFO
