#include <cassert>
#include <iostream>
#include <string>
#include "../lib/parse_election_results.h"
#include "test_util.h"

using std::cout;

// Note: The only test I want to do is to check whether I'm parsing the
// actual data correctly.

int main() {
  cout << "[ RUNNING ]" << std::endl;
  auto res = ElectionResultsFromFile(
      "../data/sejm_election_results/by_district/2019.csv");
  assert_eq((size_t) 41, res->ByDistrict().size(), "Number of districts");
  auto wroclaw = res->ByDistrict()["3"];
  assert_eq(std::string("3"), wroclaw.DistrictId(), "district ID");
  assert_eq(1001757, wroclaw.TotalVoters(), "citizens");
  assert_eq(654455, wroclaw.TotalVotes(), "voters");
  assert_eq(42269, wroclaw.VoteCountByParty().at(
      "KOMITET WYBORCZY POLSKIE STRONNICTWO LUDOWE - ZPOW-601-19/19"),
    "PSL votes");
  assert_eq(48775, wroclaw.VoteCountByParty().at(
      "KOMITET WYBORCZY KONFEDERACJA WOLNOŚĆ I NIEPODLEGŁOŚĆ - ZPOW-601-5/19"),
    "Konfederacja votes");
  auto psl = res->VoteCountsByParty().at(
      "KOMITET WYBORCZY POLSKIE STRONNICTWO LUDOWE - ZPOW-601-19/19");
  assert_eq(42269, psl["3"], "By Party PSL in Wroclaw");
  assert_eq(65683, psl["19"], "By Party PSL in Warsaw");
  cout << "[ OK ]" << std::endl;
}
