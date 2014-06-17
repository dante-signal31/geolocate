#!/usr/bin/env bash

coverage3 run ./run_tests.py
echo "Removing previous reports..."
rm -rf htmlcov/*
rmdir htmlcov
echo "Removed."
echo "Building coverage report..."
coverage3 html
echo "Coverage report built."
echo "Let's show report."
(firefox htmlcov/index.html &> /dev/null &)
echo "Bye!"

