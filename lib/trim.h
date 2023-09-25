#ifndef TRIM
#define TRIM

const char *whitespace_for_trim_function = " \t\n\r\f\v";

void Trim(std::string &s) {
  s.erase(s.find_last_not_of(whitespace_for_trim_function) + 1);
}

#endif // TRIM
