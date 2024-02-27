#ifndef MAP_TOOLS
#define MAP_TOOLS

#include <cassert>
#include <map>
#include <functional>

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

// Pivots the first key to become the deepest subkey in a three-level map.
// Same restrictions as with PivotMap apply.
template<typename K1, typename K2, typename K3, typename T>
std::map<K2, std::map<K3, std::map<K1, T>>>
PivotToThree(const std::map<K1, std::map<K2, std::map<K3, T>>> &source) {
  std::map<K2, std::map<K3, std::map<K1, T>>> result;
  for (const auto &entry : PivotMap(source)) {
    result[entry.first] = PivotMap(entry.second);
  }
  return result;
}

template<typename oldK, typename newK, typename T>
std::map<newK, T> TranslateKeys(const std::map<oldK, T> &M,
                                std::function<newK(oldK)> translate) {
  std::map<newK, T> res;
  for (const auto &entry : M) {
    res[translate(entry.first)] = entry.second;
  }
  return res;
}

template<typename K1, typename K2, typename T1, typename T2>
std::map<K1, std::map<K2, T2>> TransformSubValues(
    const std::map<K1, std::map<K2, T1>> &source,
    std::function<T2(T1)> &translate) {
  std::map<K1, std::map<K2, T2>> result;
  for (const auto &entry : source) {
    for (const auto &subentry : entry.second) {
      result[entry.first][subentry.first] = translate(subentry.second);
    }
  }
  return result;
}

template<typename K, typename T>
T SumMap(const std::map<K, T> &source) {
  T res = 0;
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

// Sums the value in the sub-submap.
template<typename K1, typename K2, typename K3, typename T>
std::map<K1, std::map<K2, T>> SumSubSubmaps(
    const std::map<K1, std::map<K2, std::map<K3, T>>> &source) {
  std::map<K1, std::map<K2, T>> result;
  for (const auto &submap : source) {
    result[submap.first] = SumSubmaps(submap.second);
  }
  return result;
}

// Take two maps x -> a and x -> b, return a map of x -> a / b
template<typename K, typename T> std::map<K, T> DivideMaps(
    const std::map<K, T> &A, const std::map<K, T> &B) {
  std::map<K, T> result;
  for (const auto &entry : A) {
    result[entry.first] = entry.second / B.at(entry.first);
  }
  return result;
}

template<typename K1, typename K2, typename T>
std::map<K1, std::map<K2, T>> DivideByConst(
    const std::map<K1, std::map<K2, T>> &S, T divisor) {
  std::map<K1, std::map<K2, T>> res;
  for (const auto &entry : S) {
    for (const auto &subentry : entry.second) {
      res[entry.first][subentry.first] = subentry.second / divisor;
    }
  }
  return res;
}

template<typename From, typename To>
std::map<std::string, To> CastMap(const std::map<std::string, From> &M) {
  std::map<std::string, To> res;
  for (const auto &entry : M) {
    res[entry.first] = (To) entry.second;
  }
  return res;
}

template<typename From, typename To>
std::map<std::string, std::map<std::string, To>> CastMapOfMaps(
    const std::map<std::string, std::map<std::string, From>> &M) {
  std::map<std::string, std::map<std::string, To>> res;
  for (const auto &entry : M) {
    res[entry.first] = CastMap<From, To>(entry.second);
  }
  return res;
}

#endif // MAP_TOOLS
