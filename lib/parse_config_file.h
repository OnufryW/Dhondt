#ifndef PARSE_CONFIG_FILE
#define PARSE_CONFIG_FILE

#include <fstream>
#include <vector>
#include <string>

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

std::string ParseOneLineConfigFile(const std::string &filename) {
  auto res = ParseConfigFile(filename);
  assert(res.size() == 1);
  return res[0];
}

#endif // PARSE_CONFIG_FILE
