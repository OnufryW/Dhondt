#include <iostream>
#include "lib/parse_pkw_district_info.h"
using std::cout;

int main() {
  auto res = VotesPerMandate("data_2019_sejm/okregi_sejm.csv",
                             "data_2019_sejm/wyniki_sejm.csv",
                             "data_2019_sejm/dane_z_listu_pkw.csv");
  auto DI = DistrictInfoFromFile2019("data_2019_sejm/okregi_sejm.csv");
  for (auto v : res) {
    std::string district = v.first;
    cout << DI[district].name << "(" << district
         << "): " << v.second << std::endl;
  }
  return 0;
}
