#include <string>
#include <iostream>
#include <random>

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

const string results_2019_filename = "data_2019_sejm/wyniki_sejm.csv";
const string results_2020_filename = "data_2020_president/prezydenckie.csv";
const string district_info_filename = "data_2019_sejm/okregi_sejm.csv";
const string pkw_citizens_filename = "data_2019_sejm/dane_z_listu_pkw.csv";
const string surveys_filename = "data_2019_sejm/sondaze.csv";

const string transferral_config = "config/vote_transferral_policy.txt";
const string first_seat_policy_config = "config/first_seat_policy.txt";
const string stddev_config = "config/vote_distribution_config.txt";

const int repeats = 10000;

const bool OUTPUT_INTERIM_DATA = false;

int main() {
  /********************* 2019 results transferred to 2023 **************/
  // Get 2019 election results, in committee -> district -> votes format.
  auto results2019 =
      FromFile2019(results_2019_filename)->VoteCountsByParty();
  // Get 2020 presidential election results, same format.
  auto results2020 = Presidential2020FromFile(results_2020_filename);
  // Calculate unscaled 2023 results, based on the transferral config.
  // Same format.
  auto unscaled2023 = CalculateVoteTransferral({results2019, results2020},
                                               transferral_config);
  if (OUTPUT_INTERIM_DATA) {
    std::cout << "Unscaled results: " << std::endl;
    DisplayMapOfMaps(unscaled2023);
    VisualDivider();
  }

  /*********** Scaling by population changes ****************************/
  auto district_infos = DistrictInfoFromFile2019(district_info_filename);
  // PKW population data.
  auto pkw_data = GetPkwPopulationData(pkw_citizens_filename);
  // Get the scaling factors for population (district name -> double)
  auto population_scaling_factors = CalculateScalingFactors(
      DistrictsToCitizens(district_infos), pkw_data);
  // Scale the vote counts by population changes.
  auto popscaled2023 = ScaleVotesByDistrict(
      unscaled2023, population_scaling_factors);
  if (OUTPUT_INTERIM_DATA) {
    std::cout << "Results scaled by population: " << std::endl;
    DisplayMapOfMaps(popscaled2023);
    VisualDivider();
  }

  /************** Scaling to survey results ****************************/
  // Scale by survey results. First, load surveys.
  auto surveys = ParseSurvey(surveys_filename);
  // Scale survey results, so that they sum up (roughly) to the number of
  // votes we expect:
  auto scaled_surveys = ScaleSingleMap(
      surveys,
      (double) SumMap(SumSubmaps(popscaled2023)) / (double) SumMap(surveys));
  // Scaling factors by party - we want to bring total votes for every
  // party to the survey values.
  auto party_scaling_factors = CalculateScalingFactors(
      SumSubmaps(popscaled2023), scaled_surveys);
  // And apply the scaling factors.
  auto scaled2023 = ScaleVotesByParty(popscaled2023, party_scaling_factors);
  if (OUTPUT_INTERIM_DATA) {
    std::cout << "Results scaled by population and surveys:" << std::endl;
    DisplayMapOfMaps(scaled2023);
    VisualDivider();
  }
  if (OUTPUT_INTERIM_DATA) {
    std::cout << "Predicted election results:" << std::endl;
    DisplayMap(AssignSeatsToParty(
        DistrictsToSeats(district_infos), scaled2023));
    VisualDivider();
  }

  /************* Calculating vote strength by interval ****************/
  // Get the first seat policy
  FirstSeatPolicy *first_seat_policy =
      FirstSeatPolicyFromFile(first_seat_policy_config);
  // Calculate vote strength by party
  auto vote_strengths_interval = InverseVoteStrengthForAll(
      scaled2023, DistrictsToSeats(district_infos), first_seat_policy);

  /*************** Calculate vote strength by probability *************/
  // Randomness.
  std::random_device rd{};
  std::mt19937 gen{rd()};
  // Parse the stddev config.
  Expression *vote_distribution_config =
      PartyVoteDistributionConfig(stddev_config);
  // Get the seat strengthsi
  auto vote_strengths_probability = ProbabilisticSeatStrengths(
      scaled2023, DistrictsToSeats(district_infos), repeats, gen,
      vote_distribution_config);

  /*************** Output *********************************************/
  std::cout << std::endl << "Vote strengths by interval length" << std::endl;
  DisplayMapOfMaps(ExpandDistrictNamesInMapOfMaps(
      vote_strengths_interval, DistrictsToNames(district_infos))); 
  std::cout << std::endl << "Vote strengths by probability" << std::endl;
  DisplayMapOfMaps(ExpandDistrictNamesInMapOfMaps(
      vote_strengths_probability, DistrictsToNames(district_infos)));
}
