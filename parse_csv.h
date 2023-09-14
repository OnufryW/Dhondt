#ifndef PARSE_CSV
#define PARSE_CSV

#include <fstream>
#include <string>
#include <vector>

const char *whitespace = " \t\n\r\f\v";
std::string VectorCharToString(const std::vector<char> &V) {
  std::string s;
  s.resize(V.size(), '_');
  for (int i = 0; i < (int) V.size(); ++i) s[i] = V[i];
  s.erase(s.find_last_not_of(whitespace) + 1);
  return s;
}

std::vector<std::string> ParseLine(const std::string &line) {
  std::vector<std::string> res;
  std::vector<char> curr;
  for (int i = 0; i < (int) line.size(); ++i) {
    if (line[i] == ';') {
      res.push_back(VectorCharToString(curr));
      curr.clear();
    } else if (line[i] == '"') {
      continue;
    } else {
      curr.push_back(line[i]);
    }
  }
  res.push_back(VectorCharToString(curr));
  return res;
}

std::vector<std::vector<std::string>> ParseFile(
    const std::string &filename) {
  std::fstream fs;
  fs.open(filename, std::ios::in);
  std::string line;
  std::vector<std::vector<std::string>> res;
  while (std::getline(fs, line)) {
    res.push_back(ParseLine(line));
  }
  fs.close();
  return res;
}

#endif  // PARSE_CSV
