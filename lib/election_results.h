#ifndef ELECTION_RESULTS
#define ELECTION_RESULTS

#include <string>
#include <map>
#include <vector>
#include <algorithm>

// Helper class holding the results for a single district.
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

  // Map from party name to the number of votes it received.
  std::map<std::string, int> VoteCountByParty() { return vcbp; }
  // The ID of the district (e.g., "19").
  std::string DistrictId() { return id; }
  // The name of the district (e.g., "Okręg Wyborczy Nr 19").
  std::string DistrictName() { return name; }
  // The total number of votes cast (should be equal to the sum of all the
  // values in the vcbp map).
  int TotalVotes() { return total_votes; }
  // The number of eligible voters in this district.
  int TotalVoters() { return total_voters; }

 private:
  std::map<std::string, int> vcbp;
  std::string id;
  std::string name;
  int total_votes;
  int total_voters;
};

// Class holding the results for the whole elections, and various methods
// to pivot this data.
class ElectionResults {
 public:
  ElectionResults() {}
  ElectionResults(const std::map<std::string, DistrictResults> results) :
      election_results(results) {};

  // Map from district ID to DistrictResults.
  std::map<std::string, DistrictResults> ByDistrict();

  // Map from party name to a map < District ID, vote count >
  std::map<std::string, std::map<std::string, int>> VoteCountsByParty();

  // Map from party name to total votes that party received countrywide.
  std::map<std::string, int> TotalVoteCountsByParty();

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

std::map<std::string, int> ElectionResults::TotalVoteCountsByParty() {
  std::map<std::string, int> result;
  auto vcbp = VoteCountsByParty();
  for (auto party : vcbp) {
    result[party.first] = 0;
    for (auto district : party.second) {
      result[party.first] += district.second;
    }
  }
  return result;
}
#endif // ELECTION_RESULTS
