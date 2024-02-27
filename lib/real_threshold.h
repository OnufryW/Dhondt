#ifndef REAL_THRESHOLD
#define REAL_THRESHOLD

#include "dhondt.h"
#include "map_tools.h"

// If we add a new party, with totally new voters, into the district, what
// percentage of the vote would it have to get in order to get one seat.
// Note that this effectively decreases the percentages other parties get.
double GetNewPartyThresholdInDistrict(
    const std::map<std::string, int> &votes_cast, int seats) {
  double required_votes = MinimumVotesToSeats(votes_cast, seats, 1);
  return required_votes / (double) (SumMap(votes_cast) + required_votes);
}

// If we keep the existing parties in the district, and we add votes to the
// strongest party that didn't get a seat, what percentage of the vote would
// it have to get in order to get a seat. If there's no such party, assume
// a new party with zero votes.
double GetRisingPartyThresholdInDistrict(
    const std::map<std::string, int> &votes_cast, int seats) {
  auto party_seats = VotesToSeats(votes_cast, seats); 
  std::pair<std::string, int> rising_party = {"", 0};
  for (auto party_and_votes : votes_cast) {
    if (party_and_votes.second > rising_party.second &&
        party_seats[party_and_votes.first] == 0) {
      rising_party = party_and_votes;
    }
  }
  auto votes_copy = votes_cast;
  votes_copy[rising_party.first] = 0;
  return GetNewPartyThresholdInDistrict(votes_copy, seats);
}

// If we keep the existing parties, and remove votes from the weakest party
// that did get a seat, what percentage of the vote would that party have
// to get in order to lose all seats.
double GetWeakeningPartyThresholdInDistrict(
    const std::map<std::string, int> &votes_cast, int seats) {
  auto party_seats = VotesToSeats(votes_cast, seats);
  std::pair<std::string, int> weakening_party = {"", SumMap(votes_cast)};
  for (auto party_and_votes : votes_cast) {
    if (party_and_votes.second <= weakening_party.second &&
        party_seats[party_and_votes.first] > 0) {
      weakening_party = party_and_votes;
    }
  }
  auto votes_copy = votes_cast;
  votes_copy[weakening_party.first] = 0;
  return GetNewPartyThresholdInDistrict(votes_copy, seats);
}

double GetThresholdInDistrict(
    const std::map<std::string, int> &votes_cast, std::string type,
    int seats) {
  if (type == "new") {
    return GetNewPartyThresholdInDistrict(votes_cast, seats);
  }
  if (type == "rising") {
    return GetRisingPartyThresholdInDistrict(votes_cast, seats);
  }
  if (type == "weakening") {
    return GetWeakeningPartyThresholdInDistrict(votes_cast, seats);
  }
  assert(false);
}

std::map<int, double> GetThresholdsInDistrict(
    const std::map<std::string, int> &votes_cast, std::string type,
    int max_seats) {
  std::map<int, double> res;
  for (int seats = 1; seats <= max_seats; seats++) {
    res[seats] = GetThresholdInDistrict(votes_cast, type, seats);
  }
  return res;
}

std::map<std::string, std::map<int, double>> GetThresholds(
    const std::map<std::string, std::map<std::string, int>> &votes_cast,
    std::string type, int max_seats) {
  std::map<std::string, std::map<int, double>> res;
  for (const auto &district_and_votes : PivotMap(votes_cast)) {
    res[district_and_votes.first] = GetThresholdsInDistrict(
        district_and_votes.second, type, max_seats);
  }
  return res;
}

#endif // REAL_THRESHOLD
