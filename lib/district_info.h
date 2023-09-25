#ifndef DISTRICT_INFO
#define DISTRICT_INFO

#include <string>
#include <map>

// Encodes the information about a particular district (independent from
// the results of voting - this is stuff that is known about the district
// prior to the election).
class DistrictInfo {
 public:
  DistrictInfo() {}
  DistrictInfo(std::string code, int seats, int citizens, int voters,
               std::string name) :
      code(std::move(code)), seats(seats), citizens(citizens),
      voters(voters), name(std::move(name)) {}

  std::string code;  // The code (a number from 1 to 41) of the district.
  int seats;  // The number of seats to be won in this district
  int citizens;  // The number of citizens of this distrcit acc. to PKW
  int voters;  // The number of citizens eligible to vote acc. to PKW
  std::string name;  // The name of the district (usually, a city name).
};

// DistrictInfo generally flies around in a map from the code to
// DistrictInfo. Below a bunch of helper functions to translate such a map
// to a map from code to something that interests us.

std::map<std::string, int> DistrictsToSeats(
    const std::map<std::string, DistrictInfo> &district_info) {
  std::map<std::string, int> res;
  for (const auto &D : district_info) {
    res[D.first] = D.second.seats;
  }
  return res;
}

std::map<std::string, int> DistrictsToCitizens(
    const std::map<std::string, DistrictInfo> &district_info) {
  std::map<std::string, int> res;
  for (const auto &D : district_info) {
    res[D.first] = D.second.citizens;
  }
  return res;
}

std::map<std::string, int> DistrictsToVoters(
    const std::map<std::string, DistrictInfo> &district_info) {
  std::map<std::string, int> res;
  for (const auto &D : district_info) {
    res[D.first] = D.second.voters;
  }
  return res;
}

std::map<std::string, std::string> DistrictsToNames(
    const std::map<std::string, DistrictInfo> &district_info) {
  std::map<std::string, std::string> res;
  for (const auto &D : district_info) {
    res[D.first] = D.second.name;
  }
  return res;
}

#endif // DISTRICT_INFO
