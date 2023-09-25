#ifndef FIRST_SEAT_POLICY
#define FIRST_SEAT_POLICY

#include <fstream>
#include <string>
#include "expression.h"

// A "First Seat Policy" is in the context of calculating vote strength
// based on the length of the d'Hondt interval.

class FirstSeatPolicy {
 public:
  virtual int GetStrength(int votes, int G) const = 0;
};

class ExpressionFirstSeatPolicy : public FirstSeatPolicy {
 public:
  // Should take an expression taking variables V (expected vote number)
  // and G (votes needed for first seat).
  ExpressionFirstSeatPolicy(Expression *expr) : expr(expr) {}
  int GetStrength(int votes, int G) const {
    expr->SetVariable("V", votes);
    expr->SetVariable("G", G);
    return (int) expr->Calculate();
  }
 private:
  Expression *expr;
};

FirstSeatPolicy *FirstSeatPolicyFromFile(const std::string &filename) {
  std::fstream fs;
  fs.open(filename, std::ios::in);
  std::string line;
  while (std::getline(fs, line)) {
    if (line.size() == 0 || line[0] == '\n' || line[0] == '#') {
      continue;
    }
    return new ExpressionFirstSeatPolicy(ExpressionFromString(line));
  }
  assert(false);
}

#endif  // FIRST_SEAT_POLICY
