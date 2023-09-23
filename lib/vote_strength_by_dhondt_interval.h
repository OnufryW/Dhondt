#ifndef VOTE_STRENGTH_BY_DHONDT_INTERVAL
#define VOTE_STRENGTH_BY_DHONDT_INTERVAL

#include <map>
#include <string>
#include "dhondt.h"
#include "first_seat_policy.h"

// This is a policy for counting vote strength for a given party in a given
// district based on the length of the d'Hondt intervals.
// Let's say that we have a party that has N seats in a district, and
// predicted vote numbers for every party. We can calculate two numbers:
// - how many votes can this party lose, and still retain N seats (L)
// - how many votes the party needs to win in order to get N+1 seats (G).
// We will say the strengdth of a vote for the party in the district is
// inversely proportional to L+G.
// 
// First, maybe a bit of explanation why L+G. The more natural number to
// take is simply G (how close are we to winning the next vote). The problem
// is that the "predicted vote numbers for every party" are never exact,
// they are calculated with a noticeable error (I would estimate between
// 3 and 5 percent, based on absolutely nothing). So, the real vote value
// will be roughly estimate +/- error. The error is comparable in size to
// L+G, generally (maybe a bit smaller, maybe a bit larger); and so the
// real question is how close we land to the border of L+G (because a single
// vote will give gains to the party if we land one vote shy of estimate-L,
// or exactly at estimate+G. And so, with L+G values to choose from, we
// want to hit one of two of them - which happens roughly with 2/(L+G)
// chance.
// What's more, the number L+G is pretty stable. In particular, if the real
// vote count doesn't change by more than min(L,G), the number L+G stays
// the same. On the other hand, if the real vote count changes by, say,
// G/2, if we took just G as estimate of vote strength, it would increase
// twice with a very small change of actual results. Given that we have
// predictions encumbered with an error, we really need stable estimates
// of vote strength.
//
// Of course, that's a heuristic. The better number to use would be actual
// probability numbers, but that would involve making some assumptions
// about the distribution of the vote counts. The goal here is to have a
// number to look at which is stable, and doesn't involve making too many
// assumptions (similarly to the "votes per mandate" number).
//
// Finally, there's the question what to do about parties that didn't get
// even one seat in the district (and so for which L is undefined). We
// delegate this to the "first seat policy", which will calculate the
// equivalent of L+G for a party that we expect to get roughly V votes,
// and needing G more to get it's first seat.

// Returns the map from party to inverse vote strength.
std::map<std::string, int> InverseVoteStrengths(
    const std::map<std::string, int> &votes, int total_seats,
    const FirstSeatPolicy *first_seat_policy) {
  // This is horrifyingly ineffective, but given that I won't need to repeat
  // the calculation multiple times, whatever.
  std::map<std::string, int> result;
  std::map<std::string, int> expected_seat_counts = VotesToSeats(
      votes, total_seats);
  for (const auto &party_votes : votes) {
    int seats = expected_seat_counts.at(party_votes.first);
    auto votes_copy = votes;
    votes_copy.erase(party_votes.first);
    int G = MinimumVotesToSeats(votes_copy, total_seats, seats + 1) -
        votes.at(party_votes.first);
    // Technically, I should also use a "last vote policy", to cover the
    // case where a party gets all the seats in a district. In practice,
    // this is not expected to happen.
    if (seats == 0) {
      result[party_votes.first] = first_seat_policy->GetStrength(
          party_votes.second, G);
    } else {
      int L = votes.at(party_votes.first) -
          MinimumVotesToSeats(votes_copy, total_seats, seats);
      result[party_votes.first] = L + G;
    }
  }
  return result;
}
                        
#endif  // VOTE_STRENGTH_BY_DHONDT_INTERVAL
