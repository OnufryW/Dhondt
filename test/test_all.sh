#!/bin/bash
for testfile in ./*.cpp; do
  g++ -Wall -O3 $testfile -o test_to_run
  if [ $? -ne 0 ]; then
    echo "Compiling $testfile failed!"
    exit 1
  fi
  echo ""
  echo "Testing $testfile"
  ./test_to_run
  if [ $? -ne 0 ]; then
    echo "Test $testfile failed!"
    rm ./test_to_run
    exit 1
  fi
  rm ./test_to_run
done
