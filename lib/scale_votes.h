#ifndef SCALE_VOTES
#define SCALE_VOTES

#include <cassert>
#include "map_tools.h"

// Scales all the votes in a map.
template<typename T>
std::map<std::string, T> ScaleSingleMap(
    const std::map<std::string, T> &source,
    double scaling_factor) {
  std::map<std::string, T> result;
  for (const auto &entry : source) {
    result[entry.first] = entry.second * scaling_factor;
  }
  return result;
}

// Scales all the votes in the map (which is committee -> dist -> T),
// the scaling factors are a map of committee -> scaling factor
template<typename T>
std::map<std::string, std::map<std::string, T>> ScaleByParty(
    const std::map<std::string, std::map<std::string, T>> &source,
    const std::map<std::string, double> &scaling_factors) {
  std::map<std::string, std::map<std::string, T>> result;
  for (const auto &comm : source) {
    result[comm.first] = ScaleSingleMap(
        comm.second, scaling_factors.at(comm.first));
  }
  return result;
}

// Scales all the votes in the map (which is committee -> distr -> int),
// the scaling factors are a map of district -> scaling factor.
std::map<std::string, std::map<std::string, int>> ScaleVotesByDistrict(
    const std::map<std::string, std::map<std::string, int>> &source,
    const std::map<std::string, double> &scaling_factors) {
  // Abusing the notation a bit, we'll pivot the map, treat committees as
  // districts and districts as committees, scale the votes, and pivot
  // back again.
  return PivotMap(ScaleByParty(PivotMap(source), scaling_factors));
}

// Calculates scaling factors, that will bring the first map to be equal
// to the second map.
template<typename T>
std::map<std::string, double> CalculateScalingFactors(
    const std::map<std::string, int> &source,
    const std::map<std::string, T> &target) {
  std::map<std::string, double> result;
  assert(source.size() == target.size());
  for (const auto &source_pair : source) {
    const std::string &key = source_pair.first;
    result[key] = (double) target.at(key) / source_pair.second;
  }
  return result;
}

#endif // SCALE_VOTES
