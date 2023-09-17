#include <iostream>
#include <map>
#include <string>
#include "../lib/assign_seats_to_party.h"
#include "test_util.h"
#include "test_election_results.h"

using std::cout;

void test_assign(
    const std::string &desc,
    const std::map<std::string, int> &district_seats,
    const std::map<std::string, std::map<std::string, int>> &er,
    const std::map<std::string, int> &expected) {
  cout << "[ RUNNING ] " << desc << std::endl;
  auto input = ER(er);
  auto res = AssignSeatsToParty(district_seats, &input);
  assert_eq_maps(expected, res);
  cout << "[ OK ]" << std::endl;
}

int main() {
  test_assign("Trivial", {{"1", 1}}, {{"1", {{"A", 1}}}}, {{"A", 1}});
  // The votes sum up to 100.
  // C with 4% and E with 1% don't pass the bar.
  // A gets all the 3 seats in D1 (as C doesn't participate), and 2/5 in D2.
  // B gets 4 seats in D3.
  // D gets 3/5 seats in D2, and the remaining 6 seats in D3.
  test_assign("Real",
      {{"D1", 3}, {"D2", 5}, {"D3", 10}},
      {{"D1", {{"A", 4}, {"B", 1}, {"C", 2}}},
       {"D2", {{"D", 11}, {"A", 9}, {"C", 1}, {"B", 1}}},
       {"D3", {{"E", 1}, {"A", 0}, {"C", 1}, {"B", 30}, {"D", 39}}}},
      {{"A", 5}, {"B", 4}, {"D", 9}});
}
