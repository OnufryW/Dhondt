#include <iostream>
#include <map>
#include <string>
#include "../lib/calculate_vote_transferral.h"
#include "test_util.h"

using std::cout;

void test_transfer(
    const std::string &desc,
    const std::vector<std::map<std::string, std::map<std::string, int>>> &votes,
    const std::map<std::string, std::map<std::string, int>> &expected) {
  cout << "[ RUNNING ] " << desc << std::endl;
  auto res = CalculateVoteTransferral(
      votes, "./test_vote_transfer_config.txt");
  // Contents of the file:
  // P1 = A + B
  // P2 = A
  // P3 = P3 * 0.5
  assert_eq_map_of_maps(expected, res);
  cout << "[ OK ]" << std::endl;
}

int main() {
  test_transfer("Simple, one district, one vector",
                {{{"A", {{"D1", 2}}},
                  {"B", {{"D1", 4}}},
                  {"P3", {{"D1", 0}}}}},
                {{"P1", {{"D1", 6}}},
                 {"P2", {{"D1", 2}}},
                 {"P3", {{"D1", 0}}}});
  test_transfer("Two districts",
                {{{"A", {{"D1", 2}, {"D2", 7}}},
                  {"B", {{"D1", 4}, {"D2", 3}}},
                  {"P3", {{"D1", 2}, {"D2", 4}}}}},
                {{"P1", {{"D1", 6}, {"D2", 10}}},
                 {"P2", {{"D1", 2}, {"D2", 7}}},
                 {"P3", {{"D1", 1}, {"D2", 2}}}});
  test_transfer("Two vector entries",
                {{{"A", {{"D1", 2}}},
                  {"B", {{"D1", 4}}}},
                 {{"P3", {{"D1", 0}}}}},
                {{"P1", {{"D1", 6}}},
                 {"P2", {{"D1", 2}}},
                 {"P3", {{"D1", 0}}}});
  test_transfer("Rounding",
                {{{"A", {{"D1", 1}}},
                  {"B", {{"D1", 1}}},
                  {"P3", {{"D1", 3}}}}},
                {{"P1", {{"D1", 2}}},
                 {"P2", {{"D1", 1}}},
                 {"P3", {{"D1", 1}}}});
  test_transfer("Useless variables",
                {{{"A", {{"D1", 1}}},
                  {"B", {{"D1", 1}}},
                  {"P2", {{"D1", 1000}}},
                  {"Something else", {{"D1", 2000}}},
                  {"P3", {{"D1", 3}}}}},
                {{"P1", {{"D1", 2}}},
                 {"P2", {{"D1", 1}}},
                 {"P3", {{"D1", 1}}}});
  test_transfer("Prefix and suffix",
                {{{"Another party", {{"D1", 3}}},
                  {"Party with suffix P3", {{"D1", 5}}},
                  {"Useless A B P3 party", {{"D1", 1000}}},
                  {"Be a party B", {{"D1", 9}}}}},
                {{"P1", {{"D1", 12}}},
                 {"P2", {{"D1", 3}}},
                 {"P3", {{"D1", 2}}}});
}
