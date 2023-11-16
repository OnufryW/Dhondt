#ifndef RESOLVE_STRATEGY
#define RESOLVE_STRATEGY

#include <cassert>
#include <string>
#include <vector>
#include <set>
#include <map>
#include "parse_csv.h"
#include "strategy.h"

class StrategyOverride {
 public:
  virtual std::vector<MoveComponent> MC(
      const std::string &home_district,
      const std::string &home_committee) = 0;
};

class OverrideDistrict : public StrategyOverride {
 public:
  OverrideDistrict(const std::string &district) : district(district) {}
  std::vector<MoveComponent> MC(
      const std::string &home_district, const std::string &home_committee) {
    return { { district, home_committee, 1.0 } };
  }

 private:
  std::string district;
};

class OverrideCommittee : public StrategyOverride {
 public:
  OverrideCommittee(const std::string &committee) : committee(committee) {}
  std::vector<MoveComponent> MC(
      const std::string &home_district, const std::string &home_committee) {
    return { { home_district, committee, 1.0 } };
  }

 private:
  std::string committee;
};

class OverrideFull : public StrategyOverride {
 public:
  OverrideFull(const std::vector<MoveComponent> &res) : res(res) {}
  std::vector<MoveComponent> MC(
      const std::string &home_district, const std::string &home_committee) {
    std::vector<MoveComponent> result;
    for (const auto &mc : res) {
      MoveComponent new_mc = mc;
      if (new_mc.target_committee == "*") {
        new_mc.target_committee = home_committee;
      }
      if (new_mc.target_district_id == "*") {
        new_mc.target_district_id = home_district;
      }
      result.push_back(new_mc);
    }
    return result;
  }

 private:
  std::vector<MoveComponent> res;
};

class StrategyWithOverrides : public Strategy {
 public:
  StrategyWithOverrides(
      const std::map<std::string, std::map<std::string, StrategyOverride*>>
          &overrides) : overrides(overrides) {}

  bool IsSource(
      const std::string &district_id, const std::string &committee) {
    std::map<std::string, StrategyOverride *> *comm;
    if (overrides.find(district_id) != overrides.end()) {
      comm = &overrides[district_id];
    } else if (overrides.find("*") != overrides.end()) {
      comm = &overrides["*"];
    } else {
      return false;
    }
    return (comm->find(committee) != comm->end() ||
            comm->find("*") != comm->end());
  };

  std::vector<MoveComponent> GetStrategy(
      const std::string &district_id, const std::string &committee) {
    std::map<std::string, StrategyOverride*> *comm;
    if (overrides.find(district_id) != overrides.end()) {
      comm = &overrides[district_id];
    } else if (overrides.find("*") != overrides.end()) {
      comm = &overrides["*"];
    } else {
      return {};
    }
    if (comm->find(committee) != comm->end()) {
      return comm->find(committee)->second->MC(district_id, committee);
    }
    if (comm->find("*") != comm->end()) {
      return comm->find("*")->second->MC(district_id, committee);
    }
    return {};
  }

 private:
  std::map<std::string, std::map<std::string, StrategyOverride*>> overrides;
};

Strategy *PartyDistrictToDistrictListStrategy(const std::string &filename) {
  auto lines = ParseFile(filename);
  std::map<std::string, std::map<std::string, StrategyOverride *>> overs;
  for (auto line : lines) {
    const std::string &party = line[0];
    const std::string &source_district = line[1];
    std::vector<MoveComponent> targets;
    double prob = 1. / (line.size() - 2);
    for (size_t i = 2; i < line.size(); ++i) {
      MoveComponent mc;
      mc.target_district_id = line[i];
      mc.target_committee = line[0];
      mc.probability = prob;
      targets.push_back(mc);
    }
    overs[source_district][party] = new OverrideFull(targets);
  }
  return new StrategyWithOverrides(overs);
}

Strategy *PartyDistrictToWeightedDistrictListStrategy(
    const std::string &filename) {
  auto lines = ParseFile(filename);
  std::map<std::string, std::map<std::string, StrategyOverride *>> overs;
  for (auto line : lines) {
    const std::string &party = line[0];
    const std::string &source_district = line[1];
    std::vector<MoveComponent> targets;
    double sum_prob = 0;
    for (size_t i = 2; i < line.size(); i += 2) {
      sum_prob += std::atof(line[i+1].c_str()) - 1;
    }
    for (size_t i = 2; i < line.size(); i += 2) {
      MoveComponent mc;
      mc.target_district_id = line[i];
      mc.target_committee = line[0];
      mc.probability = (std::atof(line[i+1].c_str()) - 1.001) / sum_prob;
      targets.push_back(mc);
    }
    overs[source_district][party] = new OverrideFull(targets);
  }
  return new StrategyWithOverrides(overs);
}

