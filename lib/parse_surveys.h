#ifndef PARSE_SURVEYS
#define PARSE_SURVEYS

#include <map>
#include <utility>
#include <string>
#include "parse_csv.h"

std::map<std::string, std::pair<std::string, long double>>
    ParseSurvey(const std::string &filename) {
  std::map<std::string, std::pair<std::string, long double>> result;
  auto parsed = ParseFile(filename);
  for (auto line : parsed) {
    result[line[0]] = make_pair(line[1], (long double) atof(line[2].c_str()));
  }
  return result;
}

#endif // PARSE_SURVEYS
