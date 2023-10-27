#ifndef RESOLVE_STRATEGY
#define RESOLVE_STRATEGY

#include <cassert>
#include <string>
#include <vector>
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
    return res;
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
    for (size_t i = 3; i < line.size(); i += 2) {
      sum_prob += std::atof(line[i].c_str()) - 1;
    }
    for (size_t i = 2; i < line.size(); i += 2) {
      MoveComponent mc;
      mc.target_district_id = line[i];
      mc.target_committee = line[0];
      mc.probability = (std::atof(line[i+1].c_str()) - 1) / sum_prob;
      targets.push_back(mc);
    }
    overs[source_district][party] = new OverrideFull(targets);
  }
  return new StrategyWithOverrides(overs);
}

Strategy *ResolveStrategy(const std::string &strategy_config) {
  if (strategy_config == "go_to_olsztyn") {
    // Naive test strategy, everybody goes to district 35 (Olsztyn)
    return new StrategyWithOverrides(
        {{"*", {{"*", new OverrideDistrict("35")}}}});
  } else if (strategy_config == "majewski") {
    return PartyDistrictToDistrictListStrategy(
        "data_recommendations/majewski.txt");
  } else if (strategy_config == "glosujtam") {
    return PartyDistrictToDistrictListStrategy(
        "data_recommendations/glosujtam.txt");
  } else if (strategy_config == "wazymyglosy") {
    return PartyDistrictToDistrictListStrategy(
        "data_recommendations/wazymyglosy.txt");
  } else if (strategy_config == "podrozewyborcze") {
    return PartyDistrictToDistrictListStrategy(
        "data_recommendations/podrozewyborcze.txt");
  }
  assert(false);
}

#endif // RESOLVE_STRATEGY
