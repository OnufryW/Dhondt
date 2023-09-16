#ifndef TEST_UTIL
#define TEST_UTIL

#include <string>
#include <map>
#include <cassert>
#include <iostream>

// Note: if needed, this can be templatized, I'm not using the actual
// types here (as long as they're comparable and cout-able).
void print_si_map(const std::map<std::string, int> &M) {
	for (auto &value : M) {
    std::cout << value.first << ": " << value.second << std::endl;
	}
}

void print_si_maps_and_fail(const std::map<std::string, int> &expected,
                            const std::map<std::string, int> &actual) {
  std::cout << "Expected map: " << std::endl;
  print_si_map(expected);
  std::cout << std::endl;
  std::cout << "Actually obtained map: " << std::endl;
  print_si_map(actual);
  std::cout.flush();
  assert(false);
}

void assert_eq_si_maps(const std::map<std::string, int> &expected,
                     const std::map<std::string, int> &actual) {
  if (actual.size() != expected.size()) {
    std::cout << "FAILED: result map size (" << actual.size() 
              << ") does not match expected (" << expected.size() << ")!"
              << std::endl;
    print_si_maps_and_fail(expected, actual);
  }
  for (auto V : expected) {
    std::string key = V.first;
    if (actual.find(key) == actual.end()) {
      std::cout << "FAILED: result for " << key << " not found in actually "
                << "obtained map!" << std::endl;
      print_si_maps_and_fail(expected, actual);
    }
    if (actual.find(key)->second != V.second) {
      std::cout << "FAILED: result for " << key << " ("
                << actual.find(key)->second << ") does not match expectation("
                << V.second << ")!" << std::endl;
      print_si_maps_and_fail(expected, actual);
    }
  }
}

template<typename T>
void assert_eq(const T &expected, const T &actual, const std::string &desc) {
  if (expected != actual) {
    std::cout << "FAILED: Obtained " << desc << " equal to '" << actual
              << "', does not match expected '" << expected << "'"
              << std::endl;
    assert(false);
  }
}

#endif // TEST_UTIL
