#include "lib/parse_election_results.h"
#include "lib/parse_district_info.h"
#include <iostream>
using std::cout;

int main() {
  ElectionResults *er = ElectionResultsFromFile(
      "data/sejm_election_results/by_district/2019.csv");
  auto DI = DistrictInfoFromFile2019("data_2019_sejm/okregi_sejm.csv");
  auto vcbp = er->VoteCountsByParty();

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
