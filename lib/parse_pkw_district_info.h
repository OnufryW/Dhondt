#ifndef PARSE_PKW_DISTRICT_INFO
#define PARSE_PKW_DISTRICT_INFO

#include "parse_csv.h"

std::map<std::string, int> GetPkwPopulationData(const std::string &filename) {
  std::map<std::string, int> res;
  auto PKW = ParseFile(filename);
  for (auto line : PKW) {
    if (line[0] == PKW[0][0]) continue;  // Skip header line.
    res[line[0]] = std::atoi(line[1].c_str());
  }
  return res;
}

#endif // PARSE_PKW_DISTRICT_INFO
