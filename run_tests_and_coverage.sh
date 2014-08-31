#!/usr/bin/env bash

python3-coverage run --omit "/usr/*" ./run_tests.py
echo "Removing previous reports..."
rm -rf htmlcov/*
rmdir htmlcov
echo "Removed."
echo "Building coverage report..."
python3-coverage html
echo "Coverage report built."
echo "Let's show report."
(firefox htmlcov/index.html &> /dev/null &)
echo "Bye!"

