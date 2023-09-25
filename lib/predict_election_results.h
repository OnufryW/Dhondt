#ifndef PREDICT_ELECTION_RESULTS
#define PREDICT_ELECTION_RESULTS

#include "election_results.h"
#include "parse_csv.h"

// TODO: Remove this file.
ElectionResults *ModifyElectionResults(
    ElectionResults *old_results,
    std::map<std::string, std::pair<std::string, long double>> surveys) {
  std::map<std::string, int> old_votes = old_results->TotalVoteCountsByParty();
  int total_votes = 0;
  for (auto party : old_votes) total_votes += party.second;
  std::map<std::string, long double> modifiers;
  for (auto party : old_votes) {
    std::string pn = party.first;
    if (surveys.find(pn) == surveys.end()) {
      // No survey data, so let's assume old results hold.
      modifiers[pn] = 1.L;
    } else {
      modifiers[pn] = surveys[pn].second * total_votes /
          (100. * old_votes[party.first]);
    }
  }
  std::map<std::string, DistrictResults> new_results;
  for (auto district : old_results->ByDistrict()) {
    auto dr = district.second;
    std::map<std::string, int> new_votes;
    for (auto party : dr.VoteCountByParty()) {
      new_votes[party.first] = party.second * modifiers[party.first];
    }
    new_results[district.first] = DistrictResults(
        new_votes, dr.DistrictId(), dr.DistrictName(), dr.TotalVotes(),
        dr.TotalVoters());
  }
  return new ElectionResults(new_results);
}

#endif // PREDICT_ELECTION_RESULTS
