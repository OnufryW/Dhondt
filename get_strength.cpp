#include <vector>
#include <string>
#include <iostream>
#include <random>
#include <cassert>
#include <sstream>
#include <iomanip>

#include "lib/parse_election_results.h"
#include "lib/parse_presidential_results.h"
#include "lib/calculate_vote_transferral.h"
#include "lib/parse_district_info.h"
#include "lib/parse_pkw_district_info.h"
#include "lib/scale_votes.h"
#include "lib/map_tools.h"
#include "lib/parse_surveys.h"
#include "lib/first_seat_policy.h"
#include "lib/vote_strength_by_dhondt_interval.h"
#include "lib/assign_seats_to_party.h"
#include "lib/vote_position.h"
#include "lib/party_vote_distribution.h"
#include "lib/seat_probability.h"
#include "lib/output_map.h"
#include "lib/stddev_calculations.h"
#include "lib/strategy.h"
#include "lib/resolve_strategy.h"
#include "lib/strategy_seat_changes.h"

using std::string;

// Obligatory configs
const string transferral_config = "transferral_config";
const string district_info_filename = "district_info_filename";
const string action = "action";
const string output = "output";

// Optional configs
const string sejm_results_filename = "sejm_results_filename";
const string presidential_results_filename = "presidential_results_filename";
const string pkw_citizens_filename = "pkw_citizens_filename";
const string surveys_filename = "surveys_filename";
const string multi_surveys_filename = "multi_surveys_filename";
const string district_names = "district_names";
const string first_seat_policy_config = "first_seat_policy_config";
const string stddev_config = "stddev_config";
const string repeats = "repeats";
const string rejected_parties = "rejected_parties";
const string vote_number_delta = "vote_number_delta";
const string hardcoded_stddevs = "hardcoded_stddevs";
const string extra_survey_stddev = "extra_survey_stddev";
const string data_year = "data_year";
const string strategy_config = "strategy";
const string strategy_min_voters_config = "strategy_min_voters";
const string strategy_max_voters_config = "strategy_max_voters";
const string strategy_voters_step_config = "strategy_voters_step";
const string strategy_output_config = "strategy_output";


bool ConfigContains(const std::map<std::string, std::string> &config,
                    const std::string &key) {
  return config.find(key) != config.end();
}

void AssertConfigContains(const std::map<std::string, std::string> &config,
                          const std::string &key) {
  assert(ConfigContains(config, key));
}

std::string AssertGetConfigValue(
    const std::map<std::string, std::string> &config,
    const std::string &key) {
  AssertConfigContains(config, key);
  return config.at(key);
}

int AssertGetIntConfigValue(
    const std::map<std::string, std::string> &config,
    const std::string &key) {
  return std::atoi(AssertGetConfigValue(config, key).c_str());
}



