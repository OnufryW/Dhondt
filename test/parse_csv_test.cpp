#include <cassert>
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include "../lib/parse_csv.h"

using std::cout;

void print_line(const std::vector<std::string> &line) {
  for (const auto &s : line) {
    cout << "\"" << s << "\"  ";
  }
  cout << std::endl;
}

void print_file(const std::vector<std::vector<std::string>> &F) {
  for (const auto &l : F) {
    print_line(l);
  }
}

void test_real_file() {
  std::vector<std::vector<std::string>> expected = {
    {"ABC", "DEF"}, {"GHI", "JK"}, {"LM"}};
  auto R = ParseFile("test_csv.txt");
  if (R.size() != expected.size()) {
    cout << "Unexpected file size" << std::endl;
    print_file(R);
    assert(false);
  }
  for (int i = 0; i < (int) expected.size(); ++i) {
    if (expected[i].size() != R[i].size()) {
      cout << "Different line length on line " << i << ", "
           << expected[i].size() << " vs " << R[i].size() << std::endl;
      cout << "Actual: " << std::endl;
      print_line(R[i]);
      cout << "Expected: " << std::endl;
      print_line(expected[i]);
      assert(false);
    }
    for (int j = 0; j < (int) expected[i].size(); ++j) {
      if (expected[i][j] != R[i][j]) {
        cout << "Values differ on the " << j << "th entry, "
             << R[i][j] << " vs " << expected[i][j] << std::endl;
        cout << "Actual: " << std::endl;
        print_line(R[i]);
        cout << "Expected: " << std::endl;
        print_line(expected[i]);
        assert(false);
      }
    }
  }
  cout << "[ OK ]" << std::endl;
}

int main() {
  test_real_file();
  return 0;
}
