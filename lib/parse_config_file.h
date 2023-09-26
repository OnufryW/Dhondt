#ifndef PARSE_CONFIG_FILE
#define PARSE_CONFIG_FILE

#include <fstream>
#include <vector>
#include <string>
#include <map>
#include "trim.h"

std::vector<std::string> ParseConfigFile(const std::string &filename) {
  std::fstream fs;
  fs.open(filename, std::ios::in);
  std::vector<std::string> res;
  std::string line;
  while (std::getline(fs, line)) {
    if (line.size() == 0 || line[0] == '\n' || line[0] == '#') {
      continue;
    }
    res.push_back(line);
  }
  return res;
}

std::map<std::string, std::string> ParseConfigFileToMap(
    const std::string &filename) {
  auto parsed_to_vector = ParseConfigFile(filename);
  std::map<std::string, std::string> res;
  for (const std::string &line : parsed_to_vector) {
    auto equals_pos = line.find("=");
    assert(equals_pos != std::string::npos);
    std::string key = line.substr(0, equals_pos);
    Trim(key);
    std::string value = line.substr(equals_pos + 1);
    Trim(value);
    res[key] = value;
  }
  return res;
}

std::string ParseOneLineConfigFile(const std::string &filename) {
  auto res = ParseConfigFile(filename);
  assert(res.size() == 1);
  return res[0];
}

#endif // PARSE_CONFIG_FILE
