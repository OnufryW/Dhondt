#include <iostream>
#include <string>
#include "../lib/first_seat_policy.h"
#include "test_util.h"

using std::cout;

const std::string filename = "../config/first_vote_policy.txt";

int main() {
  cout << "[ RUNNING ] First seat policy config test" << std::endl;
  FirstSeatPolicy *policy = FirstSeatPolicyFromFile(filename);
  assert_eq(1000, policy->GetStrength(999, 1), "Close to new seat");
  assert_eq(10000, policy->GetStrength(7000, 3000), "Borderline");
  assert_eq(18, policy->GetStrength(5, 5), "Halfway");
  assert_eq(180, policy->GetStrength(50, 50), "Scales");
  assert_eq(1080, policy->GetStrength(0, 100), "No votes");
  cout << "[ OK ]" << std::endl;
}
