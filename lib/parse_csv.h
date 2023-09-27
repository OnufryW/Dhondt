#ifndef PARSE_CSV
#define PARSE_CSV

#include <fstream>
#include <string>
#include <vector>

// Utility function to convert a vector<char> to a string, trimming
// whitespace from the end.
const char *whitespace = " \t\n\r\f\v";
std::string VectorCharToString(const std::vector<char> &V) {
  std::string result;
  result.resize(V.size(), '_');  // _ to make it obvious in case of bugs.
  for (int i = 0; i < (int) V.size(); ++i) result[i] = V[i];
  result.erase(result.find_last_not_of(whitespace) + 1);
  return result;
}

// Parses a line of a CSV (actually, semicolon-separated) into a vector
// of strings, each string being one separated entry.
std::vector<std::string> ParseLine(const std::string &line) {
  std::vector<std::string> result;
  std::vector<char> current;
  for (int i = 0; i < (int) line.size(); ++i) {
    if (line[i] == ';') {
      result.push_back(VectorCharToString(current));
      current.clear();
    } else if (line[i] == '"') {
      continue;
    } else {
      current.push_back(line[i]);
    }
  }
  result.push_back(VectorCharToString(current));
  return result;
}

// Parses a whole semicolon-separated file.
// The filename should be a path (relative or absolute) to a file containing
// a bunch of lines, each containing a bunch of values with semicolon as
// the separator. I also remove all '"' characters from the input.
// The output is a vector of per-line results, each line parsed to a vector
// of strings (the semicolon-separated values).
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
