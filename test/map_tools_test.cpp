#include <iostream>
#include <map>
#include "../lib/map_tools.h"
#include "test_util.h"

void test_pivot(
    const std::map<std::string, std::map<std::string, int>> &source,
    const std::map<std::string, std::map<std::string, int>> &expected,
    const std::string &description) {
  std::cout << "[ RUNNING ] " << "Pivot: " << description << std::endl;
  assert_eq_map_of_maps(expected, PivotMap(source));
  assert_eq_map_of_maps(PivotMap(source), expected);
  std::cout << "[ OK ]" << std::endl;
}

void test_sum_submaps(
    const std::map<std::string, std::map<std::string, int>> &source,
    const std::map<std::string, int> &expected,
    const std::string &description) {
  std::cout << "[ RUNNING ] " << "Sum Submaps" << description << std::endl;
  assert_eq_maps(expected, SumSubmaps(source));
  std::cout << "[ OK ]" << std::endl;
}

int main() {
  test_pivot({{"A", {{"B", 1}}}}, {{"B", {{"A", 1}}}}, "Single entry");
  test_pivot({{"A", {{"B", 1}}}, {"C", {{"B", 2}}}},
             {{"B", {{"A", 1}, {"C", 2}}}}, "Vertical to horizontal");
  test_pivot({{"A", {{"1", 1}, {"2", 2}, {"3", 3}}},
              {"B", {{"1", 2}, {"2", 4}, {"3", 6}}}},
             {{"1", {{"A", 1}, {"B", 2}}},
              {"2", {{"A", 2}, {"B", 4}}},
              {"3", {{"A", 3}, {"B", 6}}}},
             "2 x 3");
  test_sum_submaps({{"A", {{"D1", 2}, {"D2", 4}}},
                    {"B", {{"D1", 10}, {"D2", 2}}}},
                   {{"A", 6}, {"B", 12}},
                   "Simple test");
}
