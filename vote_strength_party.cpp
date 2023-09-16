#include "lib/parse_election_results.h"
#include "lib/parse_district_info.h"
#include <iostream>
#include "seat_probability.h"
using std::cout;

const long double percent_error = 0.03;
const int repeats = 1000;

int main() {
  ElectionResults *er = FromFile2019("data_2019_sejm/wyniki_sejm.csv");
  auto DI = DistrictInfoFromFile2019("data_2019_sejm/okregi_sejm.csv");
  auto vcbp = er->VoteCountsByParty();
  auto dts = DistrictsToSeats(DI);
  auto dr = er->ByDistrict();

  std::map<std::string, int> district_votes;

  for (auto &d : dr) {
    district_votes[d.first] = d.second.TotalVotes();
  }

  std::random_device rd{};
  std::mt19937 gen{rd()};
  for (auto &p : vcbp) {
    long double all_probs = 0;
    cout << p.first << std::endl;
    for (auto &d : dr) {
      long double stddev = district_votes[d.first] * percent_error;
      long double prob = SeatShiftProbabilityAllRandom(
          d.second.VoteCountByParty(), dts[d.first], stddev, p.first,
          repeats, gen);
      cout << std::fixed << DI[d.first].name << "(" << d.first << "): " << prob * 1000000 << std::endl;
      all_probs += prob;
    }
    cout << std::fixed << "Average: " << all_probs * 1000000/ dr.size() << std::endl << std::endl;
  }
  return 0;
}