Strategy *PartyChangeStrategy(const std::string &filename) {
  auto lines = ParseFile(filename);
  std::map<std::string, std::map<std::string, StrategyOverride *>> overs;
  std::vector<std::string> all_strategy_parties = {
      "Koalicja Obywatelska", "Lewica", "Trzecia Droga" };
  for (auto line : lines) {
    const std::string &district = line[0];
    std::vector<MoveComponent> targets;
    std::vector<std::string> source_parties;
    for (const auto &party : all_strategy_parties) {
      bool source = true;
      for (size_t i = 1; i < line.size(); ++i) {
        if (line[i] == party) source = false;
      }
      if (source) source_parties.push_back(party);
    }
    for (const auto &source_party : source_parties) {
      std::vector<MoveComponent> targets;
      for (size_t i = 1; i < line.size(); ++i) {
        MoveComponent mc;
        mc.target_district_id = district;
        mc.target_committee = line[i];
        mc.probability = 0.5 / (line.size() - 1);
        targets.push_back(mc);
      }
      overs[district][source_party] = new OverrideFull(targets);
    }
  }
  return new StrategyWithOverrides(overs);
}

std::vector<std::string> Neighbors(const std::string &district) {
  int distnum = std::atoi(district.c_str());
  switch (distnum) {
    case 1: return {"8", "3", "2"};
    case 2: return {"1", "3", "21"};
    case 3: return {"1", "2", "21", "36", "8"};
    case 4: return {"5", "37", "38", "26", "25"};
    case 5: return {"4", "25", "34", "16", "11", "37"};
    case 6: return {"7", "23", "33", "17", "18"};
    case 7: return {"22", "23", "6", "18", "24"};
    case 8: return {"1", "3", "36", "38", "40", "41"};
    case 9: return {"10", "11"};
    case 10: return {"28", "33", "17", "16", "11", "9"};
    case 11: return {"21", "28", "10", "9", "16", "5", "37", "36"};
    case 12: return {"14", "15", "13", "32", "31", "30"};
    case 13: return {"12", "15", "33", "32"};
    case 14: return {"12", "15", "22"};
    case 15: return {"14", "12", "13", "33", "23", "22"};
    case 16: return {"34", "34", "18", "20", "17", "10", "11", "5", "19"};
    case 17: return {"33", "10", "16", "20", "18", "6", "19"};
    case 18: return {"19", "20", "16", "35", "24", "7", "6", "17"};
    case 19: return {"20", "16", "18", "18"};
    case 20: return {"19", "16", "18", "17"};
    case 21: return {"2", "3", "36", "11", "28", "29", "30"};
    case 22: return {"14", "15", "23", "7"};
    case 23: return {"22", "15", "33", "6", "7"};
    case 24: return {"35", "18", "7"};
    case 25: return {"34", "5", "4", "26"};
    case 26: return {"25", "4", "38", "40"};
    case 27: return {"30", "31", "12"};
    case 28: return {"11", "10", "33", "32", "29", "21"};
    case 29: return {"21", "28", "32", "31", "30"};
    case 30: return {"21", "29", "31", "27"};
    case 31: return {"29", "32", "12", "27", "30"};
    case 32: return {"12", "13", "33", "28", "29", "31"};
    case 33: return {"10", "17", "6", "23", "15", "13", "32", "28"};
    case 34: return {"25", "5", "16", "35"};
    case 35: return {"34", "16", "18", "24"};
    case 36: return {"3", "8", "38", "39", "37", "11", "21"};
    case 37: return {"36", "39", "38", "4", "5", "11"};
    case 38: return {"40", "26", "4", "37", "39", "36", "8"};
    case 39: return {"36", "37", "38"};
    case 40: return {"41", "8", "38", "26"};
    case 41: return {"40", "8"};
    default: assert(false);
  }
}

std::vector<std::string> FarNeighbors(const std::string &district) {
  std::set<std::string> far_neighbors;
  for (const std::string &nei : Neighbors(district)) {
    for (const std::string &far_nei : Neighbors(nei)) {
      far_neighbors.insert(far_nei);
    }
  }
  return {far_neighbors.begin(), far_neighbors.end()};
}

