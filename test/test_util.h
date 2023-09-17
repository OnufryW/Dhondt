#ifndef TEST_UTIL
#define TEST_UTIL

#include <string>
#include <map>
#include <cassert>
#include <iostream>

template<typename T, typename K>
void print_map(const std::map<K, T> &M) {
	for (auto &value : M) {
    std::cout << value.first << ": " << value.second << std::endl;
	}
}

template<typename T, typename K>
void print_maps_and_fail(const std::map<K, T> &expected,
                         const std::map<K, T> &actual) {
  std::cout << "Expected map: " << std::endl;
  print_map(expected);
  std::cout << std::endl;
  std::cout << "Actually obtained map: " << std::endl;
  print_map(actual);
  std::cout.flush();
  assert(false);
}

template<typename T, typename K>
void assert_eq_maps(const std::map<K, T> &expected,
                       const std::map<K, T> &actual) {
  if (actual.size() != expected.size()) {
    std::cout << "FAILED: result map size (" << actual.size() 
              << ") does not match expected (" << expected.size() << ")!"
              << std::endl;
    print_maps_and_fail(expected, actual);
  }
  for (auto V : expected) {
    std::string key = V.first;
    if (actual.find(key) == actual.end()) {
      std::cout << "FAILED: result for " << key << " not found in actually "
                << "obtained map!" << std::endl;
      print_maps_and_fail(expected, actual);
    }
    if (actual.find(key)->second != V.second) {
      std::cout << "FAILED: result for " << key << " ("
                << actual.find(key)->second << ") does not match expectation("
                << V.second << ")!" << std::endl;
      print_maps_and_fail(expected, actual);
    }
  }
}

template<typename T>
void print_vector(const std::vector<T> &V) {
  std::cout << "[";
  bool first = true;
  for (auto &v : V) {
    if (!first) std::cout << ", ";
    first = false;
    std::cout << v;
  }
  std::cout << "]" << std::endl;
}

template<typename T>
void print_vectors_and_fail(const std::vector<T> &expected,
                            const std::vector<T> &actual) {
  std::cout << "Expected vector: ";
  print_vector(expected);
  std::cout << "Actual vector: ";
  print_vector(actual);
  std::cout.flush();
  assert(false);
}

template<typename T>
void assert_vector_eq(const std::vector<T> &expected,
                      const std::vector<T> &actual) {
  if (actual.size() != expected.size()) {
    std::cout << "FAILED: result vector size (" << actual.size() 
              << ") does not match expected (" << expected.size() << ")!"
              << std::endl;
    print_vectors_and_fail(expected, actual);
  }
  for (int i = 0; i < (int) expected.size(); ++i) {
    if (actual[i] != expected[i]) {
      std::cout << "FAILED: at position " << i << ", expected vector is "
                << expected[i] << ", while actual is " << actual[i]
                << std::endl;
      print_vectors_and_fail(expected, actual);
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
