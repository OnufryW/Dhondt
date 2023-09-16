#include "parse_district_info.h"
#include "lib/assign_seats_to_districts.h"
#include <iostream>
using std::cout;

int main() {
  auto DI = DistrictInfoFromFile2019("data_2019_sejm/okregi_sejm.csv");
  auto correct = AssignSeatsToDistricts(DistrictsToCitizens(DI), 460);
  auto actual = DistrictsToSeats(DI);
  for (auto D : DI) {
    cout << D.second.name << " (" << D.first << ")"
         << ": " << actual[D.first] << " -> "
         << correct[D.first] 
         << std::endl;
  }
  return 0;
}
