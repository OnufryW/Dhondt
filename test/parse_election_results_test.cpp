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
  auto res = FromFile2019("../data_2019_sejm/wyniki_sejm.csv");
  assert_eq(res->ByDistrict().size(), (size_t) 41, "Number of districts");
  auto wroclaw = res->ByDistrict()["3"];
  assert_eq(wroclaw.DistrictId(), std::string("3"), "district ID");
  assert_eq(wroclaw.TotalVoters(), 1001757, "citizens");
  assert_eq(wroclaw.TotalVotes(), 654455, "voters");
  assert_eq(wroclaw.DistrictName(), std::string("Okręg Wyborczy Nr 3"), "district name");
  assert_eq(wroclaw.VoteCountByParty().at(
      "KOMITET WYBORCZY POLSKIE STRONNICTWO LUDOWE - ZPOW-601-19/19"),
    42269, "PSL votes");
  assert_eq(wroclaw.VoteCountByParty().at(
      "KOMITET WYBORCZY KONFEDERACJA WOLNOŚĆ I NIEPODLEGŁOŚĆ - ZPOW-601-5/19"),
    48775, "Konfederacja votes");
  auto psl = res->VoteCountsByParty().at(
      "KOMITET WYBORCZY POLSKIE STRONNICTWO LUDOWE - ZPOW-601-19/19");
  assert_eq(psl["3"], 42269, "By Party PSL in Wroclaw");
  assert_eq(psl["19"], 65683, "By Party PSL in Warsaw");
  cout << "[ OK ]" << std::endl;
}
