#ifndef DHONDT
#define DHONDT

#include <cmath>
#include <set>
#include <map>
#include <string>
#include <vector>
#include <algorithm>
#include <queue>

namespace {

typedef struct vote_candidate {
  std::string party;
  int votes;
  int denominator;
} vote_candidate;

struct Compare {
  bool operator()(const vote_candidate &A, const vote_candidate &B) const {
    if (A.votes * B.denominator != B.votes * A.denominator) {
      return A.votes * B.denominator < B.votes * A.denominator;
    }
    if (A.votes != B.votes) return A.votes < B.votes;
    return A.party > B.party;
  }
};

} // anon namespace

// Takes vote counts (map from party name to number of votes), and the total
// number of seats available in the district, and returns seat counts
// (map from party name to number of seats).
std::map<std::string, int> VotesToSeats(
    const std::map<std::string, int>& votes, int total_seats) {
  std::priority_queue<
      vote_candidate, std::vector<vote_candidate>, Compare> VC;
  std::map<std::string, int> result;
  for (auto &V : votes) {
    result[V.first] = 0;
    vote_candidate cand;
    cand.party = V.first;
    cand.votes = V.second;
    cand.denominator = 1;
    VC.push(cand);
  }
  for (int i = 0; i < total_seats; ++i) {
    auto cand = VC.top();
    result[cand.party] += 1;
    VC.pop();
    cand.denominator += 1;
    VC.push(cand);
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
  // The implementation is somewhat optimized. What we do is:
  // 1) Calculate the d'Hondt seat winners --- what really matters is the
  //    set of values with which a seat is won.
  //    We do that the same way as in VotesToSeats. It would probably be
  //    faster to use a priority_queue instead of a set here, FWIW, but
  //    I didn't bother.
  // 2) Beginning from the weakest winner, we try to take away their
  //    seat as our i-th seat. This means 
  //        our_votes / i+1 >= their_votes / their_denominator.
  //    Which allows us to calculate the key vote value.
  std::vector<int> res;
  std::priority_queue<
      vote_candidate, std::vector<vote_candidate>, Compare> VC;
  for (auto &V : votes) {
    vote_candidate cand;
    cand.party = V.first;
    cand.votes = V.second;
    cand.denominator = 1;
    VC.push(cand);
  }
  std::vector<vote_candidate> winners;
  for (int i = 0; i < total_seats; ++i) {
    auto cand = VC.top();
    winners.push_back(cand);
    VC.pop();
    cand.denominator += 1;
    VC.push(cand);
  }
  // Begin from the last seat won.
  std::reverse(winners.begin(), winners.end()); 
  for (int i = 0; i < total_seats; ++i) {
    res.push_back(
        (winners[i].votes * (i + 1) + winners[i].denominator - 1) /
            winners[i].denominator);
  }
  return res;
}

#endif // DHONDT
