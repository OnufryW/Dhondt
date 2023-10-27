#ifndef TRIM
#define TRIM

const char *whitespace_for_trim_function = " \t\n\r\f\v";

std::string &RTrim(std::string &s) {
  s.erase(s.find_last_not_of(whitespace_for_trim_function) + 1);
  return s;
}

std::string &LTrim(std::string &s) {
  s.erase(0, s.find_first_not_of(whitespace_for_trim_function));
  return s;
}

std::string &Trim(std::string &s) {
  return LTrim(RTrim(s));
}

#endif // TRIM
