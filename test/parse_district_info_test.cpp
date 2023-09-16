#include <cassert>
#include <iostream>
#include <string>
#include "../lib/parse_district_info.h"
#include "test_util.h"

using std::cout;

// Note: The only test I want to do is to check whether I'm parsing the
// actual data correctly.

int main() {
  cout << "[ RUNNING ]" << std::endl;
  auto res = DistrictInfoFromFile2019("../data_2019_sejm/okregi_sejm.csv");
  auto wroclaw = res["3"];
  assert_eq(wroclaw.code, std::string("3"), "district ID");
  assert_eq(wroclaw.seats, 14, "seats");
  assert_eq(wroclaw.citizens, 1201333, "citizens");
  assert_eq(wroclaw.voters, 993744, "voters");
  assert_eq(wroclaw.name, std::string("Wrocław"), "district name");
  cout << "[ OK ]" << std::endl;
}
