#include <cassert>
#include <iostream>
#include <string>
#include <map>
#include <vector>
#include "../lib/assign_seats_to_districts.h"
#include "test_util.h"

using std::cout;

void test_assign_seats(const std::map<std::string, int> &in,
                       int total_seats,
                       const std::map<std::string, int> &expected,
                       const std::string &description) {
  cout << "[ RUNNING ] " << description << std::endl;
  auto res = AssignSeatsToDistricts(in, total_seats);
  assert_eq_si_maps(expected, res);
  cout << "[ OK ]" << std::endl;
}

int main() {
  test_assign_seats({{"A", 20}, {"B", 10}}, 3, {{"A", 2}, {"B", 1}},
                    "Equal assignment");
  test_assign_seats({{"A", 15}, {"B", 10}}, 3, {{"A", 2}, {"B", 1}},
                    "Rounding");
  test_assign_seats({{"A", 10}, {"B", 9}, {"C", 7}, {"D", 2}, {"E", 5}},
                    10, {{"A", 3}, {"B", 3}, {"C", 2}, {"D", 1}, {"E", 1}},
                    "Larger case");
  test_assign_seats({{"A", 20}, {"B", 4}}, 2, {{"A", 2}, {"B", 0}},
                    "One takes all");
  test_assign_seats({{"A", 25}, {"B", 15}}, 4, {{"A", 3}, {"B", 1}},
                    "Weight tiebreaker");
  test_assign_seats({{"A", 20}, {"B", 20}}, 1, {{"A", 0}, {"B", 1}},
                    "Name tiebreaker");
}
