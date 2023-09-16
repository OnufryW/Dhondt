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
  if (A.votes != B.votes) return A.votes > B.votes;
  return A.party < B.party;
}

} // anon namespace

// Takes vote counts (map from party name to number of votes), and the total
// number of seats available in the district, and returns seat counts
// (map from party name to number of seats).
std::map<std::string, int> VotesToSeats(
    const std::map<std::string, int>& votes, int total_seats) {
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
  for (int i = 0; i < total_seats; ++i) {
    auto cand = *VC.begin();
    result[cand.party] += 1;
    VC.erase(VC.begin());
    cand.denominator += 1;
    VC.insert(cand);
  }
  return result;
}

// Takes vote counts (map from party name to number of votes), missing one
// party, and the total number of seats; plus a number k (between 1 and
// the number of seats, inclusive. Determines the number of votes V that
// the missing party has to get that to get at least k seats.
// Assumes our party wins tiebreakers on party name (which might be
// inaccurate, but it will be an off-by-one error, which shouldn't matter)
int MinimumVotesToSeats(const std::map<std::string, int> &votes,
                        int total_seats, int desired_seats) {
  int max_votes = 0;
  for (const auto &V : votes) {
    if (max_votes < V.second) max_votes = V.second;
  }
  auto map_copy = votes;
  int lo = 0;
  int hi = desired_seats * max_votes + 1;
  // Note: Efficiency might be improved here and in KeyVoteValues - I could
  // run dhondt just once for all the other parties, and produce the key
  // vote values based on that, instead of running the admittedly silly
  // binary search.
  while (hi - lo > 1) {
    int me = (hi + lo) / 2;
    map_copy[""] = me;
    int res = VotesToSeats(map_copy, total_seats)[""];
    if (res < desired_seats) {
      lo = me;
    } else {
      hi = me;
    }
  }
  return hi;
}

// Take vote counts (map from party name to votes), missing one party,
// and the total number of seats available. Return a vector of key vote
// counts C such that the extra party would receive one seat more by
// getting C votes than by getting C-1 votes.
// Assumes our party wins tiebreakers on party name (which might be
// inaccurate, but it will be an off-by-one error, which shouldn't matter)
std::vector<int> KeyVoteValues(const std::map<std::string, int> &votes,
                               int total_seats) {
  std::vector<int> res;
  for (int desired_seats = 1; desired_seats <= total_seats; ++desired_seats) {
    res.push_back(MinimumVotesToSeats(votes, total_seats, desired_seats));
  }
  return res;
}

#endif // DHONDT
