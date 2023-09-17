#include <iostream>
#include <string>
#include <map>
#include "../lib/election_results.h"
#include "../lib/country_vote_bar.h"
#include "test_util.h"
#include "test_election_results.h"

using std::cout;

void test_bar_value(const std::string &name, int expected) {
  cout << "[ RUNNING ] Test Vote Bar for " << name << std::endl;
  assert_eq(expected, BarValue(name), "bar value");
  cout << "[ OK ]" << std::endl;
}

void test_passes_bar(
    const std::string &desc,
    const std::map<std::string, std::map<std::string, int>> &er,
    const std::map<std::string, bool> &expected) {
  cout << "[ RUNNING ] Test passes bar " << desc << std::endl;
  ElectionResults input = ER(er);
  auto res = PassesBar(&input);
  assert_eq_maps(expected, res);
  cout << "[ OK ]" << std::endl;
}

void test_filter_parties(
    const std::string &desc,
    const std::map<std::string, int> &input,
    const std::map<std::string, bool> &bar,
    const std::map<std::string, int> &expected) {
  cout << "[ RUNNING ] Test filter parties " << desc << std::endl;
  auto res = FilterParties(input, bar);
  assert_eq_maps(expected, res);
  cout << "[ OK ]" << std::endl;
}

int main() {
  test_bar_value("KOALICYJNY KOMITET WYBORCZY KOALICJA OBYWATELSKA PO .N IPL ZIELONI - ZPOW-601-6/19", 8);
  test_bar_value("KOMITET WYBORCZY AKCJA ZAWIEDZIONYCH EMERYTÓW RENCISTÓW - ZPOW-601-21/19", 5);
  test_bar_value("KOMITET WYBORCZY WYBORCÓW MNIEJSZOŚĆ NIEMIECKA - ZPOW-601-15/19", 0);

  // Sums to 100.
  test_passes_bar(
      "One district",
      {{"1", {{"A", 80}, {"B", 16}, {"C", 4}}}},
      {{"A", true}, {"B", true}, {"C", false}});
  // Sums to 100.
  test_passes_bar(
      "Coalition and minority one district",
      {{"1", {{"KOALICYJNY KOMITET 1", 10}, {"KOALICYJNY KOMITET 2", 6},
              {"MNIEJSZOŚĆ NIEMIECKA 1", 10}, {"MNIEJSZOŚĆ NIEMIECKA 2", 6},
              {"MNIEJSZOŚĆ NIEMIECKA 3", 2},
              {"PARTIA 1", 10}, {"PARTIA 2", 6}, {"PARTIA 3", 4},
              {"RESZTA", 46}}}},
      {{"KOALICYJNY KOMITET 1", true}, {"KOALICYJNY KOMITET 2", false},
       {"MNIEJSZOŚĆ NIEMIECKA 1", true}, {"MNIEJSZOŚĆ NIEMIECKA 2", true},
       {"MNIEJSZOŚĆ NIEMIECKA 3", true},
       {"PARTIA 1", true}, {"PARTIA 2", true}, {"PARTIA 3", false},
       {"RESZTA", true}});
  // Sums to 101, to test edge values.
  test_passes_bar(
      "Edge Values One District",
      {{"1", {{"KOALICYJNY KOMITET 1", 9}, {"KOALICYJNY KOMITET 2", 8},
              {"PARTIA 1", 6}, {"PARTIA 2", 5},
              {"MNIEJSZOŚĆ NIEMIECKA", 1}, {"RESZTA", 72}}}},
      {{"KOALICYJNY KOMITET 1", true}, {"KOALICYJNY KOMITET 2", false},
       {"PARTIA 1", true}, {"PARTIA 2", false},
       {"MNIEJSZOŚĆ NIEMIECKA", true}, {"RESZTA", true}});
  // Sums up to 1001, with votes 900 for A, 51 for B, 49 for C.
  test_passes_bar(
      "Three districts three parties",
      {{"1", {{"A", 0}, {"B", 20}, {"C", 20}}},
       {"2", {{"A", 100}, {"B", 5}, {"C", 26}}},
       {"3", {{"A", 800}, {"B", 26}, {"C", 3}}}},
      {{"A", true}, {"B", true}, {"C", false}});

  test_filter_parties("All",
      {{"A", 10}, {"B", 20}, {"C", 30}},
      {{"A", true}, {"B", true}, {"C", true}},
      {{"A", 10}, {"B", 20}, {"C", 30}});
  test_filter_parties("None",
      {{"A", 20}, {"B", 10}}, {{"A", false}, {"B", false}}, {});
  test_filter_parties("Some",
      {{"A", 3}, {"B", 1}, {"C", 4}, {"D", 1}},
      {{"A", true}, {"B", true}, {"C", false}, {"D", false}},
      {{"A", 3}, {"B", 1}});
}

