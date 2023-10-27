#ifndef EXPRESSION
#define EXPRESSION

#include <cmath>
#include <cassert>
#include <vector>
#include <set>
#include <map>
#include <algorithm>

class Expression {
 public:
  virtual double Calculate() = 0;
  virtual void SetVariable(const std::string &name, double value) {}
  // Add the names of all the variables in all the sub-expressions.
  virtual void CollectVariableNames(std::set<std::string> &names) = 0;
};

class Variable : public Expression {
 public:
  Variable(const std::string &C) : name(C), value(0), is_set(false) {}
  double Calculate() {
    assert(is_set);
    return value;
  }
  void SetVariable(const std::string &toset, double val) {
    if (toset == name) { 
      is_set = true;
      value = val;
    }
  }
  void CollectVariableNames(std::set<std::string> &names) {
    names.insert(name);
  }

 private:
  std::string name;
  double value;
  bool is_set;
};

class Const : public Expression {
 public:
  Const(double val) : val(val) {}
  double Calculate() { return val; }
  void CollectVariableNames(std::set<std::string> &names) {}
 private:
  double val;
};

class BinaryExpr : public Expression {
 public:
  BinaryExpr(Expression *left, Expression *right)
      : left(left), right(right) {}
  virtual void SetVariable(const std::string &name, double val) {
    left->SetVariable(name, val);
    right->SetVariable(name, val);
  }
  virtual void CollectVariableNames(std::set<std::string> &names) {
    left->CollectVariableNames(names);
    right->CollectVariableNames(names);
  }
 protected:
  Expression *left, *right;
};

class UnaryExpr : public Expression {
 public:
  UnaryExpr(Expression *child) : child(child) {}
  virtual void SetVariable(const std::string &name, double val) {
    child->SetVariable(name, val);
  }
  virtual void CollectVariableNames(std::set<std::string> &names) {
    child->CollectVariableNames(names);
  }
 protected:
  Expression *child;
};

class Sqrt : public UnaryExpr {
 public:
  Sqrt(Expression *child) : UnaryExpr(child) {}
  double Calculate() { return std::sqrt(child->Calculate()); }
};

class Sum : public BinaryExpr {
 public:
  Sum(Expression *left, Expression *right) : BinaryExpr(left, right) {}
  double Calculate() { return left->Calculate() + right->Calculate(); }
};

class Difference : public BinaryExpr {
 public:
  Difference(Expression *left, Expression *right)
      : BinaryExpr(left, right) {}
  double Calculate() { return left->Calculate() - right->Calculate(); }
};

class Min : public BinaryExpr {
 public:
  Min(Expression *left, Expression *right) : BinaryExpr(left, right) {}
  double Calculate() {
    return std::min(left->Calculate(), right->Calculate());
  }
};

class Max : public BinaryExpr {
 public:
  Max(Expression *left, Expression *right) : BinaryExpr(left, right) {}
  double Calculate() {
    return std::max(left->Calculate(), right->Calculate());
  }
};

class Quotient : public BinaryExpr {
 public:
  Quotient(Expression *left, Expression *right)
      : BinaryExpr(left, right) {}
  double Calculate() { return left->Calculate() / right->Calculate(); }
};

class Product : public BinaryExpr {
 public:
  Product(Expression *left, Expression *right) : BinaryExpr(left, right) {}
  double Calculate() { return left->Calculate() * right->Calculate(); }
};

struct Token {
  Token(Expression *e) : preparsed(e), token(0) {}
  Token(char token) : preparsed(nullptr), token(token) {}
  Expression *preparsed;
  char token;
};

const std::string VALID_TOKENS = "+-*/,()";
const std::string NUMBER_ELEMENTS = "0123456789.";

std::vector<Token> tokenize(const std::string &S) {
  std::vector<Token> res;
  size_t pos = 0;
  while (pos < S.size()) {
    if (std::isspace(S[pos])) { pos++; continue; }
    // Parsing function names.
    if (S.size() >= 3 && S.substr(pos,3) == "min") {
      res.push_back(Token('I'));
      pos += 3;
      continue;
    }
    if (S.size() >= 3 && S.substr(pos,3) == "max") {
      res.push_back(Token('X'));
      pos += 3;
      continue;
    }
    if (S.size() >= 4 && S.substr(pos,4) == "sqrt") {
      res.push_back(Token('Q'));
      pos += 4;
      continue;
    }
    if (VALID_TOKENS.find(S[pos]) != std::string::npos) {
      res.push_back(Token(S[pos++]));
      continue;
    }
    size_t numend = pos;
    while (numend < S.size() &&
           NUMBER_ELEMENTS.find(S[numend]) != std::string::npos) {
      numend++;
    }
    if (numend > pos) {
      res.push_back(
          Token(new Const(atof(S.substr(pos, numend-pos).c_str()))));
      pos = numend;
      continue;
    }
    // Allow variables that are single-char, unquoted, or quoted string.
    if (S[pos] == '"') {
      std::string name;
      pos++;
      while (S[pos] != '"') {
        name += S[pos++];
      }
      pos++;
      res.push_back(Token(new Variable(name)));
      continue;
    }
    res.push_back(Token(new Variable(std::string(1, S[pos++]))));
  }
  return res;
}

Expression *GetExpression(std::vector<Token> &tokens, size_t &curr);

Expression *GetPrimary(std::vector<Token> &tokens, size_t &curr) {
  if (tokens[curr].preparsed != nullptr) {
    curr++;
    return tokens[curr-1].preparsed;
  }
  if (tokens[curr].token == '(') {
    curr++;
    Expression *expr = GetExpression(tokens, curr);
    assert(tokens[curr].token == ')');
    curr++;
    return expr;
  }
  if (tokens[curr].token == 'I' || tokens[curr].token == 'X') {
    char func = tokens[curr++].token;
    assert(tokens[curr++].token == '(');
    Expression *left = GetExpression(tokens, curr);
    assert(tokens[curr++].token == ',');
    Expression *right = GetExpression(tokens, curr);
    assert(tokens[curr++].token == ')');
    if (func == 'I') return new Min(left, right);
    if (func == 'X') return new Max(left, right);
  }
  if (tokens[curr].token == 'Q') {
    char func = tokens[curr++].token;
    assert(tokens[curr++].token == '(');
    Expression *child = GetExpression(tokens, curr);
    assert(tokens[curr++].token == ')');
    if (func == 'Q') return new Sqrt(child);
  }
  assert(false);
}

Expression *GetFactor(std::vector<Token> &tokens, size_t &curr) {
  Expression *left = GetPrimary(tokens, curr);
  while (curr < tokens.size() && 
         (tokens[curr].token == '/' || tokens[curr].token == '*')) {
    char op = tokens[curr].token;
    curr++;
    Expression *right = GetPrimary(tokens, curr);
    if (op == '*') left = new Product(left, right);
    if (op == '/') left = new Quotient(left, right);
  }
  return left;
}

Expression *GetExpression(std::vector<Token> &tokens, size_t &curr) {
  Expression *left = GetFactor(tokens, curr);
  while (curr < tokens.size() &&
         (tokens[curr].token == '+' || tokens[curr].token == '-')) {
    char op = tokens[curr].token;
    curr++;
    Expression *right = GetFactor(tokens, curr);
    if (op == '+') left = new Sum(left, right);
    if (op == '-') left = new Difference(left, right);
  }
  return left;
}

// Parses an expression from a string.
Expression *ExpressionFromString(const std::string &S) {
  auto tokens = tokenize(S);
  size_t pos = 0;
  return GetExpression(tokens, pos);
}

#endif  // EXPRESSION
