#include <iostream>
#include <map>
#include "../lib/vote_strength_by_dhondt_interval.h"
#include "../lib/first_seat_policy.h"
#include "test_util.h"

using std::cout;

void test_str(
    const std::map<std::string, int> &votes, int total_seats,
    const std::map<std::string, int> &expected, const std::string &desc) {
  cout << "[ RUNNING ] " << desc << std::endl;
  // Consider a fake FSP instead?
  auto fsp = FirstSeatPolicyFromFile("test_first_seat_policy.txt");
  auto res = InverseVoteStrengths(votes, total_seats, fsp);
  assert_eq_maps(expected, res);
  cout << "[ OK ]" << std::endl;
}

int main() {
  test_str({{"A", 11}, {"B", 10}}, 2, {{"A", 14}, {"B", 16}}, "Two seats");
  test_str({{"A", 30}, {"B", 14}}, 4, {{"A", 4*14 - 3*7}, {"B", 21-8}},
           "Four seats");
  test_str({{"A", 30}, {"B", 14}, {"C", 8}, {"D", 1}}, 4,
           {{"A", 4*14 - 3*8}, {"B", 21 - 8}, {"C", 11}, {"D", 20}},
           "Four parties, first seat policy on");
}
