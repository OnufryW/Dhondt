#include <iostream>
#include "../lib/first_seat_policy.h"
#include "test_util.h"

using std::cout;

int main() {
  cout << "[ RUNNING ] First seat policy" << std::endl;
  FirstSeatPolicy *policy = FirstSeatPolicyFromFile("test_first_seat_policy.txt");
  assert_eq(10, policy->GetStrength(5, 5), "Equal distance");
  assert_eq(15, policy->GetStrength(10, 5), "Close to new seat");
  assert_eq(14, policy->GetStrength(1, 7), "Far from new seat");
  cout << "[ OK ]" << std::endl;
}
