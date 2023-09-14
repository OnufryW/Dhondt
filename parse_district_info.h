#ifndef PARSE_DISTRICT_INFO
#define PARSE_DISTRICT_INFO

#include <string>
#include <map>
#include "parse_csv.h"
#include "result_types.h"

std::map<std::string, DistrictInfo> DistrictInfoFromFile2019(
    const std::string &filename) {
  auto parsed_district_lines = ParseFile(filename);
  std::map<std::string, DistrictInfo> result;
  for (int i = 1; i < (int) parsed_district_lines.size(); ++i) {
    auto row = parsed_district_lines[i];
    DistrictInfo d(row[1], atoi(row[2].c_str()), atoi(row[5].c_str()),
                   atoi(row[6].c_str()), row[0]);
    result[row[1]] = d;
  }
  return result;
}

#endif  // PARSE_DISTRICT_INFO
