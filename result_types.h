#ifndef RESULT_TYPES
#define RESULT_TYPES

#include <string>
#include <map>
#include <vector>
#include <algorithm>

class DistrictInfo {
 public:
  DistrictInfo() {}
  DistrictInfo(std::string code, int seats, int citizens, int voters,
               std::string name) :
      code(code), seats(seats), citizens(citizens), voters(voters),
      name(name) {}

  std::string code;
  int seats;
  int citizens;
  int voters;
  std::string name;
};

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

std::map<std::string, int> AssignSeatsToDistricts(
    const std::map<std::string, int> &district_info, int total_mandates) {
  long long total_value = 0;
  for (const auto &d : district_info) {
    total_value += d.second;
  }
  std::map<std::string, int> res;
  int assigned = 0;
  // Vector of (remainder, (original votes, district code))
  std::vector<std::pair<int, std::pair<int, std::string>>> remainders;
  for (const auto &d : district_info) {
    long long base = (total_mandates * d.second) / total_value;
    res[d.first] = base;
    assigned += base;
    long long remainder = (total_mandates * d.second) - base * total_value;
    remainders.push_back(
        make_pair(remainder, make_pair(d.second, d.first)));
  }
  sort(remainders.begin(), remainders.end());
  int curr = remainders.size() - 1;
  while (assigned < total_mandates) {
    res[remainders[curr].second.second] += 1;
    assigned += 1;
    curr -= 1;
  }
  return res;
}

class DistrictResults {
 public:
  DistrictResults() {}
  DistrictResults(std::map<std::string, int> vcbp,
                  std::string id,
                  std::string name,
                  int total_votes,
                  int total_voters) :
      vcbp(vcbp), id(id), name(name), total_votes(total_votes),
      total_voters(total_voters) {}

  std::map<std::string, int> VoteCountByParty() { return vcbp; }
  std::string DistrictId() { return id; }
  std::string DistrictName() { return name; }
  int TotalVotes() { return total_votes; }
  int TotalVoters() { return total_voters; }

 private:
  std::map<std::string, int> vcbp;
  std::string id;
  std::string name;
  int total_votes;
  int total_voters;
};

class ElectionResults {
 public:
  ElectionResults() {}
  ElectionResults(const std::map<std::string, DistrictResults> results) :
      election_results(results) {};

  std::map<std::string, DistrictResults> ByDistrict();

  std::map<std::string, std::map<std::string, int>> VoteCountsByParty();

  static ElectionResults *FromFile(const std::string &filename);

 private:
  std::map<std::string, DistrictResults> election_results;
};

std::map<std::string, DistrictResults> ElectionResults::ByDistrict() {
  return election_results;
}

std::map<std::string, std::map<std::string, int>>
ElectionResults::VoteCountsByParty() {
  std::map<std::string, std::map<std::string, int>> result;
  for (auto dist : election_results) {
    for (auto party : dist.second.VoteCountByParty()) {
      result[party.first][dist.first] = party.second;
    }
  }
  return result;
}

#endif // RESULT_TYPES
