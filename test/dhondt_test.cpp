#include <cassert>
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include "../lib/dhondt.h"
#include "test_util.h"

using std::cout;

void test_dhondt(const std::map<std::string, int> &in, int total_seats,
                 const std::map<std::string, int> &expected,
                 const std::string &test_description) {
  cout << "[ RUNNING ] " << test_description << std::endl;
  auto res = VotesToSeats(in, total_seats);
  assert_eq_si_maps(expected, res);
  cout << "[ OK ]" << std::endl;
}

void test_minimum_votes(const std::map<std::string, int> &in,
                        int total_seats,
                        int desired_seats,
                        int expected,
                        const std::string &test_description) {
  cout << "[ RUNNING ] " << test_description << std::endl;
  int res = MinimumVotesToSeats(in, total_seats, desired_seats);
  assert_eq(expected, res, "minimum votes");
  cout << "[ OK ]" << std::endl;
}

void test_key_vote_values(const std::map<std::string, int> &in,
                          int total_seats,
                          const std::vector<int> &expected,
                          const std::string &test_description) {
  cout << "[ RUNNING ] " << test_description << std::endl;
  auto res = KeyVoteValues(in, total_seats);
  assert_vector_eq(expected, res);
  cout << "[ OK ]" << std::endl;
}

int main() {
  test_dhondt({{"A", 20}, {"B", 4}}, 4, {{"A", 4}, {"B", 0}}, "All votes");
  test_dhondt({{"A", 20}, {"B", 7}}, 4, {{"A", 3}, {"B", 1}}, "3-1");
  test_dhondt({{"A", 20}, {"B", 16}, {"C", 10}}, 3,
              {{"A", 2}, {"B", 1}, {"C", 0}}, "Tiebreaker");
  test_minimum_votes({{"A", 20}, {"B", 4}}, 4, 1, 6, "Grab one");
  test_minimum_votes({{"A", 20}, {"B", 4}}, 4, 3, 30, "Grab most");
  test_minimum_votes({{"A", 5}, {"B", 4}, {"C", 3}},
                     6, 3, 8, "Grab middle");
  test_minimum_votes({{"A", 5}}, 3, 3, 15, "Grab all with one party");
  test_key_vote_values({{"A", 5}}, 3, {2, 5, 15}, "Single opponent");
  test_key_vote_values({{"A", 20}, {"B", 7}}, 4, {7, 14, 30, 80},
                       "Two opponents");
  test_key_vote_values({{"A", 21}, {"B", 21}}, 5, {8, 21, 32, 84, 105},
                       "Two equal opponents");
  test_key_vote_values({{"A", 20}, {"B", 16}, {"C", 10}, {"D", 1}}, 6,
                       {7, 16, 30, 40, 80, 120},
                       "Four opponents, one without seat");
  return 0;
}
