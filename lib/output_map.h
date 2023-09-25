#ifndef OUTPUT_MAP
#define OUTPUT_MAP

#include <map>
#include <string>
#include <iostream>

template<typename T>
void DisplayMap(const std::map<std::string, T> &m) {
  for (const auto &key_value : m) {
    std::cout << key_value.first << ": " << key_value.second << std::endl;
  }
}

void DisplayMapOfMaps(
    const std::map<std::string, std::map<std::string, int>> &m) {
  for (const auto &entry : m) {
    std::cout << entry.first << std::endl;
    DisplayMap(entry.second);
    std::cout << std::endl;
  }
}

void VisualDivider() {
  std::cout << "----------------------------------------"
            << "----------------------------------------" << std::endl 
            << std::endl;
}

// Changes a map mapping district ID to integers to the same map, but the
// key is DistrictName (ID)
std::map<std::string, int> ExpandDistrictNamesInMap(
    const std::map<std::string, int> &input,
    const std::map<std::string, std::string> &district_names) {
  std::map<std::string, int> result;
  for (const auto &key_value : input) {
    std::string key = key_value.first;
    result[district_names.at(key) + " (" + key + ")"] = key_value.second;
  }
  return result;
}

// Same operation as above, except the map is committee->district->int
std::map<std::string, std::map<std::string, int>>
ExpandDistrictNamesInMapOfMaps(
    const std::map<std::string, std::map<std::string, int>> &input,
    const std::map<std::string, std::string> &district_names) {
  std::map<std::string, std::map<std::string, int>> result;
  for (const auto &key_map : input) {
    result[key_map.first] =
        ExpandDistrictNamesInMap(key_map.second, district_names);
  }
  return result;
}

#endif  // OUTPUT_MAP
