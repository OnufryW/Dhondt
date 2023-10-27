#include <iostream>
#include <map>
#include <string>
#include "../lib/assign_seats_to_party.h"
#include "test_util.h"

using std::cout;

void test_assign(
    const std::string &desc,
    const std::map<std::string, int> &district_seats,
    const std::map<std::string, std::map<std::string, int>> &input,
    const std::map<std::string, int> &expected) {
  cout << "[ RUNNING ] " << desc << std::endl;
  auto res = AssignSeatsToParty(district_seats, input);
  assert_eq_maps(expected, res);
  cout << "[ OK ]" << std::endl;
}

int main() {
  test_assign("Trivial", {{"1", 1}}, {{"A", {{"1", 1}}}}, {{"A", 1}});
  // The votes sum up to 100.
  // C with 4% and E with 1% don't pass the bar.
  // A gets all the 3 seats in D1 (as C doesn't participate), and 2/5 in D2.
  // B gets 4 seats in D3.
  // D gets 3/5 seats in D2, and the remaining 6 seats in D3.
  test_assign("Real",
      {{"D1", 3}, {"D2", 5}, {"D3", 10}},
      {{"A", {{"D1", 4}, {"D2", 9}, {"D3", 0}}},
       {"B", {{"D1", 1}, {"D2", 1}, {"D3", 30}}},
       {"C", {{"D1", 2}, {"D2", 1}, {"D3", 1}}},
       {"D", {{"D1", 0}, {"D2", 11}, {"D3", 39}}},
       {"E", {{"D1", 0}, {"D2", 0}, {"D3", 1}}}},
      {{"A", 5}, {"B", 4}, {"D", 9}});
}
