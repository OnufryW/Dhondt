#ifndef DHONDT
#define DHONDT

#include <set>
#include <map>
#include <string>
#include <vector>

namespace {

typedef struct vote_candidate {
  std::string party;
  int votes;
  int denominator;
} vote_candidate;

bool compare(const vote_candidate &A, const vote_candidate &B) {
  if (A.votes * B.denominator != B.votes * A.denominator) {
    return A.votes * B.denominator > B.votes * A.denominator;
  }
  return A.votes > B.votes;
}

} // anon namespace

// Takes vote counts (map from party name to number of votes), and the total
// number of mandates available in the district, and returns mandate counts
// (map from party name to number of mandates).
std::map<std::string, int> VotesToMandates(
    const std::map<std::string, int>& votes,
    int total_mandates) {
  std::set<vote_candidate, decltype(compare)*> VC(compare);
  std::map<std::string, int> result;
  for (auto &V : votes) {
    result[V.first] = 0;
    vote_candidate cand;
    cand.party = V.first;
    cand.votes = V.second;
    cand.denominator = 1;
    VC.insert(cand);
  }
  for (int i = 0; i < total_mandates; ++i) {
    auto cand = *VC.begin();
    result[cand.party] += 1;
    VC.erase(VC.begin());
    cand.denominator += 1;
    VC.insert(cand);
  }
  return result;
}

// Takes vote counts (map from party name to number of votes), missing one
// party, and the total number of mandates; plus a number k (between 1 and
// the number of mandates, inclusive. Determines the number of votes V that
// the missing party has to get that to get at least k mandates.
int MinimumVotesToSeats(const std::map<std::string, int> &votes,
                        int total_seats, int desired_seats) {
  int max_votes = 0;
  for (const auto &V : votes) {
    if (max_votes < V.second) max_votes = V.second;
  }
  auto map_copy = votes;
  int lo = 0;
  int hi = desired_seats * max_votes + 1;
  while (hi - lo > 1) {
    int me = (hi + lo) / 2;
    map_copy[""] = me;
    int res = VotesToMandates(map_copy, total_seats)[""];
    if (res < desired_seats) {
      lo = me;
    } else {
      hi = me;
    }
  }
  return hi;
}

std::vector<int> KeyVoteValues(const std::map<std::string, int> &votes,
                               int total_seats) {
  std::vector<int> res;
  for (int desired_seats = 1; desired_seats <= total_seats; ++desired_seats) {
    res.push_back(MinimumVotesToSeats(votes, total_seats, desired_seats));
  }
  return res;
}

#endif // DHONDT
