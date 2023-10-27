#ifndef STRATEGY
#define STRATEGY

#include <string>
#include <vector>

// A component of a strategy - a target district and committee for any
// affected voters, and a probability with which this should be applied.
struct MoveComponent {
  std::string target_district_id;
  std::string target_committee;
  double probability;
};

// An electoral tourism strategy - 
class Strategy {
 public:
  // Do we expect voters in district voting for committee to do anything.
  virtual bool IsSource(
      const std::string &district_id, const std::string &committee) = 0;
  // A list of move components. The probabilities of all the move
  // components for one committee should sum up to something no larger
  // than 1 (if they sum up to less than 1, the remaining probability
  // has the voter stay in their district and vote as they had).
  virtual std::vector<MoveComponent> GetStrategy(
      const std::string &district_id, const std::string &committee) = 0;
};

#endif // STRATEGY
