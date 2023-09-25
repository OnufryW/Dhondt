#ifndef MAP_TOOLS
#define MAP_TOOLS

#include <cassert>
#include <map>

// Pivots a map of maps in the other direction. Asserts that the
// map is actually a full rectangular matrix (or, in other words, that
// the set of keys in every sub-map is the same).
template<typename K1, typename K2, typename T>
std::map<K2, std::map<K1, T>>
PivotMap(const std::map<K1, std::map<K2, T>> &source) {
  std::map<K2, std::map<K1, T>> result;
  // Collect all the keys in a sub-map.
  for (const auto &key_value : source.begin()->second) {
    result[key_value.first] = {};
  }
  for (const auto &submap : source) {
    assert(submap.second.size() == result.size());
    for (const auto &key2_value : submap.second) {
      assert(result.find(key2_value.first) != result.end());
      result[key2_value.first][submap.first] = key2_value.second;
    }
  }
  return result;
}

int SumMap(const std::map<std::string, int> &source) {
  int res = 0;
  for (const auto &key_value : source) {
    res += key_value.second;
  }
  return res;
}

// Sums the values in the submap.
template<typename K1, typename K2, typename T>
std::map<K1, T> SumSubmaps(const std::map<K1, std::map<K2, T>> &source) {
  std::map<K1, T> result;
  for (const auto &submap : source) {
    result[submap.first] = SumMap(submap.second);
  }
  return result;
}

#endif // MAP_TOOLS
