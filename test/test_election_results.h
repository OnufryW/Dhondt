#ifndef TEST_ELECTION_RESULTS
#define TEST_ELECTION_RESULTS

// The ElectionResults class is somewhat of a pain to construct (in real
// life, we construct it by parsing CSV files), so for test purposes
// I provide here a simpler method of construction that fakes out a lot
// of stuff.
// Also a test constructor for DistrictResults

DistrictResults DR(
    const std::map<std::string, int> &party_to_votes,
    const std::string &name) {
  int total = 0;
  for (auto v : party_to_votes) total += v.second;
  return DistrictResults(party_to_votes, name, name, total, 2 * total);
}

ElectionResults ER(
    const std::map<std::string, std::map<std::string, int>> &by_district) {
  std::map<std::string, DistrictResults> res;
  for (auto district : by_district) {
    res[district.first] = DR(district.second, district.first);
  }
  return ElectionResults(res);
}

#endif // TEST_ELECTION_RESULTS
