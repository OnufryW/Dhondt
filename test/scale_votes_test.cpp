#include <iostream>
#include <map>
#include "../lib/scale_votes.h"
#include "test_util.h"

void test_scale_district(
    const std::map<std::string, std::map<std::string, int>> &source,
    const std::map<std::string, double> &scaling_factors,
    const std::map<std::string, std::map<std::string, int>> &expected,
    const std::string &description) {
  std::cout << "[ RUNNING ] " << "Scale distr " << description << std::endl;
  auto res = ScaleVotesByDistrict(source, scaling_factors);
  assert_eq_map_of_maps(expected, res);
  std::cout << "[ OK ]" << std::endl;
}

void test_scale_party(
    const std::map<std::string, std::map<std::string, int>> &source,
    const std::map<std::string, double> &scaling_factors,
    const std::map<std::string, std::map<std::string, int>> &expected,
    const std::string &description) {
  std::cout << "[ RUNNING ] " << "Scale party " << description << std::endl;
  auto res = ScaleByParty(source, scaling_factors);
  assert_eq_map_of_maps(expected, res);
  std::cout << "[ OK ]" << std::endl;
}

void test_calculate_scaling_factors(
    const std::map<std::string, int> &source,
    const std::map<std::string, int> &target,
    const std::map<std::string, double> &expected,
    const std::string &description) {
  std::cout << "[ RUNNING ] Scaling factors " << description << std::endl;
  auto res = CalculateScalingFactors(source, target);
  assert_eq_maps(expected, res);
  std::cout << "[ OK ]" << std::endl;
}


int main() {
  test_scale_district({{"A", {{"D1", 10}, {"D2", 20}}},
                       {"B", {{"D1", 7}, {"D2", 12}}}},
                      {{"D1", 0.5}, {"D2", 1.1}},
                      {{"A", {{"D1", 5}, {"D2", 22}}},
                       {"B", {{"D1", 3}, {"D2", 13}}}},
                      "ScaleByDistrict Basic test");
  test_scale_party({{"A", {{"D1", 10}, {"D2", 20}}},
                    {"B", {{"D1", 7}, {"D2", 12}}}},
                   {{"A", 0.5}, {"B", 0.3}},
                   {{"A", {{"D1", 5}, {"D2", 10}}},
                    {"B", {{"D1", 2}, {"D2", 3}}}},
                   "ScaleByParty Basic test");
  test_calculate_scaling_factors(
      {{"A", 10}, {"B", 20}, {"C", 7}, {"D", 2}},
      {{"A", 5}, {"B", 25}, {"C", 14}, {"D", 2}},
      {{"A", 0.5}, {"B", 1.25}, {"C", 2.}, {"D", 1.}},
      "Basic test");
}
