#include <map>
#include <string>
#include <cmath>
#include "map_tools.h"
#include "party_vote_distribution.h"

std::map<std::string, std::map<std::string, double>> StdDevFromConfig(
    const std::map<std::string, std::map<std::string, int>> &votes,
    Expression *vote_distribution_config) {
  std::map<std::string, std::map<std::string, double>> p_res;
  auto by_district = PivotMap(votes);
  for (auto &district_data : by_district) {
    const auto &district = district_data.first;
    p_res[district] = {};
    int total_votes = SumMap(district_data.second);
    for (const auto &committee_data : district_data.second) {
      p_res[district][committee_data.first] =
          GetPartyVoteDistribution(
              committee_data.second, total_votes, vote_distribution_config)
                  ->StdDev();

    }
  }
  return PivotMap(p_res);
}

std::map<std::string, std::map<std::string, double>> HardcodedStddev(
    const std::string &filename) {
  std::map<std::string, std::map<std::string, double>> res;
  auto parsed_lines = ParseFile(filename);
  for (size_t i = 1; i < parsed_lines.size(); ++i) {
    std::string district_id = parsed_lines[i][0];
    for (size_t j = 1; j < parsed_lines[i].size(); ++j) {
      res[parsed_lines[0][j]][district_id] =
          std::atof(parsed_lines[i][j].c_str());
    }
  }
  return res;
}

double hypotenuse(double a, double b) {
  return sqrt(a * a + b * b);
}

std::map<std::string, std::map<std::string, double>> AccumulateStdDev(
		const std::map<std::string, std::map<std::string, double>> &one,
    const std::map<std::string, std::map<std::string, double>> &two) {
	std::map<std::string, std::map<std::string, double>> res;
 	for (const auto &entry : one) {
    res[entry.first] = {};
    for (const auto &sub_entry : entry.second) {
      res[entry.first][sub_entry.first] = hypotenuse(
          sub_entry.second, two.at(entry.first).at(sub_entry.first));
    }
  }
  return res;
}