int main(int argc, char *argv[]) {
  assert(argc == 2);
  auto main_config = ParseConfigFileToMap(argv[1]);
  AssertConfigContains(main_config, "action");
  /********************* Old results transferred to new **************/
  std::cerr << "Parsing old results" << std::endl;
  std::vector<std::map<string, std::map<string, int>>> old_res;
  // Get Sejm election results, in committee -> district -> votes format.
  if (ConfigContains(main_config, sejm_results_filename)) {
    old_res.push_back(FromFile2019(
        main_config[sejm_results_filename])->VoteCountsByParty());
  }
  // Get 2020 presidential election results, same format.
  if (ConfigContains(main_config, presidential_results_filename)) {
    old_res.push_back(Presidential2020FromFile(
        main_config[presidential_results_filename]));
  }
  std::cerr << "Transferring votes to new committees" << std::endl;
  // Calculate unscaled 2023 results, based on the transferral config.
  // Same format.
  assert(old_res.size() > 0);
  auto votes = CalculateVoteTransferral(
      old_res, AssertGetConfigValue(main_config, transferral_config));

  /*********** Scaling by population changes ****************************/
  int data_year_int = 2019;
  if (ConfigContains(main_config, data_year)) {
    data_year_int = AssertGetIntConfigValue(main_config, data_year);
  }
  auto district_infos = DistrictInfoFromFile2019(
      AssertGetConfigValue(main_config, district_info_filename),
      data_year_int);
  // PKW population data.
  if (ConfigContains(main_config, pkw_citizens_filename)) {
    std::cerr << "Adjusting votes by population data" << std::endl;
    auto pkw_data = GetPkwPopulationData(main_config[pkw_citizens_filename]);
    // Get the scaling factors for population (district name -> double)
    auto population_scaling_factors = CalculateScalingFactors(
        DistrictsToCitizens(district_infos), pkw_data);
    // Scale the vote counts by population changes.
    votes = ScaleVotesByDistrict(votes, population_scaling_factors);
  }

  /************** Prepare the map of stddevs, to accumulate into *******/
  std::map<std::string, std::map<std::string, double>> stddevs;
  for (const auto &entry : votes) {
    stddevs[entry.first] = {};
    for (const auto &sub_entry : entry.second) {
      stddevs[entry.first][sub_entry.first] = 0;
    }
  }

  /************** Scaling to survey results ****************************/
  if (ConfigContains(main_config, surveys_filename)) {
    // Scale by survey results. First, load surveys.
    std::cerr << "Adjusting votes by surveys" << std::endl;
    auto surveys = ParseSurvey(main_config[surveys_filename]);
    // Scale survey results, so that they sum up (roughly) to the number of
    // votes we expect:
    auto scaled_surveys = ScaleSingleMap(
        surveys,
        (double) SumMap(SumSubmaps(votes)) / (double) SumMap(surveys));
    // Scaling factors by party - we want to bring total votes for every
    // party to the survey values.
    auto party_scaling_factors = CalculateScalingFactors(
        SumSubmaps(votes), scaled_surveys);
    // And apply the scaling factors.
    votes = ScaleByParty(votes, party_scaling_factors);
  } else if (ConfigContains(main_config, multi_surveys_filename)) {
    std::cerr << "Collecting multi-survey data" << std::endl;
    auto surveys = ParseSurveys(main_config[multi_surveys_filename]);
    auto expected_values = SurveyExpectedValues(surveys);
    Expression *extra_survey_stddev_expr = ExtraSurveyStdDevConfig(
        AssertGetConfigValue(main_config, extra_survey_stddev));
    auto survey_stddevs = SurveyStdDevs(surveys, expected_values,
                                        extra_survey_stddev_expr);
    // Both the expected values and the stddevs are expressed in units of
    // thousandth of a percent. We need to scale the stddevs to be in
    // fractions of the expected value. This will then translate to stddevs
    // being in fractions of votes once we scale; and allow us to calculate
    // per-party per-district stddevs.
    for (auto &entry : survey_stddevs) {
      entry.second /= expected_values[entry.first];
    }  // Now it's unitless.
    // Scale the expected values to be roughly sum up to the total number
    // of votes.
    auto scaled_exp_values = ScaleSingleMap(expected_values,
        (double) SumMap(SumSubmaps(votes)) / (double) SumMap(expected_values));
    auto party_scaling_factors = CalculateScalingFactors(
        SumSubmaps(votes), scaled_exp_values);
    votes = ScaleByParty(votes, party_scaling_factors);
    // Now, stddevs should be votes * survey_stddevs
    auto party_district_stddevs = ScaleByParty(
        CastMapOfMaps<int, double>(votes), survey_stddevs);
    stddevs = AccumulateStdDev(stddevs, party_district_stddevs);
  }

  if (ConfigContains(main_config, stddev_config)) {
    Expression *vote_distribution_config =
        PartyVoteDistributionConfig(main_config[stddev_config]); 
    stddevs = AccumulateStdDev(
        stddevs, StdDevFromConfig(votes, vote_distribution_config));
  }

  if (ConfigContains(main_config, hardcoded_stddevs)) {
    stddevs = AccumulateStdDev(
        stddevs, HardcodedStddev(main_config[hardcoded_stddevs]));
  }

  std::cerr << "Reading data done" << std::endl;
  /************** Output vote counts, if asked for *********************/
  auto d_names = DistrictsToNames(district_infos);
  auto d_seats = DistrictsToSeats(district_infos);
  if (main_config[action] == "output_votes") {
    OutputMapOfMaps(votes, main_config[output], main_config[district_names],
                    d_names);
  }
  if (main_config[action] == "output_seats") {
    // The key here isn't the district name, so expanding district names
    // makes zero sense.
    OutputMap(AssignSeatsToParty(d_seats, votes),
              main_config[output], "", {});
  }
  if (main_config[action] == "output_votes_per_seat") {
    OutputMap(
        DivideMaps(SumSubmaps(PivotMap(votes)), d_seats),
        main_config[output], main_config[district_names], d_names);
  }
  if (main_config[action] == "output_vote_percentages") {
    OutputMapOfMaps(VoteFraction(votes), main_config[output],
                    main_config[district_names], d_names);
  }
  if (main_config[action] == "output_votes_to_next_seat") {
    OutputMapOfMaps(VotesToNextSeat(votes, d_seats), main_config[output],
                    main_config[district_names], d_names);
  }
  if (main_config[action] == "output_votes_to_previous_seat") {
    OutputMapOfMaps(VotesToPreviousSeat(votes, d_seats),
                    main_config[output],
                    main_config[district_names], d_names);   
  }
  if (main_config[action] == "output_last_seat_winner") {
    OutputMap(LastSeatWinner(votes, d_seats), main_config[output],
              main_config[district_names], d_names);
  }
  if (main_config[action] == "output_apply_strategy") {
    Strategy *strategy = ResolveStrategy(
        AssertGetConfigValue(main_config, strategy_config));
    std::vector<std::pair<int, int>> ranges;
    int min_voters =
        AssertGetIntConfigValue(main_config, strategy_min_voters_config);
    int max_voters =
        AssertGetIntConfigValue(main_config, strategy_max_voters_config);
    if (ConfigContains(main_config, strategy_voters_step_config)) {
      int step =
          AssertGetIntConfigValue(main_config, strategy_voters_step_config);
      assert((max_voters - min_voters) % step == 0);
      for (int lower = min_voters; lower < max_voters; lower += step) {
        ranges.push_back({ lower, lower + step});
      }
    } else {
      ranges = { std::make_pair(
          AssertGetIntConfigValue(main_config, strategy_min_voters_config),
          AssertGetIntConfigValue(main_config, strategy_max_voters_config)) };
    } 
    int repeats_cnt =
        AssertGetIntConfigValue(main_config, repeats);
    std::set<std::string> rejected_parties_list;
    if (ConfigContains(main_config, rejected_parties)) {
      rejected_parties_list = ParseConfigList(main_config[rejected_parties]);
    }
    AssertConfigContains(main_config, strategy_output_config);
    std::set<std::string> strategy_output =
        ParseConfigList(main_config[strategy_output_config]);
    std::random_device rd{};
    std::mt19937 gen{rd()};
    std::map<std::pair<int, int>, std::map<std::string, std::map<std::string, double>>>
        strategy_results;  // Voter range -> committee -> district -> seatdelta
    std::function<std::string(std::pair<int, int>)> pair_to_string =
        [](std::pair<int, int> p) {
          std::ostringstream ostr;
          ostr << "[" << std::setfill('0') << std::setw(7) << p.first << "-"
               << std::setfill('0') << std::setw(7) << p.second << "]";
          return ostr.str(); };
    for (auto &voters_range : ranges) {
      std::cerr << "Strategy for " << pair_to_string(voters_range) << std::endl;
      strategy_results[voters_range] = CheckStrategyResults(
          votes, d_seats, *strategy, rejected_parties_list, voters_range.first,
          voters_range.second, repeats_cnt, gen);
    }
    if (strategy_output.find("table_for_each_party") != strategy_output.end()) {
      for (const auto &party_and_res : PivotMap(strategy_results)) {
        std::cout << party_and_res.first << std::endl;
        OutputMapOfMaps(TranslateKeys(party_and_res.second, pair_to_string),
                        main_config[output], main_config[district_names], d_names);
        std::cout << std::endl;
      }
    }
    if (strategy_output.find("aggregate_districts") != strategy_output.end()) {
      auto to_print = PivotMap(
          TranslateKeys(SumSubSubmaps(strategy_results), pair_to_string));
      OutputMapOfMaps(to_print, main_config[output], "", {});
      std::cout << std::endl;
    }
  }
  if (main_config[action] == "output_stddev") {
    OutputMapOfMaps(stddevs,
                    main_config[output], main_config[district_names],
                    d_names);
  }
  if (main_config[action] == "interval_strength") {
    std::cerr << "Calculating interval-based strength" << std::endl;
    AssertConfigContains(main_config, first_seat_policy_config);
    FirstSeatPolicy *first_seat_policy =
        FirstSeatPolicyFromFile(main_config[first_seat_policy_config]);
    auto vote_strength = InverseVoteStrengthForAll(
        votes, d_seats, first_seat_policy);
    OutputMapOfMaps(vote_strength, main_config[output],
                    main_config[district_names], d_names);
  }
  if (main_config[action] == "probabilistic") {
    std::cerr << "Running probabilistic strength calculations" << std::endl;
    std::set<std::string> rejected_parties_list;
    if (ConfigContains(main_config, rejected_parties)) {
      rejected_parties_list = ParseConfigList(main_config[rejected_parties]);
    }
    std::random_device rd{};
    std::mt19937 gen{rd()};
    AssertConfigContains(main_config, repeats);
    int num_repeats = std::atoi(main_config[repeats].c_str());
    int vote_number_delta_val = 1;
    if (ConfigContains(main_config, vote_number_delta)) {
      vote_number_delta_val = std::atoi(
          main_config[vote_number_delta].c_str());
    }
    std::cerr << "VND: " << vote_number_delta_val << std::endl;
    auto vote_strength = ProbabilisticSeatStrengths(
        votes, d_seats, num_repeats, gen, vote_number_delta_val,
        stddevs, rejected_parties_list);
    OutputMapOfMaps(vote_strength, main_config[output],
                    main_config[district_names], d_names);
  }
}
