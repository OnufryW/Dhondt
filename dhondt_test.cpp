#include <cassert>
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include "dhondt.h"

using std::cout;

void print_mandate_map(const std::map<std::string, int> &M) {
  for (auto &E : M) {
    std::cout << E.first << " " << E.second << std::endl;
  }
}

void print_maps_and_fail(const std::map<std::string, int> &expected,
                         const std::map<std::string, int> &res) {
  cout << "Expected map: " << std::endl;
  print_mandate_map(expected);
  cout << std::endl;
  cout << "Actually obtained map: " << std::endl;
  print_mandate_map(res);
  cout.flush();
  assert(false);
}

void test_dhondt(const std::map<std::string, int> &in, int total_mandates,
                 const std::map<std::string, int> &expected,
                 const std::string &test_description) {
  cout << "[ RUNNING ] " << test_description << std::endl;
  auto res = VotesToMandates(in, total_mandates);
  if (res.size() != expected.size()) {
    cout << "FAILED: result map sizes do not match (" << res.size()
         << " vs " << expected.size() << std::endl;
    print_maps_and_fail(expected, res);
  }
  for (auto E : expected) {
    std::string party = E.first;
    if (res.find(party) == res.end()) {
      cout << "FAILED: result for party " << party << " not found in " 
           << "actually obtained map!" << std::endl;
      print_maps_and_fail(expected, res);
    }
    if (res.find(party)->second != E.second) {
      cout << "FAILED: result for party " << party << " ("
           << res.find(party)->second << ") does not match expectation ("
           << E.second << ")" << std::endl;
      print_maps_and_fail(expected, res);
    }
  }
  cout << "[ OK ]" << std::endl;
}

void test_minimum_votes(const std::map<std::string, int> &in,
                        int total_mandates,
                        int desired_mandates,
                        int expected,
                        const std::string &test_description) {
  cout << "[ RUNNING ] " << test_description << std::endl;
  int res = MinimumVotesToSeats(in, total_mandates, desired_mandates);
  if (res != expected) {
    cout << "FAILED: expected " << expected << ", received " << res 
         << std::endl;
    assert(false);
  }
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
  return 0;
}
