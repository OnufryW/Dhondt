#ifndef VOTE_POSITION
#define VOTE_POSITION

#include <map>
#include <string>
#include "map_tools.h"
#include "dhondt.h"

std::map<std::string, std::map<std::string, double>> VoteFraction(
    const std::map<std::string, std::map<std::string, int>> &votes) {
  auto total_votes_per_district = SumSubmaps(PivotMap(votes));
  std::map<std::string, std::map<std::string, double>> res;
  for (const auto &committee_data : votes) {
    const auto &committee = committee_data.first;
    res[committee] = {};
    for (const auto &district_data : committee_data.second) {
      const auto &district = district_data.first;
      res[committee][district] = (double) district_data.second /
          (double) total_votes_per_district[district];
    }
  }
  return res;
}

std::map<std::string, std::string> LastSeatWinner(
    const std::map<std::string, std::map<std::string, int>> &votes,
    const std::map<std::string, int> &seat_counts) {
  std::map<std::string, std::string> res;
  auto by_district = PivotMap(votes);
  for (const auto &district_data : by_district) {
    int seats = seat_counts.at(district_data.first);
    res[district_data.first] =
        LastSeatWinnerInDistrict(district_data.second, seats);
  }
  return res;
}

std::map<std::string, std::map<std::string, int>> VotesToNextSeat(
    const std::map<std::string, std::map<std::string, int>> &votes,
    const std::map<std::string, int> &seats_counts) {
  auto by_district = PivotMap(votes);
  std::map<std::string, std::map<std::string, int>> pivoted_res;
  for (const auto &district_data : by_district) {
    const auto &district = district_data.first;
    int seats = seats_counts.at(district);
    pivoted_res[district] = {};
    auto seat_counts = VotesToSeats(district_data.second, seats);
    for (const auto &committee_data : district_data.second) {
      const auto &committee = committee_data.first;
      if (seat_counts[committee] == seats) {
        pivoted_res[district][committee] = -1;
        continue;
      }
      auto tweaked_votes = district_data.second;
      tweaked_votes.erase(committee);
      pivoted_res[district][committee] = MinimumVotesToSeats(
          tweaked_votes, seats, seat_counts[committee] + 1) - 
          committee_data.second;
    }
  }
  return PivotMap(pivoted_res);
}

std::map<std::string, std::map<std::string, int>> VotesToPreviousSeat(
    const std::map<std::string, std::map<std::string, int>> &votes,
    const std::map<std::string, int> &seats_counts) {
  auto by_district = PivotMap(votes);
  std::map<std::string, std::map<std::string, int>> pivoted_res;
  for (const auto &district_data : by_district) {
    const auto &district = district_data.first;
    int seats = seats_counts.at(district);
    pivoted_res[district] = {};
    auto seat_counts = VotesToSeats(district_data.second, seats);
    for (const auto &committee_data : district_data.second) {
      const auto &committee = committee_data.first;
      if (seat_counts[committee] == 0) {
        pivoted_res[district][committee] = -1;
        continue;
      }
      auto tweaked_votes = district_data.second;
      tweaked_votes.erase(committee);
      pivoted_res[district][committee] = committee_data.second -
          MinimumVotesToSeats(tweaked_votes, seats, seat_counts[committee]);
    }
  }
  return PivotMap(pivoted_res);
}

#endif // VOTE_POSITION
