#ifndef PARSE_SURVEYS
#define PARSE_SURVEYS

#include <map>
#include <utility>
#include <vector>
#include <string>
#include <cmath>
#include "parse_csv.h"
#include "expression.h"
#include "parse_config_file.h"

Expression *ExtraSurveyStdDevConfig(const std::string &filename) {
  return ExpressionFromString(ParseOneLineConfigFile(filename));
}

std::map<std::string, double> SurveyExpectedValues(
    const std::map<std::string, std::vector<int>> &surveys) {
  std::map<std::string, double> res;
  for (const auto &entry : surveys) {
    double val = 0;
    for (int i : entry.second) {
      val += i;
    }
    res[entry.first] = val / entry.second.size();
  }
  return res;
}

std::map<std::string, double> SurveyStdDevs(
    const std::map<std::string, std::vector<int>> &surveys,
    const std::map<std::string, double> &expected_values,
    Expression *extra_stddev) {
  std::map<std::string, double> res;
  for (const auto &entry : surveys) {
    double val = 0;
    double expected_value = expected_values.at(entry.first);
    for (int i : entry.second) {
      val += (i - expected_value) * (i - expected_value);
    }
    val /= (entry.second.size() - 1);
    extra_stddev->SetVariable("E", expected_value);
    double extra_stddev_val = extra_stddev->Calculate();
    res[entry.first] = std::sqrt(val + extra_stddev_val * extra_stddev_val);
  }
  return res;
}

std::map<std::string, std::vector<int>> ParseSurveys(
    const std::string &filename) {
  std::map<std::string, std::vector<int>> result;
  auto parsed = ParseFile(filename);
  for (auto line : parsed) {
    result[line[0]] = {};
    for (size_t i = 1; i < line.size(); ++i) {
      double val = (int) (1000 * atof(line[1].c_str())); 
      if (val) result[line[0]].push_back(val);
    }
  }
  return result;
}

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
