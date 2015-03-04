#!/usr/bin/env python3
"""
 run_tests

 Programmed by: Dante Signal 31

 email: dante.signal31@gmail.com

 Run geolocate unittest test cases.
"""
####################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###################################

import sys
import unittest

DEFAULT_TEST_DIR = "geolocate/tests"

def load_all_tests():
    tests = unittest.defaultTestLoader.discover(DEFAULT_TEST_DIR)
    return tests

def load_tests_by_pattern(pattern):
    pattern_with_globs = "%s" % (pattern,)
    tests = unittest.defaultTestLoader.discover("tests",
                                                pattern=pattern_with_globs)
    return tests

def run_tests(tests):
    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=1)
    runner.run(tests)

def run_functional_tests(pattern=None):
    print("Running tests...")
    if pattern is None:
        tests = load_all_tests()
    else:
        tests = load_tests_by_pattern(pattern)
    run_tests(tests)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_functional_tests()
    else:
        run_functional_tests(pattern=sys.argv[1])