StrategyOverride *ColorsBasedOverride(
    const std::string &district,
    const std::map<std::string, int> &colors) {
  int my_color = colors.at(district);
  int best_close_neighbor = my_color;
  int best_far_neighbor = my_color;
  for (const auto &nei : Neighbors(district)) {
    if (colors.at(nei) > best_close_neighbor) {
      best_close_neighbor = colors.at(nei);
    }
  }
  for (const auto &farnei : FarNeighbors(district)) {
    if (colors.at(farnei) > best_far_neighbor) {
      best_far_neighbor = colors.at(farnei);
    }
  }
  if (best_close_neighbor == my_color &&
      best_far_neighbor <= my_color + 1) {
    // Can't make enough progress to travel from this district.
    return nullptr;
  }
  std::vector<std::string> close_moves;
  std::vector<std::string> far_moves;
  if (best_close_neighbor != my_color) {
    for (const auto &nei : Neighbors(district)) {
      if (colors.at(nei) == best_close_neighbor) {
        close_moves.push_back(nei);
      }
    }
  }
  if (best_far_neighbor > my_color + 1 &&
      best_far_neighbor > best_close_neighbor) {
    for (const auto &nei : FarNeighbors(district)) {
      if (colors.at(nei) == best_far_neighbor) {
        far_moves.push_back(nei);
      }
    }
  }
  double close_weight = far_moves.empty() ? 1 : 0.75;
  double far_weight = close_moves.empty() ? 1 : 0.25;
  std::vector<MoveComponent> targets;
  for (const std::string &nei : close_moves) {
    MoveComponent mc;
    mc.target_district_id = nei;
    mc.target_committee = "*";
    mc.probability = close_weight / close_moves.size();
    targets.push_back(mc);
  }
  for (const std::string &nei : far_moves) {
    MoveComponent mc;
    mc.target_district_id = nei;
    mc.target_committee = "*";
    mc.probability = far_weight / far_moves.size();
    targets.push_back(mc);
  }
  return new OverrideFull(targets);
}

Strategy *DistrictWeightsStrategy(const std::string &filename) {
  auto lines = ParseFile(filename);
  std::map<std::string, int> colors;
  for (auto &line : lines) {
    const std::string &district = line[0];
    colors[district] = std::atoi(line[1].c_str());
  }
  std::map<std::string, std::map<std::string, StrategyOverride *>> overs;
  for (const auto &district_data : colors) {
    const auto &district = district_data.first;
    auto over = ColorsBasedOverride(district, colors);
    if (over != nullptr) {
      overs[district]["*"] = over;
    }
  }
  return new StrategyWithOverrides(overs);
}

Strategy *PartyDistrictWeightsStrategy(const std::string &filename) {
  auto lines = ParseFile(filename);
  std::map<std::string, std::map<std::string, int>> colors_by_party;
  for (auto &line : lines) {
    const std::string &committee = line[0];
    const std::string &district = line[1];
    colors_by_party[committee][district] = std::atoi(line[2].c_str());
  }
  std::map<std::string, std::map<std::string, StrategyOverride *>> overs;
  for (const auto &party_data : colors_by_party) {
    for (const auto &district_data : party_data.second) {
      const auto &district = district_data.first;
      auto over = ColorsBasedOverride(district, party_data.second);
      if (over != nullptr) {
        overs[district][party_data.first] = over;
      }
    }
  }
  return new StrategyWithOverrides(overs);
}

std::string DIR_PREFIX;

Strategy *ResolveStrategy(const std::string &strategy_config) {
  if (strategy_config == "go_to_olsztyn") {
    // Naive test strategy, everybody goes to district 35 (Olsztyn)
    return new StrategyWithOverrides(
        {{"*", {{"*", new OverrideDistrict("35")}}}});
  } else if (strategy_config == "majewski") {
    return PartyDistrictToDistrictListStrategy(
        DIR_PREFIX + "data_recommendations/majewski.txt");
  } else if (strategy_config == "glosujtam") {
    return PartyDistrictToDistrictListStrategy(
        DIR_PREFIX + "data_recommendations/glosujtam.txt");
  } else if (strategy_config == "wazymyglosy") {
    return PartyDistrictToDistrictListStrategy(
        DIR_PREFIX + "data_recommendations/wazymyglosy.txt");
  } else if (strategy_config == "podrozewyborcze") {
    return PartyDistrictToWeightedDistrictListStrategy(
        DIR_PREFIX + "data_recommendations/podrozewyborcze.txt");
  } else if (strategy_config == "fb_weights") {
    return DistrictWeightsStrategy(
        DIR_PREFIX + "data_recommendations/fb_weights.txt");
  } else if (strategy_config == "pers") {
    return DistrictWeightsStrategy(
        DIR_PREFIX + "data_recommendations/pers.txt");
  } else if (strategy_config == "fb_party") {
    return PartyDistrictWeightsStrategy(
        DIR_PREFIX + "data_recommendations/fb_party.txt");
  }
  assert(false);
}

#endif // RESOLVE_STRATEGY
