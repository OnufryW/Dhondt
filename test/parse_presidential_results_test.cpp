#include <cassert>
#include <iostream>
#include <string>
#include "../lib/parse_presidential_results.h"
#include "test_util.h"

using std::cout;

// Note: The only test I want to do is to check whether I'm parsing the
// actual data correctly.

int main() {
  cout << "[ RUNNING ]" << std::endl;
  auto res = Presidential2020FromFile(
      "../data_2020_president/prezydenckie.csv");
  assert_eq(res.size(), (size_t) 6, "Number of candidates");
  assert_eq(
      res["Robert BIEDROŃ"].size(), (size_t) 41, "Number of districts");
  assert_eq(res["Krzysztof BOSAK"]["2"], 17014, "Number of votes");
  cout << "[ OK ]" << std::endl;
}
