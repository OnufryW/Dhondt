#ifndef TEST_UTIL
#define TEST_UTIL

#include <string>
#include <vector>
#include <set>
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
void print_set(const std::set<T> &S) {
  std::cout << "[";
  bool first = true;
  for (auto &e : S) {
    if (!first) std::cout << ", ";
    first = false;
    std::cout << e;
  }
  std::cout << "]" << std::endl;
}

template<typename T>
void print_sets_and_fail(const std::set<T> &expected,
                         const std::set<T> &actual) {
  std::cout << "Expected set: ";
  print_set(expected);
  std::cout << "Actual set: ";
  print_set(actual);
  std::cout.flush();
  assert(false);
}

template<typename T>
void assert_set_eq(const std::set<T> &expected, const std::set<T> &actual) {
  if (actual.size() != expected.size()) {
    std::cout << "FAILED: result set size (" << actual.size()
              << ") does not match expected (" << expected.size() << ")!"
              << std::endl;
    print_sets_and_fail(expected, actual);
  }
  for (auto &el : expected) {
    if (actual.find(el) == actual.end()) {
      std::cout << "FAILED: element '" << el << "' is expected, but absent "
                << "in the actual set!" << std::endl;
      print_sets_and_fail(expected, actual);
    }
  }
}

template<typename T, typename K1, typename K2>
void assert_eq_map_of_maps(const std::map<K1, std::map<K2, T>> &expected,
                           const std::map<K1, std::map<K2, T>> &actual) {
  if (actual.size() != expected.size()) {
    std::cout << "FAILED: result map size (" << actual.size()
              << ") does not match expected (" << expected.size() << ")!"
              << std::endl;
    std::set<K1> expected_keys;
    for (const auto &entry : expected) {
      expected_keys.insert(entry.first);
    }
    std::set<K1> actual_keys;
    for (const auto &entry : actual) {
      actual_keys.insert(entry.first);
    }
    std::cout << "Keys of both the maps: " << std::endl;
    print_sets_and_fail(expected_keys, actual_keys);
  }
  for (auto &entry : expected) {
    std::cout << "Checking " << entry.first << std::endl;
    assert_eq_maps(expected.at(entry.first), actual.at(entry.first));
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

const long double EPS = 1e-9;
template<typename T>
void assert_eq_eps(T expected, T actual, const std::string &desc,
                   long double eps=EPS) {
  if (actual < expected - eps || actual > expected + eps) {
    std::cout << "FAILED: Obtained " << desc << " equal to '" << actual
              << "', does not match expected '" << expected << "' within "
              << eps << " precision" << std::endl;
    assert(false);
  }
}

#endif // TEST_UTIL
