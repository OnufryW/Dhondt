#include "assign_seats.h"
#include "lib/assign_seats_to_districts.h"
#include <iostream>
#include <map>
#include <string>
using std::cout;

int main() {
  ElectionResults *er = FromFile2019("data_2019_sejm/wyniki_sejm.csv");
  auto district_info = DistrictInfoFromFile2019(
      "data_2019_sejm/okregi_sejm.csv");
  auto district_seats = DistrictsToSeats(district_info);
  auto res = GetElectionResults(district_seats, er);
  cout << "Faktyczne wyniki" << std::endl;
  for (auto R : res) {
    cout << R.first << "      " << R.second << std::endl;
  }
  cout << std::endl;
  auto correct_district_seats = AssignSeatsToDistricts(
      DistrictsToCitizens(district_info), 460);
  res = GetElectionResults(correct_district_seats, er);
  cout << "Poprawne wyniki:" << std::endl;
  for (auto R : res) {
    std::cout << R.first << "      " << R.second << std::endl;
  }
  cout << std::endl;
  auto voter_district_seats = AssignSeatsToDistricts(
      DistrictsToVoters(district_info), 460);
  res = GetElectionResults(voter_district_seats, er);
  cout << "Wg uprawnionych do glosowania wyniki:" << std::endl;
  for (auto R : res) {
    std::cout << R.first << "      " << R.second << std::endl;
  }
  return 0;
}
