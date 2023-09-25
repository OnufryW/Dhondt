#ifndef CALCULATE_VOTE_TRANSFERRAL
#define CALCULATE_VOTE_TRANSFERRAL

#include <cassert>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
#include "expression.h"
#include "trim.h"

// Takes a bunch of maps with old results, and uses a vote transferral
// policy config to produce expected new results.
// Assume the set of districts is the same in all the maps.


// Merge the vector of maps (representing results from various years) into
// one map (keyed by the committee name, which we assume to be unique
// across years).
std::map<std::string, std::map<std::string, int>> MergeMaps(
  const std::vector<std::map<std::string, std::map<std::string, int>>> &votes) {
  std::map<std::string, std::map<std::string, int>> result;
  for (const auto &mp: votes) {
    for (const auto &committee : mp) {
      assert(result.find(committee.first) == result.end());
      result[committee.first] = committee.second;
    }
  }
  return result;
}

// Collect the set of districts in the input.
std::set<std::string> CollectDistrictsFromMaps(
    const std::map<std::string, std::map<std::string, int>> &votes) {
  std::set<std::string> result;
  bool first = true;
  for (auto &committee : votes) {
    for (auto &district : committee.second) {
      if (first) {
        result.insert(district.first);
      } else {
        assert(result.find(district.first) != result.end());
      }
    }
    first = false;    
  }
  return result;
}

// Find a committee named referred to by a variable name. We assume the
// variable name should be a prefix or suffix of the actual committe name,
// and (of course) it should be unique.
std::string ResolveVariable(
    const std::string &variable, 
    const std::map<std::string, std::map<std::string, int>> &votes) {
  bool found = false;
  std::string result;
  for (auto &committee : votes) {
    const std::string &key = committee.first;
    // Check if name is prefix or suffix of key
    if (key.length() >= variable.length() && (
          key.find(variable) == 0 || 
          key.compare(key.length() - variable.length(),
                      std::string::npos, variable) == 0)) {
      if (found) {
        std::cerr << "Two options to resolve '" << variable << "': '"
                  << key << "' and '" << result << "'" << std::endl;
        assert(false);
      }
      result = key;
      found = true;
    }
  }
  assert(found);
  return result;
}

// The result is a standard "map of party to map of district to votes"
// The arguments is an arbitrary set of "map of party/candidate to map
// of district to votes", and a config filename.
std::map<std::string, std::map<std::string, int>> CalculateVoteTransferral(
    const std::vector<std::map<std::string, std::map<std::string, int>>> &votes,
    const std::string &transferral_policy_filename) {
  std::map<std::string, std::map<std::string, int>> merged =
      MergeMaps(votes);
  std::map<std::string, std::map<std::string, int>> results;
  std::set<std::string> districts = CollectDistrictsFromMaps(merged);
  std::fstream fs;
  fs.open(transferral_policy_filename, std::ios::in);
  std::string line;
  while (std::getline(fs, line)) {
    if (line.size() == 0 || line[0] == '\n' || line[0] == '#') {
      continue;
    }
    // The line should be in the form of Party Name = Expression
    auto equals_pos = line.find("=");
    assert(equals_pos != std::string::npos);
    std::string party_name = line.substr(0, equals_pos);
    Trim(party_name);
    std::string expr = line.substr(equals_pos + 1);
    Trim(expr);
    Expression *calculation = ExpressionFromString(expr);

    std::set<std::string> variable_names;
    std::map<std::string, std::string> variable_resolution;
    calculation->CollectVariableNames(variable_names);
    for (const std::string &name : variable_names) {
      variable_resolution[name] = ResolveVariable(name, merged);
    }
    results[party_name] = {};
    for (const std::string &district : districts) {
      for (const std::string &variable : variable_names) {
        calculation->SetVariable(
            variable, merged[variable_resolution[variable]][district]);
      }
      results[party_name][district] = (int) calculation->Calculate();
    }
  }
  return results;
}

#endif // CALCULATE_VOTE_TRANSFERRAL
