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

template<typename T>
void DisplayMapOfMaps(
    const std::map<std::string, std::map<std::string, T>> &m) {
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

template<typename T>
void CsvMapOfMaps(const std::map<std::string, std::map<std::string, T>> &m) {
  std::cout << "\"\";";
  for (const auto &committee_data : m) {
    std::cout << "\"" << committee_data.first << "\";";
  }
  std::cout << std::endl;
  for (const auto &district : m.begin()->second) {
    std::cout << "\"" << district.first << "\";";
    for (const auto &committee_data : m) {
      std::cout << committee_data.second.at(district.first) << ";";
    }
    std::cout << std::endl;
  }
}

// Changes a map mapping district ID to integers to the same map, but the
// key is DistrictName (ID)
template<typename T>
std::map<std::string, T> ExpandDistrictNamesInMap(
    const std::map<std::string, T> &input,
    const std::map<std::string, std::string> &district_names) {
  std::map<std::string, T> result;
  for (const auto &key_value : input) {
    std::string key = key_value.first;
    result[district_names.at(key) + " (" + key + ")"] = key_value.second;
  }
  return result;
}

// Same operation as above, except the map is committee->district->int
template<typename T>
std::map<std::string, std::map<std::string, T>>
ExpandDistrictNamesInMapOfMaps(
    const std::map<std::string, std::map<std::string, T>> &input,
    const std::map<std::string, std::string> &district_names) {
  std::map<std::string, std::map<std::string, T>> result;
  for (const auto &key_map : input) {
    result[key_map.first] =
        ExpandDistrictNamesInMap(key_map.second, district_names);
  }
  return result;
}

template<typename T>
void OutputMapOfMaps(
    std::map<std::string, std::map<std::string, T>> map_of_maps,
    const std::string &output_format,
    const std::string &district_names_config,
    const std::map<std::string, std::string> &district_names) {
  if (district_names_config == "expanded") {
    map_of_maps = ExpandDistrictNamesInMapOfMaps(
        map_of_maps, district_names);
  } else {
    assert(district_names_config == "");
  }
  if (output_format == "stdout") {
    DisplayMapOfMaps(map_of_maps);
  } else if (output_format == "csv") {
    CsvMapOfMaps(map_of_maps);
  } else {
    assert(false);
  }
}

template<typename T>
void OutputMap(
    std::map<std::string, T> mp, const std::string &output_format,
    const std::string &district_names_config,
    const std::map<std::string, std::string> &district_names) {
  if (district_names_config == "expanded") {
    mp = ExpandDistrictNamesInMap(mp, district_names);
  } else {
    assert(district_names_config == "");
  }
  if (output_format == "stdout") {
    DisplayMap(mp);
  } else {  // TODO: Add CSV option.
    assert(false);
  }
}

#endif  // OUTPUT_MAP
