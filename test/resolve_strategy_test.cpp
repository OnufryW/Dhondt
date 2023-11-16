#include <iostream>
#include "../lib/resolve_strategy.h"
#include "test_util.h"

using std::cout;

// Strategy.IsSource(district, committee)
// Strategy.GetStrategy(district, committee) = vector<MoveComponent>

void test_void_strategy(
    const std::string &strategy_name, const std::string &district,
    const std::string &party, const std::string &description) {
  cout << "[ RUNNING ] Strategy test " << description << std::endl;
  Strategy *strategy = ResolveStrategy(strategy_name);
  assert_eq(false, strategy->IsSource(district, party),
            "IsSource(" + district + ", " + party + ")");
  cout << "[ OK ]" << std::endl;
}

void test_move_strategy(
    const std::string &strategy_name, const std::string &district,
    const std::string &party, const std::string &description,
    const std::map<std::string, double> &expected) {
  cout << "[ RUNNING ] Strategy test " << description << std::endl;
  Strategy *strategy = ResolveStrategy(strategy_name);
  assert_eq(true, strategy->IsSource(district, party),
            "IsSource(" + district + ", " + party + ")");
  auto actual = strategy->GetStrategy(district, party);
  std::map<std::string, double> actual_map;
  for (const auto &component : actual) {
    if (actual_map.find(component.target_district_id) ==
        actual_map.end()) {
      actual_map[component.target_district_id] = 0;
    }
    actual_map[component.target_district_id] += component.probability;
    if (component.target_committee != "*" &&
        component.target_committee != party) {
      cout << "[ FAILED ] Expected no party switch, but got a component "
           << "that moves to district " << district << ", party " << party
           << std::endl;
      assert(false);
    }
  }
  assert_eq_eps_maps(expected, actual_map,
                     "GetStrategy(" + district + ", " + party + ")", 0.001);
  cout << "[ OK ]" << std::endl;
}

void test_strategy_consistency(const std::string &strategy_name) {
  cout << "[ RUNNING ] Strategy consistency test for " << strategy_name
       << std::endl;
  std::set<std::string> parties =
      { "Koalicja Obywatelska", "Lewica", "Trzecia Droga" };
  const int num_districts = 41;
  Strategy *strategy = ResolveStrategy(strategy_name);
  for (const auto &party : parties) {
    for (int distr_num = 1; distr_num <= num_districts; distr_num++) {
      std::string district = std::to_string(distr_num);
      if (strategy->IsSource(district, party)) {
        auto res = strategy->GetStrategy(district, party);
        double total_prob = 0;
        for (auto &component : res) {
          int target_distr_num =
              std::atoi(component.target_district_id.c_str());
          if (target_distr_num < 1 || target_distr_num > num_districts) {
            cout << "[ FAILED ] Invalid district ID "
                 << component.target_district_id << " in strategy for "
                 << party << ", " << district << std::endl;
            assert(false);
          }
          if (parties.find(component.target_committee) == parties.end() &&
              component.target_committee != "*") {
            cout << "[ FAILED ] Invalid target committee "
                 << component.target_committee << " in strategy for "
                 << party << ", " << district << std::endl;
            assert(false);
          }
          if (component.probability < 0) {
            cout << "[ FAILED ] Invalid probability "
                 << component.probability << " in strategy for "
                 << party << ", " << district << std::endl;
            assert(false);
          }
          total_prob += component.probability;
        }
        if (total_prob > 1.0) {
          cout << "[ FAILED ] Total probabilities " << total_prob
               << " exceed 1 in strategy for " << party << ", "
               << district << std::endl;
          assert(false);
        }
      }
    }
  }
  cout << "[ OK ]" << std::endl;
}

