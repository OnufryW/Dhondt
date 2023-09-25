#ifndef PARSE_SURVEYS
#define PARSE_SURVEYS

#include <map>
#include <utility>
#include <string>
#include "parse_csv.h"

std::map<std::string, int> ParseSurvey(const std::string &filename) {
  std::map<std::string, int> result;
  auto parsed = ParseFile(filename);
  for (auto line : parsed) {
    int value = (int) (1000 * atof(line[1].c_str()));
    result[line[0]] = value;
  }
  return result;
}

#endif // PARSE_SURVEYS
