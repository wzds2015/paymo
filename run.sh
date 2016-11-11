#!/usr/bin/env bash

# example of the run script for running the fraud detection algorithm with a python file,
# but could be replaced with similar files from any major language

# I'll execute my programs, with the input directory paymo_input and output the files in the directory paymo_output
python ./src/test/antifraud_test.py
rm -f ./paymo_output/*test.txt
echo "\n"
echo "Start main run"
python ./src/main/antifraud.py
