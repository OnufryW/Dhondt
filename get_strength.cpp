#include <vector>
#include <string>
#include <iostream>
#include <random>
#include <cassert>

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
#include "lib/party_vote_distribution.h"
#include "lib/seat_probability.h"
#include "lib/output_map.h"

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
const string district_names = "district_names";
const string first_seat_policy_config = "first_seat_policy_config";
const string stddev_config = "stddev_config";
const string repeats = "repeats";

bool ConfigContains(const std::map<std::string, std::string> &config,
                    const std::string &key) {
  return config.find(key) != config.end();
}

void AssertConfigContains(const std::map<std::string, std::string> &config,
                          const std::string &key) {
  assert(ConfigContains(config, key));
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
  AssertConfigContains(main_config, transferral_config);
  auto votes = CalculateVoteTransferral(
      old_res, main_config[transferral_config]);

  /*********** Scaling by population changes ****************************/
  AssertConfigContains(main_config, district_info_filename);
  auto district_infos = DistrictInfoFromFile2019(
      main_config[district_info_filename]);
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
    votes = ScaleVotesByParty(votes, party_scaling_factors);
  }

  /************** Output vote counts, if asked for *********************/
  auto d_names = DistrictsToNames(district_infos);
  if (main_config[action] == "output_votes") {
    OutputMapOfMaps(votes, main_config[output], main_config[district_names],
                    d_names);
  }
  if (main_config[action] == "output_seats") {
    OutputMap(AssignSeatsToParty(DistrictsToSeats(district_infos), votes),
              main_config[output], main_config[district_names], d_names);
  }
  if (main_config[action] == "interval_strength") {
    std::cerr << "Calculating interval-based strength" << std::endl;
    AssertConfigContains(main_config, first_seat_policy_config);
    FirstSeatPolicy *first_seat_policy =
        FirstSeatPolicyFromFile(main_config[first_seat_policy_config]);
    auto vote_strength = InverseVoteStrengthForAll(
        votes, DistrictsToSeats(district_infos), first_seat_policy);
    OutputMapOfMaps(vote_strength, main_config[output],
                    main_config[district_names], d_names);
  }
  if (main_config[action] == "probabilistic") {
    std::cerr << "Running probabilistic strength calculations" << std::endl;
    std::random_device rd{};
    std::mt19937 gen{rd()};
    AssertConfigContains(main_config, stddev_config);
    Expression *vote_distribution_config =
        PartyVoteDistributionConfig(main_config[stddev_config]);
    AssertConfigContains(main_config, repeats);
    int num_repeats = std::atoi(main_config[repeats].c_str());
    auto vote_strength = ProbabilisticSeatStrengths(
        votes, DistrictsToSeats(district_infos), num_repeats, gen,
        vote_distribution_config);
    OutputMapOfMaps(vote_strength, main_config[output],
                    main_config[district_names], d_names);
  }
}
