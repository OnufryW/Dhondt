#ifndef PARTY_VOTE_DISTRIBUTION
#define PARTY_VOTE_DISTRIBUTION

#include <string>
#include "parse_config_file.h"
#include "expression.h"
#include "distribution.h"
#include "normal_distribution.h"

Distribution *GetPartyVoteDistribution(
    int expected_votes, int total_votes, Expression *stddev) {
  stddev->SetVariable("T", total_votes);
  stddev->SetVariable("V", expected_votes);
  return new NormalDistribution(expected_votes, stddev->Calculate());
}

Expression *PartyVoteDistributionConfig(const std::string &filename) {
  return ExpressionFromString(ParseOneLineConfigFile(filename));
}

#endif // PARTY_VOTE_DISTRIBUTION
