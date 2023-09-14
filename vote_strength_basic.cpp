#include "parse_election_results.h"
#include <iostream>
#include "election_results.h"
using std::cout;

int main() {
  ElectionResults *er = FromFile2019("data_2019_sejm/wyniki_sejm.csv");
  auto DI = DistrictInfoFromFile2019("data_2019_sejm/okregi_sejm.csv");
  auto vcbp = er->VoteCountsByParty();
  auto res = GetElectionResults(DistrictsToSeats(DI), er);

  int total = 0;
  std::map<std::string, int> total_votes_by_district;
  for (auto p : vcbp) {
    for (auto d : p.second) {
      total += d.second;
      total_votes_by_district[d.first] += d.second;
    }
  }
  std::vector<std::pair<int, std::string>> stre;
  for (auto p : total_votes_by_district) {
    stre.push_back(std::make_pair(p.second / DI[p.first].seats, p.first));
  }
  std::sort(stre.begin(), stre.end());
  for (auto S : stre) {
    cout << DI[S.second].name << "(" << S.second << "): " << S.first << std::endl;
  }
  return 0;
}