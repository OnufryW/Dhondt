#include <iostream>
#include <map>
#include "../lib/expression.h"
#include "test_util.h"

using std::cout;

void test_expression(const std::string &S,
                     const std::map<std::string, double> &vars,
                     double expected, const std::string &desc) {
  cout << "[ RUNNING ] Test Expression " << desc << std::endl;
  Expression *expr = ExpressionFromString(S);
  for (auto c : vars) {
    expr->SetVariable(c.first, c.second);
  }
  assert_eq(expected, expr->Calculate(), "expression value");
  cout << "[ OK ]" << std::endl;
}

void test_collect_variable_names(const std::string &S,
                                 const std::set<std::string> &expected,
                                 const std::string &desc) {
  cout << "[ RUNNING ] Test collect expression variable names "
       << desc << std::endl;
  Expression *expr = ExpressionFromString(S);
  std::set<std::string> names;
  expr->CollectVariableNames(names);
  assert_set_eq(expected, names);
  cout << "[ OK ]" << std::endl;
}

int main() {
  test_expression("0", {}, 0, "literal zero");
  test_expression("1", {}, 1, "literal one");
  test_expression("1200", {}, 1200, "multidigit literal constant");
  test_expression("1.5", {}, 1.5, "non-integral constant");
  test_expression("A", {{"A", 0.5}}, 0.5, "variable");
  test_expression("A + 0.5", {{"A", 0.5}}, 1, "addition");
  test_expression("X - 1", {{"X", 2}}, 1, "subtraction");
  test_expression("C - 1 - 1", {{"C", 7}}, 5, "chaining");
  test_expression("C*2", {{"C", -1}}, -2, "multiplication");
  test_expression("c/2", {{"c", 2}}, 1, "division");
  test_expression("c/(c+1)", {{"c", 1}}, 0.5, "parens");
  test_expression("min(0, 1)", {}, 0, "min");
  test_expression("max(A+B, 2*A) + 1", {{"A", 2}, {"B", 3}}, 6, "complex");
  test_expression("A", {{"A", 3}, {"B", 2}}, 3, "unused variable");
  test_expression("A + \"ZMIENNA\"", {{"A", 2}, {"ZMIENNA", 2}}, 4,
                  "multi-char variable");
  test_expression("\"XY\" + 1", {{"XY", 1}}, 2, "multi-char expression");
  test_expression("2 + 2 / 2", {}, 3, "Precedence");
  test_expression("max(0.7 * (V+G) - V, 0)", {{"V", 999}, {"G", 1}}, 0,
                  "FVP calculation, part 1");
  test_expression(
      "20 * max(0.7 * (V+G) - V, 0) * (0.7 * (V+G) - V) / (V+G) + (V+G)",
      {{"V", 999}, {"G", 1}},
      1000, "First vote policy expression");
  test_collect_variable_names("\"AB\" + A", {"AB", "A"}, "simple");
  test_collect_variable_names("15", {}, "no variables");
  test_collect_variable_names("A * A + B * B + B/A",
                              {"A", "B"}, "repeated");
}
