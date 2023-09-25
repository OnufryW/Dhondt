#ifndef PARSE_DISTRICT_INFO
#define PARSE_DISTRICT_INFO

#include <cassert>
#include <cstdlib>
#include <string>
#include <map>
#include "parse_csv.h"
#include "district_info.h"

std::map<std::string, DistrictInfo> DistrictInfoFromFile2019(
    const std::string &filename) {
  auto parsed_district_lines = ParseFile(filename);
  std::map<std::string, DistrictInfo> result;
  // Starting from i=1, because the first line is a header line.
  for (int i = 1; i < (int) parsed_district_lines.size(); ++i) {
    auto row = parsed_district_lines[i];
    assert(row.size() >= 7);
    DistrictInfo d(row[1], atoi(row[2].c_str()), std::atoi(row[5].c_str()),
                   std::atoi(row[6].c_str()), row[0]);
    assert(result.find(row[1]) == result.end());
    result[row[1]] = d;
  }
  return result;
}

#endif  // PARSE_DISTRICT_INFO