int main() {
  DIR_PREFIX = "../";
  std::vector<std::string> strategies = {
    "go_to_olsztyn", "majewski", "glosujtam", "wazymyglosy",
    "podrozewyborcze", "fb_weights", "pers", "fb_party" };
  for (const std::string &strategy : strategies) {
    test_strategy_consistency(strategy);
  }
  test_move_strategy("go_to_olsztyn", "14", "Trzecia Droga",
                     "Go to Olsztyn", { {"35", 1.0 } });
  test_move_strategy("majewski", "40", "Trzecia Droga",
                     "Majewski", { { "38", 1.0 } });
  test_move_strategy("majewski", "37", "Trzecia Droga",
                     "Majewski", { { "11", 1.0 } });
  test_move_strategy("majewski", "20", "Trzecia Droga",
                     "Majewski", { { "16", 0.5 }, { "18", 0.5 } });
  test_move_strategy("majewski", "19", "Koalicja Obywatelska",
                     "Majewski",
                     {{"17", 0.3333}, {"18", 0.3333}, {"20", 0.3333}}); 
  test_move_strategy("majewski", "13", "Koalicja Obywatelska",
                     "Majewski", { { "15", 1.0 } });
  test_move_strategy("majewski", "5", "Koalicja Obywatelska",
                     "Majewski", { { "37", 1.0 } });
  test_move_strategy("majewski", "12", "Lewica", "Majewski", {{"14", 1.0}});
  test_move_strategy("majewski", "15", "Lewica", "Majewski", {{"14", 1.0}});
  test_move_strategy("majewski", "22", "Lewica", "Majewski", {{"23", 1.0}});
  test_move_strategy("majewski", "17", "Lewica", "Majewski",
                     {{ "10", 0.5 }, { "16", 0.5 }});
  test_move_strategy("majewski", "20", "Lewica", "Majewski",
                     {{"16", 0.5}, {"20", 0.5}});
  
  test_move_strategy("glosujtam", "19", "Lewica", "Glosuj Tam",
                     { { "16", 0.3333 },{ "17", 0.3333 },{ "18", 0.3333 }});
  test_move_strategy("glosujtam", "13", "Trzecia Droga", "Glosuj Tam",
                     {{"32", 0.25}, {"12", 0.25},
                      {"15", 0.25}, {"33", 0.25}});
  test_move_strategy("glosujtam", "3", "Koalicja Obywatelska", "Glosuj Tam",
                     {{"1", 0.2}, {"8", 0.2}, {"36", 0.2}, {"21", 0.2},
                      {"2", 0.2}});
  test_move_strategy("glosujtam", "38", "Lewica", "Glosuj Tam",
                     {{"36", 1.0}});
  test_move_strategy("glosujtam", "39", "Koalicja Obywatelska",
                     "Glosuj Tam", { {"36", 1.0 } });
  test_move_strategy("glosujtam", "37", "Trzecia Droga", "Glosuj Tam",
                     {{"36", 1.0}});
  test_move_strategy("glosujtam", "26", "Lewica", "Glosuj Tam",
                     {{"40", 0.25},{"4", 0.25},{"5", 0.25},{"34", 0.25}});
  test_move_strategy("glosujtam", "25", "Trzecia Droga", "Glosuj Tam",
                     {{"40", 0.25},{"4", 0.25},{"5", 0.25},{"34", 0.25}});
  test_void_strategy("glosujtam", "23", "Lewica", "Glosuj Tam");
  test_move_strategy("glosujtam", "23", "Trzecia Droga", "Glosuj Tam",
                     {{"33", 0.25}, {"6", 0.25}, {"7", 0.25},
                      {"22", 0.25}});
  test_move_strategy("wazymyglosy", "26", "Lewica", "Ważymy Głosy",
                     {{"34", 0.3333}, {"5", 0.3333}, {"35", 0.3333}});
  test_move_strategy("wazymyglosy", "25", "Trzecia Droga", "Ważymy Głosy",
                     {{"5", 0.3333}, {"34", 0.333}, {"35", 0.3333}});
  test_move_strategy("wazymyglosy", "4", "Lewica", "Ważymy Głosy",
                     {{"5", 1.0}});
  test_move_strategy("wazymyglosy", "9", "Koalicja Obywatelska", "Waż. Gł.",
                     {{"16",0.25}, {"17",0.25}, {"5",0.25}, {"33",0.25}});
  test_void_strategy("wazymyglosy", "33", "Lewica", "Ważymy Głosy");
  test_move_strategy("wazymyglosy", "23", "Trzecia Droga", "Ważymy Głosy",
                     {{"7", 0.3333}, {"33", 0.3333}, {"22", 0.3333}});
  test_move_strategy("wazymyglosy", "20", "Koalicja Obywatelska", "Waż Gł",
                     {{"16", 0.4}, {"17", 0.2}, {"18", 0.4}});
  test_move_strategy("podrozewyborcze", "19", "Koalicja Obywatelska", "PW",
                     {{"17", 3.3/(3.3+3.1+2.8)},
                      {"18", 3.1/(3.3+3.1+2.8)},
                      {"16", 2.8/(3.3+3.1+2.8)}});
  test_move_strategy("podrozewyborcze", "25", "Lewica", "Podróże Wyborcze",
                     {{"34", 2.3/(2.3+0.8+0.4)},
                      {"5", 0.8/(2.3+0.8+0.4)},
                      {"4", 0.4/(2.3+0.8+0.4)}});
  test_move_strategy("podrozewyborcze", "3", "Trzecia Droga", "Podróże W.",
                     {{"11", 0.7/(0.7+1.4+0.6)},
                      {"2", 1.4/(0.7+1.4+0.6)},
                      {"1", 0.6/(0.7+1.4+0.6)}});
  test_move_strategy("podrozewyborcze", "39", "Koalicja Obywatelska", "PW",
                     {{"37", 1.6/(1.6+1.3+1)},
                      {"36", 1.3/(1.6+1.3+1)},
                      {"4", 1.0/(1.6+1.3+1)}});
  test_move_strategy("podrozewyborcze", "9", "Trzecia Droga", "Podróże W.",
                     {{"10", 0.6/(0.6+0.6+0.3)},
                      {"16", 0.6/(0.6+0.6+0.3)},
                      {"11", 0.3/(0.6+0.6+0.3)}});
  test_move_strategy("podrozewyborcze", "13", "Lewica", "Podróże Wyborcze",
                     {{"33", 0.8/(0.8+0.5+0.3)},
                      {"29", 0.5/(0.8+0.5+0.3)},
                      {"32", 0.3/(0.8+0.5+0.3)}});
  test_void_strategy("podrozewyborcze", "20", "Lewica", "Podróże Wyborcze");
  test_move_strategy("fb_weights", "39", "Lewica", "Mapa z Facebooka",
                     {{"37", 0.25}, {"36", 0.25}, {"38", 0.25},
                      {"5", 0.125}, {"21", 0.125}});
  test_move_strategy("fb_weights", "13", "Koalicja obywatelska", "Mapa FB",
                     {{"12",0.25}, {"32",0.25}, {"33",0.25}, {"15",0.25}});
  test_void_strategy("fb_weights", "14", "Trzecia Droga", "Mapa siły FB");
  test_move_strategy("fb_weights", "20", "Lewica", "Mapa siły FB",
                     {{"16", 0.25}, {"17", 0.25}, {"18", 0.25},
                      {"5", 0.0625}, {"34", 0.0625}, {"35", 0.0625},
                      {"7", 0.0625}});
}
